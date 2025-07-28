from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from typing import Optional, List, Literal
import pandas as pd
from datetime import datetime
from pathlib import Path
from pv_tool.imports.validate_catagories import (validate_monster, validate_clas, validate_triaxiaal, validate_crs,
                                                 validate_dss, validate_samendrukking, validate_alg,
                                                 validate_kenmerken_boring)

if TYPE_CHECKING:
    from pv_tool.imports.import_data import Dbase


class Validation:
    """In deze class staan alle functies die nodig zijn om de validatie uit te voeren."""

    def __init__(self, dbase: Dbase,
                 critical: Optional[bool] = True):
        self.dbase_df = dbase.dbase_df
        self.dataframes: Optional[Dict] = None
        self.critical = critical
        self.total_error_log: Optional[List] = None

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

        if self.dbase_df is None:
            raise ValueError("dbase_df is not initialized. Please ensure it is loaded properly.")

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
        """Deze functie verwijderd rijen uit de dataframes waar geen proef is gedaan."""
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

    def validation_log(self, export_path: Path):
        """
        Voert alle validaties uit en genereert een Excel-bestand (logbestand)."""
        if export_path.is_dir():
            file_name = f"validation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            export_path = export_path / file_name
        elif export_path.suffix != ".xlsx":
            raise ValueError("Als save_path een bestandspad is, moet het de extensie '.xlsx' bevatten.")

        print(f"{export_path=}") # TODO: foutmelding maar tot hier gaat sowieso goed

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
                validation_results[func_name] = validation_df
                error_logs.extend(error_log)

            sheet_names_print = []
            with pd.ExcelWriter(str(export_path), engine="xlsxwriter") as writer:
                for func_name, validation_df in validation_results.items():
                    sheet_name = func_name.upper()
                    sheet_names_print.append(sheet_name)
                    validation_df.to_excel(writer, sheet_name=sheet_name, index=True)

            self.total_error_log = error_logs

        except Exception as e:
            print(f"Er trad een fout op tijdens validatie of het schrijven van Excel: {str(e)}")
            raise e
