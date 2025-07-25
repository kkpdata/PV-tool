from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.analysis.c_phi_analysis import CPhiAnalyse
from pv_tool.analysis.variables import *
from scipy.stats import linregress, norm


def calc_phi_gem(self: CPhiAnalyse):
    """Geeft een eerste benadering voor de gemiddelde phi."""
    x_values = self.cphi_analyses_data_df['S\'']
    y_values = self.cphi_analyses_data_df['T']
    phi_gem = linregress(x=x_values, y=y_values).slope
    return phi_gem


def calc_cohesie_gem(self: CPhiAnalyse):
    """Geeft een eerste benadering voor de gemiddelde cohesie."""
    return (sum_t(self) - sum_s(self) * e_a2(self)) / count_s(self)


def calc_phi_kar(self: CPhiAnalyse):
    """Geeft een eerste benadering voor de karakteristieke phi."""
    # =ALS(ISGETAL(D80); U61; L62)
    if self.cohesie_gem_handmatig is not None:
        phi_kar = a2_kar_gecorrigeerd(self)
    else:
        phi_kar = a2_kar(self)
    return phi_kar


def calc_cohesie_kar(self: CPhiAnalyse):
    """Geeft een eerste benadering voor de karakteristieke cohesie."""
    if self.cohesie_gem_handmatig is not None:
        cohesie_kar = a1_kar_gecorrigeerd(self)
    else:
        # =(M58 - L57 * L62) / L56
        cohesie_kar = a1_kar(self)
    return cohesie_kar


def calc_tan_phi_gem(self: CPhiAnalyse):
    return math.atan(var_tan_phi_gem(self))*180 / np.pi


def calc_c_gem(self: CPhiAnalyse):
    return self.cohesie_gem_handmatig / np.sqrt(1 - helling_gecor(self)**2)


def calc_tan_phi_kar(self: CPhiAnalyse):
    return math.atan(var_tan_phi_kar(self))*180 / np.pi


def calc_c_kar(self: CPhiAnalyse):
    return self.cohesie_kar_handmatig / np.sqrt(1 - self.phi_kar_handmatig**2)


def calc_tan_phi_d(self: CPhiAnalyse):
    return math.atan(var_tan_phi_kar(self)/self.material_tan_phi)*180 / np.pi


def calc_c_d(self: CPhiAnalyse):
    return calc_c_kar(self) / self.material_cohesie

def calc_st_dev(self: CPhiAnalyse):
    return calc_tan_phi_gem(self) * math.sqrt(math.exp((((norm.ppf(0.05)*2) + math.sqrt((norm.ppf(0.05)*2)**2 + 8 * (math.log(calc_tan_phi_gem(self)) - math.log(calc_tan_phi_d(self))))) / 2)**2)-1)