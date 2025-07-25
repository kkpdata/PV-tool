from typing import Optional, List, Literal
from pandas import DataFrame
import math
from pathlib import Path
from pv_tool.imports.validate_catagories import *
from pv_tool.imports.import_data import Dbase


class Validation:
    """In deze class staan alle functies die nodig zijn om de validatie uit te voeren."""

    def __init__(self, dbase: Dbase,
                 critical: Optional[bool] = True):
        self.dbase_df = dbase.dbase_df
        self.critical = critical
        self.total_error_log: Optional[List] = None
        self.dataframes: Optional[List] = None

    def split_dbase(self):
        """Hier komt per proef een df uit in een library van dataframes
        deze zijn later aan te roepen door bijvoorbeeld df_algemeen = dataframes['Algemene kenmerken']"""

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

        self.dataframes = {}

        for name, prefix in prefix_mapping.items():
            filtered_columns = [col for col in self.dbase_df.columns if col.startswith(prefix)]
            self.dataframes[name] = self.dbase_df[filtered_columns]

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
        """Deze functie bepaalt welke rijen door gaan naar de validatie, gebaseerd op de kolom in algemene kenmerken.
        Als de waarde = FALSE wordt de rij verwijderd"""
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

        valid_indices = uitgevoerd[uitgevoerd is True].index
        df_to_check_filtered = df_to_check.loc[valid_indices]

        return df_to_check_filtered

    def validate_with_schema(self, category, schema: Schema):
        """
        This function validates a dataframe with a certain name (category) and uses the corresponding schema for it
        This function is called in each individual validation function, where the schema is made for each category
        NB in error log and validation_df, the rows in which there are only errors or no errors are deleted
        """
        # Define dataframe and schema columns;
        # Filter the DataFrame to only include columns present in both the schema and DataFrame
        df = self.split_dbase().get(category, pd.DataFrame())

        schema_columns = [col.name for col in schema.columns]
        missing_columns = [col for col in schema_columns if col not in df.columns]

        if missing_columns:
            print(f"Missing columns in category '{category}': {', '.join(missing_columns)}")

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

    def validation_log(self, save_path: Path):  # save_path is the location where the Excel file will be saved
        """
        Voert alle validaties uit en genereert een Excel-bestand en een logbestand.

        Parameters:
            save_path (str): Pad waar het Excel-bestand moet worden opgeslagen.
            critical is true if only critical errors should be tested. critical is false will only return warnings.
            Default is True

        Returns:
            lijst met strings: Logbestand met alle foutmeldingen.
        """
        # A dictionary to hold the validation DataFrames and error logs
        validation_results = {}
        error_logs = []

        # List of validation functions to call
        if not self.critical:
            validation_functions = [
                validate_alg(self),
                validate_kenmerken_boring(self),
                validate_clas(self),
                validate_crs(self),
                validate_samendrukking(self),
                validate_monster(self),
                validate_triaxiaal(self),
                validate_dss(self),
            ]
            sheet_names = {'validate_alg': 'ALG',
                           'validate_kenmerken_boring': 'BORING',
                           'validate_clas': 'CLAS',
                           'validate_crs': 'CRS',
                           'validate_samendrukking': 'SD',
                           'validate_monster': 'MONSTER',
                           'validate_triaxiaal': 'TXT',
                           'validate_dss': 'DSS'
                           }
        else:
            validation_functions = [

                validate_kenmerken_boring(self),
                validate_clas(self),
                validate_crs(self),
                validate_samendrukking(self),
                validate_monster(self),
                validate_triaxiaal(self),
                validate_dss(self),
            ]
            sheet_names = {
                'validate_kenmerken_boring': 'BORING',
                'validate_clas': 'CLAS',
                'validate_crs': 'CRS',
                'validate_samendrukking': 'SD',
                'validate_monster': 'MONSTER',
                'validate_triaxiaal': 'TXT',
                'validate_dss': 'DSS'
            }

        # Iterate through each validation function and collect the results
        for func in validation_functions:
            validation_name = func.__name__  # Get the name of the function (e.g., 'validate_alg')
            validation_df, error_log = func()  # Call the function and get its output

            # Store the validation DataFrame and error log
            validation_results[validation_name] = validation_df

            error_logs.append(error_log)

        sheet_names_print = []
        # Create the Excel file with each validation_df as a separate sheet
        with pd.ExcelWriter(str(save_path), engine='xlsxwriter') as writer:
            for validation_name, validation_df in validation_results.items():
                # Use the corresponding sheet name from the sheet_names dictionary
                sheet_name = sheet_names.get(validation_name, validation_name)  # Fallback to function name if not found
                sheet_names_print.append(sheet_name)
                validation_df.to_excel(writer, sheet_name=sheet_name, index=True)

        self.total_error_log = error_logs

        return error_logs, sheet_names_print, validation_results
