import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def make_grens_df(
    df: pd.DataFrame,
    loop_column: str = "ALG_REFERENTIE",
) -> pd.DataFrame:
    """
    Maakt het dataframe dat als input dient voor de volumegewicht/OCR/POP/grensspanning-plots.

    Parameters
    ----------
    df : pd.DataFrame
        Dbase dataframe.
    loop_column : str, default "ALG_REFERENTIE"
        Kolom waarover later geloopt wordt bij het genereren van figuren.
        Deze kolom wordt automatisch opgenomen in het output dataframe.

    Returns
    -------
    pd.DataFrame
        Dataframe met per proef een rij en alle benodigde plotinformatie.
    """

    required_columns = [
        "ALG__BORING_MONSTERNR_ID",
        "BORING_NUMMER",
        "BORING_POSITIE",
        "ANA_GRENSSPANNING_PROEF",
        "ANA_GRENSSPANNING_VOORSTEL",
        "ANA_GRENSSPANNING_HANDMATIG",
        "ANA_TERREINSPANNING",
        "OCR_TXT",
        "OCR_DSS",
    ]

    extra_columns = [
        "CLAS_MONSTERNIVEAU",
        "CLAS_VOLUMEGEWICHT_NAT",
        "CRS_MONSTERNIVEAU",
        "CRS_VOLUMEGEWICHT_NAT",
        "SD_MONSTERNIVEAU",
        "SD_VOLUMEGEWICHT_NAT",
        "DSS_MONSTERNIVEAU",
        "DSS_VOLUMEGEWICHT_NAT",
        "TXT_SS_MONSTERNIVEAU",
        "TXT_SS_VOLUMEGEWICHT_NAT",
    ]

    columns_to_check = list(dict.fromkeys(required_columns + extra_columns + [loop_column]))

    missing_columns = [col for col in columns_to_check if col not in df.columns]
    if missing_columns:
        raise KeyError(
            "De volgende kolommen ontbreken in het input dataframe:\n"
            + "\n".join(f"- {col}" for col in missing_columns)
        )

    records = []

    proef_config = [
        ("CLAS", "CLAS_MONSTERNIVEAU", "CLAS_VOLUMEGEWICHT_NAT", None),
        ("CRS", "CRS_MONSTERNIVEAU", "CRS_VOLUMEGEWICHT_NAT", None),
        ("SD", "SD_MONSTERNIVEAU", "SD_VOLUMEGEWICHT_NAT", None),
        ("DSS", "DSS_MONSTERNIVEAU", "DSS_VOLUMEGEWICHT_NAT", "OCR_DSS"),
        ("TXT", "TXT_SS_MONSTERNIVEAU", "TXT_SS_VOLUMEGEWICHT_NAT", "OCR_TXT"),
    ]

    for index, row in df.iterrows():
        boring_monsternr_id = row["ALG__BORING_MONSTERNR_ID"]

        boring_nr = row["BORING_NUMMER"]
        boring_pos = row["BORING_POSITIE"]
        loop_value = row[loop_column]

        grensspanning_proef = row["ANA_GRENSSPANNING_PROEF"]
        grensspanning_voorstel = row["ANA_GRENSSPANNING_VOORSTEL"]
        grensspanning_handmatig = row["ANA_GRENSSPANNING_HANDMATIG"]

        terreinspanning = row["ANA_TERREINSPANNING"]

        ocr_txt_val = row.get("OCR_TXT")
        ocr_dss_val = row.get("OCR_DSS")

        ocr_rij = (
            ocr_txt_val
            if pd.notna(ocr_txt_val)
            else (ocr_dss_val if pd.notna(ocr_dss_val) else None)
        )

        for proef, diepte_col, volw_col, ocr_col in proef_config:
            diepte = row[diepte_col]
            volumegewicht = row[volw_col]

            if pd.notna(diepte) and diepte != "":
                # NaN volumegewicht wordt overgeslagen, lege string blijft staan.
                if pd.isna(volumegewicht) and volumegewicht != "":
                    continue

                record = {
                    "ALG__BORING_MONSTERNR_ID": boring_monsternr_id,
                    "BORING_NUMMER": boring_nr,
                    "BORING_POSITIE": boring_pos,
                    loop_column: loop_value,
                    "monster": proef,
                    "diepte": diepte,
                    "volumegewicht": volumegewicht,
                    "grensspanning": None,
                    "grensspanning_aangenomen": None,
                    "terreinspanning": terreinspanning,
                    "ocr": None,
                    "ocr_aangenomen": None,
                    "pop": None,
                    "pop_aangenomen": None,
                }

                # OCR
                if proef == "CLAS":
                    record["ocr"] = None
                    record["ocr_aangenomen"] = None
                elif pd.notna(grensspanning_proef):
                    record["ocr"] = ocr_rij
                    record["ocr_aangenomen"] = None
                else:
                    record["ocr"] = None
                    record["ocr_aangenomen"] = ocr_rij

                # Grensspanning / POP
                if proef == "CLAS":
                    record["grensspanning"] = None
                    record["grensspanning_aangenomen"] = None
                    record["pop"] = None
                    record["pop_aangenomen"] = None

                else:
                    # 1. Grensspanning uit proef
                    if pd.notna(grensspanning_proef) and grensspanning_proef != "":
                        record["grensspanning"] = grensspanning_proef
                        record["grensspanning_aangenomen"] = None

                        if pd.notna(terreinspanning) and terreinspanning != "":
                            record["pop"] = grensspanning_proef - terreinspanning
                        else:
                            record["pop"] = None

                        record["pop_aangenomen"] = None

                    # 2. Geen grensspanning uit proef, dus aangenomen grensspanning bepalen
                    else:
                        record["grensspanning"] = None

                        if pd.notna(grensspanning_handmatig) and grensspanning_handmatig != "":
                            grensspanning_aangenomen = grensspanning_handmatig
                        elif pd.notna(grensspanning_voorstel) and grensspanning_voorstel != "":
                            grensspanning_aangenomen = grensspanning_voorstel
                        else:
                            grensspanning_aangenomen = None

                        record["grensspanning_aangenomen"] = grensspanning_aangenomen
                        record["pop"] = None

                        if (
                                pd.notna(terreinspanning)
                                and terreinspanning != ""
                                and pd.notna(grensspanning_aangenomen)
                                and grensspanning_aangenomen != ""
                        ):
                            record["pop_aangenomen"] = grensspanning_aangenomen - terreinspanning
                        else:
                            record["pop_aangenomen"] = None

                records.append(record)

    grens_df = pd.DataFrame.from_records(records)

    # Kolomvolgorde expliciet vastzetten.
    base_columns = [
        "ALG__BORING_MONSTERNR_ID",
        "BORING_NUMMER",
        "BORING_POSITIE",
    ]

    if loop_column not in base_columns:
        base_columns.append(loop_column)

    ordered_columns = base_columns + [
        "monster",
        "diepte",
        "volumegewicht",
        "grensspanning",
        "grensspanning_aangenomen",
        "terreinspanning",
        "ocr",
        "ocr_aangenomen",
        "pop",
        "pop_aangenomen",
    ]

    grens_df = grens_df[ordered_columns]

    return grens_df

