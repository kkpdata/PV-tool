import ipywidgets as widgets
from ipywidgets import HTML
from ipyfilechooser import FileChooser
from IPython.display import display, Markdown, clear_output
import importlib.util
import subprocess
import sys
from pathlib import Path
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
import os
from pv_tool.sutabel_analysis.sutabel_analysis import SUTABEL
from pv_tool.utilities.widget_functions_cphi import maak_verzamelings_lijsten, koppel_callbacks


def maak_proef_widgets_su(pv_txt_lijst, pv_dss_lijst):
    """Maakt de widgets voor de proefkeuze, rekpercentage en verzamelingen"""
    # Dropdowns
    dropdown_type_proef_su = widgets.Dropdown(
        options=['TXT_su_tabel', 'DSS_su_tabel'],
        value='TXT_su_tabel',
        description='Type proef:',
        layout=widgets.Layout(width='400px')
    )
    dropdown_rekpercentage_txt_su = widgets.Dropdown(
        options=['2% rek', '5% rek', '15% rek', 'eindsterkte', 'pieksterkte'],
        value='eindsterkte',
        description='Rekpercentage TXT:',
        layout=widgets.Layout(width='400px')
    )
    dropdown_rekpercentage_dss_su = widgets.Dropdown(
        options=['2% rek', '5% rek', '10% rek', '15% rek', '20% rek', 'eindsterkte', 'pieksterkte'],
        value='eindsterkte',
        description='Rekpercentage DSS:',
        layout=widgets.Layout(width='400px')
    )
    dropdown_verzameling_su = widgets.Dropdown(
        options=pv_txt_lijst,
        value=pv_txt_lijst[0] if pv_txt_lijst else None,
        description='Verzameling:',
        layout=widgets.Layout(width='400px')
    )
    multi_select_verzameling_su = widgets.SelectMultiple(
        options=pv_txt_lijst,
        value=[pv_txt_lijst[0]] if pv_txt_lijst else [],
        description='Vergelijk met:',
        layout=widgets.Layout(width='400px', height='150px')
    )
    # Outputs
    container_rekpercentage_su = widgets.Output()
    output_rekpercentage_su = widgets.Output()

    return (dropdown_type_proef_su, dropdown_rekpercentage_txt_su, dropdown_rekpercentage_dss_su,
            dropdown_verzameling_su, multi_select_verzameling_su, container_rekpercentage_su, output_rekpercentage_su)


def toon_widgets_su(
        dropdown_type_proef_su, dropdown_verzameling_su, container_rekpercentage_su, output_rekpercentage_su,
        multi_select_verzameling_su
):
    """Toont alle widgets netjes onder elkaar."""
    display(Markdown("**Kies type proef:**"))
    display(dropdown_type_proef_su)
    display(Markdown("**Kies verzameling voor statistische analyse:**"))
    display(dropdown_verzameling_su)
    display(Markdown("**Kies rekpercentage Su:**"))
    display(container_rekpercentage_su)
    display(output_rekpercentage_su)
    display(Markdown(
        "**Kies één of meerdere verzamelingen om naast de gekozen verzameling voor de statistische analyse te tonen:**"))
    display(multi_select_verzameling_su)


def dropdown_widgets_su(dbase):
    dbase_df = dbase.dbase_df
    PV_txt_lijst, PV_dss_lijst = maak_verzamelings_lijsten(dbase_df)

    # Widgets aanmaken
    (dropdown_type_proef_su, dropdown_rekpercentage_txt_su, dropdown_rekpercentage_dss_su,
     dropdown_verzameling_su, multi_select_verzameling_su, container_rekpercentage_su,
     output_rekpercentage_su) = maak_proef_widgets_su(PV_txt_lijst, PV_dss_lijst)

    # 'gekozen_rekpercentage' als lijst zodat het binnen callbacks aanpasbaar blijft
    gekozen_rekpercentage_su = ['eindsterkte']

    # Koppel callbacks
    koppel_callbacks(
        dropdown_type_proef_su, dropdown_rekpercentage_txt_su, dropdown_rekpercentage_dss_su,
        dropdown_verzameling_su, multi_select_verzameling_su, container_rekpercentage_su,
        output_rekpercentage_su, PV_txt_lijst, PV_dss_lijst, gekozen_rekpercentage_su
    )

    # Toon alles
    toon_widgets_su(
        dropdown_type_proef_su, dropdown_verzameling_su, container_rekpercentage_su,
        output_rekpercentage_su, multi_select_verzameling_su
    )
    return (dropdown_type_proef_su, dropdown_verzameling_su, dropdown_rekpercentage_txt_su,
            dropdown_rekpercentage_dss_su, container_rekpercentage_su, output_rekpercentage_su,
            multi_select_verzameling_su, gekozen_rekpercentage_su)


def toon_grid_settings_su():
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


def get_benaderingswaarden(analyse):
    a2_kar = round(analyse.a2_kar_sutabel, 2) if analyse.a2_kar_sutabel is not None else None
    a1_kar = round(analyse.a1_kar_sutabel, 2) if analyse.a1_kar_sutabel is not None else None
    vc = round(analyse.vc_fit_kar_sutabel, 2) if analyse.vc_fit_kar_sutabel is not None else None
    return a2_kar, a1_kar, vc


