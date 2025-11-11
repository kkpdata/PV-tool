import math
from pv_tool.imports.import_data import Dbase
from typing import Optional, List, Literal
from pv_tool.shansep_analysis.globals import (TEXTUAL_NAMES, NEW_COLUMN_NAMES, TEXTUAL_NAMES_DSS)
from pandas import DataFrame, ExcelWriter, read_excel
from pv_tool.shansep_analysis.calc_parameters import (
    calc_watergehalte_gem,
    calc_watergehalte_sd,
    calc_vgwnat_gem,
    calc_vgwnat_sd
)

from pv_tool.shansep_analysis.visualization_shansep import (
    add_proefresultaten_sv_su,
    add_extra_proefresultaten,
    add_5pr_bovengrens_sv_su,
    add_5pr_ondergrens_sv_su,
    add_fysische_realiseerbare_ondergrens_sv_su,
    add_lineair_fit_sv_su,
    add_proefresultaten_ln_ocr_ln_s,
    add_5pr_bovengrens_ln_ocr_ln_s,
    add_5pr_ondergrens_ln_ocr_ln_s,
    add_lineair_fit_ln_ocr_ln_s,
    set_layout_sv_su,
    set_layout_ln_ocr_ln_s
)

from pv_tool.shansep_analysis.variables import (
    gem_ln_su_svc_nc, exp_gem_ln_su_svc_nc,
    std_ln_su_svc_nc, kar_ln_su_svc_nc, exp_kar_ln_su_svc_nc,
    gem_pop_oc, std_pop_oc, kar_pop_oc,
    e_a1_oc, e_a2_oc, e_a1_nc_oc, e_a2_nc_oc,
    a1_kar_oc, a2_kar_oc,
    a1_kar_nc_oc, a2_kar_nc_oc, exp_gem_ln_su_svc_nc, gem_pop_oc,
    exp_kar_ln_su_svc_nc, kar_pop_oc)

from pv_tool.shansep_analysis.expand_analysis import (calculate_ln_ocr, calculate_pop,
                                                          calculate_chi_2_nc_oc, calculate_sv_tt_oc, calculate_sv_spop,
                                                          calculate_chi_2_oc, calculate_ln_sv_spop, calculate_sv_ty_oc,
                                                          calculate_chi_2_ondergrens_nc_oc, calculate_sv_tt_ondergrens_nc_oc,
                                                          calculate_chi_2_ondergrens_oc, calculate_sv_tt_nc_oc,
                                                          calculate_sv_ty_ondergrens_nc_oc, calculate_sv_ty_ondergrens_oc,
                                                          calculate_5pr_ondergrens_nc_oc, calculate_5pr_ondergrens_oc,
                                                          calculate_sv_ty_nc_oc, calculate_sv_tt_ondergrens_oc, calculate_sv_eff_oc,
                                                          calculate_sv_eff_nc_oc, calculate_5pr_bovengrens_oc, calculate_5pr_bovengrens_nc_oc)


#-------------------------- SHANSEP Analysis Class ---------------------------------------#

