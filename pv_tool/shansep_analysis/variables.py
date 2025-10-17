from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
import numpy as np
from scipy.stats import t

# -------------------------- alleen OC ---------------------------------------
def count_sv_oc(self: SHANSEP):
    return self.shansep_data_df_oc['S\'v'].count()


def sum_sv_oc(self: SHANSEP):
    return self.shansep_data_df_oc['S\'v'].sum()


def sum_su_oc(self: SHANSEP):
    return self.shansep_data_df_oc['Su'].sum()


def sum_sv_tt_oc(self: SHANSEP):
    return self.shansep_data_df_oc['s_tt'].sum()


def sum_sv_ty_oc(self: SHANSEP):
    return self.shansep_data_df_oc['s_ty'].sum()


def e_a2_oc(self: SHANSEP):
    return sum_sv_ty_oc(self) / sum_sv_tt_oc(self)


def e_a1_oc(self: SHANSEP):
    return (sum_su_oc(self) - sum_sv_oc(self) * e_a2_oc(self)) / count_sv_oc(self)


def sum_kappa_2_oc(self: SHANSEP):
    return self.shansep_data_df_oc['kappa_2'].sum()


def var_a2_oc(self: SHANSEP):
    return (1 / sum_sv_tt_oc(self)) * sum_kappa_2_oc(self) / (count_sv_oc(self) - 2)


def var_a1_oc(self: SHANSEP):
    return 1 / count_sv_oc(self) * (1 + sum_sv_oc(self) ** 2 / (count_sv_oc(self) * sum_sv_tt_oc(self))) * sum_kappa_2_oc(self) / (
                count_sv_oc(self) - 2)


def cov_a1_a2_oc(self: SHANSEP):
    return -(sum_sv_oc(self) / (count_sv_oc(self) * sum_sv_tt_oc(self))) * sum_kappa_2_oc(self) / (count_sv_oc(self) - 2)


def rho_a1_a2_oc(self: SHANSEP):
    return cov_a1_a2_oc(self) / (var_a2_oc(self) * var_a1_oc(self)) ** 0.5


def sigma_a2_oc(self: SHANSEP):
    return np.sqrt(var_a2_oc(self))


def sigma_a1_oc(self: SHANSEP):
    return np.sqrt(var_a1_oc(self))


def t_n_2_oc(self: SHANSEP):
    significantieniveau = 0.1
    degrees_of_freedom = count_sv_oc(self) - 2
    return t.ppf(1 - significantieniveau / 2, degrees_of_freedom)

def sum_s_eff_oc(self: SHANSEP):
    return self.shansep_data_df_oc['s\''].sum()

def count_s_eff_oc(self: SHANSEP):
    return self.shansep_data_df_oc['s\''].count()

def sum_5_pr_ondergrens_oc(self: SHANSEP):
    return self.shansep_data_df_oc['5_pr_ondergrens'].sum()

def sum_stt_ondergrens_oc(self: SHANSEP):
    return self.shansep_data_df_oc['s_tt_ondergrens'].sum()

def sum_sty_ondergrens_oc(self: SHANSEP):
    return self.shansep_data_df_oc['s_ty_ondergrens'].sum()

def a2_kar_oc(self: SHANSEP):
    return sum_sty_ondergrens_oc(self) / sum_stt_ondergrens_oc(self)

def a1_kar_oc(self: SHANSEP):
    return (sum_5_pr_ondergrens_oc(self) - a2_kar_oc(self) * sum_s_eff_oc(self)) / count_s_eff_oc(self)

# -------------------------- NC en OC ---------------------------------------
def count_sv_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['LN(OCR)'].count()


def sum_sv_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['LN(OCR)'].sum()


def sum_su_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['Su'].sum()


def sum_sv_tt_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['s_tt'].sum()


def sum_sv_ty_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['s_ty'].sum()


def e_a2_nc_oc(self: SHANSEP):
    return sum_sv_ty_nc_oc(self) / sum_sv_tt_nc_oc(self)


def e_a1_nc_oc(self: SHANSEP):
    return (sum_su_nc_oc(self) - sum_sv_nc_oc(self) * e_a2_nc_oc(self)) / count_sv_nc_oc(self)


def sum_kappa_2_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['kappa_2'].sum()


def var_a2_nc_oc(self: SHANSEP):
    return (1 / sum_sv_tt_nc_oc(self)) * sum_kappa_2_nc_oc(self) / (count_sv_nc_oc(self) - 2)


def var_a1_nc_oc(self: SHANSEP):
    return 1 / count_sv_nc_oc(self) * (1 + sum_sv_nc_oc(self) ** 2 / (count_sv_nc_oc(self) * sum_sv_tt_nc_oc(self))) * sum_kappa_2_nc_oc(self) / (
                count_sv_nc_oc(self) - 2)


def cov_a1_a2_nc_oc(self: SHANSEP):
    return -(sum_sv_nc_oc(self) / (count_sv_nc_oc(self) * sum_sv_tt_nc_oc(self))) * sum_kappa_2_nc_oc(self) / (count_sv_nc_oc(self) - 2)


def rho_a1_a2_nc_oc(self: SHANSEP):
    return cov_a1_a2_nc_oc(self) / (var_a2_nc_oc(self) * var_a1_nc_oc(self)) ** 0.5


def sigma_a2_nc_oc(self: SHANSEP):
    return np.sqrt(var_a2_nc_oc(self))


def sigma_a1_nc_oc(self: SHANSEP):
    return np.sqrt(var_a1_nc_oc(self))


def t_n_2_nc_oc(self: SHANSEP):
    significantieniveau = 0.1
    degrees_of_freedom = count_sv_nc_oc(self) - 2
    return t.ppf(1 - significantieniveau / 2, degrees_of_freedom)

def sum_s_eff_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['s\''].sum()

def count_s_eff_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['s\''].count()

def sum_5_pr_ondergrens_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['5_pr_ondergrens'].sum()

def sum_stt_ondergrens_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['s_tt_ondergrens'].sum()

def sum_sty_ondergrens_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['s_ty_ondergrens'].sum()

def a2_kar_nc_oc(self: SHANSEP):
    return sum_sty_ondergrens_nc_oc(self) / sum_stt_ondergrens_nc_oc(self)

def a1_kar_nc_oc(self: SHANSEP):
    return (sum_5_pr_ondergrens_nc_oc(self) - a2_kar_nc_oc(self) * sum_s_eff_nc_oc(self)) / count_s_eff_nc_oc(self)

