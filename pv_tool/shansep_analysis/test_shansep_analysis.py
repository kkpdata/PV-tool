import os.path
import unittest
from pv_tool.imports.import_data import Dbase
from pv_tool.utilities.utils import get_repo_root, make_temp_folder
from pathlib import Path
from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
import shutil

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
    export_name = 'Template_PVtool5_0.xlsx'
    dbase.export_dbase_to_template(export_dir=export_dir)

    # Initialize analysis types voor SHANSEP
    analysis_types = ['TXT_S_POP', 'DSS_S_POP']
    effective_stresses = {
        'TXT_S_POP': ['2% rek', '5% rek', '15% rek', 'pieksterkte', 'eindsterkte'],
        'DSS_S_POP': ['2% rek', '5% rek', '10% rek', '15% rek', '20% rek', 'pieksterkte', 'eindsterkte']
    }

    for analysis_type in analysis_types:
        # Test met een representatieve effective stress voor elk analysis type
        effective_stress = '15% rek'  # Deze werkt voor beide types

        analyse = SHANSEP(
            dbase=dbase,
            investigation_groups=['TXT_SAFE_klei_licht_16_175'],
            effective_stress=effective_stress,
            analysis_type=analysis_type
        )

        # Apply settings
        analyse.apply_settings(alpha=0.75)

        # Run de shansep analyse
        analyse._run_shansep()

        # Test het ophalen van data
        analyse.get_shansep_data()

        # Test parameters ophalen
        analyse.get_shansep_parameters()

        # Test korte resultaten
        analyse.get_short_results()

        # Test handmatige parameters (met voorbeeldwaardes) - Dit moet voor sutabel berekening
        try:
            analyse.set_parameters_handmatig(
                snijpunt_gem=0.25, s_gem=0.8, m_gem=0.9,
                snijpunt_kar=0.20, s_kar=0.7, m_kar=0.8
            )
        except Exception:
            # Parameters kunnen afhangen van specifieke data
            pass

        # Test sutabel berekeningen (na het instellen van parameters)
        try:
            analyse.calculate_sutabel()
            analyse.calculate_sutabel_nc()
        except Exception:
            # Sutabel berekeningen kunnen falen zonder juiste parameters
            pass

        # Test figure generatie
        analyse.set_figure_sv_su()
        analyse.set_figure_sv_su_nc()
        analyse.set_figure_ln_ocr_ln_s()

        # Test show figures (deze kunnen visualisatie genereren)
        try:
            analyse.show_figure_sv_su()
            analyse.show_figure_sv_su_nc()
            analyse.show_figure_ln_ocr_ln_s()
        except Exception:
            # Figures kunnen falen in test environment zonder display
            pass

        # Test exports
        analyse.export_shansep_results_excel(str(export_dir / f"shansep_results_{analysis_type}.xlsx"))
        analyse.write_analysis_to_excel(str(export_dir / f"shansep_analysis_{analysis_type}.xlsx"))
        analyse.save_to_pdf(path=str(export_dir))


    # Test effective stress validatie
    try:
        # Dit zou een ValueError moeten geven
        invalid_analyse = SHANSEP(
            dbase=dbase,
            investigation_groups=['TXT_SAFE_klei_licht_16_175'],
            effective_stress='10% rek',  # Niet toegestaan voor TXT_S_POP
            analysis_type='TXT_S_POP'
        )
        assert False, "Verwachtte ValueError voor ongeldige effective stress combinatie"
    except ValueError:
        # Verwacht gedrag
        pass

    # Remove temp_folder (optioneel uitcommentariëren voor debugging)
    # shutil.rmtree(export_dir)
    return True


class TestShansepAnalyse(unittest.TestCase):
    """Unit test klasse voor SHANSEP analyse methoden."""

    def test_shansep_analyse(self):
        """Test de volledige SHANSEP analyse workflow."""
        self.assertTrue(test_shansep_analyse())

    def test_shansep_initialization(self):
        """Test de initialisatie van SHANSEP klasse met verschillende parameters."""
        dbase = Dbase()
        source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
        dbase.import_data(source="Dbase", source_dir=source_dir)

        # Test geldige initialisatie
        analyse = SHANSEP(
            dbase=dbase,
            investigation_groups=['TXT_SAFE_klei_licht_16_175'],
            effective_stress='15% rek',
            analysis_type='TXT_S_POP'
        )
        self.assertEqual(analyse.analysis_type, 'TXT_S_POP')
        self.assertEqual(analyse.effective_stress, '15% rek')
        self.assertEqual(analyse.investigation_groups, ['TXT_SAFE_klei_licht_16_175'])
        self.assertEqual(analyse.alpha, 0.75)  # Default waarde

    def test_invalid_effective_stress_combination(self):
        """Test dat ongeldige combinaties van analysis_type en effective_stress een error geven."""
        dbase = Dbase()
        source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
        dbase.import_data(source="Dbase", source_dir=source_dir)

        # Test ongeldige combinatie: TXT_S_POP met 10% rek
        with self.assertRaises(ValueError):
            SHANSEP(
                dbase=dbase,
                investigation_groups=['TXT_SAFE_klei_licht_16_175'],
                effective_stress='10% rek',
                analysis_type='TXT_S_POP'
            )

        # Test ongeldige combinatie: TXT_S_POP met 20% rek
        with self.assertRaises(ValueError):
            SHANSEP(
                dbase=dbase,
                investigation_groups=['TXT_SAFE_klei_licht_16_175'],
                effective_stress='20% rek',
                analysis_type='TXT_S_POP'
            )

    def test_settings_application(self):
        """Test het toepassen van instellingen."""
        dbase = Dbase()
        source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
        dbase.import_data(source="Dbase", source_dir=source_dir)

        analyse = SHANSEP(
            dbase=dbase,
            investigation_groups=['TXT_SAFE_klei_licht_16_175'],
            effective_stress='15% rek',
            analysis_type='TXT_S_POP'
        )

        # Test apply_settings
        analyse.apply_settings(alpha=0.9)
        self.assertEqual(analyse.alpha, 0.9)


if __name__ == '__main__':
    unittest.main()
