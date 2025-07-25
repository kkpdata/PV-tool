# In deze file wil ik alle code opslaan wat betreft de validatie van de import
# Kijk in de file van Leo:
# C:\Users\deenekat7271\ARCADIS\30287614 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie
# welke kolommen we allemaal moeten valideren.

from typing import Optional, List, Literal
from pandas import DataFrame
import pandas as pd
from pandas_schema import Column, Schema
from pandas_schema.validation import (
    CustomElementValidation, InRangeValidation
)
import math
from pathlib import Path


# onderstaande code is een idee van Chris. Mogelijk iets voor later als we nog tijd hebben.
# class ValidationVB:
#     class Methods:
#         pass
#
#     class Categories:
#
#         def dss(self):
#             pass
#
#         def txt(self):
#             pass
#
#         def etc(self):
#             pass
#
#     class Utils:
#         pass


###
IsEmptyValidator = CustomElementValidation(
    lambda value: value != "" and not pd.isna(value), "This cell is empty"
)

class Validation:
    """In deze class staan alle functies die de validatie uitvoeren."""

    def __init__(self, dbase_df: Optional[DataFrame] = None, critical: Optional[bool]=True):
        self.dbase_df = dbase_df
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

    def validation_selection(self, category: Literal['Classificatie', 'Constant rate of strain proeven (CRS)',
    'Samendrukkingsproeven', 'DSS-proeven', 'Triaxiaalproeven single stage']):
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

        valid_indices = uitgevoerd[uitgevoerd == True].index
        df_to_check_filtered = df_to_check.loc[valid_indices]

        return df_to_check_filtered

    def validate_with_schema(self, category, schema: Schema):
        """
        This function validates a dataframe with a certain name (category) and uses the corresponding schema for it
        This function is called in each individual validation function, where the schema is made for each category
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
            error_log.append(f"Error in row '{row}' and column '{column}': {error_message}")

        # Add extra validation summary rows at the top
        summary_row_1 = []
        summary_row_2 = []

        for col in available_columns:  # TODO: dit komt niet goed door in output excel - checken
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
        initial_index = validation_df.index.tolist()
        new_index = ['samenvatting', 'aantal fouten'] + initial_index

        # Prepend the summary rows using pd.concat
        summary_df = pd.DataFrame([summary_row_1, summary_row_2], columns=validation_df.columns)
        validation_df = pd.concat([summary_df, validation_df], ignore_index=True)

        validation_df.index = new_index
        return validation_df, error_log

    def validate_alg(self):
        """
        This function validates the dataframe 'algemene kenmerken' with the following schema.
        It uses validate_with_schema
        """
        category = "Algemene kenmerken"
        if not self.critical:
            schema = Schema([
                Column('ALG_NAAM_POLDER_DIJK', [IsEmptyValidator]),
                Column('ALG_REFERENTIE', [IsEmptyValidator])
            ])

            return self.validate_with_schema(category, schema)

    def validate_kenmerken_boring(self):
        """
        This function validates the dataframe 'Kenmerken van de boring' with the following schema.
        It uses validate_with_schema
        """
        category = "Kenmerken van de boring"
        if not self.critical:
            schema = Schema([
                Column('BORING_FILENAAM_PDF', [IsEmptyValidator]),
                Column('BORING_FILENAAM_GEF', [IsEmptyValidator])
            ])
        else:
            schema = Schema([
                Column('BORING_XID', [InRangeValidation(-7000, 300000)]),
                Column('BORING_YID', [InRangeValidation(289000, 629000)]),
                Column('BORING_MAAIVELDPEIL', [InRangeValidation(-100, 500)]),
                Column('BORING_NUMMER', [IsEmptyValidator]),
                Column('BORING_POSITIE', [IsEmptyValidator])
            ])

        return self.validate_with_schema(category, schema)

    def validate_monster(self):
        """
        This function validates the dataframe 'Monster' with the following schema.
        It uses validate_with_schema
        """
        category = "Monster"
        if not self.critical:
            schema = Schema([
                Column('MONSTER_NIVEAU_MV_VANAF', [IsEmptyValidator]),
                Column('MONSTER_NIVEAU_MV_TOT', [IsEmptyValidator])
            ])
        else:
            schema = Schema([
                Column('MONSTER_ID', [IsEmptyValidator]),
                Column('MONSTER_NIVEAU_NAP_VANAF', [InRangeValidation(-100, 500)]),
                Column('MONSTER_NIVEAU_NAP_TOT', [InRangeValidation(-100, 500)])
            ])
        return self.validate_with_schema(category, schema)

    def validate_clas(self):
        """
        This function validates the dataframe 'Classificatie' with the following schema.
        It uses validate_with_schema
        """
        category = "Classificatie"
        if not self.critical:
            schema = Schema([
                Column('CLAS_GRONDSOORT', [IsEmptyValidator]),
                Column('CLAS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
                Column('CLAS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
                Column('CLAS_VOLUMEGEWICHT_DRG', [InRangeValidation(0, 25)]),
                Column('CLAS_WATERGEHALTE', [InRangeValidation(0, 1000)])
            ])
        else:
            schema = Schema([
                Column('CLAS_MONSTERID', [IsEmptyValidator])
            ])
        return self.validate_with_schema(category, schema)

    def validate_crs(self):
        """
        This function validates the dataframe 'Constant rate of strain proeven (CRS)' with the following schema.
        It uses validate_with_schema
        """
        category = "Constant rate of strain proeven (CRS)"
        if not self.critical:
            schema = Schema([
                Column('CRS_FILENAAM_PDF', [IsEmptyValidator]),
                Column('CRS_MONSTERID', [IsEmptyValidator]),
                Column('CRS_GRONDSOORT', [IsEmptyValidator]),
                Column('CRS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
                Column('CRS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
                Column('CRS_VOLUMEGEWICHT_DRG', [InRangeValidation(0, 25)]),
                Column('CRS_WATERGEHALTE_VOOR', [InRangeValidation(0, 1000)]),
                Column('CRS_REK_BIJ_GRENSSPANNING_A', [InRangeValidation(0, 100)]),

            ])
        else:
            schema = Schema([
                Column('CRS_TERREINSPANNING', [InRangeValidation(0, 500)]),
                Column('CRS_GRENSSPANNING_A', [InRangeValidation(0, 1000)]),
                Column('CRS_ISOTACHE_A', [InRangeValidation(0, 0.1)]),
                Column('CRS_ISOTACHE_B', [InRangeValidation(0, 1)]),
                Column('CRS_ISOTACHE_C', [InRangeValidation(0, 0.1)])
            ])

        return self.validate_with_schema(category, schema)

    def validate_samendrukking(self):
        """
        This function validates the dataframe 'Samendrukkingsproeven' with the following schema.
        It uses validate_with_schema
        """
        category = "Samendrukkingsproeven"
        if not self.critical:
            schema = Schema([
                Column('SD_FILENAAM_PDF', [IsEmptyValidator]),
                Column('SD_MONSTERID', [IsEmptyValidator]),
                Column('SD_GRONDSOORT',
                       [IsEmptyValidator]),
                Column('SD_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
                Column('SD_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
                Column('SD_VOLUMEGEWICHT_DR', [InRangeValidation(0, 25)]),
                Column('SD_WATERGEHALTE_INI', [InRangeValidation(0, 1000)]),
                Column('SD_ISOTACHE_REK_BIJ_GRENSSPANNING_A', [IsEmptyValidator, InRangeValidation(0, 100)]),
                Column('SD_ISOTACHE_BOVENGRENS_GRENSSPANNING_B', [IsEmptyValidator, InRangeValidation(0, 100)])
            ])
        else:
            schema = Schema([
                Column('SD_TERREINSPANNING', [InRangeValidation(0, 500)]),
                Column('SD_ISOTACHE_A', [InRangeValidation(0, 0.1)]),
                Column('SD_ISOTACHE_B', [InRangeValidation(0, 1)]),
                Column('SD_ISOTACHE_C', [InRangeValidation(0, 0.1)]),
                Column('SD_ISOTACHE_GRENSSPANNING_A', [InRangeValidation(0, 1000)])
            ])
        return self.validate_with_schema(category, schema)

    def validate_dss(self):
        """
        This function validates the dataframe 'DSS-proeven' with the following schema.
        It uses validate_with_schema
        """
        category = "DSS-proeven"
        if not self.critical:
            schema = Schema([
                Column('DSS_FILENAAM_PDF', [IsEmptyValidator]),
                Column('DSS_FILENAAM_SPANNINGSPAD', [IsEmptyValidator]),
                Column('DSS_MONSTERID', [IsEmptyValidator]),
                Column('DSS_GRONDSOORT',[IsEmptyValidator]),
                Column('DSS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
                Column('DSS_TERREINSPANNING', [InRangeValidation(0, 500)]),
                Column('DSS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
                Column('DSS_WATERGEHALTE_VOOR', [InRangeValidation(0, 1000)])
            ])
        else:
            schema = Schema([
                Column('DSS_TERREINSPANNING', [InRangeValidation(0, 500)]),
                Column('DSS_MAX_EFF_VERT_SPANNING_CONSOLIDATIE', [InRangeValidation(0, 2000)]),
                Column('DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE', [InRangeValidation(0, 2000)]),
                Column('DSS_S_2%', [InRangeValidation(0, 2000)]),
                Column('DSS_T_2%', [InRangeValidation(0, 1000)]),
                Column('DSS_S_5%', [InRangeValidation(0, 2000)]),
                Column('DSS_T_5%', [InRangeValidation(0, 1000)]),
                Column('DSS_S_10%', [InRangeValidation(0, 2000)]),
                Column('DSS_T_10%', [InRangeValidation(0, 1000)]),
                Column('DSS_S_15%', [InRangeValidation(0, 2000)]),
                Column('DSS_T_15%', [InRangeValidation(0, 1000)]),
                Column('DSS_S_20%', [InRangeValidation(0, 2000)]),
                Column('DSS_T_20%', [InRangeValidation(0, 1000)]),
                Column('DSS_S_BIJ_T_MAX', [InRangeValidation(0, 2000)]),
                Column('DSS_T_MAX', [InRangeValidation(0, 1000)]),
                Column('DSS_REK_BIJ_T_MAX', [InRangeValidation(0, 60)]),
                Column('DSS_S_BIJ_T_EIND', [InRangeValidation(0, 2000)]),
                Column('DSS_T_EIND', [InRangeValidation(0, 1000)]),
                Column('DSS_REK_BIJ_T_EIND', [InRangeValidation(0, 60)])
            ])
        return self.validate_with_schema(category, schema)

    def validate_triaxiaal(self):
        """
        This function validates the dataframe 'Triaxiaalproeven single stage' with the following schema.
        It uses validate_with_schema
        """
        category = "Triaxiaalproeven single stage"
        if not self.critical:
            schema = Schema([
                Column('TXT_SS_FILENAAM_PDF', [IsEmptyValidator]),
                Column('TXT_SS_MONSTERID', [IsEmptyValidator]),
                Column('TXT_SS_GRONDSOORT',[IsEmptyValidator]),
                Column('TXT_SS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
                Column('TXT_SS_WATERGEHALTE_NA_PROEF', [InRangeValidation(0, 1000)])
            ])
        else:
            schema = Schema([
                Column('TXT_SS_TERREINSPANNING', [InRangeValidation(0, 500)]),
                Column('TXT_SS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
                Column("TXT_SS_S\'_MAX_CONSOLIDATIE", [InRangeValidation(0, 2000)]),
                Column('TXT_SS_T_MAX_CONSOLIDATIE', [InRangeValidation(0, 1000)]),
                Column("TXT_SS_S\'_EIND_CONSOLIDATIE", [InRangeValidation(0, 2000)]),
                Column('TXT_SS_T_EIND_CONSOLIDATIE', [InRangeValidation(0, 1000)]),
                Column("TXT_SS_S\'_2%", [InRangeValidation(0, 2000)]),
                Column('TXT_SS_T_2%', [InRangeValidation(0, 1000)]),
                Column("TXT_SS_S\'_5%", [InRangeValidation(0, 2000)]),
                Column('TXT_SS_T_5%', [InRangeValidation(0, 1000)]),
                Column("TXT_SS_S\'_15%", [InRangeValidation(0, 2000)]),
                Column('TXT_SS_T_15%', [InRangeValidation(0, 1000)]),
                Column("TXT_SS_S\'_BIJ_T_PIEK", [InRangeValidation(0, 2000)]),
                Column('TXT_SS_T_PIEK', [InRangeValidation(0, 1000)]),
                Column('TXT_SS_REK_BIJ_T_PIEK', [InRangeValidation(0, 40)]),
                Column("TXT_SS_S\'_BIJ_T_EIND", [InRangeValidation(0, 2000)]),
                Column('TXT_SS_T_EIND', [InRangeValidation(0, 1000)]),
                Column('TXT_SS_REK_BIJ_T_EIND', [InRangeValidation(0, 40)])
            ])
        return self.validate_with_schema(category, schema)

    def validation_log(self, save_path: Path):  # save_path is the location where the Excel file will be saved
        """
        Voert alle validaties uit en genereert een Excel-bestand en een logbestand.

        Parameters:
            save_path (str): Pad waar het Excel-bestand moet worden opgeslagen.
            critical is true if only critical errors should be tested. critical is false will only return warnings. default is True

        Returns:
            lijst met strings: Logbestand met alle foutmeldingen.
        """
        # A dictionary to hold the validation DataFrames and error logs
        validation_results = {}
        error_logs = []

        # List of validation functions to call
        if not self.critical:
            validation_functions = [
                self.validate_alg,
                self.validate_kenmerken_boring,
                self.validate_clas,
                self.validate_crs,
                self.validate_samendrukking,
                self.validate_monster,
                self.validate_triaxiaal,
                self.validate_dss,
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

                self.validate_kenmerken_boring,
                self.validate_clas,
                self.validate_crs,
                self.validate_samendrukking,
                self.validate_monster,
                self.validate_triaxiaal,
                self.validate_dss,
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
            #error_logs.append(f"Errors in {validation_name}:\n" + "\n".join(error_log))  # Categorize and append errors

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


