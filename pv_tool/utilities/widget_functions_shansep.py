import ipywidgets as widgets
import numpy as np
from ipyfilechooser import FileChooser
from IPython.display import display, Markdown, clear_output
import importlib.util
import subprocess
import sys
from pathlib import Path
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
import os
from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
from pv_tool.utilities.widget_functions_cphi import maak_verzamelings_lijsten, koppel_callbacks


def maak_proef_widgets_shansep(pv_txt_lijst, pv_dss_lijst):
    """Maakt de widgets voor de proefkeuze, rekpercentage en verzamelingen"""
    # Dropdowns
    dropdown_type_proef_shansep = widgets.Dropdown(
        options=['TXT_S_POP', 'DSS_S_POP'],
        value='TXT_S_POP',
        description='Type proef:',
        layout=widgets.Layout(width='400px')
    )
    dropdown_rekpercentage_txt_shansep = widgets.Dropdown(
        options=['2% rek', '5% rek', '15% rek', 'eindsterkte', 'pieksterkte'],
        value='eindsterkte',
        description='Rekpercentage TXT:',
        layout=widgets.Layout(width='400px')
    )
    dropdown_rekpercentage_dss_shansep = widgets.Dropdown(
        options=['2% rek', '5% rek', '10% rek', '15% rek', '20% rek', 'eindsterkte', 'pieksterkte'],
        value='eindsterkte',
        description='Rekpercentage DSS:',
        layout=widgets.Layout(width='400px')
    )
    dropdown_verzameling_shansep = widgets.Dropdown(
        options=pv_txt_lijst,
        value=pv_txt_lijst[0] if pv_txt_lijst else None,
        description='Verzameling:',
        layout=widgets.Layout(width='400px')
    )
    multi_select_verzameling_shansep = widgets.SelectMultiple(
        options=pv_txt_lijst,
        value=[pv_txt_lijst[0]] if pv_txt_lijst else [],
        description='Vergelijk met:',
        layout=widgets.Layout(width='400px', height='150px')
    )
    # Outputs
    container_rekpercentage_shansep = widgets.Output()
    output_rekpercentage_shansep = widgets.Output()

    return (dropdown_type_proef_shansep, dropdown_rekpercentage_txt_shansep, dropdown_rekpercentage_dss_shansep,
            dropdown_verzameling_shansep, multi_select_verzameling_shansep, container_rekpercentage_shansep,
            output_rekpercentage_shansep)


def toon_widgets_shansep(
        dropdown_type_proef_shansep, dropdown_verzameling_shansep, container_rekpercentage_shansep,
        output_rekpercentage_shansep, multi_select_verzameling_shansep
):
    """Toont alle widgets netjes onder elkaar."""
    display(Markdown("**Kies type proef:**"))
    display(dropdown_type_proef_shansep)
    display(Markdown("**Kies verzameling voor statistische analyse:**"))
    display(dropdown_verzameling_shansep)
    display(Markdown("**Kies rekpercentage Su:**"))
    display(container_rekpercentage_shansep)
    display(output_rekpercentage_shansep)
    display(Markdown(
        "**Kies één of meerdere verzamelingen om naast de gekozen verzameling voor de statistische analyse te tonen:**"))
    display(multi_select_verzameling_shansep)


