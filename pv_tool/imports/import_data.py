from pandas import DataFrame, read_excel, ExcelWriter
from datetime import datetime
from typing import Optional, Literal
from pathlib import Path
from pv_tool.imports.create_dbase import add_missing_columns, select_columns, alg_columns, add_ana_columns, add_pv_naam
from pv_tool.imports.import_options import import_dbase, import_pv_tool, import_stowa
from pv_tool.imports.validation import Validation


class Dbase:
    """Deze class bevat alle functies die te maken hebben met het bouwen de Dbase-dataframe"""

    def __init__(self):
        self.stowa_df: Optional[DataFrame] = None
        self.pv_tool: Optional[DataFrame] = None
        self.dbase_df: Optional[DataFrame] = None
        self.validation = Validation(dbase=self)

    def _create_dbase(self, source: Literal['Stowa', 'PV-tool', 'Dbase']):
        """Maakt de dbase-dataframe"""
        if source == 'Stowa':
            add_missing_columns(self)
            alg_columns(self)
            add_ana_columns(self)
            add_pv_naam(self)
        elif source == 'PV-tool':
            select_columns(self)
            alg_columns(self)
            add_ana_columns(self)
            add_pv_naam(self)
        elif source == 'Dbase':
            add_ana_columns(self)
            add_pv_naam(self)

    def import_data_and_validate(self, source: Literal['Stowa', 'PV-tool', 'Dbase'],
                                 source_dir: Path, export_path: Path):
        if source == 'Stowa':
            import_stowa(self, stowa_dir=source_dir)
            self.dbase_df = self.stowa_df
        elif source == 'PV-tool':
            import_pv_tool(self, pv_dir=source_dir)
            self.dbase_df = self.pv_tool
        elif source == 'Dbase':
            import_dbase(self, dbase_dir=source_dir)
<<<<<<< HEAD

        self.validation.validation_export(export_path=export_path)  # TODO splits op in import en validate - maar behoud wel de analyse kolommen etc.
        self.validation.print_critical_errors()

=======
        self.validation.validation_export(export_path=export_path)  # TODO splits op in import en validate - maar behoud wel de analyse kolommen etc.
        self.validation.print_critical_errors()
>>>>>>> 3606918258a7be714e360ee4c6608058465def29
        self._create_dbase(source=source) # kijk of deze snapt als de input niet gevalideerd is
        return self.dbase_df

    from datetime import datetime
    from pandas import read_excel, ExcelWriter
    import os

    def export_dbase_to_excel(self, export_dir: Path, filename: str = 'Template_PVtool5_0.xlsx'):
        """
        Exports the Dbase DataFrame to an Excel file.
        :param export_dir: The directory where the file will be saved.
        :param filename: The name of the file. Default is 'Template_PVtool5_0.xlsx'.
        """
        export_path = export_dir / filename
        sheet_name = 'Dbase5_0'

        # Ensure the export directory exists
        if not export_dir.exists():
            export_dir.mkdir(parents=True)
            print(f"Directory created: {export_dir}")

        # Check if the file exists
        if export_path.exists():
            print(f"File already exists: {export_path}")
            try:
                existing_df = read_excel(export_path, sheet_name=sheet_name)
                # Compare the existing dataframe with the new dataframe
                if existing_df.equals(self.dbase_df):
                    print("Dbase is already present at this location.")
                    return
                else:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"Template_PVtool5_0.xlsx is already present but the dbase is different. "
                          f"The sheet 'Dbase5_0' will be overwritten at {timestamp}.")
            except ValueError:  # Raised if the sheet does not exist
                print(f"Sheet '{sheet_name}' does not exist in the file. Adding it.")
        else:
            print(f"Creating new file: {export_path}")
            # Ensure the file is created if it doesn't exist
            with ExcelWriter(export_path, engine='openpyxl', mode='w') as writer:
                self.dbase_df.to_excel(writer, sheet_name=sheet_name, index=True)
            print(f"Excel file created: {export_path}")
            return

        # If the file already exists, append or replace the sheet
        with ExcelWriter(export_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            self.dbase_df.to_excel(writer, sheet_name=sheet_name, index=True)
        print(f"Excel file exported to: {export_path}")
