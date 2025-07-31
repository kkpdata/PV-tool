from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.analysis.c_phi_analysis import CPhiAnalyse
from pv_tool.analysis.variables import *
from scipy.stats import linregress, norm


def calc_tan_phi_gem(self: CPhiAnalyse):
    """Geeft een eerste benadering voor de gemiddelde phi."""
    x_values = self.cphi_analyses_data_df['S\'']
    y_values = self.cphi_analyses_data_df['T']
    phi_gem = linregress(x=x_values, y=y_values).slope
    return phi_gem


def calc_cohesie_gem(self: CPhiAnalyse):
    """Geeft een eerste benadering voor de gemiddelde cohesie."""
    return (sum_t(self) - sum_s(self) * e_a2(self)) / count_s(self)


def calc_tan_phi_kar(self: CPhiAnalyse):
    """Geeft een eerste benadering voor de karakteristieke phi."""
    # =ALS(ISGETAL(D80); U61; L62)
    if self.cohesie_gem_handmatig is not None:
        tan_phi_kar = a2_kar_gecorrigeerd(self)
    else:
        tan_phi_kar = a2_kar(self)
    return tan_phi_kar

def calc_tan_phi_d(self: CPhiAnalyse):
    tan_phi_d = calc_tan_phi_kar(self)/self.material_tan_phi
    return tan_phi_d


def calc_cohesie_kar(self: CPhiAnalyse):
    """Geeft een eerste benadering voor de karakteristieke cohesie."""
    if self.cohesie_gem_handmatig is not None:
        cohesie_kar = a1_kar_gecorrigeerd(self)
    else:
        # =(M58 - L57 * L62) / L56
        cohesie_kar = a1_kar(self)
    return cohesie_kar


def calc_phi_gem(self: CPhiAnalyse):
    return math.atan(var_tan_phi_gem(self)) * 180 / np.pi


def calc_c_gem(self: CPhiAnalyse):
    return self.cohesie_gem_handmatig / np.sqrt(1 - helling_gecor(self) ** 2)


def calc_phi_kar(self: CPhiAnalyse):
    return math.atan(var_tan_phi_kar(self)) * 180 / np.pi


def calc_c_kar(self: CPhiAnalyse):
    return self.cohesie_kar_handmatig / np.sqrt(1 - self.phi_kar_handmatig ** 2)


def calc_phi_d(self: CPhiAnalyse):  # TODO: dit berekent de phi d en niet tan phi d - eventueel nog aanpassen
    return math.atan(var_tan_phi_kar(self) / self.material_tan_phi) * 180 / np.pi


def calc_c_d(self: CPhiAnalyse):
    return calc_c_kar(self) / self.material_cohesie


def calc_st_dev_phi(self: CPhiAnalyse):
    phi_gem = calc_phi_gem(self)
    phi_d = calc_phi_d(self)
    if phi_gem <= 0 or phi_d <= 0:
        phi_gem = max(phi_gem, 0.1)
        phi_d = max(phi_d, 0.1)
        print(f"Ongeldige waarde phi: phi_gem={calc_phi_gem(self)}, phi_d={calc_phi_d(self)}. "
              f"Nieuwe waardes worden vastgezet op: phi_gem={phi_gem}, phi_d={phi_d}")

    st_dev = phi_gem * math.sqrt(math.exp((((norm.ppf(0.05) * 2) + math.sqrt((norm.ppf(0.05) * 2) ** 2 +
                                                                             8 * (math.log(phi_gem) - math.log(phi_d))))
                                           / 2) ** 2) - 1)
    return st_dev


def calc_st_dev_c(self: CPhiAnalyse):  # TODO er komt een te grote stdev uit - checken
    c_gem = calc_c_gem(self)
    c_d = calc_c_d(self)
    if c_gem <= 0 or c_d <= 0:
        c_gem = max(c_gem, 0.1)
        c_d = max(c_d, 0.1)
        print(f"Ongeldige waarde cohesie: c_gem={calc_c_gem(self)}, c_d={calc_c_d(self)}. "
              f"Nieuwe waardes worden vastgezet op: c_gem={c_gem}, c_d={c_d}")

    st_dev = c_gem * math.sqrt(math.exp((((norm.ppf(0.05) * 2) + math.sqrt((norm.ppf(0.05) * 2) ** 2 +
                                                                           8 * (math.log(c_gem) - math.log(c_d)))) / 2)
                                        ** 2) - 1)
    return st_dev