class SHANSEP:

    def __init__(self, dbase: Dbase,
                 analysis_type: Literal['TXT_S_POP', 'TXT_su_tabel', 'DSS_S_POP', 'DSS_su_tabel'],
                 investigation_groups: List,
                 effective_stress: Literal['2% rek', '5% rek', '10% rek', '15% rek', '20% rek',
                                            'pieksterkte', 'eindsterkte']):
        
        # Validate effective_stress based on analysis_type
        if analysis_type in ['TXT_S_POP', 'TXT_su_tabel'] and effective_stress in ['10% rek', '20% rek']:
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
        
        # Parameters
        self.calc_watergehalte_gem: Optional[float] = None
        self.calc_watergehalte_sd: Optional[float] = None
        self.calc_vgwnat_gem: Optional[float] = None
        self.calc_vgwnat_sd: Optional[float] = None

        self.e_a2_oc: Optional[float] = None
        self.e_a1_oc: Optional[float] = None
        self.e_a2_nc_oc: Optional[float] = None
        self.e_a1_nc_oc: Optional[float] = None
        self.exp_e_a1_nc_oc: Optional[float] = None
        self.exp_gem_ln_su_svc_nc: Optional[float] = None
        self.pop_gem_oc: Optional[float] = None

        self.a2_kar_oc: Optional[float] = None
        self.a1_kar_oc: Optional[float] = None
        self.a2_kar_nc_oc: Optional[float] = None
        self.a1_kar_nc_oc: Optional[float] = None
        self.exp_a1_kar_nc_oc: Optional[float] = None
        self.exp_kar_ln_su_svc_nc: Optional[float] = None
        self.pop_kar_oc: Optional[float] = None

        # Handmatige parameters
        self.snijpunt_gem_handmatig: Optional[float] = None
        self.s_gem_handmatig: Optional[float] = None
        self.m_gem_handmatig: Optional[float] = None

        self.snijpunt_kar_handmatig: Optional[float] = None
        self.s_kar_handmatig: Optional[float] = None
        self.m_kar_handmatig: Optional[float] = None

        self.pop_kar_handmatig: Optional[float] = None
        self.pop_gem_handmatig: Optional[float] = None

        # dataframes
        self.shansep_data_df: Optional[DataFrame] = None
        self.total_shansep_data_df: Optional[DataFrame] = None
        self.shansep_data_df_oc: Optional[DataFrame] = None
        self.shansep_data_df_nc_oc: Optional[DataFrame] = None
        self.df_results_shansep_gem: Optional[DataFrame] = None
        self.df_results_shansep_kar: Optional[DataFrame] = None

        pass

    def get_shansep_data(self):
        """Deze functie filtert de dbase-dataframe op basis van type analyse, PV_NAAM en de gewenste effectieve stress.
        Daarnaast worden de kolomnamen aangepast zodat ze ongeacht het rekpercentage allemaal dezelfde kolomnaam hebben.
        """
        if self.analysis_type in ['TXT_S_POP', 'TXT_su_tabel']:
            self.shansep_data_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
            self.shansep_data_df = self.shansep_data_df[self.shansep_data_df['PV_NAAM'].isin(
                    self.investigation_groups)]
            self.calc_watergehalte_gem = calc_watergehalte_gem(self.shansep_data_df)
            self.calc_watergehalte_sd = calc_watergehalte_sd(self.shansep_data_df)
            self.calc_vgwnat_gem = calc_vgwnat_gem(self.shansep_data_df)
            self.calc_vgwnat_sd = calc_vgwnat_sd(self.shansep_data_df)
            self.total_shansep_data_df = self.shansep_data_df
            self.shansep_data_df = self.shansep_data_df[TEXTUAL_NAMES.get(self.effective_stress, [])]

        elif self.analysis_type in ['DSS_S_POP', 'DSS_su_tabel']:
            self.shansep_data_df = self.dbase_df[self.dbase_df['ALG__DSS']]
            self.shansep_data_df = self.shansep_data_df[self.shansep_data_df['PV_NAAM'].isin(
                    self.investigation_groups)]
            self.calc_watergehalte_gem = calc_watergehalte_gem(self.shansep_data_df)
            self.calc_watergehalte_sd = calc_watergehalte_sd(self.shansep_data_df)
            self.calc_vgwnat_gem = calc_vgwnat_gem(self.shansep_data_df)
            self.calc_vgwnat_sd = calc_vgwnat_sd(self.shansep_data_df)
            self.total_shansep_data_df = self.shansep_data_df
            self.shansep_data_df = self.shansep_data_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])]

        self.shansep_data_df.columns = NEW_COLUMN_NAMES

    def apply_settings(self, alpha: Optional[float] = None):
        """Met deze functie kan je de alpha en materiaalfactoren opgeven."""
        self.alpha = alpha if alpha is not None else self.alpha

    def get_previous_results(self, file_path: str):
        """
        Zoekt naar eerdere analyseresultaten in een Excel-bestand.

        Parameters
        ----------
        file_path : str
            Pad naar de map waar het Excel-bestand staat plus de bestandsnaam

        Returns
        -------
        DataFrame of None
            DataFrame met eerdere resultaten als deze gevonden zijn, anders None
        """
        # file_name = 'Template_PVtool5_0.xlsx'
        # file_path = f"{path}/{file_name}"

        try:
            with open(file_path, 'r'):
                pass
        except FileNotFoundError:
            raise FileNotFoundError(f"Er is geen dbase aanwezig op de locatie {file_path}.")

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

        latest_entry = filtered_df.sort_values(by='Timestamp', ascending=False).iloc[0]

        return latest_entry

    def expand_analysis_df_sutabel(self):
        """Deze functie berekent alle benodigde parameters per monster voor de analyse."""
        # calculate_s_tt(self)
        # calculate_s_ty(self)
        # calculate_chi_2(self)
        # calculate_s_sutabel(self)
        # calculate_5pr_ondergrens(self)
        # calculate_5pr_bovengrens(self)
        # calculate_s_tt_ondergrens(self)
        # calculate_s_ty_ondergrens(self)
        # calculate_chi_2_ondergrens(self)
        return f"Deze functie is nog niet geïmplementeerd voor de su tabel analyse."

    def expand_analysis_df_s_pop_alleen_oc(self):
        """Deze functie berekent alle benodigde parameters per monster voor de analyse."""
        calculate_ln_ocr(self)
        calculate_sv_spop(self)
        calculate_ln_sv_spop(self)
        calculate_pop(self)

        self.shansep_data_df_oc = self.shansep_data_df[self.shansep_data_df['consolidatietype'] == 'OC'].copy()

        calculate_sv_tt_oc(self)
        calculate_sv_ty_oc(self)
        calculate_chi_2_oc(self)
        calculate_sv_eff_oc(self)
        calculate_5pr_ondergrens_oc(self)
        calculate_5pr_bovengrens_oc(self)
        calculate_sv_tt_ondergrens_oc(self)
        calculate_sv_ty_ondergrens_oc(self)
        calculate_chi_2_ondergrens_oc(self)

    def expand_analysis_df_s_pop(self):
        """Deze functie berekent alle benodigde parameters per monster voor de analyse."""
        calculate_ln_ocr(self)
        calculate_sv_spop(self)
        calculate_ln_sv_spop(self)
        calculate_pop(self)

        self.shansep_data_df_nc_oc = self.shansep_data_df.copy()
        self.shansep_data_df_nc_oc = self.shansep_data_df_nc_oc.sort_values(
            by=['consolidatietype', self.shansep_data_df_nc_oc.index.name or self.shansep_data_df_nc_oc.index],
            ascending=[False, True]
        )

        calculate_sv_tt_nc_oc(self)
        calculate_sv_ty_nc_oc(self)
        calculate_chi_2_nc_oc(self)
        calculate_sv_eff_nc_oc(self)
        calculate_5pr_ondergrens_nc_oc(self)
        calculate_5pr_bovengrens_nc_oc(self)
        calculate_sv_tt_ondergrens_nc_oc(self)
        calculate_sv_ty_ondergrens_nc_oc(self)
        calculate_chi_2_ondergrens_nc_oc(self)

    def write_analysis_to_excel(self, file_path: str):
        """
        Schrijft de analyse dataframes naar een Excel-bestand met verschillende sheets.

        Parameters
        ----------
        file_path : str
            Pad naar de map waar het Excel-bestand moet worden opgeslagen plus de bestandsnaam
        """
        with ExcelWriter(file_path) as writer:
            if self.shansep_data_df is not None:
                self.shansep_data_df.to_excel(writer, sheet_name='Shansep Data', index=False)
            if self.shansep_data_df_oc is not None:
                self.shansep_data_df_oc.to_excel(writer, sheet_name='Shansep Data OC', index=False)
            if self.shansep_data_df_nc_oc is not None:
                self.shansep_data_df_nc_oc.to_excel(writer, sheet_name='Shansep Data NC_OC', index=False)

    def get_shansep_parameters(self):
        """
        Berekent de parameters van de shansep analyse
        """
        self.e_a2_oc = e_a2_oc(self)
        self.e_a1_oc = e_a1_oc(self)
        self.e_a2_nc_oc = e_a2_nc_oc(self)
        self.e_a1_nc_oc = e_a1_nc_oc(self)
        self.exp_e_a1_nc_oc = math.exp(e_a1_nc_oc(self))
        self.exp_gem_ln_su_svc_nc = exp_gem_ln_su_svc_nc(self)
        self.pop_gem_oc = gem_pop_oc(self)

        self.a2_kar_oc = a2_kar_oc(self)
        self.a1_kar_oc = a1_kar_oc(self)
        self.a2_kar_nc_oc = a2_kar_nc_oc(self)
        self.a1_kar_nc_oc = a1_kar_nc_oc(self)
        self.exp_a1_kar_nc_oc = math.exp(a1_kar_nc_oc(self))
        self.exp_kar_ln_su_svc_nc = exp_kar_ln_su_svc_nc(self)
        self.pop_kar_oc = kar_pop_oc(self)

    def _run_shansep(self):
        """
        Voert de volledige shansep analyse uit in de juiste volgorde:
        data ophalen, parameters berekenen en resultaten bepalen.
        """
        self.get_shansep_data()

        if self.analysis_type in ['TXT_S_POP', 'DSS_S_POP']:
            self.expand_analysis_df_s_pop_alleen_oc()
            self.expand_analysis_df_s_pop()
        elif self.analysis_type in ['TXT_su_tabel', 'DSS_su_tabel']:
            self.expand_analysis_df_sutabel()

        self.get_shansep_parameters()


    def get_result_values_shansep(self):
        """
        Berekent de definitieve resultaten van de shansep analyse
        """
        self._run_shansep()
        self.df_results_shansep_gem = DataFrame(
            index=['bepaling S en POP uit triaxiaal- of DSS proeven', 'bepaling S en m uit triaxiaal- of DSS proeven',
                    'o.b.v. opgegeven POP bij triaxiaal- of DSS proeven',
                   'bepaling S uit triaxiaal- of DSS proeven OCR=1'])
        self.df_results_shansep_gem['snijpunt y-as [kPa]'] = [self.e_a1_oc, None, None, None]
        self.df_results_shansep_gem['Schuifsterkteratio S [-]'] = [self.e_a2_oc, self.exp_e_a1_nc_oc, None, self.exp_gem_ln_su_svc_nc]
        self.df_results_shansep_gem['sterkte toename exponent = m [-]'] = [None, self.e_a2_nc_oc, None, None]
        pop_bepaald = self.e_a1_oc/self.e_a2_oc/self.e_a2_nc_oc
        self.df_results_shansep_gem['POP [kPa]'] = [pop_bepaald, pop_bepaald, self.pop_gem_oc, None]

        self.df_results_shansep_kar = DataFrame(
            index=['bepaling S en POP uit triaxiaal- of DSS proeven', 'bepaling S en m uit triaxiaal- of DSS proeven',
                   'o.b.v. opgegeven POP bij triaxiaal- of DSS proeven',
                   'bepaling S uit triaxiaal- of DSS proeven OCR=1'])
        self.df_results_shansep_gem['snijpunt y-as [kPa]'] = [self.a1_kar_oc, None, None, None]
        self.df_results_shansep_gem['Schuifsterkteratio S [-]'] = [self.a2_kar_oc, self.exp_a1_kar_nc_oc, None, self.exp_kar_ln_su_svc_nc]
        self.df_results_shansep_gem['sterkte toename exponent = m [-]'] = [None, self.a2_kar_nc_oc, None, None]
        pop_bepaald = self.a1_kar_oc/self.a2_kar_oc/self.a2_kar_nc_oc
        self.df_results_shansep_gem['POP [kPa]'] = [pop_bepaald, pop_bepaald, self.pop_kar_oc, None]

        # write these dataframes to excel
        return self.df_results_shansep_gem, self.df_results_shansep_kar

    def export_shansep_results_excel(self, file_path: str):
        """
        Exporteert de shansep resultaten naar een Excel-bestand.

        Parameters
        ----------
        file_path : str
            Pad naar de map waar het Excel-bestand moet worden opgeslagen plus de bestandsnaam
        """
        df_gem, df_kar = self.get_result_values_shansep()
        with ExcelWriter(file_path) as writer:
            df_gem.to_excel(writer, sheet_name='Gemiddeld')
            df_kar.to_excel(writer, sheet_name='Karakteristiek')

    def print_sutabel(self):
        """print de blauwe tabel in de excel naar excel
        wordt ook weggeschreven naar pdf bij save_to_pdf
        wordt nu bij visualisation ook aangeroepen all
        """

    def set_parameters_handmatig(self, snijpunt_gem: float, s_gem: float, m_gem: float,
                              snijpunt_kar: float, s_kar: float, m_kar: float):
        """
        Stelt de handmatige parameters in voor de analyse. De invoer moet handmatig worden gedaan door de gebruiker op basis van de resultaten tabel
        """
        self.snijpunt_gem_handmatig = snijpunt_gem
        self.s_gem_handmatig = s_gem
        self.m_gem_handmatig = m_gem
        self.pop_gem_handmatig = snijpunt_gem / s_gem / m_gem

        self.snijpunt_kar_handmatig = snijpunt_kar
        self.s_kar_handmatig = s_kar
        self.m_kar_handmatig = m_kar
        self.pop_kar_handmatig = snijpunt_kar / s_kar / m_kar




    def set_figure_sv_su(self, plot_extra_dataset: Optional[List] = None, plot_spanningspaden: bool = False):
        """
        Maakt een visualisatie van de analyseresultaten.

        Parameters
        ----------
        plot_extra_dataset : List, optioneel
            Extra dataset om in de plot weer te geven

        plot_spanningspaden : bool, optioneel
            Of de spanningspaden moeten worden weergegeven
        """
        self._run_shansep()
        add_proefresultaten_sv_su(self)
        if plot_extra_dataset is not None:
            add_extra_proefresultaten(self, plot_extra_dataset)
        add_5pr_bovengrens_sv_su(self)
        add_5pr_ondergrens_sv_su(self)
        add_fysische_realiseerbare_ondergrens_sv_su(self)
        add_lineair_fit_sv_su(self)
        set_layout_sv_su(self)

    def set_figure_ln_ocr_ln_s(self, plot_extra_dataset: Optional[List] = None):
        """
        Maakt een visualisatie van de analyseresultaten.

        Parameters
        ----------
        plot_extra_dataset : List, optioneel
            Extra dataset om in de plot weer te geven
        """
        self._run_shansep()
        add_proefresultaten_ln_ocr_ln_s(self)
        if plot_extra_dataset is not None:
            add_extra_proefresultaten(self, plot_extra_dataset)
        add_5pr_bovengrens_ln_ocr_ln_s(self)
        add_5pr_ondergrens_ln_ocr_ln_s(self)
        add_lineair_fit_ln_ocr_ln_s(self)
        set_layout_ln_ocr_ln_s(self)
