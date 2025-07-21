# # Voorbeeldje
# my_obj = PVTool()
# stowa_dir = ...
# my_obj.import_stowa(stowa_dir=stowa_dir)
# investigation_groups = ['Klei_licht', 'Klei_zwaar']
# my_obj.c_phi_plot(investigation_groups=investigation_groups)

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


## Test the import + validate
from pv_tool.imports.import_options import *

path_to_data = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel_TD.xlsm")

dir_dbase = path_to_data
dbase = Dbase()
dbase.import_data_and_validate(source='PV-tool', source_dir=dir_dbase)
df = dbase.dbase_df
print(df)

##
path_to_export = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\Test output\validation_output_test.xlsx")

validate = Validation()
validate.dbase_df = df
print(validate.dbase_df)

# validate.set_index()
# print(validate.dbase_df)

# dataframes = validate.split_dbase()
# print(validate.dbase_df)

# df2 = validate.dbase_df['BORING_XID'].unique()
# print(df2)
#

test_output = validate.validation_log(save_path=path_to_export)
print(validate.dbase_df)
for error in test_output:
    print(error)


#
# print(validate.dbase_df.columns)
#
# validate.dbase_df.set_index('ALG__BORING_MONSTERNR_ID')
# print(validate.dbase_df)



## test only stuff in validate class

path_to_export = Path(r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie")



# validate = Validation()
# validate.dbase_df = dbase
# validate.validation_log(path_to_export)

validate = Validation()
validate.dbase_df = dbase.dbase_df

testpath = f"c:\\Users\\gebraadn0645\\ARCADIS\\103076457 - STOWA PV Tool - 05 Project execution\\Deliverables\\2. validatie\\Test output\\validation_output_test.xlsx"
test_output = validate.validation_log(save_path=testpath)

print(validate.dbase_df)



