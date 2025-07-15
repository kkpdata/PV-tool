# In deze file wil ik alle code opslaan wat betreft de validatie van de import
# Kijk in de file van Leo:
# C:\Users\deenekat7271\ARCADIS\30287614 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie
# welke kolommen we allemaal moeten valideren.

from typing import Optional
from pandas import DataFrame
import pandas as pd
from io import StringIO
from pandas_schema import Column, Schema
from pandas_schema.validation import (
    CustomElementValidation, CanCallValidation, LeadingWhitespaceValidation, TrailingWhitespaceValidation,
    InRangeValidation, InListValidation, MatchesPatternValidation
)
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import math

###
class Validation:
    """In deze class staan alle functies die de validatie uitvoeren."""

    def __init__(self, dbase_df: Optional[DataFrame] = None):
        self.dbase_df = dbase_df

    def split_dbase(self):
        """hier komt  per proef een df uit in een library van dataframes"""
        """deze zijn later aan te roepen door bijvoorbeeld df_algemeen = dataframes['Algemene kenmerken']"""

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

        # Dictionary to store resulting dataframes
        self.dataframes = {}

        # Split dataframe based on column prefixes
        for name, prefix in prefix_mapping.items():
            # Filter columns based on the prefix
            filtered_columns = [col for col in self.dbase_df.columns if col.startswith(prefix)]

            # Create a new dataframe with those columns
            self.dataframes[name] = self.dbase_df[filtered_columns]
        return self.dataframes
        pass

    def validation_selection(self, df, category):
        """Deze functie bepaalt welke rijen door gaan naar de validatie, gebaseerd op de kolom in algemene kenmerken. Als de waarde = FALSE wordt de rij verwijderd"""
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

        # Ensure 'uitgevoerd' and 'df_to_check' have the same index
        if not uitgevoerd.index.equals(df_to_check.index):
            raise ValueError("Indices van 'uitgevoerd' en 'df_to_check' komen niet overeen")

        # Only keep rows where 'uitgevoerd' is True
        valid_indices = uitgevoerd[uitgevoerd == True].index
        df_to_check_filtered = df_to_check.loc[valid_indices]

        return df_to_check_filtered

        pass

    # Define validation functions
    def is_not_empty(value):
        return value != "" and not pd.isna(value)

    def is_not_empty_and_string(value):
        return isinstance(value, str) and value.strip() != "" and not pd.isna(value)

    # Check welke van de ID kolommen unieke waardes bevatten
    def is_unique(series):
        # Filter out empty strings and NaN values
        non_empty_values = series.dropna().loc[series != ""]
        print(len(non_empty_values), len(non_empty_values.unique()))
        return len(non_empty_values) == len(non_empty_values.unique())

    def validate_with_schema(self, category, schema):
        df = self.split_dbase()[category]

        if category in ['Classificatie', 'Constant rate of strain proeven (CRS)', 'Samendrukkingsproeven', 'DSS-proeven', 'Triaxiaalproeven single stage']:
            df = self.validation_selection(df, category)

        # Filter the DataFrame to only include columns present in the schema
        schema_columns = [col.name for col in schema.columns]
        data_to_validate = df[schema_columns]

        # Validate the data
        errors = schema.validate(data_to_validate)

        error_log = []

        # Prepare a DataFrame for validation errors
        validation_df = data_to_validate.copy()

        # Populate the validation columns with error messages
        for column in schema_columns:
            validation_df[f"{column}_validate"] = ""  # Add validation column with empty strings
            # Move the validation column to the right of the original column
            col_position = validation_df.columns.get_loc(column) + 1
            validation_df.insert(col_position, f"{column}_validate", validation_df.pop(f"{column}_validate"))

        for error in errors:
            row = error.row
            column = error.column
            error_message = error.message
            validation_df.at[row, f"{column}_validate"] = error_message
            error_log.append(f"error in row '{row}' and column '{column}': {error_message}")

        # Add extra validation summary rows at the top
        summary_row_1 = []
        summary_row_2 = []

        for col in schema_columns:
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

        # Prepend the summary rows using pd.concat
        summary_df = pd.DataFrame([summary_row_1, summary_row_2], columns=validation_df.columns)
        validation_df = pd.concat([summary_df, validation_df], ignore_index=True)

        return validation_df, error_log
        pass

    def validate_alg(self):
        category = "Algemene kenmerken"
        schema = Schema([
            Column('ALG_NAAM_POLDER_DIJK', [CustomElementValidation(is_not_empty, "General name polder is empty")]),
            Column('ALG_REFERENTIE', [CustomElementValidation(is_not_empty, "General reference is empty")])
        ])
        return self.validate_with_schema(category, schema)
        pass

    def validate_kenmerken_boring(self):
        category = "Kenmerken van de boring"
        schema = Schema([
            Column('BORING_XID', [InRangeValidation(-7000, 300000)]),
            Column('BORING_YID', [InRangeValidation(289000, 629000)]),
            Column('BORING_MAAIVELDPEIL', [InRangeValidation(-100, 500)]),
            Column('BORING_NUMMER',
                   [CustomElementValidation(self.is_not_empty_and_string, "No (or incorrect) borehole numbering")]),
            Column('BORING_POSITIE',
                   [CustomElementValidation(self.is_not_empty_and_string, "No (or incorrect) borehole position")]),
            Column('BORING_FILENAAM_PDF', [CustomElementValidation(self.is_not_empty_and_string, "No borehole log PDF")]),
            Column('BORING_FILENAAM_GEF', [CustomElementValidation(self.is_not_empty_and_string, "No borehole log GEF")])
        ])
        return self.validate_with_schema(category, schema)
        pass

    def validate_monster(self):
        category = "Monster"
        schema = Schema([
            Column('MONSTER_ID', [CustomElementValidation(self.is_not_empty, "No sample ID")]),
            Column('MONSTER_NIVEAU_NAP_VANAF', [InRangeValidation(-100, 500)]),
            Column('MONSTER_NIVEAU_NAP_TOT', [InRangeValidation(-100, 500)])
        ])
        return self.validate_with_schema(category, schema)
        pass

    def validate_clas(self):
        category = "Classificatie"
        schema = Schema([
        Column('CLAS_MONSTERID', [CustomElementValidation(self.is_not_empty, "No classification sample ID")]),
        Column('CLAS_GRONDSOORT', [CustomElementValidation(self.is_not_empty, "No soil type classification")]),
        Column('CLAS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
        Column('CLAS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
        Column('CLAS_VOLUMEGEWICHT_DRG', [InRangeValidation(0, 25)]),
        Column('CLAS_WATERGEHALTE', [InRangeValidation(0, 1000)])
    ])

        return self.validate_with_schema(category, schema)
        pass

    def validate_kenmerken_sondering(self):
        category = "Kenmerken van de sondering"
        schema = Schema([
            Column('CPT_QNET', [InRangeValidation(0, 5000)])
        ])
        return self.validate_with_schema(category, schema)
        pass

    def validate_csr(self):
        category = "Constant rate of strain proeven (CRS)"
        schema = Schema([
            Column('CRS_FILENAAM_PDF', [CustomElementValidation(self.is_not_empty, "No CRS PDF")]),
            Column('CRS_MONSTERID', [CustomElementValidation(self.is_not_empty, "No CRS sample ID")]),
            Column('CRS_GRONDSOORT', [CustomElementValidation(self.is_not_empty, "No soil type classification for CRS")]),
            Column('CRS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
            Column('CRS_TERREINSPANNING', [InRangeValidation(0, 500)]),
            Column('CRS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
            Column('CRS_VOLUMEGEWICHT_DRG', [InRangeValidation(0, 25)]),
            Column('CRS_WATERGEHALTE_VOOR', [InRangeValidation(0, 1000)]),
            Column('CRS_GRENSSPANNING_A', [InRangeValidation(0, 1000)]),
            Column('CRS_REK_BIJ_GRENSSPANNING_A', [InRangeValidation(0, 100)]),
            Column('CRS_ISOTACHE_A', [InRangeValidation(0, 0.1)]),
            Column('CRS_ISOTACHE_B', [InRangeValidation(0, 1)]),
            Column('CRS_ISOTACHE_C', [InRangeValidation(0, 0.1)])
        ])
        return self.validate_with_schema(category, schema)
        pass

    def validate_samendrukking(self):
        category = "Samendrukkingsproeven"
        schema = Schema([
            Column('SD_FILENAAM_PDF', [CustomElementValidation(self.is_not_empty, "No samendrukkingsproef PDF")]),
            Column('SD_MONSTERID', [CustomElementValidation(self.is_not_empty, "No samendrukkingsproef sample ID")]),
            Column('SD_GRONDSOORT',
                   [CustomElementValidation(self.is_not_empty, "No soil type classification for samendrukkingsproef")]),
            Column('SD_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
            Column('SD_TERREINSPANNING', [InRangeValidation(0, 500)]),
            Column('SD_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
            # Column('SD_VOLUMEGEWICHT_DR', [InRangeValidation(0, 25)]),
            Column('SD_WATERGEHALTE_INI', [InRangeValidation(0, 1000)]),
            Column('SD_ISOTACHE_A', [InRangeValidation(0, 0.1)]),
            Column('SD_ISOTACHE_B', [InRangeValidation(0, 1)]),
            Column('SD_ISOTACHE_C', [InRangeValidation(0, 0.1)]),
            Column('SD_ISOTACHE_GRENSSPANNING_A', [InRangeValidation(0, 1000)])
        ])
        return self.validate_with_schema(category, schema)
        pass

    def validate_dss(self):
        category = "DSS-proeven"
        schema = Schema([
            Column('DSS_FILENAAM_PDF', [CustomElementValidation(self.is_not_empty, "No DSS PDF")]),
            Column('DSS_MONSTERID', [CustomElementValidation(self.is_not_empty, "No DSS sample ID")]),
            Column('DSS_GRONDSOORT',
                   [CustomElementValidation(self.is_not_empty, "No soil type classification for DSS")]),
            Column('DSS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
            Column('DSS_TERREINSPANNING', [InRangeValidation(0, 500)]),
            Column('DSS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
            Column('DSS_WATERGEHALTE_VOOR', [InRangeValidation(0, 1000)]),
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
        pass

    def validate_triaxiaal(self):
        category = "Triaxiaalproeven single stage"
        schema = Schema([
            Column('TXT_SS_FILENAAM_PDF', [CustomElementValidation(self.is_not_empty, "No TXT_SS PDF")]),
            Column('TXT_SS_MONSTERID', [CustomElementValidation(self.is_not_empty, "No TXT_SS sample ID")]),
            Column('TXT_SS_GRONDSOORT',
                   [CustomElementValidation(self.is_not_empty, "No soil type classification for TXT_SS")]),
            Column('TXT_SS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
            Column('TXT_SS_TERREINSPANNING', [InRangeValidation(0, 500)]),
            Column('TXT_SS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
            Column('TXT_SS_WATERGEHALTE_NA_PROEF', [InRangeValidation(0, 1000)]),
            Column("TXT_SS_S'_MAX_CONSOLIDATIE", [InRangeValidation(0, 2000)]),
            Column('TXT_SS_T_MAX_CONSOLIDATIE', [InRangeValidation(0, 1000)]),
            Column("TXT_SS_S'_EIND_CONSOLIDATIE", [InRangeValidation(0, 2000)]),
            Column('TXT_SS_T_EIND_CONSOLIDATIE', [InRangeValidation(0, 1000)]),
            Column("TXT_SS_S'_2%", [InRangeValidation(0, 2000)]),
            Column('TXT_SS_T_2%', [InRangeValidation(0, 1000)]),
            Column("TXT_SS_S'_5%", [InRangeValidation(0, 2000)]),
            Column('TXT_SS_T_5%', [InRangeValidation(0, 1000)]),
            Column("TXT_SS_S'_10%", [InRangeValidation(0, 2000)]),
            Column('TXT_SS_T_10%', [InRangeValidation(0, 1000)]),
            Column("TXT_SS_S'_15%", [InRangeValidation(0, 2000)]),
            Column('TXT_SS_T_15%', [InRangeValidation(0, 1000)]),
            Column("TXT_SS_S'_BIJ_T_PIEK", [InRangeValidation(0, 2000)]),
            Column('TXT_SS_T_PIEK', [InRangeValidation(0, 1000)]),
            Column('TXT_SS_REK_BIJ_T_PIEK', [InRangeValidation(0, 40)]),
            Column("TXT_SS_S'_BIJ_T_EIND", [InRangeValidation(0, 2000)]),
            Column('TXT_SS_T_EIND', [InRangeValidation(0, 1000)]),
            Column('TXT_SS_REK_BIJ_T_EIND', [InRangeValidation(0, 40)])
        ])

        return self.validate_with_schema(category, schema)
        pass

    def validate_ana(self):
        category = "Analyse"
        schema = Schema([
            Column('ANA_GRENSSPANNING', [InRangeValidation(0, 1000)]),
            Column('ANA_GRENSSPANNING_HANDMATIG', [InRangeValidation(0, 1000)])

        ])
        return self.validate_with_schema(category, schema)
        pass





# TODO Nathan: Je kan helemaal los op alle validaties in het voorbeeldbestand van Leo. Elke validatie een eigen
    #  functie maken en toevoegen aan check_all. Mogelijk wordt de check_all dan straks wel mega groot maar we kunnen
    #  hem later misschien opsplitsen om het wat overzichtelijker te maken, per proef oid.

    import pandas as pd

    def validation_log(self, save_path):  # save_path is the location where the Excel file will be saved
        """
        Voert alle validaties uit en genereert een Excel-bestand en een logbestand.

        Parameters:
            save_path (str): Pad waar het Excel-bestand moet worden opgeslagen.

        Returns:
            str: Logbestand met alle foutmeldingen.
        """
        # A dictionary to hold the validation DataFrames and error logs
        validation_results = {}
        error_logs = []

        # List of validation functions to call
        validation_functions = [
            self.validate_alg,
            self.validate_kenmerken_boring,
            self.validate_clas,
            self.validate_csr,
            self.validate_kenmerken_sondering,
            self.validate_samendrukking,
            self.validate_monster,
            self.validate_triaxiaal,
            self.validate_dss,
            self.validate_ana
        ]

        # Iterate through each validation function and collect the results
        for func in validation_functions:
            validation_name = func.__name__  # Get the name of the function (e.g., 'validate_alg')
            validation_df, error_log = func()  # Call the function and get its output

            # Store the validation DataFrame and error log
            validation_results[validation_name] = validation_df
            error_logs.append(f"Errors in {validation_name}:\n" + "\n".join(error_log))  # Categorize and append errors

        # Create the Excel file with each validation_df as a separate sheet
        with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
            for sheet_name, validation_df in validation_results.items():
                validation_df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Combine all error logs into a single log string
        combined_error_log = "\n\n".join(error_logs)

        return combined_error_log


### Inladen van de data. Let op: dit gebeurt in de functie import, maar moet voor het testen nu hier ook gebeuren

path_to_data = r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel.xlsm"


## Vervang de eerste kolommen in de algemene kenmerken dataframe met validatie of de proeven zijn uitgevoerd
# Het zou 'Null' moeten geven als alle validatie kolommen vol zijn (overal errors, de proef is niet uitgevoerd)
# Het zou 'error' moeten geven als sommige validatie kolommen vol zijn (proef wel uitgevoerd maar er zitten fouten in)
# Het zou 'OK' moeten geven als alle validatie kolommen leeg zijn (geen opmerkingen)

# Deze vervalt en wordt vervangen door een TRUE/FALSE bij het inladen van de data - geschreven door Tjalda in import
# even laten staan als backup voor het geval we dit toch willen

# general_validation = []
# for category in ['Classificatie', 'Constant rate of strain proeven (CRS)', 'Samendrukkingsproeven', 'DSS-proeven', 'Triaxiaalproeven single stage']:
#     validation_column_list = []
#     schema = schemas.get(category)
#     if not schema:
#         print(f"No schema defined for category: {category}")
#     # pak de validatie kolommen
#     schema_columns = [f"{col.name}_validate" for col in schema.columns]
#     for i in range(len(validation_results[category])):
#         data = [validation_results[category][schema_column].iloc[i] for schema_column in schema_columns]
#         if not data or all(item == '' for item in data) or all(isinstance(item, float) and math.isnan(item) for item in data):
#             validation_column_list.append('OK')
#         elif all(data):
#             validation_column_list.append('Null')
#             for schema_column in schema_columns:
#                 validation_results[category].at[i, schema_column] = ''  # Als overal errors zijn is de proef niet uitgevoerd dus haal dan de errors eruit
#         else:
#             validation_column_list.append('Error')
#
#     general_validation.append(validation_column_list)
#
#
# validation_results['Algemene kenmerken']['ALG__CLASSIFICATIE']  = general_validation[0]
# validation_results['Algemene kenmerken']['ALG__CRS']            = general_validation[1]
# validation_results['Algemene kenmerken']['ALG__SAMENDRUKKING']  = general_validation[2]
# validation_results['Algemene kenmerken']['ALG__DSS']            = general_validation[3]
# validation_results['Algemene kenmerken']['ALG__TRIAXIAAL']      = general_validation[4]


### test met test data
# Define a validation function
def is_not_empty(value):
    return value != "" and not pd.isna(value)

def is_unique(series):
    return len(series) == len(series.unique())

# Validation rule for uniqueness
unique_validation = CustomElementValidation(is_unique, "is not unique")

# Which columns should not be empty
warning_empty_columns = ['Family Name', 'Sex']

# Define the schema
schema = Schema([
    Column('Family Name', [CustomElementValidation(is_not_empty, "Veld is leeg")]),
    Column('Age', [InRangeValidation(20,80)]),
    Column('Sex', [InListValidation(['Male', 'Female', 'Other'])]),
    Column('Customer ID', [MatchesPatternValidation(r'\d{4}[A-Z]{4}')])
])

# Load the test data
test_data = pd.read_csv(StringIO('''Given Name,Family Name,Age,Sex,Customer ID
Gerald ,Hampton,82, ,2582GABK
Yuuwa, ,82,male,7951WVLW
Edyta,Majewska ,50,Female,775ANSID
'''))

# Filter the DataFrame to only include columns present in the schema
schema_columns = [col.name for col in schema.columns]
data_to_validate = test_data[schema_columns]

# Validate the data
errors = schema.validate(data_to_validate)

# Prepare a DataFrame for validation errors
validation_df = data_to_validate.copy()

# Populate the validation columns with error messages
for column in schema_columns:
    validation_df[f"{column}_validate"] = ""  # Add validation column with empty strings
    # Move the validation column to the right of the original column
    col_position = validation_df.columns.get_loc(column) + 1
    validation_df.insert(col_position, f"{column}_validate", validation_df.pop(f"{column}_validate"))

for error in errors:
    row = error.row
    column = error.column
    error_message = error.message
    validation_df.at[row, f"{column}_validate"] = error_message

# Add extra validation rows at the top
summary_row_1 = []
summary_row_2 = []

for col in schema_columns:
    original_column_data = test_data[col]
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

# Prepend the summary rows using pd.concat
summary_df = pd.DataFrame([summary_row_1, summary_row_2], columns=validation_df.columns)
validation_df = pd.concat([summary_df, validation_df], ignore_index=True)

# Export the validation DataFrame to an Excel file
output_path = r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\pandas_schema_test.xlsx"
validation_df.to_excel(output_path, index=False)

# Load the workbook and select the active worksheet
workbook = load_workbook(output_path)
worksheet = workbook.active

# Set text wrapping and adjust column width
for column_cells in worksheet.columns:
    # Set the column width to twice the default size (default is about 8.43 in Excel)
    new_column_width = 16.86
    worksheet.column_dimensions[column_cells[0].column_letter].width = new_column_width

    for cell in column_cells:
        # Apply text wrapping
        cell.alignment = Alignment(wrap_text=True)

# Save the changes
workbook.save(output_path)

print("Validation results exported successfully.")