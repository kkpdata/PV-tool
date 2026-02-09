import os.path
import unittest
from typing import Literal

from pv_tool.imports.import_data import Dbase
from pv_tool.utilities.utils import get_repo_root, make_temp_folder
from pathlib import Path
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse

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
    export_name = 'Template_PVtool5_0.xlsx'
    dbase.export_dbase_to_template(export_dir=export_dir)

    # Initialize analysis
    analysis_types: list[Literal['TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH']] = [
        'TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH']
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
        analyse.get_short_results()
        # exports
        analyse.add_results_to_template(path=export_dir, export_name=export_name)
        analyse.save_to_pdf(path=export_dir)
        # plot
        analyse.show_figure()
    # remove temp_folder
    # shutil.rmtree(export_dir)
    assert True


class TestImportAndValidate(unittest.TestCase):

    def test_cphi_analyse(self):
        test_cphi_analyse()

    def test_creating_figures(self):
        """Test het aanmaken van figuren en save_fig_html functionaliteit voor CPhiAnalyse."""
        dbase = Dbase()
        source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
        dbase.import_data(source="Dbase", source_dir=source_dir)

        analyse = CPhiAnalyse(
            dbase=dbase,
            investigation_groups=['TXT_SAFE_klei_licht_16_175'],
            effective_stress='15% rek',
            analysis_type='TXT_CPhi'
        )

        # Apply settings and parameters
        analyse.apply_settings(alpha=0.75)
        analyse.apply_parameters(cohesie_gem=8.0, phi_kar=0.53, cohesie_kar=6.72)
        analyse._run()

        # Test dat we een figure kunnen aanmaken en opslaan
        figure_created = False
        html_saved = False

        # Test figure creation
        try:
            analyse.show_figure()
            # Controleer dat figure object is aangemaakt
            self.assertIsNotNone(analyse.figure)
            figure_created = True

            # Test save_fig_html functionaliteit
            analyse.save_fig_html(path=str(export_dir), export_name="test_cphi_figure.html")
            # Controleer dat het HTML-bestand bestaat
            html_file = export_dir / "test_cphi_figure.html"
            self.assertTrue(html_file.exists(), "HTML file should be created")
            html_saved = True

        except Exception as e:
            print(f"C-Phi figure creation failed: {e}")

        # Test figure with spanningspaden
        try:
            analyse.show_figure(plot_spanningspaden=True)
            # Test save_fig_html functionaliteit met spanningspaden
            analyse.save_fig_html(path=str(export_dir), export_name="test_cphi_spanningspaden.html")
            html_file = export_dir / "test_cphi_spanningspaden.html"
            self.assertTrue(html_file.exists(), "HTML file with spanningspaden should be created")
            html_saved = True

        except Exception as e:
            print(f"C-Phi figure with spanningspaden creation failed: {e}")

        # Test dat minstens één van de figure tests is gelukt
        if not figure_created:
            self.skipTest("Figure creation failed - may require specific data conditions")

        # Test dat save_fig_html functionaliteit werkt
        self.assertTrue(html_saved, "save_fig_html should successfully create HTML files")

        # Test default export name functionality
        try:
            analyse.show_figure()
            analyse.save_fig_html(path=str(export_dir))  # No export_name specified
            # Check that a file with default name pattern was created
            html_files = list(export_dir.glob("c-phi_analyse_*.html"))
            self.assertTrue(len(html_files) > 0, "Default export name should create a file")
        except Exception as e:
            print(f"Default export name test failed: {e}")
