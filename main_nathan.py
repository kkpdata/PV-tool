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
from pv_tool.imports.import_options import *


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


def test_database_import():
    """Test de database import en validatie functionaliteit."""
    repo_root = Path(get_repo_root())
    path_to_data = repo_root / "example_files" / "Template_PVtool5_0.xlsx"
    save_test = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output")

    # Database import
    dbase = Dbase()
    dbase.import_data(source='Dbase', source_dir=path_to_data)

    # Print unieke verzamelingen
    print('\nUnieke verzamelingen:')
    for pvnaam in dbase.dbase_df['PV_NAAM'].unique():
        print(pvnaam)

    return dbase


def test_cphi_analysis_txt(dbase: Dbase):
    """
    Test een TXT C-phi analyse.

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    """
    save_test = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output")

    # Initialiseer analyse
    analyse = CPhiAnalyse(
        dbase=dbase,
        investigation_groups=['TXT_SAFE_klei_licht_16_175'],
        effective_stress='15% rek',
        analysis_type='TXT_CPhi'
    )

    # Pas instellingen toe
    analyse.apply_settings(alpha=0.75)
    analyse.apply_parameters(cohesie_kar=0)

    # Print en exporteer resultaten
    print('\nResultaten TXT C-phi analyse:')
    print(analyse.print_short_results())
    analyse.add_results_to_dbase(path=str(save_test))

    # Visualisatie
    analyse.show_figure()
    analyse.save_to_pdf(path=str(save_test))


def test_cphi_analysis_dss(dbase: Dbase):
    """
    Test een DSS C-phi analyse.

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    """
    save_test = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output")

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
    analyse.add_results_to_dbase(path=str(save_test))

    # Visualisatie
    analyse.show_figure()
    analyse.save_to_pdf(path=str(save_test))


def test_cphi_analysis_txt_sh(dbase: Dbase):
    """
    Test een TXT C-phi analyse volgens schematiseringshandleiding (SH).

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    """
    save_test = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output")

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
    analyse.add_results_to_dbase(path=str(save_test))

    # Visualisatie
    analyse.show_figure()
    analyse.save_to_pdf(path=str(save_test))


def test_cphi_analysis_dss_sh(dbase: Dbase):
    """
    Test een DSS C-phi analyse volgens schematiseringshandleiding (SH).

    Parameters
    ----------
    dbase : Dbase
        Database instance met testdata
    """
    save_test = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output")

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
    analyse.add_results_to_dbase(path=str(save_test))

    # Visualisatie
    analyse.show_figure()
    analyse.save_to_pdf(path=str(save_test))


if __name__ == "__main__":
    # Test database import
    dbase = test_database_import()

    # Test verschillende analyses
    print("\nUitvoeren van verschillende test cases...")

    print("\n1. TXT C-phi analyse test")
    test_cphi_analysis_txt(dbase)

    # print("\n2. DSS C-phi analyse test")
    # test_cphi_analysis_dss(dbase)
    #
    # print("\n3. TXT C-phi analyse test (schematiseringshandleiding)")
    # test_cphi_analysis_txt_sh(dbase)
    #
    # print("\n4. DSS C-phi analyse test (schematiseringshandleiding)")
    # test_cphi_analysis_dss_sh(dbase)

    print("\nAlle tests zijn voltooid!")
