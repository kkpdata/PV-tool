import os.path
import unittest
from pv_tool.imports.import_data import Dbase
from utils import get_repo_root, make_temp_folder
from pathlib import Path
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse

FILE_PATH = os.path.join(get_repo_root(), "test_files")


def test_cphi_txt_analyse() -> bool:
    """Test implemented. Do not change input."""
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
    dbase.import_data(source="Dbase", source_dir=source_dir)

    # test settings
    investigation_groups = ['TXT_SAFE_klei_licht_16_175']
    effective_stress = '15% rek'
    analysis_type = 'TXT_CPhi'

    analyse = CPhiAnalyse(
        dbase=dbase,
        investigation_groups=investigation_groups,
        effective_stress=effective_stress,
        analysis_type=analysis_type
    )
    analyse.print_short_results()
    return True


# TODO: test apply_parameter, show_figure, safe_to_pdf

def test_cphi_dss_analyse() -> bool:
    """Test implemented. Do not change input."""
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
    dbase.import_data(source="Dbase", source_dir=source_dir)

    # test settings
    investigation_groups = ['TXT_SAFE_klei_licht_16_175']
    effective_stress = '20% rek'
    analysis_type = 'DSS_CPhi'

    analyse = CPhiAnalyse(
        dbase=dbase,
        investigation_groups=investigation_groups,
        effective_stress=effective_stress,
        analysis_type=analysis_type
    )
    analyse.print_short_results()
    return True


class TestImportAndValidate(unittest.TestCase):

    def test_cphi_txt(self):
        self.assertTrue(test_cphi_txt_analyse())


if __name__ == "__main__":
    if __name__ == '__main__':
        unittest.main()
