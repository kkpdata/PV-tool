"""
Variabelen en parameters voor Sutabel-m analyse.

Deze module bevat alle functies voor het berekenen van statistische parameters
en variabelen voor sutabel-m analyses.
"""

from typing import TYPE_CHECKING
import numpy as np
from scipy.stats import t

if TYPE_CHECKING:
    from pv_tool.sutabel_analysis.sutabel_analysis import SUTABEL


def count_ln_sv_sutabel(self: "SUTABEL"):
    """Telt het aantal ln(s'v) waarden in de sutabel dataframe."""
    return self.sutabel_data_df['ln(s\'v)'].count()


def sum_ln_sv_sutabel(self: "SUTABEL"):
    """Berekent de som van ln(s'v) waarden in de sutabel dataframe."""
    return self.sutabel_data_df['ln(s\'v)'].sum()


def sum_ln_su_sutabel(self: "SUTABEL"):
    """Berekent de som van ln(su) waarden in de sutabel dataframe."""
    return self.sutabel_data_df['ln(su)'].sum()


def sum_sv_tt_sutabel(self: "SUTABEL"):
    """Berekent de som van s_tt waarden in de sutabel dataframe."""
    return self.sutabel_data_df['s_tt'].sum()


def sum_sv_ty_sutabel(self: "SUTABEL"):
    """Berekent de som van s_ty waarden in de sutabel dataframe."""
    return self.sutabel_data_df['s_ty'].sum()


def e_a2_sutabel(self: "SUTABEL"):
    """Berekent de helling (a2) van de lineaire regressie voor sutabel analyse."""
    return sum_sv_ty_sutabel(self) / sum_sv_tt_sutabel(self)


def e_a1_sutabel(self: "SUTABEL"):
    """Berekent het snijpunt (a1) van de lineaire regressie voor sutabel analyse."""
    return (sum_ln_su_sutabel(self) - sum_ln_sv_sutabel(self) * e_a2_sutabel(self)) / count_ln_sv_sutabel(self)


def sum_chi_2_sutabel(self: "SUTABEL"):
    """Berekent de som van chi-kwadraat waarden in de sutabel dataframe."""
    return self.sutabel_data_df['chi_2'].sum()


def var_a2_sutabel(self: "SUTABEL"):
    """Berekent de variantie van a2 voor sutabel analyse."""
    return (1 / sum_sv_tt_sutabel(self)) * sum_chi_2_sutabel(self) / (count_ln_sv_sutabel(self) - 2)


def var_a1_sutabel(self: "SUTABEL"):
    """Berekent de variantie van a1 voor sutabel analyse."""
    return (1 / count_ln_sv_sutabel(self) *
            (1 + sum_ln_sv_sutabel(self) ** 2 /
             (count_ln_sv_sutabel(self) * sum_sv_tt_sutabel(self))) * sum_chi_2_sutabel(self) /
            (count_ln_sv_sutabel(self) - 2))


def cov_a1_a2_sutabel(self: "SUTABEL"):
    """Berekent de covariantie tussen a1 en a2 voor sutabel analyse."""
    return (-(sum_ln_sv_sutabel(self) /
              (count_ln_sv_sutabel(self) * sum_sv_tt_sutabel(self))) * sum_chi_2_sutabel(self) /
            (count_ln_sv_sutabel(self) - 2))


def rho_a1_a2_sutabel(self: "SUTABEL"):
    """Berekent de correlatie tussen a1 en a2 voor sutabel analyse."""
    return cov_a1_a2_sutabel(self) / (var_a2_sutabel(self) * var_a1_sutabel(self)) ** 0.5


def sigma_a2_sutabel(self: "SUTABEL"):
    """Berekent de standaarddeviatie van a2 voor sutabel analyse."""
    return np.sqrt(var_a2_sutabel(self))


def sigma_a1_sutabel(self: "SUTABEL"):
    """Berekent de standaarddeviatie van a1 voor sutabel analyse."""
    return np.sqrt(var_a1_sutabel(self))


def t_n_2_sutabel(self: "SUTABEL"):
    """Berekent de t-waarde voor sutabel analyse."""
    significantieniveau = 0.1
    degrees_of_freedom = count_ln_sv_sutabel(self) - 2
    return t.ppf(1 - significantieniveau / 2, degrees_of_freedom)


def sum_s_eff_sutabel(self: "SUTABEL"):
    """Berekent de som van effectieve spanning waarden in de sutabel dataframe."""
    return self.sutabel_data_df['s\''].sum()


def count_s_eff_sutabel(self: "SUTABEL"):
    """Telt het aantal effectieve spanning waarden in de sutabel dataframe."""
    return self.sutabel_data_df['s\''].count()


def sum_5_pr_ondergrens_sutabel(self: "SUTABEL"):
    """Berekent de som van 5% ondergrens waarden in de sutabel dataframe."""
    return self.sutabel_data_df['5_pr_ondergrens'].sum()


def sum_stt_ondergrens_sutabel(self: "SUTABEL"):
    """Berekent de som van s_tt ondergrens waarden in de sutabel dataframe."""
    return self.sutabel_data_df['s_tt_ondergrens'].sum()


def sum_sty_ondergrens_sutabel(self: "SUTABEL"):
    """Berekent de som van s_ty ondergrens waarden in de sutabel dataframe."""
    return self.sutabel_data_df['s_ty_ondergrens'].sum()


def a2_kar_sutabel(self: "SUTABEL"):
    """Berekent de karakteristieke helling (a2) voor sutabel analyse."""
    return sum_sty_ondergrens_sutabel(self) / sum_stt_ondergrens_sutabel(self)


def a1_kar_sutabel(self: "SUTABEL"):
    """Berekent het karakteristieke snijpunt (a1) voor sutabel analyse."""
    return (sum_5_pr_ondergrens_sutabel(self) - a2_kar_sutabel(self) * sum_s_eff_sutabel(self)) / count_s_eff_sutabel(
        self)


def steyx_sutabel(self: "SUTABEL"):
    """Berekent de STEYX (standaardfout van de schatting) voor ln(s'v) en ln(su) data."""
    # Bereken de residuen
    n = count_ln_sv_sutabel(self)
    sum_squared_residuals = sum_chi_2_sutabel(self)

    # STEYX formule: sqrt(sum((y - y_pred)^2) / (n - 2))
    steyx = np.sqrt(sum_squared_residuals / (n - 2))

    return steyx
