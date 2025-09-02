from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
import plotly.graph_objects as go
from pv_tool.cphi_analysis.calc_parameters import *
from typing import Optional, List
from pv_tool.cphi_analysis.globals import (TEXTUAL_NAMES, TEXTUAL_NAMES_DSS, NEW_COLUMN_NAMES)


def add_proefresultaten(self: CPhiAnalyse):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    boring_monsternummer = self.cphi_analyses_data_df.index

    x_proefresultaten = self.cphi_analyses_data_df['S\'']
    y_proefresultaten = self.cphi_analyses_data_df['T']

    self.figure.add_trace(
        go.Scatter(
            x=x_proefresultaten,
            y=y_proefresultaten,
            mode='markers',
            name=f'Geanalyseerd: {self.investigation_groups[0]}',
            text=boring_monsternummer,
            hoverinfo='text'
        )
    )


def get_extra_data(self: CPhiAnalyse, investigationgroups_extra: Optional[List]):
    if self.analysis_type in ['TXT_CPhi', 'TXT_SH']:
        dataset_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
    elif self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
        dataset_df = self.dbase_df[self.dbase_df['ALG__DSS']]
    else:
        raise ValueError(f"analysis type for extra dataset not right: {self.analysis_type}")

    dataset_df = dataset_df[
        dataset_df['PV_NAAM'].isin(investigationgroups_extra)]
    print(dataset_df)
    if self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
        dataset_df = dataset_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])]
        print(dataset_df)
    else:
        dataset_df = dataset_df[TEXTUAL_NAMES.get(self.effective_stress, [])]
        print(dataset_df)
    dataset_df.columns = NEW_COLUMN_NAMES
    return dataset_df


def add_extra_proefresultaten(self: CPhiAnalyse, extra_groepen: Optional[List]):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    df = get_extra_data(self, investigationgroups_extra=extra_groepen)
    boring_monsternummer = df.index

    x_extra_proefresultaten = df['S\'']
    y_extra_proefresultaten = df['T']

    self.figure.add_trace(
        go.Scatter(
            x=x_extra_proefresultaten,
            y=y_extra_proefresultaten,
            mode='markers',
            name=f'Extra: {extra_groepen[0]}',
            text=boring_monsternummer,
            hoverinfo='text'
        )
    )


def add_5pr_bovengrens(self: CPhiAnalyse):
    """Deze functie voegt de 5% bovengrens toe aan de figuur."""
    x_5pr = self.cphi_analyses_data_df['s\'']
    y_5pr = self.cphi_analyses_data_df['5pr_bovengrens_cor']

    self.figure.add_trace(
        go.Scatter(
            x=x_5pr,
            y=y_5pr,
            mode='lines',
            name='5% bovengrens',
            line=dict(
                color='black',
                width=1,
                dash='dash'
            )
        )
    )

def add_raaklijn_kar_boven(self: CPhiAnalyse):
    """Deze functie voegt de bovenste raaklijn van de schematiseringshandleiding methode toe aan de figuur."""
    x1 = 0
    x2 = self.cphi_analyses_data_df['S\''].max() + 5
    y1 = x1 * calc_a2_phi_kar_boven_sh(self)
    y2 = x2 * calc_a2_phi_kar_boven_sh(self)

    x = [x1, x2]
    y = [y1, y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Raaklijn boven',
            line=dict(
                color='black',
                width=1,
                dash='dash'
            )
        )
    )

def add_5pr_ondergrens(self: CPhiAnalyse):
    """Deze functie voegt de 5% bovengrens toe aan de figuur."""
    x_5pr = self.cphi_analyses_data_df['s\'']
    y_5pr = self.cphi_analyses_data_df['5pr_ondergrens_cor']

    self.figure.add_trace(
        go.Scatter(
            x=x_5pr,
            y=y_5pr,
            mode='lines',
            name='5% ondergrens',
            line=dict(
                color='black',
                width=1,
                dash='dash'
            )
        )
    )

def add_raaklijn_kar_onder(self: CPhiAnalyse):
    """Deze functie voegt de onderste raaklijn van de schematiseringshandleiding methode toe aan de figuur."""
    x1 = 0
    x2 = self.cphi_analyses_data_df['S\''].max() + 5
    y1 = x1 * calc_a2_phi_kar_onder_sh(self)
    y2 = x2 * calc_a2_phi_kar_onder_sh(self)

    x = [x1, x2]
    y = [y1, y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Raaklijn onder',
            line = dict(
                color='black',
                width=1,
                dash='dash'
            )
        )
    )