def dropdown_widgets_shansep(dbase):
    dbase_df = dbase.dbase_df
    PV_txt_lijst, PV_dss_lijst = maak_verzamelings_lijsten(dbase_df)

    # Widgets aanmaken
    (dropdown_type_proef_shansep, dropdown_rekpercentage_txt_shansep, dropdown_rekpercentage_dss_shansep,
     dropdown_verzameling_shansep, multi_select_verzameling_shansep, container_rekpercentage_shansep,
     output_rekpercentage_shansep) = maak_proef_widgets_shansep(PV_txt_lijst, PV_dss_lijst)

    # 'gekozen_rekpercentage' als lijst zodat het binnen callbacks aanpasbaar blijft
    gekozen_rekpercentage_shansep = ['eindsterkte']

    # Koppel callbacks
    koppel_callbacks(
        dropdown_type_proef_shansep, dropdown_rekpercentage_txt_shansep, dropdown_rekpercentage_dss_shansep,
        dropdown_verzameling_shansep, multi_select_verzameling_shansep, container_rekpercentage_shansep,
        output_rekpercentage_shansep,
        PV_txt_lijst, PV_dss_lijst, gekozen_rekpercentage_shansep
    )

    # Toon alles
    toon_widgets_shansep(
        dropdown_type_proef_shansep, dropdown_verzameling_shansep, container_rekpercentage_shansep,
        output_rekpercentage_shansep, multi_select_verzameling_shansep
    )
    return (dropdown_type_proef_shansep, dropdown_verzameling_shansep, dropdown_rekpercentage_txt_shansep,
            dropdown_rekpercentage_dss_shansep, container_rekpercentage_shansep, output_rekpercentage_shansep,
            multi_select_verzameling_shansep, gekozen_rekpercentage_shansep)


def toon_grid_settings_shansep():
    """
    Toon een grid met de alpha.
    """
    display(Markdown("**Pas alpha aan (lokaal = 1,0, regionaal = 0,75):**"))
    alpha_widget = widgets.FloatText(
        value=0.75,
        description='Alpha:',
        step=0.01
    )
    display(widgets.VBox([alpha_widget]))
    return alpha_widget


def get_benaderings_waarden(analyse):
    SNIJPUNT_GEM_BENADERING_R2 = round(analyse.e_a1_oc, 2)
    S_GEM_BENADERING_UIT_S_en_POP_R2 = round(analyse.e_a2_oc, 2)
    m_GEM_BENADERING_uit_S_en_m_R3 = round(analyse.e_a2_nc_oc, 2)
    SNIJPUNT_KAR_BENADERING_R2 = round(analyse.a1_kar_oc, 2)
    S_KAR_BENADERING_UIT_S_en_POP_R2 = round(analyse.a2_kar_oc, 2)
    m_KAR_BENADERING_uit_S_en_m_R3 = round(analyse.a2_kar_nc_oc, 2)
    return (SNIJPUNT_GEM_BENADERING_R2,
            S_GEM_BENADERING_UIT_S_en_POP_R2,
            m_GEM_BENADERING_uit_S_en_m_R3,
            SNIJPUNT_KAR_BENADERING_R2,
            S_KAR_BENADERING_UIT_S_en_POP_R2,
            m_KAR_BENADERING_uit_S_en_m_R3)


def run_shansep_analysis(
        dbase,
        dropdown_verzameling_shansep,
        alpha_widget,
        import_dropdown,
        import_filechooser,
        dropdown_rekpercentage_txt_shansep,
        dropdown_rekpercentage_dss_shansep,
        dropdown_type_proef_shansep,
        export_dir_widget=None,
        export_name_widget=None
):
    # Get rekpercentage
    verzameling = dropdown_verzameling_shansep.value
    rekpercentage = dropdown_rekpercentage_txt_shansep.value if dropdown_type_proef_shansep.value.startswith(
        'TXT') else dropdown_rekpercentage_dss_shansep.value

    analyse = SHANSEP(
        dbase=dbase,
        investigation_groups=[verzameling],
        effective_stress=rekpercentage,
        analysis_type=dropdown_type_proef_shansep.value
    )
    analyse.apply_settings(alpha=alpha_widget.value)
    analyse.get_shansep_data()
    df_gem, df_kar = analyse.get_result_values_shansep()

    # Ophalen laatste resultaten
    handmatig = get_laatste_resultaten_shansep(analyse, import_dropdown, import_filechooser, export_dir_widget,
                                               export_name_widget)
    handmatig_gem = (
        handmatig['PV_A1_SNIJPUNT_YAS_GEM'][0],
        handmatig['PV_A2_S_GEM'][0],
        handmatig['PV_m_GEM'][0]
    )
    handmatig_kar = (
        handmatig['PV_A1_SNIJPUNT_YAS_KAR'][0],
        handmatig['PV_A2_S_KAR'][0],
        handmatig['PV_m_KAR'][0]
    )

    widgets_kar, widgets_gem = show_grids(analyse, handmatig_gem, handmatig_kar)

    return analyse, df_gem, df_kar, widgets_gem, widgets_kar


