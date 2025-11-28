from __future__ import annotations
from pv_tool.imports.excel_utils import format_excel_sheet
import math
from typing import TYPE_CHECKING, Dict
from typing import Optional, List, Literal
import pandas as pd
from datetime import datetime
from pathlib import Path

from pandas_schema import Schema

from pv_tool.imports.validate_catagories import (validate_alg, validate_kenmerken_boring, validate_monster,
                                                 validate_clas, validate_crs, validate_samendrukking, validate_dss,
                                                 validate_triaxiaal)

if TYPE_CHECKING:
    from pv_tool.imports.import_data import Dbase


class Validation:
    """In deze class staan alle functies die nodig zijn om de validatie uit te voeren."""

    def __init__(self, dbase: Dbase,
                 critical: Optional[bool] = True):
        self.dbase = dbase
        self.dataframes: Optional[Dict] = None
        self.critical = critical
        self.total_error_log: Optional[List] = None
        self.critical_error_log: Optional[List] = None
        self.warning_error_log: Optional[List] = None
        self.error_totals: Optional[List] = []

    def split_dbase(self):
        """Deze functie verdeelt het invoer-dataframe in kleinere dataframes op basis van categorie."""

        prefix_mapping = {
            "Algemene kenmerken": "ALG_",
            "Kenmerken van de boring": "BORING_",
            "Monster": "MONSTER_",
            "Classificatie": "CLAS_",
            "Korrelverdeling zeefproef en fractieverdeling": "KV_",
            "Kenmerken van de sondering": "CPT_",
            "Constant rate of strain proeven (CRS)": "CRS_",
            "Samendrukkingsproeven": "SD_",
            "DSS-proeven": "DSS_",
            "Triaxiaalproeven single stage": "TXT_SS_",
            "Triaxiaalproeven multistage": "TXT_MS",
            "Beschrijving proefresultaten en controle berekening terreinspanning": "CEL_",
            "Analyse": "ANA_"
        }

        if self.dbase.dbase_df is None:
            raise ValueError("dbase_df is not initialized. Please ensure it is loaded properly.")

        self.dataframes = {}

        for name, prefix in prefix_mapping.items():
            filtered_columns = [col for col in self.dbase.dbase_df.columns if col.startswith(prefix)]
            self.dataframes[name] = self.dbase.dbase_df[filtered_columns]

        return self.dataframes

    def validation_selection(
            self,
            category: Literal[
                'Classificatie',
                'Constant rate of strain proeven (CRS)',
                'Samendrukkingsproeven',
                'DSS-proeven',
                'Triaxiaalproeven single stage'
            ]
    ):
        """Deze functie verwijdert rijen uit de dataframes waar geen proef is gedaan."""
        df_alg = self.split_dbase()['Algemene kenmerken']
        df_to_check = self.split_dbase()[category]
        if category == 'Classificatie':
            uitgevoerd = df_alg['ALG__CLASSIFICATIE']
        elif category == 'Constant rate of strain proeven (CRS)':
            uitgevoerd = df_alg['ALG__CRS']
        elif category == 'Samendrukkingsproeven':
            uitgevoerd = df_alg['ALG__SAMENDRUKKING']
        elif category == 'DSS-proeven':
            uitgevoerd = df_alg['ALG__DSS']
        elif category == 'Triaxiaalproeven single stage':
            uitgevoerd = df_alg['ALG__TRIAXIAAL']
        else:
            raise ValueError("Ongeldige categorie")

        if not uitgevoerd.index.equals(df_to_check.index):
            raise ValueError("Indices van 'uitgevoerd' en 'df_to_check' komen niet overeen")

        valid_indices = uitgevoerd[uitgevoerd.astype(bool)].index
        df_to_check_filtered = df_to_check.loc[valid_indices]

        self.dataframes[category] = df_to_check_filtered

    def validate_with_schema(self, category, schema: Schema):
        """
        This function validates a dataframe with a certain name (category) and uses the corresponding schema for it
        This function is called in each individual validation function, where the schema is made for each category
        NB in error log and validation_df, the rows in which there are only errors or no errors are deleted
        """
        # Filter the DataFrame to only include columns present in both the schema and DataFrame
        df = self.split_dbase().get(category, pd.DataFrame())

        schema_columns = [col.name for col in schema.columns]
        missing_columns = [col for col in schema_columns if col not in df.columns]

        if missing_columns:
            print(f"Ontbrekende kolommen in categorie '{category}': {', '.join(missing_columns)}")

        available_columns = [col for col in schema_columns if col in df.columns]
        data_to_validate = df[available_columns]

        # Validate the data
        errors = schema.validate(data_to_validate)

        error_log = []
        validation_df = data_to_validate.copy()

        # Populate the validation columns with error messages
        for column in available_columns:
            validation_df[f"{column}_validate"] = ""
            col_position = validation_df.columns.get_loc(column) + 1
            validation_df.insert(col_position, f"{column}_validate", validation_df.pop(f"{column}_validate"))

        for error in errors:
            row = error.row
            column = error.column
            error_message = error.message
            validation_df.at[row, f"{column}_validate"] = error_message
            error_log.append([row, column, error_message])

        # Remove rows without any errors or with all errors - those are not interesting for the user
        to_delete = []
        for i in validation_df.index:
            data = [validation_df[f"{schema_column}_validate"].loc[i] for schema_column in available_columns]
            if not data or all(item == '' for item in data) or all(
                    isinstance(item, float) and math.isnan(item) for item in data):
                to_delete.append(i)
            elif all(data):
                to_delete.append(i)

        validation_df = validation_df.drop(index=to_delete)

        for error in error_log[:]:
            if error[0] in to_delete:
                error_log.remove(error)

        # Add extra validation summary rows at the top
        summary_row_1 = []
        summary_row_2 = []

        for col in available_columns:
            original_column_data = df[col]
            validation_column_data = validation_df[f"{col}_validate"]

            # Determine the messages for the first row
            if original_column_data.isnull().all():
                summary_row_1.append('geen data')
            elif validation_column_data.str.strip().any():
                summary_row_1.append('fouten gevonden')
            else:
                summary_row_1.append('geen fouten gevonden')

            # No message for the validation column
            summary_row_1.append('')

            # No message for the original column
            summary_row_2.append('')

            # Add number of errors
            summary_row_2.append(validation_df[f"{col}_validate"]
                                 .apply(lambda x: bool(str(x).strip()) if pd.notna(x) else False)
                                 .sum())

        initial_index = validation_df.index.tolist()
        new_index = ['samenvatting', 'aantal fouten'] + initial_index

        # Prepend the summary rows using pd.concat
        summary_df = pd.DataFrame([summary_row_1, summary_row_2], columns=validation_df.columns)
        validation_df = pd.concat([summary_df, validation_df], ignore_index=True)

        validation_df.index = new_index
        return validation_df, error_log

    def validation_log(self, export_path: Path, critical: Optional[bool] = True):
        """ Voert alle validaties uit en genereert een Excel-bestand (logbestand)."""
        self.critical = critical

        c = 'critical_errors' if self.critical else 'warnings'

        if export_path.is_dir():
            file_name = f"validation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{c}.xlsx"
            export_path = export_path / file_name
        elif export_path.suffix != ".xlsx":
            raise ValueError("Als save_path een bestandspad is, moet het de extensie '.xlsx' bevatten.")

        validation_mapping = {
            "validate_alg": validate_alg,
            "validate_kenmerken_boring": validate_kenmerken_boring,
            "validate_clas": validate_clas,
            "validate_crs": validate_crs,
            "validate_samendrukking": validate_samendrukking,
            "validate_monster": validate_monster,
            "validate_triaxiaal": validate_triaxiaal,
            "validate_dss": validate_dss
        }

        if self.critical:
            validation_mapping.pop("validate_alg", None)

        validation_results = {}
        error_logs = []

        try:
            for func_name, func in validation_mapping.items():
                validation_df, error_log = func(self)
                # Ensure all column names are strings
                validation_df.columns = validation_df.columns.astype(str)
                validation_results[func_name] = validation_df
                self.error_totals.append(f"number of {c} in {func_name} = {len(error_log)}")
                error_logs.extend(error_log)

            sheet_names_print = []
            # First write all sheets to Excel
            with pd.ExcelWriter(str(export_path), engine="xlsxwriter") as writer:
                for func_name, validation_df in validation_results.items():
                    sheet_name = func_name.upper()
                    sheet_names_print.append(sheet_name)
                    # Ensure index is also strings when writing
                    validation_df.index = validation_df.index.astype(str)
                    # Set index name if it's empty to prevent Excel warnings
                    if validation_df.index.name is None:
                        validation_df.index.name = 'ID'
                    validation_df.to_excel(writer, sheet_name=sheet_name, index=True)

            # After the file is completely written and closed, then format each sheet
            for sheet_name in sheet_names_print:
                try:
                    num_rows, num_columns = validation_results[sheet_name.lower()].shape
                    format_excel_sheet(
                        file_path=str(export_path),
                        sheet_name=sheet_name,
                        num_columns=num_columns,
                        num_rows=num_rows,
                        table_name=f'tabel_{sheet_name.lower()}',
                        index=True
                    )
                except Exception as format_error:
                    print(f"Waarschuwing: Kon sheet {sheet_name} niet formatteren: {str(format_error)}")
                    # Continue with other sheets even if one fails to format

        except Exception as e:
            print(f"Er trad een fout op tijdens validatie of het schrijven van Excel: {str(e)}")
            raise e

        return error_logs

    def validation_export(self, export_path: Path):
        """Hier worden twee exports gemaakt van de validatie.
        1 voor de kritieke fouten en 1 voor de waarschuwingen."""
        self.critical_error_log = self.validation_log(export_path, critical=True)
        self.warning_error_log = self.validation_log(export_path, critical=False)
        self.total_error_log = [self.critical_error_log, self.warning_error_log]

    def print_critical_errors(self):
        """"Print de errors uit de import."""
        errors = self.error_totals
        for error in errors:
            print(error)
