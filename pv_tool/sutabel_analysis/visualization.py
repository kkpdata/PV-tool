"""
Visualisatie functies voor Sutabel-m analyse.

Deze module bevat functies voor het visualiseren van sutabel-m analyseresultaten
met Plotly.
"""

from typing import TYPE_CHECKING
import plotly.graph_objects as go

if TYPE_CHECKING:
    from pv_tool.sutabel_analysis.sutabel_analysis import SUTABEL


def add_proefresultaten_ln_sv_ln_su_sutabel(self: "SUTABEL"):
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


def add_linear_fit_ln_sv_ln_su_sutabel(self: "SUTABEL"):
    """Voegt de lineaire fit toe aan de figuur voor sutabel analyse."""
    # Gebruik de min en max van ln(s'v) voor de lijn
    x1 = self.shansep_data_df_sutabel['ln(s\'v)'].min()
    x2 = self.shansep_data_df_sutabel['ln(s\'v)'].max()

    # Gebruik de berekende regressie parameters
    from pv_tool.sutabel_analysis.variables import e_a2_sutabel, e_a1_sutabel
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


def add_5pr_bovengrens_ln_sv_ln_su_sutabel(self: "SUTABEL"):
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


def add_5pr_ondergrens_ln_sv_ln_su_sutabel(self: "SUTABEL"):
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


def add_fysische_realiseerbare_ondergrens_ln_sv_ln_su_sutabel(self: "SUTABEL"):
    """Voegt de fysische realiseerbare ondergrens toe aan de figuur voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import a2_kar_sutabel, a1_kar_sutabel

    # Bereken de karakteristieke lijn: ln(su) = a1_kar + a2_kar * ln(s'v)
    # x1 = self.shansep_data_df_sutabel['ln(s\'v)'].min()
    x1 = 0
    x2 = self.shansep_data_df_sutabel['ln(s\'v)'].max()

    # Gebruik handmatige parameters als deze zijn ingesteld, anders berekende waarden
    if hasattr(self, 'parameters_handmatig') and self.parameters_handmatig:
        # Gebruik handmatige waarden als beschikbaar
        a2_kar = self.a2_kar_handmatig if self.a2_kar_handmatig is not None else a2_kar_sutabel(self)
        a1_kar = self.a1_kar_handmatig if self.a1_kar_handmatig is not None else a1_kar_sutabel(self)
    else:
        # Gebruik berekende waarden
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
            name='Fysisch realiseerbare ondergrens',
            line=dict(color='black', width=2),
        )
    )


def set_layout_ln_sv_ln_su_sutabel(self: "SUTABEL"):
    """Stelt de layout van de figuur in voor sutabel analyse (ln(s'v) vs ln(su))."""
    title = f'Sutabel-m analyse: ln(s\'v) vs ln(su) - {self.analysis_type} proef'

    xas_title = "ln(σ'ᵥ) [-]"
    yas_title = "ln(sᵤ) [-]"

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


# ========================== SUTABEL SV-SU PLOT ==========================

def add_proefresultaten_sv_su_sutabel(self: "SUTABEL"):
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


def add_sutabel_kar_line(self: "SUTABEL"):
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


def add_sutabel_gem_line(self: "SUTABEL"):
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


def add_su_kar_fit_constante_vc(self: "SUTABEL"):
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


def set_layout_sv_su_sutabel(self: "SUTABEL"):
    """Stelt de layout van de figuur in voor sutabel analyse (s'v vs su)."""
    title = f'Sutabel-m analyse: s\'v vs su - {self.analysis_type} proef'

    xas_title = "σ'ᵥ [kPa]"
    yas_title = "sᵤ [kPa]"

    legend_title = 'Legenda'
    self.figure.update_layout(
        width=1280,
        height=720,
        title=title if self.show_title else None,
        xaxis_title=xas_title,
        yaxis_title=yas_title,
        yaxis=dict(rangemode='tozero'),
        legend_title=legend_title,
        margin=dict(t=100, r=50, b=100, l=50)
    )