def get_laatste_resultaten_shansep(analyse, import_dropdown, import_filechooser,
                                   export_dir_widget=None, export_name_widget=None):
    # Benaderingswaarden
    (SNIJPUNT_GEM_BENADERING_R2,
     S_GEM_BENADERING_UIT_S_en_POP_R2,
     m_GEM_BENADERING_uit_S_en_m_R3,
     SNIJPUNT_KAR_BENADERING_R2,
     S_KAR_BENADERING_UIT_S_en_POP_R2,
     m_KAR_BENADERING_uit_S_en_m_R3) = get_benaderings_waarden(analyse)

    # Ophalen van directory en bestandsnaam uit widgets
    if import_dropdown.value == 'Proevenverzamelingtool 5.0':
        import_path = Path(import_filechooser.selected)
        export_dir = str(import_path.parent)
        export_name = import_path.name
    else:
        export_dir = export_dir_widget.selected_path if hasattr(export_dir_widget,
                                                                "selected_path") else export_dir_widget
        export_name = export_name_widget.value if hasattr(export_name_widget, "value") else export_name_widget
        if not export_name.lower().endswith('.xlsx'):
            export_name += '.xlsx'
    laatste_resultaten = analyse.get_previous_results(path=export_dir, file_name=export_name)
    if (laatste_resultaten is not None and
            not laatste_resultaten.empty and
            'PV_A1_SNIJPUNT_YAS_GEM [-]' in laatste_resultaten):
        handmatig = {
            'PV_A1_SNIJPUNT_YAS_GEM': [laatste_resultaten['PV_A1_SNIJPUNT_YAS_GEM [-]']],
            'PV_A2_S_GEM': [laatste_resultaten['PV_A2_S_GEM [-]']],
            'PV_m_GEM': [laatste_resultaten['PV_m_GEM [-]']],
            'PV_A1_SNIJPUNT_YAS_KAR': [laatste_resultaten['PV_A1_SNIJPUNT_YAS_KAR [-]']],
            'PV_A2_S_KAR': [laatste_resultaten['PV_A2_S_KAR [-]']],
            'PV_m_KAR': [laatste_resultaten['PV_m_KAR [-]']]
        }
    else:
        handmatig = {
            'PV_A1_SNIJPUNT_YAS_GEM': [SNIJPUNT_GEM_BENADERING_R2],
            'PV_A2_S_GEM': [S_GEM_BENADERING_UIT_S_en_POP_R2],
            'PV_m_GEM': [m_GEM_BENADERING_uit_S_en_m_R3],
            'PV_A1_SNIJPUNT_YAS_KAR': [SNIJPUNT_KAR_BENADERING_R2],
            'PV_A2_S_KAR': [S_KAR_BENADERING_UIT_S_en_POP_R2],
            'PV_m_KAR': [m_KAR_BENADERING_uit_S_en_m_R3]
        }
    return handmatig


def _create_grid_row(descriptions, values_yas, values_S, values_m, values_pop):
    rows = []
    for desc, y_as, S, m, pop in zip(descriptions, values_yas, values_S, values_m, values_pop):
        row = [
            widgets.Label(desc, layout=widgets.Layout(width='350px')),
            widgets.Label(str(y_as) if y_as is not None else "-"),
            widgets.Label(str(S) if S is not None else "-"),
            widgets.Label(str(m) if m is not None else "-"),
            widgets.Label(str(pop) if pop is not None else "-")
        ]
        rows.append(row)
    return rows


