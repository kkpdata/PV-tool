from typing import Optional, List, Literal
from pandas import DataFrame
from pv_tool.analysis.globals import (TWO_PERC_COLUMNS, FIVE_PERC_COLUMNS, FIFTEEN_PERC_COLUMNS, PIEKSTERKTE_COLUMNS,
                                      EINDSTERKTE_COLUMNS, TEXTUAL_NAMES, NEW_COLUMN_NAMES)
import numpy as np
from pv_tool.imports.import_data import Dbase
from enum import Enum
from pv_tool.analysis.expand_analysis_df import *


class Alpha(Enum):
    REGIONAL = 1.0
    LOCAL = 0.75


class CPhiAnalyse:
    def __init__(self, dbase: Dbase, investigation_groups: List, effective_stress: Literal['2% rek', '5% rek', '15% rek', 'pieksterkte', 'eindsterkte']):

        # Data
        self.dbase_df = dbase.dbase_df
        self.investigation_groups = investigation_groups  # kan er 1 zijn, maar ook meer. Dit is puur voor de analyse, later kunnen we in het plaatje meer puntjes erbij plakken.
        self.effective_stress = effective_stress

        # Settings
        self.alpha: Alpha = Alpha.LOCAL
        self.cohesie_gem: Optional[float] = None
        self.phi_kar: Optional[float] = None
        self.cohesie_kar: Optional[float] = None

        # Placeholder
        self.cphi_analyses_data_df: Optional[DataFrame] = None

    def get_cphi_data(self):
        """Deze functie filtert de dbase-dataframe op basis van PV_NAAM en de gewenste effectieve stress. Daarnaast
        worden de kolomnamen aangepast zodat ze ongeacht het rekpercentage allemaal dezelfde kolomnaam hebben."""
        self.cphi_analyses_data_df = self.dbase_df[self.dbase_df['PV_NAAM'].isin(self.investigation_groups)]
        self.cphi_analyses_data_df = self.cphi_analyses_data_df[TEXTUAL_NAMES[self.effective_stress]]
        self.cphi_analyses_data_df.columns = NEW_COLUMN_NAMES


    def expand_analysis_df(self):
        """Deze functie berekend alle benodigde parameters per monster voor de analyse."""
        # kolommen bijlage 5
        calculate_s_tt(self)
        # calculate_s_ty(self)
        # calculate_kappa_2(self)
        # calculate_s(self)
        # calculate_5pr_ondergrens(self)
        # calculate_5pr_bovengrens(self)
        # calculate_s_tt_ondergrens(self)
        # calculate_s_ty_ondergrens(self)
        # calculate_kappa_2_ondergrens(self)
        # # kolommen Leo
        # calculate_correctie_t(self)
        # calculate_5pr_ondergrens_correctie_c(self)
        # calculate_5pr_bovengrens_correctie_c(self)
        # kappa_2_2pr_cor(self)
        # calculate_s_ty_ondergrens_correctie_c(self)
        # calculate_kappa_2_ondergrens_correctie_c(self)

    def _run(self):
        """Deze functie zorgt ervoor dat zodra er iets veranderd in de bron-data alles opnieuw wordt berekend."""
        self.get_cphi_data()
        self.expand_analysis_df()
        self.task2()
        self.task3()

    def output_values(self):
        pass

    def output_table_row(self):
        self._run()

    def figure(self):
        self._run()

    def factsheet(self):
        self._run()

# voorbeeld uitvoer
# my_analysis = CPhiAnalyse(dbase=..., investigation_groups=['klei_licht'], effective_stress='2%')
# my_analysis.figure().show()
# dbase.change_group.minus(16)
# my_analysis.figure().show()
# my_analysis.alpha = 0.8
# my_analysis.figure().show()


# class CPhiAnalyses:
#     def __init__(self):
#         self.analyses: List[CPhiAnalyse] = []
#
#     def output_table(self):
#         output_df = ...
#         for analysis in self.analyses:
#             output_df.append(analysis.output_table_row)
