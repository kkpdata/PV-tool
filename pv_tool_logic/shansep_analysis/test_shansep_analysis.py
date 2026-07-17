import os.path
import unittest
from pathlib import Path
from typing import Literal

from pv_tool_logic.imports.import_data import Dbase
from pv_tool_logic.shansep_analysis.shansep_analysis import SHANSEP
from pv_tool_logic.utilities.utils import get_repo_root, make_temp_folder

FILE_PATH = os.path.join(get_repo_root(), "test_files")
repo_root = get_repo_root()

export_dir = make_temp_folder(
    parent_folder=os.path.join(repo_root, "temp_exports"),
    add_microseconds=True,
)
export_dir = Path(export_dir)


def test_complete_shansep_analyse():
    """
    Test voor SHANSEP analyse.
    Voert een volledige SHANSEP analyse uit met verschillende analyse types.
    """

    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "Template_PVtool5_0.xlsx"))

    dbase.import_data(
        source="Dbase",
        source_dir=source_dir,
    )

    dbase.export_dbase_to_template(export_dir=export_dir)

    analysis_types: list[Literal["TXT_S_POP", "DSS_S_POP"]] = [
        "TXT_S_POP",
        "DSS_S_POP",
    ]

    effective_stresses: dict[
        Literal["TXT_S_POP", "DSS_S_POP"],
        list[
            Literal[
                "2% rek",
                "5% rek",
                "10% rek",
                "15% rek",
                "20% rek",
                "pieksterkte",
                "eindsterkte",
            ]
        ],
    ] = {
        "TXT_S_POP": [
            "2% rek",
            "5% rek",
            "15% rek",
            "pieksterkte",
            "eindsterkte",
        ],
        "DSS_S_POP": [
            "2% rek",
            "5% rek",
            "10% rek",
            "15% rek",
            "20% rek",
            "pieksterkte",
            "eindsterkte",
        ],
    }

    for analysis_type in analysis_types:
        ig = (
            ["DSS_voorbeeld"]
            if analysis_type == "DSS_S_POP"
            else ["TXT_voorbeeld"]
        )
        es = effective_stresses[analysis_type][-1]

        analyse = SHANSEP(
            dbase=dbase,
            investigation_groups=ig,
            effective_stress=es,
            analysis_type=analysis_type,
        )
        analyse.apply_settings(alpha=0.75)

        # Korte resultaten
        analyse_df = analyse.get_short_results()

        assert analyse_df is not None
        assert not analyse_df.empty

        # SHANSEP resultaten
        (
            df_results_shansep_gem,
            df_results_shansep_kar,
        ) = analyse.get_result_values_shansep()

        assert df_results_shansep_gem is not None
        assert df_results_shansep_kar is not None
        assert not df_results_shansep_gem.empty
        assert not df_results_shansep_kar.empty

        # Geschatte parameters

        estimated_params = analyse.get_estimated_parameters()

        assert estimated_params is not None
        assert "snijpunt_gem" in estimated_params

        estimated_params_nc = analyse.get_estimated_parameters_nc()
        if estimated_params_nc is not None:
        # assert estimated_params_nc is not None
            assert "snijpunt_gem_nc" in estimated_params_nc

        # Handmatige parameters instellen op basis van schatting

        if all(
            v is not None
            for v in [
                estimated_params["snijpunt_gem"],
                estimated_params["s_gem"],
                estimated_params["m_gem"],
                estimated_params["snijpunt_kar"],
                estimated_params["s_kar"],
                estimated_params["m_kar"],
            ]
        ):
            analyse.set_parameters_handmatig(
                snijpunt_gem=estimated_params["snijpunt_gem"],
                s_gem=estimated_params["s_gem"],
                m_gem=estimated_params["m_gem"],
                snijpunt_kar=estimated_params["snijpunt_kar"],
                s_kar=estimated_params["s_kar"],
                m_kar=estimated_params["m_kar"],
            )

        # Berekeningen

        analyse.calculate_sutabel()
        if analyse.shansep_data_df_nc is not None:
            analyse.calculate_sutabel_nc()  # TODO: nu geen NC-data in test-set, toevoegen en if-statements verwijderen

        # Figuren genereren en exporteren

        figures = {
            "sv_su": analyse.show_figure_sv_su(),
            # "sv_su_nc": analyse.show_figure_sv_su_nc(),
            "ln_ocr_ln_s": analyse.show_figure_ln_ocr_ln_s(),
        }
        if analyse.shansep_data_df_nc is not None:
            figures["sv_su_nc"] = analyse.show_figure_sv_su_nc()

        for name, fig in figures.items():

            if fig is None:
                continue

            html_name = f"test_shansep_{name}_{analysis_type}.html"

            analyse.save_fig_html(
                path=str(export_dir),
                fig=fig,
                export_name=html_name,
            )

            assert (export_dir / html_name).exists()

        # Figure setters expliciet testen
        analyse.set_figure_sv_su()
        # analyse.set_figure_sv_su_nc()
        analyse.set_figure_ln_ocr_ln_s()

        analyse.show_figure_sv_su()
        # analyse.show_figure_sv_su_nc()
        analyse.show_figure_ln_ocr_ln_s()

        if analyse.shansep_data_df_nc is not None:
            analyse.set_figure_sv_su_nc()
            analyse.show_figure_sv_su_nc()

        # Exports
        excel_results = (
            export_dir / f"shansep_results_{analysis_type}.xlsx"
        )

        excel_analysis = (
            export_dir / f"shansep_analysis_{analysis_type}.xlsx"
        )

        analyse.export_shansep_results_excel(
            str(excel_results)
        )

        analyse.write_analysis_to_excel(
            str(excel_analysis)
        )

        analyse.save_to_pdf(
            path=str(export_dir)
        )

        assert excel_results.exists()
        assert excel_analysis.exists()

        # Test met vaste handmatige parameters
        analyse.set_parameters_handmatig(
            snijpunt_gem=11,
            s_gem=0.31,
            m_gem=0.9,
            snijpunt_kar=7,
            s_kar=0.28,
            m_kar=0.9,
        )

        analyse.calculate_sutabel()

        if analyse.shansep_data_df_nc is not None:
            analyse.calculate_sutabel_nc()

        analyse.set_figure_sv_su()
        # analyse.set_figure_sv_su_nc()
        analyse.set_figure_ln_ocr_ln_s()

        analyse.show_figure_sv_su()
        # analyse.show_figure_sv_su_nc()
        analyse.show_figure_ln_ocr_ln_s()

        if analyse.shansep_data_df_nc is not None:
            analyse.set_figure_sv_su_nc()
            analyse.show_figure_sv_su_nc()

        analyse.export_shansep_results_excel(
            str(excel_results)
        )

        analyse.write_analysis_to_excel(
            str(excel_analysis)
        )

        analyse.save_to_pdf(
            path=str(export_dir)
        )

        assert excel_results.exists()
        assert excel_analysis.exists()

    # Validatie effectieve spanning
    try:
        SHANSEP(
            dbase=dbase,
            investigation_groups=["TXT_voorbeeld"],
            effective_stress="10% rek",
            analysis_type="TXT_S_POP",
        )

        raise AssertionError(
            "Verwachte ValueError voor ongeldige "
            "effective stress combinatie"
        )

    except ValueError:
        pass


class TestShansepAnalyse(unittest.TestCase):
    """Unit test klasse voor SHANSEP analyse methoden."""

    def test_shansep_analyse(self):
        """Test de volledige SHANSEP analyse workflow."""
        test_complete_shansep_analyse()


if __name__ == "__main__":
    unittest.main()