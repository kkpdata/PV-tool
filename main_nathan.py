# # Voorbeeldje
# my_obj = PVTool()
# stowa_dir = ...
# my_obj.import_stowa(stowa_dir=stowa_dir)
# investigation_groups = ['Klei_licht', 'Klei_zwaar']
# my_obj.c_phi_plot(investigation_groups=investigation_groups)

from pathlib import Path
import os
from pv_tool.importeren import Dbase
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


# dir_pv_tool = Path(os.path.join(get_repo_root(), "example_files", "Proevenverzameling_tool_v4.2n.xlsm"))
dir_pv_tool = Path(os.path.join(get_repo_root(), "example_files", "PV-tool_platte_data.xlsx"))
dbase = Dbase()
dbase.import_pv_tool(pv_dir=dir_pv_tool)
df = dbase.pv_tool

##
validate = Validation()
validate.dbase_df = df

warnings = validate.check_all()

for warning in warnings:
    print(warning)


##
from pathlib import Path
import os
from pv_tool.importeren import Dbase
from pv_tool.validation import Validation
from typing import Optional
import git

path_to_data = r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel.xlsm"
dbase = Dbase()


validate = Validation()



