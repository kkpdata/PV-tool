from __future__ import annotations
from typing import TYPE_CHECKING
import math
import numpy as np

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
            name=f'Geanalyseerd: {self.investigation_groups[0]} (OC)',
            text=boring_monsternummer,
            hoverinfo='text'
        )
    )

def add_proefresultaten_sv_su_nc(self: SHANSEP):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    boring_monsternummer = self.shansep_data_df_nc.index

    x_proefresultaten = self.shansep_data_df_nc['S\'v']
    y_proefresultaten = self.shansep_data_df_nc['Su']

    self.figure.add_trace(
        go.Scatter(
            x=x_proefresultaten,
            y=y_proefresultaten,
            mode='markers',
            marker=dict(
                color='blue'
            ),
            name=f'Geanalyseerd: {self.investigation_groups[0]} (NC)',
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
    y_5pr = self.shansep_data_df_oc['5_pr_bovengrens']

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
    y_5pr = self.shansep_data_df_oc['5_pr_ondergrens']

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
    y_5pr = self.shansep_data_df_nc_oc['5_pr_bovengrens']

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
    y_5pr = self.shansep_data_df_nc_oc['5_pr_ondergrens']

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
            line=dict(color='black', width=2),
        )
    )

def add_fysische_realiseerbare_ondergrens_sv_su_nc(self: SHANSEP):
    """Deze functie voegt de fysische realiseerbare ondergrens toe aan de figuur."""
    raaklijn_kar_x1 = 0
    raaklijn_kar_x2 = self.shansep_data_df_nc['S\'v'].max() + 5

    raaklijn_kar_y1 = 0 + (raaklijn_kar_x1 * self.s_kar_handmatig)
    raaklijn_kar_y2 = 0 + (raaklijn_kar_x2 * self.s_kar_handmatig)

    x = [raaklijn_kar_x1, raaklijn_kar_x2]
    y = [raaklijn_kar_y1, raaklijn_kar_y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Fysische realiseerbare ondergrens',
            line=dict(color='black', width=2),
        )
    )


def _get_helling_value(helling):
    """Helper function om de juiste waarde uit helling te halen, ongeacht of het een float of array is."""
    if isinstance(helling, (list, np.ndarray)):
        return float(helling[0])
    return float(helling)


def add_lineair_fit_sv_su(self: SHANSEP):
    """Deze functie voegt de lineaire fit van de proefresultaten toe aan de figuur."""
    # Gebruik dezelfde x-range als de andere lijnen (5% grenzen) om overlap te voorkomen
    x1 = self.shansep_data_df_oc['S\'v'].min()
    x2 = self.shansep_data_df_oc['S\'v'].max()

    # lineaire fit helling berekenen
    x_data = self.shansep_data_df_oc['S\'v'].values
    y_data = self.shansep_data_df_oc['Su'].values
    # Gebruik numpy polyfit voor lineaire regressie (graad 1 = lineair)
    helling, intercept = np.polyfit(x_data, y_data, 1)

    # formula voor y1 en y2
    y1 = x1 * helling + intercept
    y2 = x2 * helling + intercept

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

def add_lineair_fit_sv_su_nc(self: SHANSEP):
    """Deze functie voegt de lineaire fit van de proefresultaten toe aan de figuur."""
    # Gebruik dezelfde x-range als de andere lijnen (5% grenzen) om overlap te voorkomen
    x1 = self.shansep_data_df_nc['S\'v'].min()
    x2 = self.shansep_data_df_nc['S\'v'].max()

    # lineaire fit helling berekenen
    x_data = self.shansep_data_df_nc['S\'v'].values
    y_data = self.shansep_data_df_nc['Su'].values
    # Gebruik numpy polyfit voor lineaire regressie (graad 1 = lineair)
    helling, intercept = np.polyfit(x_data, y_data, 1)

    # formula voor y1 en y2
    y1 = x1 * helling + intercept
    y2 = x2 * helling + intercept

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
    # Gebruik dezelfde x-range als de datapoints om overlap te voorkomen
    x1 = self.shansep_data_df_nc_oc['LN(OCR)'].min()
    x2 = self.shansep_data_df_nc_oc['LN(OCR)'].max()

    # lineaire fit helling berekenen
    x_data = self.shansep_data_df_nc_oc['LN(OCR)'].values
    y_data = self.shansep_data_df_nc_oc['LN(su/svc)'].values
    # Gebruik numpy polyfit voor lineaire regressie (graad 1 = lineair)
    helling, intercept = np.polyfit(x_data, y_data, 1)

    # formula voor y1 en y2
    y1 = x1 * helling + intercept
    y2 = x2 * helling + intercept

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

