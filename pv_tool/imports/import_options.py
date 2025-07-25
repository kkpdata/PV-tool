from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pv_tool.imports.import_data import Dbase


def import_dbase(self: Dbase, dbase_dir: Path):
    """Importeert de Dbase-df (template)."""
    dbase = pd.read_excel(dbase_dir)
    self.dbase_df = dbase
    return self.dbase_df


def import_pv_tool(self: Dbase, pv_dir: Path):
    """Importeert de oude pv-tool"""
    pv = pd.read_excel(pv_dir, skiprows=47, sheet_name='Dbase2', index_col='ALG__BORING_MONSTERNR_ID') # Dit is nieuw dat dze kolom als index wordt gezet
    pv = pv[pv.index.notna()]  # Verwijder rijen met een NaN in de index
    self.pv_tool = pv
    return self.pv_tool


def import_stowa(self: Dbase, stowa_dir: Path):
    """Importeert de stowa-database"""
    stowa = pd.read_excel(stowa_dir, skiprows=8, sheet_name='Dbase')
    self.stowa_df = stowa
