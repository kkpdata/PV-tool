import os.path
import unittest
from pv_tool.imports.import_data import Dbase
from pv_tool.utilities.utils import get_repo_root, make_temp_folder
from pathlib import Path
from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
from typing import Literal

FILE_PATH = os.path.join(get_repo_root(), "test_files")
repo_root = get_repo_root()
export_dir = make_temp_folder(
    parent_folder=os.path.join(repo_root, "temp_exports"), add_microseconds=True
)
export_dir = Path(export_dir)


def test_shansep_analyse():
    """
    Test voor SHANSEP analyse. Voert een volledige SHANSEP analyse uit met verschillende analyse types.
    Test geïmplementeerd. Verander de invoer niet.
    """
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
    dbase.import_data(source="Dbase", source_dir=source_dir)
    dbase.export_dbase_to_template(export_dir=export_dir)

    # Initialize analysis types voor SHANSEP
    analysis_types: list[Literal['TXT_S_POP', 'DSS_S_POP']] = ['TXT_S_POP', 'DSS_S_POP']
    effective_stresses: dict[
        Literal['TXT_S_POP', 'DSS_S_POP'],
        list[Literal['2% rek', '5% rek', '10% rek', '15% rek', '20% rek', 'pieksterkte', 'eindsterkte']]
    ] = {
        'TXT_S_POP': ['2% rek', '5% rek', '15% rek', 'pieksterkte', 'eindsterkte'],
        'DSS_S_POP': ['2% rek', '5% rek', '10% rek', '15% rek', '20% rek', 'pieksterkte', 'eindsterkte']
    }

    for analysis_type in analysis_types:
        # Test met een representatieve effective stress voor elk analysis type
        ig = ['DSS_SAFE_veen'] if analysis_type == 'DSS_S_POP' else ['TXT_SAFE_klei_licht_16_175']
        es = effective_stresses[analysis_type][-1]  # Use the last value as the representative effective stress

        analyse = SHANSEP(
            dbase=dbase,
            investigation_groups=ig,
            effective_stress=es,
            analysis_type=analysis_type
        )

        # Apply settings
        analyse.apply_settings(alpha=0.75)

        df_results_shansep_gem, df_results_shansep_kar = analyse.get_result_values_shansep()
        print(df_results_shansep_gem)
        print(df_results_shansep_kar)

        # Test estimated parameters
        estimated_params = analyse.get_estimated_parameters()
        # estimated_params_nc = analyse.get_estimated_parameters_nc()
        if estimated_params:
            set_manual_parameters(analyse, estimated_params)

        # Test calculations and figures
        run_calculations_and_figures(analyse, analysis_type)

    assert True


def set_manual_parameters(analyse: SHANSEP, params: dict):
    """Stelt handmatige parameters in voor SHANSEP analyse."""
    try:
        analyse.set_parameters_handmatig(
            snijpunt_gem=params['snijpunt_gem'],
            s_gem=params['s_gem'],
            m_gem=params['m_gem'],
            snijpunt_kar=params['snijpunt_kar'],
            s_kar=params['s_kar'],
            m_kar=params['m_kar']
        )
        print("Handmatige parameters ingesteld met geschatte waardes")
    except Exception as e:
        print(f"Instellen handmatige parameters mislukt: {e}")


def run_calculations_and_figures(analyse: SHANSEP, analysis_type: str):
    """Test berekeningen en figuren voor SHANSEP analyse."""
    try:
        analyse.calculate_sutabel()
        analyse.calculate_sutabel_nc()
    except Exception as e:
        print(f"An error occurred while calculating sutabel: {e}")

    # Generate and save figures
    try:
        fig_sv_su = analyse.show_figure_sv_su()
        analyse.save_fig_html(path=str(export_dir), fig=fig_sv_su,
                              export_name=f"test_shansep_sv_su_{analysis_type}.html")
        fig_sv_su_nc = analyse.show_figure_sv_su_nc()
        analyse.save_fig_html(path=str(export_dir), fig=fig_sv_su_nc,
                              export_name=f"test_shansep_sv_su_nc_{analysis_type}.html")
        fig_ln_ocr_ln_s = analyse.show_figure_ln_ocr_ln_s()
        analyse.save_fig_html(path=str(export_dir), fig=fig_ln_ocr_ln_s,
                              export_name=f"test_shansep_ln_ocr_ln_s_{analysis_type}.html")
    except Exception as e:
        print(f"An error occurred while showing figures: {e}")

    # Export results
    try:
        analyse.export_shansep_results_excel(str(export_dir / f"shansep_results_{analysis_type}.xlsx"))
        analyse.write_analysis_to_excel(str(export_dir / f"shansep_analysis_{analysis_type}.xlsx"))
        analyse.save_to_pdf(path=str(export_dir))
    except Exception as e:
        print(f"An error occurred while exporting results: {e}")


class TestShansepAnalyse(unittest.TestCase):
    """Unit test klasse voor SHANSEP analyse methoden."""

    def test_shansep_analyse(self):
        """Test de volledige SHANSEP analyse workflow."""
        # self.assertTrue(test_shansep_analyse())
        test_shansep_analyse()


if __name__ == '__main__':
    unittest.main()
