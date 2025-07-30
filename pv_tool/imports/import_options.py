from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pv_tool.imports.import_data import Dbase


def import_dbase(self: Dbase, dbase_dir: Path):
    """Importeert de Dbase-df (template)."""
    dbase = pd.read_excel(dbase_dir, index_col='ALG__BORING_MONSTERNR_ID')
    self.dbase_df = dbase
    return self.dbase_df


def import_pv_tool(self: Dbase, pv_dir: Path):
    """Importeert data uit de oude pv-tool (Excel-versie)."""
    pv = pd.read_excel(pv_dir, skiprows=47, sheet_name='Dbase2')
    pv = pv.dropna(subset=['ALG__BORING_MONSTERNR_ID'])
    pv[['ALG__REGEL', 'BORING_NUMMER', 'MONSTER_ID']] = pv[['ALG__REGEL', 'BORING_NUMMER', 'MONSTER_ID']].fillna(
        '').astype(str)
    pv['ALG__BORING_MONSTERNR_ID'] = pv[['ALG__REGEL', 'BORING_NUMMER', 'MONSTER_ID']].apply('_'.join, axis=1)
    pv = pv.set_index('ALG__BORING_MONSTERNR_ID')
    self.
    = pv
    return self.pv_tool


def import_stowa(self: Dbase, stowa_dir: Path):
    """Importeert de stowa-database"""
    stowa = pd.read_excel(stowa_dir, skiprows=8, sheet_name='Dbase')
    stowa[['REGEL', 'BORING_NUMMER', 'MONSTER_ID']] = stowa[['REGEL', 'BORING_NUMMER', 'MONSTER_ID']].fillna(
        '').astype(str)
    stowa['ALG__BORING_MONSTERNR_ID'] = stowa[['REGEL', 'BORING_NUMMER', 'MONSTER_ID']].apply('_'.join, axis=1)
    stowa = stowa.set_index('ALG__BORING_MONSTERNR_ID')
    self.stowa_df = stowa
    return self.pv_tool
