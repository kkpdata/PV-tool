from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
from pv_tool.shansep_analysis.variables import (count_sv_oc, sum_sv_oc, e_a1_oc, e_a2_oc,
                                                t_n_2_oc, sigma_a1_oc, sigma_a2_oc, rho_a1_a2_oc,
                                                sum_chi_2_oc, count_s_eff_oc, sum_s_eff_oc,
                                                count_ln_ocr_nc_oc, sum_ln_ocr_nc_oc, e_a1_nc_oc, e_a2_nc_oc,
                                                t_n_2_nc_oc, sigma_a1_nc_oc, sigma_a2_nc_oc, rho_a1_a2_nc_oc,
                                                sum_chi_2_nc_oc, count_s_eff_nc_oc, sum_s_eff_nc_oc,
                                                a1_kar_oc, a2_kar_oc,
                                                a1_kar_nc_oc, a2_kar_nc_oc)
import numpy as np


def calculate_ln_ocr(self: SHANSEP):
    self.shansep_data_df.loc[:, 'LN(OCR)'] = (
        self.shansep_data_df['OCR'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))


def calculate_sv_spop(self: SHANSEP):
    self.shansep_data_df.loc[:, 'S'] = self.shansep_data_df['Su'] / self.shansep_data_df['S\'v']


def calculate_ln_sv_spop(self: SHANSEP):
    self.shansep_data_df.loc[:, 'LN(su/svc)'] = (
        self.shansep_data_df['S'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))


def calculate_pop(self: SHANSEP):
    self.shansep_data_df.loc[:, 'POP'] = ((self.shansep_data_df['terreinspanning'] *
                                           self.shansep_data_df['OCR']) -
                                          self.shansep_data_df['terreinspanning'])


# -------------------------- alleen OC ---------------------------------------

def calculate_sv_tt_oc(self: SHANSEP):
    df = self.shansep_data_df_oc.copy()
    df['s_tt'] = (df['S\'v'] - sum_sv_oc(self) / count_sv_oc(self)) ** 2
    self.shansep_data_df_oc = df


def calculate_sv_ty_oc(self: SHANSEP):
    df = self.shansep_data_df_oc.copy()
    mean_s = sum_sv_oc(self) / count_sv_oc(self)
    df['s_ty'] = (df['S\'v'] - mean_s) * df['Su']
    self.shansep_data_df_oc = df


def calculate_chi_2_oc(self: SHANSEP):
    formule = (self.shansep_data_df_oc['Su'] - e_a1_oc(self) - e_a2_oc(self) * self.shansep_data_df_oc['S\'v']) ** 2
    self.shansep_data_df_oc['chi_2'] = formule


def s_min_oc(self: SHANSEP):
    return self.shansep_data_df_oc['S\'v'].min()


def s_max_oc(self: SHANSEP):
    return self.shansep_data_df_oc['S\'v'].max()


def calculate_sv_eff_oc(self: SHANSEP):
    """Berekent s' waarden met gelijke intervallen tussen min en max."""
    lijst = [s_min_oc(self)]
    formule = (s_max_oc(self) - s_min_oc(self)) / (count_sv_oc(self) - 1)
    aantal_waarden = len(self.shansep_data_df_oc)
    for i in range(1, aantal_waarden):
        nieuwe_waarde = lijst[i - 1] + formule
        lijst.append(nieuwe_waarde)
    self.shansep_data_df_oc['s\''] = lijst


def calculate_5pr_ondergrens_oc(self: SHANSEP):
    formule = (
            e_a1_oc(self) +
            e_a2_oc(self) * self.shansep_data_df_oc['s\''] - t_n_2_oc(self) *
            (sigma_a1_oc(self) ** 2 + self.shansep_data_df_oc['s\''] ** 2 * sigma_a2_oc(self) ** 2 +
             2 * rho_a1_a2_oc(self) * self.shansep_data_df_oc['s\''] * sigma_a1_oc(self) * sigma_a2_oc(self) +
             (1.0 - self.alpha) * (sum_chi_2_oc(self) / (count_sv_oc(self) - 2))) ** 0.5
    )
    self.shansep_data_df_oc['5_pr_ondergrens'] = formule


def calculate_5pr_bovengrens_oc(self: SHANSEP):
    formule = (
            e_a1_oc(self) +
            e_a2_oc(self) * self.shansep_data_df_oc['s\''] + t_n_2_oc(self) *
            (sigma_a1_oc(self) ** 2 + self.shansep_data_df_oc['s\''] ** 2 * sigma_a2_oc(self) ** 2 +
             2 * rho_a1_a2_oc(self) * self.shansep_data_df_oc['s\''] * sigma_a1_oc(self) * sigma_a2_oc(self) +
             (1 - self.alpha) * (sum_chi_2_oc(self) / (count_sv_oc(self) - 2))) ** 0.5
    )
    self.shansep_data_df_oc['5_pr_bovengrens'] = formule


def calculate_sv_tt_ondergrens_oc(self: SHANSEP):
    formule = (self.shansep_data_df_oc['s\''] - sum_s_eff_oc(self) / count_s_eff_oc(self)) ** 2
    self.shansep_data_df_oc['s_tt_ondergrens'] = formule


