from typing import Optional, List
from pandas import DataFrame


class CPhi:
    """Deze class bevat alle functies die te maken hebben met de C-phi analyse"""

    def __init__(self):
        self.dbase_df: Optional[DataFrame] = None
        self.analysis_df: Optional[DataFrame] = None

    def get_selection_for_analysis(self, investigation_groups: List):
        """Deze functie maakt een selecte van de benodigde date voor de C-Phi-analyse"""
        columns = ['ALG__BORING_MONSTERNR', 'PV_NAAM', 'TXT_SS_S\'_2%', 'TXT_SS_T_2%', 'TXT_SS_S\'_5%', 'TXT_SS_T_5%',
                   'TXT_SS_S\'_15%', 'TXT_SS_T_15%', 'TXT_SS_S\'_BIJ_T_PIEK', 'TXT_SS_T_PIEK', 'TXT_SS_S\'_BIJ_T_EIND',
                   'TXT_SS_T_EIND']
        filtered_df = self.dbase_df[self.dbase_df['PV_NAAM'].isin(investigation_groups)]
        self.analysis_df = filtered_df[columns]

    def expand_analysis_df(self):
        """Deze functie berekend alle benodigde parameters per monster voor de analyse."""
        # kolommen bijlage 5
        self.calculate_s_tt()
        self.calculate_s_ty()
        self.calculate_kappa_2()
        self.calculate_s()
        self.calculate_5pr_ondergrens()
        self.calcualte_5pr_bovengrens()
        self.calculate_s_tt_ondergrens()
        self.calcualte_s_ty_ondergrens()
        self.calculate_kappa_2_ondergrens()
        #kolommen Leo
        self.calculate_correctie_t()
        self.calculate_5pr_ondergrens_correctie_c()
        self.calculate_5pr_bovengrens_correctie_c()
        self.kappa_2_2pr_cor()
        self.calculate_s_ty_ondergrens_correctie_c()
        self.calculate_kappa_2_ondergrens_correctie_c
        pass
