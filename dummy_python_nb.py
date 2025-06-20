
from pv_tool import PVTool
from typing import Optional

pv_tool = PVTool()
pv_tool.import_stowa_db(path=...)
# pv_tool.dbase = DBase(path_to_stowa_file)

# Analyse
pv_tool.analyse_cphi_txt(investigation_group=None, show_graph=True)
pv_tool.analyse_cphi_txt(investigation_groups=["klei_licht"], background_groups=["klei_zwaar"], show_graph=True)

pv_tool.alter_pv_naam(monsters=[23, 24, 25], new_group="klei_licht_dijk")
pv_tool.alter_pv_naam(monsters=[26, 27, 28], new_group="klei_licht_al")
# indien PV_naam wordt aangepast moeten verschillende ana_kolommen ook worden geupdate

# Display groups
pv_tool.show_pv_naam_table()

pv_tool.analyse_cphi_txt(
    investigation_groups=["klei_licht_dijk", "klei_licht_al"],
    background_groups=["klei_zwaar"], show_graph=True,
    fit_parameter_a=..., #optional
    fit_parameter_b=..., #optional,
)
pv_tool.analyse_cphi_txt(
    investigation_groups=["klei_licht_dijk", "klei_licht_al"],
    background_groups=["klei_zwaar"], show_graph=True,
    fit_parameter_a=0.5, #optional
    fit_parameter_b=0.9, #optional
    save=True,
)

pv_tool.export_factsheet()





#
# class PVTool:
#
#     def generate_graph_cphi(self, create_new_group_from_subset: Optional[str] = None):
#
#         # code graphs
#
#         if create_new_group_from_subset:
#             self.create_new_group()

