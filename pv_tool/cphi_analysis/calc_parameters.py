from __future__ import annotations

import math
import numpy as np
from scipy.stats import linregress, norm
from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
from pv_tool.cphi_analysis.variables import (count_s, sum_s, sum_t, e_a2, a2_kar, a1_kar, t_n_2_sh,
                                             gem_ln_tan_a_sh, std_ln_tan_a_sh,
                                             a2_kar_gecorrigeerd, a1_kar_gecorrigeerd, helling_gecor, var_tan_phi_gem,
                                             var_tan_phi_kar, var_tan_phi_kar_sh)


def calc_watergehalte_gem(self: CPhiAnalyse):
    """Berekent het gemiddelde watergehalte van de geselecteerde monsters [%]."""
    column_name = self.cphi_analyses_data_df.filter(like='WATERGEHALTE_VOOR').columns[0]
    watergehalte = self.cphi_analyses_data_df[column_name]
    return float(watergehalte.mean())


def calc_watergehalte_sd(self: CPhiAnalyse):
    """Berekent de standaarddeviatie van het watergehalte [%]."""
    column_name = self.cphi_analyses_data_df.filter(like='WATERGEHALTE_VOOR').columns[0]
    watergehalte = self.cphi_analyses_data_df[column_name]
    return float(watergehalte.std())


def calc_vgwnat_gem(self: CPhiAnalyse):
    """Berekent het gemiddelde nat volumegewicht [kN/m³]."""
    column_name = self.cphi_analyses_data_df.filter(like='VOLUMEGEWICHT_NAT').columns[0]
    vgwnat = self.cphi_analyses_data_df[column_name]
    return float(vgwnat.mean())


def calc_vgwnat_sd(self: CPhiAnalyse):
    """Berekent de standaarddeviatie van het nat volumegewicht [kN/m³]."""
    column_name = self.cphi_analyses_data_df.filter(like='VOLUMEGEWICHT_NAT').columns[0]
    vgwnat = self.cphi_analyses_data_df[column_name]
    return float(vgwnat.std())


def calc_a2_phi_gem(self: CPhiAnalyse):
    """Berekent een eerste schatting van de gemiddelde phi middels lineaire regressie."""
    x_values = self.cphi_analyses_data_df['S\'']
    y_values = self.cphi_analyses_data_df['T']
    a2_phi_gem = linregress(x=x_values, y=y_values).slope
    return a2_phi_gem


def calc_a2_phi_gem_sh(self: CPhiAnalyse):
    """Berekent een eerste schatting van de gemiddelde phi voor SHANSEP analyse."""
    a2_phi_gem = math.exp(gem_ln_tan_a_sh(self))
    return a2_phi_gem


def calc_a2_phi_kar_onder_sh(self: CPhiAnalyse):
    """Geeft de benadering van de a2 karakteristieke phi ondergrens bij schematiseringshandleiding berekening c phi."""
    a2_phi_kar_onder = math.exp(gem_ln_tan_a_sh(self) + t_n_2_sh(self) * std_ln_tan_a_sh(self) *
                                math.sqrt((1 - self.alpha) + 1 / count_s(self)))
    return a2_phi_kar_onder


def calc_a2_phi_kar_boven_sh(self: CPhiAnalyse):
    """Geeft de benadering van de a2 karakteristieke phi bovengrens bij schematiseringshandleiding berekening c phi."""
    a2_phi_kar_boven = math.exp(gem_ln_tan_a_sh(self) - t_n_2_sh(self) * std_ln_tan_a_sh(self) *
                                math.sqrt((1 - self.alpha) + 1 / count_s(self)))
    return a2_phi_kar_boven


def calc_tan_phi_gem(self: CPhiAnalyse):
    """Berekent de gemiddelde tan(phi) op basis van het analysetype."""
    if self.analysis_type == 'TXT_CPhi':
        return float(helling_gecor(self) / np.sqrt(1 - helling_gecor(self) ** 2))
    elif self.analysis_type == 'DSS_CPhi':
        return float(helling_gecor(self))
    elif self.analysis_type == 'TXT_SH':
        return float(calc_a2_phi_gem_sh(self) / np.sqrt(1 - calc_a2_phi_gem_sh(self) ** 2))
    elif self.analysis_type == 'DSS_SH':
        return float(calc_a2_phi_gem_sh(self))


