# Deze file gaan we gebruiken om alle imports te doen die nodig zijn om de PV-tool te draaien.
# Dus de stowa of een oude PV-tool (mogelijk nog andere dingen in de toekomst)
# We moeten zorgen dat we ondanks de verschillende bronnen 1 eindproduct krijgen,
# dus 1 database met allemaal dezelfde kolommen

import pandas as pd
from pandas import DataFrame
from typing import Optional
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





