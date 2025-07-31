from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.analysis.c_phi_analysis import CPhiAnalyse
from pv_tool.analysis.variables import *
from scipy.stats import linregress, norm


def calc_a2_phi_gem(self: CPhiAnalyse):
    """Geeft een eerste benadering voor de gemiddelde phi."""
    x_values = self.cphi_analyses_data_df['S\'']
    y_values = self.cphi_analyses_data_df['T']
    a2_phi_gem = linregress(x=x_values, y=y_values).slope
    return a2_phi_gem


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
    # =$C$89 / WORTEL(1 -$C$89 ^ 2)
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
    if self.cohesie_gem_handmatig is not None:
        coh_gem = self.cohesie_gem_handmatig
    else:
        coh_gem = self.eerste_benadering_a1_gem
    return coh_gem / np.sqrt(1 - helling_gecor(self) ** 2)


def calc_phi_kar(self: CPhiAnalyse):
    return math.atan(var_tan_phi_kar(self)) * 180 / np.pi


def calc_c_kar(self: CPhiAnalyse):
    if self.phi_kar_handmatig is not None:
        phi_kar = self.phi_kar_handmatig
    else:
        phi_kar = self.eerste_benadering_a2_kar
    if self.cohesie_kar_handmatig is not None:
        coh_kar = self.cohesie_kar_handmatig
    else:
        coh_kar = self.eerste_benadering_a1_kar
    return coh_kar / np.sqrt(1 - phi_kar ** 2)


def calc_phi_d(self: CPhiAnalyse):  # TODO: dit berekent de phi d en niet tan phi d - eventueel nog aanpassen
    return math.atan(var_tan_phi_kar(self) / self.material_tan_phi) * 180 / np.pi


def calc_c_d(self: CPhiAnalyse):
    return calc_c_kar(self) / self.material_cohesie


def calc_st_dev_phi(self: CPhiAnalyse):  # TODO: check of het klopt als de rest klopt
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


def calc_st_dev_c(self: CPhiAnalyse):  # TODO: check of het klopt als de rest klopt.
    c_gem = calc_c_gem(self)
    c_d = calc_c_d(self)
    if c_gem <= 0 or c_d <= 0:
        c_gem = max(c_gem, 0.1)
        c_d = max(c_d, 0.1)

    st_dev = c_gem * math.sqrt(math.exp((((norm.ppf(0.05) * 2) + math.sqrt((norm.ppf(0.05) * 2) ** 2 +
                                                                           8 * (math.log(c_gem) - math.log(c_d)))) / 2)
                                        ** 2) - 1)
    return st_dev