def _create_handmatig_row(init_vals, calc_func):
    ft_1 = widgets.FloatText(value=init_vals[0], layout=widgets.Layout(width='180px'))
    ft_2 = widgets.FloatText(value=init_vals[1], layout=widgets.Layout(width='180px'))
    ft_3 = widgets.FloatText(value=init_vals[2], layout=widgets.Layout(width='180px'))
    result_label = widgets.Label(value='', layout=widgets.Layout(width='180px'))

    def _update_result(change=None):
        try:
            v1, v2, v3 = ft_1.value, ft_2.value, ft_3.value
            result_label.value = calc_func(v1, v2, v3)
        except Exception:
            result_label.value = "Fout"

    _update_result()
    ft_1.observe(_update_result, names="value")
    ft_2.observe(_update_result, names="value")
    ft_3.observe(_update_result, names="value")
    return [widgets.Label("Handmatige invoer", layout=widgets.Layout(width='350px')), ft_1, ft_2, ft_3, result_label], (ft_1, ft_2, ft_3, result_label)


def _pop_calc(v1, v2, v3):
    if v2 == 0 or v3 == 0:
        return "Niet gedefinieerd"
    else:
        return f"{v1 / v2 / v3:.3f}"


def show_grids(analyse, handmatig_gem, handmatig_kar):
    """
    Toont de grids voor gemiddelde en karakteristieke SHANSEP-waarden.
    Haalt de benaderingswaarden direct uit analyse.get_estimated_parameters().
    handmatig_gem = (init_yas, init_S, init_m)
    handmatig_kar = (init_yas, init_S, init_m)
    """
    # Beschrijvingen
    descriptions = [
        "bepaling S en POP uit triaxiaal- of DSS proeven",
        "bepaling S en m uit triaxiaal- of DSS proeven",
        "o.b.v. opgegeven POP bij triaxiaal- of DSS proeven",
        "bepaling S uit triaxiaal- of DSS proeven OCR=1"
    ]

    # Haal benaderingswaarden op uit analyse object
    matrix_gem, matrix_kar = analyse.get_result_values_shansep()
    benadering_gem = matrix_gem.drop(matrix_gem.index[-1])
    col_order = ['snijpunt y-as [kPa]', 'Schuifsterkteratio S [-]', 'sterkte toename exponent = m [-]', 'POP [kPa]']

    def to_display_list(series):
        return [('-' if (isinstance(val, float) and np.isnan(val)) else val) for val in series.round(2)]

    benadering_gem = [to_display_list(benadering_gem[col]) for col in col_order]
    benadering_kar = matrix_kar.drop(matrix_kar.index[-1])
    benadering_kar = [to_display_list(benadering_kar[col]) for col in col_order]

    # GRID GEMIDDELDE
    grid_gem = widgets.GridspecLayout(6, 5, width='1050px')
    grid_gem[0, 0] = widgets.Label("Parameters", layout=widgets.Layout(width='300px'))
    grid_gem[0, 1] = widgets.Label("Snijpunt y-as")
    grid_gem[0, 2] = widgets.Label("Schuifsterkteratio S")
    grid_gem[0, 3] = widgets.Label("Sterkte toename exponent m")
    grid_gem[0, 4] = widgets.Label("POP")

    # Benaderingswaarden vullen
    for i, row in enumerate(
            _create_grid_row(descriptions, *benadering_gem),
            start=1
    ):
        for j, item in enumerate(row):
            grid_gem[i, j] = item

    # Handmatige invoer (rij 6)
    hand_row, hand_widgets_gem = _create_handmatig_row(handmatig_gem, _pop_calc)
    for j, item in enumerate(hand_row):
        grid_gem[5, j] = item

    # GRID KARAKTERISTIEK
    grid_kar = widgets.GridspecLayout(6, 5, width='1050px')
    grid_kar[0, 0] = widgets.Label("Parameters", layout=widgets.Layout(width='300px'))
    grid_kar[0, 1] = widgets.Label("Snijpunt y-as")
    grid_kar[0, 2] = widgets.Label("Schuifsterkterratio S")
    grid_kar[0, 3] = widgets.Label("Sterkte toename exponent m")
    grid_kar[0, 4] = widgets.Label("POP")

    for i, row in enumerate(
            _create_grid_row(descriptions, *benadering_kar),
            start=1
    ):
        for j, item in enumerate(row):
            grid_kar[i, j] = item

    hand_row_kar, hand_widgets_kar = _create_handmatig_row(handmatig_kar, _pop_calc)
    for j, item in enumerate(hand_row_kar):
        grid_kar[5, j] = item

    # Toelichting
    display(Markdown("**Stel de raaklijnen vast voor de bepaling van de gemiddelde en karakteristieke waarden van:**"))
    display(Markdown(""" - S en POP door het opgeven van het snijpunt met de y-as (a1) en de schuifsterkteratio (a2)
- S en m door het opgeven van het schuifsterkterratio (a1) en de macht (a2)

Op basis van regressie wordt een eerste benadering gegeven voor de gemiddelde en karakteristieke waarden van al deze parameters, tevens wordt de POP op basis van de CRS of samendrukkingsproeven gegeven en de S op basis van de normaal geconsolideerde proeven.

Toets in de volgende stap bij het genereren van de grafieken of de raaklijnen juist zijn gekozen en pas deze aan naar eigen inzicht.
De invoer wordt automatisch opgehaald uit het `template_PVtool5_0.xlsx` ([resultaten Shansep]) indien er eerder resultaten zijn opgeslagen voor de betreffende verzameling.
    """))
    display(Markdown("**Opgeven gemiddelde waarden (fit):**"))
    display(grid_gem)
    display(Markdown("**Opgeven karakteristieke waarden (fit):**"))
    display(grid_kar)
    return hand_widgets_kar, hand_widgets_gem


