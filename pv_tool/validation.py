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

    def validate_txt(self):
        """Valideert of kolom 2 t/m 17 volledig is"""
        pass

    def check_txt(self):
        """Deze functie controleert of de triaxiaalproeven zijn uitgevoerd."""
        # of alles leeg dan geef terug False, of
        # check of kolom 2 t/m17 gevuld is. zo ja, geef terug in ALG_TRIAXIAAL = True
        # als 1 of meerdere ontbreken of foute data bevatten, geef warning.

    def check_naam_polder_dijk(self): # TODO: herschijven met pandas_schema
        """Deze functie controleert of de naam van de dijk is opgegeven, zo niet dan geeft hij een melding terug"""
        if self.dbase_df is not None:
            missing_name_mask = self.dbase_df['ALG_NAAM_POLDER_DIJK'].isnull()
            warnings = [
                f"Rij {idx}: ALG_NAAM_POLDER_DIJK is niet ingevuld"
                for idx in self.dbase_df.index[missing_name_mask]
            ]
            return warnings
        return []

    def nieuwe_functie(self):
        """jdjdksdnjdk"""

# TODO Nathan: Je kan helemaal los op alle validaties in het voorbeeldbestand van Leo. Elke validatie een eigen
    #  functie maken en toevoegen aan check_all. Mogelijk wordt de check_all dan straks wel mega groot maar we kunnen
    #  hem later misschien opsplitsen om het wat overzichtelijker te maken, per proef oid.

    def check_all(self):
        """Voert alle validaties uit"""
        warnings = []
        warnings.extend(self.check_naam_polder_dijk())
        return warnings


### Inladen van de data. Let op: dit gebeurt in de notebook in een aparte cel, maar moet voor het testen nu hier ook gebeuren

path_to_data = r"c:\Users\gebraadn0645\ARCADIS\103076457 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie\SAFE 2022 Proevenverzameling_tool_v4.2n validatie eerste opzet origineel.xlsm"
df = pd.read_excel(path_to_data, sheet_name="Dbase2", header=None)

# Find the index of the row containing "Algemene kenmerken"
row0_index = df.index[df.apply(lambda row: row.astype(str).str.contains("Algemene kenmerken").any(), axis=1)][0]

# Define the index where actual column headers start
headers_index = row0_index + 16

# Split the DataFrame into metadata and actual data
metadata_df = df.iloc[:headers_index]  # All rows up to and including headers_index
data_df = df.iloc[headers_index + 1:]  # All rows from headers_index onward

# Set the actual column names using the row at headers_index
data_df.columns = df.iloc[headers_index]

# Rename the first two columns
data_df.rename(columns={data_df.columns[0]: 'ALG__BORING_MONSTERNR', data_df.columns[1]: 'ALG__REGEL'}, inplace=True)

# Remove rows where the first column is NaN, null, or empty
data_df = data_df.dropna(subset=[data_df.columns[0]])

## Het volgende stuk knipt het dataframe op per categorie. Dit zodat:
# het makkelijker inlaadt,
# Je kan coderen dat er geen validatie plaatsvindt als de ID van die specifieke categorie leeg is,
# gebruiksvriendelijk en inzichtelijk is,
# Overzichtelijker tijdens het bouwen van de tool en
# dat je later makkelijker kan zien in welke categorie de fouten zitten

# Get the row0 values (assumes row0 is available in df at row0_index)
row0_values = df.iloc[row0_index]

# Initialize a dictionary to store the separate DataFrames
dataframes = {}

# Find the indices of the non-NaN values in row0
non_nan_indices = row0_values.dropna().index

# Iterate over each category defined by non-NaN values in row0
for i in range(len(non_nan_indices)):
    # Get the start and end index for the current category
    start_index = non_nan_indices[i]
    end_index = non_nan_indices[i + 1] if i + 1 < len(non_nan_indices) else len(data_df.columns)

    # Get the category name
    category_name = row0_values[start_index]

    # Select columns for the current category
    category_columns = ['ALG__BORING_MONSTERNR', 'ALG__REGEL'] + list(data_df.columns[start_index:end_index])

    # Create a new DataFrame for this category
    category_df = data_df[category_columns]

    # Store the DataFrame in the dictionary with the category name
    dataframes[category_name] = category_df

print(dataframes.keys())
# Now you have a dictionary `dataframes` where the keys are the category names,
# and the values are the corresponding DataFrames.


### pandas schema op de verschillende dataframes.
# Mocht het nodig zijn dan kan dit later natuurlijk makkelijk worden omgezet naar 1 dataframe

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

unique_columns = ['ALG__BORING_MONSTERNR_ID', 'MONSTER_ID', 'CLAS_MONSTERID', 'CRS_MONSTERID', 'SD_MONSTERID', 'DSS_MONSTERID', 'TXT_SS_MONSTERID']