def generate_grens_figures(
    grens_df: pd.DataFrame,
    loop_column: str = "ALG_REFERENTIE",
    export_dir: str | Path | None = None,
    show: bool = True,
    write_html: bool = True,
) -> dict:
    """
    Genereert per unieke waarde in loop_column dezelfde figuren als in je voorbeeldcode.

    Parameters
    ----------
    grens_df : pd.DataFrame
        Output van make_grens_df.
    loop_column : str, default "ALG_REFERENTIE"
        Kolom waarover geloopt wordt.
    export_dir : str | Path | None, default None
        Map waar HTML-bestanden opgeslagen worden.
    show : bool, default True
        Of fig.show() wordt aangeroepen.
    write_html : bool, default True
        Of de figuren als HTML worden opgeslagen.

    Returns
    -------
    dict
        Dictionary met per loop_column-waarde de bijbehorende Plotly figuur.
    """

    if loop_column not in grens_df.columns:
        raise KeyError(f"Loop column '{loop_column}' zit niet in grens_df.")

    if write_html and export_dir is None:
        raise ValueError("Geef export_dir op als write_html=True.")

    if export_dir is not None:
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)

    figures = {}

    grens_values = pd.concat(
        [
            grens_df["grensspanning"],
            grens_df["grensspanning_aangenomen"],
        ],
        ignore_index=True,
    )

    pop_values = pd.concat(
        [
            grens_df["pop"],
            grens_df["pop_aangenomen"],
        ],
        ignore_index=True,
    )

    ocr_values = pd.concat(
        [
            grens_df["ocr"],
            grens_df["ocr_aangenomen"],
         ],
        ignore_index=True,
    )

    max_grensspanning = grens_values.max()
    min_pop = pop_values.min()
    max_pop = pop_values.max()
    min_ocr = ocr_values.min()
    max_ocr = ocr_values.max()

    marker_dict = {
        "CLAS": {"color": "black", "symbol": "circle"},
        "CRS": {"color": "orange", "symbol": "square"},
        "SD": {"color": "green", "symbol": "square"},
        "DSS": {"color": "red", "symbol": "diamond"},
        "TXT": {"color": "blue", "symbol": "diamond"},
    }

    marker_dict2 = {
        "CLAS": {"color": "black", "symbol": "circle-open"},
        "CRS": {"color": "orange", "symbol": "square-open"},
        "SD": {"color": "green", "symbol": "square-open"},
        "DSS": {"color": "red", "symbol": "diamond-open"},
        "TXT": {"color": "blue", "symbol": "diamond-open"},
    }

    def get_marker_style(proef, marker_dict_to_use, default_symbol="circle", size=8):
        """
        Maakt marker-dict zonder ** unpacking.
        """
        base_marker = marker_dict_to_use.get(
            proef,
            {"color": "grey", "symbol": default_symbol},
        )

        return {
            "color": base_marker["color"],
            "symbol": base_marker["symbol"],
            "size": size,
        }

    def add_empty_if_needed(fig, col):
        """
        Voegt een onzichtbare dummy trace toe als subplot leeg is.
        """
        xaxis_name = "x" if col == 1 else f"x{col}"

        has_trace_in_col = any(
            getattr(trace, "xaxis", None) == xaxis_name
            for trace in fig.data
        )

        if not has_trace_in_col:
            fig.add_trace(
                go.Scatter(
                    x=[np.nan],
                    y=[np.nan],
                    mode="markers",
                    showlegend=False,
                    marker={
                        "color": "rgba(0,0,0,0)",
                    },
                ),
                row=1,
                col=col,
            )

    for loop_value in grens_df[loop_column].dropna().unique():
        subset_vg = grens_df[grens_df[loop_column] == loop_value]

        # Data voor volumegewicht
        vol_data = subset_vg[
            subset_vg["monster"].isin(["CLAS", "SD", "CRS", "TXT", "DSS"])
        ][
            ["diepte", "volumegewicht", "monster", "ALG__BORING_MONSTERNR_ID"]
        ]

        vol_data = vol_data[
            vol_data["volumegewicht"].notna()
            & (vol_data["volumegewicht"] != "")
        ]

        # Data voor grensspanning
        grens_data = subset_vg[
            subset_vg["monster"].isin(["SD", "CRS", "TXT", "DSS"])
        ][
            ["diepte", "grensspanning", "monster", "ALG__BORING_MONSTERNR_ID"]
        ]

        grens_data = grens_data[
            grens_data["grensspanning"].notna()
            & (grens_data["grensspanning"] != "")
        ]

        # grensspanning_aangenomen, aangenomen indien geen grensspanning
        reken_grens_data = subset_vg[
            (subset_vg["monster"].isin(["TXT", "DSS"]))
            & (
                (subset_vg["grensspanning"].isna())
                | (subset_vg["grensspanning"] == "")
            )
            & (subset_vg["grensspanning_aangenomen"].notna())
            & (subset_vg["grensspanning_aangenomen"] != "")
        ][
            ["diepte", "grensspanning_aangenomen", "monster", "ALG__BORING_MONSTERNR_ID"]
        ]

        # Data voor OCR
        ocr_data = subset_vg[
            subset_vg["monster"].isin(["SD", "CRS", "TXT", "DSS"])
        ][
            ["diepte", "ocr", "monster", "ALG__BORING_MONSTERNR_ID"]
        ]

        ocr_data = ocr_data[
            ocr_data["ocr"].notna()
            & (ocr_data["ocr"] != "")
        ]

        # OCR aangenomen
        ocr_aang_data = subset_vg[
            subset_vg["monster"].isin(["SD", "CRS", "TXT", "DSS"])
        ][
            ["diepte", "ocr_aangenomen", "monster", "ALG__BORING_MONSTERNR_ID"]
        ]

        ocr_aang_data = ocr_aang_data[
            ocr_aang_data["ocr_aangenomen"].notna()
            & (ocr_aang_data["ocr_aangenomen"] != "")
        ]

        # Data voor POP
        pop_data = subset_vg[
            subset_vg["monster"].isin(["SD", "CRS", "TXT", "DSS"])
        ][
            ["diepte", "pop", "monster", "ALG__BORING_MONSTERNR_ID"]
        ]

        pop_data = pop_data[
            pop_data["pop"].notna()
            & (pop_data["pop"] != "")
        ]

        # POP_aangenomen, aangenomen indien geen POP
        pop_aangenomen_data = subset_vg[
            (subset_vg["monster"].isin(["SD", "CRS", "TXT", "DSS"]))
            & (
                (subset_vg["pop"].isna())
                | (subset_vg["pop"] == "")
            )
            & (subset_vg["pop_aangenomen"].notna())
            & (subset_vg["pop_aangenomen"] != "")
        ][
            ["diepte", "pop_aangenomen", "monster", "ALG__BORING_MONSTERNR_ID"]
        ]

        fig = make_subplots(
            rows=1,
            cols=4,
            shared_yaxes=True,
        )

        # Voeg CLAS toe aan legenda
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=get_marker_style("CLAS", marker_dict),
                name="CLAS",
                showlegend=True,
                legendgroup="CLAS",
            ),
            row=1,
            col=1,
        )

        # Voeg een subkopje toe aan legenda voor samendrukkingsproeven
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker={
                    "color": "rgba(0,0,0,0)",
                },
                name="--- Samendrukkingsproeven ---",
                showlegend=True,
                legendgroup="samendrukkingsproeven",
            ),
            row=1,
            col=1,
        )

        # Voeg SD en CRS toe aan legenda
        for proef in ["SD", "CRS"]:
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=get_marker_style(proef, marker_dict),
                    name=proef,
                    showlegend=True,
                    legendgroup=proef,
                ),
                row=1,
                col=1,
            )

        # Voeg een subkopje toe aan legenda voor sterkteproeven
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker={
                    "color": "rgba(0,0,0,0)",
                },
                name="--- Sterkteproeven ---",
                showlegend=True,
                legendgroup="sterkteproeven",
            ),
            row=1,
            col=1,
        )

        # Voeg DSS en TXT toe aan legenda
        for proef in ["DSS", "TXT"]:
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=get_marker_style(proef, marker_dict),
                    name=proef,
                    showlegend=True,
                    legendgroup=proef,
                ),
                row=1,
                col=1,
            )

        legend_shown = {}

        # Volumegewicht subplot
        for proef in vol_data["monster"].unique():
            data = vol_data[vol_data["monster"] == proef].copy()

            if not data.empty:
                showlegend = not legend_shown.get(proef, False)

                fig.add_trace(
                    go.Scatter(
                        x=data["volumegewicht"],
                        y=data["diepte"],
                        mode="markers",
                        name=proef,
                        marker=get_marker_style(proef, marker_dict),
                        legendgroup=proef,
                        showlegend=False,
                        hovertemplate=(
                            f"Proef: {proef}<br>"
                            "Diepte: %{y}<br>"
                            "Volumegewicht: %{x}<br>"
                            "ALG__BORING_MONSTERNR_ID: %{customdata}"
                            "<extra></extra>"
                        ),
                        customdata=data["ALG__BORING_MONSTERNR_ID"],
                    ),
                    row=1,
                    col=1,
                )

                if showlegend:
                    legend_shown[proef] = True

        add_empty_if_needed(fig, 1)

        # Grensspanning subplot
        for proef in grens_data["monster"].unique():
            data = grens_data[grens_data["monster"] == proef].copy()

            if not data.empty:
                showlegend = not legend_shown.get(proef, False)

                fig.add_trace(
                    go.Scatter(
                        x=data["grensspanning"],
                        y=data["diepte"],
                        mode="markers",
                        name=proef,
                        marker=get_marker_style(proef, marker_dict),
                        legendgroup=proef,
                        showlegend=False,
                        hovertemplate=(
                            f"Proef: {proef}<br>"
                            "Diepte: %{y}<br>"
                            "Grensspanning: %{x}<br>"
                            "ALG__BORING_MONSTERNR_ID: %{customdata}"
                            "<extra></extra>"
                        ),
                        customdata=data["ALG__BORING_MONSTERNR_ID"],
                    ),
                    row=1,
                    col=2,
                )

                if showlegend:
                    legend_shown[proef] = True

        # Grensspanning aangenomen
        for proef in reken_grens_data["monster"].unique():
            data = reken_grens_data[reken_grens_data["monster"] == proef].copy()

            if not data.empty:
                showlegend = not legend_shown.get(f"{proef}_open", False)

                fig.add_trace(
                    go.Scatter(
                        x=data["grensspanning_aangenomen"],
                        y=data["diepte"],
                        mode="markers",
                        name=f"{proef} (aangenomen)",
                        marker=get_marker_style(
                            proef=proef,
                            marker_dict_to_use=marker_dict2,
                            default_symbol="circle-open",
                        ),
                        legendgroup=proef,
                        showlegend=showlegend,
                        hovertemplate=(
                            f"Proef: {proef}<br>"
                            "Diepte: %{y}<br>"
                            "Grensspanning: %{x}<br>"
                            "ALG__BORING_MONSTERNR_ID: %{customdata}"
                            "<extra></extra>"
                        ),
                        customdata=data["ALG__BORING_MONSTERNR_ID"],
                    ),
                    row=1,
                    col=2,
                )

                if showlegend:
                    legend_shown[f"{proef}_open"] = True

        add_empty_if_needed(fig, 2)

        # OCR subplot
        for proef in ocr_data["monster"].unique():
            data = ocr_data[ocr_data["monster"] == proef].copy()

            if not data.empty:
                showlegend = not legend_shown.get(proef, False)

                fig.add_trace(
                    go.Scatter(
                        x=data["ocr"],
                        y=data["diepte"],
                        mode="markers",
                        name=proef,
                        marker=get_marker_style(proef, marker_dict),
                        legendgroup=proef,
                        showlegend=False,
                        hovertemplate=(
                            f"Proef: {proef}<br>"
                            "Diepte: %{y}<br>"
                            "OCR: %{x}<br>"
                            "ALG__BORING_MONSTERNR_ID: %{customdata}"
                            "<extra></extra>"
                        ),
                        customdata=data["ALG__BORING_MONSTERNR_ID"],
                    ),
                    row=1,
                    col=3,
                )

                if showlegend:
                    legend_shown[proef] = True

        # OCR aangenomen
        for proef in ocr_aang_data["monster"].unique():
            data = ocr_aang_data[ocr_aang_data["monster"] == proef].copy()

            if not data.empty:
                showlegend = not legend_shown.get(f"{proef}_open", False)

                fig.add_trace(
                    go.Scatter(
                        x=data["ocr_aangenomen"],
                        y=data["diepte"],
                        mode="markers",
                        name=f"{proef} (aangenomen)",
                        marker=get_marker_style(
                            proef=proef,
                            marker_dict_to_use=marker_dict2,
                            default_symbol="circle-open",
                        ),
                        legendgroup=proef,
                        showlegend=showlegend,
                        hovertemplate=(
                            f"Proef: {proef}<br>"
                            "Diepte: %{y}<br>"
                            "OCR: %{x}<br>"
                            "ALG__BORING_MONSTERNR_ID: %{customdata}"
                            "<extra></extra>"
                        ),
                        customdata=data["ALG__BORING_MONSTERNR_ID"],
                    ),
                    row=1,
                    col=3,
                )

                if showlegend:
                    legend_shown[f"{proef}_open"] = True

        add_empty_if_needed(fig, 3)

        # POP subplot
        for proef in pop_data["monster"].unique():
            data = pop_data[pop_data["monster"] == proef].copy()

            if not data.empty:
                showlegend = not legend_shown.get(proef, False)

                fig.add_trace(
                    go.Scatter(
                        x=data["pop"],
                        y=data["diepte"],
                        mode="markers",
                        name=proef,
                        marker=get_marker_style(proef, marker_dict),
                        legendgroup=proef,
                        showlegend=False,
                        hovertemplate=(
                            f"Proef: {proef}<br>"
                            "Diepte: %{y}<br>"
                            "POP: %{x}<br>"
                            "ALG__BORING_MONSTERNR_ID: %{customdata}"
                            "<extra></extra>"
                        ),
                        customdata=data["ALG__BORING_MONSTERNR_ID"],
                    ),
                    row=1,
                    col=4,
                )

                if showlegend:
                    legend_shown[proef] = True

        # POP aangenomen
        for proef in pop_aangenomen_data["monster"].unique():
            data = pop_aangenomen_data[pop_aangenomen_data["monster"] == proef].copy()

            if not data.empty:
                showlegend = not legend_shown.get(f"{proef}_open", False)

                fig.add_trace(
                    go.Scatter(
                        x=data["pop_aangenomen"],
                        y=data["diepte"],
                        mode="markers",
                        name=f"{proef} (aangenomen)",
                        marker=get_marker_style(
                            proef=proef,
                            marker_dict_to_use=marker_dict2,
                            default_symbol="circle-open",
                        ),
                        legendgroup=proef,
                        showlegend=showlegend,
                        hovertemplate=(
                            f"Proef: {proef}<br>"
                            "Diepte: %{y}<br>"
                            "POP: %{x}<br>"
                            "ALG__BORING_MONSTERNR_ID: %{customdata}"
                            "<extra></extra>"
                        ),
                        customdata=data["ALG__BORING_MONSTERNR_ID"],
                    ),
                    row=1,
                    col=4,
                )

                if showlegend:
                    legend_shown[f"{proef}_open"] = True

        add_empty_if_needed(fig, 4)

        # As-titels en layout
        fig.update_xaxes(
            title_text="Nat volumegewicht [kN/m³]",
            row=1,
            col=1,
            range=[8, 22],
        )

        fig.update_xaxes(
            title_text="Grensspanning [kPa]",
            row=1,
            col=2,
            range=[0, max_grensspanning],
        )

        fig.update_xaxes(
            title_text="OCR [-]",
            row=1,
            col=3,
            range=[min_ocr, max_ocr],
        )

        fig.update_xaxes(
            title_text="POP [kPa]",
            row=1,
            col=4,
            range=[min_pop, max_pop],
        )

        fig.update_yaxes(
            title_text="Diepte [NAP m]",
            row=1,
            col=1,
        )

        fig.update_layout(
            title_text=f"{loop_column}: {loop_value}",
            legend_title_text="Legenda",
            width=1200,
            height=800,
        )

        # Achtergrond blokken toevoegen aan volumegewicht plot
        fig.add_vrect(
            x0=9.5,
            x1=11,
            fillcolor="rgba(235,120,120,0.5)",
            layer="below",
            line_width=0,
            row=1,
            col=1,
        )

        fig.add_vrect(
            x0=11,
            x1=13,
            fillcolor="rgba(255,160,70,0.5)",
            layer="below",
            line_width=0,
            row=1,
            col=1,
        )

        fig.add_vrect(
            x0=13,
            x1=14,
            fillcolor="rgba(230,200,100,0.5)",
            layer="below",
            line_width=0,
            row=1,
            col=1,
        )

        fig.add_vrect(
            x0=14,
            x1=16,
            fillcolor="rgba(120,220,120,0.5)",
            layer="below",
            line_width=0,
            row=1,
            col=1,
        )

        fig.add_vrect(
            x0=16,
            x1=17.5,
            fillcolor="rgba(80,150,255,0.5)",
            layer="below",
            line_width=0,
            row=1,
            col=1,
        )

        fig.add_vrect(
            x0=17.5,
            x1=21,
            fillcolor="rgba(255,255,120,0.5)",
            layer="below",
            line_width=0,
            row=1,
            col=1,
        )

        if show:
            fig.show()

        if write_html:
            html_filename = f"{loop_column}_{loop_value}.html"
            html_filepath = export_dir / html_filename
            fig.write_html(html_filepath)

        figures[loop_value] = fig

    return figures