def calculate_sv_ty_ondergrens_oc(self: SHANSEP):
    formule = (self.shansep_data_df_oc['s\''] - sum_s_eff_oc(self) /
               count_s_eff_oc(self)) * self.shansep_data_df_oc['5_pr_ondergrens']
    self.shansep_data_df_oc['s_ty_ondergrens'] = formule


def calculate_chi_2_ondergrens_oc(self: SHANSEP):
    formule = (self.shansep_data_df_oc['5_pr_ondergrens'] - a1_kar_oc(self) -
               a2_kar_oc(self) * self.shansep_data_df_oc['s\'']) ** 2
    self.shansep_data_df_oc['chi_2_ondergrens'] = formule


# -------------------------- NC en OC ---------------------------------------

def calculate_sv_tt_nc_oc(self: SHANSEP):
    df = self.shansep_data_df_nc_oc.copy()
    df['s_tt'] = (df['LN(OCR)'] - sum_ln_ocr_nc_oc(self) / count_ln_ocr_nc_oc(self)) ** 2
    self.shansep_data_df_nc_oc = df


def calculate_sv_ty_nc_oc(self: SHANSEP):
    df = self.shansep_data_df_nc_oc.copy()
    mean_s = sum_ln_ocr_nc_oc(self) / count_ln_ocr_nc_oc(self)
    df['s_ty'] = (df['LN(OCR)'] - mean_s) * df['LN(su/svc)']
    self.shansep_data_df_nc_oc = df


def calculate_chi_2_nc_oc(self: SHANSEP):
    formule = (self.shansep_data_df_nc_oc['LN(su/svc)'] - e_a1_nc_oc(self) - e_a2_nc_oc(self) *
               self.shansep_data_df_nc_oc['LN(OCR)']) ** 2
    self.shansep_data_df_nc_oc['chi_2'] = formule


def s_min_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['LN(OCR)'].min()


def s_max_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['LN(OCR)'].max()


def calculate_sv_eff_nc_oc(self: SHANSEP):
    """Berekent s' waarden met gelijke intervallen tussen min en max."""
    lijst = [s_min_nc_oc(self)]
    formule = (s_max_nc_oc(self) - s_min_nc_oc(self)) / (count_ln_ocr_nc_oc(self) - 1)
    aantal_waarden = len(self.shansep_data_df_nc_oc)
    for i in range(1, aantal_waarden):
        nieuwe_waarde = lijst[i - 1] + formule
        lijst.append(nieuwe_waarde)
    self.shansep_data_df_nc_oc['s\''] = lijst


def calculate_5pr_ondergrens_nc_oc(self: SHANSEP):
    formule = (
            e_a1_nc_oc(self) +
            e_a2_nc_oc(self) * self.shansep_data_df_nc_oc['s\''] - t_n_2_nc_oc(self) *
            (sigma_a1_nc_oc(self) ** 2 + self.shansep_data_df_nc_oc['s\''] ** 2 * sigma_a2_nc_oc(self) ** 2 +
             2 * rho_a1_a2_nc_oc(self) * self.shansep_data_df_nc_oc['s\''] * sigma_a1_nc_oc(self) * sigma_a2_nc_oc(
                        self) +
             (1.0 - self.alpha) * (sum_chi_2_nc_oc(self) / (count_ln_ocr_nc_oc(self) - 2))) ** 0.5
    )

    self.shansep_data_df_nc_oc['5_pr_ondergrens'] = formule


def calculate_5pr_bovengrens_nc_oc(self: SHANSEP):
    formule = (
            e_a1_nc_oc(self) +
            e_a2_nc_oc(self) * self.shansep_data_df_nc_oc['s\''] + t_n_2_nc_oc(self) *
            (sigma_a1_nc_oc(self) ** 2 + self.shansep_data_df_nc_oc['s\''] ** 2 * sigma_a2_nc_oc(self) ** 2 +
             2 * rho_a1_a2_nc_oc(self) * self.shansep_data_df_nc_oc['s\''] * sigma_a1_nc_oc(self) * sigma_a2_nc_oc(
                        self) +
             (1 - self.alpha) * (sum_chi_2_nc_oc(self) / (count_ln_ocr_nc_oc(self) - 2))) ** 0.5
    )
    self.shansep_data_df_nc_oc['5_pr_bovengrens'] = formule


def calculate_sv_tt_ondergrens_nc_oc(self: SHANSEP):
    formule = (self.shansep_data_df_nc_oc['s\''] - sum_s_eff_nc_oc(self) / count_s_eff_nc_oc(self)) ** 2
    self.shansep_data_df_nc_oc['s_tt_ondergrens'] = formule


def calculate_sv_ty_ondergrens_nc_oc(self: SHANSEP):
    formule = (self.shansep_data_df_nc_oc['s\''] - sum_s_eff_nc_oc(self) /
               count_s_eff_nc_oc(self)) * self.shansep_data_df_nc_oc['5_pr_ondergrens']
    self.shansep_data_df_nc_oc['s_ty_ondergrens'] = formule


def calculate_chi_2_ondergrens_nc_oc(self: SHANSEP):
    formule = (self.shansep_data_df_nc_oc['5_pr_ondergrens'] - a1_kar_nc_oc(self) -
               a2_kar_nc_oc(self) * self.shansep_data_df_nc_oc['s\'']) ** 2
    self.shansep_data_df_nc_oc['chi_2_ondergrens'] = formule
