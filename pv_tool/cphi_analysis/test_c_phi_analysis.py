import os.path
import unittest
from pv_tool.imports.import_data import Dbase
from utils import get_repo_root, make_temp_folder
from pathlib import Path
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
import shutil

FILE_PATH = os.path.join(get_repo_root(), "test_files")
repo_root = get_repo_root()
export_dir = make_temp_folder(
    parent_folder=os.path.join(repo_root, "temp_exports"), add_microseconds=True
)
export_dir = Path(export_dir)


def test_cphi_analyse():
    """Test implemented. Do not change input."""
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
    dbase.import_data(source="Dbase", source_dir=source_dir)
    dbase.export_dbase_to_template(export_dir=export_dir)

    # Initialize analysis
    analysis_types = ['TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH']
    for analysis_type in analysis_types:
        analyse = CPhiAnalyse(
            dbase=dbase,
            investigation_groups=['TXT_SAFE_klei_licht_16_175'],
            effective_stress='15% rek',
            analysis_type=analysis_type
        )
        # apply settings
        analyse.apply_settings(alpha=0.75)
        # apply parameters
        analyse.apply_parameters(cohesie_gem=8.0, phi_kar=0.53, cohesie_kar=6.72)
        # print results
        analyse.print_short_results()
        # exports
        analyse.add_results_to_template(path=export_dir)
        analyse.save_to_pdf(path=export_dir)
        # plot
        analyse.show_figure()
    # remove temp_folder
    # shutil.rmtree(export_dir)
    return True


class TestImportAndValidate(unittest.TestCase):

    def test_cphi_analyse(self):
        self.assertTrue(test_cphi_analyse())
