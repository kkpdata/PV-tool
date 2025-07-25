from pathlib import Path
import os
from pv_tool.imports.import_data import Dbase
from pv_tool.validation import Validation
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

# path_to_data = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel_TD.xlsm")
path_to_data = Path(
    r"C:\Users\deenekat7271\ARCADIS\30287614 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel_TD.xlsm")
dir_dbase = path_to_data

dbase = Dbase()
dbase.import_data_and_validate(source='PV-tool', source_dir=dir_dbase)
df = dbase.dbase_df


##
path_to_export_warnings = Path(
    r"C:\Users\deenekat7271\ARCADIS\30287614 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output\validation_output_warnings.xlsx")
path_to_export_critical = Path(
    r"C:\Users\deenekat7271\ARCADIS\30287614 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output\validation_output_critical.xlsx")

validate_w = Validation(dbase_df=df, critical=False)
validate_c = Validation(dbase_df=df, critical=True)

val_warning = validate_w.validation_log(save_path=path_to_export_warnings)
val_crit = validate_c.validation_log(save_path=path_to_export_critical)

test_output_warnings = val_warning[0]
names_output_warnings = val_warning[1]
dfs_warnings = val_warning[2]
test_output_critical = val_crit[0]
names_output_critical = val_crit[1]
dfs_critical = val_warning[2]

for i in range(len(names_output_warnings)):
    c = names_output_warnings[i]
    e = 0
    for error in test_output_warnings[i]:
        e += 1
        print(f"waarschuwing in categorie {c} in row {error[0]} in column {error[1]}: {error[2]}")
    print(f"in categorie {c} zijn {e} waarschuwingen gevonden")

for i in range(len(names_output_critical)):
    c = names_output_critical[i]
    e = 0
    for error in test_output_critical[i]:
        e += 1
        print(f"kritieke fout in category {c} in row {error[0]} in column {error[1]}: {error[2]}")
    print(f"in categorie {c} zijn {e} fatale errors gevonden")
