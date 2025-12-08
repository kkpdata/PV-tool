from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
from pv_tool.cphi_analysis.variables import *


def calculate_tan_a(self: CPhiAnalyse):
    """Berekent de tangens van hoek a voor alle rijen in de DataFrame."""
    df = self.cphi_analyses_data_df.copy()
    df.loc[:, 'tan(a)'] = df['T'] / df['S\'']
    self.cphi_analyses_data_df = df


def calculate_ln_tan_a(self: CPhiAnalyse):
    """Berekent de natuurlijke logaritme van tan(a) voor alle rijen in de DataFrame."""
    df = self.cphi_analyses_data_df.copy()
    df.loc[:, 'LN(tan(a))'] = df['tan(a)'].apply(lambda x: np.log(x) if x is not None and x > 0 else "")
    self.cphi_analyses_data_df = df


def calculate_s_tt(self: CPhiAnalyse):
    """Berekent de s_tt waarden voor de statistische analyse."""
    df = self.cphi_analyses_data_df.copy()
    df['s_tt'] = (df['S\''] - sum_s(self) / count_s(self)) ** 2
    self.cphi_analyses_data_df = df


def calculate_s_ty(self: CPhiAnalyse):
    """Berekent de s_ty waarden voor de statistische analyse."""
    df = self.cphi_analyses_data_df.copy()
    mean_s = sum_s(self) / count_s(self)
    df['s_ty'] = (df['S\''] - mean_s) * df['T']
    self.cphi_analyses_data_df = df


def calculate_kappa_2(self: CPhiAnalyse):
    """Berekent kappa_2 waarden voor de statistische analyse."""
    formule = (self.cphi_analyses_data_df['T'] - e_a1(self) - e_a2(self) * self.cphi_analyses_data_df['S\'']) ** 2
    self.cphi_analyses_data_df['kappa_2'] = formule


def s_min(self: CPhiAnalyse):
    """Geeft de minimale S' waarde terug."""
    return self.cphi_analyses_data_df['S\''].min()


def s_max(self: CPhiAnalyse):
    """Geeft de maximale S' waarde terug."""
    return self.cphi_analyses_data_df['S\''].max()


def calculate_s(self: CPhiAnalyse):
    """Berekent s' waarden met gelijke intervallen tussen min en max."""
    lijst = [s_min(self)]
    formule = (s_max(self) - s_min(self)) / (count_s(self) - 1)
    aantal_waarden = len(self.cphi_analyses_data_df)
    for i in range(1, aantal_waarden):
        nieuwe_waarde = lijst[i - 1] + formule
        lijst.append(nieuwe_waarde)
    self.cphi_analyses_data_df['s\''] = lijst


def calculate_5pr_ondergrens(self: CPhiAnalyse):
    """Berekent de 5% ondergrens van het betrouwbaarheidsinterval."""
    formule = (
            e_a1(self) +
            e_a2(self) * self.cphi_analyses_data_df['s\''] - t_n_2(self) *
            (sigma_a1(self) ** 2 + self.cphi_analyses_data_df['s\''] ** 2 * sigma_a2(self) ** 2 +
             2 * rho_a1_a2(self) * self.cphi_analyses_data_df['s\''] * sigma_a1(self) * sigma_a2(self) +
             (1.0 - self.alpha) * (sum_kappa_2(self) / (count_s(self) - 2))) ** 0.5
    )
    self.cphi_analyses_data_df['5_pr_ondergrens'] = formule


def calculate_5pr_bovengrens(self: CPhiAnalyse):
    """Berekent de 5% bovengrens van het betrouwbaarheidsinterval."""
    formule = (
            e_a1(self) +
            e_a2(self) * self.cphi_analyses_data_df['s\''] + t_n_2(self) *
            (sigma_a1(self) ** 2 + self.cphi_analyses_data_df['s\''] ** 2 * sigma_a2(self) ** 2 +
             2 * rho_a1_a2(self) * self.cphi_analyses_data_df['s\''] * sigma_a1(self) * sigma_a2(self) +
             (1 - self.alpha) * (sum_kappa_2(self) / (count_s(self) - 2))) ** 0.5
    )
    self.cphi_analyses_data_df['5_pr_bovengrens'] = formule


def calculate_s_tt_ondergrens(self: CPhiAnalyse):
    """Berekent de s_tt waarden voor de ondergrens analyse."""
    formule = (self.cphi_analyses_data_df['s\''] - sum_s2(self) / count_s2(self)) ** 2
    self.cphi_analyses_data_df['s_tt_ondergrens'] = formule