def helling_gecorrigeerd(self: CPhiAnalyse):
    """Geeft de gecorrigeerde helling van de regressielijn."""
    return helling_gecor(self)


def calc_a1_c_gem(self: CPhiAnalyse):
    """Berekent de gemiddelde cohesie intercept uit de lineaire regressie."""
    return (sum_t(self) - sum_s(self) * e_a2(self)) / count_s(self)


def calc_a2_kar(self: CPhiAnalyse):
    """Berekent de karakteristieke tan(phi), rekening houdend met handmatige invoer."""
    if self.cohesie_gem_handmatig is not None:
        tan_phi_kar = a2_kar_gecorrigeerd(self)
    else:
        tan_phi_kar = a2_kar(self)
    return tan_phi_kar


def calc_tan_phi_d(self: CPhiAnalyse):
    """Berekent de rekenwaarde van tan(phi) op basis van het analysetype."""
    if self.analysis_type in ['TXT_SH', 'DSS_SH']:
        tan_phi_d = calc_tan_phi_kar_sh(self) / self.material_tan_phi
    else:
        tan_phi_d = calc_tan_phi_kar(self) / self.material_tan_phi
    return tan_phi_d


def calc_a1_kar(self: CPhiAnalyse):
    """Berekent de karakteristieke cohesie, rekening houdend met handmatige invoer."""
    if self.cohesie_gem_handmatig is not None:
        cohesie_kar = a1_kar_gecorrigeerd(self)
    else:
        cohesie_kar = a1_kar(self)
    return cohesie_kar


def calc_phi_gem(self: CPhiAnalyse):
    """Berekent de gemiddelde phi in graden."""
    return math.atan(var_tan_phi_gem(self)) * 180 / np.pi


def calc_c_gem(self: CPhiAnalyse):
    """Berekent de gemiddelde cohesie [kPa], rekening houdend met handmatige invoer."""
    if self.cohesie_gem_handmatig is not None:
        coh_gem = self.cohesie_gem_handmatig
    else:
        coh_gem = self.eerste_benadering_a1_gem
    if self.analysis_type == 'TXT_CPhi':
        return float(coh_gem / np.sqrt(1 - helling_gecor(self) ** 2))
    elif self.analysis_type == 'DSS_CPhi':
        return float(coh_gem)
    else:
        print('WAARSCHUWING: analysetype SH bevat geen cohesie')


def calc_phi_kar(self: CPhiAnalyse):
    """Berekent de karakteristieke phi in graden."""
    if self.analysis_type in ['TXT_SH', 'DSS_SH']:
        return float(math.atan(var_tan_phi_kar_sh(self)) * 180 / np.pi)
    else:
        return float(math.atan(var_tan_phi_kar(self)) * 180 / np.pi)


def calc_c_kar(self: CPhiAnalyse):
    """Berekent de karakteristieke cohesie [kPa], rekening houdend met handmatige invoer."""
    if self.phi_kar_handmatig is not None:
        phi_kar = self.phi_kar_handmatig
    else:
        phi_kar = self.eerste_benadering_a2_kar

    # Explicitly check if cohesie_kar_handmatig is not None, including when it's 0
    coh_kar = self.cohesie_kar_handmatig if self.cohesie_kar_handmatig is not None else self.eerste_benadering_a1_kar

    if self.analysis_type == 'TXT_CPhi':
        return float(coh_kar / np.sqrt(1 - phi_kar ** 2))
    elif self.analysis_type == 'DSS_CPhi':
        return float(coh_kar)
    else:
        print('WAARSCHUWING: analysetype SH bevat geen cohesie')


def calc_phi_d(self: CPhiAnalyse):
    """Berekent de rekenwaarde van phi in graden."""
    return float(math.atan(calc_tan_phi_d(self)) * 180 / np.pi)


