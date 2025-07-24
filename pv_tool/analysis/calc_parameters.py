from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.analysis.c_phi_analysis import CPhiAnalyse
from pv_tool.analysis.variables import *
from scipy.stats import linregress


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
        cohesie_kar = a1_kar(self)
    return cohesie_kar
