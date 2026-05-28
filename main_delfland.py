# Imports
import os.path
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pv_tool_logic.imports.import_data import Dbase

dbase = Dbase()
dbase_dir = Path(r"C:\Users\deenekat7271\Downloads\Delfland2026_PVtool5_0.xlsx")
export_dir = Path(r"C:\Users\deenekat7271\Downloads")
dbase.import_data(source="Dbase", source_dir=dbase_dir)

df = dbase.dbase_df
# print(df)

#%% Klaarzetten data in df
columns = ['ALG__BORING_MONSTERNR_ID', 'ALG_NAAM_POLDER_DIJK', 'BORING_NUMMER', 'BORING_POSITIE',
           'CRS_MONSTERNIVEAU', 'CRS_VOLUMEGEWICHT_DRG', 'SD_MONSTERNIVEAU', 'SD_VOLUMEGEWICHT_DR', 'DSS_MONSTERNIVEAU',
           'DSS_VOLUMEGEWICHT_DRG', 'TXT_SS_MONSTERNIVEAU', 'TXT_SS_VOLUMEGEWICHT_DRG', 'ANA_GRENSSPANNING_REKEN',
           'OCR_TXT', 'OCR_DSS', 'ANA_POP_VELD_GEMIDDELD']
filtered_df = df[columns]

index_list = []
boring_nr_list = []
boring_pos_list = []
monster_list = []
diepte_list = []
volumegewicht_list = []
ocr_list = []
grens_list = []
pop_list = []

for index, row in filtered_df.iterrows():
    monster = None
    diepte = None
    volumegewicht = None
    ocr = None
    boring_nr = row['BORING_NUMMER']
    boring_pos = row['BORING_POSITIE']
    grensspanning = row['ANA_GRENSSPANNING_REKEN']
    pop = row['ANA_POP_VELD_GEMIDDELD']

    if pd.notna(row['CRS_MONSTERNIVEAU']) and row['CRS_MONSTERNIVEAU'] != '':
        monster = 'CRS'
        diepte = row['CRS_MONSTERNIVEAU']
        volumegewicht = row['CRS_VOLUMEGEWICHT_DRG']
        ocr = None
    elif pd.notna(row['SD_MONSTERNIVEAU']) and row['SD_MONSTERNIVEAU'] != '':
        monster = 'SD'
        diepte = row['SD_MONSTERNIVEAU']
        volumegewicht = row['SD_VOLUMEGEWICHT_DR']
        ocr = None
    elif pd.notna(row['DSS_MONSTERNIVEAU']) and row['DSS_MONSTERNIVEAU'] != '':
        monster = 'DSS'
        diepte = row['DSS_MONSTERNIVEAU']
        volumegewicht = row['DSS_VOLUMEGEWICHT_DRG']
        ocr = row['OCR_DSS']
    elif pd.notna(row['TXT_SS_MONSTERNIVEAU']) and row['TXT_SS_MONSTERNIVEAU'] != '':
        monster = 'TXT'
        diepte = row['TXT_SS_MONSTERNIVEAU']
        volumegewicht = row['TXT_SS_VOLUMEGEWICHT_DRG']
        ocr = row['OCR_TXT']

    if monster is not None:
        index_list.append(index)
        boring_nr_list.append(boring_nr)
        boring_pos_list.append(boring_pos)
        monster_list.append(monster)
        diepte_list.append(diepte)
        volumegewicht_list.append(volumegewicht)
        ocr = ocr_list.append(ocr)
        grensspanning = grens_list.append(grensspanning)
        pop = pop_list.append(pop)

vg_df = pd.DataFrame({'ALG__BORING_MONSTERNR_ID': index_list, 'BORING_NUMMER': boring_nr_list,
                      'BORING_POSITIE': boring_pos_list, 'monster': monster_list, 'diepte': diepte_list,
                      "volumegewicht": volumegewicht_list})
print(vg_df)

#%% plots

