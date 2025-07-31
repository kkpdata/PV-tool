from typing import Optional


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

##
from pathlib import Path
import os
from pv_tool.imports.import_data import Dbase
from pv_tool.imports.import_options import import_pv_tool
import git

# de grote test van importeren.py

import pv_tool
path_pv_tool = Path(get_repo_root()) / "example_files" / "SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel_TD.xlsm"
# path_pv_tool = Path(get_repo_root()) / "example_files" / "SAFE 2022 Proevenverzameling_tool_v4.2n_test_zonder_zonder_functies.xlsm"
export_dir = Path(get_repo_root()) / "example_files" / "test.xlsx"
dbase = Dbase()
dbase.import_data_and_validate(source='PV-tool', source_dir=path_pv_tool, export_path=export_dir)


## CPHI-analyse
from pv_tool.analysis.c_phi_analysis import CPhiAnalyse
analyse = CPhiAnalyse(dbase=dbase, investigation_groups=['TXT_SAFE_klei_licht_16_175'], effective_stress='15% rek',
                      analysis_type='TXT_CPhi')

analyse.show_results()
##
# print('alpha =', analyse.alpha)
#
# print('c_gem_hand', analyse.cohesie_gem_handmatig)
# print('phi_kar_hand', analyse.phi_kar_handmatig)
# print('c_kar_hand', analyse.cohesie_kar_handmatig)
#
# # gaat goed tot hier


##
analyse.apply_parameters(cohesie_gem=8, phi_kar=0.53, cohesie_kar=2.45)
print('c_gem_hand', analyse.cohesie_gem_handmatig)
print('phi_kar_hand', analyse.phi_kar_handmatig)
print('c_kar_hand', analyse.cohesie_kar_handmatig)
analyse.show_results()


##


##



