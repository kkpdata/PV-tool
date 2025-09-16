from operator import index
from typing import Optional, List, Literal
from datetime import datetime
from pandas import DataFrame, ExcelWriter, concat, read_excel, isna

from pv_tool.cphi_analysis.globals import (TEXTUAL_NAMES, ALL_TEXTUAL_NAMES,
                                           NEW_COLUMN_NAMES, TEXTUAL_NAMES_DSS, ALL_TEXTUAL_NAMES_DSS)

from pv_tool.imports.import_data import Dbase
import plotly.graph_objects as go
from pv_tool.cphi_analysis.expand_analysis_df import (calculate_tan_a, calculate_ln_tan_a, calculate_s_tt,
                                                      calculate_s_ty, calculate_kappa_2, calculate_s,
                                                      calculate_5pr_ondergrens, calculate_5pr_bovengrens,
                                                 calculate_s_tt_ondergrens, calculate_s_ty_ondergrens,
                                                 calculate_kappa_2_ondergrens, calculate_correctie_t, kappa_2_2pr_cor,
                                                 calculate_5pr_ondergrens_correctie_c,
                                                 calculate_5pr_bovengrens_correctie_c,
                                                 calculate_s_ty_ondergrens_correctie_c,
                                                 calculate_kappa_2_ondergrens_correctie_c)
from pv_tool.cphi_analysis.visualization import (add_proefresultaten, add_extra_proefresultaten, add_5pr_bovengrens,
                                            add_5pr_ondergrens, add_fysische_realiseerbare_ondergrens, add_gemiddelde,
                                            set_layout, add_gemiddelde_sh, add_raaklijn_kar_boven,
                                                 add_raaklijn_kar_onder)
from pv_tool.cphi_analysis.calc_parameters import (calc_watergehalte_gem, calc_watergehalte_sd, calc_vgwnat_gem,
                                                   calc_vgwnat_sd, calc_a2_phi_gem,  calc_a2_kar, calc_phi_d,
                                                   helling_gecorrigeerd, calc_a1_c_gem, calc_tan_phi_gem, calc_phi_kar,
                                                   calc_cohesie_kar, calc_phi_gem, calc_c_gem, calc_tan_phi_kar,
                                              calc_c_kar, calc_tan_phi_d, calc_c_d, calc_st_dev_phi, calc_st_dev_c,
                                                calc_a2_phi_gem_sh, calc_a2_phi_kar_boven_sh, calc_a2_phi_kar_onder_sh,
                                                   calc_tan_phi_kar_sh)
from openpyxl import load_workbook


from reportlab.lib import colors

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, LongTable, TableStyle, Paragraph, Spacer, Image

from openpyxl.worksheet.table import Table as XLTable, TableStyleInfo
from openpyxl.utils import get_column_letter


