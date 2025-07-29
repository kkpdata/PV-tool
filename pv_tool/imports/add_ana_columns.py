from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.imports.import_data import Dbase


def add_terreinspanning(self: Dbase):
    """deze functie berekend de terreinspanning."""
    columns = ['SD_TERREINSPANNING', 'CRS_TERREINSPANNING', 'DSS_TERREINSPANNING', 'TXT_SS_TERREINSPANNING']
    self.dbase_df['ANA_TERREINSPANNING'] = self.dbase_df[columns].max(axis=1, skipna=True)


def add_grensspanning(self: Dbase):
    """Deze functie berekend de grensspanning."""
    columns = ['CRS_GRENSSPANNING_A', 'SD_ISOTACHE_GRENSSPANNING_A', 'ANA_GRENSSPANNING_HANDMATIG']
    grens_values = self.dbase_df[columns].max(axis=1)
    self.dbase_df['ANA_GRENSSPANNING'] = grens_values


def add_txt_max_vert_consol_sp(self: Dbase):
    """Deze functie berekend de maximale verticale consolidatiespanning van de triaxiaalproef."""
    product1 = self.dbase_df["TXT_SS_S'_MAX_CONSOLIDATIE"] + self.dbase_df['TXT_SS_T_MAX_CONSOLIDATIE']
    product2 = self.dbase_df["TXT_SS_S'_EIND_CONSOLIDATIE"] + self.dbase_df['TXT_SS_T_EIND_CONSOLIDATIE']
    self.dbase_df['ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING'] = np.maximum(product1, product2)


def add_dss_max_consol_sp(self: Dbase):
    """Deze functie berekend de maximale verticale consolidatiespanning van de DSS-proef."""
    self.dbase_df['ANA_DSS_MAX_CONSOLIDATIE_SPANNING'] = self.dbase_df[
        ['DSS_MAX_EFF_VERT_SPANNING_CONSOLIDATIE', 'DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE']].max(axis=1)


def add_txt_consol_type(self: Dbase):
    """Geeft een voorstel voor het consolidatietype van de triaxiaalproef. Indien de maximale consolidatiespanning
    niet meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
    consolidatietype NC aangenomen."""
    if self.dbase_df['ALG_TRIAXIAAL'].any():  # Controleer of er überhaupt True-waarden zijn
        self.dbase_df.loc[self.dbase_df['ALG_TRIAXIAAL'], 'ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL'] = self.dbase_df.apply(
            lambda row: 'OC' if row['ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING'] / row['ANA_TERREINSPANNING'] <= 1.3
            else 'NC', axis=1
        )


def add_dss_consol_type(self: Dbase):
    """Geeft een voorstel voor het consolidatietype van de DSS-proef. Indien de maximale consolidatiespanning niet
    meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
    consolidatietype NC aangenomen."""
    if self.dbase_df['ALG_DSS'].any():
        self.dbase_df.loc[self.dbase_df['ALG_DSS'], 'ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL'] = self.dbase_df.apply(
            lambda row: 'OC' if row['ANA_DSS_MAX_CONSOLIDATIE_SPANNING'] / row['ANA_TERREINSPANNING'] <= 1.3
            else 'NC', axis=1
        )


def add_txt_consol_type_handmatig(self: Dbase):
    """Met deze functie wordt een kolom aangemaakt waarin je handmatig het consolidatietype van de triaxiaalproef
    kan aanpassen."""
    self.dbase_df['ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG'] = None


def add_dss_consol_type_handmatig(self: Dbase):
    """Met deze functie wordt een kolom aangemaakt waarin je handmatig het consolidatietype van de DSS-proef
    kan aanpassen."""
    self.dbase_df['ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG'] = None


def add_max_vert_spanning(self: Dbase):
    """Deze functie bepaald de maximale ondervonden verticale spanning van het monster."""
    selected_cols = ['ANA_GRENSSPANNING', 'ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING',
                     'ANA_DSS_MAX_CONSOLIDATIE_SPANNING']
    values = self.dbase_df[selected_cols].max(axis=1)
    self.dbase_df['ANA_MAX_VERTICALE_SPANNING'] = values


def add_ocr_txt(self: Dbase):
    """Deze functie berekend de OCR van de triaxiaalproef"""
    func = self.dbase_df['ANA_MAX_VERTICALE_SPANNING'] / (
            self.dbase_df["TXT_SS_S'_EIND_CONSOLIDATIE"] + self.dbase_df['TXT_SS_T_EIND_CONSOLIDATIE'])
    ocr = self.dbase_df['TXT_SS_OCR'].copy()
    vert_sp = self.dbase_df['ANA_MAX_VERTICALE_SPANNING'].copy()
    self.dbase_df['ANA_OCR_TXT_MONSTER'] = np.maximum(func, ocr, vert_sp)


def add_ocr_dss(self: Dbase):
    """Deze functie berekend de OCR van de DSS-proef."""
    product = self.dbase_df['ANA_MAX_VERTICALE_SPANNING'] / self.dbase_df[
        'DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE']
    ocr = self.dbase_df['DSS_OCR']
    self.dbase_df['ANA_OCR_DSS_MONSTER'] = np.maximum(product, ocr)
