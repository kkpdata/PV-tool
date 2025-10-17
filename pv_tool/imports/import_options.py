from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pv_tool.imports.import_data import Dbase


def import_dbase(self: Dbase, dbase_dir: Path):
    """Importeert de Dbase-df (template)."""
    dbase = pd.read_excel(dbase_dir, sheet_name='Dbase5_0', index_col='ALG__BORING_MONSTERNR_ID')
    self.dbase_df = dbase
    return self.dbase_df


def import_pv_tool(self: Dbase, pv_dir: Path):
    """Importeert data uit de oude pv-tool (Excel-versie)."""
    preserve_cols = [
        'ANA_GRENSSPANNING_HANDMATIG',
        'ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG',
        'ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG'
    ]

    # Read the PV-tool file
    pv = pd.read_excel(pv_dir, skiprows=47, sheet_name='Dbase2')
    pv = pv.dropna(subset=['ALG__BORING_MONSTERNR_ID'])

    # Create the ID column
    pv[['ALG__REGEL', 'BORING_NUMMER', 'MONSTER_ID']] = pv[['ALG__REGEL', 'BORING_NUMMER', 'MONSTER_ID']].fillna(
        '').astype(str)
    pv['ALG__BORING_MONSTERNR_ID'] = pv[['ALG__REGEL', 'BORING_NUMMER', 'MONSTER_ID']].apply('_'.join, axis=1)

    # Ensure preserved columns maintain their data types
    for col in preserve_cols:
        if col in pv.columns:
            if col.endswith('_HANDMATIG') and 'CONSOLIDATIE_TYPE' in col:
                pv[col] = pv[col].astype(str)
            elif col == 'ANA_GRENSSPANNING_HANDMATIG':
                pv[col] = pd.to_numeric(pv[col], errors='coerce')

    pv = pv.set_index('ALG__BORING_MONSTERNR_ID')
    self.pv_tool = pv
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
