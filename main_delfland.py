# Imports
import os.path
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pv_tool_logic.imports.import_data import Dbase

# Import Dbase
dbase = Dbase()
dbase_dir = Path(r"C:\Users\deenekat7271\ARCADIS\30242510 - Proevenverzameling - Project\05 Project execution\Proevenverzameling_v3\Delfland2026_PVtool5_0.xlsx")
export_dir = Path(r"C:\Users\deenekat7271\Downloads")
dbase.import_data(source="Dbase", source_dir=dbase_dir)

df = dbase.dbase_df

#%%
print(df.index)

print(df['ALG__BORING_MONSTERNR_ID'])

#%%
export_loc = dbase_dir.parent
export_name = dbase_dir.name
print(export_loc)
print(export_name)

dbase.export_dbase_to_template(export_dir=export_loc, export_name=export_name)

#%% Klaarzetten data in df voor plots
index_list = []
boring_ref_list = []
boring_nr_list = []
boring_pos_list = []
monster_list = []
diepte_list = []
volumegewicht_list = []
ocr_list = []
ocr_aangenomen_list = []
grens_list = []
grens_reken_list = []
pop_list = []
pop_gem_list = []

for index, row in df.iterrows():
    boring_ref = row['ALG_REFERENTIE']
    boring_nr = row['BORING_NUMMER']
    boring_pos = row['BORING_POSITIE']
    grensspanning_proef = row['ANA_GRENSSPANNING_PROEF']
    grensspanning_voorstel = row['ANA_GRENSSPANNING_VOORSTEL']
    grensspanning_reken = row['ANA_GRENSSPANNING_REKEN']
    pop_veld = row['ANA_POP_VELD']
    pop_veld_gem = row['ANA_POP_VELD_GEMIDDELD']
    ocr_txt_val = row.get('OCR_TXT')
    ocr_dss_val = row.get('OCR_DSS')
    ocr_rij = ocr_txt_val if pd.notna(ocr_txt_val) else (ocr_dss_val if pd.notna(ocr_dss_val) else None)

    for proef, diepte_col, volw_col, ocr_col in [
        ('CLAS', 'CLAS_MONSTERNIVEAU', 'CLAS_VOLUMEGEWICHT_NAT', None),
        ('CRS', 'CRS_MONSTERNIVEAU', 'CRS_VOLUMEGEWICHT_NAT', None),
        ('SD', 'SD_MONSTERNIVEAU', 'SD_VOLUMEGEWICHT_NAT', None),
        ('DSS', 'DSS_MONSTERNIVEAU', 'DSS_VOLUMEGEWICHT_NAT', 'OCR_DSS'),
        ('TXT', 'TXT_SS_MONSTERNIVEAU', 'TXT_SS_VOLUMEGEWICHT_NAT', 'OCR_TXT'),
    ]:
        if pd.notna(row[diepte_col]) and row[diepte_col] != '':
            if pd.isna(row[volw_col]) and row[volw_col] != '':
                continue
            index_list.append(index)
            boring_ref_list.append(boring_ref)
            boring_nr_list.append(boring_nr)
            boring_pos_list.append(boring_pos)
            monster_list.append(proef)
            diepte_list.append(row[diepte_col])
            volumegewicht_list.append(row[volw_col])
            # OCR
            if proef == 'CLAS':
                ocr_list.append(None)
                ocr_aangenomen_list.append(None)
            elif pd.notna(grensspanning_proef):
                ocr_list.append(ocr_rij)
                ocr_aangenomen_list.append(None)
            else:
                ocr_list.append(None)
                ocr_aangenomen_list.append(ocr_rij)

            # Grensspanning
            if proef == 'CLAS':
                grens_list.append(None)
                grens_reken_list.append(None)
                pop_list.append(None)
                pop_gem_list.append(None)
            elif proef in ['CRS', 'SD']:
                grens_list.append(grensspanning_proef)
                grens_reken_list.append(None)
                pop_list.append(pop_veld)
                pop_gem_list.append(None)
            else:  # TXT, DSS
                grens_list.append(grensspanning_reken if pd.notna(grensspanning_proef) else None)
                grens_reken_list.append(grensspanning_voorstel if pd.isna(grensspanning_proef) else None)
                pop_list.append(pop_veld if pd.notna(grensspanning_proef) else None)
                pop_gem_list.append(pop_veld_gem if pd.isna(grensspanning_proef) else None)

vg_df = pd.DataFrame({
    'ALG__BORING_MONSTERNR_ID': index_list,
    'ALG_REFERENTIE': boring_ref_list,
    'BORING_NUMMER': boring_nr_list,
    'boring_pos': boring_pos_list,
    'monster': monster_list,
    'diepte': diepte_list,
    "volumegewicht": volumegewicht_list,
    "grensspanning": grens_list,
    "grensspanning_reken": grens_reken_list,
    'ocr': ocr_list,
    'ocr_aangenomen': ocr_aangenomen_list,
    'pop': pop_list,
    'pop_gem': pop_gem_list,
})

