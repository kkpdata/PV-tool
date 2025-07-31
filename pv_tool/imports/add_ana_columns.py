from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.imports.import_data import Dbase


def add_terreinspanning(self: Dbase):  # TODO: test!!
    """deze functie berekend de terreinspanning."""
    columns = ['SD_TERREINSPANNING', 'CRS_TERREINSPANNING', 'DSS_TERREINSPANNING', 'TXT_SS_TERREINSPANNING']
    self.dbase_df['ANA_TERREINSPANNING'] = self.dbase_df[columns].max(axis=1, skipna=True)


def add_txt_consol_type(self: Dbase):
    """Geeft een voorstel voor het consolidatietype van de triaxiaalproef. Indien de maximale consolidatiespanning
    niet meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
    consolidatietype NC aangenomen."""
    if self.dbase_df['ALG__TRIAXIAAL'].any():  # Controleer of er überhaupt True-waarden zijn
        self.dbase_df.loc[self.dbase_df['ALG__TRIAXIAAL'], 'ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL'] = self.dbase_df.apply(
            lambda row: 'OC' if row['ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING'] / row['ANA_TERREINSPANNING'] <= 1.3
            else 'NC', axis=1
        )


def add_txt_consol_type_handmatig(self: Dbase):
    """Met deze functie wordt een kolom aangemaakt waarin je handmatig het consolidatietype van de triaxiaalproef
    kan aanpassen."""
    self.dbase_df['ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG'] = None


def add_dss_consol_type(self: Dbase):
    """Geeft een voorstel voor het consolidatietype van de DSS-proef. Indien de maximale consolidatiespanning niet
    meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
    consolidatietype NC aangenomen."""
    if self.dbase_df['ALG__DSS'].any():
        self.dbase_df.loc[self.dbase_df['ALG__DSS'], 'ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL'] = self.dbase_df.apply(
            lambda row: 'OC' if row['ANA_DSS_MAX_CONSOLIDATIE_SPANNING'] / row['ANA_TERREINSPANNING'] <= 1.3
            else 'NC', axis=1
        )


def add_dss_consol_type_handmatig(self: Dbase):
    """Met deze functie wordt een kolom aangemaakt waarin je handmatig het consolidatietype van de DSS-proef
    kan aanpassen."""
    self.dbase_df['ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG'] = None


def add_grensspanning_proef(self: Dbase):
    """Deze functie bepaald de grensspanning."""
    columns = ['CRS_GRENSSPANNING_A', 'SD_ISOTACHE_GRENSSPANNING_A', 'ANA_GRENSSPANNING_HANDMATIG']
    grens_values = self.dbase_df[columns].max(axis=1)
    self.dbase_df['ANA_GRENSSPANNING_PROEF'] = grens_values


def calc_pop_veld(self):
    """Calculates the POP in the field while taking the sample"""
    self.dbase_df['ANA_POP_VELD'] = self.dbase_df['ANA_GRENSSPANNING'] - self.dbase_df['ANA_TERREINSPANNING']


def calc_pop_average(self):
    """Calculates the average POP of the sample. Here is assumed that the POP stays the same with depth"""
    self.dbase_df['ANA_POP_VELD_GEMIDDELD'] = self.dbase_df.groupby('BORING_NUMMER')['ANA_POP_VELD'].transform(
        'mean')


def add_grensspanning_voorstel(self: Dbase):
    self.dbase_df['ANA_GRENSSPANNING_VOORSTEL'] = (self.dbase_df['ANA_TERREINSPANNING'] +
                                                   self.dbase_df['ANA_POP_VELD_GEMIDDELD'])


def add_grensspanning_handmatig(self: Dbase):
    """Maakt een kolom voor het handmatig invullen van de grensspanning."""
    self.dbase_df['ANA_GRENSSPANNING_HANDMATIG'] = None


def calc_grensspanning_reken(self: Dbase):
    """Berekend de rekenwaarde van de grensspanning."""
    if self.dbase_df['ANA_GRENSSPANNING_HANDMATIG']:
        self.dbase_df['ANA_GRENSSPANNING_REKEN'] = self.dbase_df['ANA_GRENSSPANNING_HANDMATIG']
    else:
        self.dbase_df['ANA_GRENSSPANNING_REKEN'] = self.dbase_df['ANA_GRENSSPANNING_VOORSTEL']


def calc_ocr_txt(self: Dbase):
    if self.dbase_df['ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG'] is not None:
        if self.dbase_df['ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG'] == 'OC':
            self.dbase_df['OCR_TXT'] = self.dbase_df['ANA_GRENSSPANNING_REKEN'] / self.dbase_df['ANA_TERREINSPANNING']
        else:
            self.dbase_df['OCR_TXT'] = 1.0
    else:
        if self.dbase_df['ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL'] == 'OC':
            self.dbase_df['OCR_TXT'] = self.dbase_df['ANA_GRENSSPANNING_REKEN'] / self.dbase_df['ANA_TERREINSPANNING']
        else:
            self.dbase_df['OCR_TXT'] = 1.0


def calc_ocr_dss(self: Dbase):
    if self.dbase_df['ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG'] is not None:
        if self.dbase_df['ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG'] == 'OC':
            self.dbase_df['OCR_DSS'] = self.dbase_df['ANA_GRENSSPANNING_REKEN'] / self.dbase_df['ANA_TERREINSPANNING']
        else:
            self.dbase_df['OCR_DSS'] = 1.0
    else:
        if self.dbase_df['ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL'] == 'OC':
            self.dbase_df['OCR_DSS'] = self.dbase_df['ANA_GRENSSPANNING_REKEN'] / self.dbase_df['ANA_TERREINSPANNING']
        else:
            self.dbase_df['OCR_DSS'] = 1.0
