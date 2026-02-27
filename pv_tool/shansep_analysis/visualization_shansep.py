from __future__ import annotations
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
import plotly.graph_objects as go
from typing import Optional, List
from pv_tool.shansep_analysis.globals import (TEXTUAL_NAMES, TEXTUAL_NAMES_DSS, NEW_COLUMN_NAMES)
import numpy as np


def add_proefresultaten_sv_su(self: SHANSEP):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    boring_monsternummer = self.shansep_data_df_oc.index

    x_proefresultaten = self.shansep_data_df_oc['S\'v']
    y_proefresultaten = self.shansep_data_df_oc['Su']

    self.figure_sv_su.add_trace(
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

    self.figure_sv_su_nc.add_trace(
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

    self.figure_ln_ocr_ln_s.add_trace(
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
    if self.analysis_type in ['TXT_S_POP']:
        dataset_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
    elif self.analysis_type in ['DSS_S_POP']:
        dataset_df = self.dbase_df[self.dbase_df['ALG__DSS']]
    else:
        raise ValueError(f"analysis type for extra dataset not right: {self.analysis_type}")

    dataset_df = dataset_df[
        dataset_df['PV_NAAM'].isin(investigationgroups_extra)]
    if self.analysis_type in ['DSS_S_POP']:
        dataset_df = dataset_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])]
    else:
        dataset_df = dataset_df[TEXTUAL_NAMES.get(self.effective_stress, [])]
    dataset_df.columns = NEW_COLUMN_NAMES
    return dataset_df


