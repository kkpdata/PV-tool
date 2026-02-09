import os.path
import unittest
from pv_tool.imports.import_data import Dbase
from pv_tool.utilities.utils import get_repo_root, make_temp_folder
from pathlib import Path
import shutil

FILE_PATH = os.path.join(get_repo_root(), "test_files")


def test_import_dbase_data():
    """Test implemented. Do not change input."""
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
    dbase.import_data(source="Dbase", source_dir=source_dir)
    assert True


def test_import_stowa_data():
    """Test implemented. Do not change input."""
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "STOWA.xlsx"))
    dbase.import_data(source="Stowa", source_dir=source_dir)
    assert True


def test_import_pv_data():
    """Test implemented. Do not change input."""
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "PV-tool.xlsm"))
    dbase.import_data(source="PV-tool", source_dir=source_dir)
    assert True


def test_validate():
    dbase = Dbase()
    source_dir = Path(os.path.join(FILE_PATH, "Dbase.xlsx"))
    dbase.import_data(source="Dbase", source_dir=source_dir)

    repo_root = get_repo_root()
    export_dir = make_temp_folder(
        parent_folder=os.path.join(repo_root), add_microseconds=True
    )
    export_dir = Path(export_dir)
    dbase.validate_data(export_path=export_dir)

    # remove temp_folder
    shutil.rmtree(export_dir)
    assert True


class TestImportAndValidate(unittest.TestCase):

    def test_import_dbase_data(self):
        test_import_dbase_data()

    def test_import_stowa_data(self):
        test_import_stowa_data()

    def test_import_pv_data(self):
        test_import_pv_data()

    def test_validate_data(self):
        test_validate()
