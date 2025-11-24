"""
Expand Analysis functies voor Sutabel-m analyse.

Deze module bevat functies voor het uitbreiden van de analyse dataframe
met berekende kolommen voor sutabel-m analyses.
"""

from typing import TYPE_CHECKING
import numpy as np
import pandas as pd
from pandas import DataFrame

if TYPE_CHECKING:
    from pv_tool.sutabel_analysis.sutabel_analysis import SUTABEL


def calculate_ln_sv_sutabel(self: "SUTABEL"):
    """Berekent ln(s'v) voor de sutabel dataframe."""
    self.shansep_data_df_sutabel.loc[:, 'ln(s\'v)'] = (
        self.shansep_data_df_sutabel['S\'v'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))


def calculate_ln_su_sutabel(self: "SUTABEL"):
    """Berekent ln(su) voor de sutabel dataframe."""
    self.shansep_data_df_sutabel.loc[:, 'ln(su)'] = (
        self.shansep_data_df_sutabel['Su'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))


def calculate_sv_tt_sutabel(self: "SUTABEL"):
    """Berekent s_tt voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import count_ln_sv_sutabel, sum_ln_sv_sutabel
    if self.shansep_data_df_sutabel is None or self.shansep_data_df_sutabel.empty:
        raise ValueError("shansep_data_df_sutabel is None of leeg. Run de analyse en controleer je data.")
    count = count_ln_sv_sutabel(self)
    if count == 0:
        raise ValueError("Aantal ln(s'v) waarden is 0. Kan niet delen door nul.")
    df: DataFrame = self.shansep_data_df_sutabel.copy()
    # Zorg dat kolom numeriek is
    df['ln(s\'v)'] = pd.to_numeric(df['ln(s\'v)'], errors='coerce')
    mean_sv = sum_ln_sv_sutabel(self) / count
    df['s_tt'] = (df['ln(s\'v)'] - mean_sv) ** 2
    self.shansep_data_df_sutabel = df


def calculate_sv_ty_sutabel(self: "SUTABEL"):
    """Berekent s_ty voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import count_ln_sv_sutabel, sum_ln_sv_sutabel
    if self.shansep_data_df_sutabel is None or self.shansep_data_df_sutabel.empty:
        raise ValueError("shansep_data_df_sutabel is None of leeg. Run de analyse en controleer je data.")
    count = count_ln_sv_sutabel(self)
    if count == 0:
        raise ValueError("Aantal ln(s'v) waarden is 0. Kan niet delen door nul.")
    df: DataFrame = self.shansep_data_df_sutabel.copy()
    # Zorg dat kolommen numeriek zijn
    df['ln(s\'v)'] = pd.to_numeric(df['ln(s\'v)'], errors='coerce')
    df['ln(su)'] = pd.to_numeric(df['ln(su)'], errors='coerce')
    mean_s = sum_ln_sv_sutabel(self) / count
    df['s_ty'] = (df['ln(s\'v)'] - mean_s) * df['ln(su)']
    self.shansep_data_df_sutabel = df


