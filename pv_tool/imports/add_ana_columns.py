from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING
import pandas as pd

if TYPE_CHECKING:
    from pv_tool.imports.import_data import Dbase


def add_columns(self: Dbase):
    """
    Append analysis columns in specified order to the back of the DataFrame,
    preserving data in 'preserve_cols' if they exist.
    """
    # Your desired analysis columns (in order)
    analysis_columns = [
        'ANA_TERREINSPANNING', 'ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING',
        'ANA_DSS_MAX_CONSOLIDATIE_SPANNING', 'ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL',
        'ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG', 'ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL',
        'ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG', 'ANA_GRENSSPANNING_PROEF', 'ANA_POP_VELD',
        'ANA_POP_VELD_GEMIDDELD', 'ANA_GRENSSPANNING_VOORSTEL', 'ANA_GRENSSPANNING_HANDMATIG',
        'ANA_GRENSSPANNING_REKEN', 'OCR_TXT', 'OCR_DSS'
    ]
    preserve_cols = [
        'ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG',
        'ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG',
        'ANA_GRENSSPANNING_HANDMATIG'
    ]
    df = self.dbase_df

    # Remove any analysis columns from the main columns list to avoid duplicates
    other_columns = [col for col in df.columns if col not in analysis_columns]

    # Add or overwrite analysis columns as needed (preserved ones are kept if present)
    for col in analysis_columns:
        if col in preserve_cols and col in df.columns:
            continue  # preserve existing data
        else:
            df[col] = None  # add or overwrite with None

    # Reindex to: [existing non-analysis columns, then analysis columns in order]
    df = df[other_columns + analysis_columns]
    self.dbase_df = df


def add_terreinspanning(self: Dbase):
    """deze functie berekend de terreinspanning."""
    columns = ['SD_TERREINSPANNING', 'CRS_TERREINSPANNING', 'DSS_TERREINSPANNING', 'TXT_SS_TERREINSPANNING']
    self.dbase_df['ANA_TERREINSPANNING'] = self.dbase_df[columns].max(axis=1, skipna=True)


def add_txt_max_vert_consol_sp(self: Dbase):
    """Deze functie berekend de eind verticale consolidatiespanning van de triaxiaalproef. Kan worden omgezet naar max"""
    # product1 = self.dbase_df["TXT_SS_S'_MAX_CONSOLIDATIE"] + self.dbase_df['TXT_SS_T_MAX_CONSOLIDATIE']
    product2 = self.dbase_df["TXT_SS_S'_EIND_CONSOLIDATIE"] + self.dbase_df['TXT_SS_T_EIND_CONSOLIDATIE']
    self.dbase_df['ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING'] = product2


def add_dss_max_consol_sp(self: Dbase):
    """Deze functie berekend de eind verticale consolidatiespanning van de DSS-proef. Kan worden omgezet naar max"""
    # self.dbase_df['ANA_DSS_MAX_CONSOLIDATIE_SPANNING'] = self.dbase_df[
    #     ['DSS_MAX_EFF_VERT_SPANNING_CONSOLIDATIE', 'DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE']].max(axis=1)
    self.dbase_df['ANA_DSS_MAX_CONSOLIDATIE_SPANNING'] = self.dbase_df['DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE']


def add_txt_consol_type(self: Dbase):
    """Geeft een voorstel voor het consolidatietype van de triaxiaalproef. Indien de maximale consolidatiespanning
    niet meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
    consolidatietype NC aangenomen."""

    if self.dbase_df['ALG__TRIAXIAAL'].any():
        self.dbase_df.loc[self.dbase_df['ALG__TRIAXIAAL'], 'ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL'] = self.dbase_df.apply(
            lambda row: 'OC' if row['ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING'] / row['ANA_TERREINSPANNING'] <= 1.3
            else 'NC', axis=1
        )


def add_dss_consol_type(self: Dbase):
    """Geeft een voorstel voor het consolidatietype van de DSS-proef. Indien de maximale consolidatiespanning niet
    meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
    consolidatietype NC aangenomen."""
    if self.dbase_df['ALG__DSS'].any():
        self.dbase_df.loc[self.dbase_df['ALG__DSS'], 'ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL'] = self.dbase_df.apply(
            lambda row: 'OC' if row['ANA_DSS_MAX_CONSOLIDATIE_SPANNING'] / row['ANA_TERREINSPANNING'] <= 1.3
            else 'NC', axis=1
        )


def add_grensspanning_proef(self: Dbase):
    """Deze functie bepaalt de grensspanning."""
    columns = ['CRS_GRENSSPANNING_A', 'SD_ISOTACHE_GRENSSPANNING_A', 'ANA_GRENSSPANNING_HANDMATIG']
    grens_values = self.dbase_df[columns].max(axis=1)
    self.dbase_df['ANA_GRENSSPANNING_PROEF'] = grens_values

