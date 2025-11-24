"""
Test script voor PV-tool functionaliteiten.

Dit script bevat verschillende test cases voor de PV-tool, inclusief:
- Repository root bepaling
- Database import en validatie
- C-phi analyses (regulier en schematiseringshandleiding)
"""

import os
from pathlib import Path
from typing import Optional
import git
from pv_tool.imports.validation import Validation
from pv_tool.imports.import_data import Dbase
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
from pv_tool.sutabel_analysis import SUTABEL
from pv_tool.imports.import_options import *
from typing import Literal


def get_repo_root(root_search_dir: Optional[str] = None) -> str:
    """
    Bepaalt de repository root door te zoeken in de gegeven directory en zijn subdirectories.

    Parameters
    ----------
    root_search_dir : str, optioneel
        De directory waarin gezocht moet worden naar de repository root.
        Als niet opgegeven (None) wordt os.getcwd() gebruikt.

    Returns
    -------
    str
        Pad naar de repository root
    """
    if root_search_dir is None:
        root_search_dir = os.getcwd()

    # Zoek eerst in de opgegeven directory
    try:
        repo = git.Repo(root_search_dir, search_parent_directories=False)
        return repo.working_tree_dir
    except git.InvalidGitRepositoryError:
        pass

    # Zoek vervolgens in subdirectories
    for subdir, dirs, files in os.walk(os.getcwd()):
        for directory in dirs:
            try:
                repo = git.Repo(os.path.join(subdir, directory), search_parent_directories=False)
                return repo.working_tree_dir
            except git.InvalidGitRepositoryError:
                continue

    # Als laatste optie: zoek in parent directories
    repo = git.Repo(root_search_dir, search_parent_directories=True)
    return repo.working_tree_dir


def database_import_test(source: Literal['Stowa', 'PV-tool', 'Dbase'],
                                 file_name_import: str, file_name_export: str = 'Template_PVtool5_0.xlsx', short=False, validate=False, export=False):
    """Test de database import en validatie functionaliteit."""
    repo_root = Path(get_repo_root())
    path_to_data = repo_root / "example_files" / file_name_import
    save_test = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output")

    # Check if input file exists
    if not path_to_data.exists():
        print(f"Error: Input file not found at {path_to_data}")
        return None

    # Create save directory if it doesn't exist
    save_test.mkdir(parents=True, exist_ok=True)

    dbase = Dbase()
    try:
        if short and not validate:
            print(f"Uitvoeren van korte database import test voor {path_to_data}...")
            dbase.import_dbase_short(source=source, source_dir=path_to_data)
        elif validate and not short:
            print(f"Uitvoeren van database import en validatie test voor {path_to_data}...")
            dbase.import_data(source=source, source_dir=path_to_data)
            dbase.validate_data(export_path=save_test)
        elif short and validate:
            print("Korte import en validatie kan niet samen worden uitgevoerd. Kies één optie.")
            return None
        else:
            print(f"Uitvoeren van volledige database import test voor {path_to_data}...")
            dbase.import_data(source=source, source_dir=path_to_data)

        # Verify database was loaded successfully
        if dbase.dbase_df is None or dbase.dbase_df.empty:
            print("Error: Database import failed - dataframe is None or empty")
            return None

        if export:
            print(f"Exporting database to {save_test / file_name_export}")
            dbase.export_dbase_to_excel(export_dir=save_test, filename=file_name_export)

        return dbase

    except Exception as e:
        print(f"Error during database import/export: {str(e)}")
        return None


def cphi_analysis_txt_test(dbase: Dbase, export_path: Path, export_file: str):
    """
    Test een TXT C-phi analyse.

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    export_path : Path
        Directory waar resultaten worden opgeslagen
    export_file : str
        Naam van het export database bestand
    """
    # Initialiseer analyse
    analyse = CPhiAnalyse(
        dbase=dbase,
        investigation_groups=['TXT_SAFE_klei_licht_16_175'],
        effective_stress='15% rek',
        analysis_type='TXT_CPhi'
    )

    # Pas instellingen toe
    analyse.apply_settings(alpha=0.75)
    analyse.apply_parameters(cohesie_kar=6.72, phi_kar=0.53, cohesie_gem=8.0)

    # Print en exporteer resultaten
    print('\nResultaten TXT C-phi analyse:')
    print(analyse.print_short_results())
    analyse.add_results_to_dbase(path=str(export_path), file_name=export_file)

    # Visualisatie
    analyse.show_figure()
    analyse.save_to_pdf(path=str(export_path))


def cphi_analysis_dss_test(dbase: Dbase, export_path: Path, export_file: str):
    """
    Test een DSS C-phi analyse.

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    export_path : Path
        Directory waar resultaten worden opgeslagen
    export_file : str
        Naam van het export database bestand
    """
    # Initialiseer analyse
    analyse = CPhiAnalyse(
        dbase=dbase,
        investigation_groups=['DSS_SAFE_veen'],
        effective_stress='20% rek',
        analysis_type='DSS_CPhi'
    )

    # Pas instellingen toe
    analyse.apply_settings(alpha=0.75)

    # Print en exporteer resultaten
    print('\nResultaten DSS C-phi analyse:')
    print(analyse.print_short_results())
    analyse.add_results_to_dbase(path=str(export_path), file_name=export_file)

    # Visualisatie
    analyse.show_figure()
    analyse.save_to_pdf(path=str(export_path))


