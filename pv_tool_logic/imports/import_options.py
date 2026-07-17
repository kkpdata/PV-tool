from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import TYPE_CHECKING
from datetime import time

if TYPE_CHECKING:
    from pv_tool_logic.imports.import_data import Dbase


def import_dbase(self: Dbase, dbase_dir: Path):
    """Importeert de Dbase-df (template)."""
    # First, read the file without headers to find the correct header row
    temp_df = pd.read_excel(dbase_dir, sheet_name="Dbase5_0", header=None)

    # Search for the row containing ALG__BORING_MONSTERNR_ID
    header_row: int | None = None
    for idx, row in temp_df.iterrows():
        if "ALG__BORING_MONSTERNR_ID" in row.values:
            # Cast pandas index to int - pandas ensures this is numeric for default RangeIndex
            header_row = int(str(idx))
            break

    if header_row is None:
        raise ValueError("Column 'ALG__BORING_MONSTERNR_ID' not found in the Excel file")

    # Now read the file with the correct header row and set the index
    dbase = pd.read_excel(dbase_dir, sheet_name="Dbase5_0", skiprows=header_row)

    # Opschonen boring_datum kolommen
    date_columns = ['BORING_DATUM', 'CLAS_DATUM', 'KV_DATUM', 'CRS_DATUM', 'SD_DATUM', 'DSS_DATUM', 'TXT_SS_DATUM']
    for col in date_columns:
        if col in dbase.columns:
            dbase[col] = pd.to_datetime(
                dbase[col],
                errors="coerce"
            )

    dbase = dbase.set_index("ALG__BORING_MONSTERNR_ID", drop=False)
    self.dbase_df = dbase
    return self.dbase_df


def import_pv_tool(self: Dbase, pv_dir: Path):
    """Importeert data uit de oude pv-tool (Excel-versie)."""
    preserve_cols = [
        "ANA_GRENSSPANNING_HANDMATIG",
        "ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG",
        "ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG",
    ]

    # Read the PV-tool file
    pv = pd.read_excel(pv_dir, skiprows=47, sheet_name="Dbase2")
    pv = pv.dropna(subset=["ALG__BORING_MONSTERNR_ID"])

    # Opschonen datumkolommen
    date_columns = ['BORING_DATUM', 'CLAS_DATUM', 'KV_DATUM', 'CRS_DATUM', 'SD_DATUM', 'DSS_DATUM', 'TXT_SS_DATUM']

    for col in date_columns:
        if col in pv.columns:
            pv[col] = pd.to_datetime(
                pv[col],
                errors="coerce"
            )

    # Create the ID column
    pv[["ALG__REGEL", "BORING_NUMMER", "MONSTER_ID"]] = (
        pv[["ALG__REGEL", "BORING_NUMMER", "MONSTER_ID"]].fillna("").astype(str)
    )
    pv["ALG__BORING_MONSTERNR_ID"] = pv[["ALG__REGEL", "BORING_NUMMER", "MONSTER_ID"]].apply("_".join, axis=1)

    # Ensure preserved columns maintain their data types
    for col in preserve_cols:
        if col in pv.columns:
            if col.endswith("_HANDMATIG") and "CONSOLIDATIE_TYPE" in col:
                pv[col] = pv[col].astype(str)
            elif col == "ANA_GRENSSPANNING_HANDMATIG":
                pv[col] = pd.to_numeric(pv[col], errors="coerce")

    pv = pv.set_index("ALG__BORING_MONSTERNR_ID", drop=False)
    self.pv_tool = pv
    return self.pv_tool


def _converteer_komma_naar_punt(df: pd.DataFrame) -> pd.DataFrame:
    """Converteert string kolommen met komma als decimaalscheiding naar numeriek.

    Vervangt ',' door '.' in string-waarden en converteert naar float waar mogelijk.
    Kolommen die niet volledig numeriek zijn blijven als object-type.
    """
    for col in df.columns:
        if df[col].dtype == object:
            converted = df[col].apply(lambda x: str(x).replace(",", ".") if isinstance(x, str) else x)
            numeriek = pd.to_numeric(converted, errors="coerce")
            # Alleen omzetten als er minstens één geldige numerieke waarde is
            if numeriek.notna().any():
                df[col] = numeriek
    return df


def import_stowa(self: Dbase, stowa_dir: Path):
    """Importeert de stowa-database"""
    stowa = pd.read_excel(stowa_dir, skiprows=8, sheet_name="Dbase")

    # Opschonen datumkolommen
    date_columns = ['BORING_DATUM', 'CLAS_DATUM', 'KV_DATUM', 'CRS_DATUM', 'SD_DATUM', 'DSS_DATUM', 'TXT_SS_DATUM']
    for col in date_columns:
        if col in stowa.columns:
            stowa[col] = pd.to_datetime(
                stowa[col],
                errors="coerce"
            )

    stowa[["REGEL", "BORING_NUMMER", "MONSTER_ID"]] = (
        stowa[["REGEL", "BORING_NUMMER", "MONSTER_ID"]].fillna("").astype(str)
    )
    stowa["ALG__BORING_MONSTERNR_ID"] = stowa[["REGEL", "BORING_NUMMER", "MONSTER_ID"]].apply("_".join, axis=1)
    stowa = stowa.set_index("ALG__BORING_MONSTERNR_ID", drop=False)

    # Converteer komma-decimalen naar punt en zet om naar numeriek
    stowa = _converteer_komma_naar_punt(stowa)

    self.stowa_df = stowa
    return self.stowa_df
