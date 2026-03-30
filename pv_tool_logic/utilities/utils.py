import os

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import git  # TODO: git gaat nu fout als je werkt met conda
from typing import Optional
import datetime


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


def make_temp_folder(parent_folder: Optional[str] = None, add_microseconds: bool = False) -> str:
    timestamp_expression = "%Y%m%d_%H%M%S.%f"
    now = datetime.datetime.now().strftime(timestamp_expression)
    if not add_microseconds:
        now = now[:-7]
    if parent_folder is not None:
        export_dir = os.path.join(parent_folder, f"Temp_{now}")
    else:
        export_dir = os.path.join(get_repo_root(), "_temp_files", f"Temp_{now}")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir
