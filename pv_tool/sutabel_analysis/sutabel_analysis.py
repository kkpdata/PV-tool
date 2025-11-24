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
from pv_tool.shansep_analysis.calc_parameters import (
    calc_watergehalte_gem_txt, calc_watergehalte_gem_dss,
    calc_watergehalte_sd_txt, calc_watergehalte_sd_dss,
    calc_vgwnat_gem_txt, calc_vgwnat_gem_dss,
    calc_vgwnat_sd_txt, calc_vgwnat_sd_dss
)


class SUTABEL:
    """
    Klasse voor het uitvoeren van sutabel-m analyses.

    De sutabel-m methode analyseert overgeconsolideerde (OC) triaxiaal of DSS proeven
    om parameters te bepalen voor het berekenen van ongedraineerde schuifsterkte.

    Attributes
    ----------
    dbase : Dbase
        Database object met proefgegevens
    analysis_type : str
        Type analyse ('TXT_su_tabel' of 'DSS_su_tabel')
    investigation_groups : List[str]
        Lijst met te analyseren proevenverzamelingen
    effective_stress : str
        Effectieve spanning niveau (bijv. '15% rek')
    alpha : float
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
    CV_fit_kar_sutabel : float
        Coefficient of Variation voor fit (user input)
    STDEV_logn_CV_sutabel : float
        sqrt(LN(1 + CV^2)) - standaarddeviatie lognormaal
    steyx_sutabel : float
        Standaardfout van de schatting
    """

    def __init__(self,
                 dbase: Dbase,
                 analysis_type: Literal['TXT_su_tabel', 'DSS_su_tabel'],
                 investigation_groups: List[str],
                 effective_stress: str,
                 alpha: float = 0.75):
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
        alpha : float, optional
            Type verzameling (1.0 = lokaal, 0.75 = regionaal), default 0.75
        """
        self.dbase = dbase
        self.dbase_df: DataFrame = dbase.df_database
        self.analysis_type = analysis_type
        self.investigation_groups = investigation_groups
        self.effective_stress = effective_stress
        self.alpha = alpha
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
        self.m_gem_sutabel: Optional[float] = None     # 1 - e_a2
        self.svgm_kar_sutabel: Optional[float] = None  # exp(a1_kar)
        self.m_kar_sutabel: Optional[float] = None     # 1 - a2_kar
        self.CV_fit_kar_sutabel: Optional[float] = None  # User input
        self.STDEV_logn_CV_sutabel: Optional[float] = None  # sqrt(LN(1 + CV^2))

        # Dataframes
        self.shansep_data_df: Optional[DataFrame] = None
        self.total_shansep_data_df: Optional[DataFrame] = None
        self.shansep_data_df_sutabel: Optional[DataFrame] = None
        self.sutabel_grafiek: Optional[DataFrame] = None
        self.su_fit_constante_CV: Optional[DataFrame] = None

        # Figure voor plotly
        self.figure: Optional[go.Figure] = None

    def get_shansep_data(self):
        """
        Haalt de relevante proefgegevens op uit de database.

        Filtert de database op basis van:
        - Analysis type (TXT of DSS)
        - Investigation groups (PV_NAAM)
        - Effective stress niveau

        Maakt self.shansep_data_df en self.total_shansep_data_df aan.
        """
        # Filter op analysis type
        if self.analysis_type == 'TXT_su_tabel':
            dataset_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
        elif self.analysis_type == 'DSS_su_tabel':
            dataset_df = self.dbase_df[self.dbase_df['ALG__DSS']]
        else:
            raise ValueError(f"Onbekend analysis type: {self.analysis_type}")

        # Filter op investigation groups
        dataset_df = dataset_df[dataset_df['PV_NAAM'].isin(self.investigation_groups)]

        # Store complete dataset
        self.total_shansep_data_df = dataset_df.copy()

        # Filter op effective stress
        if self.analysis_type.startswith('DSS'):
            dataset_df = dataset_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])]
        else:
            dataset_df = dataset_df[TEXTUAL_NAMES.get(self.effective_stress, [])]

        # Hernoem kolommen
        dataset_df.columns = NEW_COLUMN_NAMES

        # Bereken algemene parameters
        from pv_tool.shansep_analysis.expand_analysis import (
            calculate_ln_ocr, calculate_sv_spop, calculate_ln_sv_spop, calculate_pop
        )

        self.shansep_data_df = dataset_df.copy()
        calculate_ln_ocr(self)
        calculate_sv_spop(self)
        calculate_ln_sv_spop(self)
        calculate_pop(self)

        # Bereken watergehalte en volumegewicht
        if self.analysis_type.startswith('TXT'):
            self.calc_watergehalte_gem = calc_watergehalte_gem_txt(self)
            self.calc_watergehalte_sd = calc_watergehalte_sd_txt(self)
            self.calc_vgwnat_gem = calc_vgwnat_gem_txt(self)
            self.calc_vgwnat_sd = calc_vgwnat_sd_txt(self)
        else:
            self.calc_watergehalte_gem = calc_watergehalte_gem_dss(self)
            self.calc_watergehalte_sd = calc_watergehalte_sd_dss(self)
            self.calc_vgwnat_gem = calc_vgwnat_gem_dss(self)
            self.calc_vgwnat_sd = calc_vgwnat_sd_dss(self)

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
        from pv_tool.shansep_analysis.expand_analysis import (
            calculate_ln_sv_sutabel, calculate_ln_su_sutabel,
            calculate_sv_tt_sutabel, calculate_sv_ty_sutabel,
            calculate_chi_2_sutabel, calculate_sv_eff_sutabel,
            calculate_5pr_ondergrens_sutabel, calculate_5pr_bovengrens_sutabel,
            calculate_sv_tt_ondergrens_sutabel, calculate_sv_ty_ondergrens_sutabel,
            calculate_chi_2_ondergrens_sutabel
        )

        # Filter op alleen OC proeven
        self.shansep_data_df_sutabel = self.shansep_data_df[
            self.shansep_data_df['consolidatietype'] == 'OC'
        ].copy()

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

    def get_sutabel_parameters(self, CV_fit_kar_sutabel: Optional[float] = None):
        """
        Berekent de sutabel-m parameters.

        Parameters
        ----------
        CV_fit_kar_sutabel : float, optioneel
            Coefficient of Variation voor sutabel fit (user input)
        """
        from pv_tool.shansep_analysis.variables import (
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

        # Sla CV_fit_kar op (kan None zijn als niet opgegeven)
        if CV_fit_kar_sutabel is not None:
            self.CV_fit_kar_sutabel = CV_fit_kar_sutabel
            self.STDEV_logn_CV_sutabel = math.sqrt(math.log(1 + (self.CV_fit_kar_sutabel ** 2)))
        else:
            self.CV_fit_kar_sutabel = None
            self.STDEV_logn_CV_sutabel = None

    def calculate_sutabel_grafiek(self):
        """
        Berekent de dataframes voor sutabel grafiek lijnen.

        Maakt twee dataframes:
        - sutabel_grafiek: bevat su_gem en su_kar lijnen
        - su_fit_constante_CV: bevat su_kar fit met constante CV lijn
        """
        import numpy as np
        from scipy.stats import lognorm

        # Bepaal s'v waarden voor de grafiek
        max_sv = self.shansep_data_df_sutabel['S\'v'].max()
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

        # Als CV_fit_kar is opgegeven, bereken ook de constante CV fit
        if self.CV_fit_kar_sutabel is not None and self.STDEV_logn_CV_sutabel is not None:
            # Bereken ln waarden
            ln_su_gem = [math.log(su) - 0.5 * (self.STDEV_logn_CV_sutabel ** 2) for su in su_gem_values]
            ln_su_kar = [math.log(su) - 0.5 * (self.STDEV_logn_CV_sutabel ** 2) for su in su_kar_values]

            # Bereken su_kar fit met constante CV
            su_kar_fit_cv = [lognorm.ppf(0.05, s=self.STDEV_logn_CV_sutabel, scale=math.exp(ln))
                             for ln in ln_su_gem]

            self.su_fit_constante_CV = DataFrame({
                "s'v [kPa]": sv_values,
                "ln(su_gem) [kPa]": ln_su_gem,
                "ln(su_kar) [kPa]": ln_su_kar,
                "su_kar fit met constante CV [kPa]": su_kar_fit_cv
            })
        else:
            self.su_fit_constante_CV = None

    def _run_sutabel(self):
        """
        Voert de volledige sutabel analyse uit in de juiste volgorde.
        """
        self.get_shansep_data()
        self.expand_analysis_df_sutabel()
        self.get_sutabel_parameters()

    def write_analysis_to_excel(self, file_path: str):
        """
        Schrijft de analyse dataframes naar een Excel-bestand.

        Parameters
        ----------
        file_path : str
            Pad naar de map waar het Excel-bestand moet worden opgeslagen plus de bestandsnaam
        """
        with ExcelWriter(file_path) as writer:
            if self.shansep_data_df is not None:
                self.shansep_data_df.to_excel(writer, sheet_name='Data', index=False)
            if self.shansep_data_df_sutabel is not None:
                self.shansep_data_df_sutabel.to_excel(writer, sheet_name='Sutabel Data', index=False)
            if self.sutabel_grafiek is not None:
                self.sutabel_grafiek.to_excel(writer, sheet_name='Sutabel Grafiek', index=False)
            if self.su_fit_constante_CV is not None:
                self.su_fit_constante_CV.to_excel(writer, sheet_name='CV Fit', index=False)

    # ========== Visualization Methods ==========

    def set_figure_ln_sv_ln_su_sutabel(self):
        """
        Maakt een visualisatie van de sutabel analyseresultaten voor ln(s'v) vs ln(su).

        Deze plot toont:
        - Proefresultaten (OC data)
        - Lineaire fit
        - 5% boven- en ondergrens
        - Fysische realiseerbare ondergrens (gebaseerd op a1_kar en a2_kar)
        """
        from pv_tool.shansep_analysis.visualization_shansep import (
            add_proefresultaten_ln_sv_ln_su_sutabel,
            add_lineair_fit_ln_sv_ln_su_sutabel,
            add_5pr_bovengrens_ln_sv_ln_su_sutabel,
            add_5pr_ondergrens_ln_sv_ln_su_sutabel,
            add_fysische_realiseerbare_ondergrens_ln_sv_ln_su_sutabel,
            set_layout_ln_sv_ln_su_sutabel
        )

        self._run_sutabel()
        add_proefresultaten_ln_sv_ln_su_sutabel(self)
        add_lineair_fit_ln_sv_ln_su_sutabel(self)
        add_5pr_bovengrens_ln_sv_ln_su_sutabel(self)
        add_5pr_ondergrens_ln_sv_ln_su_sutabel(self)
        add_fysische_realiseerbare_ondergrens_ln_sv_ln_su_sutabel(self)
        set_layout_ln_sv_ln_su_sutabel(self)

    def show_figure_ln_sv_ln_su_sutabel(self):
        """
        Toont de visualisatie van de sutabel analyseresultaten voor ln(s'v) vs ln(su).
        """
        self._run_sutabel()
        self.figure = go.Figure()
        self.set_figure_ln_sv_ln_su_sutabel()
        self.figure.show()

    def set_figure_sv_su_sutabel(self):
        """
        Maakt een visualisatie van de sutabel analyseresultaten voor s'v vs su.

        Deze plot toont:
        - Proefresultaten (OC data)
        - Sutabel_gem lijn
        - Sutabel_kar lijn
        - Su_kar fit met constante VC (als CV_fit_kar is opgegeven)
        """
        from pv_tool.shansep_analysis.visualization_shansep import (
            add_proefresultaten_sv_su_sutabel,
            add_sutabel_gem_line,
            add_sutabel_kar_line,
            add_su_kar_fit_constante_vc,
            set_layout_sv_su_sutabel
        )

        self._run_sutabel()

        # Bereken grafiek dataframes
        self.calculate_sutabel_grafiek()

        # Voeg data en lijnen toe
        add_proefresultaten_sv_su_sutabel(self)
        add_sutabel_gem_line(self)
        add_sutabel_kar_line(self)

        # Voeg CV fit lijn toe als deze beschikbaar is
        if self.su_fit_constante_CV is not None:
            add_su_kar_fit_constante_vc(self)

        set_layout_sv_su_sutabel(self)

    def show_figure_sv_su_sutabel(self):
        """
        Toont de visualisatie van de sutabel analyseresultaten voor s'v vs su.
        """
        self._run_sutabel()
        self.figure = go.Figure()
        self.set_figure_sv_su_sutabel()
        self.figure.show()

    # ========== Export Methods ==========

    def add_results_to_dbase(self, path: str, file_name: str = 'Template_PVtool5_0.xlsx'):
        """
        Voegt de sutabel-m analyseresultaten toe aan de database Excel-bestand.

        Parameters
        ----------
        path : str
            Pad naar de map waar het Excel-bestand staat
        file_name : str
            Naam van het Excel-bestand

        Returns
        -------
        DataFrame
            Bijgewerkte DataFrame met alle resultaten
        """
        from pv_tool.shansep_analysis.save_and_export_sutabel import add_sutabel_results_to_dbase
        return add_sutabel_results_to_dbase(self, path, file_name)

    def save_to_pdf(self, path: str, CV_fit_kar: float = None) -> str:
        """
        Slaat de sutabel-m analyseresultaten op in een PDF-document.

        Parameters
        ----------
        path : str
            Map locatie waar het PDF-bestand moet worden opgeslagen
        CV_fit_kar : float, optioneel
            Coefficient of Variation voor de fit

        Returns
        -------
        str
            Het absolute bestandspad van het aangemaakte PDF-bestand
        """
        from pv_tool.shansep_analysis.save_and_export_sutabel import save_sutabel_to_pdf
        return save_sutabel_to_pdf(self, path, CV_fit_kar)