# def add_karakteristieke_lijn_sv_su(self: SHANSEP):
#     """Deze functie voegt de karakteristieke lijn toe aan de figuur."""
#     x1 = 0
#     x2 = self.shansep_data_df_oc['S\'v'].max() + 5
#
#     y1 = x1 + self.snijpunt_kar_handmatig
#     y2 = self.snijpunt_kar_handmatig + (x2 * self.s_kar_handmatig)
#
#     x = [x1, x2]
#     y = [y1, y2]
#
#     self.figure.add_trace(
#         go.Scatter(
#             x=x,
#             y=y,
#             mode='lines',
#             name='Karakteristieke lijn',
#             line=dict(color='black', width=3),
#         )
#     )

def add_shansep_lijn_sv_su(self: SHANSEP):
    x = self.sutabel['S\'v [kPa]'].tolist()
    shansep_kar = self.sutabel['Su in-situ karakteristiek'].tolist()
    shansep_gem = self.sutabel['Su in-situ gemiddeld'].tolist()

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=shansep_gem,
            mode='lines',
            name='SHANSEP gemiddelde lijn',
            line=dict(color='purple', width=2, dash='dot')
        )
    )

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=shansep_kar,
            mode='lines',
            name='SHANSEP karakteristieke lijn',
            line=dict(color='purple', width=2)
        )
    )

def add_shansep_lijn_sv_su_nc(self: SHANSEP):
    x = self.sutabel_nc['S\'v [kPa]'].tolist()
    shansep_kar = self.sutabel_nc['Su in-situ karakteristiek'].tolist()
    shansep_gem = self.sutabel_nc['Su in-situ gemiddeld'].tolist()

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=shansep_gem,
            mode='lines',
            name='SHANSEP gemiddelde lijn',
            line=dict(color='purple', width=2, dash='dot')
        )
    )

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=shansep_kar,
            mode='lines',
            name='SHANSEP karakteristieke lijn',
            line=dict(color='purple', width=2)
        )
    )