def cphi_analysis_txt_sh_test(dbase: Dbase, export_path: Path, export_file: str):
    """
    Test een TXT C-phi analyse volgens schematiseringshandleiding (SH).

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    export_path : Path
        Directory waar resultaten worden opgeslagen
    export_file : str
        Naam van het export database bestand
    """
    # Initialiseer analyse
    analyse = CPhiAnalyse(
        dbase=dbase,
        investigation_groups=['TXT_SAFE_klei_licht_16_175'],
        effective_stress='15% rek',
        analysis_type='TXT_SH'  # SH = schematiseringshandleiding
    )

    # Pas instellingen toe
    analyse.apply_settings(alpha=0.75)

    # Print en exporteer resultaten
    print('\nResultaten TXT C-phi analyse (schematiseringshandleiding):')
    print(analyse.print_short_results())
    analyse.add_results_to_dbase(path=str(export_path), file_name=export_file)

    # Visualisatie
    analyse.show_figure()
    analyse.save_to_pdf(path=str(export_path))


def cphi_analysis_dss_sh_test(dbase: Dbase, export_path: Path, export_file: str):
    """
    Test een DSS C-phi analyse volgens schematiseringshandleiding (SH).

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    export_path : Path
        Directory waar resultaten worden opgeslagen
    export_file : str
        Naam van het export database bestand
    """
    # Initialiseer analyse
    analyse = CPhiAnalyse(
        dbase=dbase,
        investigation_groups=['DSS_SAFE_veen'],
        effective_stress='20% rek',
        analysis_type='DSS_SH'  # SH = schematiseringshandleiding
    )

    # Pas instellingen toe
    analyse.apply_settings(alpha=0.75)

    # Print en exporteer resultaten
    print('\nResultaten DSS C-phi analyse (schematiseringshandleiding):')
    print(analyse.print_short_results())
    analyse.add_results_to_dbase(path=str(export_path), file_name=export_file)

    # Visualisatie
    analyse.show_figure()
    analyse.save_to_pdf(path=str(export_path))


# function for testing shansep analysis
def shansep_analysis_test(dbase: Dbase, export_path: Path, export_file: str):
    """
    Test een SHANSEP analyse.

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    export_path : Path
        Directory waar resultaten worden opgeslagen
    export_file : str
        Naam van het export database bestand
    """
    analyse = SHANSEP(
        dbase=dbase,
        investigation_groups=['TXT_SAFE_klei_licht_16_175'],
        effective_stress='15% rek',
        analysis_type='TXT_S_POP')

    # Pas instellingen toe
    analyse.apply_settings(alpha=0.75)

    # Print en exporteer resultaten
    print('\nResultaten SHANSEP analyse:')
    analyse.add_results_to_dbase(path=str(export_path), file_name=export_file)

    analyse.set_parameters_handmatig(snijpunt_gem=11, s_gem=0.31, m_gem=0.9, snijpunt_kar=7, s_kar=0.28, m_kar=0.9)

    # sutabel = analyse.calculate_sutabel()
    # analyse.show_figure_sv_su(plot_extra_dataset=None, plot_spanningspaden=False)
    # analyse.show_figure_ln_ocr_ln_s(plot_extra_dataset=None)
    # analyse.show_figure_sv_su_nc(plot_extra_dataset=None)
    pdf_path = analyse.save_to_pdf(path=str(export_path))
    analyse.save_total_to_excel(path=str(export_path))


def sutabel_analysis_test(dbase: Dbase, export_path: Path, export_file: str):
    """
    Test een SUTABEL analyse.

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    export_path : Path
        Directory waar resultaten worden opgeslagen
    export_file : str
        Naam van het export database bestand
    """
    sutabel = SUTABEL(
        dbase=dbase,
        analysis_type='TXT_su_tabel',
        investigation_groups=['PVNAAM'],
        effective_stress='15% rek',
        alpha=0.75
    )

    # Visualize (analysis runs automatically)
    sutabel.show_figure_ln_sv_ln_su_sutabel()
    sutabel.show_figure_sv_su_sutabel()

    # Export (analysis runs automatically if needed)
    sutabel.add_results_to_dbase(str(export_path), export_file)
    sutabel.save_to_pdf(str(export_path), cv_fit_kar=0.2)


if __name__ == "__main__":
    # Test database import
    source = 'Dbase'  # Opties: 'Stowa', 'PV-tool', 'Dbase'
    import_name = 'Template_PVtool5_0_SAFE_2022_PV.xlsx'
    export_name = 'Nieuwe database testje.xlsx'
    export_dir = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output")
    export_dir.mkdir(parents=True, exist_ok=True)

    print("Start van de tests...\n")
    print(f"Using source: {source}")
    print(f"Import file: {import_name}")
    print(f"Export file: {export_name}")
    print(f"Export directory: {export_dir}")

    dbase = database_import_test(
        source=source,
        file_name_import=import_name,
        file_name_export=export_name,
        short=True,
        validate=False,
        export=False
    )

    if dbase is None or dbase.dbase_df is None:
        print("ERROR: Database import gefaald!")
        exit(1)

    # Test verschillende analyses
    print("\nUitvoeren van verschillende test cases...")

    # print("\nTXT C-phi analyse test")
    # cphi_analysis_txt_test(dbase, export_dir, export_name)
    #
    # print("\nDSS C-phi analyse test")
    # cphi_analysis_dss_test(dbase, export_dir, export_name)
    #
    # print("\nTXT C-phi analyse (schematiseringshandleiding) test")
    # cphi_analysis_txt_sh_test(dbase, export_dir, export_name)
    #
    # print("\nDSS C-phi analyse (schematiseringshandleiding) test")
    # cphi_analysis_dss_sh_test(dbase, export_dir, export_name)
    #
    # print("\nTXT SHANSEP analyse test")
    # shansep_analysis_test(dbase, export_dir, export_name)

    print("\nSUTABEL analyse test")
    sutabel_analysis_test(dbase, export_dir, export_name)

    print("\nAlle tests zijn voltooid!")
