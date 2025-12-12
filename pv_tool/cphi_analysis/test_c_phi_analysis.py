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
    parent_folder=os.path.join(repo_root), add_microseconds=True
)
export_dir = Path(export_dir)


def test_cphi_analyse():
    """Test implemented. Do not change input."""
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
    dbase.import_data(source="Dbase", source_dir=source_dir)
    dbase.export_dbase_to_excel(export_dir=export_dir)

    # Initialize analysis
    analysis_types = ['TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH']
    for analysis_type in analysis_types:
        analyse = CPhiAnalyse(
            dbase=dbase,
            investigation_groups=['TXT_SAFE_klei_licht_16_175'],
            effective_stress='15% rek',
            analysis_type=analysis_type
        )

        if analysis_type == 'TXT_CPhi':
            # apply settings
            analyse.apply_settings(alpha=0.75)
            # apply parameters
            analyse.apply_parameters(cohesie_gem=8.0, phi_kar=0.53, cohesie_kar=6.72)
            # print results
            analyse.print_short_results()
            # exports
            file_name = 'Template_PVtool5_0.xlsx'
            analyse.add_results_to_dbase(path=export_dir, file_name=file_name)
            analyse.save_to_pdf(path=export_dir)

    # remove temp_folder
    shutil.rmtree(export_dir)
    return True


class TestImportAndValidate(unittest.TestCase):

    def test_import_stowa_data(self):
        self.assertTrue(test_cphi_analyse())