class CPhiAnalyse:
    """
    Klasse voor het uitvoeren van c-phi analyses op grondmonsters.

    Ondersteunt zowel triaxiaal (TXT) als direct simple shear (DSS) testen,
    en kan zowel reguliere c-phi als shansep (SH) analyses uitvoeren.
    """

    def __init__(self, dbase: Dbase,
                 analysis_type: Literal['TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH'],
                 investigation_groups: List,
                 effective_stress: Literal['2% rek', '5% rek', '10% rek', '15% rek', '20% rek',
                                            'pieksterkte', 'eindsterkte']):
        """
        Initialiseert een nieuwe c-phi analyse.

        Parameters
        ----------
        dbase : Dbase
            Database object met proefresultaten
        analysis_type : str
            Type analyse ('TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH')
        investigation_groups : List
            Lijst met te analyseren proefgroepen
        effective_stress : str
            Rekpercentage of sterkte criterium voor de analyse
        """

        # Validate effective_stress based on analysis_type
        if analysis_type in ['TXT_CPhi', 'TXT_SH'] and effective_stress in ['10% rek', '20% rek']:
            raise ValueError(
                f"De waardes '10% rek' and '20% rek' kunnen alleen gebruikt worden bij de DSS analyse. "
                f"De gekozen analyse is: '{analysis_type}', en de sterkte is: '{effective_stress}'"
            )

        # Data
        self.dbase_df = dbase.dbase_df
        self.analysis_type = analysis_type
        self.investigation_groups = investigation_groups
        self.effective_stress = effective_stress

        # Settings
        self.alpha: Optional[float] = 0.75
        self.material_cohesie: Optional[float] = 1.0
        self.material_tan_phi: Optional[float] = 1.0

        # Parameters
        self.eerste_benadering_a2_gem: Optional[float] = None  # phi_gem
        self.eerste_benadering_a2_kar: Optional[float] = None  # phi_kar
        self.eerste_benadering_a1_gem: Optional[float] = None  # cohesie_gem
        self.eerste_benadering_a1_kar: Optional[float] = None  # cohesie_kar

        self.helling_gecorrigeerd: Optional[float] = None
        self.cohesie_gem_handmatig: Optional[float] = None
        self.phi_kar_handmatig: Optional[float] = None
        self.cohesie_kar_handmatig: Optional[float] = None

        self.calc_watergehalte_gem: Optional[float] = None
        self.calc_watergehalte_sd: Optional[float] = None
        self.calc_vgwnat_gem: Optional[float] = None
        self.calc_vgwnat_sd: Optional[float] = None

        # Placeholder
        self.cphi_analyses_data_df: Optional[DataFrame] = None
        self.total_cphi_analyses_data_df: Optional[DataFrame] = None

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

        self.gem_a1: Optional[float] = None
        self.gem_a2: Optional[float] = None

        self.kar_a1: Optional[float] = None
        self.kar_a2: Optional[float] = None

        self.a2_phi_kar_onder: Optional[float] = None
        self.a2_phi_kar_boven: Optional[float] = None

        # Figure
        self.figure = go.Figure()
        self.show_title: Optional[bool] = True

    def get_cphi_data(self):
        """
        Filtert de database op basis van analysetype en proefgroepen.

        Selecteert de juiste data voor de analyse op basis van het type test (TXT/DSS),
        de proefgroepen en het gewenste rekpercentage. Berekent tevens gemiddelde
        eigenschappen zoals watergehalte.
        """
        if self.analysis_type in ['TXT_CPhi', 'TXT_SH']:
            self.cphi_analyses_data_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
            self.cphi_analyses_data_df = self.cphi_analyses_data_df[self.cphi_analyses_data_df['PV_NAAM'].isin(
                    self.investigation_groups)]  # TODO should have selectie veranderen in de dbase en daarmee verder
            self.calc_watergehalte_gem = calc_watergehalte_gem(self)
            self.calc_watergehalte_sd = calc_watergehalte_sd(self)
            self.calc_vgwnat_gem = calc_vgwnat_gem(self)
            self.calc_vgwnat_sd = calc_vgwnat_sd(self)
            self.total_cphi_analyses_data_df = self.cphi_analyses_data_df
            self.cphi_analyses_data_df = self.cphi_analyses_data_df[TEXTUAL_NAMES.get(self.effective_stress, [])]

        elif self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
            self.cphi_analyses_data_df = self.dbase_df[self.dbase_df['ALG__DSS']]
            self.cphi_analyses_data_df = self.cphi_analyses_data_df[self.cphi_analyses_data_df['PV_NAAM'].isin(
                    self.investigation_groups)]  # TODO should have selectie veranderen in de dbase en daarmee verder
            self.calc_watergehalte_gem = calc_watergehalte_gem(self)
            self.calc_watergehalte_sd = calc_watergehalte_sd(self)
            self.calc_vgwnat_gem = calc_vgwnat_gem(self)
            self.calc_vgwnat_sd = calc_vgwnat_sd(self)
            self.total_cphi_analyses_data_df = self.cphi_analyses_data_df
            self.cphi_analyses_data_df = self.cphi_analyses_data_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])]

        self.cphi_analyses_data_df.columns = NEW_COLUMN_NAMES

    def apply_settings(self, alpha: Optional[float] = None,
                       material_factor_cohesion: Optional[float] = None,
                       material_factor_tan_phi: Optional[float] = None):
        """
        Past analyse-instellingen aan.

        Parameters
        ----------
        alpha : float, optioneel
            Alpha-waarde voor de analyse
        material_factor_cohesion : float, optioneel
            Materiaalfactor voor cohesie
        material_factor_tan_phi : float, optioneel
            Materiaalfactor voor tan(phi)
        """
        self.alpha = alpha if alpha is not None else self.alpha
        self.material_cohesie = material_factor_cohesion if material_factor_cohesion is not None \
            else self.material_cohesie
        self.material_tan_phi = material_factor_tan_phi if material_factor_tan_phi is not None \
            else self.material_tan_phi

    def apply_parameters(self, cohesie_gem: Optional[float] = None,
                         phi_kar: Optional[float] = None,
                         cohesie_kar: Optional[float] = None):
        """
        Past handmatige parameters aan en herberekent de analyse.

        Parameters
        ----------
        cohesie_gem : float, optioneel
            Gemiddelde cohesie
        phi_kar : float, optioneel
            Karakteristieke phi-waarde
        cohesie_kar : float, optioneel
            Karakteristieke cohesie
        """
        if cohesie_gem is not None:
            self.cohesie_gem_handmatig = cohesie_gem
        if phi_kar is not None:
            self.phi_kar_handmatig = phi_kar
        if cohesie_kar is not None:
            self.cohesie_kar_handmatig = cohesie_kar
        if self.analysis_type in ['TXT_SH', 'DSS_SH']:
            self._run_sh()
        else:
            self._run()

    def plot_spanningspaden(self):
        """
        Plot de spanningspaden voor alle beschikbare effective stress waarden
        binnen de geselecteerde investigation groups.

        Dit helpt bij het visualiseren van de spanningsveranderingen
        tijdens de proeven. Voor elk monster (uit de index van de dataframes)
        wordt een apart spanningspad gemaakt met alle beschikbare spanningsstappen.
        """
        if self.analysis_type in ['TXT_CPhi', 'TXT_SH']:
            relevant_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
            relevant_df = relevant_df[relevant_df['PV_NAAM'].isin(self.investigation_groups)]
            effective_stress_options = ['consolidatie', '2% rek', '5% rek', '15% rek', 'pieksterkte', 'eindsterkte']
        elif self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
            relevant_df = self.dbase_df[self.dbase_df['ALG__DSS']]
            relevant_df = relevant_df[relevant_df['PV_NAAM'].isin(self.investigation_groups)]
            effective_stress_options = ['consolidatie', '2% rek', '5% rek', '10% rek', '15% rek', '20% rek', 'pieksterkte', 'eindsterkte']
            relevant_df['DSS_T_CONSOLIDATIE'] = [0]*len(relevant_df)
        else:
            raise ValueError("Ongeldig analysetype. Gebruik 'TXT_CPhi', 'TXT_SH', 'DSS_CPhi' of 'DSS_SH'.")

        # Eerst verzamelen we alle data per spanningsstap
        all_data = {}
        for stress in effective_stress_options:
            columns = ALL_TEXTUAL_NAMES.get(stress, []) if self.analysis_type in ['TXT_CPhi', 'TXT_SH'] else ALL_TEXTUAL_NAMES_DSS.get(stress, [])
            if len(columns) > 0:
                data = relevant_df[columns].copy()
                if not data.empty and not data.isna().all().all():
                    data.columns = NEW_COLUMN_NAMES
                    all_data[stress] = data

        # Nu herstructureren we de data per monster (uit de index)
        sample_stress_paths = {}

        # Verzamel alle unieke monster namen uit de indices van alle dataframes
        all_samples = set()
        for df in all_data.values():
            all_samples.update(df.index)

        # Voor elk monster, verzamel alle spanningsstappen
        for sample_name in all_samples:
            stress_data = {'S\'': [], 'T': [], 'stress_state': []}
            for stress, df in all_data.items():
                if sample_name in df.index:
                    sample_data = df.loc[sample_name]
                    if not (isna(sample_data['S\'']) or isna(sample_data['T'])):
                        stress_data['S\''].append(sample_data['S\''])
                        stress_data['T'].append(sample_data['T'])
                        stress_data['stress_state'].append(stress)

            if stress_data['S\'']:  # Als er data is voor dit monster
                stress_df = DataFrame(stress_data)

                if self.analysis_type in ['TXT_CPhi', 'TXT_SH']:
                    rek_bij_t_piek = self.total_cphi_analyses_data_df.loc[sample_name, 'TXT_SS_REK_BIJ_T_PIEK']
                    rek_bij_t_eind = self.total_cphi_analyses_data_df.loc[sample_name, 'TXT_SS_REK_BIJ_T_EIND']
                    if not isna(rek_bij_t_piek) and 'pieksterkte' in stress_df['stress_state'].values:
                        # Verplaats de rij met 'pieksterkte' naar de juiste positie
                        piek_row = stress_df[stress_df['stress_state'] == 'pieksterkte']
                        stress_df = stress_df[stress_df['stress_state'] != 'pieksterkte']
                        if rek_bij_t_piek < 2:
                            insert_index = 1
                        elif rek_bij_t_piek <5:
                            insert_index = 2
                        elif rek_bij_t_piek <15:
                            insert_index = 3
                        elif not isna(rek_bij_t_eind) and rek_bij_t_eind > rek_bij_t_piek:
                            insert_index = 4
                        else:
                            insert_index = len(stress_df)
                        stress_df = concat([stress_df.iloc[:insert_index], piek_row, stress_df.iloc[insert_index:]]).reset_index(drop=True)
                elif self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
                    rek_bij_t_max = self.total_cphi_analyses_data_df.loc[sample_name, 'DSS_REK_BIJ_T_MAX']
                    rek_bij_t_eind = self.total_cphi_analyses_data_df.loc[sample_name, 'DSS_REK_BIJ_T_EIND']
                    if not isna(rek_bij_t_max) and 'pieksterkte' in stress_df['stress_state'].values:
                        # Verplaats de rij met 'pieksterkte' naar de juiste positie
                        piek_row = stress_df[stress_df['stress_state'] == 'pieksterkte']
                        stress_df = stress_df[stress_df['stress_state'] != 'pieksterkte']
                        if rek_bij_t_max < 2:
                            insert_index = 1
                        elif rek_bij_t_max <5:
                            insert_index = 2
                        elif rek_bij_t_max <10:
                            insert_index = 3
                        elif rek_bij_t_max <15:
                            insert_index = 4
                        elif rek_bij_t_max <20:
                            insert_index = 5
                        elif not isna(rek_bij_t_eind) and rek_bij_t_eind > rek_bij_t_max:
                            insert_index = 6
                        else:
                            insert_index = len(stress_df)
                        stress_df = concat([stress_df.iloc[:insert_index], piek_row, stress_df.iloc[insert_index:]]).reset_index(drop=True)

                sample_stress_paths[sample_name] = stress_df


        
        # Plot de spanningspaden
        if sample_stress_paths:
            from pv_tool.cphi_analysis.visualization import add_stress_paths
            add_stress_paths(self, sample_stress_paths)
        else:
            raise ValueError("Geen geldige data gevonden voor de spanningspaden.")

    def get_previous_results(self, path: str):
        """
        Zoekt naar eerdere analyseresultaten in een Excel-bestand.

        Parameters
        ----------
        path : str
            Pad naar de map waar het Excel-bestand staat

        Returns
        -------
        DataFrame of None
            DataFrame met eerdere resultaten als deze gevonden zijn, anders None
        """
        file_name = 'Template_PVtool5_0.xlsx'
        file_path = f"{path}/{file_name}"

        try:
            with open(file_path, 'r'):
                pass
        except FileNotFoundError:
            raise FileNotFoundError("Er is geen dbase aanwezig onder de naam Template_PVtool5_0.xlsx")

        try:
            results_df = read_excel(file_path, sheet_name='Resultaten')
        except ValueError:
            print("Er is geen tabblad 'Resultaten' aanwezig in het Excel-bestand.")
            return None

        filtered_df = results_df[
            (results_df['PV_RESULTAAT_ID'].str.contains(self.investigation_groups[0])) &
            (results_df['PV_RESULTAAT_ID'].str.contains(self.effective_stress)) &
            (results_df['PV_RESULTAAT_ID'].str.contains(self.analysis_type))
        ]

        if filtered_df.empty:
            print("Er zijn geen eerdere resultaten gevonden voor de opgegeven parameters.")
            return None

        latest_entry = filtered_df.loc[filtered_df['PV_RESULTAAT_ID'].idxmax()]

        return latest_entry

    def expand_analysis_df(self):
        """
        Berekent afgeleide parameters voor de c-phi analyse.

        Voegt kolommen toe aan het dataframe met berekende waarden voor
        s_tt, s_ty, kappa_2 en verschillende onder- en bovengrenzen.
        """
        calculate_s_tt(self)
        calculate_s_ty(self)
        calculate_kappa_2(self)
        calculate_s(self)
        calculate_5pr_ondergrens(self)
        calculate_5pr_bovengrens(self)
        calculate_s_tt_ondergrens(self)
        calculate_s_ty_ondergrens(self)
        calculate_kappa_2_ondergrens(self)

    def expand_analysis_df_sh(self):
        """
        Berekent afgeleide parameters voor de shansep analyse.

        Voegt kolommen toe aan het dataframe met berekende waarden voor
        tan(alpha) en ln(tan(alpha)).
        """
        calculate_tan_a(self)
        calculate_ln_tan_a(self)

    def eerste_benadering(self):
        """
        Maakt een eerste schatting van de gemiddelde sterkteparameters cohesie (a1) en phi (a2).
        """
        # self.eerste_benadering_a1_gem = calc_cohesie_gem(self)
        self.eerste_benadering_a1_gem = calc_a1_c_gem(self)
        self.eerste_benadering_a2_gem = calc_a2_phi_gem(self)

    def eerste_benadering_deel2(self):
        """
        Maakt een eerste schatting van de karakteristieke sterkteparameters cohesie (a1) en phi (a2).
        """
        self.eerste_benadering_a2_kar = calc_a2_kar(self)
        self.eerste_benadering_a1_kar = calc_cohesie_kar(self)

    def expand_analysis_df_corrected(self):
        """
        Voegt gecorrigeerde parameters toe aan de analyse: gecorrigeerde waarden voor
        onder- en bovengrenzen en kappa_2.
        """
        calculate_correctie_t(self)
        kappa_2_2pr_cor(self)
        calculate_5pr_ondergrens_correctie_c(self)
        calculate_5pr_bovengrens_correctie_c(self)
        calculate_s_ty_ondergrens_correctie_c(self)
        calculate_kappa_2_ondergrens_correctie_c(self)

    def result_values(self):  # TODO dit gaat nog steeds niet goed want de handmatige waarden moeten de rest overschrijven als ze er zijn. ligt dit aan calc of moeten we dat hier definieren met if else
        """
        Berekent de definitieve resultaten van de c-phi analyse: gemiddelde, karakteristieke en rekenwaarden voor
        cohesie en phi, inclusief standaarddeviaties.
        """
        self.helling_gecorrigeerd = helling_gecorrigeerd(self)

        self.gem_a1 = calc_a1_c_gem(self)
        self.gem_a2 = calc_a2_phi_gem(self)

        self.kar_a1 = calc_cohesie_kar(self)
        self.kar_a2 = self.phi_kar_handmatig if self.phi_kar_handmatig is not None else self.eerste_benadering_a2_kar

        self.phi_gem = calc_phi_gem(self)
        self.tan_phi_gem = calc_tan_phi_gem(self)
        self.c_gem = calc_c_gem(self)

        self.tan_phi_kar = calc_tan_phi_kar(self)
        self.phi_kar = calc_phi_kar(self)
        self.c_kar = calc_c_kar(self)

        self.phi_d = calc_phi_d(self)
        self.tan_phi_d = calc_tan_phi_d(self)
        self.c_d = calc_c_d(self)

        self.st_dev_phi = calc_st_dev_phi(self)
        self.st_dev_c = calc_st_dev_c(self)

    def result_values_sh(self):
        """
        Berekent de definitieve resultaten van de shansep analyse:
        gemiddelde, karakteristieke en rekenwaarden voor phi,
        inclusief standaarddeviatie.

        """
        self.gem_a2 = calc_a2_phi_gem_sh(self)
        self.a2_phi_kar_onder = calc_a2_phi_kar_onder_sh(self)
        self.a2_phi_kar_boven = calc_a2_phi_kar_boven_sh(self)
        self.kar_a2 = self.a2_phi_kar_onder

        self.tan_phi_gem = calc_tan_phi_gem(self)
        self.tan_phi_kar = calc_tan_phi_kar_sh(self)
        self.tan_phi_d = calc_tan_phi_d(self)

        self.phi_gem = calc_phi_gem(self)
        self.phi_kar = calc_phi_kar(self)
        self.phi_d = calc_phi_d(self)

        self.st_dev_phi = calc_st_dev_phi(self)

    def _run(self):
        """
        Voert de volledige c-phi analyse uit in de juiste volgorde:
        data ophalen, parameters berekenen en resultaten bepalen.
        """
        self.get_cphi_data()
        self.expand_analysis_df()
        self.eerste_benadering()
        self.expand_analysis_df_corrected()
        self.eerste_benadering_deel2()
        self.result_values()

    def _run_sh(self):
        """
        Voert de volledige shansep analyse uit in de juiste volgorde:
        data ophalen, parameters berekenen en resultaten bepalen.
        """
        self.get_cphi_data()
        self.expand_analysis_df_sh()
        self.result_values_sh()

    def set_figure(self, plot_extra_dataset: Optional[List] = None, plot_spanningspaden: bool = False):
        """
        Maakt een visualisatie van de analyseresultaten.

        Parameters
        ----------
        plot_extra_dataset : List, optioneel
            Extra dataset om in de plot weer te geven

        plot_spanningspaden : bool, optioneel
            Of de spanningspaden moeten worden weergegeven
        """
        if plot_spanningspaden:
            self.plot_spanningspaden()

        add_proefresultaten(self)
        if plot_extra_dataset is not None:
            add_extra_proefresultaten(self, plot_extra_dataset)

        if self.analysis_type in ['TXT_SH', 'DSS_SH']:
            add_gemiddelde_sh(self)
            add_raaklijn_kar_onder(self)
            add_raaklijn_kar_boven(self)
        else:
            add_5pr_bovengrens(self)
            add_5pr_ondergrens(self)
            add_fysische_realiseerbare_ondergrens(self)
            add_gemiddelde(self)

        set_layout(self)

    def show_figure(self, plot_extra_dataset: Optional[List] = None, plot_spanningspaden: bool = False):
        """
        Toont de visualisatie van de analyseresultaten.

        Parameters
        ----------
        plot_extra_dataset : List, optioneel
            Extra dataset om in de plot weer te geven

        plot_spanningspaden : bool, optioneel
            Of de spanningspaden moeten worden weergegeven
        """
        if self.analysis_type in ['TXT_SH', 'DSS_SH']:
            self._run_sh()
        else:
            self._run()
        self.figure = go.Figure()
        self.set_figure(plot_extra_dataset, plot_spanningspaden=plot_spanningspaden)
        self.figure.show()

    def print_short_results(self):
        """
        Genereert een samenvattend overzicht van de analyseresultaten.

        Returns
        -------
        DataFrame
            DataFrame met verwachtingswaarden, karakteristieke waarden,
            rekenwaarden en standaarddeviaties
        """
        if self.analysis_type in ['TXT_SH', 'DSS_SH']:
            self._run_sh()
            index = ['Verwachtingswaarde', 'Karakteristieke waarde', 'Rekenwaarde', 'Standaarddeviatie D-stability']
            columns = ['tan phi [-]', 'phi [graden]']
            analyse_output_df = DataFrame(index=index, columns=columns)
            analyse_output_df['tan phi [-]'] = [self.tan_phi_gem, self.tan_phi_kar , self.tan_phi_d, '[-]']
            analyse_output_df['phi [graden]'] = [self.phi_gem, self.phi_kar, self.phi_d, self.st_dev_phi]
        else:
            self._run()
            index = ['Verwachtingswaarde', 'Karakteristieke waarde', 'Rekenwaarde', 'Standaarddeviatie D-stability']
            columns = ['tan phi [-]', 'phi [graden]', 'cohesie [kPa]']
            analyse_output_df = DataFrame(index=index, columns=columns)
            analyse_output_df['tan phi [-]'] = [self.tan_phi_gem, self.tan_phi_kar, self.tan_phi_d, '[-]']
            analyse_output_df['phi [graden]'] = [self.phi_gem, self.phi_kar, self.phi_d, self.st_dev_phi]
            analyse_output_df['cohesie [kPa]'] = [self.c_gem, self.c_kar, self.c_d, self.st_dev_c]
        return analyse_output_df

    def add_results_to_dbase(self, path):
        """
        Voegt analyseresultaten toe aan de database export.

        Voegt de resultaten toe aan een tabblad 'Resultaten' in de Template_PVtool5_0.xlsx.
        Als het tabblad al bestaat wordt het aangevuld, anders wordt het aangemaakt.

        Parameters
        ----------
        path : str
            Map locatie waar het Excel-bestand staat of moet komen

        Returns
        -------
        DataFrame
            DataFrame met alle resultaten in het tabblad
        """
        file_name = 'Template_PVtool5_0.xlsx'
        file_path = f"{path}/{file_name}"

        try:
            with open(file_path, 'r'):
                pass
        except FileNotFoundError:
            raise FileNotFoundError("Er is geen dbase aanwezig onder de naam Template_PVtool5_0.xlsx")

        expected_columns = [
            'PV_RESULTAAT_ID', 'PVNAAM', 'PV_REK', 'PV_TYPE_PROEF', 'PV_ANALYSE',
            'PV_A1_COH_GEM [kPa]', 'PV_A2_TAN_PHI_GEM [-]', 'PV_A1_COH_KAR [kPa]', 'PV_A2_TAN_PHI_KAR [-]',
            'PV_PARTPHI [-]', 'PV_PARTCOH [-]', 'PV_TYPEVERZAMELING', 'PV_COH_GEM [kPa]', 'PV_PHI_GEM [graden]',
            'PV_COH_KAR [kPa]', 'PV_PHI_KAR [graden]', 'PV_COH_SD_DSTAB [-]', 'PV_PHI_SD_DSTAB [-]',
            'PV_VGWNAT_GEM [kN/m3]', 'PV_VGWNAT_SD [kN/m3]', 'PV_WATERGEHALTE_GEM', 'PV_WATERGEHALTE_SD', 'Timestamp'
        ]

        new_row = {
            'PVNAAM': self.investigation_groups[0],
            'PV_REK': self.effective_stress,
            'PV_TYPE_PROEF': self.analysis_type.split('_')[0],
            'PV_ANALYSE': self.analysis_type.split('_')[1],
            'PV_RESULTAAT_ID': f"{self.investigation_groups[0]}_{self.effective_stress}_{self.analysis_type.split('_')[0]}_{self.analysis_type.split('_')[1]}",
            'PV_TYPEVERZAMELING': self.alpha,
            'PV_A1_COH_GEM [kPa]': round(self.gem_a1, 3) if self.gem_a1 is not None else None,
            'PV_A2_TAN_PHI_GEM [-]': round(self.gem_a2, 3) if self.gem_a2 is not None else None,
            'PV_A1_COH_KAR [kPa]': round(self.kar_a1, 3) if self.kar_a1 is not None else None,
            'PV_A2_TAN_PHI_KAR [-]': round(self.kar_a2, 3) if self.kar_a2 is not None else None,
            'PV_COH_GEM [kPa]': (round(self.c_gem, 3) if self.c_gem is not None and self.c_gem >= 0
                                else "[-]" if self.c_gem is None
                                else f"{round(self.c_gem, 3)} (kan niet - aanpassen!)"
                                ),
            'PV_PHI_GEM [graden]': round(self.phi_gem, 3) if self.phi_gem is not None else None,
            'PV_COH_KAR [kPa]': (round(self.c_kar, 3) if self.c_kar is not None and self.c_kar >= 0
                                else "[-]" if self.c_kar is None
                                else f"{round(self.c_kar, 3)} (kan niet - aanpassen!)"
                                ),
            'PV_PHI_KAR [graden]': round(self.phi_kar, 3) if self.phi_kar is not None else None,
            'PV_COH_SD_DSTAB [-]': (round(self.st_dev_c, 3) if self.c_gem is not None and self.c_kar is not None
                                    and self.c_gem >= 0 and self.c_kar >= 0
                                    else "[-]" if self.c_gem is None or self.c_kar is None
                                    else "[-] (c < 0)"),
            'PV_PHI_SD_DSTAB [-]': round(self.st_dev_phi, 3) if self.st_dev_phi is not None else None,
            'PV_PARTPHI [-]': self.material_tan_phi,
            'PV_PARTCOH [-]': self.material_cohesie,
            'PV_VGWNAT_GEM [kN/m3]': round(self.calc_vgwnat_gem, 3) if self.calc_vgwnat_gem is not None else None,
            'PV_VGWNAT_SD [kN/m3]': round(self.calc_vgwnat_sd, 3) if self.calc_vgwnat_sd is not None else None,
            'PV_WATERGEHALTE_GEM': round(self.calc_watergehalte_gem, 3) if self.calc_watergehalte_gem is not None else None,
            'PV_WATERGEHALTE_SD': round(self.calc_watergehalte_sd, 3) if self.calc_watergehalte_sd is not None else None,
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        workbook = load_workbook(file_path)

        if 'Resultaten' in workbook.sheetnames:
            print('Tabblad resultaten in dbase excel bestaat al en wordt aangevuld')
            df_existing = read_excel(file_path, sheet_name='Resultaten')
            df_updated = concat([df_existing, DataFrame([new_row])], ignore_index=True)
        else:
            print('Tabblad resultaten in dbase excel bestaat nog niet en wordt aangemaakt')
            df_updated = DataFrame([new_row], columns=expected_columns)

        # Write data to Excel
        with ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_updated.to_excel(writer, sheet_name='Resultaten', index=False)

        return df_updated

    @staticmethod
    def format_excel_sheet(file_path: str, sheet_name: str, num_columns: int, num_rows: int, table_name: str = None):
        """
        Formatteert een Excel werkblad als een tabel met filters en aangepaste kolombreedtes.

        Parameters
        ----------
        file_path : str
            Het volledige pad naar het Excel bestand
        sheet_name : str
            Naam van het werkblad dat geformatteerd moet worden
        num_columns : int
            Aantal kolommen in de tabel
        num_rows : int
            Aantal rijen in de tabel (exclusief de header)
        table_name : str, optioneel
            Naam voor de Excel tabel. Als None wordt opgegeven, wordt sheet_name + "Table" gebruikt.
        """

        workbook = load_workbook(file_path)
        worksheet = workbook[sheet_name]

        # Auto-adjust column widths based on content
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            adjusted_width = max_length + 2
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # Define table range
        table_range = f"A1:{get_column_letter(num_columns)}{num_rows + 1}"

        # Create table with filters
        if table_name is None:
            table_name = f"{sheet_name}Table"

        # Remove spaces and special characters from table name
        table_name = "".join(c for c in table_name if c.isalnum())

        table = XLTable(displayName=table_name, ref=table_range)

        # Add a default style
        style = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False
        )
        table.tableStyleInfo = style

        # Remove existing table if it exists
        for existing_table in worksheet.tables.values():
            if existing_table.name == table_name:
                del worksheet.tables[existing_table.name]
                break

        # Add the table to the worksheet
        worksheet.add_table(table)

        workbook.save(file_path)

    def save_total_to_excel(self, path):
        """
        Exporteert alle analysegegevens naar Excel.

        Slaat de volledige dataset met alle berekende kolommen op in een Excel bestand.
        De bestandsnaam wordt automatisch gegenereerd op basis van de analyse-instellingen.

        Parameters
        ----------
        path : str
            Map locatie waar het Excel-bestand moet worden opgeslagen
        """
        # pas de effective stress naam aan zodat het weggeschreven kan worden in de bestandsnaam
        effective_stress = str(self.effective_stress).replace('%', 'procent_')
        effective_stress = str(effective_stress).replace(' ', '')

        # exporteer onder de juiste naam
        file_name = f"c_phi_export_test_{self.investigation_groups[0]}_{self.analysis_type}_{effective_stress}.xlsx"
        file_path = f"{path}/{file_name}"

        # Hernoem de kolommen voor een ander analyse type
        if self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
            self.cphi_analyses_data_df = self.cphi_analyses_data_df.rename(columns={'S\'': '\u03C3 \'', 'T': '\u03C4'})

        # schrijf het totaal weg
        df_totaal = self.cphi_analyses_data_df
        with ExcelWriter(file_path, engine='openpyxl') as writer:
            df_totaal.to_excel(writer)

    @staticmethod
    def _df_to_table_with_index(df, index_name='Index'):
        """
        Zet een DataFrame om naar een lijst voor gebruik in een PDF tabel. Gebruikt in save_to_pdf.

        Parameters
        ----------
        df : DataFrame
            De DataFrame die moet worden omgezet
        index_name : str, optioneel
            Naam voor de index kolom (default='Index')

        Returns
        -------
        list
            Lijst met header en data rijen voor een PDF tabel
        """
        header = [df.index.name or index_name] + df.columns.tolist()
        data = [[idx] + row.tolist() for idx, row in df.iterrows()]
        return [header] + data

    def _create_input_table(self) -> Table:
        """
        Maakt een tabel met de invoerselectie informatie. Gebruikt in save_to_pdf.

        Returns
        -------
        Table
            ReportLab tabel object met de invoerselectie informatie
        """
        columns_base = [
            'PV_NAAM', 'BORING_POSITIE', 'MONSTER_NIVEAU_NAP_VANAF', 'MONSTER_NIVEAU_NAP_TOT'
        ]
        if self.analysis_type in ['TXT_CPhi', 'TXT_SH']:
            columns_extra = ['TXT_SS_VOLUMEGEWICHT_NAT', 'TXT_SS_VOLUMEGEWICHT_DRG', 'TXT_SS_WATERGEHALTE_VOOR']
        else:
            columns_extra = ['DSS_VOLUMEGEWICHT_NAT', 'DSS_VOLUMEGEWICHT_DRG', 'DSS_WATERGEHALTE_VOOR']

        columns_data = self.cphi_analyses_data_df.iloc[:, 1:3].copy()
        table1_cols = columns_base + columns_extra
        table1_df = self.total_cphi_analyses_data_df[table1_cols].copy()
        table1_df.columns = ['Groep', 'Positie', 'NAP Vanaf [m]', 'NAP Tot [m]', 'VGW nat', 'VGW droog', 'Watergehalte voor']
        table1_df = concat([table1_df, columns_data], axis=1)
        table1_df = table1_df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) else x)

        t1_data = self._df_to_table_with_index(table1_df, index_name="alg_boring_monsternummer_id")
        t1 = LongTable(t1_data, repeatRows=1, hAlign='LEFT')
        t1.setStyle(TableStyle([

            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        return t1

    def _create_initial_values_table(self) -> Table:
        """
        Maakt een tabel met de initiële waarden van de analyse. Gebruikt in save_to_pdf.

        Returns
        -------
        Table
            ReportLab tabel object met de initiële waarden
        """
        # name_gem_a1 = 'a1 gem = snijpunt y-as (cohesie gemiddeld)' if self.cohesie_gem_handmatig is None else 'a1 gem = cohesie gemiddeld (handmatig)'
        # name_gem_a2 = 'a2 gem = tan(phi) gemiddeld'
        # name_kar_a1 = 'a1 kar = snijpunt y-as (cohesie karakteristiek)' if self.cohesie_kar_handmatig is None else 'a1 kar = cohesie karakteristiek (handmatig)'
        # name_kar_a2 = 'a2 kar = tan(phi) karakteristiek' if self.phi_kar_handmatig is None else 'a2 kar = tan(phi) karakteristiek (handmatig)'
        name_phi_kar_onder = 'a2 kar onder = tan(phi) karakteristiek ondergrens'
        name_phi_kar_boven = 'a2 kar boven = tan(phi) karakteristiek bovengrens'

        initial_values = []

        if self.cohesie_gem_handmatig is not None: initial_values.append(['a1 gem = cohesie gemiddeld (handmatig)', round(self.cohesie_gem_handmatig,3)])
        elif self.gem_a1 is not None: initial_values.append(['a1 gem = snijpunt y-as (cohesie gemiddeld)', round(self.gem_a1,3)])

        if self.gem_a2 is not None: initial_values.append(['a2 gem = tan(phi) gemiddeld', round(self.gem_a2,3)])

        if self.cohesie_kar_handmatig is not None: initial_values.append(['a1 kar = cohesie karakteristiek (handmatig)', round(self.cohesie_kar_handmatig,3)])
        elif self.kar_a1 is not None: initial_values.append(['a1 kar = snijpunt y-as (cohesie karakteristiek)' , round(self.kar_a1,3)])

        if self.phi_kar_handmatig is not None: initial_values.append(['a2 kar = tan(phi) karakteristiek (handmatig)', round(self.phi_kar_handmatig,3)])
        elif self.kar_a2 is not None: initial_values.append(['a2 kar = tan(phi) karakteristiek', round(self.kar_a2,3)])

        if hasattr(self, 'a2_phi_kar_onder') and self.a2_phi_kar_onder is not None:
            initial_values.append([name_phi_kar_onder, round(self.a2_phi_kar_onder,3)])
        if hasattr(self, 'a2_phi_kar_boven') and self.a2_phi_kar_boven is not None:
            initial_values.append([name_phi_kar_boven, round(self.a2_phi_kar_boven,3)])


        initial_values.append(['Type verzameling: lokaal = 1.0; regionaal = 0.75', self.alpha])
        initial_values.append(['Partiële materiaalfactor cohesie [-]', self.material_cohesie])
        initial_values.append(['Partiële materiaalfactor tan phi [-]', self.material_tan_phi])

        t3 = Table([['Parameter', 'Waarde']] + initial_values, hAlign='LEFT')
        t3.setStyle(TableStyle([
             ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        return t3

    def _create_results_table(self) -> Table:
        """
        Maakt een tabel met de eindresultaten van de analyse. Gebruikt in save_to_pdf.

        Returns
        -------
        Table
            ReportLab tabel object met de resultaten
        """
        output_table_df = self.print_short_results().copy()
        output_table_df.index.name = 'Parameter'
        output_table_df = output_table_df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) else x)
        output_table_data = self._df_to_table_with_index(output_table_df)
        output_table = Table(output_table_data, repeatRows=1, hAlign='LEFT')
        output_table.setStyle(TableStyle([
             ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        return output_table

    def _get_manual_values_paragraphs(self, styles) -> list:
        """
        Maakt een lijst van paragrafen met handmatig opgegeven waarden.

        Parameters
        ----------
        styles : dict
            ReportLab stylesheet met opmaakstijlen

        Returns
        -------
        list
            Lijst met ReportLab Paragraph objecten
        """
        paragraphs = []
        manual_texts = []
        if self.cohesie_gem_handmatig is not None:
            manual_texts.append(f"handmatig opgegeven: cohesie_gem_handmatig = {self.cohesie_gem_handmatig}")
        if self.phi_kar_handmatig is not None:
            manual_texts.append(f"handmatig opgegeven: phi_kar_handmatig = {self.phi_kar_handmatig}")
        if self.cohesie_kar_handmatig is not None:
            manual_texts.append(f"handmatig opgegeven: cohesie_kar_handmatig = {self.cohesie_kar_handmatig}")

        if manual_texts:
            paragraphs.append(Paragraph("Handmatig opgegeven waarden:", styles['Heading3']))
            for txt in manual_texts:
                paragraphs.append(Paragraph(txt, styles['Normal']))
        else:
            paragraphs.append(Paragraph("Geen handmatig opgegeven waarden, figuur gebaseerd op eerste inschatting", styles['Normal']))

        return paragraphs

    def save_to_pdf(self, path: str) -> str:
        """
        Slaat de analyseresultaten op in een PDF-document, inclusief figuren, datatabellen en numerieke resultaten.

        De PDF bevat:
        - Titel met analysedetails
        - Overzichtsfiguur van de analyse
        - Tabel met invoerselectie informatie
        - Tabel met initiële waarden
        - Eventueel handmatig opgegeven waarden
        - Tabel met eindresultaten

        Parameters
        ----------
        path : str
            Map locatie waar het PDF-bestand moet worden opgeslagen

        Returns
        -------
        str
            Het absolute bestandspad van het aangemaakte PDF-bestand
        """
        # Maak titel en bestandsnaam
        title = f'{self.analysis_type.split('_')[0]} {self.analysis_type.split('_')[1]} analyse met {self.effective_stress} op {self.investigation_groups[0]}'
        file_name = f"c_phi_pdf_export_{self.investigation_groups[0]}_{self.analysis_type}_{str(self.effective_stress).replace('%', 'procent_').replace(' ', '')}.pdf"
        file_path = f"{path}/{file_name}"

        # Maak en bewaar de figuur alleen als deze nog niet bestaat
        fig_path = f"{path}/temp_plot.png"
        if not hasattr(self, 'figure') or len(self.figure.data) == 0:
            self.show_title = False
            self.show_figure()

        self.show_title = True
        fig_width = 1280
        fig_height = 720
        self.figure.write_image(fig_path, width=fig_width, height=fig_height, scale=4, format="png")

        # Maak het PDF document
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Left', parent=styles['Normal'], alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='TitleLeft', parent=styles['Title'], alignment=TA_LEFT))
        story = []

        # Voeg titel toe
        story.append(Paragraph(title, styles['TitleLeft']))
        story.append(Spacer(width=1, height=12))

        # Voeg figuur toe met aangepaste grootte
        from PIL import Image as PILImage
        from reportlab.platypus import Image as RLImage

        fig_path = f"{path}/temp_plot.png"

        # Laad PNG en bepaal pixelafmetingen
        with PILImage.open(fig_path) as im:
            img_width_px, img_height_px = im.size

        # Stel gewenste breedte in punten (bijv. 95% van PDF breedte)
        max_width_pt = doc.width * 0.95

        # Bereken hoogte zodat verhouding gelijk blijft
        aspect = img_height_px / img_width_px
        img_width_pt = min(max_width_pt, doc.width)  # niet breder dan pagina
        img_height_pt = img_width_pt * aspect

        # Maak ReportLab Image aan
        img = RLImage(fig_path)
        img.drawWidth = img_width_pt
        img.drawHeight = img_height_pt
        img.hAlign = 'LEFT'

        story.append(img)
        story.append(Spacer(width=1, height=12))

        # Voeg initiële waarden toe
        story.append(Paragraph("Parameter bepaling fysisch realiseerbare ondergrens en gemiddelde waarden", styles['Heading2']))
        story.append(self._create_initial_values_table())
        story.append(Spacer(1, 12))

        # Voeg resultaten toe
        story.append(Paragraph("Resultaten", styles['Heading2']))
        story.append(self._create_results_table())
        story.append(Spacer(1, 12))

        # Voeg invoertabel toe
        story.append(Paragraph("Informatietabel invoerselectie", styles['Heading2']))
        story.append(self._create_input_table())
        story.append(Spacer(1, 12))

        # Bouw de PDF
        doc.build(story)

        print(f"PDF succesvol opgeslagen op: {file_path}")
        return file_path

