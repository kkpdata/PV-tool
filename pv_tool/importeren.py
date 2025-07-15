import numpy as np
import pandas as pd
from pandas import DataFrame
from typing import Optional, Literal
from pathlib import Path
from pv_tool.imports.globals import (PV_TOOL_DBASE_COLUMNS, CLAS_COLUMNS, CRS_COLUMNS, SD_COLUMNS, DSS_COLUMNS,
                                     TXT_COLUMNS)


class Dbase:
    """Deze class bevat alle functies die te maken hebben met het bouwen de Dbase-dataframe"""

    def __init__(self):
        self.stowa_df: Optional[DataFrame] = None
        self.pv_tool: Optional[DataFrame] = None
        self.dbase_df: Optional[DataFrame] = None

    def import_stowa(self, stowa_dir: Path):
        """Importeert de stowa-database"""
        stowa = pd.read_excel(stowa_dir, skiprows=8, sheet_name='Dbase')
        self.stowa_df = stowa

    def add_missing_columns(self):
        """Voeg de missende kolommen toe aan de stowa-df om hem gelijk te maken aan de pv-tool-df """
        self.dbase_df = self.stowa_df.copy(deep=True)
        self.dbase_df = self.dbase_df.reindex(columns=PV_TOOL_DBASE_COLUMNS, fill_value=pd.NA)
        self.dbase_df = self.dbase_df[PV_TOOL_DBASE_COLUMNS] # zorgt ervoor dat de volgorde van kolommen overeenkomt

    def import_pv_tool(self, pv_dir: Path):
        """Importeert de oude pv-tool"""
        pv = pd.read_excel(pv_dir, skiprows=47, sheet_name='Dbase2')
        pv = pv[pv.index.notna()]  # Verwijder rijen met een NaN in de index
        self.pv_tool = pv
        return self.pv_tool

    def select_columns(self):
        """Selecteert de kolommen in de pv-tool die nodig zijn voor het maken van de Dbase-df (template)"""
        self.dbase_df = self.pv_tool.copy(deep=True)
        self.dbase_df = self.dbase_df[PV_TOOL_DBASE_COLUMNS]

    def import_dbase(self, dbase_dir: Path):
        """Importeert de Dbase-df (template)."""
        dbase = pd.read_excel(dbase_dir)
        self.dbase_df = dbase
        return self.dbase_df

    def check_clas(self):
        """Controleert of de algemene classificatie proeven zijn uitgevoerd."""
        self.dbase_df['ALG__CLASSIFICATIE'] = self.dbase_df[CLAS_COLUMNS].notnull().any(axis=1)

    def check_crs(self):
        """Controleert of de CRS-proeven zijn uitgevoerd."""
        self.dbase_df['ALG__CRS'] = self.dbase_df[CRS_COLUMNS].notnull().any(axis=1)
        pass

    def check_sd(self):
        """Controleert of de samendrukkingsproeven zijn uitgevoerd."""
        self.dbase_df['ALG__SAMENDRUKKING'] = self.dbase_df[SD_COLUMNS].notnull().any(axis=1)

    def check_dss(self):
        """Controleert of de DSS-proeven zijn uitgevoerd."""
        self.dbase_df['ALG__DSS'] = self.dbase_df[DSS_COLUMNS].notnull().any(axis=1)

    def check_txt(self):
        """Controleert of de triaxiaalproeven zijn uitgevoerd."""
        self.dbase_df['ALG__TRIAXIAAL'] = self.dbase_df[TXT_COLUMNS].notnull().any(axis=1)

    def overwrite_veen_korrel_sond(self):
        """Overschrijft de waardes uit de kolommen ALG_VEENCLASSIFICATIE, ALG__KORRELVERDELING en ALG__SONDEERWAARDE
        met nan-waardes."""
        self.dbase_df['ALG__VEENCLASSIFICATIE'] = pd.NA
        self.dbase_df['ALG__KORRELVERDELING'] = pd.NA
        self.dbase_df['ALG__SONDEERWAARDE'] = pd.NA

    def alg_columns(self):
        """Controleert welke proeven zijn uitgevoerd."""
        self.check_clas()
        self.check_crs()
        self.check_sd()
        self.check_dss()
        self.check_txt()
        self.overwrite_veen_korrel_sond()

    def add_terreinspanning(self):
        """deze functie berekend de terreinspanning."""
        columns = ['SD_TERREINSPANNING', 'CRS_TERREINSPANNING', 'DSS_TERREINSPANNING', 'TXT_SS_TERREINSPANNING']
        self.dbase_df['ANA_TERREINSPANNING'] = self.dbase_df[columns].max(axis=1, skipna=True)

    def add_grensspanning(self):
        """Deze functie berekend de grensspanning."""
        columns = ['CRS_GRENSSPANNING_A', 'SD_ISOTACHE_GRENSSPANNING_A', 'ANA_GRENSSPANNING_HANDMATIG']
        grens_values = self.dbase_df[columns].max(axis=1)
        self.dbase_df['ANA_GRENSSPANNING'] = grens_values

    def add_txt_max_vert_consol_sp(self):
        """Deze functie berekend de maximale verticale consolidatiespanning van de triaxiaalproef."""
        product1 = self.dbase_df["TXT_SS_S'_MAX_CONSOLIDATIE"] + self.dbase_df['TXT_SS_T_MAX_CONSOLIDATIE']
        product2 = self.dbase_df["TXT_SS_S'_EIND_CONSOLIDATIE"] + self.dbase_df['TXT_SS_T_EIND_CONSOLIDATIE']
        self.dbase_df['ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING'] = np.maximum(product1, product2)

    def add_dss_max_consol_sp(self):
        """Deze functie berekend de maximale verticale consolidatiespanning van de DSS-proef."""
        self.dbase_df['ANA_DSS_MAX_CONSOLIDATIE_SPANNING'] = self.dbase_df[
            ['DSS_MAX_EFF_VERT_SPANNING_CONSOLIDATIE', 'DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE']].max(axis=1)

    def add_txt_consol_type(self):
        """Geeft een voorstel voor het consolidatietype van de triaxiaalproef. Indien de maximale consolidatiespanning
        niet meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
        consolidatietype NC aangenomen."""
        self.dbase_df['ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL'] = self.dbase_df.apply(
            lambda row: 'OC' if row['ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING'] / row[
                'ANA_TERREINSPANNING'] <= 1.3 else 'NC',
            axis=1
        )

    def add_dss_consol_type(self):
        """Geeft een voorstel voor het consolidatietype van de DSS-proef. Indien de maximale consolidatiespanning niet
        meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
        consolidatietype NC aangenomen."""
        self.dbase_df['ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL'] = self.dbase_df.apply(
            lambda row: 'OC' if row['ANA_DSS_MAX_CONSOLIDATIE_SPANNING'] / row['ANA_TERREINSPANNING'] <= 1.3 else 'NC',
            axis=1
        )

    def add_txt_consol_type_handmatig(self):
        """Met deze functie wordt een kolom aangemaakt waarin je handmatig het consolidatietype van de triaxiaalproef
        kan aanpassen."""
        self.dbase_df['ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG'] = None

    def add_dss_consol_type_handmatig(self):
        """Met deze functie wordt een kolom aangemaakt waarin je handmatig het consolidatietype van de DSS-proef
        kan aanpassen."""
        self.dbase_df['ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG'] = None

    def add_max_vert_spanning(self):
        """Deze functie bepaald de maximale ondervonden verticale spanning van het monster."""
        selected_cols = ['ANA_GRENSSPANNING', 'ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING',
                         'ANA_DSS_MAX_CONSOLIDATIE_SPANNING']
        values = self.dbase_df[selected_cols].max(axis=1)
        self.dbase_df['ANA_MAX_VERTICALE_SPANNING'] = values

    def add_ocr_txt(self):
        """Deze functie berekend de OCR van de triaxiaalproef"""
        func = self.dbase_df['ANA_MAX_VERTICALE_SPANNING'] / (
                self.dbase_df["TXT_SS_S'_EIND_CONSOLIDATIE"] + self.dbase_df['TXT_SS_T_EIND_CONSOLIDATIE'])
        ocr = self.dbase_df['TXT_SS_OCR'].copy()
        vert_sp = self.dbase_df['ANA_MAX_VERTICALE_SPANNING'].copy()
        self.dbase_df['ANA_OCR_TXT_MONSTER'] = np.maximum(func, ocr, vert_sp)

    def add_ocr_dss(self):
        """Deze functie berekend de OCR van de DSS-proef."""
        product = self.dbase_df['ANA_MAX_VERTICALE_SPANNING'] / self.dbase_df[
            'DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE']
        ocr = self.dbase_df['DSS_OCR']
        self.dbase_df['ANA_OCR_DSS_MONSTER'] = np.maximum(product, ocr)

    def add_ana_columns(self):
        """Voegt ANA-kolommen toe aan het dataframe"""
        self.add_terreinspanning()
        self.add_grensspanning()
        self.add_txt_max_vert_consol_sp()
        self.add_dss_max_consol_sp()
        self.add_txt_consol_type()
        self.add_dss_consol_type()
        self.add_txt_consol_type_handmatig()
        self.add_dss_consol_type_handmatig()
        self.add_max_vert_spanning()
        self.add_ocr_txt()
        self.add_ocr_dss()

    def create_dbase(self, source: Literal['Stowa', 'PV-tool', 'Dbase']):
        """Maakt de dbase-dataframe"""
        if source == 'Stowa':
            self.add_missing_columns()
            self.alg_columns()
            self.add_ana_columns()
        elif source == 'PV-tool':
            self.select_columns()  # select columns needed for building dbase
            self.alg_columns()
            self.add_ana_columns()
        elif source == 'Dbase':
            self.add_ana_columns()  # de ANA kolommen worden dan opnieuw berekend, indien een aanpassing is gedaan in de PV-naam oid.

    def import_date_and_create_dbase(self, source: Literal['Stowa', 'PV-tool', 'Dbase'], source_dir: Path):
        if source == 'Stowa':
            self.import_stowa(stowa_dir=source_dir)
            self.create_dbase(source=source)
        elif source == 'PV-tool':
            self.import_pv_tool(pv_dir=source_dir)
            self.create_dbase(source=source)
        elif source == 'Dbase':
            self.import_dbase(dbase_dir=source_dir)
            self.create_dbase(source=source)  # dependencies? anders weglaten
        return self.dbase_df