vg_df = pd.DataFrame({'ALG__BORING_MONSTERNR_ID': index_list, 'ALG_REFERENTIE': boring_ref_list,
                      'BORING_NUMMER': boring_nr_list, 'BORING_POSITIE': boring_pos_list,
                      'monster': monster_list, 'diepte': diepte_list,
                      "volumegewicht": volumegewicht_list, "grensspanning": grens_list,
                      "grensspanning_reken": grens_reken_list,
                      'ocr': ocr_list, 'ocr_aangenomen': ocr_aangenomen_list,
                      'pop': pop_list, 'pop_gem': pop_gem_list})
print(vg_df)

#%% plots
# loop_column = 'BORING_NUMMER'
# loop_column = 'ALG_REFERENTIE'
loop_column = 'BORING_POSITIE'

count = 0
max_grensspanning = vg_df['grensspanning'].max()
min_ocr = vg_df['ocr'].min()
max_ocr = vg_df['ocr'].max()
min_pop = vg_df['pop'].min()
max_pop = vg_df['pop'].max()
for boring_nr in vg_df[loop_column].unique():
    subset_vg = vg_df[vg_df[loop_column] == boring_nr]

    # Data voor volumegewicht
    vol_data = subset_vg[subset_vg['monster'].isin(['CLAS', 'SD', 'CRS', 'TXT', 'DSS'])][
        ['diepte', 'volumegewicht', 'monster', 'ALG__BORING_MONSTERNR_ID']]
    vol_data = vol_data[vol_data['volumegewicht'].notna() & (vol_data['volumegewicht'] != '')]
    # print(vol_data)

    # Data voor Grensspanning
    grens_data = subset_vg[subset_vg['monster'].isin(['SD', 'CRS', 'TXT', 'DSS'])][
        ['diepte', 'grensspanning', 'monster', 'ALG__BORING_MONSTERNR_ID']]
    grens_data = grens_data[grens_data['grensspanning'].notna() & (grens_data['grensspanning'] != '')]
    # print(grens_data)
    # Grensspanning_reken (aangenomen) indien geen grensspanning
    reken_grens_data = subset_vg[
        (subset_vg['monster'].isin(['TXT', 'DSS'])) &
        ((subset_vg['grensspanning'].isna()) | (subset_vg['grensspanning'] == '')) &
        (subset_vg['grensspanning_reken'].notna()) & (subset_vg['grensspanning_reken'] != '')
        ][['diepte', 'grensspanning_reken', 'monster', 'ALG__BORING_MONSTERNR_ID']]
    print(reken_grens_data)

    # Data voor OCR
    ocr_data = subset_vg[subset_vg['monster'].isin(['SD', 'CRS', 'TXT', 'DSS'])][
        ['diepte', 'ocr', 'monster', 'ALG__BORING_MONSTERNR_ID']]
    ocr_data = ocr_data[ocr_data['ocr'].notna() & (ocr_data['ocr'] != '')]
    # print(ocr_data)

    # Data voor POP
    pop_data = subset_vg[subset_vg['monster'].isin(['SD', 'CRS', 'TXT', 'DSS'])][
        ['diepte', 'pop', 'monster', 'ALG__BORING_MONSTERNR_ID']]
    pop_data = pop_data[pop_data['pop'].notna() & (pop_data['pop'] != '')]
    print(pop_data)
    # POP_gem (aangenomen) indien geen POP
    pop_gem_data = subset_vg[
        (subset_vg['monster'].isin(['SD', 'CRS', 'TXT', 'DSS'])) &
        ((subset_vg['pop'].isna()) | (subset_vg['pop'] == '')) &
         (subset_vg['pop_gem'].notna()) & (subset_vg['pop_gem'] != '')
    ][['diepte', 'pop_gem', 'monster', 'ALG__BORING_MONSTERNR_ID']]
    print(pop_gem_data)

    # --- Subplots opzetten ---
    fig = make_subplots(
        rows=1, cols=4,
        shared_yaxes=True
    )
    marker_dict = {
        'CLAS': {'color': 'black', 'symbol': 'circle'},
        'CRS': {'color': 'orange', 'symbol': 'square'},
        'SD': {'color': 'green', 'symbol': 'square'},
        'DSS': {'color': 'red', 'symbol': 'diamond'},
        'TXT': {'color': 'blue', 'symbol': 'diamond'},
    }
    marker_dict2 = {
        'CLAS': {'color': 'black', 'symbol': 'circle-open'},
        'CRS': {'color': 'orange', 'symbol': 'square-open'},
        'SD': {'color': 'green', 'symbol': 'square-open'},
        'DSS': {'color': 'red', 'symbol': 'diamond-open'},
        'TXT': {'color': 'blue', 'symbol': 'diamond-open'},
    }

    # Voeg CLAS toe als aan legenda
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker={**marker_dict['CLAS'], 'size': 8},
            name='CLAS',
            showlegend=True,
            legendgroup='CLAS'
        ),
        row=1, col=1
    )

    # Voeg een subkopje toe aan legenda voor samendrukkingsproeven
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(color='rgba(0,0,0,0)'),
            name='--- Samendrukkingsproeven ---',
            showlegend=True,
            legendgroup='samendrukkingsproeven'
        ),
        row=1, col=1
    )

    # Voeg SD toe aan legenda
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker={**marker_dict['SD'], 'size': 8},
            name='SD',
            showlegend=True,
            legendgroup='SD'
        ),
        row=1, col=1
    )

    # Voeg CRS toe aan legenda
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker={**marker_dict['CRS'], 'size': 8},
            name='CRS',
            showlegend=True,
            legendgroup='CRS'
        ),
        row=1, col=1
    )

    # Voeg een subkopje toe aan legenda voor sterkteproeven
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(color='rgba(0,0,0,0)'),
            name='--- Sterkteproeven ---',
            showlegend=True,
            legendgroup='sterkteproeven'
        ),
        row=1, col=1
    )
    # Voeg DSS toe aan legenda
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker={**marker_dict['DSS'], 'size': 8},
            name='DSS',
            showlegend=True,
            legendgroup='DSS'
        ),
        row=1, col=1
    )

    # Voeg TXT toe aan legenda
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker={**marker_dict['TXT'], 'size': 8},
            name='TXT',
            showlegend=True,
            legendgroup='TXT'
        ),
        row=1, col=1
    )

    legend_shown = dict()

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
    for proef in vol_data['monster'].unique():
        data = vol_data[vol_data['monster'] == proef].copy()
        if not data.empty:
            showlegend = not legend_shown.get(proef, False)
            fig.add_trace(
                go.Scatter(
                    x=data['volumegewicht'],
                    y=data['diepte'],
                    mode='markers',
                    name=proef,
                    marker={**marker_dict.get(proef, {'color': 'grey', 'symbol': 'circle'}), 'size': 8},
                    legendgroup=proef,
                    showlegend=False,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>Volumegewicht: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=1
            )
            if showlegend:
                legend_shown[proef] = True
    add_empty_if_needed(fig, 1, "Nat volumegewicht [kN/m³]")

    # Grensspanning subplot
    for proef in grens_data['monster'].unique():
        data = grens_data[grens_data['monster'] == proef].copy()
        if not data.empty:
            # showlegend = proef not in legend_shown
            showlegend = not legend_shown.get(proef, False)
            fig.add_trace(
                go.Scatter(
                    x=data['grensspanning'],
                    y=data['diepte'],
                    mode='markers',
                    name=proef,
                    marker={**marker_dict.get(proef, {'color': 'grey', 'symbol': 'circle'}), 'size': 8},
                    legendgroup=proef,
                    showlegend=False,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>Grensspanning: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=2
            )
            if showlegend:
                legend_shown[proef] = True
    for proef in reken_grens_data['monster'].unique():
        data = reken_grens_data[reken_grens_data['monster'] == proef].copy()
        if not data.empty:
            showlegend = not legend_shown.get(f"{proef}_open", False)
            fig.add_trace(
                go.Scatter(
                    x=data['grensspanning_reken'],
                    y=data['diepte'],
                    mode='markers',
                    name=f"{proef} (aangenomen)",
                    marker={**marker_dict2.get(proef, {'color': 'grey', 'symbol': 'circle-open'}), 'size': 8},
                    legendgroup=proef,
                    showlegend=showlegend,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>Grensspanning: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=2
            )
            if showlegend:
                legend_shown[f"{proef}_open"] = True
    add_empty_if_needed(fig, 3, "Grensspanning [kPa]")

    # OCR subplot
    for proef in ocr_data['monster'].unique():
        data = ocr_data[ocr_data['monster'] == proef].copy()
        if not data.empty:
            showlegend = not legend_shown.get(proef, False)
            fig.add_trace(
                go.Scatter(
                    x=data['ocr'],
                    y=data['diepte'],
                    mode='markers',
                    name=proef,
                    marker={**marker_dict.get(proef, {'color': 'grey', 'symbol': 'circle'}), 'size': 8},
                    legendgroup=proef,
                    showlegend=False,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>OCR: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=3
            )
            if showlegend:
                legend_shown[proef] = True
    # OCR aangenomen
    ocr_aang_data = subset_vg[subset_vg['monster'].isin(['SD', 'CRS', 'TXT', 'DSS'])][
        ['diepte', 'ocr_aangenomen', 'monster', 'ALG__BORING_MONSTERNR_ID']]
    ocr_aang_data = ocr_aang_data[ocr_aang_data['ocr_aangenomen'].notna() & (ocr_aang_data['ocr_aangenomen'] != '')]

    for proef in ocr_aang_data['monster'].unique():
        data = ocr_aang_data[ocr_aang_data['monster'] == proef].copy()
        if not data.empty:
            showlegend = not legend_shown.get(f"{proef}_open", False)
            fig.add_trace(
                go.Scatter(
                    x=data['ocr_aangenomen'],
                    y=data['diepte'],
                    mode='markers',
                    name=f"{proef} (aangenomen)",
                    marker={**marker_dict2.get(proef, {'color': 'grey', 'symbol': 'circle-open'}), 'size': 8},
                    legendgroup=proef,
                    showlegend=showlegend,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>OCR: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=3
            )
            if showlegend:
                legend_shown[f"{proef}_open"] = True

    add_empty_if_needed(fig, 2, "OCR [-]")

    # POP subplot
    for proef in pop_data['monster'].unique():
        data = pop_data[pop_data['monster'] == proef].copy()
        if not data.empty:
            showlegend = not legend_shown.get(proef, False)
            fig.add_trace(
                go.Scatter(
                    x=data['pop'],
                    y=data['diepte'],
                    mode='markers',
                    name=proef,
                    marker={**marker_dict.get(proef, {'color': 'grey', 'symbol': 'circle'}), 'size': 8},
                    legendgroup=proef,
                    showlegend=False,
                    hovertemplate=(
                        f"Proef: {proef}<br>Diepte: %{{y}}<br>POP: %{{x}}<br>ALG__BORING_MONSTERNR_ID: %{{customdata}}<extra></extra>"
                    ),
                    customdata=data['ALG__BORING_MONSTERNR_ID']
                ),
                row=1, col=4
            )
            if showlegend:
                legend_shown[proef] = True
    for proef in pop_gem_data['monster'].unique():
        data = pop_gem_data[pop_gem_data['monster'] == proef].copy()
        if not data.empty:
            showlegend = not legend_shown.get(f"{proef}_open", False)
            fig.add_trace(
                go.Scatter(
                    x=data['pop_gem'],
                    y=data['diepte'],
                    mode='markers',
                    name=f"{proef} (aangenomen)",
                    marker={**marker_dict2.get(proef, {'color': 'grey', 'symbol': 'circle-open'}), 'size': 8},
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
                legend_shown[f"{proef}_open"] = True

    add_empty_if_needed(fig, 4, "POP [kPa]")

    # As-titels en layout
    fig.update_xaxes(title_text="Nat volumegewicht [kN/m³]", row=1, col=1, range=[8, 22])
    fig.update_xaxes(title_text="Grensspanning [kPa]", row=1, col=2, range=[0, max_grensspanning])
    fig.update_xaxes(title_text="OCR [-]", row=1, col=3, range=[min_ocr, max_ocr])
    fig.update_xaxes(title_text="POP [kPa]", row=1, col=4, range=[min_pop, max_pop])
    fig.update_yaxes(title_text="Diepte [NAP m]", row=1, col=1)
    fig.update_layout(
        title_text=f"{loop_column}: {boring_nr}",
        legend_title_text="Legenda",
        width=1200,
        height=800
    )

    # Achtergrond blokken toevoegen aan volumegewicht plot
    fig.add_vrect(x0=9.5, x1=11, fillcolor="rgba(235,120,120,0.5)", layer="below", line_width=0, row=1,
                  col=1)
    fig.add_vrect(x0=11, x1=13, fillcolor="rgba(255,160,70,0.5)", layer="below", line_width=0, row=1,
                  col=1)
    fig.add_vrect(x0=13, x1=14, fillcolor="rgba(230,200,100,0.5)", layer="below", line_width=0, row=1,
                  col=1)
    fig.add_vrect(x0=14, x1=16, fillcolor="rgba(120,220,120,0.5)", layer="below", line_width=0, row=1,
                  col=1)
    fig.add_vrect(x0=16, x1=17.5, fillcolor="rgba(80,150,255,0.5)", layer="below", line_width=0, row=1,
                  col=1)
    fig.add_vrect(x0=17.5, x1=21, fillcolor="rgba(255,255,120,0.5)", layer="below", line_width=0, row=1,
                  col=1)


    fig.show()

    # export plots
    html_filename = f"{loop_column}_{boring_nr}.html"
    html_filepath = os.path.join(export_dir, html_filename)
    fig.write_html(html_filepath)

    count += 1
    # if count == 3:
    #     break
