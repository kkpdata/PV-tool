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
        and preserving specified columns from the current DataFrame.
        """
        export_path = export_dir / filename
        sheet_name = 'Dbase5_0'

        # Ensure the export directory exists
        export_dir.mkdir(parents=True, exist_ok=True)

        # Define analysis columns in their correct order
        analysis_columns = [
            'ANA_TERREINSPANNING', 'ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING',
            'ANA_DSS_MAX_CONSOLIDATIE_SPANNING', 'ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL',
            'ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG', 'ANA_TXT_CONSOLIDATIE_TYPE_REKEN',
            'ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL', 'ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG',
            'ANA_DSS_CONSOLIDATIE_TYPE_REKEN', 'ANA_GRENSSPANNING_PROEF', 'ANA_POP_VELD',
            'ANA_POP_VELD_GEMIDDELD', 'ANA_GRENSSPANNING_VOORSTEL', 'ANA_GRENSSPANNING_HANDMATIG',
            'ANA_GRENSSPANNING_REKEN', 'OCR_TXT', 'OCR_DSS'
        ]

        # Get base columns from PV_TOOL_DBASE_COLUMNS
        from pv_tool.imports.globals import PV_TOOL_DBASE_COLUMNS
        base_columns = [col for col in PV_TOOL_DBASE_COLUMNS if col in self.dbase_df.columns]

        # Remove any analysis columns that might be in base_columns to prevent duplication
        base_columns = [col for col in base_columns if col not in analysis_columns]

        # Get analysis columns that exist in the DataFrame
        ana_columns = [col for col in analysis_columns if col in self.dbase_df.columns]

        # Get any remaining columns that aren't in either list, excluding duplicates
        used_columns = set(base_columns + ana_columns)
        other_columns = [col for col in self.dbase_df.columns if col not in used_columns]

        # Combine all columns in the correct order
        final_columns = base_columns + ana_columns + other_columns

        # Create a copy of the DataFrame with reordered columns, ensuring no duplicates
        export_df = self.dbase_df[final_columns].copy()

        # rond waarden af voor consistentie
        # cols_to_round = ['ANA_TERREINSPANNING', 'ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING',
        #                  'ANA_DSS_MAX_CONSOLIDATIE_SPANNING', 'ANA_GRENSSPANNING_PROEF',
        #                  'ANA_POP_VELD', 'ANA_POP_VELD_GEMIDDELD', 'ANA_GRENSSPANNING_VOORSTEL',
        #                  'ANA_GRENSSPANNING_REKEN', 'OCR_TXT', 'OCR_DSS']
        # numeric_columns = export_df.select_dtypes(include=['float64', 'int64']).columns
        # for col in cols_to_round:
        #     if col in numeric_columns:
        #         export_df[col] = export_df[col].round(2)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Excel sheet Dbase5_0 wordt weggeschreven op {timestamp}")

        # Write the DataFrame to Excel with improved settings to prevent corruption
        if export_path.exists():
            with ExcelWriter(export_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                export_df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=True,
                    engine='openpyxl',
                    float_format="%.6f"  # Use consistent float format
                )
        else:
            with ExcelWriter(export_path, engine='openpyxl', mode='w') as writer:
                export_df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=True,
                    engine='openpyxl',
                    float_format="%.6f"  # Use consistent float format
                )

        print(f"Excel file exported to: {export_path}")

        # Formatting
        num_columns = export_df.shape[1]
        num_rows = export_df.shape[0]
        format_excel_sheet(
            file_path=str(export_path),
            sheet_name='Dbase5_0',
            num_columns=num_columns,
            num_rows=num_rows,
            table_name='Dbase',
            index=True
        )