def create_param_grid(a2, a1, vc, handmatig_init=None):
    if handmatig_init is None:
        handmatig_init = (a2, a1, vc)
    grid = widgets.GridspecLayout(3,4, width='1050px')

    # Eerste rij: Titels
    grid[0, 0] = widgets.Label(f'Parameters', layout=widgets.Layout(width='200px'))
    grid[0, 1] = HTML(value=f'a2<sub>kar</sub> helling ln(&sigma;&#x27;<sub>v</sub>)/ln(su)', layout=widgets.Layout(width='200px'))
    grid[0, 2] = HTML(value=f'a1<sub>kar</sub> snijpunt y-as ln(S<sub>u</sub>) [-]', layout=widgets.Layout(width='200px'))
    grid[0, 3] = widgets.Label(f'Bepaal variatiecoëfficiënt [-]', layout=widgets.Layout(width='200px'))

    # Tweede rij: benaderingswaarden
    grid[1, 0] = widgets.Label(f'Benadering', layout=widgets.Layout(width='300px'))
    grid[1, 1] = widgets.Label(f'{a2}', layout=widgets.Layout(width='200px'))
    grid[1, 2] = widgets.Label(f'{a1}', layout=widgets.Layout(width='200px'))
    grid[1, 3] = widgets.Label(f'{vc if vc is not None else "-"}', layout=widgets.Layout(width='200px'))

    # Derde rij: handmatig
    a2_handmatig = widgets.FloatText(value=handmatig_init[0], step=0.01, layout=widgets.Layout(width='200px'), placeholder='-')
    a1_handmatig = widgets.FloatText(value=handmatig_init[1], step=0.01, layout=widgets.Layout(width='200px'), placeholder='-')

    if handmatig_init[2] is None:
        vc_handmatig = widgets.FloatText(value=None, step=0.01, layout=widgets.Layout(width='200px'),
                                         placeholder='-')
    else:
        vc_handmatig = widgets.FloatText(value=handmatig_init[2], step=0.01, layout=widgets.Layout(width='200px'),
                                         placeholder='-')


    grid[2, 0] = widgets.Label(f'Handmatige invoer', layout=widgets.Layout(width='300px'))
    grid[2, 1] = a2_handmatig
    grid[2, 2] = a1_handmatig
    grid[2, 3] = vc_handmatig

    return grid, (a2_handmatig, a1_handmatig, vc_handmatig)


def run_su_analysis(
        dbase,
        dropdown_verzameling_su,
        alpha_widget,
        import_dropdown,
        import_filechooser,
        dropdown_rekpercentage_txt_su,
        dropdown_rekpercentage_dss_su,
        dropdown_type_proef_su,
        export_dir_widget=None,
        export_name_widget=None
):
    verzameling = dropdown_verzameling_su.value
    rekpercentage = dropdown_rekpercentage_txt_su.value if dropdown_type_proef_su.value.startswith(
        'TXT') else dropdown_rekpercentage_dss_su.value

    analyse = SUTABEL(
        dbase=dbase,
        investigation_groups=[verzameling],
        effective_stress=rekpercentage,
        analysis_type=dropdown_type_proef_su.value
    )

    analyse.apply_settings(alpha=alpha_widget.value)
    analyse._run_sutabel()

    # krijg eerste benadering parameters
    a2_kar, a1_kar, cv = get_benaderingswaarden(analyse)

    # Grid aanmaken
    grid, handmatige_widgets = create_param_grid(a2_kar, a1_kar, cv)
    display(Markdown("**Opgegeven karakteristieke waarden (fit):**"))
    display(grid)
    return analyse, handmatige_widgets


def show_su_analysis(
        dbase,
        dropdown_verzameling_su,
        dropdown_type_proef_su,
        dropdown_rekpercentage_txt_su,
        dropdown_rekpercentage_dss_su,
        a2_handmatig,
        a1_handmatig,
        cv_handmatig,
        multi_select_verzameling_su,
        alpha_widget,
        import_dropdown,
        import_filechooser,
):
    # Kies rekpercentage afhankelijk van type proef
    if dropdown_type_proef_su.value.startswith('TXT'):
        rekpercentage = dropdown_rekpercentage_txt_su.value
    else:
        rekpercentage = dropdown_rekpercentage_dss_su.value

    # Initialiseer analyse
    analyse = SUTABEL(
        dbase=dbase,
        analysis_type=dropdown_type_proef_su.value,
        investigation_groups=[dropdown_verzameling_su.value],
        effective_stress=rekpercentage
    )

    analyse.apply_settings(alpha=alpha_widget.value)
    analyse.set_manual_parameters(a1_kar=a1_handmatig, a2_kar=a2_handmatig, vc_fit_kar=cv_handmatig)


    # Toon resultaten
    output_df = analyse.get_short_results()
    print(output_df)

    # Toon figuren
    extra_verzameling_tonen = list(multi_select_verzameling_su.value)
    analyse.show_figure_sv_su_sutabel(plot_extra_dataset=extra_verzameling_tonen)
    analyse.show_figure_ln_sv_ln_su_sutabel(plot_extra_dataset=extra_verzameling_tonen)
    return analyse, output_df


def export_su_results(
        analyse,
        dropdown_verzameling_su,
        dropdown_type_proef_su,
        import_dropdown,
        import_filechooser,
        export_dir_widget,
        export_name_widget
):
    """Exporteert de resultaten."""
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

    # Resultaten toevoegen aan template
    analyse.add_results_to_template(path=export_dir, export_name=export_name)
    # Exporteer figuren als plotly
    analyse.save_figs_html(path=export_dir)
    # Exporteer naar pdf
    analyse.save_to_pdf(path=export_dir)
