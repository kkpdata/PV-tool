from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
from pv_tool.shansep_analysis.variables import (count_sv_oc, sum_sv_oc, e_a1_oc, e_a2_oc,
                                                t_n_2_oc, sigma_a1_oc, sigma_a2_oc, rho_a1_a2_oc,
                                                sum_chi_2_oc, count_s_eff_oc, sum_s_eff_oc,
                                                count_ln_ocr_nc_oc, sum_ln_ocr_nc_oc, e_a1_nc_oc, e_a2_nc_oc,
                                                t_n_2_nc_oc, sigma_a1_nc_oc, sigma_a2_nc_oc, rho_a1_a2_nc_oc,
                                                sum_chi_2_nc_oc, count_s_eff_nc_oc, sum_s_eff_nc_oc,
                                                a1_kar_oc, a2_kar_oc,
                                                a1_kar_nc_oc, a2_kar_nc_oc)
import numpy as np

# -------------------------- algemeen ---------------------------------------

def calculate_ln_ocr(self: SHANSEP):
    self.shansep_data_df.loc[:, 'LN(OCR)'] = (
        self.shansep_data_df['OCR'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))

def calculate_sv_spop(self: SHANSEP):
    self.shansep_data_df.loc[:, 'S'] = self.shansep_data_df['Su'] / self.shansep_data_df['S\'v']

def calculate_ln_sv_spop(self: SHANSEP):
    self.shansep_data_df.loc[:, 'LN(su/svc)'] = (
        self.shansep_data_df['S'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))

def calculate_pop(self: SHANSEP):
    self.shansep_data_df.loc[:, 'POP'] = ((self.shansep_data_df['terreinspanning'] *
                                            self.shansep_data_df['OCR']) -
                                            self.shansep_data_df['terreinspanning'])

# -------------------------- alleen OC ---------------------------------------

def calculate_sv_tt_oc(self: SHANSEP):
    df = self.shansep_data_df_oc.copy()
    df['s_tt'] = (df['S\'v'] - sum_sv_oc(self) / count_sv_oc(self)) ** 2
    self.shansep_data_df_oc = df

def calculate_sv_ty_oc(self: SHANSEP):
    df = self.shansep_data_df_oc.copy()
    mean_s = sum_sv_oc(self) / count_sv_oc(self)
    df['s_ty'] = (df['S\'v'] - mean_s) * df['Su']
    self.shansep_data_df_oc = df

def calculate_chi_2_oc(self: SHANSEP):
    formule = (self.shansep_data_df_oc['Su'] - e_a1_oc(self) - e_a2_oc(self) * self.shansep_data_df_oc['S\'v']) ** 2
    self.shansep_data_df_oc['chi_2'] = formule

def s_min_oc(self: SHANSEP):
    return self.shansep_data_df_oc['S\'v'].min()

def s_max_oc(self: SHANSEP):
    return self.shansep_data_df_oc['S\'v'].max()

def calculate_sv_eff_oc(self: SHANSEP):
    """Berekent s' waarden met gelijke intervallen tussen min en max."""
    lijst = [s_min_oc(self)]
    formule = (s_max_oc(self) - s_min_oc(self)) / (count_sv_oc(self) - 1)
    aantal_waarden = len(self.shansep_data_df_oc)
    for i in range(1, aantal_waarden):
        nieuwe_waarde = lijst[i - 1] + formule
        lijst.append(nieuwe_waarde)
    self.shansep_data_df_oc['s\''] = lijst

def calculate_5pr_ondergrens_oc(self: SHANSEP):
    formule = (
            e_a1_oc(self) +
            e_a2_oc(self) * self.shansep_data_df_oc['s\''] - t_n_2_oc(self) *
            (sigma_a1_oc(self) ** 2 + self.shansep_data_df_oc['s\''] ** 2 * sigma_a2_oc(self) ** 2 +
             2 * rho_a1_a2_oc(self) * self.shansep_data_df_oc['s\''] * sigma_a1_oc(self) * sigma_a2_oc(self) +
             (1.0 - self.alpha) * (sum_chi_2_oc(self) / (count_sv_oc(self) - 2))) ** 0.5
    )
    self.shansep_data_df_oc['5_pr_ondergrens'] = formule


def calculate_5pr_bovengrens_oc(self: SHANSEP):
    formule = (
            e_a1_oc(self) +
            e_a2_oc(self) * self.shansep_data_df_oc['s\''] + t_n_2_oc(self) *
            (sigma_a1_oc(self) ** 2 + self.shansep_data_df_oc['s\''] ** 2 * sigma_a2_oc(self) ** 2 +
             2 * rho_a1_a2_oc(self) * self.shansep_data_df_oc['s\''] * sigma_a1_oc(self) * sigma_a2_oc(self) +
             (1 - self.alpha) * (sum_chi_2_oc(self) / (count_sv_oc(self) - 2))) ** 0.5
    )
    self.shansep_data_df_oc['5_pr_bovengrens'] = formule


