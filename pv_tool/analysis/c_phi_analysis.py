from typing import Optional, List, Literal
from pandas import DataFrame, ExcelWriter
from pv_tool.analysis.globals import (TEXTUAL_NAMES, NEW_COLUMN_NAMES)
from pv_tool.imports.import_data import Dbase
import math
from enum import Enum
import plotly.graph_objects as go
from pv_tool.analysis.expand_analysis_df import (calculate_s_tt, calculate_s_ty, calculate_kappa_2,
                                                 calculate_s, calculate_5pr_ondergrens, calculate_5pr_bovengrens,
                                                 calculate_s_tt_ondergrens, calculate_s_ty_ondergrens,
                                                 calculate_kappa_2_ondergrens, calculate_correctie_t, kappa_2_2pr_cor,
                                                 calculate_5pr_ondergrens_correctie_c,
                                                 calculate_5pr_bovengrens_correctie_c,
                                                 calculate_s_ty_ondergrens_correctie_c,
                                                 calculate_kappa_2_ondergrens_correctie_c)
from pv_tool.analysis.visualization import (add_proefresultaten, add_extra_proefresultaten, add_5pr_bovengrens,
                                            add_5pr_ondergrens, add_fysische_realiseerbare_ondergrens, add_gemiddelde,
                                            set_layout)
from pv_tool.analysis.calc_parameters import (calc_tan_phi_gem, calc_cohesie_gem, calc_phi_kar, calc_cohesie_kar,
                                              calc_phi_gem, calc_c_gem, calc_tan_phi_kar, calc_c_kar,
                                              calc_tan_phi_d, calc_c_d, calc_st_dev_phi, calc_st_dev_c)


class Alpha(Enum):  # TODO: dit gaat weg en wordt een input van de class cphianalyse
    LOCAL = 1.0
    REGIONAL = 0.75


