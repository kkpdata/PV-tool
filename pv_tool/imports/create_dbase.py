from __future__ import annotations
import pandas as pd
import numpy as np
from pv_tool.imports.globals import (PV_TOOL_DBASE_COLUMNS, CLAS_COLUMNS, CRS_COLUMNS, SD_COLUMNS, DSS_COLUMNS,
                                     TXT_COLUMNS)
from pv_tool.imports.add_ana_columns import (add_columns, add_terreinspanning, add_txt_max_vert_consol_sp,
                                             add_dss_max_consol_sp, add_txt_consol_type, add_dss_consol_type,
                                             add_grensspanning_proef, calc_pop_veld, calc_pop_average,
                                             add_grensspanning_voorstel, calc_grensspanning_reken, calc_ocr_txt,
                                             calc_ocr_dss)


def add_missing_columns(self):
    """Voeg de missende kolommen toe aan de stowa-df om hem gelijk te maken aan de pv-tool-df """
    self.dbase_df = self.stowa_df.copy(deep=True)
    self.dbase_df = self.dbase_df.reindex(columns=PV_TOOL_DBASE_COLUMNS, fill_value=np.nan)
    self.dbase_df = self.dbase_df[PV_TOOL_DBASE_COLUMNS]  # zorgt ervoor dat de volgorde van kolommen overeenkomt


def select_columns(self):
    """Selecteert de kolommen in de pv-tool die nodig zijn voor het maken van de Dbase-df (template)"""
    self.dbase_df = self.pv_tool.copy(deep=True)
    pv_tool_dbase_cols_new = [col for col in PV_TOOL_DBASE_COLUMNS if col != 'ALG__BORING_MONSTERNR_ID']
    self.dbase_df = self.dbase_df[pv_tool_dbase_cols_new]


def alg_columns(self):
    """Controleert welke proeven zijn uitgevoerd."""
    # Controleert of de algemene classificatie proeven zijn uitgevoerd.
    self.dbase_df['ALG__CLASSIFICATIE'] = self.dbase_df[CLAS_COLUMNS].notnull().any(axis=1)
    # Controleert of de CRS-proeven zijn uitgevoerd.#
    self.dbase_df['ALG__CRS'] = self.dbase_df[CRS_COLUMNS].notnull().any(axis=1)
    # Controleert of de samendrukkingsproeven zijn uitgevoerd.#
    self.dbase_df['ALG__SAMENDRUKKING'] = self.dbase_df[SD_COLUMNS].notnull().any(axis=1)
    # Controleert of de DSS-proeven zijn uitgevoerd.#
    self.dbase_df['ALG__DSS'] = self.dbase_df[DSS_COLUMNS].notnull().any(axis=1)
    # Controleert of de triaxiaalproeven zijn uitgevoerd.#
    self.dbase_df['ALG__TRIAXIAAL'] = self.dbase_df[TXT_COLUMNS].notnull().any(axis=1)
    # Overschrijft de waardes uit de kolommen ALG_VEENCLASSIFICATIE, ALG__KORRELVERDELING en ALG__SONDEERWAARDE
    # met nan-waardes.
    self.dbase_df['ALG__VEENCLASSIFICATIE'] = pd.NA
    self.dbase_df['ALG__KORRELVERDELING'] = pd.NA
    self.dbase_df['ALG__SONDEERWAARDE'] = pd.NA


def add_ana_columns(self):
    """Voegt ANA-kolommen toe aan het dataframe"""
    add_columns(self)
    add_terreinspanning(self)
    add_txt_max_vert_consol_sp(self)
    add_dss_max_consol_sp(self)
    add_txt_consol_type(self)
    add_dss_consol_type(self)
    add_grensspanning_proef(self)
    calc_pop_veld(self)
    calc_pop_average(self)
    add_grensspanning_voorstel(self)
    calc_grensspanning_reken(self)
    calc_ocr_txt(self)
    calc_ocr_dss(self)


def add_pv_naam(self):
    """Als er geen PV-naam aanwezig is, wordt 'TXT-proef' en/of 'DSS-proef' gebruikt als PV-naam"""
    if self.dbase_df['PV_NAAM'].isnull().all() or (self.dbase_df['PV_NAAM'] == '').all():
        # Voeg waarden toe op basis van de condities
        self.dbase_df['PV_NAAM'] = self.dbase_df.apply(
            lambda row: 'TXT-proef' if row['ALG__TRIAXIAAL'] else (
                'DSS-proef' if row['ALG__DSS'] else None
            ),
            axis=1
        )
