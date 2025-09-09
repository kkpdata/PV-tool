from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
import plotly.graph_objects as go
from pv_tool.cphi_analysis.calc_parameters import *
from typing import Optional, List
from pv_tool.cphi_analysis.globals import (TEXTUAL_NAMES, TEXTUAL_NAMES_DSS, NEW_COLUMN_NAMES)
from pandas import DataFrame
import numpy as np


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

    # Changed the conditions to handle cohesie_kar_handmatig=0 correctly
    has_phi_kar = self.phi_kar_handmatig is not None
    has_cohesie_kar = self.cohesie_kar_handmatig is not None  # Now 0 will be considered as "has value"

    if has_phi_kar and has_cohesie_kar:
        raaklijn_kar_y1 = self.cohesie_kar_handmatig + (raaklijn_kar_x1 * self.phi_kar_handmatig)
        raaklijn_kar_y2 = self.cohesie_kar_handmatig + (self.phi_kar_handmatig * raaklijn_kar_x2)
        print('fysisch realiseerbare ondergrens gebaseerd op phi kar handmatig en cohesie kar handmatig')
    elif not has_phi_kar and has_cohesie_kar:
        raaklijn_kar_y1 = self.cohesie_kar_handmatig + (raaklijn_kar_x1 * self.eerste_benadering_a2_kar)
        raaklijn_kar_y2 = self.cohesie_kar_handmatig + (self.eerste_benadering_a2_kar * raaklijn_kar_x2)
        print('fysisch realiseerbare ondergrens gebaseerd op eerste benadering a2 kar en cohesie handmatig')
    elif has_phi_kar and not has_cohesie_kar:
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


def _get_helling_value(helling):
    """Helper function om de juiste waarde uit helling te halen, ongeacht of het een float of array is."""
    if isinstance(helling, (list, np.ndarray)):
        return float(helling[0])
    return float(helling)

def add_gemiddelde(self: CPhiAnalyse):
    """Deze functie voegt de gemiddelde waarden toe aan de figuur."""
    x1 = self.cphi_analyses_data_df['S\''].min() + 5
    x2 = self.cphi_analyses_data_df['S\''].max() + 5

    if self.cohesie_gem_handmatig is not None:
        helling = _get_helling_value(self.helling_gecorrigeerd)
        y1 = x1 * helling + self.cohesie_gem_handmatig
        y2 = x2 * helling + self.cohesie_gem_handmatig
        print('gemiddelde gebaseerd op helling gecor en cohesie gem handmatig')
    else:
        helling = _get_helling_value(self.helling_gecorrigeerd)
        y1 = x1 * helling + self.eerste_benadering_a1_gem
        y2 = x2 * helling + self.eerste_benadering_a1_gem
        print('gemiddelde gebaseerd op helling gecor en eerste benadering a1 gem')

    x = [x1, x2]
    y = [y1, y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='gemiddelde',
            line=dict(color='orange', width=2),
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
            name='Raaklijn gemiddeld',
            line=dict(color='orange', width=2)
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

def plot_stress_paths(self: CPhiAnalyse, data_df: DataFrame) -> None:
    """
    Plot de spanningspaden voor alle beschikbare effective stress waarden.
    Verbindt de punten van verschillende rekpercentages voor hetzelfde monster.

    Parameters
    ----------
    data_df : DataFrame
        DataFrame met de kolommen 'PV_NAAM', 'S\'' en 'T' voor verschillende rekpercentages
    """
    # Groepeer de data per monster
    for sample_name in data_df['PV_NAAM'].unique():
        sample_data = data_df[data_df['PV_NAAM'] == sample_name].copy()
        # Sorteer de data op S' om een logische verbinding te maken
        sample_data = sample_data.sort_values('S\'')

        # Voeg het eerste punt toe met een speciaal symbool
        self.figure.add_trace(
            go.Scatter(
                x=[sample_data['S\''].iloc[0]],
                y=[sample_data['T'].iloc[0]],
                mode='markers',
                marker=dict(
                    symbol='star',
                    size=10,
                    color='blue'
                ),
                name=f'Start {sample_name}',
                showlegend=True
            )
        )

        # Voeg de spanningspad lijn toe voor dit monster
        self.figure.add_trace(
            go.Scatter(
                x=sample_data['S\''],
                y=sample_data['T'],
                mode='lines+markers',
                line=dict(color='lightgray', width=1),
                marker=dict(color='black', size=2),
                name=f'Spanningspad {sample_name}',
                text=[f"{sample_name} - S\':{s:.1f}, T:{t:.1f}" for s, t in zip(sample_data['S\''], sample_data['T'])],
                hoverinfo='text'
            )
        )

    self.figure.update_layout(
        xaxis_title="S' [kPa]",
        yaxis_title="T [kPa]",
        title="Spanningspaden"
    )