def calculate_sv_tt_ondergrens_oc(self: SHANSEP):
    formule = (self.shansep_data_df_oc['s\''] - sum_s_eff_oc(self) / count_s_eff_oc(self)) ** 2
    self.shansep_data_df_oc['s_tt_ondergrens'] = formule


def calculate_sv_ty_ondergrens_oc(self: SHANSEP):
    formule = (self.shansep_data_df_oc['s\''] - sum_s_eff_oc(self) /
               count_s_eff_oc(self)) * self.shansep_data_df_oc['5_pr_ondergrens']
    self.shansep_data_df_oc['s_ty_ondergrens'] = formule


def calculate_chi_2_ondergrens_oc(self: SHANSEP):
    formule = (self.shansep_data_df_oc['5_pr_ondergrens'] - a1_kar_oc(self) -
               a2_kar_oc(self) * self.shansep_data_df_oc['s\'']) ** 2
    self.shansep_data_df_oc['chi_2_ondergrens'] = formule


# -------------------------- NC en OC ---------------------------------------
# TODO omdat OCR niet goed wordt berekend, werkt deze fout door in de hele analyse vanaf hier

def calculate_sv_tt_nc_oc(self: SHANSEP):
    df = self.shansep_data_df_nc_oc.copy()
    df['s_tt'] = (df['LN(OCR)'] - sum_ln_ocr_nc_oc(self) / count_ln_ocr_nc_oc(self)) ** 2
    self.shansep_data_df_nc_oc = df

def calculate_sv_ty_nc_oc(self: SHANSEP):
    df = self.shansep_data_df_nc_oc.copy()
    mean_s = sum_ln_ocr_nc_oc(self) / count_ln_ocr_nc_oc(self)
    df['s_ty'] = (df['LN(OCR)'] - mean_s) * df['LN(su/svc)']
    self.shansep_data_df_nc_oc = df

def calculate_chi_2_nc_oc(self: SHANSEP):
    formule = (self.shansep_data_df_nc_oc['LN(su/svc)'] - e_a1_nc_oc(self) - e_a2_nc_oc(self) * self.shansep_data_df_nc_oc['LN(OCR)']) ** 2
    self.shansep_data_df_nc_oc['chi_2'] = formule

def s_min_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['LN(OCR)'].min()

def s_max_nc_oc(self: SHANSEP):
    return self.shansep_data_df_nc_oc['LN(OCR)'].max()

def calculate_sv_eff_nc_oc(self: SHANSEP):
    """Berekent s' waarden met gelijke intervallen tussen min en max."""
    lijst = [s_min_nc_oc(self)]
    formule = (s_max_nc_oc(self) - s_min_nc_oc(self)) / (count_ln_ocr_nc_oc(self) - 1)
    aantal_waarden = len(self.shansep_data_df_nc_oc)
    for i in range(1, aantal_waarden):
        nieuwe_waarde = lijst[i - 1] + formule
        lijst.append(nieuwe_waarde)
    self.shansep_data_df_nc_oc['s\''] = lijst

def calculate_5pr_ondergrens_nc_oc(self: SHANSEP): # TODO de uitgerekende waardes zijn te klein, ligt dit alleen aan de OCR berekening?
    formule = (
            e_a1_nc_oc(self) +
            e_a2_nc_oc(self) * self.shansep_data_df_nc_oc['s\''] - t_n_2_nc_oc(self) *
            (sigma_a1_nc_oc(self) ** 2 + self.shansep_data_df_nc_oc['s\''] ** 2 * sigma_a2_nc_oc(self) ** 2 +
             2 * rho_a1_a2_nc_oc(self) * self.shansep_data_df_nc_oc['s\''] * sigma_a1_nc_oc(self) * sigma_a2_nc_oc(self) +
             (1.0 - self.alpha) * (sum_chi_2_nc_oc(self) / (count_ln_ocr_nc_oc(self) - 2))) ** 0.5
    )
    # print de formule waarde voor waarde om er achter te komen waar de fout zit
    print(f"formule: {formule}")
    print(f"e_a1_nc_oc: {e_a1_nc_oc(self)}")
    print(f"e_a2_nc_oc: {e_a2_nc_oc(self)}")
    print(f"s\': {self.shansep_data_df_nc_oc['s\''].iloc[:5]}")
    print(f"t_n_2_nc_oc: {t_n_2_nc_oc(self)}")
    print(f"sigma_a1_nc_oc: {sigma_a1_nc_oc(self)}")
    print(f"sigma_a2_nc_oc: {sigma_a2_nc_oc(self)}")
    print(f"rho_a1_a2_nc_oc: {rho_a1_a2_nc_oc(self)}")
    print(f"sum_chi_2_nc_oc: {sum_chi_2_nc_oc(self)}")
    print(f"count_ln_ocr_nc_oc: {count_ln_ocr_nc_oc(self)}")

    self.shansep_data_df_nc_oc['5_pr_ondergrens'] = formule


