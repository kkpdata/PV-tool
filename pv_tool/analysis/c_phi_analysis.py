from typing import Optional, List, Literal
from pandas import DataFrame
from pv_tool.analysis.globals import (TWO_PERC_COLUMNS, FIVE_PERC_COLUMNS, FIFTEEN_PERC_COLUMNS, PIEKSTERKTE_COLUMNS,
                                      EINDSTERKTE_COLUMNS)3
import numpy as np

class CPhi:
    """Deze class bevat alle functies die te maken hebben met de C-phi analyse"""

    def __init__(self):
        self.two_pr_df = None
        self.dbase_df: Optional[DataFrame] = None
        self.analysis_df: Optional[DataFrame] = None

    def get_selection_for_analysis(self, investigation_groups: List, effective_stress: Literal = ['2% rek', '5% rek', '15% rek', 'pieksterkte', 'eindsterkte']):
        """Deze functie maakt een selecte van de benodigde date voor de C-Phi-analyse"""
        if effective_stress == '2% rek':
            self.two_pr_df = self.dbase_df.copy(deep=True)
            self.two_pr_df = self.two_pr_df.reindex(columns=TWO_PERC_COLUMNS, fill_value=np.nan)
        # TODO: hier gebleven
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
