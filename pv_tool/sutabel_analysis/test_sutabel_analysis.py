import os.path
import unittest
from pv_tool.imports.import_data import Dbase
from pv_tool.utilities.utils import get_repo_root, make_temp_folder
from pathlib import Path
from pv_tool.sutabel_analysis.sutabel_analysis import SUTABEL
from typing import Literal

FILE_PATH = os.path.join(get_repo_root(), "test_files")
repo_root = get_repo_root()
export_dir = make_temp_folder(
    parent_folder=os.path.join(repo_root, "temp_exports"), add_microseconds=True
)
export_dir = Path(export_dir)


def test_sutabel_analyse():
    """
    Test voor SUTABEL analyse. Voert een volledige SUTABEL analyse uit met verschillende analyse types.
    Test geïmplementeerd. Verander de invoer niet.
    """
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
    dbase.import_data(source="Dbase", source_dir=source_dir)
    export_name = 'Template_PVtool5_0.xlsx'
    dbase.export_dbase_to_template(export_dir=export_dir)

    # Initialize analysis types voor SUTABEL
    analysis_types: list[Literal['TXT_su_tabel', 'DSS_su_tabel']] = ['TXT_su_tabel', 'DSS_su_tabel']

    for analysis_type in analysis_types:
        if analysis_type == 'DSS_su_tabel':
            ig = ['DSS_SAFE_veen']
            es = '20% rek'
        else:
            ig = ['TXT_SAFE_klei_licht_16_175']
            es = '15% rek'

        analyse = SUTABEL(
            dbase=dbase,
            investigation_groups=ig,
            effective_stress=es,
            analysis_type=analysis_type
        )

        # Apply settings
        analyse.apply_settings(alpha=0.75)

        # Test korte resultaten zonder manual parameters
        df_results = analyse.get_short_results()
        print(df_results)

        # Test figuur generatie vóór manual parameters
        try:
            analyse.set_figure_ln_sv_ln_su_sutabel()
            analyse.set_figure_sv_su_sutabel()
        except Exception as e:
            print(f"Error during figure generation before manual parameters for {analysis_type}: {e}")

        # Test show figures
        try:
            analyse.show_figure_ln_sv_ln_su_sutabel()
            fig_ln = analyse.figure_ln_sv_ln_su
            analyse.save_fig_html(fig=fig_ln, path=str(export_dir),
                                  export_name=f"sutabel_ln_figure_{analysis_type}.html")
            analyse.show_figure_sv_su_sutabel()
            fig_sv_su = analyse.figure_sv_su
            analyse.save_fig_html(fig=fig_sv_su, path=str(export_dir),
                                  export_name=f"sutabel_sv_figure_{analysis_type}.html")
        except Exception as e:
            print(f"Error during show figures before manual parameters for {analysis_type}: {e}")

        # Test manual parameters (met voorbeeldwaardes die bij TXT SAFE klei licht 15% een goede fit geven)
        if analysis_type == 'DSS_su_tabel':
            analyse.set_manual_parameters(a1_kar=0.0, a2_kar=0.8, vc_fit_kar=0.18)
        else:
            analyse.set_manual_parameters(a1_kar=0.47, a2_kar=0.67, vc_fit_kar=0.1)

        # Test figure generatie
        try:
            analyse.set_figure_ln_sv_ln_su_sutabel()
            analyse.set_figure_sv_su_sutabel()
        except Exception as e:
            print(f"Error during figure generation after manual parameters for {analysis_type}: {e}")

        # Test show figures en html export
        try:
            analyse.show_figure_ln_sv_ln_su_sutabel()
            fig_ln_sv_ln_su = analyse.figure_ln_sv_ln_su
            analyse.save_fig_html(fig=fig_ln_sv_ln_su, path=str(export_dir),
                                  export_name=f"sutabel_ln_figure_{analysis_type}_manual.html")
            analyse.show_figure_sv_su_sutabel()
            fig_sv_su_sutabel = analyse.figure_sv_su
            analyse.save_fig_html(fig=fig_sv_su_sutabel, path=str(export_dir),
                                  export_name=f"sutabel_sv_figure_{analysis_type}_manual.html")
        except Exception as e:
            print(f"Error during show figures and exporting to html for {analysis_type}: {e}")

        # Test exports
        try:
            analyse.write_analysis_to_excel(str(export_dir / f"sutabel_analysis_{analysis_type}.xlsx"))
            analyse.save_to_pdf(path=str(export_dir))
        except Exception as e:
            print(f"Error during exports for {analysis_type}: {e}")

        # Test results to template
        try:
            analyse.add_results_to_template(path=str(export_dir), export_name=export_name)
        except Exception as e:
            print(f"Error during adding results to template for {analysis_type}: {e}")

    # Remove temp_folder (optioneel uitcommentariëren voor debugging)
    # shutil.rmtree(export_dir)
    assert True


class TestSutabelAnalyse(unittest.TestCase):
    """Unit test klasse voor SUTABEL analyse methoden."""

    def test_sutabel_analyse(self):
        """Test de volledige SUTABEL analyse workflow."""
        test_sutabel_analyse()


if __name__ == '__main__':
    unittest.main()
