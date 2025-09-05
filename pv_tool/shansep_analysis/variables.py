from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
import numpy as np
from scipy.stats import t


def count_s(self: SHANSEP):
    return self.shansep_analyses_data_df['S\'v'].count()


def sum_s(self: SHANSEP):
    return self.shansep_analyses_data_df['S\'v'].sum()


def sum_t(self: SHANSEP):
    return self.shansep_analyses_data_df['Su'].sum()


def sum_s_tt(self: SHANSEP):
    return self.shansep_analyses_data_df['s_tt'].sum()


def sum_s_ty(self: SHANSEP):
    return self.shansep_analyses_data_df['s_ty'].sum()


def e_a2(self: SHANSEP):
    return sum_s_ty(self) / sum_s_tt(self)


def e_a1(self: SHANSEP):
    return (sum_t(self) - sum_s(self) * e_a2(self)) / count_s(self)


def sum_kappa_2(self: SHANSEP):
    return self.shansep_analyses_data_df['kappa_2'].sum()


def var_a2(self: SHANSEP):
    return (1 / sum_s_tt(self)) * sum_kappa_2(self) / (count_s(self) - 2)


def var_a1(self: SHANSEP):
    return 1 / count_s(self) * (1 + sum_s(self) ** 2 / (count_s(self) * sum_s_tt(self))) * sum_kappa_2(self) / (
                count_s(self) - 2)


def cov_a1_a2(self: SHANSEP):
    return -(sum_s(self) / (count_s(self) * sum_s_tt(self))) * sum_kappa_2(self) / (count_s(self) - 2)


def rho_a1_a2(self: SHANSEP):
    return cov_a1_a2(self) / (var_a2(self) * var_a1(self)) ** 0.5


def sigma_a2(self: SHANSEP):
    return np.sqrt(var_a2(self))


def sigma_a1(self: SHANSEP):
    return np.sqrt(var_a1(self))


def t_n_2(self: SHANSEP):
    significantieniveau = 0.1
    degrees_of_freedom = count_s(self) - 2
    return t.ppf(1 - significantieniveau / 2, degrees_of_freedom)