def add_extra_proefresultaten_sv_su(self: SHANSEP, extra_groepen: Optional[List]):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    df = get_extra_data(self, investigationgroups_extra=extra_groepen)
    df = df[df['consolidatietype'] == 'OC'].copy()
    boring_monsternummer = df.index

    n = 0
    for naam in df['PV_NAAM'].unique():
        sub_df = df[df['PV_NAAM'] == naam]
        x_extra_proefresultaten = sub_df['S\'v']
        y_extra_proefresultaten = sub_df['Su']

        self.figure_sv_su.add_trace(
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


def add_extra_proefresultaten_ln_ocr_ln_s(self: SHANSEP, extra_groepen: Optional[List]):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    df = get_extra_data(self, investigationgroups_extra=extra_groepen)
    boring_monsternummer = df.index

    # paar zaken berekenen van deze nieuwe data
    df.loc[:, 'LN(OCR)'] = (
        df['OCR'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))

    df.loc[:, 'S'] = df['Su'] / df['S\'v']

    df.loc[:, 'LN(su/svc)'] = (
        df['S'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))

    n = 0
    for naam in df['PV_NAAM'].unique():
        sub_df = df[df['PV_NAAM'] == naam]
        x_extra_proefresultaten = sub_df['LN(OCR)']
        y_extra_proefresultaten = sub_df['LN(su/svc)']

        self.figure_ln_ocr_ln_s.add_trace(
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


def add_extra_proefresultaten_sv_su_nc(self: SHANSEP, extra_groepen: Optional[List]):
    """Deze functie voegt de proefresultaten toe aan de figuur."""
    df = get_extra_data(self, investigationgroups_extra=extra_groepen)

    df = df[df['consolidatietype'] == 'NC'].copy()

    boring_monsternummer = df.index

    n = 0
    for naam in df['PV_NAAM'].unique():
        sub_df = df[df['PV_NAAM'] == naam]
        x_extra_proefresultaten = sub_df['S\'v']
        y_extra_proefresultaten = sub_df['Su']

        self.figure_sv_su_nc.add_trace(
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

    self.figure_sv_su.add_trace(
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

    self.figure_sv_su.add_trace(
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

    self.figure_ln_ocr_ln_s.add_trace(
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

    self.figure_ln_ocr_ln_s.add_trace(
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

    self.figure_sv_su.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Fysisch realiseerbare ondergrens',
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

    self.figure_sv_su_nc.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Fysisch realiseerbare ondergrens',
            line=dict(color='black', width=2),
        )
    )


def _get_helling_value(helling):
    """Helper function om de juiste waarde uit helling te halen, ongeacht of het een float of array is."""
    if isinstance(helling, (list, np.ndarray)):
        return float(helling[0])
    return float(helling)


def add_linear_fit_sv_su(self: SHANSEP):
    """Deze functie voegt de lineaire fit van de proefresultaten toe aan de figuur."""
    x1 = self.shansep_data_df_oc['S\'v'].min()
    x2 = self.shansep_data_df_oc['S\'v'].max()

    # lineaire fit helling berekenen
    x_data = self.shansep_data_df_oc['S\'v'].values
    y_data = self.shansep_data_df_oc['Su'].values
    helling, intercept = np.polyfit(x_data, y_data, 1)

    y1 = x1 * helling + intercept
    y2 = x2 * helling + intercept

    x = [x1, x2]
    y = [y1, y2]

    self.figure_sv_su.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Lineaire fit proefresultaten',
            line=dict(color='green', width=2),
        )
    )


def add_linear_fit_sv_su_nc(self: SHANSEP):
    """Deze functie voegt de lineaire fit van de proefresultaten toe aan de figuur door de oorsprong."""
    x = [0, self.shansep_data_df_nc['S\'v'].max()]
    s_gem = self.exp_gem_ln_su_svc_nc
    shansep_gem = [s_gem * xi for xi in x]

    self.figure_sv_su_nc.add_trace(
        go.Scatter(
            x=x,
            y=shansep_gem,
            mode='lines',
            name='Lineaire fit proefresultaten',
            line=dict(color='green', width=2),
        )
    )


def add_linear_fit_ln_ocr_ln_s(self: SHANSEP):
    """Deze functie voegt de lineaire fit van de proefresultaten toe aan de figuur."""
    x1 = self.shansep_data_df_nc_oc['LN(OCR)'].min()
    x2 = self.shansep_data_df_nc_oc['LN(OCR)'].max()

    x_data = self.shansep_data_df_nc_oc['LN(OCR)'].values
    y_data = self.shansep_data_df_nc_oc['LN(su/svc)'].values
    helling, intercept = np.polyfit(x_data, y_data, 1)

    y1 = x1 * helling + intercept
    y2 = x2 * helling + intercept

    x = [x1, x2]
    y = [y1, y2]

    self.figure_ln_ocr_ln_s.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Lineaire fit proefresultaten',
            line=dict(color='green', width=2),
        )
    )


def add_shansep_lijn_sv_su(self: SHANSEP):
    x = self.sutabel['S\'v [kPa]'].tolist()
    shansep_kar = self.sutabel['Su in-situ karakteristiek'].tolist()
    shansep_gem = self.sutabel['Su in-situ gemiddeld'].tolist()

    self.figure_sv_su.add_trace(
        go.Scatter(
            x=x,
            y=shansep_gem,
            mode='lines',
            name='SHANSEP gemiddelde lijn',
            line=dict(color='purple', width=2, dash='dot')
        )
    )

    self.figure_sv_su.add_trace(
        go.Scatter(
            x=x,
            y=shansep_kar,
            mode='lines',
            name='SHANSEP karakteristieke lijn',
            line=dict(color='purple', width=2)
        )
    )


def add_shansep_lijn_sv_su_nc(self: SHANSEP):
    if self.sutabel_nc is None:
        self.calculate_sutabel_nc()
    x = [0, self.shansep_data_df_nc['S\'v'].max()]
    s_kar = self.s_kar_handmatig
    s_gem = self.s_gem_handmatig
    shansep_kar = [s_kar * xi for xi in x]
    shansep_gem = [s_gem * xi for xi in x]

    self.figure_sv_su_nc.add_trace(
        go.Scatter(
            x=x,
            y=shansep_gem,
            mode='lines',
            name='SHANSEP gemiddelde lijn',
            line=dict(color='purple', width=2, dash='dot')
        )
    )

    self.figure_sv_su_nc.add_trace(
        go.Scatter(
            x=x,
            y=shansep_kar,
            mode='lines',
            name='SHANSEP karakteristieke lijn',
            line=dict(color='purple', width=2)
        )
    )


def add_5pr_ondergrens_sv_su_nc(self: SHANSEP):
    x = [0, self.shansep_data_df_nc['S\'v'].max()]
    s_onder = self.exp_kar_ln_su_svc_nc
    shansep_onder = [s_onder * xi for xi in x]

    self.figure_sv_su_nc.add_trace(
        go.Scatter(
            x=x,
            y=shansep_onder,
            mode='lines',
            name='5% ondergrens',
            line=dict(color='black', width=1, dash='dash')
        )
    )


def add_5pr_bovengrens_sv_su_nc(self: SHANSEP):
    x = [0, self.shansep_data_df_nc['S\'v'].max()]
    # s_boven = self.exp_gem_ln_su_svc_nc + (self.exp_gem_ln_su_svc_nc - self.exp_kar_ln_su_svc_nc)
    s_boven = self.exp_kar_ln_su_svc_nc_boven  # TODO: checken of dit klopt
    shansep_boven = [s_boven * xi for xi in x]

    self.figure_sv_su_nc.add_trace(
        go.Scatter(
            x=x,
            y=shansep_boven,
            mode='lines',
            name='5% bovengrens',
            line=dict(color='black', width=1, dash='dash')
        )
    )


def add_shansep_lijn_ln_ocr_ln_s(self: SHANSEP):
    s = [0, 1.01]

    a2gem = self.m_gem_handmatig
    a1gem = math.log(self.s_gem_handmatig)

    a2kar = self.m_kar_handmatig
    a1kar = math.log(self.s_kar_handmatig)

    t_gem = [a1gem + (x * a2gem) for x in s]
    t_kar = [a1kar + (x * a2kar) for x in s]

    self.figure_ln_ocr_ln_s.add_trace(
        go.Scatter(
            x=s,
            y=t_gem,
            mode='lines',
            name='SHANSEP gemiddelde lijn',
            line=dict(color='purple', width=2, dash='dot')
        )
    )

    self.figure_ln_ocr_ln_s.add_trace(
        go.Scatter(
            x=s,
            y=t_kar,
            mode='lines',
            name='SHANSEP karakteristieke lijn',
            line=dict(color='purple', width=2)
        )
    )


def set_layout_sv_su(self: SHANSEP):
    """
    Stelt de layout van de figuur in met titel en as-labels.

    De figuurgrootte is geoptimaliseerd voor zowel schermdisplay als PDF-export.
    """
    title = f'Bepaling S en POP uit {self.analysis_type}'

    xas_title = "σ'ᵥ [kPa]"
    yas_title = "sᵤ [kPa]"

    legend_title = 'Legenda'
    self.figure_sv_su.update_layout(
        width=1152,
        height=648,
        title=title if self.show_title else None,
        xaxis_title=xas_title,
        yaxis_title=yas_title,
        yaxis=dict(rangemode='tozero'),
        legend_title=legend_title,
        margin=dict(t=100, r=50, b=100, l=50)
    )


def set_layout_ln_ocr_ln_s(self: SHANSEP):
    """
    Stelt de layout van de figuur in met titel en as-labels.

    De figuurgrootte is geoptimaliseerd voor zowel schermdisplay als PDF-export.
    """
    title = f'Bepaling op basis van S en m op {self.analysis_type}'

    xas_title = "LN(OCR) [-]"
    yas_title = "LN(sᵤ/σ'ᵥ) [-]"

    legend_title = 'Legenda'
    self.figure_ln_ocr_ln_s.update_layout(
        width=1152,
        height=648,
        title=title if self.show_title else None,
        xaxis_title=xas_title,
        yaxis_title=yas_title,
        legend_title=legend_title,
        margin=dict(t=100, r=50, b=100, l=50)
    )


def set_layout_sv_su_nc(self: SHANSEP):
    """
    Stelt de layout van de figuur in met titel en as-labels.

    De figuurgrootte is geoptimaliseerd voor zowel schermdisplay als PDF-export.
    """
    title = f'Bepaling S en POP uit {self.analysis_type} alleen NC-proeven'

    xas_title = r"$\sigma'_{v} [kPa]$"
    yas_title = r'$s_{u} [kPa]$'

    legend_title = 'Legenda'
    self.figure_sv_su_nc.update_layout(
        width=1152,
        height=648,
        title=title if self.show_title else None,
        xaxis_title=xas_title,
        yaxis_title=yas_title,
        legend_title=legend_title,
        margin=dict(t=100, r=50, b=100, l=50)
    )
