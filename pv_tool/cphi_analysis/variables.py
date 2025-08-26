from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
import numpy as np
from scipy.stats import t


def count_s(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['S\''].count()


def sum_s(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['S\''].sum()


def sum_t(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['T'].sum()


def sum_s_tt(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['s_tt'].sum()


def sum_s_ty(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['s_ty'].sum()


def e_a2(self: CPhiAnalyse):
    return sum_s_ty(self) / sum_s_tt(self)


def e_a1(self: CPhiAnalyse):
    return (sum_t(self) - sum_s(self) * e_a2(self)) / count_s(self)


def sum_kappa_2(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['kappa_2'].sum()


def var_a2(self: CPhiAnalyse):
    return (1 / sum_s_tt(self)) * sum_kappa_2(self) / (count_s(self) - 2)


def var_a1(self: CPhiAnalyse):
    return 1 / count_s(self) * (1 + sum_s(self) ** 2 / (count_s(self) * sum_s_tt(self))) * sum_kappa_2(self) / (
                count_s(self) - 2)


def cov_a1_a2(self: CPhiAnalyse):
    return -(sum_s(self) / (count_s(self) * sum_s_tt(self))) * sum_kappa_2(self) / (count_s(self) - 2)


def rho_a1_a2(self: CPhiAnalyse):
    return cov_a1_a2(self) / (var_a2(self) * var_a1(self)) ** 0.5


def sigma_a2(self: CPhiAnalyse):
    return np.sqrt(var_a2(self))


def sigma_a1(self: CPhiAnalyse):
    return np.sqrt(var_a1(self))


def t_n_2(self: CPhiAnalyse):
    significantieniveau = 0.1
    degrees_of_freedom = count_s(self) - 2
    return t.ppf(1 - significantieniveau / 2, degrees_of_freedom)

def t_n_2_sh(self: CPhiAnalyse):
    significantieniveau = 0.05
    degrees_of_freedom = count_s(self) - 1
    return t.ppf(significantieniveau, degrees_of_freedom)

def gem_ln_tan_a_sh(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['ln(tan(a))'].mean()

def std_ln_tan_a_sh(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['ln(tan(a))'].std()

def var_a2_gem_sh(self: CPhiAnalyse):
    return math.exp(gem_ln_tan_a_sh(self))

def var_a2_onder_sh(self: CPhiAnalyse):
    a2_phi_kar_onder = math.exp(gem_ln_tan_a_sh(self) + t_n_2_sh(self) * std_ln_tan_a_sh(self) *
                                math.sqrt((1 - self.alpha) + 1 / count_s(self)))
    return a2_phi_kar_onder

def var_a2_boven_sh(self: CPhiAnalyse):
    a2_phi_kar_boven = math.exp(gem_ln_tan_a_sh(self) - t_n_2_sh(self) * std_ln_tan_a_sh(self) *
                                math.sqrt((1 - self.alpha) + 1 / count_s(self)))
    return a2_phi_kar_boven


def sum_s2(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['s\''].sum()


def count_s2(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['s\''].count()


def sum_5pr_ondergrens(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['5_pr_ondergrens'].sum()


def sum_s_tt_ondergrens(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['s_tt_ondergrens'].sum()


def sum_s_ty_ondergrens(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['s_ty_ondergrens'].sum()


def a2_kar(self: CPhiAnalyse):
    return sum_s_ty_ondergrens(self) / sum_s_tt_ondergrens(self)


def a1_kar(self: CPhiAnalyse):
    formule = (sum_5pr_ondergrens(self) - sum_s2(self) * a2_kar(self)) / count_s2(self)
    return formule


def sum_5_pr_ondergrens_gecorrigeerd(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['5pr_ondergrens_cor'].sum()


def sum_s_ty_ondergrens_gecorrigeerd(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['s_ty_ondergrens_cor'].sum()  # Deze terug aangepast want eerst stond er niet _cor


def a2_kar_gecorrigeerd(self: CPhiAnalyse):
    return sum_s_ty_ondergrens_gecorrigeerd(self) / sum_s_tt_ondergrens(self)


def a1_kar_gecorrigeerd(self: CPhiAnalyse):
    return (sum_5_pr_ondergrens_gecorrigeerd(self) - sum_s2(self) * a2_kar_gecorrigeerd(self)) / count_s(self)


def sum_kappa_2_2pr_gecorrigeerd(self: CPhiAnalyse):
    return self.cphi_analyses_data_df['kappa_2_2pr_cor'].sum()


def var_a2_gecorrigeerd(self: CPhiAnalyse):
    return (1 / sum_s_tt(self)) * sum_kappa_2_2pr_gecorrigeerd(self) / (count_s(self) - 2)


def var_a1_gecorrigeerd(self: CPhiAnalyse):
    formule = (1 / count_s(self) * (1 + sum_s(self) ** 2 / (count_s(self) * sum_s_tt(self))) *
               sum_kappa_2_2pr_gecorrigeerd(self) / (count_s(self) - 2))
    return formule


def sigma_a2_gecorrigeerd(self: CPhiAnalyse):
    return np.sqrt(var_a2_gecorrigeerd(self))


def sigma_a1_gecorrigeerd(self: CPhiAnalyse):
    return np.sqrt(var_a1_gecorrigeerd(self))


def helling_gecor(self: CPhiAnalyse):
    if self.cohesie_gem_handmatig is not None:
        x_values = self.cphi_analyses_data_df['S\'']
        y_values = self.cphi_analyses_data_df['correctie_t']
        x = np.array(x_values)[:, np.newaxis]
        helling, _, _, _ = np.linalg.lstsq(x, np.array(y_values))
    else:
        helling = sum_s_ty(self) / sum_s_tt(self)
    return helling


def var_tan_phi_gem(self: CPhiAnalyse):
    if self.analysis_type == 'TXT_CPhi':
        return helling_gecor(self) / np.sqrt(1 - helling_gecor(self)**2)
    elif self.analysis_type == 'DSS_CPhi':
        return helling_gecor(self)
    elif self.analysis_type == 'TXT_SH':
        return var_a2_gem_sh(self) / np.sqrt(1 - var_a2_gem_sh(self) ** 2)
    elif self.analysis_type == 'DSS_SH':
        return var_a2_gem_sh(self)


def var_tan_phi_kar(self: CPhiAnalyse):
    if self.phi_kar_handmatig is not None:
        phi_kar = self.phi_kar_handmatig
    else:
        phi_kar = self.eerste_benadering_a2_kar
    if self.analysis_type == 'TXT_CPhi':
        return phi_kar / np.sqrt(1 - phi_kar**2)
    elif self.analysis_type == 'DSS_CPhi':
        return phi_kar

def var_tan_phi_kar_sh(self: CPhiAnalyse):
    if self.analysis_type == 'TXT_SH':
        return var_a2_onder_sh(self) / np.sqrt(1 - var_a2_onder_sh(self) ** 2)
    elif self.analysis_type == 'DSS_SH':
        return var_a2_onder_sh(self)
