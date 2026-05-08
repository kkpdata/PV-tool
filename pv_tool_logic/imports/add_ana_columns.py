from __future__ import annotations
from typing import TYPE_CHECKING
import pandas as pd
import numpy as np

if TYPE_CHECKING:
    from pv_tool_logic.imports.import_data import Dbase


def add_columns(self: Dbase):
    """
    Voegt analyse kolommen toe in de gespecificeerde volgorde aan het einde van de DataFrame,
    waarbij data in 'preserve_cols' behouden blijft indien aanwezig.
    """
    analysis_columns = [
        "ANA_TERREINSPANNING",
        "ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING",
        "ANA_DSS_MAX_CONSOLIDATIE_SPANNING",
        "ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL",
        "ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG",
        "ANA_TXT_CONSOLIDATIE_TYPE_REKEN",
        "ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL",
        "ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG",
        "ANA_DSS_CONSOLIDATIE_TYPE_REKEN",
        "ANA_GRENSSPANNING_PROEF",
        "ANA_POP_VELD",
        "ANA_POP_VELD_GEMIDDELD",
        "ANA_GRENSSPANNING_VOORSTEL",
        "ANA_GRENSSPANNING_HANDMATIG",
        "ANA_GRENSSPANNING_REKEN",
        "OCR_TXT",
        "OCR_DSS",
    ]
    preserve_cols = [
        "ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG",
        "ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG",
        "ANA_GRENSSPANNING_HANDMATIG",
    ]
    df = self.dbase_df

    # Store preserved values with proper type conversion
    preserved_data = {}
    for col in preserve_cols:
        if col in df.columns:
            if col == "ANA_GRENSSPANNING_HANDMATIG":
                # Ensure numeric type for grensspanning
                preserved_data[col] = pd.to_numeric(df[col], errors="coerce")
            elif "CONSOLIDATIE_TYPE" in col:
                # Ensure string type for consolidation types
                preserved_data[col] = df[col].astype(str).where(df[col].notna(), None)
            else:
                preserved_data[col] = df[col]

    # Get non-analysis columns
    other_columns = [col for col in df.columns if col not in analysis_columns]

    # Create new DataFrame with non-analysis columns
    new_df = df[other_columns].copy()

    # Add each analysis column in the specified order
    for col in analysis_columns:
        if col in preserved_data:
            # If we have preserved data for this column, use it
            new_df[col] = preserved_data[col]
        else:
            # Otherwise initialize with appropriate type
            if "CONSOLIDATIE_TYPE" in col:
                new_df[col] = pd.Series(dtype="object")
            else:
                new_df[col] = pd.Series(dtype="float64")

    self.dbase_df = new_df


def add_terreinspanning(self: Dbase):
    """deze functie berekend de terreinspanning."""
    columns = ["SD_TERREINSPANNING", "CRS_TERREINSPANNING", "DSS_TERREINSPANNING", "TXT_SS_TERREINSPANNING"]
    self.dbase_df["ANA_TERREINSPANNING"] = self.dbase_df[columns].max(axis=1, skipna=True)


def add_txt_max_vert_consol_sp(self: Dbase):
    """Deze functie berekend de verticale consolidatiespanning bij het einde van de triaxiaalproef.
    Kan worden omgezet naar max"""
    # product1 = self.dbase_df["TXT_SS_S'_MAX_CONSOLIDATIE"] + self.dbase_df['TXT_SS_T_MAX_CONSOLIDATIE']
    product2 = self.dbase_df["TXT_SS_S'_EIND_CONSOLIDATIE"] + self.dbase_df["TXT_SS_T_EIND_CONSOLIDATIE"]
    self.dbase_df["ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING"] = product2


def add_dss_max_consol_sp(self: Dbase):
    """Deze functie berekend de verticale consolidatiespanning bij het einde van de DSS-proef.
    Kan worden omgezet naar max"""
    # self.dbase_df['ANA_DSS_MAX_CONSOLIDATIE_SPANNING'] = self.dbase_df[
    #     ['DSS_MAX_EFF_VERT_SPANNING_CONSOLIDATIE', 'DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE']].max(axis=1)
    self.dbase_df["ANA_DSS_MAX_CONSOLIDATIE_SPANNING"] = self.dbase_df["DSS_EFF_VERT_SPANNING_EINDE_CONSOLIDATIE"]


