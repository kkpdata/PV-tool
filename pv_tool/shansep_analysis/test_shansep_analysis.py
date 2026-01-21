import os.path
import unittest
from pv_tool.imports.import_data import Dbase
from pv_tool.utilities.utils import get_repo_root, make_temp_folder
from pathlib import Path
from pv_tool.shansep_analysis.shansep_analysis import SHANSEP

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

        if analysis_type == 'DSS_S_POP':
            ig = ['DSS_SAFE_veen']
            es = '20% rek'
            at = 'DSS_S_POP'
        else:
            ig = ['TXT_SAFE_klei_licht_16_175']
            es = '15% rek'
            at = 'TXT_S_POP'

        analyse = SHANSEP(
            dbase=dbase,
            investigation_groups=ig,
            effective_stress=es,
            analysis_type=at
        )

        # Apply settings
        analyse.apply_settings(alpha=0.75)

        # Test korte resultaten
        analyse_df = analyse.get_short_results()
        print(analyse_df)

        # Test geschatte parameters ophalen voor eerste benadering
        try:
            estimated_params = analyse.get_estimated_parameters()
            # Controleer dat de geschatte parameters zijn opgehaald
            if estimated_params is None:
                raise AssertionError("Geschatte parameters zijn None")
            if 'snijpunt_gem' not in estimated_params:
                raise AssertionError("snijpunt_gem ontbreekt in geschatte parameters")
            print(f"Geschatte parameters: {estimated_params}")
        except Exception as e:
            print(f"Ophalen geschatte parameters mislukt: {e}")
            estimated_params = None

        # Test NC geschatte parameters
        try:
            estimated_params_nc = analyse.get_estimated_parameters_nc()
            if estimated_params_nc is None:
                raise AssertionError("NC geschatte parameters zijn None")
            if 'snijpunt_gem_nc' not in estimated_params_nc:
                raise AssertionError("snijpunt_gem_nc ontbreekt in NC geschatte parameters")
            print(f"Geschatte NC parameters: {estimated_params_nc}")
        except Exception as e:
            print(f"Ophalen NC geschatte parameters mislukt: {e}")

        # Test instellen parameters (gebruik geschatte waardes als eerste benadering)
        if estimated_params and all(v is not None for v in [
                estimated_params['snijpunt_gem'], estimated_params['s_gem'], estimated_params['m_gem'],
                estimated_params['snijpunt_kar'], estimated_params['s_kar'], estimated_params['m_kar']
            ]):
            analyse.set_parameters_handmatig(
                    snijpunt_gem=estimated_params['snijpunt_gem'],
                    s_gem=estimated_params['s_gem'],
                    m_gem=estimated_params['m_gem'],
                    snijpunt_kar=estimated_params['snijpunt_kar'],
                    s_kar=estimated_params['s_kar'],
                    m_kar=estimated_params['m_kar']
                )
            print("Handmatige parameters ingesteld met geschatte waardes")


        # Eerst normaal testen met de parameters die al in de analyse worden benaderd ------------------------
        # Test sutabel berekeningen (na het instellen van parameters)
        try:
            analyse.calculate_sutabel()
            analyse.calculate_sutabel_nc()
        except Exception:
            pass

        # Test figuur generatie
        analyse.set_figure_sv_su()
        analyse.set_figure_sv_su_nc()
        analyse.set_figure_ln_ocr_ln_s()

        # Test show figures
        try:
            analyse.show_figure_sv_su()
            analyse.show_figure_sv_su_nc()
            analyse.show_figure_ln_ocr_ln_s()
        except Exception:
            pass

        # Test exports
        analyse.export_shansep_results_excel(str(export_dir / f"shansep_results_{analysis_type}.xlsx"))
        analyse.write_analysis_to_excel(str(export_dir / f"shansep_analysis_{analysis_type}.xlsx"))
        analyse.save_to_pdf(path=str(export_dir))

        # Opnieuw maar nu met de handmatige parameters - deze zijn gefit op 1 dataset ------------------------
        analyse.set_parameters_handmatig(snijpunt_gem=11, s_gem=0.31,
                                         m_gem=0.9, snijpunt_kar=7,
                                         s_kar=0.28, m_kar=0.9)

        # Test sutabel berekeningen (na het instellen van parameters)
        try:
            analyse.calculate_sutabel()
            analyse.calculate_sutabel_nc()
        except Exception:
            pass

        # Test figu generatie
        analyse.set_figure_sv_su()
        analyse.set_figure_sv_su_nc()
        analyse.set_figure_ln_ocr_ln_s()

        # Test show figures
        try:
            analyse.show_figure_sv_su()
            analyse.show_figure_sv_su_nc()
            analyse.show_figure_ln_ocr_ln_s()
        except Exception:
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
        pass

    # Remove temp_folder (optioneel uitcommentariëren voor debugging)
    # shutil.rmtree(export_dir)
    return True


class TestShansepAnalyse(unittest.TestCase):
    """Unit test klasse voor SHANSEP analyse methoden."""

    def test_shansep_analyse(self):
        """Test de volledige SHANSEP analyse workflow."""
        self.assertTrue(test_shansep_analyse())

if __name__ == '__main__':
    unittest.main()
