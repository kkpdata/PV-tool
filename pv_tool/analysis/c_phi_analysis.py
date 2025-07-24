from typing import Optional, List, Literal
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pandas import DataFrame
from pv_tool.analysis.globals import (TEXTUAL_NAMES, NEW_COLUMN_NAMES)
from pv_tool.imports.import_data import Dbase
from enum import Enum
from pv_tool.analysis.expand_analysis_df import *
from pv_tool.analysis.calc_parameters import *
from pv_tool.analysis.visualization import *


class Alpha(Enum):
    REGIONAL = 1.0
    LOCAL = 0.75


class CPhiAnalyse:
    def __init__(self, dbase: Dbase,
                 analysis_type: Literal['TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH'],
                 investigation_groups: List,
                 effective_stress: Literal['2% rek', '5% rek', '15% rek', 'pieksterkte', 'eindsterkte']):

        # Data
        self.dbase_df = dbase.dbase_df
        self.analysis_type = analysis_type
        self.investigation_groups = investigation_groups  # kan er 1 zijn, maar ook meer. Dit is puur voor de analyse, later kunnen we in het plaatje meer puntjes erbij plakken.
        self.effective_stress = effective_stress

        # Settings
        self.alpha: Alpha = Alpha.REGIONAL
        self.material_cohesie: Optional[float] = 1.0
        self.material_tan_phi: Optional[float] = 1.0
        self.cohesie_gem_handmatig: Optional[float] = None
        self.phi_kar_handmatig: Optional[float] = None
        self.cohesie_kar_handmatig: Optional[float] = None

        # Placeholder
        self.cphi_analyses_data_df: Optional[DataFrame] = None

        # Results
        self.tan_phi_gem: Optional[float] = None
        self.c_gem: Optional[float] = None
        self.tan_phi_kar: Optional[float] = None
        self.c_kar: Optional[float] = None
        self.tan_phi_d: Optional[float] = None
        self.c_d: Optional[float] = None

        # Figure
        self.figure = go.Figure()

    def get_cphi_data(self):
        """Deze functie filtert de dbase-dataframe op basis van type analyse, PV_NAAM en de gewenste effectieve stress.
        Daarnaast worden de kolomnamen aangepast zodat ze ongeacht het rekpercentage allemaal dezelfde kolomnaam hebben.
        """
        if self.analysis_type in ['TXT_CPhi', 'TXT_SH']:
            self.cphi_analyses_data_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
        elif self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
            self.cphi_analyses_data_df = self.dbase_df[self.dbase_df['ALG__DSS']]

        self.cphi_analyses_data_df = self.cphi_analyses_data_df[self.cphi_analyses_data_df['PV_NAAM'].isin(self.investigation_groups)]
        self.cphi_analyses_data_df = self.cphi_analyses_data_df[TEXTUAL_NAMES.get(self.effective_stress, [])]
        self.cphi_analyses_data_df.columns = NEW_COLUMN_NAMES

    def apply_settings(self, alpha: Optional[Alpha],
                       material_factor_cohesion: Optional[float],
                       material_factor_tan_phi: Optional[float]):
        """Met deze functie kan je de alpha en materiaalfactoren instellen."""
        self.alpha = alpha
        self.material_cohesie = material_factor_cohesion
        self.material_tan_phi = material_factor_tan_phi

    def expand_analysis_df(self):
        """Deze functie berekend alle benodigde parameters per monster voor de analyse."""
        calculate_s_tt(self)
        calculate_s_ty(self)
        calculate_kappa_2(self)
        calculate_s(self)
        calculate_5pr_ondergrens(self)
        calculate_5pr_bovengrens(self)
        calculate_s_tt_ondergrens(self)
        calculate_s_ty_ondergrens(self)
        calculate_kappa_2_ondergrens(self)

    def eerste_benadering(self):
        """Deze functie maakt een eerste benadering voor de cohesie en phi."""
        calc_phi_gem(self)
        self.cohesie_gem_handmatig = calc_cohesie_gem(self)
        self.phi_kar_handmatig = calc_phi_kar(self)
        self.cohesie_kar_handmatig = calc_cohesie_kar(self)

    def expand_analysis_df_corrected(self):
        """Voegt aanvullende kolommen toe aan het dataframe."""
        calculate_correctie_t(self)
        kappa_2_2pr_cor(self)
        calculate_5pr_ondergrens_correctie_c(self)
        calculate_5pr_bovengrens_correctie_c(self)
        calculate_s_ty_ondergrens_correctie_c(self)
        calculate_kappa_2_ondergrens_correctie_c(self)

    def result_values(self):
        """Berekend de resultaten van de analyse."""
        self.tan_phi_gem = calc_tan_phi_gem(self)
        self.c_gem = calc_c_gem(self)
        self.tan_phi_kar = calc_tan_phi_kar(self)
        self.c_kar = calc_c_kar(self)
        self.tan_phi_d = calc_tan_phi_d(self)
        self.c_d = calc_c_d(self)

    def _run(self):
        """Deze functie zorgt ervoor dat zodra er iets veranderd in de bron-data alles opnieuw wordt berekend."""
        self.get_cphi_data()
        self.expand_analysis_df()
        self.eerste_benadering()
        self.expand_analysis_df_corrected()
        self.result_values()

    def set_figure(self):
        add_proefresultaten(self)
        add_5pr_bovengrens(self)
        add_fysische_realiseerbare_ondergrens(self)
        add_gemiddelde(self)
        set_layout(self)

    def show_figure(self):
        self._run()
        self.figure = go.Figure()
        self.set_figure()
        # self.figure.show()

    def factsheet(self):
        self._run()
        # print('df =', self.cphi_analyses_data_df)
        # print('Results')
        # print('tan(phi)_gem = ', self.tan_phi_gem)
        # print('c_gem = ', self.c_gem)
        # print('tan(phi)_kar)', self.tan_phi_kar)
        # print('c_kar', self.c_kar)
        # print('tan(phi)_d', self.tan_phi_d)
        # print('c_d', self.c_d)


# voorbeeld uitvoer
# my_analysis = CPhiAnalyse(dbase=..., investigation_groups=['klei_licht'], effective_stress='2%')
# my_analysis.figure().show()
# dbase.change_group.minus(16)
# my_analysis.figure().show()
# my_analysis.alpha = 0.75
# my_analysis.figure().show()

