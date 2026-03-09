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
    path_to_data = repo_root / "test_files" / file_name_import
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
            print(f"Exporting database to {save_test / file_name_export} is no longer part of the test.")
            # dbase.export_dbase_to_excel(export_dir=save_test, filename=file_name_export)

        return dbase

    except Exception as e:
        print(f"Error during database import/export: {str(e)}")
        return None


def cphi_analysis_txt_test(dbase: Dbase, export_path: Path, export_file: str, plot_extra_dataset = None, plot_spanningspaden=False):
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

    # analyse = CPhiAnalyse(
    #     dbase=dbase,
    #     investigation_groups=['TXT_SAFE_klei_licht_16_175'],
    #     effective_stress='eindsterkte',
    #     analysis_type='TXT_CPhi'
    # )

    # Pas instellingen toe
    analyse.apply_settings(alpha=0.75)
    # analyse.apply_parameters(cohesie_gem=6.5, phi_kar=0.45, cohesie_kar=0.1)
    analyse.apply_parameters(cohesie_gem=8.0, phi_kar=0.53, cohesie_kar=6.72)

    # Print en exporteer resultaten
    print('\nResultaten TXT C-phi analyse:')
    print(analyse.get_short_results())
    analyse.add_results_to_template(path=str(export_path), export_name=export_file)

    # Visualisatie
    analyse.show_figure(plot_extra_dataset = plot_extra_dataset, plot_spanningspaden=plot_spanningspaden)
    analyse.save_to_pdf(path=str(export_path))


def cphi_analysis_dss_test(dbase: Dbase, export_path: Path, export_file: str, plot_extra_dataset = None, plot_spanningspaden=False):
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
    print(analyse.get_short_results())
    analyse.add_results_to_template(path=str(export_path), export_name=export_file)

    # Visualisatie
    analyse.show_figure(plot_extra_dataset = plot_extra_dataset, plot_spanningspaden=plot_spanningspaden)
    analyse.save_to_pdf(path=str(export_path))


def cphi_analysis_txt_sh_test(dbase: Dbase, export_path: Path, export_file: str, plot_extra_dataset = None, plot_spanningspaden=False):
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
    print(analyse.get_short_results())
    analyse.add_results_to_template(path=str(export_path), export_name=export_file)

    # Visualisatie
    analyse.show_figure(plot_extra_dataset = plot_extra_dataset, plot_spanningspaden=plot_spanningspaden)
    analyse.save_to_pdf(path=str(export_path))


def cphi_analysis_dss_sh_test(dbase: Dbase, export_path: Path, export_file: str, plot_extra_dataset = None, plot_spanningspaden=False):
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
    print(analyse.get_short_results())
    analyse.add_results_to_template(path=str(export_path), export_name=export_file)

    # Visualisatie
    analyse.show_figure(plot_extra_dataset = plot_extra_dataset, plot_spanningspaden=plot_spanningspaden)
    analyse.save_to_pdf(path=str(export_path))


# function for testing shansep analysis
def shansep_analysis_test(dbase: Dbase, export_path: Path, export_file: str, plot_extra_dataset = None):
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
    # analyse = SHANSEP(
    #     dbase=dbase,
    #     investigation_groups=['DSS_SAFE_veen'],
    #     effective_stress='20% rek',
    #     analysis_type='DSS_S_POP')

    analyse = SHANSEP(
        dbase=dbase,
        investigation_groups=['TXT_SAFE_klei_licht_16_175'],
        effective_stress='15% rek',
        analysis_type='TXT_S_POP')

    # Pas instellingen toe
    analyse.apply_settings(alpha=0.75)

    # eerst moeten de korte resultaten berekend worden en daarna de eerste plots. Dan daarna handmatige parameters
    df = analyse.get_short_results()
    print(df)
    analyse.show_figure_sv_su(plot_extra_dataset=plot_extra_dataset)
    analyse.show_figure_ln_ocr_ln_s(plot_extra_dataset=plot_extra_dataset)
    analyse.show_figure_sv_su_nc(plot_extra_dataset=plot_extra_dataset)


    analyse.set_parameters_handmatig(snijpunt_gem=11, s_gem=0.31, m_gem=0.9, snijpunt_kar=7, s_kar=0.28, m_kar=0.9)

    # sutabel = analyse.calculate_sutabel()
    analyse.show_figure_sv_su(plot_extra_dataset=plot_extra_dataset)
    analyse.show_figure_ln_ocr_ln_s(plot_extra_dataset=plot_extra_dataset)
    analyse.show_figure_sv_su_nc(plot_extra_dataset=plot_extra_dataset)

    # Print en exporteer resultaten
    analyse.add_results_to_template(path=str(export_path), export_name=export_file)
    pdf_path = analyse.save_to_pdf(path=str(export_path))
    analyse.save_total_to_excel(path=str(export_path))