def calculate_s_ty_ondergrens(self: CPhiAnalyse):
    """Berekent de s_ty waarden voor de ondergrens analyse."""
    formule = (self.cphi_analyses_data_df['s\''] - sum_s2(self) /
               count_s2(self)) * self.cphi_analyses_data_df['5_pr_ondergrens']
    self.cphi_analyses_data_df['s_ty_ondergrens'] = formule


def calculate_kappa_2_ondergrens(self: CPhiAnalyse):
    """Berekent kappa_2 waarden voor de ondergrens analyse."""
    formule = (self.cphi_analyses_data_df['5_pr_ondergrens'] - a1_kar(self) -
               a2_kar(self) * self.cphi_analyses_data_df['s\'']) ** 2
    self.cphi_analyses_data_df['kappa_2_ondergrens'] = formule


def calculate_correctie_t(self: CPhiAnalyse):
    """Berekent de T-correctie op basis van gemiddelde cohesie."""
    if self.cohesie_gem_handmatig is not None:
        coh_gem = self.cohesie_gem_handmatig
    else:
        coh_gem = self.eerste_benadering_a1_gem
    self.cphi_analyses_data_df['correctie_t'] = (- coh_gem + self.cphi_analyses_data_df['T'])


def kappa_2_2pr_cor(self: CPhiAnalyse):
    """Berekent gecorrigeerde kappa_2 waarden voor 2-parameter analyse."""
    if self.cohesie_gem_handmatig is not None:
        coh_gem = self.cohesie_gem_handmatig
    else:
        coh_gem = self.eerste_benadering_a1_gem
    formule = (self.cphi_analyses_data_df['T'] - coh_gem -
               helling_gecor(self) * self.cphi_analyses_data_df['S\'']) ** 2
    self.cphi_analyses_data_df['kappa_2_2pr_cor'] = formule


def calculate_5pr_ondergrens_correctie_c(self: CPhiAnalyse):
    """Berekent gecorrigeerde 5% ondergrens voor cohesie."""
    if self.cohesie_gem_handmatig is not None:
        coh_gem = self.cohesie_gem_handmatig
    else:
        coh_gem = self.eerste_benadering_a1_gem
    formule = (coh_gem + helling_gecor(self) *
               self.cphi_analyses_data_df['s\''] - t_n_2(self) *
               (sigma_a1_gecorrigeerd(self) ** 2 + self.cphi_analyses_data_df['s\''] ** 2 * sigma_a2_gecorrigeerd(
                   self) ** 2 +
                2 * rho_a1_a2(self) * self.cphi_analyses_data_df['s\''] * sigma_a1_gecorrigeerd(self) *
                sigma_a2_gecorrigeerd(self) + (1 - self.alpha) *
                (sum_kappa_2_2pr_gecorrigeerd(self) / (count_s(self) - 2))) ** 0.5)
    self.cphi_analyses_data_df['5pr_ondergrens_cor'] = formule


def calculate_5pr_bovengrens_correctie_c(self: CPhiAnalyse):
    """Berekent gecorrigeerde 5% bovengrens voor cohesie."""
    if self.cohesie_gem_handmatig is not None:
        coh_gem = self.cohesie_gem_handmatig
    else:
        coh_gem = self.eerste_benadering_a1_gem
    formule = (coh_gem + helling_gecor(self) * self.cphi_analyses_data_df['s\''] + t_n_2(self) *
               (sigma_a1_gecorrigeerd(self) ** 2 + self.cphi_analyses_data_df['s\''] ** 2 * sigma_a2_gecorrigeerd(
                   self) ** 2 +
                2 * rho_a1_a2(self) * self.cphi_analyses_data_df['s\''] * sigma_a1_gecorrigeerd(self) *
                sigma_a2_gecorrigeerd(self) + (1 - self.alpha) *
                (sum_kappa_2_2pr_gecorrigeerd(self) / (count_s(self) - 2))) ** 0.5)
    self.cphi_analyses_data_df['5pr_bovengrens_cor'] = formule


def calculate_s_ty_ondergrens_correctie_c(self: CPhiAnalyse):
    """Berekent de gecorrigeerde s_ty waarden voor de ondergrens analyse."""
    formule = ((self.cphi_analyses_data_df['s\''] - sum_s2(self) / count_s2(self)) *
               self.cphi_analyses_data_df['5pr_ondergrens_cor'])
    self.cphi_analyses_data_df['s_ty_ondergrens_cor'] = formule


def calculate_kappa_2_ondergrens_correctie_c(self: CPhiAnalyse):
    """Berekent de gecorrigeerde kappa_2 waarden voor de ondergrens analyse."""
    formule = (self.cphi_analyses_data_df['5pr_ondergrens_cor'] - a1_kar(self) -
               a2_kar(self) * self.cphi_analyses_data_df['s\'']) ** 2
    self.cphi_analyses_data_df['kappa_2_ondergrens_cor'] = formule
