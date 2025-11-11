from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
import plotly.graph_objects as go
from pv_tool.shansep_analysis.calc_parameters import *
from typing import Optional, List
from pv_tool.shansep_analysis.globals import (TEXTUAL_NAMES, TEXTUAL_NAMES_DSS, NEW_COLUMN_NAMES)
from pandas import DataFrame
import numpy as np


def add_proefresultaten_sv_su(self: SHANSEP):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    boring_monsternummer = self.shansep_data_df_oc.index

    x_proefresultaten = self.shansep_data_df_oc['S\'v']
    y_proefresultaten = self.shansep_data_df_oc['Su']

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

def add_proefresultaten_ln_ocr_ln_s(self: SHANSEP):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    boring_monsternummer = self.shansep_data_df_oc.index

    x_proefresultaten = self.shansep_data_df_nc_oc['LN(OCR)']
    y_proefresultaten = self.shansep_data_df_nc_oc['LN(su/svc)']

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


def get_extra_data(self: SHANSEP, investigationgroups_extra: Optional[List]):
    if self.analysis_type in ['TXT_S_POP', 'TXT_su_tabel']:
        dataset_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
    elif self.analysis_type in ['DSS_S_POP', 'DSS_su_tabel']:
        dataset_df = self.dbase_df[self.dbase_df['ALG__DSS']]
    else:
        raise ValueError(f"analysis type for extra dataset not right: {self.analysis_type}")

    dataset_df = dataset_df[
        dataset_df['PV_NAAM'].isin(investigationgroups_extra)]
    if self.analysis_type in ['DSS_S_POP', 'DSS_su_tabel']:
        dataset_df = dataset_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])]
    else:
        dataset_df = dataset_df[TEXTUAL_NAMES.get(self.effective_stress, [])]
    dataset_df.columns = NEW_COLUMN_NAMES
    return dataset_df


def add_extra_proefresultaten(self: SHANSEP, extra_groepen: Optional[List]):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    df = get_extra_data(self, investigationgroups_extra=extra_groepen)
    boring_monsternummer = df.index

    n=0
    for naam in df['PV_NAAM'].unique():

        sub_df = df[df['PV_NAAM'] == naam]
        x_extra_proefresultaten = sub_df['S\'v']
        y_extra_proefresultaten = sub_df['Su']

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


def add_5pr_bovengrens_sv_su(self: SHANSEP):
    """Deze functie voegt de 5% bovengrens toe aan de figuur."""
    x_5pr = self.shansep_data_df_oc['s\'']
    y_5pr = self.shansep_data_df_oc['5pr_bovengrens']

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

def add_5pr_ondergrens_sv_su(self: SHANSEP):
    """Deze functie voegt de 5% bovengrens toe aan de figuur."""
    x_5pr = self.shansep_data_df_oc['s\'']
    y_5pr = self.shansep_data_df_oc['5pr_ondergrens']

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

def add_5pr_bovengrens_ln_ocr_ln_s(self: SHANSEP):
    """Deze functie voegt de 5% bovengrens toe aan de figuur."""
    x_5pr = self.shansep_data_df_nc_oc['s\'']
    y_5pr = self.shansep_data_df_nc_oc['5pr_bovengrens']

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

def add_5pr_ondergrens_ln_ocr_ln_s(self: SHANSEP):
    """Deze functie voegt de 5% bovengrens toe aan de figuur."""
    x_5pr = self.shansep_data_df_nc_oc['s\'']
    y_5pr = self.shansep_data_df_nc_oc['5pr_ondergrens']

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

def add_fysische_realiseerbare_ondergrens_sv_su(self: SHANSEP):
    """Deze functie voegt de fysische realiseerbare ondergrens toe aan de figuur."""
    raaklijn_kar_x1 = 0
    raaklijn_kar_x2 = self.shansep_data_df_oc['S\'v'].max() + 5


    raaklijn_kar_y1 = self.snijpunt_kar_handmatig + (raaklijn_kar_x1 * self.s_kar_handmatig)
    raaklijn_kar_y2 = self.snijpunt_kar_handmatig + (raaklijn_kar_x2 * self.s_kar_handmatig)

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


