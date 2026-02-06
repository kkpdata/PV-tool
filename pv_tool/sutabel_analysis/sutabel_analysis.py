"""
SUTABEL Analysis Class

Deze module bevat de SUTABEL klasse voor het uitvoeren van sutabel-m analyses.
De sutabel-m methode analyseert overgeconsolideerde (OC) triaxiaal of DSS proeven
om de ongedraineerde schuifsterkte te bepalen.
"""

import math
from pv_tool.imports.import_data import Dbase
from typing import Optional, List, Literal
from pv_tool.shansep_analysis.globals import (TEXTUAL_NAMES, NEW_COLUMN_NAMES, TEXTUAL_NAMES_DSS)
from pandas import DataFrame, ExcelWriter
import plotly.graph_objects as go
from pathlib import Path
from pv_tool.shansep_analysis.calc_parameters import (
    calc_watergehalte_gem_txt, calc_watergehalte_gem_dss,
    calc_watergehalte_sd_txt, calc_watergehalte_sd_dss,
    calc_vgwnat_gem_txt, calc_vgwnat_gem_dss,
    calc_vgwnat_sd_txt, calc_vgwnat_sd_dss
)
from pandas import read_excel
from scipy.stats import lognorm


class SUTABEL:
    """
    Klasse voor het uitvoeren van sutabel-m analyses.

    De sutabel-m methode analyseert overgeconsolideerde (OC) triaxiaal of DSS proeven
    om parameters te bepalen voor het berekenen van ongedraineerde schuifsterkte.

    Attributes
    ----------
    dbase: Dbase
        Database object met proefgegevens
    analysis_type: str
        Type analyse ('TXT_su_tabel' of 'DSS_su_tabel')
    investigation_groups: List[str]
        Lijst met te analyseren proevenverzamelingen
    effective_stress: str
        Effectieve spanning niveau (bijv. '15% rek')
    alpha: float
        Type verzameling (1.0 = lokaal, 0.75 = regionaal)

    Parameters (berekend)
    ----------
    e_a1_sutabel : float
        Snijpunt gemiddeld in ln-ruimte
    e_a2_sutabel : float
        Helling gemiddeld in ln-ruimte
    svgm_gem_sutabel : float
        exp(e_a1) - sutabel parameter gemiddeld [kPa]
    m_gem_sutabel : float
        1 - e_a2 - exponent parameter gemiddeld
    a1_kar_sutabel : float
        Snijpunt karakteristiek in ln-ruimte
    a2_kar_sutabel : float
        Helling karakteristiek in ln-ruimte
    svgm_kar_sutabel : float
        exp(a1_kar) - sutabel parameter karakteristiek [kPa]
    m_kar_sutabel : float
        1 - a2_kar - exponent parameter karakteristiek
    vc_fit_kar_sutabel : float
        Coefficient of Variation voor fit (user input)
    STDEV_logn_vc_sutabel : float
        sqrt(LN(1 + vc^2)) - standaarddeviatie lognormaal
    steyx_sutabel : float
        Standaardfout van de schatting
    """

    def __init__(self,
                 dbase: Dbase,
                 analysis_type: Literal['TXT_su_tabel', 'DSS_su_tabel'],
                 investigation_groups: List[str],
                 effective_stress: str):
        """
        Initialiseert een SUTABEL analyse instantie.

        Parameters
        ----------
        dbase : Dbase
            Database object met proefgegevens
        analysis_type : Literal['TXT_su_tabel', 'DSS_su_tabel']
            Type analyse
        investigation_groups : List[str]
            Lijst met te analyseren proevenverzamelingen
        effective_stress : str
            Effectieve spanning niveau (bijv. '15% rek')
        """
        self.dbase = dbase
        self.dbase_df = dbase.dbase_df
        self.analysis_type = analysis_type
        self.investigation_groups = investigation_groups
        self.effective_stress = effective_stress
        self.alpha = 0.75
        self.show_title = True

        # Berekende watergehalte en volumegewicht
        self.calc_watergehalte_gem: Optional[float] = None
        self.calc_watergehalte_sd: Optional[float] = None
        self.calc_vgwnat_gem: Optional[float] = None
        self.calc_vgwnat_sd: Optional[float] = None

        # Sutabel basis parameters
        self.e_a2_sutabel: Optional[float] = None
        self.e_a1_sutabel: Optional[float] = None
        self.a2_kar_sutabel: Optional[float] = None
        self.a1_kar_sutabel: Optional[float] = None
        self.steyx_sutabel: Optional[float] = None

        # Sutabel afgeleide parameters voor grafieken
        self.svgm_gem_sutabel: Optional[float] = None  # exp(e_a1)
        self.m_gem_sutabel: Optional[float] = None  # 1 - e_a2
        self.svgm_kar_sutabel: Optional[float] = None  # exp(a1_kar)
        self.m_kar_sutabel: Optional[float] = None  # 1 - a2_kar
        self.vc_fit_kar_sutabel: Optional[float] = None  # User input
        self.STDEV_logn_vc_sutabel: Optional[float] = None  # sqrt(LN(1 + vc^2))

        # Handmatige parameters
        self.parameters_handmatig: bool = False
        self.a1_kar_handmatig: Optional[float] = None
        self.a2_kar_handmatig: Optional[float] = None
        self.vc_fit_kar_handmatig: Optional[float] = None

        # Dataframes
        self.sutabel_data_df: Optional[DataFrame] = None
        self.total_sutabel_data_df: Optional[DataFrame] = None
        self.sutabel_filtered_data_df: Optional[DataFrame] = None
        self.sutabel_grafiek: Optional[DataFrame] = None
        self.su_fit_constante_vc: Optional[DataFrame] = None

        # Figure voor plotly
        self.figure_sv_su = go.Figure()
        self.figure_ln_sv_ln_su = go.Figure()

    # ========= Instelling en Data Ophalen Methodes ==========

    def apply_settings(self, alpha: Optional[float] = None):
        """Met deze functie kan je de alpha en materiaalfactoren opgeven."""
        self.alpha = alpha if alpha is not None else self.alpha

    def get_sutabel_data(self):
        """
        Haalt de relevante proefgegevens op uit de database.

        Filtert de database op basis van:
        - Analysis type (TXT of DSS)
        - Investigation groups (PV_NAAM)
        - Effective stress niveau

        Maakt self.sutabel_data_df en self.total_sutabel_data_df aan.
        """
        if self.analysis_type in ['TXT_su_tabel']:
            self.sutabel_data_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']].copy()
            self.sutabel_data_df = self.sutabel_data_df[self.sutabel_data_df['PV_NAAM'].isin(
                self.investigation_groups)].copy()
            self.calc_watergehalte_gem = calc_watergehalte_gem_txt(self.sutabel_data_df)
            self.calc_watergehalte_sd = calc_watergehalte_sd_txt(self.sutabel_data_df)
            self.calc_vgwnat_gem = calc_vgwnat_gem_txt(self.sutabel_data_df)
            self.calc_vgwnat_sd = calc_vgwnat_sd_txt(self.sutabel_data_df)
            self.total_sutabel_data_df = self.sutabel_data_df.copy()
            self.sutabel_data_df = self.sutabel_data_df[TEXTUAL_NAMES.get(self.effective_stress, [])].copy()

        elif self.analysis_type in ['DSS_su_tabel']:
            self.sutabel_data_df = self.dbase_df[self.dbase_df['ALG__DSS']].copy()
            self.sutabel_data_df = self.sutabel_data_df[self.sutabel_data_df['PV_NAAM'].isin(
                self.investigation_groups)].copy()
            self.calc_watergehalte_gem = calc_watergehalte_gem_dss(self.sutabel_data_df)
            self.calc_watergehalte_sd = calc_watergehalte_sd_dss(self.sutabel_data_df)
            self.calc_vgwnat_gem = calc_vgwnat_gem_dss(self.sutabel_data_df)
            self.calc_vgwnat_sd = calc_vgwnat_sd_dss(self.sutabel_data_df)
            self.total_sutabel_data_df = self.sutabel_data_df.copy()
            self.sutabel_data_df = self.sutabel_data_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])].copy()

        self.sutabel_data_df.columns = NEW_COLUMN_NAMES

    def get_previous_results(self, path: str, file_name: str):
        """
        Zoekt naar eerdere analyseresultaten in een Excel-bestand.

        Parameters
        ----------
        path: str
            Pad naar de map waar het Excel-bestand staat
        file_name: str
            Naam van het Excel-bestand

        Returns
        -------
        DataFrame of None
            DataFrame met eerdere resultaten als deze gevonden zijn, anders None
        """

        file_path = f"{path}/{file_name}"

        try:
            with open(file_path, 'r'):
                pass
        except FileNotFoundError:
            raise FileNotFoundError(f"Er is geen dbase aanwezig op de locatie {file_path}.")

        try:
            results_df = read_excel(file_path, sheet_name='Resultaten SU-tabel-m', skiprows=6)
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
        """
        Berekent alle benodigde parameters per monster voor de sutabel-m analyse.

        Filtert op OC proeven en maakt kolommen aan voor:
        - ln(s'v) en ln(su)
        - Regressie componenten (s_tt, s_ty, chi_2)
        - Effectieve spanning waarden
        - 5% boven- en ondergrenzen
        - Ondergrens parameters
        """
        from pv_tool.sutabel_analysis.expand_analysis import (
            calculate_ln_sv_sutabel, calculate_ln_su_sutabel,
            calculate_sv_tt_sutabel, calculate_sv_ty_sutabel,
            calculate_chi_2_sutabel, calculate_sv_eff_sutabel,
            calculate_5pr_ondergrens_sutabel, calculate_5pr_bovengrens_sutabel,
            calculate_sv_tt_ondergrens_sutabel, calculate_sv_ty_ondergrens_sutabel,
            calculate_chi_2_ondergrens_sutabel
        )

        # Filter op alleen OC proeven
        self.sutabel_filtered_data_df = self.sutabel_data_df[
            self.sutabel_data_df['consolidatietype'] == 'OC'
            ].copy()

        # Update sutabel_data_df to work with the OC-filtered data
        self.sutabel_data_df = self.sutabel_filtered_data_df.copy()

        # Bereken ln(s'v) en ln(su) kolommen
        calculate_ln_sv_sutabel(self)
        calculate_ln_su_sutabel(self)

        # Bereken s_tt en s_ty voor lineaire regressie
        calculate_sv_tt_sutabel(self)
        calculate_sv_ty_sutabel(self)

        # Bereken chi_2
        calculate_chi_2_sutabel(self)

        # Bereken effectieve spanning waarden
        calculate_sv_eff_sutabel(self)

        # Bereken 5% onder- en bovengrenzen
        calculate_5pr_ondergrens_sutabel(self)
        calculate_5pr_bovengrens_sutabel(self)

        # Bereken s_tt, s_ty en chi_2 voor ondergrenzen
        calculate_sv_tt_ondergrens_sutabel(self)
        calculate_sv_ty_ondergrens_sutabel(self)
        calculate_chi_2_ondergrens_sutabel(self)

    def get_sutabel_parameters(self, vc_fit_kar_sutabel: Optional[float] = None):
        """
        Berekent de sutabel-m parameters.

        Parameters
        ----------
        vc_fit_kar_sutabel : float, optioneel
            Coefficient of Variation voor sutabel fit (user input)
        """
        from pv_tool.sutabel_analysis.variables import (
            e_a2_sutabel, e_a1_sutabel,
            a2_kar_sutabel, a1_kar_sutabel,
            steyx_sutabel
        )

        self.e_a2_sutabel = e_a2_sutabel(self)
        self.e_a1_sutabel = e_a1_sutabel(self)
        self.a2_kar_sutabel = a2_kar_sutabel(self)
        self.a1_kar_sutabel = a1_kar_sutabel(self)
        self.steyx_sutabel = steyx_sutabel(self)

        # Bereken afgeleide parameters voor grafiek
        self.svgm_gem_sutabel = math.exp(self.e_a1_sutabel)
        self.m_gem_sutabel = 1 - self.e_a2_sutabel
        self.svgm_kar_sutabel = math.exp(self.a1_kar_sutabel)
        self.m_kar_sutabel = 1 - self.a2_kar_sutabel

        # Sla vc_fit_kar op (kan None zijn als niet opgegeven)
        if vc_fit_kar_sutabel is not None:
            self.vc_fit_kar_sutabel = vc_fit_kar_sutabel
            self.STDEV_logn_vc_sutabel = math.sqrt(math.log(1 + (self.vc_fit_kar_sutabel ** 2)))
        else:
            self.vc_fit_kar_sutabel = None
            self.STDEV_logn_vc_sutabel = None

    def calculate_sutabel_grafiek(self):
        """
        Berekent de dataframes voor sutabel grafiek lijnen.

        Maakt twee dataframes:
        - sutabel_grafiek: bevat su_gem en su_kar lijnen
        - su_fit_constante_vc: bevat su_kar fit met constante vc lijn
        """
        # Bepaal s'v waarden voor de grafiek
        max_sv = self.sutabel_data_df['S\'v'].max()
        sv_values = [1, 5, 10, 20, 30, 40, max_sv]

        # Bereken su_gem en su_kar
        su_gem_values = [self.svgm_gem_sutabel * (sv ** (1 - self.m_gem_sutabel)) for sv in sv_values]
        su_kar_values = [self.svgm_kar_sutabel * (sv ** (1 - self.m_kar_sutabel)) for sv in sv_values]

        # Maak sutabel_grafiek dataframe
        self.sutabel_grafiek = DataFrame({
            "s'v [kPa]": sv_values,
            "su_gem [kPa]": su_gem_values,
            "su_kar [kPa]": su_kar_values
        })

        # Als vc_fit_kar is opgegeven, bereken ook de constante vc fit
        if self.vc_fit_kar_sutabel is not None and self.STDEV_logn_vc_sutabel is not None:
            # Bereken ln waarden
            ln_su_gem = [math.log(su) - 0.5 * (self.STDEV_logn_vc_sutabel ** 2) for su in su_gem_values]
            ln_su_kar = [math.log(su) - 0.5 * (self.STDEV_logn_vc_sutabel ** 2) for su in su_kar_values]

            # Bereken su_kar fit met constante vc
            su_kar_fit_vc = [lognorm.ppf(0.05, s=self.STDEV_logn_vc_sutabel, scale=math.exp(ln))
                             for ln in ln_su_gem]

            self.su_fit_constante_vc = DataFrame({
                "s'v [kPa]": sv_values,
                "ln(su_gem) [kPa]": ln_su_gem,
                "ln(su_kar) [kPa]": ln_su_kar,
                "su_kar fit met constante vc [kPa]": su_kar_fit_vc
            })
        else:
            self.su_fit_constante_vc = None

    def _run_sutabel(self):
        """
        Voert de volledige sutabel analyse uit in de juiste volgorde.
        """
        self.get_sutabel_data()
        self.expand_analysis_df_sutabel()
        self.get_sutabel_parameters()

    # ========== Handmatige Parameters en wegschrijven ==========

    def set_manual_parameters(self,
                              a1_kar: Optional[float] = None,
                              a2_kar: Optional[float] = None,
                              vc_fit_kar: Optional[float] = None):
        """
        Stelt handmatige parameters in voor de sutabel analyse.

        Na het instellen van handmatige parameters worden deze gebruikt in plaats van
        de berekende parameters. Dit is handig voor iteratieve analyses waarbij de
        gebruiker verschillende parameterwaarden wil testen.

        De analyse wordt automatisch uitgevoerd als deze nog niet is gedaan.

        Parameters
        ----------
        a1_kar : float, optioneel
            Handmatig ingesteld karakteristiek snijpunt in ln-ruimte
        a2_kar : float, optioneel
            Handmatig ingestelde karakteristieke helling in ln-ruimte
        vc_fit_kar : float, optioneel
            Handmatig ingestelde Coefficient of Variation voor fit

        Examples
        --------
        >>> sutabel = SUTABEL(...)
        >>> sutabel.show_figure_sv_su_sutabel()
        >>>
        >>> # Pas parameters aan en analyseer opnieuw
        >>> sutabel.set_manual_parameters(a1_kar=0.85, a2_kar=0.70, vc_fit_kar=0.25)
        >>> sutabel.show_figure_sv_su_sutabel()
        """
        # Zorg dat analyse is uitgevoerd voordat handmatige parameters worden ingesteld
        if self.sutabel_data_df is None:
            self._run_sutabel()

        self.parameters_handmatig = True

        # Sla handmatige parameters op
        if a1_kar is not None:
            self.a1_kar_handmatig = a1_kar
        if a2_kar is not None:
            self.a2_kar_handmatig = a2_kar
        if vc_fit_kar is not None:
            self.vc_fit_kar_handmatig = vc_fit_kar

        # Herbereken de afgeleide parameters met de nieuwe waarden
        self._update_parameters_from_manual()

    def _update_parameters_from_manual(self):
        """
        Update de gebruikte parameters op basis van handmatige input.

        Als handmatige parameters zijn ingesteld, worden deze gebruikt.
        Anders blijven de berekende parameters behouden.
        """
        if not self.parameters_handmatig:
            return

        # Gebruik handmatige a1_kar of behoud berekende waarde
        if self.a1_kar_handmatig is not None:
            a1_kar_te_gebruiken = self.a1_kar_handmatig
        else:
            a1_kar_te_gebruiken = self.a1_kar_sutabel

        # Gebruik handmatige a2_kar of behoud berekende waarde
        if self.a2_kar_handmatig is not None:
            a2_kar_te_gebruiken = self.a2_kar_handmatig
        else:
            a2_kar_te_gebruiken = self.a2_kar_sutabel

        # Gebruik handmatige vc_fit_kar of behoud berekende waarde
        if self.vc_fit_kar_handmatig is not None:
            vc_te_gebruiken = self.vc_fit_kar_handmatig
        else:
            vc_te_gebruiken = self.vc_fit_kar_sutabel

        # Bereken afgeleide parameters met de te gebruiken waarden
        self.svgm_kar_sutabel = math.exp(a1_kar_te_gebruiken)
        self.m_kar_sutabel = 1 - a2_kar_te_gebruiken

        # Update vc parameters
        if vc_te_gebruiken is not None:
            self.vc_fit_kar_sutabel = vc_te_gebruiken
            self.STDEV_logn_vc_sutabel = math.sqrt(math.log(1 + (vc_te_gebruiken ** 2)))

        # Herbereken de grafiek dataframes met de nieuwe parameters
        self.calculate_sutabel_grafiek()

    def get_short_results(self):
        """
        Genereert een samenvattend overzicht van de SUTABEL analyseresultaten.

        Returns
        -------
        DataFrame
            DataFrame met verwachtingswaarden, karakteristieke waarden,
            en standaarddeviaties voor de belangrijkste SUTABEL parameters
        """
        # Voer analyse uit als nog niet gedaan
        if self.sutabel_data_df is None or self.e_a1_sutabel is None:
            self._run_sutabel()
            if self.e_a1_sutabel is None:
                self.get_sutabel_parameters()

        # Update parameters als handmatige waarden zijn ingesteld
        if self.parameters_handmatig:
            self._update_parameters_from_manual()

        index = ['Verwachtingswaarde', 'Karakteristieke waarde', 'Standaarddeviatie']
        columns = ['svgm [kPa]', 'm [-]', 'vc_fit [-]']

        analyse_output_df = DataFrame(index=index, columns=columns)

        # Gebruik de huidige (mogelijk handmatig aangepaste) parameterwaarden
        svgm_gem = self.svgm_gem_sutabel
        svgm_kar = self.svgm_kar_sutabel
        m_gem = self.m_gem_sutabel
        m_kar = self.m_kar_sutabel
        vc_fit_kar = self.vc_fit_kar_sutabel
        steyx = self.steyx_sutabel

        analyse_output_df['svgm [kPa]'] = [svgm_gem, svgm_kar, steyx]
        analyse_output_df['m [-]'] = [m_gem, m_kar, '[-]']
        analyse_output_df['vc_fit [-]'] = [vc_fit_kar, vc_fit_kar, self.STDEV_logn_vc_sutabel]

        return analyse_output_df

    def write_analysis_to_excel(self, file_path: str):
        """
        Schrijft de analyse dataframes naar een Excel-bestand.

        Parameters
        ----------
        file_path : str
            Pad naar de map waar het Excel-bestand moet worden opgeslagen plus de bestandsnaam
        """
        with ExcelWriter(file_path) as writer:
            if self.sutabel_data_df is not None:
                self.sutabel_data_df.to_excel(writer, sheet_name='Data', index=False)
            if self.sutabel_filtered_data_df is not None:
                self.sutabel_filtered_data_df.to_excel(writer, sheet_name='Sutabel Filtered Data', index=False)
            if self.sutabel_grafiek is not None:
                self.sutabel_grafiek.to_excel(writer, sheet_name='Sutabel Grafiek', index=False)
            if self.su_fit_constante_vc is not None:
                self.su_fit_constante_vc.to_excel(writer, sheet_name='vc Fit', index=False)

    # ========== Visualisatie Methodes ==========

    def set_figure_ln_sv_ln_su_sutabel(self, plot_extra_dataset: Optional[List] = None):
        """
        Maakt een visualisatie van de sutabel analyseresultaten voor ln(s'v) vs ln(su).

        Deze plot toont:
        - Proefresultaten (OC-data)
        - Lineaire fit
        - 5% boven- en ondergrens
        - Fysische realiseerbare ondergrens (gebaseerd op a1_kar en a2_kar)

        De analyse wordt automatisch uitgevoerd als deze nog niet is gedaan.
        """
        from pv_tool.sutabel_analysis.visualization_sutabel import (
            add_proefresultaten_ln_sv_ln_su_sutabel,
            add_extra_proefresultaten_ln_sv_ln_su_sutabel,
            add_linear_fit_ln_sv_ln_su_sutabel,
            add_5pr_bovengrens_ln_sv_ln_su_sutabel,
            add_5pr_ondergrens_ln_sv_ln_su_sutabel,
            add_fysische_realiseerbare_ondergrens_ln_sv_ln_su_sutabel,
            set_layout_ln_sv_ln_su_sutabel
        )

        # Voer analyse uit als nog niet gedaan
        if self.sutabel_data_df is None:
            self._run_sutabel()

        if plot_extra_dataset is not None:
            add_extra_proefresultaten_ln_sv_ln_su_sutabel(self, plot_extra_dataset)
        add_proefresultaten_ln_sv_ln_su_sutabel(self)
        add_linear_fit_ln_sv_ln_su_sutabel(self)
        add_5pr_bovengrens_ln_sv_ln_su_sutabel(self)
        add_5pr_ondergrens_ln_sv_ln_su_sutabel(self)
        add_fysische_realiseerbare_ondergrens_ln_sv_ln_su_sutabel(self)
        set_layout_ln_sv_ln_su_sutabel(self)

    def show_figure_ln_sv_ln_su_sutabel(self, plot_extra_dataset: Optional[List] = None):
        """
        Toont de visualisatie van de sutabel analyseresultaten voor ln(s'v) vs ln(su).

        De analyse wordt automatisch uitgevoerd als deze nog niet is gedaan.
        """
        self.figure_ln_sv_ln_su = go.Figure()
        self.set_figure_ln_sv_ln_su_sutabel(plot_extra_dataset)
        self.figure_ln_sv_ln_su.show()

    def set_figure_sv_su_sutabel(self, plot_extra_dataset: Optional[List] = None):
        """
        Maakt een visualisatie van de sutabel analyseresultaten voor s'v vs su.

        Deze plot toont:
        - Proefresultaten (OC-data)
        - Sutabel_gem lijn
        - Sutabel_kar lijn
        - Su_kar fit met constante VC (als vc_fit_kar is opgegeven)

        Als handmatige parameters zijn ingesteld, worden deze gebruikt voor de visualisatie.
        De analyse wordt automatisch uitgevoerd als deze nog niet is gedaan.
        """
        from pv_tool.sutabel_analysis.visualization_sutabel import (
            add_proefresultaten_sv_su_sutabel,
            add_extra_proefresultaten_sv_su_sutabel,
            add_sutabel_gem_line,
            add_sutabel_kar_line,
            add_su_kar_fit_constante_vc,
            set_layout_sv_su_sutabel
        )

        # Voer analyse uit als nog niet gedaan
        if self.sutabel_data_df is None:
            self._run_sutabel()

        # Update parameters als handmatige waarden zijn ingesteld
        if self.parameters_handmatig:
            self._update_parameters_from_manual()

        # Bereken grafiek dataframes
        self.calculate_sutabel_grafiek()

        # Voeg data en lijnen toe
        if plot_extra_dataset is not None:
            add_extra_proefresultaten_sv_su_sutabel(self, plot_extra_dataset)
        add_proefresultaten_sv_su_sutabel(self)
        add_sutabel_gem_line(self)
        add_sutabel_kar_line(self)

        # Voeg vc fit lijn toe als deze beschikbaar is
        if self.su_fit_constante_vc is not None:
            add_su_kar_fit_constante_vc(self)

        set_layout_sv_su_sutabel(self)

    def show_figure_sv_su_sutabel(self, plot_extra_dataset: Optional[List] = None):
        """
        Toont de visualisatie van de sutabel analyseresultaten voor s'v vs su.

        De analyse wordt automatisch uitgevoerd als deze nog niet is gedaan.
        """
        self.figure_sv_su = go.Figure()
        self.set_figure_sv_su_sutabel(plot_extra_dataset)
        self.figure_sv_su.show()

    def save_fig_html(self, path: str, fig: go.Figure, export_name: Optional[str] = None):
        """
        Slaat de visualisatie van de analyseresultaten op als een HTML-bestand.

        N.B. als de figuur leeg is, roep dan eerst show_figure_...() aan om de figuur te genereren.
        Kies uit show_figure_ln_sv_ln_su_sutabel() of show_figure_sv_su_sutabel().

        Parameters
        ----------
        path: str
            Pad naar de map waar het bestand opgeslagen moet worden
        fig: go.Figure
            De Plotly-figuur die moet worden opgeslagen
        export_name : str, optioneel
            Naam van het HTML-bestand
        """
        if export_name is None:
            export_name = f"sutabel_analyse_{self.investigation_groups[0].replace(' ', '_')}.html"
        file_path = Path(path) / export_name
        fig.write_html(file_path)

    def save_figs_html(self, path: str, export_name: Optional[str] = None):
        """Slaat alle figuren op als afzonderlijke HTML-bestanden in de opgegeven map."""
        fig_info = [(self.figure_sv_su, 'sv_su'),
                    (self.figure_ln_sv_ln_su, 'ln_sv_ln_su')]
        for fig, naam in fig_info:
            file_name = f"{export_name}_{naam}.html" if export_name \
                else f"SU_{naam}_{self.investigation_groups[0].replace(' ', '_')}.html"
            self.save_fig_html(fig=fig, path=path, export_name=file_name)
        print(f"Figuren opgeslagen als HTML in: {path}")

    def add_results_to_template(self, path: str, export_name: str = 'Template_PVtool5_0.xlsx'):
        """
        Voegt de sutabel-m analyseresultaten toe aan het templateExcel-bestand.

        De analyse wordt automatisch uitgevoerd als deze nog niet is gedaan.

        Parameters
        ----------
        path: str
            Pad naar de map waar het Excel-bestand staat
        export_name: str
            Naam van het Excel-bestand

        Returns
        -------
        DataFrame
            Bijgewerkte DataFrame met alle resultaten
        """
        # Voer analyse uit als nog niet gedaan
        if self.sutabel_data_df is None or self.e_a1_sutabel is None:
            self._run_sutabel()
            # Zorg dat parameters zijn berekend
            if self.e_a1_sutabel is None:
                self.get_sutabel_parameters()

        from pv_tool.sutabel_analysis.save_and_export import add_results_to_template
        return add_results_to_template(self, path, export_name)

    def save_to_pdf(self, path: str, vc_fit_kar: float = None) -> str:
        """
        Slaat de sutabel-m analyseresultaten op in een PDF-document.

        De analyse wordt automatisch uitgevoerd als deze nog niet is gedaan.

        Parameters
        ----------
        path: str
            Map locatie waar het PDF-bestand moet worden opgeslagen
        vc_fit_kar : float, optioneel
            Coefficient of Variation voor de fit

        Returns
        -------
        str
            Het absolute bestandspad van het aangemaakte PDF-bestand
        """
        # Voer analyse uit als nog niet gedaan
        if self.sutabel_data_df is None or self.e_a1_sutabel is None:
            self._run_sutabel()
            # Zorg dat parameters zijn berekend
            if self.e_a1_sutabel is None:
                self.get_sutabel_parameters(vc_fit_kar_sutabel=vc_fit_kar)

        from pv_tool.sutabel_analysis.save_and_export import save_sutabel_to_pdf
        return save_sutabel_to_pdf(self, path, vc_fit_kar)