# def add_grensspanning_proef(self: Dbase):
#     """Deze functie bepaalt de grensspanning"""
#     columns = ['CRS_GRENSSPANNING_A', 'SD_ISOTACHE_GRENSSPANNING_A', 'ANA_GRENSSPANNING_HANDMATIG']
#
#     for col in columns:
#         non_numeric_positions = self.dbase_df[
#             self.dbase_df[col].apply(lambda x: not pd.api.types.is_numeric_dtype(type(x)))].index.tolist()
#         if non_numeric_positions:
#             print(f"Column '{col}' contains non-numeric values at positions: {non_numeric_positions}. "
#                   f"These values will be treated as NaN.")
#
#     numeric_dbase = self.dbase_df[columns].apply(pd.to_numeric, errors='coerce')
#     grens_values = numeric_dbase.max(axis=1)
#     self.dbase_df['ANA_GRENSSPANNING_PROEF'] = grens_values


def calc_pop_veld(self):
    """Berekend de POP in het veld"""
    self.dbase_df['ANA_POP_VELD'] = self.dbase_df['ANA_GRENSSPANNING_PROEF'] - self.dbase_df['ANA_TERREINSPANNING']


def calc_pop_average(self):
    """Berekend de gemiddelde POP van een monster. Aangenomen wordt dat de POP gelijk blijft in de diepte."""
    self.dbase_df['ANA_POP_VELD_GEMIDDELD'] = self.dbase_df.groupby('BORING_NUMMER')['ANA_POP_VELD'].transform(
        'mean')


def add_grensspanning_voorstel(self: Dbase):
    self.dbase_df['ANA_GRENSSPANNING_VOORSTEL'] = (self.dbase_df['ANA_TERREINSPANNING'] +
                                                   self.dbase_df['ANA_POP_VELD_GEMIDDELD'])


def calc_grensspanning_reken(self: Dbase):  # klopt
    """
    Berekent de rekenwaarde van de grensspanning per rij.
    """
    def calculate_row(row):
        if 'ANA_GRENSSPANNING_HANDMATIG' in row and row['ANA_GRENSSPANNING_HANDMATIG'] is not None:
            return row['ANA_GRENSSPANNING_HANDMATIG']
        elif 'ANA_GRENSSPANNING_VOORSTEL' in row:
            return row['ANA_GRENSSPANNING_VOORSTEL']
        return None
    if 'ANA_GRENSSPANNING_HANDMATIG' in self.dbase_df.columns or 'ANA_GRENSSPANNING_VOORSTEL' in self.dbase_df.columns:
        self.dbase_df['ANA_GRENSSPANNING_REKEN'] = self.dbase_df.apply(calculate_row, axis=1)
    else:
        self.dbase_df['ANA_GRENSSPANNING_REKEN'] = None


def calc_ocr_txt(self: Dbase):
    """Deze functie berekent de OCR van de triaxiaalproeven per rij."""
    def calculate_row(row):
        if row['ALG__TRIAXIAAL']:
            grensspanning_reken = row['ANA_GRENSSPANNING_REKEN']
            terreinspanning = row['ANA_TERREINSPANNING']

            if grensspanning_reken is not None and terreinspanning is not None:
                if row['ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG'] == 'OC':
                    return grensspanning_reken / terreinspanning
                elif row['ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL'] == 'OC':
                    return grensspanning_reken / terreinspanning
                else:
                    return 1.0
            return None
        return None

    if 'ALG__TRIAXIAAL' in self.dbase_df.columns:
        self.dbase_df['OCR_TXT'] = self.dbase_df.apply(calculate_row, axis=1)
    else:
        self.dbase_df['OCR_TXT'] = None


def calc_ocr_dss(self: Dbase):
    """Deze functie berekent de OCR van de DSS-proeven."""
    def calculate_row(row):
        if row['ALG__DSS']:
            grensspanning_reken = row['ANA_GRENSSPANNING_REKEN']
            terreinspanning = row['ANA_TERREINSPANNING']

            if grensspanning_reken is not None and terreinspanning is not None:
                if row['ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG'] == 'OC':
                    return grensspanning_reken / terreinspanning
                elif row['ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL'] == 'OC':
                    return grensspanning_reken / terreinspanning
                else:
                    return 1.0
            else:
                return None
        return None

    if 'ALG__DSS' in self.dbase_df.columns:
        self.dbase_df['OCR_DSS'] = self.dbase_df.apply(calculate_row, axis=1)
    else:
        self.dbase_df['OCR_DSS'] = None