def add_lineair_fit_sv_su(self: SHANSEP):
    """Deze functie voegt de lineaire fit van de proefresultaten toe aan de figuur."""
    x1 = self.shansep_data_df_oc['S\'v'].min() + 5
    x2 = self.shansep_data_df_oc['S\'v'].max() + 5

    # lineaire fit helling berekenen
    helling = _get_helling_value(self.s_kar_handmatig) # TODO klopt dit?

    y1 = x1 * helling + self.snijpunt_kar_handmatig
    y2 = x2 * helling + self.snijpunt_kar_handmatig

    x = [x1, x2]
    y = [y1, y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Lineaire fit proefresultaten',
            line=dict(color='green', width=2),
        )
    )

def add_lineair_fit_ln_ocr_ln_s(self: SHANSEP):
    """Deze functie voegt de lineaire fit van de proefresultaten toe aan de figuur."""
    x1 = self.shansep_data_df_nc_oc['LN(OCR)'].min() + 0.1
    x2 = self.shansep_data_df_nc_oc['LN(OCR)'].max() + 0.1

    # lineaire fit helling berekenen
    helling = _get_helling_value(self.e_a2_nc_oc) # TODO klopt dit?

    y1 = x1 * helling + self.e_a1_nc_oc
    y2 = x2 * helling + self.e_a1_nc_oc

    x = [x1, x2]
    y = [y1, y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Lineaire fit proefresultaten',
            line=dict(color='green', width=2),
        )
    )

def add_karakteristieke_lijn_sv_su(self: SHANSEP):
    """Deze functie voegt de karakteristieke lijn toe aan de figuur."""
    x1 = 0
    x2 = self.shansep_data_df_oc['S\'v'].max() + 5

    helling = _get_helling_value(self.s_kar_handmatig)
    y1 = x1 + self.snijpunt_kar_handmatig
    y2 = self.snijpunt_kar_handmatig + (x2 * self.s_kar_handmatig)

    x = [x1, x2]
    y = [y1, y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Karakteristieke lijn',
            line=dict(color='black', width=3),
        )
    )

def add_shansep_lijn(self: SHANSEP):


    formule_gem = 0 # TODO invullen
    x = [0.1, 1, 5, 10, 20, 30, self.shansep_data_df_oc['S\'v'].max()]
    shansep_kar = [self.s_kar_handmatig * x  * ((self.pop_kar_handmatig*x)/x) ** self.m_kar_handmatig for x in x]
    shansep_gem = [self.s_gem_handmatig * x  * ((self.pop_gem_handmatig*x)/x) ** self.m_gem_handmatig for x in x]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=shansep_gem,
            mode='lines',
            name='SHANSEP gemiddelde lijn',
            line=dict(color='pink', width=2, dash='dot')
        )
    )

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=shansep_kar,
            mode='lines',
            name='SHANSEP karakteristieke lijn',
            line=dict(color='pink', width=2)
        )
    )

# def add_gemiddelde(self: SHANSEP):
#     """Deze functie voegt de gemiddelde waarden toe aan de figuur."""
#     x1 = self.shansep_analyses_data_df['S\''].min() + 5
#     x2 = self.shansep_analyses_data_df['S\''].max() + 5
#
#     if self.cohesie_gem_handmatig is not None:
#         helling = _get_helling_value(self.helling_gecorrigeerd)
#         y1 = x1 * helling + self.cohesie_gem_handmatig
#         y2 = x2 * helling + self.cohesie_gem_handmatig
#         print('gemiddelde gebaseerd op helling gecorrigeerd en cohesie gem handmatig')
#     else:
#         helling = _get_helling_value(self.helling_gecorrigeerd)
#         y1 = x1 * helling + self.eerste_benadering_a1_gem
#         y2 = x2 * helling + self.eerste_benadering_a1_gem
#         print('gemiddelde gebaseerd op helling gecorrigeerd en eerste benadering a1 gem')
#
#     x = [x1, x2]
#     y = [y1, y2]
#
#     self.figure.add_trace(
#         go.Scatter(
#             x=x,
#             y=y,
#             mode='lines',
#             name='gemiddelde',
#             line=dict(color='orange', width=2),
#         )
#     )
#
# def add_gemiddelde_sh(self: SHANSEP):
#     """Deze functie voegt de gemiddelde waarden toe aan de figuur."""
#     x1 = self.shansep_analyses_data_df['S\''].min() + 5
#     x2 = self.shansep_analyses_data_df['S\''].max() + 5
#     y1 = x1 * calc_a2_phi_gem_sh(self)
#     y2 = x2 * calc_a2_phi_gem_sh(self)
#
#     x = [x1, x2]
#     y = [y1, y2]
#
#     self.figure.add_trace(
#         go.Scatter(
#             x=x,
#             y=y,
#             mode='lines',
#             name='Raaklijn gemiddeld',
#             line=dict(color='orange', width=2)
#         )
#     )

