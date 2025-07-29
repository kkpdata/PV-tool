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


def validate_alg(self: Validation):
    """Deze functie valideert de kolommen van het dataframe 'algemene kenmerken'."""
    if not self.critical:
        schema = Schema([
            Column('ALG_NAAM_POLDER_DIJK', [IsEmptyValidator]),
            Column('ALG_REFERENTIE', [IsEmptyValidator])
        ])
        return self.validate_with_schema(category="Algemene kenmerken", schema=schema)


def validate_kenmerken_boring(self: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Kenmerken van de boring'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
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
    return self.validate_with_schema(category="Kenmerken van de boring", schema=schema)


def validate_monster(self: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Monster'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
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
    return self.validate_with_schema(category="Monster", schema=schema)


def validate_clas(self: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Classificatie'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
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
    return self.validate_with_schema(category="Classificatie", schema=schema)


def validate_crs(self: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Constant rate of strain proeven (CRS)'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
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
    return self.validate_with_schema(category="Constant rate of strain proeven (CRS)", schema=schema)


def validate_samendrukking(self: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Samendrukkingsproeven'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
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
    return self.validate_with_schema(category="Samendrukkingsproeven", schema=schema)


def validate_dss(self: Validation):
    """Deze functie valideert de kolommen van het dataframe 'DSS-proeven'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
    if not self.critical:
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
    return self.validate_with_schema(category="DSS-proeven", schema=schema)


def validate_triaxiaal(self: Validation):
    """Deze functie valideert de kolommen van het dataframe 'Triaxiaalproeven single stage'.
    Hierbij wordt onderscheid gemaakt tussen kritieke en niet kritieke kolommen."""
    if not self.critical:
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
    return self.validate_with_schema(category="Triaxiaalproeven single stage", schema=schema)
