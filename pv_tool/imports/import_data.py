from pandas import DataFrame
from typing import Optional, Literal
from pv_tool.imports.create_dbase import *
from pv_tool.imports.import_options import *
from pv_tool.validation import Validation


class Dbase:
    """Deze class bevat alle functies die te maken hebben met het bouwen de Dbase-dataframe"""

    def __init__(self):
        self.stowa_df: Optional[DataFrame] = None
        self.pv_tool: Optional[DataFrame] = None
        self.dbase_df: Optional[DataFrame] = None

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

    def import_data_and_validate(self, source: Literal['Stowa', 'PV-tool', 'Dbase'], source_dir: Path): # TODO: set_index = ALG_BORING_MONSTERNR_ID
        if source == 'Stowa':
            import_stowa(self, stowa_dir=source_dir)
            # Validation(self)  # TODO: uncomment nadat stukje Nathan gereed is.
            self._create_dbase(source=source)
        elif source == 'PV-tool':
            import_pv_tool(self, pv_dir=source_dir)
            # Validation(self)  # TODO: uncomment nadat stukje Nathan gereed is.
            self._create_dbase(source=source)
        elif source == 'Dbase':
            import_dbase(self, dbase_dir=source_dir)
            # Validation(self)  # TODO: uncomment nadat stukje Nathan gereed is.
            self._create_dbase(source=source)
        return self.dbase_df

    def export_dbase_to_excel(self, export_dir: Path, filename: str = 'Dbase-template.xlsx'):
        """Exporteert de Dbase-df naar een excel, het template-file
        :param export_dir: Het pad naar de directory waarin het bestand wordt opgeslagen.
        :param filename: De naam van het bestand. Standaard: 'Dbase-template.xlsx."""
        export_path = export_dir / filename
        self.dbase_df.to_excel(export_path, index=False)
        print(f"Excel-bestand geëxporteerd naar: {export_path}")