class CPhiAnalyse:
    def __init__(self, dbase: Dbase,
                 analysis_type: Literal['TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH'],
                 investigation_groups: List,
                 effective_stress: Literal['2% rek', '5% rek', '15% rek', 'pieksterkte', 'eindsterkte']):

        # Data
        self.dbase_df = dbase.dbase_df
        self.analysis_type = analysis_type
        self.investigation_groups = investigation_groups
        self.effective_stress = effective_stress

        # Settings
        self.alpha: Alpha = Alpha.REGIONAL
        self.material_cohesie: Optional[float] = 1.0
        self.material_tan_phi: Optional[float] = 1.0

        # Parameters
        self.cohesie_gem_handmatig: Optional[float] = None
        self.phi_kar_handmatig: Optional[float] = None
        self.cohesie_kar_handmatig: Optional[float] = None
        self.cohesie_gem_set = False
        self.phi_kar_set = False
        self.cohesie_kar_set = False

        # Placeholder
        self.cphi_analyses_data_df: Optional[DataFrame] = None

        # Results
        self.tan_phi_gem: Optional[float] = None
        self.phi_gem: Optional[float] = None
        self.c_gem: Optional[float] = None
        self.tan_phi_kar: Optional[float] = None
        self.phi_kar: Optional[float] = None
        self.c_kar: Optional[float] = None
        self.tan_phi_d: Optional[float] = None
        self.phi_d: Optional[float] = None
        self.c_d: Optional[float] = None
        self.st_dev_phi: Optional[float] = None
        self.st_dev_c: Optional[float] = None

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
        self.cphi_analyses_data_df = self.cphi_analyses_data_df[self.cphi_analyses_data_df['PV_NAAM'].isin(
            self.investigation_groups)]
        self.cphi_analyses_data_df = self.cphi_analyses_data_df[TEXTUAL_NAMES.get(self.effective_stress, [])]
        self.cphi_analyses_data_df.columns = NEW_COLUMN_NAMES

    def apply_settings(self, alpha: Optional[Alpha] = None,
                       material_factor_cohesion: Optional[float] = None,
                       material_factor_tan_phi: Optional[float] = None):
        """Met deze functie kan je de alpha en materiaalfactoren opgeven."""
        self.alpha = alpha if alpha is not None else self.alpha
        self.material_cohesie = material_factor_cohesion if material_factor_cohesion is not None \
            else self.material_cohesie
        self.material_tan_phi = material_factor_tan_phi if material_factor_tan_phi is not None \
            else self.material_tan_phi

    def apply_parameters(self, cohesie_gem: Optional[float] = None,
                         phi_kar: Optional[float] = None,
                         cohesie_kar: Optional[float] = None):
        """Met deze functie kan je de parameters aanpassen."""
        if cohesie_gem is not None:
            self.cohesie_gem_handmatig = cohesie_gem
            self.cohesie_gem_set = True
        if phi_kar is not None:
            self.phi_kar_handmatig = phi_kar
            self.phi_kar_set = True
        if cohesie_kar is not None:
            self.cohesie_kar_handmatig = cohesie_kar
            self.cohesie_kar_set = True

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
        """Deze functie maakt een eerste benadering voor de gemiddelde cohesie en phi."""
        if not self.cohesie_gem_set:
            calc_tan_phi_gem(self)
            self.cohesie_gem_handmatig = calc_cohesie_gem(self)

    def eerste_benadering_deel2(self):
        """Deze functie maakt een eerste benadering voor de karakteristieke cohesie en phi"""
        if not self.phi_kar_set:
            self.phi_kar_handmatig = calc_phi_kar(self)
        if not self.cohesie_kar_set:
            self.cohesie_kar_handmatig = calc_cohesie_kar(self)

    def expand_analysis_df_corrected(self):
        """Voegt aanvullende kolommen toe aan het dataframe."""
        calculate_correctie_t(self)
        kappa_2_2pr_cor(self)
        calculate_5pr_ondergrens_correctie_c(self)
        calculate_5pr_bovengrens_correctie_c(self)
        calculate_s_ty_ondergrens_correctie_c(self)
        calculate_kappa_2_ondergrens_correctie_c(self)

    def result_values(self):  # TODO: voeg nog st.dev. toe
        """Berekend de resultaten van de analyse."""
        self.phi_gem = calc_phi_gem(self)
        self.tan_phi_gem = calc_tan_phi_gem(self)
        self.c_gem = calc_c_gem(self)
        self.tan_phi_kar = calc_tan_phi_kar(self)
        self.c_kar = calc_c_kar(self)
        self.tan_phi_d = calc_tan_phi_d(self)
        self.c_d = calc_c_d(self)
        self.st_dev_phi = calc_st_dev_phi(self)
        self.st_dev_c = calc_st_dev_c(self)

    def _run(self):
        """Deze functie zorgt ervoor dat zodra er iets veranderd in de bron-data alles opnieuw wordt berekend."""
        self.get_cphi_data()
        self.expand_analysis_df()
        self.eerste_benadering()
        self.expand_analysis_df_corrected()
        self.eerste_benadering_deel2()
        self.result_values()

    def set_figure(self, plot_extra_dataset: Optional[List] = None):
        """Deze functie maakt alle invoer voor het figuur."""
        if plot_extra_dataset is not None:
            add_extra_proefresultaten(self, plot_extra_dataset)
        add_proefresultaten(self)
        add_5pr_bovengrens(self)
        add_5pr_ondergrens(self)
        add_fysische_realiseerbare_ondergrens(self)
        add_gemiddelde(self)
        set_layout(self)

    def show_figure(self, plot_extra_dataset: Optional[List] = None):
        """Deze functie laat het figuur met alle resultaten zien."""
        self._run()
        self.figure = go.Figure()
        self.set_figure(plot_extra_dataset)
        self.figure.show()

    def show_results(self):
        """Deze functie presenteert alle resultaten."""
        self._run()
        self.phi_gem = 180/math.pi * math.atan(self.tan_phi_gem)  # TODO omdat tan phi is phi klopt dit niet - fix na variabelen aanpassen
        self.phi_kar = 180/math.pi * math.atan(self.tan_phi_kar)
        self.phi_d = 180/math.pi * math.atan(self.tan_phi_d)

        index = ['verwachtingswaarde', 'karakteristieke waarde', 'rekenwaarde', 'standaarddeviatie']
        columns = ['tan phi [-]', 'phi [graden]', 'cohesie [kPa]']
        analyse_output_df = DataFrame(index=index, columns=columns)
        analyse_output_df['tan phi [-]'] = [self.tan_phi_gem, self.tan_phi_kar, self.tan_phi_d, '[-]']
        analyse_output_df['phi [-]'] = [self.phi_gem, self.phi_kar, self.phi_d, self.st_dev_phi]
        analyse_output_df['cohesie [kPa]'] = [self.c_gem, self.c_kar, self.c_d, self.st_dev_c]
        print(analyse_output_df)
        return analyse_output_df

    def save_to_excel(self, path):
        sheet_name = f"{self.analysis_type}_{self.effective_stress}"
        df = self.show_results()

        with ExcelWriter(path, engine='openpyxl') as writer:
            if writer.book and sheet_name in writer.book.sheetnames:
                print(f"Sheet '{sheet_name}' already exists in the Excel file so Excel file is overwritten")
            df.to_excel(writer, sheet_name=sheet_name, index=False)
