from pv_tool.imports.import_data import Dbase
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
from typing import Literal, List, Optional
from pathlib import Path

# TODO: dit is voor de toekomst. was voor nu een idee om de notebook overzichtelijker te maken.

class PVTool:
    def __init__(self):
        self.dbase: Dbase = Dbase()
        self.analysis_type: Literal['TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH'] = 'TXT_CPhi'
        self.effective_stress: Literal['2% rek', '5% rek', '15% rek', 'pieksterkte', 'eindsterkte'] = 'eindsterkte'
        self.investigation_groups: List = [None]
        self.c_phi: CPhiAnalyse = CPhiAnalyse(dbase=self.dbase, analysis_type=self.analysis_type,
                                              effective_stress=self.effective_stress,
                                              investigation_groups=self.investigation_groups)

    def import_data_and_validate(self, source: Literal['Stowa', 'PV-tool', 'Dbase'],
                                 source_dir: Path, export_path: Path):
        self.dbase.import_data_and_validate(source=source, source_dir=source_dir, export_path=export_path)

    def export_dbase_to_excel(self, export_dir: Path, filename: str = 'Dbase-template.xlsx'):
        self.dbase.export_dbase_to_excel(export_dir=export_dir, filename=filename)

    def set_analysis_settings(self, analysis_type: Literal['TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH'],
                              effective_stress: Literal['2% rek', '5% rek', '15% rek', 'pieksterkte', 'eindsterkte'],
                              investigation_groups: List):
        self.c_phi.analysis_type = analysis_type
        self.c_phi.effective_stress = effective_stress
        self.c_phi.investigation_groups = investigation_groups

    def apply_parameters(self, cohesie_gem: Optional[float] = None,
                         phi_kar: Optional[float] = None,
                         cohesie_kar: Optional[float] = None):
        self.c_phi.apply_parameters(cohesie_gem=cohesie_gem, phi_kar=phi_kar, cohesie_kar=cohesie_kar)

    def apply_settings(self, alpha: Optional[float] = None,
                       material_factor_cohesion: Optional[float] = None,
                       material_factor_tan_phi: Optional[float] = None):
        self.c_phi.apply_settings(alpha=alpha, material_factor_cohesion=material_factor_cohesion,
                                  material_factor_tan_phi=material_factor_tan_phi)

    def show_figure(self):
        self.c_phi.show_figure()

    def show_results(self):
        self.c_phi.show_results()
