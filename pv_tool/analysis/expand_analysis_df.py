from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.analysis.c_phi_analysis import CPhiAnalyse
from pv_tool.analysis.variables import *


def calculate_s_tt(self: CPhiAnalyse):
    formule = (self.cphi_analyses_data_df['S\''] - sum_s(self) / count_s(self)) ** 2
    self.cphi_analyses_data_df['s_tt'] = formule


def calculate_s_ty(self: CPhiAnalyse):
    formule = (self.cphi_analyses_data_df['S\''] - sum_s(self) / count_s(self)) * self.cphi_analyses_data_df['T']
    self.cphi_analyses_data_df['s_ty'] = formule


def calculate_kappa_2(self: CPhiAnalyse):
    formule = (self.cphi_analyses_data_df['T'] - e_a1(self) - e_a2(self) * self.cphi_analyses_data_df['S\'']) ** 2
    self.cphi_analyses_data_df['kappa_2'] = formule


def s_min(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['S\''].min()


def s_max(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['S\''].max()


def calculate_s(self: CPhiAnalyse):
    lijst = [s_min(self)]

    formule = (s_max(self) - s_min(self)) / count_s(self) - 1

    aantal_waarden = len(self.cphi_analyses_data_df)

    for i in range(1, aantal_waarden):
        nieuwe_waarde = lijst[i - 1] + formule
        lijst.append(nieuwe_waarde)

    self.cphi_analyses_data_df['s\''] = lijst


def calculate_5pr_ondergrens(self: CPhiAnalyse):
    alpha_value = self.alpha.value

    formule = (
            e_a1(self) +
            e_a2(self) * self.cphi_analyses_data_df['s\''] - t_n_2(self) *
            (sigma_a1(self) ** 2 + self.cphi_analyses_data_df['s\''] ** 2 * sigma_a2(self) ** 2 +
             2 * rho_a1_a2(self) * self.cphi_analyses_data_df['s\''] * sigma_a1(self) * sigma_a2(self) +
             (1.0 - alpha_value) * (sum_kappa_2(self) / (count_s(self) - 2))) ** 0.5
    )
    self.cphi_analyses_data_df['5_pr_ondergrens'] = formule


def calculate_5pr_bovengrens(self: CPhiAnalyse):
    alpha_value = self.alpha.value

    formule = (
            e_a1(self) +
            e_a2(self) * self.cphi_analyses_data_df['s\''] + t_n_2(self) *
            (sigma_a1(self) ** 2 + self.cphi_analyses_data_df['s\''] ** 2 * sigma_a2(self) ** 2 +
             2 * rho_a1_a2(self) * self.cphi_analyses_data_df['s\''] * sigma_a1(self) * sigma_a2(self) +
             (1 - alpha_value) * (sum_kappa_2(self) / (count_s(self) - 2))) ** 0.5
    )
    self.cphi_analyses_data_df['5_pr_bovengrens'] = formule


def calculate_s_tt_ondergrens(self: CPhiAnalyse):
    formule = (self.cphi_analyses_data_df['s\''] - sum_s(self) / count_s2(self)) ** 2
    self.cphi_analyses_data_df['s_tt_ondergrens'] = formule


def calculate_s_ty_ondergrens(self: CPhiAnalyse):
    formule = (self.cphi_analyses_data_df['s\''] - sum_s2(self) /
               count_s2(self)) * self.cphi_analyses_data_df['5_pr_ondergrens']
    self.cphi_analyses_data_df['s_ty_ondergrens'] = formule


def calculate_kappa_2_ondergrens(self: CPhiAnalyse):
    formule = (self.cphi_analyses_data_df['5_pr_ondergrens'] - a1_kar(self) -
               a2_kar(self) * self.cphi_analyses_data_df['s\'']) ** 2
    self.cphi_analyses_data_df['kappa_2_ondergrens'] = formule


# kolommen Leo
def calculate_correctie_t(self: CPhiAnalyse):
    coh_gem = self.cohesie_gem_handmatig
    self.cphi_analyses_data_df['correctie_t'] = (- coh_gem + self.cphi_analyses_data_df['T'])


def calculate_5pr_ondergrens_correctie_c(self: CPhiAnalyse):
    formule = (e_a1(self) + e_a2(self) * self.cphi_analyses_data_df['s\''] - t_n_2(self) *
               (sigma_a1_gecorrigeerd(self) ** 2 + self.cphi_analyses_data_df['s\''] ** 2 * sigma_a2_gecorrigeerd(
                   self) ** 2 + 2 * rho_a1_a2(self) * self.cphi_analyses_data_df['s\''] * sigma_a1_gecorrigeerd(
                   self) * sigma_a2_gecorrigeerd(self) + (1 - self.alpha.value) *
                (sum_kappa_2_2pr_gecorrigeerd(self) / (count_s(self) - 2))) ** 0.5)
    self.cphi_analyses_data_df['5pr_ondergrens_cor'] = formule


def calculate_5pr_bovengrens_correctie_c(self: CPhiAnalyse):
    formule = (e_a1(self) + e_a2(self) * self.cphi_analyses_data_df['s\''] + t_n_2(self) *
               (sigma_a1_gecorrigeerd(self)**2 + self.cphi_analyses_data_df['s\'']**2 * sigma_a2_gecorrigeerd(self)**2 +
                2 * rho_a1_a2(self) * self.cphi_analyses_data_df['s\''] * sigma_a1_gecorrigeerd(self) *
                sigma_a2_gecorrigeerd(self) + (1 - self.alpha.value) *
                (sum_kappa_2_2pr_gecorrigeerd(self) / (count_s(self) - 2)))**0.5)
    self.cphi_analyses_data_df['5pr_bovengrens_cor'] = formule


def kappa_2_2pr_cor(self: CPhiAnalyse):
    formule = (self.cphi_analyses_data_df['T'] - self.cohesie_gem_handmatig -
               helling_gecor(self) * self.cphi_analyses_data_df['S\''])**2
    self.cphi_analyses_data_df['kappa_2_2pr_cor'] = formule


def calculate_s_ty_ondergrens_correctie_c(self: CPhiAnalyse):
    formule = ((self.cphi_analyses_data_df['s\''] - sum_s2(self) / count_s2(self)) *
               self.cphi_analyses_data_df['5pr_ondergrens_cor'])
    self.cphi_analyses_data_df['s_ty_ondergrens_cor'] = formule


def calculate_kappa_2_ondergrens_correctie_c(self: CPhiAnalyse):
    formule = (self.cphi_analyses_data_df['5pr_ondergrens_cor'] - a1_kar(self) -
               a2_kar(self) * self.cphi_analyses_data_df['s\''])**2
    self.cphi_analyses_data_df['kappa_2_ondergrens_cor'] = formule
