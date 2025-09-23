from pandas import DataFrame, read_excel, ExcelWriter
from datetime import datetime
from typing import Optional, Literal
from pathlib import Path
from pv_tool.imports.create_dbase import add_missing_columns, select_columns, alg_columns, add_ana_columns, add_pv_naam
from pv_tool.imports.import_options import import_dbase, import_pv_tool, import_stowa
from pv_tool.imports.validation import Validation
from pv_tool.imports.excel_utils import format_excel_sheet


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

    def import_dbase_short(self, source: Literal['Stowa', 'PV-tool', 'Dbase'],
                                 source_dir: Path):
        """Importeert data uit de Stowa-database, de oude pv-tool of de Dbase (template) en voegt kolommen toe"""
        if source == 'Dbase':
            import_dbase(self, dbase_dir=source_dir)
            return self.dbase_df
        else:
            return f"Short import only available for 'Dbase' source, not for '{source}'"

    def import_data(self, source: Literal['Stowa', 'PV-tool', 'Dbase'],
                                 source_dir: Path):
        """Importeert data uit de Stowa-database, de oude pv-tool of de Dbase (template) en voegt kolommen toe"""
        if source == 'Stowa':
            import_stowa(self, stowa_dir=source_dir)
            self.dbase_df = self.stowa_df
        elif source == 'PV-tool':
            import_pv_tool(self, pv_dir=source_dir)
            self.dbase_df = self.pv_tool
        elif source == 'Dbase':
            import_dbase(self, dbase_dir=source_dir)
        self._create_dbase(source=source)
        return self.dbase_df

    def validate_data(self, export_path: Path):
        self.validation.validation_export(export_path=export_path)
        self.validation.print_critical_errors()
        return self.dbase_df

    def export_dbase_to_excel(self, export_dir: Path, filename: str = 'Template_PVtool5_0.xlsx'):
        """
        Exports the Dbase DataFrame to an Excel file, maintaining the correct column order
        and preserving specified columns if they exist.
        """
        export_path = export_dir / filename
        sheet_name = 'Dbase5_0'
        preserve_cols = [
            'ANA_GRENSSPANNING_HANDMATIG',
            'ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG',
            'ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG'
        ]

        # Ensure the export directory exists
        export_dir.mkdir(parents=True, exist_ok=True)

        # Try to preserve columns if the file & sheet exist
        preserved_data = {}
        if export_path.exists():
            try:
                existing_df = read_excel(export_path, sheet_name=sheet_name)
                for col in preserve_cols:
                    if col in existing_df.columns and col in self.dbase_df.columns:
                        preserved_data[col] = existing_df[col]
            except Exception:
                pass

        # Restore preserved columns
        for col, data in preserved_data.items():
            self.dbase_df[col] = data

        # Ensure correct column order based on PV_TOOL_DBASE_COLUMNS
        from pv_tool.imports.globals import PV_TOOL_DBASE_COLUMNS
        ordered_columns = [col for col in PV_TOOL_DBASE_COLUMNS if col in self.dbase_df.columns]
        extra_columns = [col for col in self.dbase_df.columns if col not in PV_TOOL_DBASE_COLUMNS]
        final_columns = ordered_columns + extra_columns

        # Reorder columns
        self.dbase_df = self.dbase_df[final_columns]

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Excel sheet Dbase5_0 wordt overschreven met een nieuwe database op {timestamp}")

        # Write the DataFrame to Excel
        if export_path.exists():
            with ExcelWriter(export_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                self.dbase_df.to_excel(writer, sheet_name=sheet_name, index=True)
        else:
            with ExcelWriter(export_path, engine='openpyxl', mode='w') as writer:
                self.dbase_df.to_excel(writer, sheet_name=sheet_name, index=True)

        print(f"Excel file exported to: {export_path}")

        # Formatting
        num_columns = self.dbase_df.shape[1]
        num_rows = self.dbase_df.shape[0]
        format_excel_sheet(
            file_path=str(export_path),
            sheet_name='Dbase5_0',
            num_columns=num_columns,
            num_rows=num_rows,
            table_name='Dbase',
            index=True
        )
