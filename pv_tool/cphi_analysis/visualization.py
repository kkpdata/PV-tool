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
            marker=dict(
                color='blue'
            ),
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
    if self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
        dataset_df = dataset_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])]
    else:
        dataset_df = dataset_df[TEXTUAL_NAMES.get(self.effective_stress, [])]
    dataset_df.columns = NEW_COLUMN_NAMES
    return dataset_df


def add_extra_proefresultaten(self: CPhiAnalyse, extra_groepen: Optional[List]):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    df = get_extra_data(self, investigationgroups_extra=extra_groepen)
    boring_monsternummer = df.index

    n = 0
    for naam in df['PV_NAAM'].unique():
        sub_df = df[df['PV_NAAM'] == naam]
        x_extra_proefresultaten = sub_df['S\'']
        y_extra_proefresultaten = sub_df['T']

        self.figure.add_trace(
            go.Scatter(
                x=x_extra_proefresultaten,
                y=y_extra_proefresultaten,
                mode='markers',
                name=f'Extra: {extra_groepen[n]}',
                text=boring_monsternummer,
                hoverinfo='text'
            )
        )
        n += 1


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
            line=dict(
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

    has_phi_kar = self.phi_kar_handmatig is not None
    has_cohesie_kar = self.cohesie_kar_handmatig is not None

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
            name='Fysische realiseerbare ondergrens',
            line=dict(color='purple', width=2),
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
        print('gemiddelde gebaseerd op helling gecorrigeerd en cohesie gem handmatig')
    else:
        helling = _get_helling_value(self.helling_gecorrigeerd)
        y1 = x1 * helling + self.eerste_benadering_a1_gem
        y2 = x2 * helling + self.eerste_benadering_a1_gem
        print('gemiddelde gebaseerd op helling gecorrigeerd en eerste benadering a1 gem')

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


def _get_marker_direction(stress_df):
    """
        Bepaalt de richting van de marker op basis van het eerste segment van het spanningspad.

        Parameters
        ----------
        stress_df : DataFrame
            DataFrame met kolommen 'S\'' en 'T' voor de spanningswaarden

        Returns
        -------
        str
            Symbol naam voor de marker ('triangle-up', 'triangle-down', 'triangle-left', of 'triangle-right')
        """
    if len(stress_df) < 2:
        return 'triangle-up'

    dx = stress_df['S\''].iloc[1] - stress_df['S\''].iloc[0]
    dy = stress_df['T'].iloc[1] - stress_df['T'].iloc[0]

    # Bepaal dominante richting
    if abs(dx) > abs(dy):
        return 'triangle-right' if dx > 0 else 'triangle-left'
    else:
        return 'triangle-up' if dy > 0 else 'triangle-down'


def add_stress_paths(self: CPhiAnalyse, sample_stress_paths: dict) -> None:
    """
    Plot de spanningspaden voor alle beschikbare effective stress waarden.
    Verbindt de punten van verschillende rekpercentages voor hetzelfde monster.

    Parameters
    ----------
    self : CPhiAnalyse
        De CPhi-class wordt gebruikt als imput voor deze functie.
    sample_stress_paths : dict
        Dictionary met als key de monsternaam en als value een DataFrame met kolommen
        'S\'', 'T' en 'stress_state' voor de spanningswaarden
    """
    first_sample = True
    for sample_name, stress_df in sample_stress_paths.items():
        # Bepaal de richting van de marker
        marker_symbol = _get_marker_direction(stress_df=stress_df)

        # Voeg de spanningspad lijn toe voor dit monster
        self.figure.add_trace(
            go.Scatter(
                x=stress_df['S\''],
                y=stress_df['T'],
                mode='lines+markers',
                line=dict(color='lightgray', width=1),
                marker=dict(color='lightgray', size=1),
                name='s\'-t curve' if first_sample else f'Spanningspad {sample_name}',
                text=[f"{sample_name} - {state}<br>S\':{s:.1f}, T:{t:.1f}"
                      for state, s, t in zip(stress_df['stress_state'], stress_df['S\''], stress_df['T'])],
                hoverinfo='text',
                showlegend=first_sample,
                legendgroup='spanningspaden'  # Groepeer alle spanningspad traces
            )
        )

        # Voeg het eerste punt toe met een speciaal symbool
        self.figure.add_trace(
            go.Scatter(
                x=[stress_df['S\''].iloc[0]],
                y=[stress_df['T'].iloc[0]],
                mode='markers',
                marker=dict(
                    symbol=marker_symbol,
                    size=7,
                    color='gray'
                ),
                name='K0' if first_sample else f'Start {sample_name}',
                text=f"""{sample_name} - {stress_df['stress_state'].iloc[0]}<br>S':{stress_df["S'"].iloc[0]:.1f}, 
                T:{stress_df['T'].iloc[0]:.1f}""",
                hoverinfo='text',
                showlegend=first_sample,
                legendgroup='spanningspaden'  # Zelfde groep als de lijnen
            )
        )

        first_sample = False


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
        width=1152,
        height=648,
        title=title if self.show_title else None,
        xaxis_title=xas_title,
        yaxis_title=yas_title,
        legend_title=legend_title,
        margin=dict(t=100, r=50, b=100, l=50)
    )
