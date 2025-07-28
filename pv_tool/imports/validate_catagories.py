from __future__ import annotations
import pandas as pd
from pandas_schema import Column, Schema
from pandas_schema.validation import CustomElementValidation, InRangeValidation
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.imports.validation import Validation


IsEmptyValidator = CustomElementValidation(
    lambda value: value != "" and not pd.isna(value), "This cell is empty"
)


def validate_alg(validation_instance: Validation):
    """Deze functie valideert de kolommen van het dataframe 'algemene kenmerken'."""
    if not validation_instance.critical:
        schema = Schema([
            Column('ALG_NAAM_POLDER_DIJK', [IsEmptyValidator]),
            Column('ALG_REFERENTIE', [IsEmptyValidator])
        ])
        return validate_with_schema(validation_instance, category="Algemene kenmerken", schema=schema)


def validate_kenmerken_boring(validation_instance: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Kenmerken van de boring'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
    if not validation_instance.critical:
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
    print(schema)
    return validate_with_schema(validation_instance, category="Kenmerken van de boring", schema=schema)


def validate_monster(validation_instance: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Monster'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
    if not validation_instance.critical:
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
    return validate_with_schema(validation_instance, category="Monster", schema=schema)


def validate_clas(validation_instance: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Classificatie'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
    if not validation_instance.critical:
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
    print("Schema:", schema)
    return validate_with_schema(validation_instance, category="Classificatie", schema=schema)


def validate_crs(validation_instance: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Constant rate of strain proeven (CRS)'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
    if not validation_instance.critical:
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

    return validate_with_schema(validation_instance, category="Constant rate of strain proeven (CRS)", schema=schema)


def validate_samendrukking(validation_instance: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Samendrukkingsproeven'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
    if not validation_instance.critical:
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
    return validate_with_schema(validation_instance, category="Samendrukkingsproeven", schema=schema)


def validate_dss(validation_instance: Validation):
    """Deze functie valideert de kolommen van het dataframe 'DSS-proeven'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
    if not validation_instance.critical:
        schema = Schema([
            Column('DSS_FILENAAM_PDF', [IsEmptyValidator]),
            Column('DSS_FILENAAM_SPANNINGSPAD', [IsEmptyValidator]),
            Column('DSS_MONSTERID', [IsEmptyValidator]),
            Column('DSS_GRONDSOORT', [IsEmptyValidator]),
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
    return validate_with_schema(validation_instance, category="DSS-proeven", schema=schema)


def validate_triaxiaal(validation_instance: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Triaxiaalproeven single stage'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
    if not validation_instance.critical:
        schema = Schema([
            Column('TXT_SS_FILENAAM_PDF', [IsEmptyValidator]),
            Column('TXT_SS_MONSTERID', [IsEmptyValidator]),
            Column('TXT_SS_GRONDSOORT', [IsEmptyValidator]),
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
    return validate_with_schema(validation_instance, category="Triaxiaalproeven single stage", schema=schema)


def validate_with_schema(validation_instance: Validation, category, schema: Schema):
    """Valideert de dataframes per categorie en gebruikt het bijbehorende schema. Deze functie wordt aangeroepen
    in elke individuele validatiefunctie, waar het schema voor elke categorie wordt gemaakt."""
    df = validation_instance.split_dbase().get(category, pd.DataFrame())
    schema_columns = [col.name for col in schema.columns]

    missing_columns = [col for col in schema_columns if col not in df.columns]
    if missing_columns:
        print(f"Missing columns in category '{category}': {', '.join(missing_columns)}")

    available_columns = [col for col in schema_columns if col in df.columns]
    data_to_validate = df[available_columns]

    errors = schema.validate(data_to_validate)

    validation_df = data_to_validate.copy()
    error_log = []

    for column in available_columns:
        validation_df[f"{column}_validate"] = ""
        col_position = validation_df.columns.get_loc(column) + 1
        validation_df.insert(col_position, f"{column}_validate", validation_df.pop(f"{column}_validate"))

    for error in errors:
        row, column, error_message = error.row, error.column, error.message
        validation_df.at[row, f"{column}_validate"] = error_message
        error_log.append([row, column, error_message])

    def row_has_errors(row_index):
        row_data = [
            validation_df[f"{col}_validate"].loc[row_index]
            for col in available_columns
        ]
        if not row_data:
            return False
        if all(item == "" for item in row_data):
            return False
        if all(isinstance(item, float) and pd.isna(item) for item in row_data):
            return False
        return True

    rows_to_keep = [i for i in validation_df.index if row_has_errors(i)]
    validation_df = validation_df.loc[rows_to_keep]

    error_log = [error for error in error_log if error[0] in validation_df.index]

    summary_row_1 = []
    summary_row_2 = []

    for col in available_columns:
        original_column_data = df[col]
        validation_column_data = validation_df[f"{col}_validate"]

        if original_column_data.isnull().all():
            summary_row_1.append('geen data')
        elif validation_column_data.str.strip().any():
            summary_row_1.append('fouten gevonden')
        else:
            summary_row_1.append('geen fouten gevonden')

        summary_row_1.append('')
        summary_row_2.append('')
        # summary_row_2.append(validation_df[f"{col}_validate"]
        #                      .apply(lambda x: bool(str(x).strip()) if pd.notna(x) else False)
        #                      .sum())
        summary_row_2.append(
            validation_column_data.apply(lambda x: bool(str(x).strip()) if pd.notna(x) else False).sum()
        )

    initial_index = validation_df.index.tolist()
    new_index = ['samenvatting', 'aantal fouten'] + initial_index

    summary_df = pd.DataFrame([summary_row_1, summary_row_2], columns=validation_df.columns)
    validation_df = pd.concat([summary_df, validation_df], ignore_index=True)
    validation_df.index = new_index

    return validation_df, error_log