def add_txt_consol_type(self: Dbase):
    """Geeft een voorstel voor het consolidatietype van de triaxiaalproef. Indien de maximale consolidatiespanning
    niet meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
    consolidatietype NC aangenomen."""

    if self.dbase_df["ALG__TRIAXIAAL"].any():
        self.dbase_df.loc[self.dbase_df["ALG__TRIAXIAAL"], "ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL"] = self.dbase_df.apply(
            lambda row: (
                "OC" if row["ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING"] / row["ANA_TERREINSPANNING"] <= 1.3 else "NC"
            ),
            axis=1,
        )


def add_dss_consol_type(self: Dbase):
    """Geeft een voorstel voor het consolidatietype van de DSS-proef. Indien de maximale consolidatiespanning niet
    meer dan 30% afwijkt van de terreinspanning wordt het consolidatietype OC aangenomen, anders wordt het
    consolidatietype NC aangenomen."""
    if self.dbase_df["ALG__DSS"].any():
        self.dbase_df.loc[self.dbase_df["ALG__DSS"], "ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL"] = self.dbase_df.apply(
            lambda row: "OC" if row["ANA_DSS_MAX_CONSOLIDATIE_SPANNING"] / row["ANA_TERREINSPANNING"] <= 1.3 else "NC",
            axis=1,
        )


def add_txt_consol_type_reken(self: Dbase):
    """Vult de kolom rekenwaarde van consolidatie type: als er een handmatige waarde is ingevuld,
    wordt deze overgenomen, anders wordt de voorgestelde waarde overgenomen."""
    handmatig = self.dbase_df["ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG"].mask(
        self.dbase_df["ANA_TXT_CONSOLIDATIE_TYPE_HANDMATIG"].isin(["None", "nan"])
    )
    voorstel = self.dbase_df["ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL"]
    self.dbase_df["ANA_TXT_CONSOLIDATIE_TYPE_REKEN"] = handmatig.combine_first(voorstel)


def add_dss_consol_type_reken(self: Dbase):
    """Vult de kolom rekenwaarde van consolidatie type: als er een handmatige waarde is ingevuld,
    wordt deze overgenomen, anders wordt de voorgestelde waarde overgenomen."""
    handmatig = self.dbase_df["ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG"].mask(
        self.dbase_df["ANA_DSS_CONSOLIDATIE_TYPE_HANDMATIG"].isin(["None", "nan"])
    )
    voorstel = self.dbase_df["ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL"]
    self.dbase_df["ANA_DSS_CONSOLIDATIE_TYPE_REKEN"] = handmatig.combine_first(voorstel)


def add_grensspanning_proef(self: Dbase):
    """Deze functie bepaalt de grensspanning."""
    columns = ["CRS_GRENSSPANNING_A", "SD_ISOTACHE_GRENSSPANNING_A"]
    grens_values = self.dbase_df[columns].max(axis=1)
    self.dbase_df["ANA_GRENSSPANNING_PROEF"] = grens_values


def calc_pop_veld(self):
    """Berekent de POP in het veld"""
    self.dbase_df["ANA_POP_VELD"] = self.dbase_df["ANA_GRENSSPANNING_PROEF"] - self.dbase_df["ANA_TERREINSPANNING"]


def calc_pop_average(self):
    """Berekent de gemiddelde POP van een monster. Aangenomen wordt dat de POP gelijk blijft in de diepte."""
    self.dbase_df["ANA_POP_VELD_GEMIDDELD"] = self.dbase_df.groupby("BORING_NUMMER")["ANA_POP_VELD"].transform("mean")


