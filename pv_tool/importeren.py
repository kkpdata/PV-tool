# Deze file gaan we gebruiken om alle imports te doen die nodig zijn om de PV-tool te draaien.
# Dus de stowa of een oude PV-tool (mogelijk nog andere dingen in de toekomst)  -> Dbase moet ook in te laden zijn.
# We moeten zorgen dat we ondanks de verschillende bronnen 1 eindproduct krijgen,
# dus 1 database met allemaal dezelfde kolommen

import pandas as pd
from pandas import DataFrame
from typing import Optional, Literal
from pathlib import Path


class Dbase:
    """Deze class bevat alle functies die te maken hebben met het bouwen de Dbase-dataframe"""

    def __init__(self):
        self.stowa_df: Optional[DataFrame] = None
        self.pv_tool: Optional[DataFrame] = None
        self.dbase_df: Optional[DataFrame] = None

    def import_stowa(self, stowa_dir: Path):
        stowa = pd.read_excel(stowa_dir, skiprows=8, sheet_name='Dbase', index_col='ALG__BORING_MONSTERNR_ID')
        self.stowa_df = stowa

    def import_pv_tool(self, pv_dir: Path):
        pv = pd.read_excel(pv_dir, skiprows=47, sheet_name='Dbase2', index_col='ALG__BORING_MONSTERNR_ID')
        pv = pv[pv.index.notna()]  # Verwijder rijen met een NaN in de index
        self.pv_tool = pv
        return self.pv_tool

    def import_dbase(self, dbase_dir: Path):
        dbase = pd.read_excel(dbase_dir)
        self.dbase_df = dbase
        return self.dbase_df

    def check_clas(self):
        pass

    def check_crs(self):
        pass

    def check_samen(self):
        pass

    def check_dss(self):
        pass

    def check_txt(self):
        pass
    def check_txt(self):
        """Deze functie controleert of de triaxiaalproeven zijn uitgevoerd."""
        # of alles leeg dan geef terug False, of
        # check of kolom 2 t/m17 gevuld is. zo ja, geef terug in ALG_TRIAXIAAL = True
        # als 1 of meerdere ontbreken of foute data bevatten, geef warning.

    def alg_columns(self):
        self.check_clas()
        self.check_crs()
        self.check_samen()
        self.check_dss()
        self.check_txt()

    def create_dbase(self, source: Literal['Stowa', 'PV-tool', 'Dbase']):
        """Maakt de dbase-dataframe"""
        if source == 'Stowa':
            self.alg_columns()
            self.add_ana_colums()
        elif source == 'PV-tool':
            self.select_colums() # select columns needed for building dbase
            self.alg_columns()
            self.add_ana_colums()
        elif source == 'Dbase':
            self.add_ana_columns()  # de ANA kolommen worden dan opnieuw berekend, indien een aanpassing is gedaan in de PV-naam oid.
        # grensspanning moeten we nog even overnadenken.
        pass

    def import_and_validate(self, source: Literal['Stowa', 'PV-tool', 'Dbase'], source_dir: Path):
        if source == 'Stowa':
            self.import_stowa(stowa_dir=source_dir)
            self.create_dbase(source=source)
        elif source == 'PV-tool':
            self.import_pv_tool(pv_dir=source_dir)
            self.create_dbase(source=source)
        elif source == 'Dbase':
            self.import_dbase(dbase_dir=source_dir)
            self.create_dbase(source=source)

        # valideer dbase
        # return dbase en warnings
        return self.dbase_df
