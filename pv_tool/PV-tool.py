from pv_tool.imports.import_data import Dbase
from pv_tool.analysis.c_phi_analysis import CPhiAnalyse
from typing import Literal
from pathlib import Path


class PVTool:

    def __init__(self):
        self.dbase: Dbase = Dbase()
        self.analysis_type = []
        self.effective_stress = []
        self.investigation_groups = []
        self.c_phi: CPhiAnalyse = CPhiAnalyse(dbase=self.dbase, analysis_type=self.analysis_type,
                                              effective_stress=self.effective_stress,
                                              investigation_groups=self.investigation_groups)

    def import_data_and_validate(self, source: Literal['Stowa', 'PV-tool', 'Dbase'],
                                 source_dir: Path, export_path: Path):
        self.dbase.import_data_and_validate(source=source, source_dir=source_dir, export_path=export_path)

    def export_dbase_to_excel(self, export_dir: Path, filename: str = 'Dbase-template.xlsx'):
        self.dbase.export_dbase_to_excel(export_dir=export_dir, filename=filename)

    def show_figure(self):
        self.c_phi.show_figure()

    def show_factsheet(self):
        self.c_phi.factsheet()

