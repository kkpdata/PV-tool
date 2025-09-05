from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
from pv_tool.shansep_analysis.variables import *

def calculate_ln_ocr(self: SHANSEP):
    self.shansep_analyses_data_df['LN(OCR)'] = (
        self.shansep_analyses_data_df['OCR'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))

def calculate_s_spop(self: SHANSEP):
    self.shansep_analyses_data_df['S'] = self.shansep_analyses_data_df['Su'] / self.shansep_analyses_data_df['S\'v']

def calculate_ln_s_spop(self: SHANSEP):
    self.shansep_analyses_data_df['LN(su/svc)'] = (
        self.shansep_analyses_data_df['S'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))

def calculate_pop(self: SHANSEP):
    self.shansep_analyses_data_df['POP'] = ((self.shansep_analyses_data_df['terreinspanning'] *
                                            self.shansep_analyses_data_df['OCR']) -
                                            self.shansep_analyses_data_df['terreinspanning'])

def calculate_s_tt(self: SHANSEP):
    df = self.shansep_analyses_data_df.copy()
    df['s_tt'] = (df['S\'v'] - sum_s(self) / count_s(self)) ** 2
    self.shansep_analyses_data_df = df

def calculate_s_ty(self: SHANSEP):
    df = self.shansep_analyses_data_df.copy()
    mean_s = sum_s(self) / count_s(self)
    df['s_ty'] = (df['S\'v'] - mean_s) * df['T']
    self.shansep_analyses_data_df = df

def calculate_kappa_2(self: SHANSEP):
    formule = (self.shansep_analyses_data_df['T'] - e_a1(self) - e_a2(self) * self.shansep_analyses_data_df['S\'v']) ** 2
    self.shansep_analyses_data_df['kappa_2'] = formule

def s_min(self: SHANSEP):
    return self.shansep_analyses_data_df['S\'v'].min()

def s_max(self: SHANSEP):
    return self.shansep_analyses_data_df['S\'v'].max()

def calculate_s_sutabel(self: SHANSEP):
    lijst = [s_min(self)]

    formule = (s_max(self) - s_min(self)) / (count_s(self) - 1)

    aantal_waarden = len(self.shansep_analyses_data_df)

    for i in range(1, aantal_waarden):
        nieuwe_waarde = lijst[i - 1] + formule
        lijst.append(nieuwe_waarde)

    self.shansep_analyses_data_df['s\''] = lijst


def calculate_5pr_ondergrens(self: SHANSEP):
    formule = (
            e_a1(self) +
            e_a2(self) * self.shansep_analyses_data_df['s\''] - t_n_2(self) *
            (sigma_a1(self) ** 2 + self.shansep_analyses_data_df['s\''] ** 2 * sigma_a2(self) ** 2 +
             2 * rho_a1_a2(self) * self.shansep_analyses_data_df['s\''] * sigma_a1(self) * sigma_a2(self) +
             (1.0 - self.alpha) * (sum_kappa_2(self) / (count_s(self) - 2))) ** 0.5
    )
    self.shansep_analyses_data_df['5_pr_ondergrens'] = formule


def calculate_5pr_bovengrens(self: SHANSEP):
    formule = (
            e_a1(self) +
            e_a2(self) * self.shansep_analyses_data_df['s\''] + t_n_2(self) *
            (sigma_a1(self) ** 2 + self.shansep_analyses_data_df['s\''] ** 2 * sigma_a2(self) ** 2 +
             2 * rho_a1_a2(self) * self.shansep_analyses_data_df['s\''] * sigma_a1(self) * sigma_a2(self) +
             (1 - self.alpha) * (sum_kappa_2(self) / (count_s(self) - 2))) ** 0.5
    )
    self.shansep_analyses_data_df['5_pr_bovengrens'] = formule


def calculate_s_tt_ondergrens(self: SHANSEP):
    formule = (self.shansep_analyses_data_df['s\''] - sum_s2(self) / count_s2(self)) ** 2
    self.shansep_analyses_data_df['s_tt_ondergrens'] = formule


def calculate_s_ty_ondergrens(self: SHANSEP):
    formule = (self.shansep_analyses_data_df['s\''] - sum_s2(self) /
               count_s2(self)) * self.shansep_analyses_data_df['5_pr_ondergrens']
    self.shansep_analyses_data_df['s_ty_ondergrens'] = formule


def calculate_kappa_2_ondergrens(self: SHANSEP):
    formule = (self.shansep_analyses_data_df['5_pr_ondergrens'] - a1_kar(self) -
               a2_kar(self) * self.shansep_analyses_data_df['s\'']) ** 2
    self.shansep_analyses_data_df['kappa_2_ondergrens'] = formule