def show_shansep_analysis(
        dbase,
        widgets_kar,
        widgets_gem,
        dropdown_verzameling_shansep,
        dropdown_type_proef_shansep,
        dropdown_rekpercentage_txt_shansep,
        dropdown_rekpercentage_dss_shansep,
        multi_select_verzameling_shansep,
        alpha_widget,
):
    if dropdown_type_proef_shansep.value.startswith('TXT'):
        rekpercentage = dropdown_rekpercentage_txt_shansep.value
    else:
        rekpercentage = dropdown_rekpercentage_dss_shansep.value

    analyse = SHANSEP(
        dbase=dbase,
        investigation_groups=[dropdown_verzameling_shansep.value],
        effective_stress=rekpercentage,
        analysis_type=dropdown_type_proef_shansep.value
    )
    analyse.apply_settings(alpha=alpha_widget.value)
    analyse.set_parameters_handmatig(
        snijpunt_gem=widgets_gem[0].value,
        s_gem=widgets_gem[1].value,
        m_gem=widgets_gem[2].value,
        snijpunt_kar=widgets_kar[0].value,
        s_kar=widgets_kar[1].value,
        m_kar=widgets_kar[2].value
    )

    # Toon resultaten
    output_df = analyse.get_short_results()
    print(output_df)

    # Figuur tonen
    extra_verzamelingen_tonen = list(multi_select_verzameling_shansep.value)
    analyse.show_figure_sv_su(plot_extra_dataset=extra_verzamelingen_tonen)
    analyse.show_figure_ln_ocr_ln_s(plot_extra_dataset=extra_verzamelingen_tonen)
    analyse.show_figure_sv_su_nc(plot_extra_dataset=extra_verzamelingen_tonen)
    return analyse, output_df


def export_shansep_results(analyse,
                           dropdown_verzameling,
                           dropdown_type_proef_shansep,
                           import_dropdown,
                           import_filechooser,
                           export_dir_widget=None,
                           export_name_widget=None):
    """Exporteert de resultaten."""
    if import_dropdown.value == 'Proevenverzamelingtool 5.0':
        import_path = Path(import_filechooser.selected)
        export_dir = str(import_path.parent)
        export_name = import_path.name
    else:
        export_dir = export_dir_widget.selected_path if hasattr(export_dir_widget,
                                                                "selected_path") else export_dir_widget
        export_name = export_name_widget.value if hasattr(export_name_widget, "value") else export_name_widget
        if not export_name.lower().endswith('.xlsx'):
            export_name += '.xlsx'

    # resultaten toevoegen aan template
    analyse.add_results_to_template(path=export_dir, export_name=export_name)
    # exporteer figuren als plotly
    analyse.save_figs_html(path=export_dir)
    # export to pdf
    analyse.save_to_pdf(path=export_dir)