def _get_marker_direction(self, stress_df):
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

        dx = stress_df['S\'v'].iloc[1] - stress_df['S\'v'].iloc[0]
        dy = stress_df['Su'].iloc[1] - stress_df['Su'].iloc[0]

        # Bepaal dominante richting
        if abs(dx) > abs(dy):
            return 'triangle-right' if dx > 0 else 'triangle-left'
        else:
            return 'triangle-up' if dy > 0 else 'triangle-down'

def add_stress_paths(self: SHANSEP, sample_stress_paths: dict) -> None:
    """
    Plot de spanningspaden voor alle beschikbare effective stress waarden.
    Verbindt de punten van verschillende rekpercentages voor hetzelfde monster.

    Parameters
    ----------
    sample_stress_paths : dict
        Dictionary met als key de monster naam en als value een DataFrame met kolommen
        'S\'', 'T' en 'stress_state' voor de spanningswaarden
    """
    first_sample = True
    for sample_name, stress_df in sample_stress_paths.items():
        # Bepaal de richting van de marker
        marker_symbol = _get_marker_direction(self, stress_df=stress_df)

        # Voeg de spanningspad lijn toe voor dit monster
        self.figure.add_trace(
            go.Scatter(
                x=stress_df['S\'v'],
                y=stress_df['Su'],
                mode='lines+markers',
                line=dict(color='lightgray', width=1),
                marker=dict(color='lightgray', size=1),
                name='s\'v-su curve' if first_sample else f'Spanningspad {sample_name}',
                text=[f"{sample_name} - {state}<br>S\':{s:.1f}, T:{t:.1f}"
                      for state, s, t in zip(stress_df['stress_state'], stress_df['S\'v'], stress_df['Su'])],
                hoverinfo='text',
                showlegend=first_sample
            )
        )

        # Voeg het eerste punt toe met een speciaal symbool
        self.figure.add_trace(
            go.Scatter(
                x=[stress_df['S\'v'].iloc[0]],
                y=[stress_df['Su'].iloc[0]],
                mode='markers',
                marker=dict(
                    symbol=marker_symbol,
                    size=7,
                    color='gray'
                ),
                name='K0' if first_sample else f'Start {sample_name}',
                text = f"""{sample_name} - {stress_df['stress_state'].iloc[0]}<br>S'v:{stress_df["S\'v"].iloc[0]:.1f}, Su:{stress_df['Su'].iloc[0]:.1f}""",
                hoverinfo='text',
                showlegend=first_sample
            )
        )

        first_sample = False


def set_layout_sv_su(self: SHANSEP):
    """
    Stelt de layout van de figuur in met titel en as-labels.

    De figuurgrootte is geoptimaliseerd voor zowel schermdisplay als PDF-export.
    """
    title = f'Bepaling S en POP uit {self.analysis_type} proef'

    xas_title = '\u03C3 \'v [kPa]'
    yas_title = 'su [kPa]'

    legend_title = 'Legenda'
    self.figure.update_layout(
        width=1280,
        height=720,
        title=title if self.show_title else None,
        xaxis_title=xas_title,
        yaxis_title=yas_title,
        legend_title=legend_title,
        margin=dict(t=100, r=50, b=100, l=50)
    )

def set_layout_ln_ocr_ln_s(self: SHANSEP):
    """
    Stelt de layout van de figuur in met titel en as-labels.

    De figuurgrootte is geoptimaliseerd voor zowel schermdisplay als PDF-export.
    """
    title = f'Bepaling op basis van S en m op {self.analysis_type} proef'

    xas_title = 'LN(OCR) [-]'
    yas_title = 'LN(su/sv) [-]'

    legend_title = 'Legenda'
    self.figure.update_layout(
        width=1280,
        height=720,
        title=title if self.show_title else None,
        xaxis_title=xas_title,
        yaxis_title=yas_title,
        legend_title=legend_title,
        margin=dict(t=100, r=50, b=100, l=50)
    )