def calc_c_d(self: CPhiAnalyse):
    """Berekent de rekenwaarde van de cohesie [kPa]."""
    return float(calc_c_kar(self) / self.material_cohesie)


def calc_st_dev_phi(self: CPhiAnalyse):
    """Berekent de standaarddeviatie van phi op basis van gemiddelde en rekenwaarde.

    Raises:
        ValueError: Als phi_gem of phi_d negatief of nul is.
    """
    phi_gem = calc_phi_gem(self)
    phi_d = calc_phi_d(self)

    # Controleer op fysisch onmogelijke waarden
    if phi_gem <= 0:
        raise ValueError(f"Gemiddelde phi waarde moet positief zijn, gevonden waarde: {phi_gem}")
    if phi_d <= 0:
        raise ValueError(f"Rekenwaarde phi moet positief zijn, gevonden waarde: {phi_d}")

    st_dev = phi_gem * math.sqrt(math.exp((((norm.ppf(0.05) * 2) + math.sqrt((norm.ppf(0.05) * 2) ** 2 +
                                                                             8 * (math.log(phi_gem) - math.log(phi_d))))
                                           / 2) ** 2) - 1)
    return float(st_dev)


def calc_st_dev_c(self: CPhiAnalyse):
    """Berekent de standaarddeviatie van de cohesie op basis van gemiddelde en rekenwaarde.

    Geeft een waarschuwing als c_gem of c_d negatief is en retourneert None.
    """
    c_gem = calc_c_gem(self)
    c_d = calc_c_d(self)

    if c_gem <= 0:
        warnings.warn(
            f"Om berekening standaarddeviatie voor D-stability te kunnen doen moet gemiddelde cohesie waarde positief "
            f"zijn, gevonden waarde: {round(c_gem, 3)}. Gemiddelde cohesie wordt aangepast naar 0.01 om "
            f"standaarddeviatie uit te rekenen")
        c_gem = 0.01

    if c_d <= 0:
        warnings.warn(
            f"Om berekening standaarddeviatie voor D-stability te kunnen doen moet rekenwaarde van de cohesie waarde "
            f"positief zijn, gevonden waarde: {round(c_d, 3)}. Rekenwaarde cohesie wordt aangepast naar 0.01 om "
            f"berekening standaarddeviatie voor D-stability te kunnen doen")
        c_d = 0.01

    try:
        st_dev = c_gem * math.sqrt(math.exp((((norm.ppf(0.05) * 2) + math.sqrt((norm.ppf(0.05) * 2) ** 2 +
                                                                               8 * (math.log(c_gem) - math.log(
                                                                                c_d)))) / 2) ** 2) - 1)
        return st_dev
    except (ValueError, OverflowError):
        warnings.warn("Standaarddeviatie berekening resulteerde in een ongeldige waarde.")
        return None


def calc_tan_phi_kar(self: CPhiAnalyse):
    """Berekent de karakteristieke tan(phi) voor CPhi analyses."""
    if self.phi_kar_handmatig is not None:
        phi_kar = self.phi_kar_handmatig
    else:
        phi_kar = self.eerste_benadering_a2_kar

    if self.analysis_type == 'TXT_CPhi':
        return float(phi_kar / np.sqrt(1 - phi_kar ** 2))
    elif self.analysis_type == 'DSS_CPhi':
        return float(phi_kar)
    else:
        print('WAARSCHUWING: tan phi kar voor analysetype SH wordt berekend met de functie calc_tan_phi_kar_sh')


def calc_tan_phi_kar_sh(self: CPhiAnalyse):
    """Berekent de karakteristieke tan(phi) voor SHANSEP analyses."""
    if self.analysis_type == 'TXT_SH':
        return float(calc_a2_phi_kar_onder_sh(self) / np.sqrt(1 - calc_a2_phi_kar_onder_sh(self) ** 2))
    elif self.analysis_type == 'DSS_SH':
        return float(calc_a2_phi_kar_onder_sh(self))
    else:
        print('WAARSCHUWING: tan phi kar voor analysetype CPhi wordt berekend met de functie calc_tan_phi_kar')