def calculate_5pr_bovengrens_nc_oc(self: SHANSEP):
    formule = (
            e_a1_nc_oc(self) +
            e_a2_nc_oc(self) * self.shansep_data_df_nc_oc['s\''] + t_n_2_nc_oc(self) *
            (sigma_a1_nc_oc(self) ** 2 + self.shansep_data_df_nc_oc['s\''] ** 2 * sigma_a2_nc_oc(self) ** 2 +
             2 * rho_a1_a2_nc_oc(self) * self.shansep_data_df_nc_oc['s\''] * sigma_a1_nc_oc(self) * sigma_a2_nc_oc(self) +
             (1 - self.alpha) * (sum_chi_2_nc_oc(self) / (count_ln_ocr_nc_oc(self) - 2))) ** 0.5
    )
    self.shansep_data_df_nc_oc['5_pr_bovengrens'] = formule


def calculate_sv_tt_ondergrens_nc_oc(self: SHANSEP):
    formule = (self.shansep_data_df_nc_oc['s\''] - sum_s_eff_nc_oc(self) / count_s_eff_nc_oc(self)) ** 2
    self.shansep_data_df_nc_oc['s_tt_ondergrens'] = formule


def calculate_sv_ty_ondergrens_nc_oc(self: SHANSEP):
    formule = (self.shansep_data_df_nc_oc['s\''] - sum_s_eff_nc_oc(self) /
               count_s_eff_nc_oc(self)) * self.shansep_data_df_nc_oc['5_pr_ondergrens']
    self.shansep_data_df_nc_oc['s_ty_ondergrens'] = formule


def calculate_chi_2_ondergrens_nc_oc(self: SHANSEP):
    formule = (self.shansep_data_df_nc_oc['5_pr_ondergrens'] - a1_kar_nc_oc(self) -
               a2_kar_nc_oc(self) * self.shansep_data_df_nc_oc['s\'']) ** 2
    self.shansep_data_df_nc_oc['chi_2_ondergrens'] = formule


# -------------------------- sutabel-m methode ---------------------------------------

def calculate_ln_sv_sutabel(self: SHANSEP):
    """Berekent ln(s'v) voor de sutabel dataframe."""
    self.shansep_data_df_sutabel.loc[:, 'ln(s\'v)'] = (
        self.shansep_data_df_sutabel['S\'v'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))


def calculate_ln_su_sutabel(self: SHANSEP):
    """Berekent ln(su) voor de sutabel dataframe."""
    self.shansep_data_df_sutabel.loc[:, 'ln(su)'] = (
        self.shansep_data_df_sutabel['Su'].apply
        (lambda x: np.log(x) if x is not None and x > 0 else ""))


def calculate_sv_tt_sutabel(self: SHANSEP):
    """Berekent s_tt voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import count_ln_sv_sutabel, sum_ln_sv_sutabel
    df = self.shansep_data_df_sutabel.copy()
    df['s_tt'] = (df['ln(s\'v)'] - sum_ln_sv_sutabel(self) / count_ln_sv_sutabel(self)) ** 2
    self.shansep_data_df_sutabel = df


def calculate_sv_ty_sutabel(self: SHANSEP):
    """Berekent s_ty voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import count_ln_sv_sutabel, sum_ln_sv_sutabel
    df = self.shansep_data_df_sutabel.copy()
    mean_s = sum_ln_sv_sutabel(self) / count_ln_sv_sutabel(self)
    df['s_ty'] = (df['ln(s\'v)'] - mean_s) * df['ln(su)']
    self.shansep_data_df_sutabel = df


