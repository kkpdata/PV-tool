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

    if short and not validate:
        print("Uitvoeren van korte database import test...")
        dbase = Dbase()
        dbase.import_dbase_short(source=source, source_dir=path_to_data)
        if export:
            dbase.export_dbase_to_excel(export_dir = save_test, filename=file_name_export)
        return dbase
    elif validate and not short:
        print("Uitvoeren van database import en validatie test...")
        dbase = Dbase()
        dbase.import_data(source=source, source_dir=path_to_data)
        dbase.validate_data(export_path=save_test)
        if export:
            dbase.export_dbase_to_excel(export_dir = save_test, filename=file_name_export)
        return dbase
    elif short and validate:
        print("Korte import en validatie kan niet samen worden uitgevoerd. Kies één optie.")
        return None
    else:
        print("Uitvoeren van volledige database import test...")
        # Database import
        dbase = Dbase()
        dbase.import_data(source=source, source_dir=path_to_data)
        if export:
            dbase.export_dbase_to_excel(export_dir = save_test, filename=file_name_export)
        return dbase


def cphi_analysis_txt_test(dbase: Dbase, file_name: str = 'Template_PVtool5_0.xlsx'):
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
    analyse.apply_parameters(cohesie_kar=0.0)

    # Print en exporteer resultaten
    print('\nResultaten TXT C-phi analyse:')
    print(analyse.print_short_results())
    analyse.add_results_to_dbase(path=str(save_test), file_name=file_name)

    # Visualisatie
    analyse.show_figure()
    analyse.save_to_pdf(path=str(save_test))


def cphi_analysis_dss_test(dbase: Dbase):
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


def cphi_analysis_txt_sh_test(dbase: Dbase):
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


def cphi_analysis_dss_sh_test(dbase: Dbase):
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

# function for testing shansep analysis
def shansep_analysis_test(dbase: Dbase):
    analyse = SHANSEP(
        dbase=dbase,
        investigation_groups=['TXT_SAFE_klei_licht_16_175'],
        effective_stress='15% rek',
        analysis_type='TXT_S_POP')

    # Pas instellingen toe
    analyse.apply_settings(alpha=0.75)

    # Print en exporteer resultaten
    print('\nResultaten SHANSEP analyse:')
    analyse.get_shansep_data()
    analyse.expand_analysis_df_s_pop_alleen_oc()
    analyse.expand_analysis_df_s_pop()
    analyse.write_analysis_to_excel(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output\shansep_test_output.xlsx")
    print("resultaten weggeschreven naar excel.")


if __name__ == "__main__":
    # Test database import
    source = 'Dbase'  # Opties: 'Stowa', 'PV-tool', 'Dbase'
    # import_name = 'WSRL 2025 Proevenverzameling_tool_v4.2n_gevalideerd_nieuw4.xlsm'
    import_name = 'Template_PVtool5_0_SAFE_2022_PV.xlsx'
    export_name = 'Template_PVtool5_0_SAFE_2022_PV.xlsx'
    import_name2 = export_name  # TODO eventueel: import naam kan nu niet export naam zijn, dan kan die niet de layout aanpassen. Moet nog worden aangepast in de toekomst.
    print("Start van de tests...\n")
    dbase = database_import_test(source=source, file_name_import=import_name, file_name_export=export_name, short=True, validate=False, export=False)

    # Test verschillende analyses
    print("\nUitvoeren van verschillende test cases...")

    print("\n1. TXT SHANSEP analyse test")
    shansep_analysis_test(dbase)

    # print("\n1. TXT C-phi analyse test")
    # file_name = 'Template_PVtool5_0_SAFE_2022_PV.xlsx'
    # cphi_analysis_txt_test(dbase, file_name=file_name)

    # print("\n2. DSS C-phi analyse test")
    # cphi_analysis_dss_test(dbase)
    #
    # print("\n3. TXT C-phi analyse test (schematiseringshandleiding)")
    # cphi_analysis_txt_sh_test(dbase)
    #
    # print("\n4. DSS C-phi analyse test (schematiseringshandleiding)")
    # cphi_analysis_dss_sh_test(dbase)

    print("\nAlle tests zijn voltooid!")