def add_shansep_lijn_ln_ocr_ln_s(self: SHANSEP):
    s = [0, 1.01]

    a2gem = self.m_gem_handmatig
    a1gem = math.log(self.s_gem_handmatig)

    a2kar = self.m_kar_handmatig
    a1kar = math.log(self.s_kar_handmatig)

    t_gem = [a1gem+(x*a2gem) for x in s]
    t_kar = [a1kar+(x*a2kar) for x in s]


    self.figure.add_trace(
        go.Scatter(
            x=s,
            y=t_gem,
            mode='lines',
            name='SHANSEP gemiddelde lijn',
            line=dict(color='purple', width=2, dash='dot')
        )
    )

    self.figure.add_trace(
        go.Scatter(
            x=s,
            y=t_kar,
            mode='lines',
            name='SHANSEP karakteristieke lijn',
            line=dict(color='purple', width=2)
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

    xas_title = r"$\sigma'_{v} [kPa]$"
    yas_title = r'$s_{u} [kPa]$'

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

    xas_title = r'$LN(OCR) [-]$'
    yas_title = r"$LN(s_{u}/\sigma'_{v}) [-]$"

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


# ========================== SUTABEL VISUALIZATION FUNCTIONS ==========================

def add_proefresultaten_ln_sv_ln_su_sutabel(self: SHANSEP):
    """Voegt de proefresultaten toe aan de figuur voor sutabel analyse (ln(s'v) vs ln(su))."""
    boring_monsternummer = self.shansep_data_df_sutabel.index

    x_proefresultaten = self.shansep_data_df_sutabel['ln(s\'v)']
    y_proefresultaten = self.shansep_data_df_sutabel['ln(su)']

    self.figure.add_trace(
        go.Scatter(
            x=x_proefresultaten,
            y=y_proefresultaten,
            mode='markers',
            marker=dict(
                color='blue'
            ),
            name=f'Geanalyseerd: {self.investigation_groups[0]} (OC)',
            text=boring_monsternummer,
            hoverinfo='text'
        )
    )


def add_lineair_fit_ln_sv_ln_su_sutabel(self: SHANSEP):
    """Voegt de lineaire fit toe aan de figuur voor sutabel analyse."""
    # Gebruik de min en max van ln(s'v) voor de lijn
    x1 = self.shansep_data_df_sutabel['ln(s\'v)'].min()
    x2 = self.shansep_data_df_sutabel['ln(s\'v)'].max()

    # Gebruik de berekende regressie parameters
    from pv_tool.shansep_analysis.variables import e_a2_sutabel, e_a1_sutabel
    a2 = e_a2_sutabel(self)
    a1 = e_a1_sutabel(self)

    # Bereken y-waarden met de regressievergelijking: ln(su) = a1 + a2 * ln(s'v)
    y1 = a1 + a2 * x1
    y2 = a1 + a2 * x2

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


def add_5pr_bovengrens_ln_sv_ln_su_sutabel(self: SHANSEP):
    """Voegt de 5% bovengrens toe aan de figuur voor sutabel analyse."""
    x_5pr = self.shansep_data_df_sutabel['s\'']
    y_5pr = self.shansep_data_df_sutabel['5_pr_bovengrens']

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


def add_5pr_ondergrens_ln_sv_ln_su_sutabel(self: SHANSEP):
    """Voegt de 5% ondergrens toe aan de figuur voor sutabel analyse."""
    x_5pr = self.shansep_data_df_sutabel['s\'']
    y_5pr = self.shansep_data_df_sutabel['5_pr_ondergrens']

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


def add_fysische_realiseerbare_ondergrens_ln_sv_ln_su_sutabel(self: SHANSEP):
    """Voegt de fysische realiseerbare ondergrens toe aan de figuur voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import a2_kar_sutabel, a1_kar_sutabel

    # Bereken de karakteristieke lijn: ln(su) = a1_kar + a2_kar * ln(s'v)
    x1 = self.shansep_data_df_sutabel['ln(s\'v)'].min()
    x2 = self.shansep_data_df_sutabel['ln(s\'v)'].max()

    a2_kar = a2_kar_sutabel(self)
    a1_kar = a1_kar_sutabel(self)

    y1 = a1_kar + a2_kar * x1
    y2 = a1_kar + a2_kar * x2

    x = [x1, x2]
    y = [y1, y2]

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Fysische realiseerbare ondergrens',
            line=dict(color='black', width=2),
        )
    )


def set_layout_ln_sv_ln_su_sutabel(self: SHANSEP):
    """Stelt de layout van de figuur in voor sutabel analyse (ln(s'v) vs ln(su))."""
    title = f'Sutabel-m analyse: ln(s\'v) vs ln(su) - {self.analysis_type} proef'

    xas_title = r"$\ln(\sigma'_{v}) [-]$"
    yas_title = r'$\ln(s_{u}) [-]$'

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


# ========================== SUTABEL SV-SU PLOT ==========================

def add_proefresultaten_sv_su_sutabel(self: SHANSEP):
    """Voegt de proefresultaten toe aan de figuur voor sutabel analyse (s'v vs su)."""
    boring_monsternummer = self.shansep_data_df_sutabel.index

    x_proefresultaten = self.shansep_data_df_sutabel['S\'v']
    y_proefresultaten = self.shansep_data_df_sutabel['Su']

    self.figure.add_trace(
        go.Scatter(
            x=x_proefresultaten,
            y=y_proefresultaten,
            mode='markers',
            marker=dict(
                color='blue'
            ),
            name=f'Geanalyseerd: {self.investigation_groups[0]} (OC)',
            text=boring_monsternummer,
            hoverinfo='text'
        )
    )


def add_sutabel_kar_line(self: SHANSEP):
    """
    Voegt de karakteristieke sutabel lijn toe aan de s'v vs su plot.

    Deze lijn wordt berekend met: su_kar = svgm_kar * (s'v)^(1-m_kar)
    """
    if self.sutabel_grafiek is None:
        return

    x = self.sutabel_grafiek["s'v [kPa]"].tolist()
    y = self.sutabel_grafiek["su_kar [kPa]"].tolist()

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Sutabel karakteristiek',
            line=dict(color='black', width=2)
        )
    )


def add_sutabel_gem_line(self: SHANSEP):
    """
    Voegt de gemiddelde sutabel lijn toe aan de s'v vs su plot.

    Deze lijn wordt berekend met: su_gem = svgm_gem * (s'v)^(1-m_gem)
    """
    if self.sutabel_grafiek is None:
        return

    x = self.sutabel_grafiek["s'v [kPa]"].tolist()
    y = self.sutabel_grafiek["su_gem [kPa]"].tolist()

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Sutabel gemiddeld',
            line=dict(color='purple', width=2, dash='dot')
        )
    )


def add_su_kar_fit_constante_vc(self: SHANSEP):
    """
    Voegt de karakteristieke su fit met constante s'vc toe aan de s'v vs su plot.

    Deze lijn wordt berekend met lognormale verdeling:
    su_kar_fit = LOGNORM.INV(0.05; ln(su_gem); STDEV_logn_CV)
    """
    if self.su_fit_constante_CV is None:
        return

    x = self.su_fit_constante_CV["s'v [kPa]"].tolist()
    y = self.su_fit_constante_CV["su_kar fit met constante CV [kPa]"].tolist()

    self.figure.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Su kar fit met constante CV',
            line=dict(color='red', width=2, dash='dashdot')
        )
    )


def set_layout_sv_su_sutabel(self: SHANSEP):
    """Stelt de layout van de figuur in voor sutabel analyse (s'v vs su)."""
    title = f'Sutabel-m analyse: s\'v vs su - {self.analysis_type} proef'

    xas_title = r"$\sigma'_{v} [kPa]$"
    yas_title = r'$s_{u} [kPa]$'

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