for col in unique_columns:
    print(col, ' has unique values? ', is_unique(data_df[col]))

# Define schemas for each dataframe (example: you need 15 schemas for 15 DataFrames)
schemas = {
    "Algemene kenmerken": Schema([
        Column('ALG_NAAM_POLDER_DIJK', [CustomElementValidation(is_not_empty, "General name polder is empty")]),
        Column('ALG_REFERENTIE', [CustomElementValidation(is_not_empty, "General reference is empty")])
    ]),
    "Kenmerken van de boring": Schema([
        Column('BORING_XID', [InRangeValidation(-7000, 300000)]),
        Column('BORING_YID', [InRangeValidation(289000, 629000)]),
        Column('BORING_MAAIVELDPEIL', [InRangeValidation(-100, 500)]),
        Column('BORING_NUMMER', [CustomElementValidation(is_not_empty_and_string, "No (or incorrect) borehole numbering")]),
        Column('BORING_POSITIE', [CustomElementValidation(is_not_empty_and_string, "No (or incorrect) borehole position")]),
        Column('BORING_FILENAAM_PDF', [CustomElementValidation(is_not_empty_and_string, "No borehole log PDF")]),
        Column('BORING_FILENAAM_GEF', [CustomElementValidation(is_not_empty_and_string, "No borehole log GEF")])
    ]),
    "Monster": Schema([
        Column('MONSTER_ID', [CustomElementValidation(is_not_empty, "No sample ID")]),
        Column('MONSTER_NIVEAU_NAP_VANAF', [InRangeValidation(-100, 500)]),
        Column('MONSTER_NIVEAU_NAP_TOT', [InRangeValidation(-100, 500)])
    ]),
    "Classificatie": Schema([
        Column('CLAS_MONSTERID', [CustomElementValidation(is_not_empty, "No classification sample ID")]),
        Column('CLAS_GRONDSOORT', [CustomElementValidation(is_not_empty, "No soil type classification")]),
        Column('CLAS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
        Column('CLAS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
        Column('CLAS_VOLUMEGEWICHT_DRG', [InRangeValidation(0, 25)]),
        Column('CLAS_WATERGEHALTE', [InRangeValidation(0, 1000)])
    ]),
    #"Atterbergsche grenzen": Schema([

    #]),
    #"Veenclassificatie": Schema([

    #]),
    #"Korrelverdeling zeefproef en fractieverdeling": Schema([

    #]),
    # "Kenmerken van de sondering" alleen uitvoeren als validatie triaxiaal of DDS = OK. Hoe toevoegen?
    "Kenmerken van de sondering": Schema([
        Column('CPT_QNET', [InRangeValidation(0, 5000)])
    ]),
    "Constant rate of strain proeven (CRS)": Schema([
        Column('CRS_FILENAAM_PDF', [CustomElementValidation(is_not_empty, "No CRS PDF")]),
        Column('CRS_MONSTERID', [CustomElementValidation(is_not_empty, "No CRS sample ID")]),
        Column('CRS_GRONDSOORT', [CustomElementValidation(is_not_empty, "No soil type classification for CRS")]),
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
    ]),
    "Samendrukkingsproeven": Schema([
        Column('SD_FILENAAM_PDF', [CustomElementValidation(is_not_empty, "No samendrukkingsproef PDF")]),
        Column('SD_MONSTERID', [CustomElementValidation(is_not_empty, "No samendrukkingsproef sample ID")]),
        Column('SD_GRONDSOORT', [CustomElementValidation(is_not_empty, "No soil type classification for samendrukkingsproef")]),
        Column('SD_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
        Column('SD_TERREINSPANNING', [InRangeValidation(0, 500)]),
        Column('SD_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
        # Column('SD_VOLUMEGEWICHT_DR', [InRangeValidation(0, 25)]),
        Column('SD_WATERGEHALTE_INI', [InRangeValidation(0, 1000)]),
        Column('SD_ISOTACHE_A', [InRangeValidation(0, 0.1)]),
        Column('SD_ISOTACHE_B', [InRangeValidation(0, 1)]),
        Column('SD_ISOTACHE_C', [InRangeValidation(0, 0.1)]),
        Column('SD_ISOTACHE_GRENSSPANNING_A', [InRangeValidation(0, 1000)])
    ]),
    "DSS-proeven": Schema([
        Column('DSS_FILENAAM_PDF', [CustomElementValidation(is_not_empty, "No DSS PDF")]),
        Column('DSS_MONSTERID', [CustomElementValidation(is_not_empty, "No DSS sample ID")]),
        Column('DSS_GRONDSOORT',
               [CustomElementValidation(is_not_empty, "No soil type classification for DSS")]),
        Column('DSS_MONSTERNIVEAU', [InRangeValidation(-100, 500)]),
        Column('DSS_TERREINSPANNING', [InRangeValidation(0, 500)]),
        Column('DSS_VOLUMEGEWICHT_NAT', [InRangeValidation(8, 25)]),
        Column('DSS_WATERGEHALTE_VOOR', [InRangeValidation(0, 1000)]),
        Column('DSS_MAX_EFF_VERT_SPANNING_CONSOLIDATIE', [InRangeValidation(0, 2000)]),
        Column('DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE', [InRangeValidation(0, 2000)]),
    ]),
    "Triaxiaalproeven single stage": Schema([
        Column('Family Name', [CustomElementValidation(is_not_empty, "Veld is leeg")]),
        Column('Age', [InRangeValidation(20, 60)]),
        Column('Sex', [InListValidation(['Male', 'Female', 'Other'])]),
        Column('Customer ID', [MatchesPatternValidation(r'\d{4}[A-Z]{4}')])
    ]),
    "Triaxiaalproeven multistage": Schema([
        Column('Family Name', [CustomElementValidation(is_not_empty, "Veld is leeg")]),
        Column('Age', [InRangeValidation(49, 51)]),
        Column('Sex', [InListValidation(['Male', 'Female', 'Other'])]),
        Column('Customer ID', [MatchesPatternValidation(r'\d{4}[A-Z]{4}')])
    ]),
    "Beschrijving proefresultaten": Schema([
        Column('Family Name', [CustomElementValidation(is_not_empty, "Veld is leeg")]),
        Column('Age', [InRangeValidation(20, 60)]),
        Column('Sex', [InListValidation(['Male', 'Female', 'Other'])]),
        Column('Customer ID', [MatchesPatternValidation(r'\d{4}[A-Z]{4}')])
    ]),
    "controle berekening terreinspanning": Schema([
        Column('Family Name', [CustomElementValidation(is_not_empty, "Veld is leeg")]),
        Column('Age', [InRangeValidation(49, 51)]),
        Column('Sex', [InListValidation(['Male', 'Female', 'Other'])]),
        Column('Customer ID', [MatchesPatternValidation(r'\d{4}[A-Z]{4}')])
    ])


}

# Initialize a dictionary to hold validation results
validation_results = {}

# Validate the first 15 DataFrames in `dataframes`
for i, (category, df) in enumerate(dataframes.items()):
    if i >= 15:  # Only process the first 15 DataFrames
        break
    print(category)
    # Get the schema corresponding to this category
    schema = schemas.get(category)
    if not schema:
        print(f"No schema defined for category: {category}")
        continue

    # Filter the DataFrame to only include columns present in the schema
    schema_columns = [col.name for col in schema.columns]
    data_to_validate = df[schema_columns]

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

    # Store the validation result in the dictionary
    validation_results[category] = validation_df

## Vervang de eerste kolommen in de algemene kenmerken dataframe met validatie of de proeven zijn uitgevoerd
# Het zou 'Null' moeten geven als alle validatie kolommen vol zijn (overal errors, de proef is niet uitgevoerd)
# Het zou 'error' moeten geven als sommige validatie kolommen vol zijn (proef wel uitgevoerd maar er zitten fouten in)
# Het zou 'OK' moeten geven als alle validatie kolommen leeg zijn (geen opmerkingen)


general_validation = []
for category in ['Classificatie', 'Constant rate of strain proeven (CRS)', 'Samendrukkingsproeven', 'DSS-proeven', 'Triaxiaalproeven single stage']:
    validation_column_list = []
    schema = schemas.get(category)
    if not schema:
        print(f"No schema defined for category: {category}")
    # pak de validatie kolommen
    schema_columns = [f"{col.name}_validate" for col in schema.columns]
    for i in range(len(validation_results[category])):
        data = [validation_results[category][schema_column].iloc[i] for schema_column in schema_columns]
        if not data or all(item == '' for item in data) or all(isinstance(item, float) and math.isnan(item) for item in data):
            validation_column_list.append('OK')
        elif all(data):
            validation_column_list.append('Null')
            for schema_column in schema_columns:
                validation_results[category].at[i, schema_column] = ''  # Als overal errors zijn is de proef niet uitgevoerd dus haal dan de errors eruit
        else:
            validation_column_list.append('Error')

    general_validation.append(validation_column_list)


validation_results['Algemene kenmerken']['ALG__CLASSIFICATIE']  = general_validation[0]
validation_results['Algemene kenmerken']['ALG__CRS']            = general_validation[1]
validation_results['Algemene kenmerken']['ALG__SAMENDRUKKING']  = general_validation[2]
validation_results['Algemene kenmerken']['ALG__DSS']            = general_validation[3]
validation_results['Algemene kenmerken']['ALG__TRIAXIAAL']      = general_validation[4]


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