def add_fysische_realiseerbare_ondergrens(self: CPhiAnalyse):
    """Deze functie voegt de fysische realiseerbare ondergrens toe aan de figuur."""
    raaklijn_kar_x1 = 0
    raaklijn_kar_x2 = self.cphi_analyses_data_df['S\''].max() + 5

    if self.phi_kar_handmatig and self.cohesie_kar_handmatig:
        raaklijn_kar_y1 = self.cohesie_kar_handmatig + (raaklijn_kar_x1 * self.phi_kar_handmatig)
        raaklijn_kar_y2 = self.cohesie_kar_handmatig + (self.phi_kar_handmatig * raaklijn_kar_x2)
        print('fysisch realiseerbare ondergrens gebaseerd op phi kar handmatig en cohesie kar handmatig')
    elif not self.phi_kar_handmatig and self.cohesie_kar_handmatig:
        raaklijn_kar_y1 = self.cohesie_kar_handmatig + (raaklijn_kar_x1 * self.eerste_benadering_a2_kar)
        raaklijn_kar_y2 = self.cohesie_kar_handmatig + (self.eerste_benadering_a2_kar * raaklijn_kar_x2)
        print('fysisch realiseerbare ondergrens gebaseerd op eerste benadering a2 kar en cohesie handmatig')
    elif self.phi_kar_handmatig and not self.cohesie_kar_handmatig:
        raaklijn_kar_y1 = self.eerste_benadering_a1_kar + (raaklijn_kar_x1 * self.phi_kar_handmatig)
        raaklijn_kar_y2 = self.eerste_benadering_a1_kar + (self.phi_kar_handmatig * raaklijn_kar_x2)
        print('fysisch realiseerbare ondergrens gebaseerd op phi kar handmatig en eerste benadering a1')
    else:
        raaklijn_kar_y1 = self.eerste_benadering_a1_kar + (raaklijn_kar_x1 * self.eerste_benadering_a2_kar)
        raaklijn_kar_y2 = self.eerste_benadering_a1_kar + (self.eerste_benadering_a2_kar * raaklijn_kar_x2)
        print('fysisch realiseerbare ondergrens gebaseerd op eerste benadering a1 en eerste benadering a2')

    x = [raaklijn_kar_x1, raaklijn_kar_x2]
    y = [raaklijn_kar_y1, raaklijn_kar_y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Fysische realiseerbare ondergrens'
        )
    )


def add_gemiddelde(self: CPhiAnalyse):
    """Deze functie voegt de gemiddelde waarden toe aan de figuur."""
    x1 = self.cphi_analyses_data_df['S\''].min() + 5
    x2 = self.cphi_analyses_data_df['S\''].max() + 5

    if self.cohesie_gem_handmatig:
        y1 = x1 * helling_gecor(self) + self.cohesie_gem_handmatig
        y2 = x2 * helling_gecor(self) + self.cohesie_gem_handmatig
    else:
        y1 = x1 * helling_gecor(self) + self.eerste_benadering_a1_gem
        y2 = x2 * helling_gecor(self) + self.eerste_benadering_a1_gem

    x = [x1, x2]
    y = [y1, y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Gemiddelde'
        )
    )

def add_gemiddelde_sh(self: CPhiAnalyse):
    """Deze functie voegt de gemiddelde waarden toe aan de figuur."""
    x1 = self.cphi_analyses_data_df['S\''].min() + 5
    x2 = self.cphi_analyses_data_df['S\''].max() + 5
    y1 = x1 * calc_a2_phi_gem_sh(self)
    y2 = x2 * calc_a2_phi_gem_sh(self)

    x = [x1, x2]
    y = [y1, y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Raaklijn gemiddeld'
        )
    )

def set_layout(self: CPhiAnalyse):
    """
    Stelt de layout van de figuur in met titel en as-labels.

    De figuurgrootte is geoptimaliseerd voor zowel schermdisplay als PDF-export.
    """
    title = f'{self.analysis_type} analyse met {self.effective_stress} op {self.investigation_groups[0]}'
    if self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
        xas_title = '\u03C3 \' [kPa]'
        yas_title = '\u03C4 [kPa]'
    else:
        xas_title = 's\' [kPa]'
        yas_title = 't [kPa]'
    legend_title = 'Legenda'
    self.figure.update_layout(
        width=1200,  # Smaller base width for better scaling
        height=600,  # Adjusted height to maintain aspect ratio
        title=title,
        xaxis_title=xas_title,
        yaxis_title=yas_title,
        legend_title=legend_title,
        margin=dict(t=100, r=50, b=100, l=50)  # Adjusted margins for better layout
    )
