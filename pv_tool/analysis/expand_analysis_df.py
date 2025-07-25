from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pv_tool.analysis.c_phi_analysis import CPhiAnalyse


def calculate_s_tt(self: CPhiAnalyse):
    som_s = self.cphi_analyses_data_df['S\''].sum()
    print(som_s)
    aantal_s = self.cphi_analyses_data_df['S\''].count()
    print(aantal_s)
    formule = (self.cphi_analyses_data_df['S\''] - som_s / aantal_s) ** 2
    self.cphi_analyses_data_df['s_tt'] = formule


def calculate_s_ty(self):
    pass


def calculate_kappa_2(self):
    pass


def calculate_s(self):
    pass


def calculate_5pr_ondergrens(self):
    pass


def calculate_5pr_bovengrens(self):
    pass


def calculate_s_tt_ondergrens(self):
    pass


def calculate_s_ty_ondergrens(self):
    pass


def calculate_kappa_2_ondergrens(self):
    pass


# kolommen Leo
def calculate_correctie_t(self):
    pass


def calculate_5pr_ondergrens_correctie_c(self):
    pass


def calculate_5pr_bovengrens_correctie_c(self):
    pass


def kappa_2_2pr_cor(self):
    pass


def calculate_s_ty_ondergrens_correctie_c(self):
    pass


def calculate_kappa_2_ondergrens_correctie_c(self):
    pass