def calculate_chi_2_sutabel(self: SHANSEP):
    """Berekent chi_2 voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import e_a1_sutabel, e_a2_sutabel
    formule = (self.shansep_data_df_sutabel['ln(su)'] - e_a1_sutabel(self) -
               e_a2_sutabel(self) * self.shansep_data_df_sutabel['ln(s\'v)']) ** 2
    self.shansep_data_df_sutabel['chi_2'] = formule


def s_min_sutabel(self: SHANSEP):
    """Berekent minimum ln(s'v) waarde voor sutabel analyse."""
    return self.shansep_data_df_sutabel['ln(s\'v)'].min()


def s_max_sutabel(self: SHANSEP):
    """Berekent maximum ln(s'v) waarde voor sutabel analyse."""
    return self.shansep_data_df_sutabel['ln(s\'v)'].max()


def calculate_sv_eff_sutabel(self: SHANSEP):
    """Berekent s' waarden met gelijke intervallen tussen min en max voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import count_ln_sv_sutabel
    lijst = [s_min_sutabel(self)]
    formule = (s_max_sutabel(self) - s_min_sutabel(self)) / (count_ln_sv_sutabel(self) - 1)
    aantal_waarden = len(self.shansep_data_df_sutabel)
    for i in range(1, aantal_waarden):
        nieuwe_waarde = lijst[i - 1] + formule
        lijst.append(nieuwe_waarde)
    self.shansep_data_df_sutabel['s\''] = lijst


def calculate_5pr_ondergrens_sutabel(self: SHANSEP):
    """Berekent 5% ondergrens voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import (e_a1_sutabel, e_a2_sutabel, t_n_2_sutabel,
                                                      sigma_a1_sutabel, sigma_a2_sutabel,
                                                      rho_a1_a2_sutabel, sum_chi_2_sutabel,
                                                      count_ln_sv_sutabel)
    formule = (
            e_a1_sutabel(self) +
            e_a2_sutabel(self) * self.shansep_data_df_sutabel['s\''] - t_n_2_sutabel(self) *
            (sigma_a1_sutabel(self) ** 2 + self.shansep_data_df_sutabel['s\''] ** 2 * sigma_a2_sutabel(self) ** 2 +
             2 * rho_a1_a2_sutabel(self) * self.shansep_data_df_sutabel['s\''] * sigma_a1_sutabel(self) * sigma_a2_sutabel(self) +
             (1.0 - self.alpha) * (sum_chi_2_sutabel(self) / (count_ln_sv_sutabel(self) - 2))) ** 0.5
    )
    self.shansep_data_df_sutabel['5_pr_ondergrens'] = formule


def calculate_5pr_bovengrens_sutabel(self: SHANSEP):
    """Berekent 5% bovengrens voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import (e_a1_sutabel, e_a2_sutabel, t_n_2_sutabel,
                                                      sigma_a1_sutabel, sigma_a2_sutabel,
                                                      rho_a1_a2_sutabel, sum_chi_2_sutabel,
                                                      count_ln_sv_sutabel)
    formule = (
            e_a1_sutabel(self) +
            e_a2_sutabel(self) * self.shansep_data_df_sutabel['s\''] + t_n_2_sutabel(self) *
            (sigma_a1_sutabel(self) ** 2 + self.shansep_data_df_sutabel['s\''] ** 2 * sigma_a2_sutabel(self) ** 2 +
             2 * rho_a1_a2_sutabel(self) * self.shansep_data_df_sutabel['s\''] * sigma_a1_sutabel(self) * sigma_a2_sutabel(self) +
             (1 - self.alpha) * (sum_chi_2_sutabel(self) / (count_ln_sv_sutabel(self) - 2))) ** 0.5
    )
    self.shansep_data_df_sutabel['5_pr_bovengrens'] = formule


def calculate_sv_tt_ondergrens_sutabel(self: SHANSEP):
    """Berekent s_tt ondergrens voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import sum_s_eff_sutabel, count_s_eff_sutabel
    formule = (self.shansep_data_df_sutabel['s\''] - sum_s_eff_sutabel(self) / count_s_eff_sutabel(self)) ** 2
    self.shansep_data_df_sutabel['s_tt_ondergrens'] = formule


def calculate_sv_ty_ondergrens_sutabel(self: SHANSEP):
    """Berekent s_ty ondergrens voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import sum_s_eff_sutabel, count_s_eff_sutabel
    formule = (self.shansep_data_df_sutabel['s\''] - sum_s_eff_sutabel(self) /
               count_s_eff_sutabel(self)) * self.shansep_data_df_sutabel['5_pr_ondergrens']
    self.shansep_data_df_sutabel['s_ty_ondergrens'] = formule


def calculate_chi_2_ondergrens_sutabel(self: SHANSEP):
    """Berekent chi_2 ondergrens voor sutabel analyse."""
    from pv_tool.shansep_analysis.variables import a1_kar_sutabel, a2_kar_sutabel
    formule = (self.shansep_data_df_sutabel['5_pr_ondergrens'] - a1_kar_sutabel(self) -
               a2_kar_sutabel(self) * self.shansep_data_df_sutabel['s\'']) ** 2
    self.shansep_data_df_sutabel['chi_2_ondergrens'] = formule