def sutabel_analysis_test(dbase: Dbase, export_path: Path, export_file: str, plot_extra_dataset = None):
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
    # sutabel = SUTABEL(
    #     dbase=dbase,
    #     analysis_type='DSS_su_tabel',
    #     investigation_groups=['DSS_SAFE_veen'],
    #     effective_stress='20% rek'
    # )

    # sutabel = SUTABEL(
    #     dbase=dbase,
    #     analysis_type='TXT_su_tabel',
    #     investigation_groups=['TXT_SAFE_klei_licht_16_175'],
    #     effective_stress='15% rek'
    # )

    sutabel = SUTABEL(
        dbase=dbase,
        analysis_type='TXT_su_tabel',
        investigation_groups=['TXT_SAFE_klei_zwaar'],
        effective_stress='15% rek'
    )

    sutabel.apply_settings(alpha=0.75)

    sutabel.set_manual_parameters(a2_kar=0.683, a1_kar=0.489, vc_fit_kar=0.1)

    # Visualize (analysis runs automatically)
    sutabel.show_figure_ln_sv_ln_su_sutabel(plot_extra_dataset=plot_extra_dataset)
    sutabel.show_figure_sv_su_sutabel(plot_extra_dataset=plot_extra_dataset)

    # Export (analysis runs automatically if needed)
    sutabel.add_results_to_template(str(export_path), export_file)
    sutabel.save_to_pdf(str(export_path))



if __name__ == "__main__":
    # Test database import
    source = 'Dbase'  # Opties: 'Stowa', 'PV-tool', 'Dbase'
    import_name = 'Dbase.xlsx'
    # import_name = 'WSRL 2025 PVtool5_0_gevalideerd.xlsx'
    export_name = 'Template_PVtool5_0'
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
        export=True
    )

    if dbase is None or dbase.dbase_df is None:
        print("ERROR: Database import gefaald!")
        exit(1)

    print(dbase.dbase_df['PV_NAAM'].unique())

    # Uiteindelijk moeten deze mapjes verwijderd worden van de github repo

    plot_extra_dataset = ['TXT_SAFE_klei_licht_outlier', 'TXT_SAFE_klei_zwaar']
    plot_spanningspaden = True

    # Test verschillende analyses
    print("\nUitvoeren van verschillende test cases...")

    # print("\nTXT C-phi analyse test")
    # cphi_analysis_txt_test(dbase, export_dir, export_name, plot_extra_dataset=plot_extra_dataset, plot_spanningspaden=plot_spanningspaden)

    # print("\nDSS C-phi analyse test")
    # cphi_analysis_dss_test(dbase, export_dir, export_name, plot_extra_dataset=plot_extra_dataset, plot_spanningspaden=plot_spanningspaden)
    #
    # print("\nTXT C-phi analyse (schematiseringshandleiding) test")
    # cphi_analysis_txt_sh_test(dbase, export_dir, export_name, plot_extra_dataset=plot_extra_dataset, plot_spanningspaden=plot_spanningspaden)
    #
    # print("\nDSS C-phi analyse (schematiseringshandleiding) test")
    # cphi_analysis_dss_sh_test(dbase, export_dir, export_name, plot_extra_dataset=plot_extra_dataset, plot_spanningspaden=plot_spanningspaden)
    #
    # plot_extra_dataset = ['TXT_SAFE_klei_zwaar']
    #
    # print("\nTXT SHANSEP analyse test")
    # shansep_analysis_test(dbase, export_dir, export_name, plot_extra_dataset=plot_extra_dataset)
    # # #
    print("\nSUTABEL analyse test")
    sutabel_analysis_test(dbase, export_dir, export_name+'xlsx', plot_extra_dataset=plot_extra_dataset)

    # print("\nAlle tests zijn voltooid!")
