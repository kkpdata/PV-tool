import os
from pv_tool.imports.validation import Validation
from typing import Optional
import git


def get_repo_root(root_search_dir: Optional[str] = None) -> str:
    """Returns the repository root by searching in the given directory and its subdirectories.

    :param root_search_dir: The given directory in which it will search for the repository root. It will also
        search in the subdirectories of this given directory. If not provided (i.e. None) then function will use
        os.getcwd().
    :return:
    """

    # Determine search directory
    if root_search_dir is None:
        root_search_dir = os.getcwd()

    # Initial search at that directory
    try:
        repo = git.Repo(root_search_dir, search_parent_directories=False)
        return repo.working_tree_dir
    except git.InvalidGitRepositoryError:
        pass

    # After that subdirectories
    for subdir, dirs, files in os.walk(os.getcwd()):
        for directory in dirs:
            try:
                repo = git.Repo(os.path.join(subdir, directory), search_parent_directories=False)
                return repo.working_tree_dir
            except git.InvalidGitRepositoryError:
                continue

    # Last resort: search parent directories
    repo = git.Repo(root_search_dir, search_parent_directories=True)
    return repo.working_tree_dir


## Test the import + validate
from pv_tool.imports.import_options import *
from pv_tool.imports.import_data import Dbase


path_to_data = Path(get_repo_root()) / "example_files" / "SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel_TD.xlsm"
# path_to_data = Path(get_repo_root()) / "example_files" / "SAFE 2022 Proevenverzameling_tool_v4.2n_test_zonder_functies.xlsm"
# path_to_data = Path(get_repo_root()) / "example_files" / "Dbase-template.xlsx"

save_test = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output")

dbase = Dbase()
dbase.import_data_and_validate(source='PV-tool', source_dir=path_to_data, export_path=save_test)

print(dbase.dbase_df)

print('Unieke verzamelingen:')
for pvnaam in dbase.dbase_df['PV_NAAM'].unique():
    print(pvnaam)

##
# CPHI-analyse
from pv_tool.analysis.c_phi_analysis import *
from pv_tool.analysis.variables import *

analyse = CPhiAnalyse(dbase=dbase, investigation_groups=['TXT_SAFE_klei_zwaar'], effective_stress='5% rek',
                      analysis_type='TXT_CPhi')

#analyse.apply_parameters(cohesie_gem=9, phi_kar=0.6, cohesie_kar=7)
analyse.show_results()
analyse.show_figure()


## Forceer parameters test
analyse.apply_parameters(cohesie_gem=8, phi_kar=0.53, cohesie_kar=6.72)


analyse.show_results()
analyse.show_figure(plot_extra_dataset=['TXT_SAFE_klei_licht_12_16'])

analyse_path = save_test / f"analyse_output_{analyse.investigation_groups[0]}.xlsx"
analyse.save_to_excel(path=analyse_path)

analyse_total_path = save_test / f"c_phi_export_test.xlsx"
analyse.save_total_to_excel(path=analyse_total_path)
