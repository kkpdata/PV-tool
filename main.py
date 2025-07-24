from pathlib import Path
import os
from pv_tool.imports.import_data import Dbase
from pv_tool.validation import Validation
from typing import Optional
import git


# Deze functie is ooit geschreven door Chris, willen we deze openbaar maken?
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
from pv_tool.validation import Validation
from typing import Optional
import git

# de grote test van importeren.py
# dir_pv = Path(os.path.join(get_repo_root(), "example_files", "Proevenverzameling_tool_v4.2o.xlsm"))
# dir_stowa = Path(os.path.join(get_repo_root(), "example_files", "Uitwisselformat-database"
#                                                                 "-proevenverzameling_versie_4_2l.xlsx"))
# dir_dbase = Path(os.path.join(get_repo_root(), "example_files", "Dbase-template.xlsx"))
check_path_nathan = Path(r"C:\Users\deenekat7271\ARCADIS\30287614 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel_TD.xlsm")

dbase = Dbase()
# dbase.import_date_and_create_dbase(source='Stowa', source_dir=dir_stowa)
# dbase.import_date_and_create_dbase(source='PV-tool', source_dir=dir_pv)
# dbase.import_date_and_create_dbase(source='Dbase', source_dir=dir_dbase)
dbase.import_data_and_validate(source='PV-tool', source_dir=check_path_nathan)

# df = dbase.dbase_df
# print(df)

##
from pv_tool.analysis.c_phi_analysis import *
analyse = CPhiAnalyse(dbase=dbase, investigation_groups=['TXT_SAFE_klei_licht_16_175'], effective_stress='15% rek',
                      analysis_type='TXT_CPhi')

# analyse.factsheet()

analyse.show_figure()

##
df = analyse.cphi_analyses_data_df
print(df['5pr_ondergrens_cor'])

# test
# cphi_analyses_data_df['S\''].max


##
analyse.get_cphi_data()
analyse.expand_analysis_df()
analyse.eerste_benadering()
analyse.expand_analysis_df_corrected()
analyse.result_values()

df3 = analyse.cphi_analyses_data_df
print(df3.columns)
