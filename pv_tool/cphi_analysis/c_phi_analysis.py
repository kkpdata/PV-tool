from typing import Optional, List, Literal
from datetime import datetime
from pandas import DataFrame, ExcelWriter, concat, read_excel

from pv_tool.cphi_analysis.globals import (TEXTUAL_NAMES, NEW_COLUMN_NAMES, TEXTUAL_NAMES_DSS)

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


class CPhiAnalyse:
    def __init__(self, dbase: Dbase,
                 analysis_type: Literal['TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH'],
                 investigation_groups: List,
                 effective_stress: Literal['2% rek', '5% rek', '10% rek', '15% rek', '20% rek',
                                            'pieksterkte', 'eindsterkte']):

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

    def get_cphi_data(self):
        """Deze functie filtert de dbase-dataframe op basis van type analyse, PV_NAAM en de gewenste effectieve stress.
        Daarnaast worden de kolomnamen aangepast zodat ze ongeacht het rekpercentage allemaal dezelfde kolomnaam hebben.
        """
        if self.analysis_type in ['TXT_CPhi', 'TXT_SH']:
            self.cphi_analyses_data_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
            self.cphi_analyses_data_df = self.cphi_analyses_data_df[self.cphi_analyses_data_df['PV_NAAM'].isin(
                    self.investigation_groups)]  # TODO should have selectie veranderen in de dbase en daarmee verder
            self.calc_watergehalte_gem = calc_watergehalte_gem(self)
            self.calc_watergehalte_sd = calc_watergehalte_sd(self)
            self.calc_vgwnat_gem = calc_vgwnat_gem(self)
            self.calc_vgwnat_sd = calc_vgwnat_sd(self)
            self.cphi_analyses_data_df = self.cphi_analyses_data_df[TEXTUAL_NAMES.get(self.effective_stress, [])]

        elif self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
            self.cphi_analyses_data_df = self.dbase_df[self.dbase_df['ALG__DSS']]
            self.cphi_analyses_data_df = self.cphi_analyses_data_df[self.cphi_analyses_data_df['PV_NAAM'].isin(
                    self.investigation_groups)]  # TODO should have selectie veranderen in de dbase en daarmee verder
            self.calc_watergehalte_gem = calc_watergehalte_gem(self)
            self.calc_watergehalte_sd = calc_watergehalte_sd(self)
            self.calc_vgwnat_gem = calc_vgwnat_gem(self)
            self.calc_vgwnat_sd = calc_vgwnat_sd(self)
            self.cphi_analyses_data_df = self.cphi_analyses_data_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])]

        self.cphi_analyses_data_df.columns = NEW_COLUMN_NAMES


    def apply_settings(self, alpha: Optional[float] = None,
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
        if phi_kar is not None:
            self.phi_kar_handmatig = phi_kar
        if cohesie_kar is not None:
            self.cohesie_kar_handmatig = cohesie_kar
        self._run()

    def expand_analysis_df(self):
        """Deze functie berekent alle benodigde parameters per monster voor de analyse."""
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
        """Deze functie berekent alle benodigde parameters per monster voor de analyse."""
        calculate_tan_a(self)
        calculate_ln_tan_a(self)

    def eerste_benadering(self):
        """Deze functie maakt een eerste benadering voor de gemiddelde cohesie en phi."""
        # self.eerste_benadering_a1_gem = calc_cohesie_gem(self)
        self.eerste_benadering_a1_gem = calc_a1_c_gem(self)
        self.eerste_benadering_a2_gem = calc_a2_phi_gem(self)

    def eerste_benadering_deel2(self):
        """Deze functie maakt een eerste benadering voor de karakteristieke cohesie en phi"""
        self.eerste_benadering_a2_kar = calc_a2_kar(self)
        self.eerste_benadering_a1_kar = calc_cohesie_kar(self)


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
        self.gem_a2 = calc_a2_phi_gem_sh(self)
        self.a2_phi_kar_onder = calc_a2_phi_kar_onder_sh(self)
        self.a2_phi_kar_boven = calc_a2_phi_kar_boven_sh(self)
        self.kar_a2 = self.a2_phi_kar_onder

        self.tan_phi_gem = calc_tan_phi_gem(self)
        self.tan_phi_kar = calc_tan_phi_kar_sh(self)
        self.tan_phi_d = calc_tan_phi_d(self)

        self.phi_gem = calc_phi_gem(self)
        self.phi_kar = calc_phi_kar(self)

        self.st_dev_phi = calc_st_dev_phi(self)


    def _run(self):
        """Deze functie zorgt ervoor dat zodra er iets veranderd in de bron-data alles opnieuw wordt berekend."""
        self.get_cphi_data()
        self.expand_analysis_df()
        self.eerste_benadering()
        self.expand_analysis_df_corrected()
        self.eerste_benadering_deel2()
        self.result_values()

    def _run_sh(self):
        """Deze functie zorgt ervoor dat zodra er iets veranderd in de bron-data alles opnieuw wordt berekend."""
        self.get_cphi_data()
        self.expand_analysis_df_sh()
        self.result_values_sh()

    def set_figure(self, plot_extra_dataset: Optional[List] = None):
        """Deze functie maakt alle invoer voor het figuur."""

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

    def show_figure(self, plot_extra_dataset: Optional[List] = None):
        """Deze functie laat het figuur met alle resultaten zien."""
        if self.analysis_type in ['TXT_SH', 'DSS_SH']:
            self._run_sh()
        else:
            self._run()
        self.figure = go.Figure()
        self.set_figure(plot_extra_dataset)
        self.figure.show()

    def print_short_results(self):
        """Deze functie presenteert alle resultaten."""
        if self.analysis_type in ['TXT_SH', 'DSS_SH']:
            self._run_sh()
            index = ['verwachtingswaarde', 'karakteristieke waarde', 'rekenwaarde', 'standaarddeviatie']
            columns = ['tan phi [-]', 'phi [graden]']
            analyse_output_df = DataFrame(index=index, columns=columns)
            analyse_output_df['tan phi [-]'] = [self.tan_phi_gem, self.tan_phi_kar, self.tan_phi_d, '[-]']
            analyse_output_df['phi [graden]'] = [self.phi_gem, self.phi_kar, self.phi_d, self.st_dev_phi]
        else:
            self._run()
            index = ['verwachtingswaarde', 'karakteristieke waarde', 'rekenwaarde', 'standaarddeviatie']
            columns = ['tan phi [-]', 'phi [graden]', 'cohesie [kPa]']
            analyse_output_df = DataFrame(index=index, columns=columns)
            analyse_output_df['tan phi [-]'] = [self.tan_phi_gem, self.tan_phi_kar, self.tan_phi_d, '[-]']
            analyse_output_df['phi [graden]'] = [self.phi_gem, self.phi_kar, self.phi_d, self.st_dev_phi]
            analyse_output_df['cohesie [kPa]'] = [self.c_gem, self.c_kar, self.c_d, self.st_dev_c]
        return analyse_output_df

    def add_results_to_dbase(self, path):
        """
        This function adds results to the dbase Excel export, generated with the
        function `export_dbase_to_excel` in `import_data`. The results are added in
        a separate sheet called 'Resultaten'.
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
            'PV_VGWNAT_GEM', 'PV_VGWNAT_SD', 'PV_WATERGEHALTE_GEM [kN/m3]', 'PV_WATERGEHALTE_SD [kN/m3]', 'Timestamp'
        ]

        new_row = {
            'PVNAAM': self.investigation_groups,
            'PV_REK': self.effective_stress,
            'PV_TYPE_PROEF': self.analysis_type.split('_')[0],
            'PV_ANALYSE': self.analysis_type.split('_')[1],
            'PV_RESULTAAT_ID': f"{self.investigation_groups}_{self.effective_stress}_{self.analysis_type.split('_')[0]}_{self.analysis_type.split('_')[1]}",
            'PV_TYPEVERZAMELING': self.alpha,
            'PV_A1_COH_GEM [kPa]': self.gem_a1,
            'PV_A2_TAN_PHI_GEM [-]': self.gem_a2,
            'PV_A1_COH_KAR [kPa]': self.kar_a1,
            'PV_A2_TAN_PHI_KAR [-]': self.kar_a2,
            'PV_COH_GEM [kPa]': (self.c_gem if self.c_gem is not None and self.c_gem > 0
                                else "[-]" if self.c_gem is None
                                else f"{self.c_gem} (kan niet - aanpassen!)"
                                ),
            'PV_PHI_GEM [graden]': self.phi_gem,
            'PV_COH_KAR [kPa]': (self.c_kar if self.c_kar is not None and self.c_kar > 0
                                else "[-]" if self.c_kar is None
                                else f"{self.c_kar} (kan niet - aanpassen!)"
                                ),
            'PV_PHI_KAR [graden]': self.phi_kar,
            'PV_COH_SD_DSTAB [-]': (self.st_dev_c if self.c_gem is not None and self.c_kar is not None
                                    and self.c_gem > 0 and self.c_kar > 0
                                    else "[-]" if self.c_gem is None or self.c_kar is None
                                    else "[-] (c < 0)"),
            'PV_PHI_SD_DSTAB [-]': self.st_dev_phi,
            'PV_PARTPHI [-]': self.material_tan_phi,
            'PV_PARTCOH [-]': self.material_cohesie,
            'PV_VGWNAT_GEM [kN/m3]': self.calc_vgwnat_gem,
            'PV_VGWNAT_SD [kN/m3]': self.calc_vgwnat_sd,
            'PV_WATERGEHALTE_GEM': self.calc_watergehalte_gem,
            'PV_WATERGEHALTE_SD': self.calc_watergehalte_sd,
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

        with ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_updated.to_excel(writer, sheet_name='Resultaten', index=False)
        # door de manier van wegschrijven wordt het een beetje raar als je iets in deze code verandert, dus dit kan nog anders

        return df_updated


    def save_total_to_excel(self, path):
        effective_stress = str(self.effective_stress).replace('%', 'procent_')
        effective_stress = str(effective_stress).replace(' ', '')
        file_name = f"c_phi_export_test_{self.investigation_groups[0]}_{self.analysis_type}_{effective_stress}.xlsx"
        file_path = f"{path}/{file_name}"
        if self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
            self.cphi_analyses_data_df = self.cphi_analyses_data_df.rename(columns={'S\'': '\u03C3 \'', 'T': '\u03C4'})
        df_totaal = self.cphi_analyses_data_df
        with ExcelWriter(file_path, engine='openpyxl') as writer:
            df_totaal.to_excel(writer)