def add_grensspanning_voorstel(self: Dbase):
    """Bepaalt de voorgestelde grensspanning alleen wanneer er geen proefwaarde is.

    Als 'ANA_GRENSSPANNING_PROEF' leeg of NaN is, wordt 'ANA_GRENSSPANNING_VOORSTEL'
    gelijk aan 'ANA_TERREINSPANNING' + 'ANA_POP_VELD_GEMIDDELD'.
    In alle andere gevallen wordt 'ANA_GRENSSPANNING_VOORSTEL' op None gezet.
    """
    mask = self.dbase_df["ANA_GRENSSPANNING_PROEF"].isna()
    # Standaard None, alleen vullen waar geen proefwaarde is
    self.dbase_df["ANA_GRENSSPANNING_VOORSTEL"] = None
    self.dbase_df.loc[mask, "ANA_GRENSSPANNING_VOORSTEL"] = (
        self.dbase_df.loc[mask, "ANA_TERREINSPANNING"] + self.dbase_df.loc[mask, "ANA_POP_VELD_GEMIDDELD"]
    )


def calc_grensspanning_reken(self: Dbase):
    """
    Berekent de rekenwaarde van de grensspanning per rij.

    De prioriteitsvolgorde is:
    1. ANA_GRENSSPANNING_HANDMATIG  (handmatig ingevuld)
    2. ANA_GRENSSPANNING_VOORSTEL   (berekend voorstel)
    3. ANA_GRENSSPANNING_PROEF      (gemeten proefwaarde)
    """
    df = self.dbase_df

    handmatig = (
        pd.to_numeric(df.get("ANA_GRENSSPANNING_HANDMATIG"), errors="coerce")
        if "ANA_GRENSSPANNING_HANDMATIG" in df.columns
        else pd.Series(pd.NA, index=df.index)
    )

    voorstel = (
        pd.to_numeric(df.get("ANA_GRENSSPANNING_VOORSTEL"), errors="coerce")
        if "ANA_GRENSSPANNING_VOORSTEL" in df.columns
        else pd.Series(pd.NA, index=df.index)
    )

    proef = (
        pd.to_numeric(df.get("ANA_GRENSSPANNING_PROEF"), errors="coerce")
        if "ANA_GRENSSPANNING_PROEF" in df.columns
        else pd.Series(pd.NA, index=df.index)
    )

    # Fallback: handmatig → voorstel → proef
    self.dbase_df["ANA_GRENSSPANNING_REKEN"] = handmatig.combine_first(voorstel).combine_first(proef)


def calc_ocr_txt(self: Dbase):
    """Deze functie berekent de OCR van de triaxiaalproeven per rij."""
    if "ALG__TRIAXIAAL" not in self.dbase_df.columns:
        self.dbase_df["OCR_TXT"] = None
        return

    df = self.dbase_df
    mask = df["ALG__TRIAXIAAL"] & df["ANA_GRENSSPANNING_REKEN"].notna() & df["ANA_TERREINSPANNING"].notna()
    is_oc = df["ANA_TXT_CONSOLIDATIE_TYPE_REKEN"] == "OC"

    self.dbase_df["OCR_TXT"] = pd.Series(
        np.where(mask & is_oc, df["ANA_GRENSSPANNING_REKEN"] / df["ANA_TERREINSPANNING"], np.where(mask, 1.0, np.nan)),
        index=df.index,
        dtype="float64",
    )


def calc_ocr_dss(self: Dbase):
    """Deze functie berekent de OCR van de DSS-proeven."""
    if "ALG__DSS" not in self.dbase_df.columns:
        self.dbase_df["OCR_DSS"] = None
        return

    df = self.dbase_df
    mask = df["ALG__DSS"] & df["ANA_GRENSSPANNING_REKEN"].notna() & df["ANA_TERREINSPANNING"].notna()
    is_oc = df["ANA_DSS_CONSOLIDATIE_TYPE_REKEN"] == "OC"

    self.dbase_df["OCR_DSS"] = pd.Series(
        np.where(mask & is_oc, df["ANA_GRENSSPANNING_REKEN"] / df["ANA_TERREINSPANNING"], np.where(mask, 1.0, np.nan)),
        index=df.index,
        dtype="float64",
    )
