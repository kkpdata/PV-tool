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
import git

# de grote test van importeren.py

# import pv_tool
# path_pv_tool = Path(get_repo_root()) / "example_files" / "SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel_TD.xlsm"
# dbase = Dbase()
# dbase.import_data_and_validate(source='PV-tool', source_dir=path_pv_tool)

#import stowa
# dir_stowa = Path(get_repo_root()) / "example_files" / "23ZP0747_STOWA-definitief.xlsx"
# dbase2 = Dbase()
# dbase2.import_data_and_validate(source_dir=dir_stowa, source='Stowa')
#
# print(dbase2.dbase_df.columns)

# export_dir = Path(get_repo_root()) / "example_files" / "test.xlsx"
# dbase2.dbase_df.to_excel(export_dir)

#import dbase
dbase_dir = Path(get_repo_root()) / "example_files" / "test.xlsx"
dbase = Dbase()
dbase.import_data_and_validate(source_dir=dbase_dir, source='Dbase')

print(dbase.dbase_df)
export_dir = Path(get_repo_root()) / "example_files"
dbase = Dbase()
dbase.import_data_and_validate(source_dir=dbase_dir, source='Dbase', export_path=export_dir)

print(dbase.dbase_df)







## CPHI-analyse
from pv_tool.analysis.c_phi_analysis import *
from pv_tool.analysis.variables import *
analyse = CPhiAnalyse(dbase=dbase, investigation_groups=['TXT_SAFE_klei_licht_16_175'], effective_stress='15% rek',
                      analysis_type='TXT_CPhi')

analyse.factsheet()
analyse.show_figure()
##

analyse.apply_settings(alpha=Alpha.LOCAL)
analyse.show_figure()

##
print(analyse.cohesie_gem_handmatig)

analyse.apply_parameters(cohesie_gem=15)
analyse.show_figure()
print(analyse.cohesie_gem_handmatig)

##
analyse.apply_parameters(cohesie_kar=15)  # volgens mij werkt dit nog niet
analyse.show_figure()

##