def calculate_chi_2_sutabel(self: "SUTABEL"):
    """Berekent chi_2 voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import e_a1_sutabel, e_a2_sutabel
    formule = (self.shansep_data_df_sutabel['ln(su)'] - e_a1_sutabel(self) -
               e_a2_sutabel(self) * self.shansep_data_df_sutabel['ln(s\'v)']) ** 2
    self.shansep_data_df_sutabel['chi_2'] = formule


def s_min_sutabel(self: "SUTABEL"):
    """Berekent minimum ln(s'v) waarde voor sutabel analyse."""
    return self.shansep_data_df_sutabel['ln(s\'v)'].min()


def s_max_sutabel(self: "SUTABEL"):
    """Berekent maximum ln(s'v) waarde voor sutabel analyse."""
    return self.shansep_data_df_sutabel['ln(s\'v)'].max()


def calculate_sv_eff_sutabel(self: "SUTABEL"):
    """Berekent s' waarden met gelijke intervallen tussen min en max voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import count_ln_sv_sutabel
    lijst = [s_min_sutabel(self)]
    formule = (s_max_sutabel(self) - s_min_sutabel(self)) / (count_ln_sv_sutabel(self) - 1)
    aantal_waarden = len(self.shansep_data_df_sutabel)
    for i in range(1, aantal_waarden):
        nieuwe_waarde = lijst[i - 1] + formule
        lijst.append(nieuwe_waarde)
    self.shansep_data_df_sutabel['s\''] = lijst


def calculate_5pr_ondergrens_sutabel(self: "SUTABEL"):
    """Berekent 5% ondergrens voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import (e_a1_sutabel, e_a2_sutabel, t_n_2_sutabel,
                                                      sigma_a1_sutabel, sigma_a2_sutabel,
                                                      rho_a1_a2_sutabel, sum_chi_2_sutabel,
                                                      count_ln_sv_sutabel)
    formule = (
            e_a1_sutabel(self) +
            e_a2_sutabel(self) * self.shansep_data_df_sutabel['s\''] - t_n_2_sutabel(self) *
            (sigma_a1_sutabel(self) ** 2 + self.shansep_data_df_sutabel['s\''] ** 2 * sigma_a2_sutabel(self) ** 2 +
             2 * rho_a1_a2_sutabel(self) * self.shansep_data_df_sutabel['s\''] * sigma_a1_sutabel(self) * sigma_a2_sutabel(self) +
             (1.0 - self.alpha) * (sum_chi_2_sutabel(self) / (count_ln_sv_sutabel(self) - 2))) ** 0.5
    )
    self.shansep_data_df_sutabel['5_pr_ondergrens'] = formule


def calculate_5pr_bovengrens_sutabel(self: "SUTABEL"):
    """Berekent 5% bovengrens voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import (e_a1_sutabel, e_a2_sutabel, t_n_2_sutabel,
                                                      sigma_a1_sutabel, sigma_a2_sutabel,
                                                      rho_a1_a2_sutabel, sum_chi_2_sutabel,
                                                      count_ln_sv_sutabel)
    formule = (
            e_a1_sutabel(self) +
            e_a2_sutabel(self) * self.shansep_data_df_sutabel['s\''] + t_n_2_sutabel(self) *
            (sigma_a1_sutabel(self) ** 2 + self.shansep_data_df_sutabel['s\''] ** 2 * sigma_a2_sutabel(self) ** 2 +
             2 * rho_a1_a2_sutabel(self) * self.shansep_data_df_sutabel['s\''] * sigma_a1_sutabel(self) * sigma_a2_sutabel(self) +
             (1 - self.alpha) * (sum_chi_2_sutabel(self) / (count_ln_sv_sutabel(self) - 2))) ** 0.5
    )
    self.shansep_data_df_sutabel['5_pr_bovengrens'] = formule


def calculate_sv_tt_ondergrens_sutabel(self: "SUTABEL"):
    """Berekent s_tt ondergrens voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import sum_s_eff_sutabel, count_s_eff_sutabel
    formule = (self.shansep_data_df_sutabel['s\''] - sum_s_eff_sutabel(self) / count_s_eff_sutabel(self)) ** 2
    self.shansep_data_df_sutabel['s_tt_ondergrens'] = formule


def calculate_sv_ty_ondergrens_sutabel(self: "SUTABEL"):
    """Berekent s_ty ondergrens voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import sum_s_eff_sutabel, count_s_eff_sutabel
    formule = (self.shansep_data_df_sutabel['s\''] - sum_s_eff_sutabel(self) /
               count_s_eff_sutabel(self)) * self.shansep_data_df_sutabel['5_pr_ondergrens']
    self.shansep_data_df_sutabel['s_ty_ondergrens'] = formule


def calculate_chi_2_ondergrens_sutabel(self: "SUTABEL"):
    """Berekent chi_2 ondergrens voor sutabel analyse."""
    from pv_tool.sutabel_analysis.variables import a1_kar_sutabel, a2_kar_sutabel
    formule = (self.shansep_data_df_sutabel['5_pr_ondergrens'] - a1_kar_sutabel(self) -
               a2_kar_sutabel(self) * self.shansep_data_df_sutabel['s\'']) ** 2
    self.shansep_data_df_sutabel['chi_2_ondergrens'] = formule
