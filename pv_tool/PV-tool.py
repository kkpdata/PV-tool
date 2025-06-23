# Hier komt alle functies in die we in de notebook gaan draaien

from pv_tool.importeren import Dbase
from pv_tool.analyse_c_phi import CPhi

from pathlib import Path


class PVTool:

    def __init__(self):
        self.dbase: Dbase = Dbase()
        self.c_phi: CPhi = CPhi()

    def import_stowa(self, stowa_dir: Path):
        self.dbase.import_stowa(stowa_dir=stowa_dir)

    def import_pv_tool(self, pv_dir: Path):
        self.dbase.import_pv_tool(pv_dir=pv_dir)

    def c_phi_plot(self, investigation_groups: list[str]):
        self.c_phi.c_phi_plot(investigation_groups=investigation_groups)




