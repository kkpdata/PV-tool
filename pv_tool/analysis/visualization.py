from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pv_tool.analysis.c_phi_analysis import CPhiAnalyse
import plotly.graph_objects as go
from pv_tool.analysis.variables import *
from pv_tool.analysis.calc_parameters import *


def add_proefresultaten(self: CPhiAnalyse):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    boring_monsternummer = self.cphi_analyses_data_df['ALG__BORING_MONSTERNR_ID']

    x_proefresultaten = self.cphi_analyses_data_df['S\'']
    y_proefresultaten = self.cphi_analyses_data_df['T']

    self.figure.add_trace(
        go.Scatter(
            x=x_proefresultaten,
            y=y_proefresultaten,
            mode='markers',
            name='Proefresultaten',
            text=boring_monsternummer,
            hoverinfo='text'
        )
    )

def add_extra_proefresultaten(self: CPhiAnalyse):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    boring_monsternummer = self.cphi_analyses_data_df['ALG__BORING_MONSTERNR_ID']

    x_proefresultaten = self.cphi_analyses_data_df['S\'']  # TODO: hier moet nog iets anders komen aangezien het om extra resultaten gaat
    y_proefresultaten = self.cphi_analyses_data_df['T']  # TODO: hier moet nog iets anders komen aangezien het om extra resultaten gaat

    self.figure.add_trace(
        go.Scatter(
            x=x_proefresultaten,
            y=y_proefresultaten,
            mode='markers',
            name='Proefresultaten',
            text=boring_monsternummer,
            hoverinfo='text'
        )
    )

def add_5pr_bovengrens(self: CPhiAnalyse):
    """Deze functie voegt de 5% bovengrens toe aan de figuur."""
    x_5pr = self.cphi_analyses_data_df['s\'']
    # print('x_5pr', x_5pr)
    y_5pr = self.cphi_analyses_data_df['5pr_bovengrens_cor']
    # print('y_5pr', y_5pr)

    self.figure.add_trace(
        go.Scatter(
            x=x_5pr,
            y=y_5pr,
            mode='lines',
            name='5% bovengrens'
        )
    )


def add_fysische_realiseerbare_ondergrens(self: CPhiAnalyse):
    """Deze functie voegt de fysische realiseerbare ondergrens toe aan de figuur."""
    raaklijn_kar_x1 = 0
    raaklijn_kar_x2 = self.cphi_analyses_data_df['S\''].max() + 5

    raaklijn_kar_y1 = self.cohesie_kar_handmatig + (raaklijn_kar_x1 * self.phi_kar_handmatig)
    raaklijn_kar_y2 = self.cohesie_kar_handmatig + (self.phi_kar_handmatig * raaklijn_kar_x2)

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

    y1 = x1 * helling_gecor(self) + self.cohesie_gem_handmatig
    y2 = x2 * helling_gecor(self) + self.cohesie_gem_handmatig

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


def set_layout(self: CPhiAnalyse):
    """Voegt een titel en labels toe."""
    title = 'TXT C-Phi analyse'
    xas_title = 's\' [kPa]'
    yas_title = 't [kPa]'
    legend_title = 'Legenda'
    self.figure.update_layout(
        title=title,
        xaxis_title=xas_title,
        yaxis_title=yas_title,
        legend_title=legend_title
    )


