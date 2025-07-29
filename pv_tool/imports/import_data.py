from pandas import DataFrame
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

    def set_validation_critical(self, value: bool):
        """Mogelijkheid om de critical value van Validation aan ta passen."""
        self.validation.critical = value

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
        self.validation.validation_log(export_path=export_path)
        self._create_dbase(source=source)
        return self.dbase_df

    def export_dbase_to_excel(self, export_dir: Path, filename: str = 'Dbase-template.xlsx'):
        """Exporteert de Dbase-df naar een excel, het template-file
        :param export_dir: Het pad naar de directory waarin het bestand wordt opgeslagen.
        :param filename: De naam van het bestand. Standaard: 'Dbase-template.xlsx."""
        export_path = export_dir / filename
        self.dbase_df.to_excel(export_path, index=False)
        print(f"Excel-bestand geëxporteerd naar: {export_path}")