count = 0
for boring_nr in vg_df['BORING_NUMMER'].unique():
    subset_vg = vg_df[vg_df['BORING_NUMMER'] == boring_nr]
    subset_full = filtered_df[filtered_df['BORING_NUMMER'] == boring_nr].copy()

    # Data voor OCR
    ocr_rows = []
    for proef, diepte_col, ocr_col in [
        ('TXT', 'TXT_SS_MONSTERNIVEAU', 'OCR_TXT'),
        ('DSS', 'DSS_MONSTERNIVEAU', 'OCR_DSS'),
    ]:
        if diepte_col in subset_full and ocr_col in subset_full:
            d = subset_full[[diepte_col, ocr_col, 'ALG__BORING_MONSTERNR_ID']].dropna()
            d = d.rename(columns={diepte_col: 'diepte', ocr_col: 'ocr'})
            d['monster'] = proef
            ocr_rows.append(d)
    ocr_long = pd.concat(ocr_rows) if ocr_rows else pd.DataFrame(columns=['diepte', 'ocr', 'monster', 'ALG__BORING_MONSTERNR_ID'])

    # Data voor Grensspanning
    grens_rows = []
    for proef, diepte_col in [
        ('CRS', 'CRS_MONSTERNIVEAU'),
        ('SD', 'SD_MONSTERNIVEAU'),
        ('DSS', 'DSS_MONSTERNIVEAU'),
        ('TXT', 'TXT_SS_MONSTERNIVEAU'),
    ]:
        if diepte_col in subset_full:
            d = subset_full[[diepte_col, 'ANA_GRENSSPANNING_REKEN', 'ALG__BORING_MONSTERNR_ID']].dropna(subset=[diepte_col, 'ANA_GRENSSPANNING_REKEN'])
            d = d.rename(columns={diepte_col: 'diepte', 'ANA_GRENSSPANNING_REKEN': 'grensspanning'})
            d['monster'] = proef
            grens_rows.append(d)
    grens_long = pd.concat(grens_rows) if grens_rows else pd.DataFrame(columns=['diepte', 'grensspanning', 'monster', 'ALG__BORING_MONSTERNR_ID'])

    # Data voor POP
    pop_rows = []
    for proef, diepte_col in [
        ('CRS', 'CRS_MONSTERNIVEAU'),
        ('SD', 'SD_MONSTERNIVEAU'),
        ('DSS', 'DSS_MONSTERNIVEAU'),
        ('TXT', 'TXT_SS_MONSTERNIVEAU'),
    ]:
        if diepte_col in subset_full:
            d = subset_full[[diepte_col, 'ANA_POP_VELD_GEMIDDELD', 'ALG__BORING_MONSTERNR_ID']].dropna(subset=[diepte_col, 'ANA_POP_VELD_GEMIDDELD'])
            d = d.rename(columns={diepte_col: 'diepte', 'ANA_POP_VELD_GEMIDDELD': 'pop'})
            d['monster'] = proef
            pop_rows.append(d)
    pop_long = pd.concat(pop_rows) if pop_rows else pd.DataFrame(columns=['diepte', 'pop', 'monster', 'ALG__BORING_MONSTERNR_ID'])


    # --- Subplots opzetten ---
    fig = make_subplots(
        rows=1, cols=4,
        shared_yaxes=True
    )

    kleur_dict = {'CRS': 'orange', 'SD': 'green', 'DSS': 'red', 'TXT': 'blue'}
    alle_proeven = set(subset_vg['monster'].unique()).union(
        ocr_long['monster'].unique()
    ).union(grens_long['monster'].unique()).union(pop_long['monster'].unique())

    legend_shown = set()

    # Functie om te controleren of er data is voor een subplot
    def add_empty_if_needed(fig, col, x_label):
        # Voeg een onzichtbare dummy trace toe als deze kolom nog geen data heeft
        if len(fig['data']) == 0 or not any([t for t in fig['data'] if t['xaxis'] == f'x{col}']):
            fig.add_trace(
                go.Scatter(
                    x=[np.nan], y=[np.nan], mode='markers',
                    showlegend=False, marker=dict(color='rgba(0,0,0,0)')  # Transparant
                ),
                row=1, col=col
            )

    # Volumegewicht subplot
    for proef in alle_proeven:
        data = subset_vg[subset_vg['monster'] == proef]
        if not data.empty:
            showlegend = proef not in legend_shown
            fig.add_trace(
                go.Scatter(
                    x=data['volumegewicht'],
                    y=data['diepte'],
                    mode='markers',
                    name=proef,
                    marker=dict(size=10, color=kleur_dict.get(proef, None)),
                    legendgroup=proef,
                    showlegend=showlegend,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>Volumegewicht: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=1
            )
            if showlegend:
                legend_shown.add(proef)
    # Voeg lege trace toe indien geen data
    add_empty_if_needed(fig, 1, "Volumegewicht [kN/m³]")

    # OCR subplot
    for proef in alle_proeven:
        data = ocr_long[ocr_long['monster'] == proef]
        if not data.empty:
            showlegend = proef not in legend_shown
            fig.add_trace(
                go.Scatter(
                    x=data['ocr'],
                    y=data['diepte'],
                    mode='markers',
                    name=proef,
                    marker=dict(size=10, color=kleur_dict.get(proef, None)),
                    legendgroup=proef,
                    showlegend=showlegend,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>OCR: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=2
            )
            if showlegend:
                legend_shown.add(proef)
    add_empty_if_needed(fig, 2, "OCR [-]")

    # Grensspanning subplot
    for proef in alle_proeven:
        data = grens_long[grens_long['monster'] == proef]
        if not data.empty:
            showlegend = proef not in legend_shown
            fig.add_trace(
                go.Scatter(
                    x=data['grensspanning'],
                    y=data['diepte'],
                    mode='markers',
                    name=proef,
                    marker=dict(size=10, color=kleur_dict.get(proef, None)),
                    legendgroup=proef,
                    showlegend=showlegend,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>Grensspanning: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=3
            )
            if showlegend:
                legend_shown.add(proef)
    add_empty_if_needed(fig, 3, "Grensspanning [kPa]")

    # POP subplot
    for proef in alle_proeven:
        data = pop_long[pop_long['monster'] == proef]
        if not data.empty:
            showlegend = proef not in legend_shown
            fig.add_trace(
                go.Scatter(
                    x=data['pop'],
                    y=data['diepte'],
                    mode='markers',
                    name=proef,
                    marker=dict(size=10, color=kleur_dict.get(proef, None)),
                    legendgroup=proef,
                    showlegend=showlegend,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>POP: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=4
            )
            if showlegend:
                legend_shown.add(proef)
    add_empty_if_needed(fig, 4, "POP [kPa]")

    # As-titels en layout
    fig.update_xaxes(title_text="Volumegewicht [kN/m³]", row=1, col=1)
    fig.update_xaxes(title_text="OCR [-]", row=1, col=2)
    fig.update_xaxes(title_text="Grensspanning [kPa]", row=1, col=3)
    fig.update_xaxes(title_text="POP [kPa]", row=1, col=4)
    fig.update_yaxes(title_text="Diepte [NAP m]", row=1, col=1)
    fig.update_layout(
        title_text=f"Boringnummer: {boring_nr}",
        legend_title_text="Proef",
        width=2500,
        height=1000
    )

    fig.show()

    # export plots
    html_filename = f"boring_{boring_nr}.html"
    html_filepath = os.path.join(export_dir, html_filename)
    fig.write_html(html_filepath)

    # count += 1
    # if count == 3:
    #     break