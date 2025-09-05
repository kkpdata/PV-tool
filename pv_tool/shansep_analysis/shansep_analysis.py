from pv_tool.imports.import_data import Dbase
from typing import Optional, List, Literal
from pv_tool.shansep_analysis.globals import (TEXTUAL_NAMES, NEW_COLUMN_NAMES, TEXTUAL_NAMES_DSS)
from pandas import DataFrame, ExcelWriter, concat, read_excel

from pv_tool.shansep_analysis.calc_parameters import (calc_watergehalte_gem, calc_watergehalte_sd, calc_vgwnat_gem,
                                                   calc_vgwnat_sd)

from pv_tool.shansep_analysis.expand_analysis import (calculate_s_tt, calculate_s_sutabel, calculate_pop,
                                                      calculate_s_spop, calculate_ln_ocr, calculate_ln_s_spop,
                                                      calculate_s_ty, calculate_kappa_2,
                                                      calculate_5pr_ondergrens, calculate_5pr_bovengrens,
                                                 calculate_s_tt_ondergrens, calculate_s_ty_ondergrens,
                                                 calculate_kappa_2_ondergrens)

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

        # Placeholder
        self.shansep_analyses_data_df: Optional[DataFrame] = None
        self.total_shansep_analyses_data_df: Optional[DataFrame] = None

        pass

    def get_shansep_data(self):
        """Deze functie filtert de dbase-dataframe op basis van type analyse, PV_NAAM en de gewenste effectieve stress.
        Daarnaast worden de kolomnamen aangepast zodat ze ongeacht het rekpercentage allemaal dezelfde kolomnaam hebben.
        """
        if self.analysis_type in ['TXT_S_POP', 'TXT_su_tabel']:
            self.shansep_analyses_data_df = self.dbase_df[self.dbase_df['ALG__TRIAXIAAL']]
            self.shansep_analyses_data_df = self.shansep_analyses_data_df[self.shansep_analyses_data_df['PV_NAAM'].isin(
                    self.investigation_groups)]
            self.calc_watergehalte_gem = calc_watergehalte_gem(self)
            self.calc_watergehalte_sd = calc_watergehalte_sd(self)
            self.calc_vgwnat_gem = calc_vgwnat_gem(self)
            self.calc_vgwnat_sd = calc_vgwnat_sd(self)
            self.total_shansep_analyses_data_df = self.shansep_analyses_data_df
            self.shansep_analyses_data_df = self.shansep_analyses_data_df[TEXTUAL_NAMES.get(self.effective_stress, [])]

        elif self.analysis_type in ['DSS_S_POP', 'DSS_su_tabel']:
            self.shansep_analyses_data_df = self.dbase_df[self.dbase_df['ALG__DSS']]
            self.shansep_analyses_data_df = self.shansep_analyses_data_df[self.shansep_analyses_data_df['PV_NAAM'].isin(
                    self.investigation_groups)]
            self.calc_watergehalte_gem = calc_watergehalte_gem(self)
            self.calc_watergehalte_sd = calc_watergehalte_sd(self)
            self.calc_vgwnat_gem = calc_vgwnat_gem(self)
            self.calc_vgwnat_sd = calc_vgwnat_sd(self)
            self.total_shansep_analyses_data_df = self.shansep_analyses_data_df
            self.shansep_analyses_data_df = self.shansep_analyses_data_df[TEXTUAL_NAMES_DSS.get(self.effective_stress, [])]

        self.shansep_analyses_data_df.columns = NEW_COLUMN_NAMES

    def apply_settings(self, alpha: Optional[float] = None):
        """Met deze functie kan je de alpha en materiaalfactoren opgeven."""
        self.alpha = alpha if alpha is not None else self.alpha


    def expand_analysis_df_sutabel(self):
        """Deze functie berekent alle benodigde parameters per monster voor de analyse."""
        calculate_s_tt(self)
        calculate_s_ty(self)
        calculate_kappa_2(self)
        calculate_s_sutabel(self)
        calculate_5pr_ondergrens(self)
        calculate_5pr_bovengrens(self)
        calculate_s_tt_ondergrens(self)
        calculate_s_ty_ondergrens(self)
        calculate_kappa_2_ondergrens(self)

    def expand_analysis_df_s_pop(self):
        """Deze functie berekent alle benodigde parameters per monster voor de analyse."""
        calculate_ln_ocr(self)
        calculate_s_spop(self)
        calculate_ln_s_spop(self)
        calculate_pop(self)
        # TODO nog toevoegen 'alleen op OC' of 'OC en NC'
        calculate_s_tt(self)
        calculate_s_ty(self)
        calculate_kappa_2(self)
        calculate_s_sutabel(self)
        calculate_5pr_ondergrens(self)
        calculate_5pr_bovengrens(self)
        calculate_s_tt_ondergrens(self)
        calculate_s_ty_ondergrens(self)
        calculate_kappa_2_ondergrens(self)