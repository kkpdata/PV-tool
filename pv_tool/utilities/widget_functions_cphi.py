import ipywidgets as widgets
from ipyfilechooser import FileChooser
from IPython.display import display, Markdown, clear_output
import importlib.util
import subprocess
import sys
from pathlib import Path
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse
import os


def check_package_install(package_name):
    """Checkt of een package is geïnstalleerd; zo niet, wordt het geïnstalleerd."""
    if importlib.util.find_spec(package_name) is None:
        display(Markdown(f"**{package_name} wordt geïnstalleerd...**"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    else:
        display(Markdown(f"**{package_name} is al geïnstalleerd.**"))


def create_import_dropdown():
    """Maakt een dropdown voor templates."""
    return widgets.Dropdown(
        options=[
            'Proevenverzamelingtool 4.2n of hoger',
            'STOWA uitwisselingsformat 4.2x',
            'Proevenverzamelingtool 5.0'
        ],
        value='Proevenverzamelingtool 5.0',
        description='Template:',
        layout=widgets.Layout(width='400px')
    )


def create_file_chooser(folder='/'):
    """Geeft een FileChooser-widget."""
    return FileChooser(
        folder,
        title="Selecteer een bestand om te uploaden",
        show_hidden=False
    )


def determine_template_code(template_name):
    """Bepaalt de code op basis van de gekozen template."""
    mapping = {
        "Proevenverzamelingtool 4.2n of hoger": "PV-tool",
        "STOWA uitwisselingsformat 4.2x": "Stowa",
        "Proevenverzamelingtool 5.0": "Dbase"
    }
    return mapping.get(template_name, "Onbekend template")


def select_export_location_and_name(default_filename="Template_PVtool5_0.xlsx"):
    """Laat gebruiker exportlocatie en -naam kiezen."""
    dir_chooser = FileChooser(use_dir_icons=True, select_default=True, show_only_dirs=True)
    dir_chooser.title = "<b>Kies een exportmap</b>"
    name_box = widgets.Text(
        value=default_filename,
        description='Bestandsnaam:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='50%')
    )
    return widgets.VBox([dir_chooser, name_box]), dir_chooser, name_box


def toon_grid_settings():
    """
    Toon een grid met materiaalfactoren en alpha.
    Als type_proef eindigt op 'SH', dan wordt partcoh_widget niet getoond.
    """
    display(Markdown("**Pas alpha aan (lokaal = 1,0, regionaal = 0,75):**"))
    alpha_widget = widgets.FloatText(
        value=0.75,
        description='Alpha :',
        step=0.01
    )
    display(widgets.VBox([alpha_widget]))

    display(Markdown("**Pas materiaalfactoren aan:**"))
    partphi_widget = widgets.FloatText(
        value=1.0,
        description='φ :',
        step=0.01
    )
    partcoh_widget = widgets.FloatText(
        value=1.0,
        description='c :',
        step=0.01
    )

    display(widgets.VBox([partphi_widget, partcoh_widget]))
    return alpha_widget, partphi_widget, partcoh_widget


def setup_interactive_import_export():
    import_dropdown = create_import_dropdown()
    import_filechooser = create_file_chooser()
    export_box, export_dirchooser, export_namebox = select_export_location_and_name()

    export_placeholder = widgets.Output()

    def update_export_selection(*args):
        with export_placeholder:
            clear_output()
            if import_dropdown.value == "Proevenverzamelingtool 5.0":
                if import_filechooser.selected:
                    export_path = import_filechooser.selected
                    display(widgets.HTML(
                        f"<b>Exportbestand is gelijk aan importbestand:</b><br>{export_path}"
                    ))
                else:
                    display(widgets.HTML(
                        "<i>Kies eerst een bestand om deze functie te activeren.</i>"
                    ))
            else:
                display(export_box)

    import_dropdown.observe(update_export_selection, names='value')
    import_filechooser.register_callback(update_export_selection)

    display(import_dropdown)
    display(import_filechooser)
    display(export_placeholder)

    update_export_selection()

    return import_dropdown, import_filechooser, export_dirchooser, export_namebox


def process_import_and_validate(dbase, template_name, file_path, export_dir):
    """Importeert, valideert en exporteert validatierapporten."""
    template_code = determine_template_code(template_name)
    display(Markdown(f"**Template-code:** {template_code}"))
    dbase.import_data(source=template_code, source_dir=file_path)
    dbase.validate_data(export_path=export_dir)
    display(Markdown(f"**Validatierapporten geëxporteerd naar:** {export_dir}"))


def handle_import_export(
    dbase,
    import_dropdown,
    import_filechooser,
    export_dirchooser,
    process_import_and_validate
):
    # Validatie
    if not import_dropdown.value:
        print("Er is geen template geselecteerd.")
        return
    if not import_filechooser.selected:
        print("Er is geen bestand geselecteerd. Selecteer een bestand voordat je verder gaat.")
        return

    # Bepaal exportmap
    if import_dropdown.value == "Proevenverzamelingtool 5.0":
        export_dir = os.path.dirname(import_filechooser.selected)
    else:
        export_dir = export_dirchooser.selected_path
        if not export_dir:
            print("Selecteer een exportlocatie.")
            return

    # Aanroepen van de hoofd-functionaliteit
    process_import_and_validate(
        dbase=dbase,
        template_name=import_dropdown.value,
        file_path=import_filechooser.selected,
        export_dir=Path(export_dir)   # Alleen de map!
    )


def process_import_only(dbase, template_name, file_path):
    """
    Importeert alleen de data, zonder validatie of export.
    """
    template_code = determine_template_code(template_name)
    display(Markdown(f"**Template-code:** {template_code}"))
    dbase.import_dbase_short(source=template_code, source_dir=file_path)
    display(Markdown(f"**Data geïmporteerd uit:** {file_path}"))


def handle_import_only(
    dbase,
    import_dropdown,
    import_filechooser,
    process_import_only
):
    # Validatie
    if not import_dropdown.value:
        print("Er is geen template geselecteerd.")
        return
    if not import_filechooser.selected:
        print("Er is geen bestand geselecteerd. Selecteer een bestand voordat je verder gaat.")
        return

    # Alleen import uitvoeren
    process_import_only(
        dbase=dbase,
        template_name=import_dropdown.value,
        file_path=import_filechooser.selected
    )


def process_export(dbase, export_dir, filename=None):
    """Exporteert dbase naar Excel."""
    export_filename = filename or "Template_PVtool5_0.xlsx"
    if not export_filename.lower().endswith('.xlsx'):
        export_filename += '.xlsx'
    out_path = Path(export_dir) / export_filename
    dbase.export_dbase_to_template(export_dir=export_dir, export_name=export_filename)
    display(Markdown(f"**DataFrame geëxporteerd naar:** `{out_path}`"))


def maak_verzamelings_lijsten(dbase_df):
    """
    Genereert lijsten met unieke verzamelnamen voor TXT en DSS.
    """
    pv_txt_lijst = ['geen'] + dbase_df.loc[dbase_df['ALG__TRIAXIAAL'], 'PV_NAAM'].dropna().unique().tolist()
    pv_dss_lijst = ['geen'] + dbase_df.loc[dbase_df['ALG__DSS'], 'PV_NAAM'].dropna().unique().tolist()
    return pv_txt_lijst, pv_dss_lijst


def maak_proef_widgets(pv_txt_lijst, pv_dss_lijst):
    """Maakt de widgets voor de proefkeuze, rekpercentage en verzamelingen"""
    # Dropdowns
    dropdown_type_proef = widgets.Dropdown(
        options=['TXT_CPhi', 'DSS_CPhi', 'TXT_SH', 'DSS_SH'],
        value='TXT_CPhi',
        description='Type proef:',
        layout=widgets.Layout(width='400px')
    )
    dropdown_rekpercentage_txt = widgets.Dropdown(
        options=['2% rek', '5% rek', '15% rek', 'eindsterkte', 'pieksterkte'],
        value='eindsterkte',
        description='Rekpercentage TXT:',
        layout=widgets.Layout(width='400px')
    )
    dropdown_rekpercentage_dss = widgets.Dropdown(
        options=['2% rek', '5% rek', '10% rek', '15% rek', '20% rek', 'eindsterkte', 'pieksterkte'],
        value='eindsterkte',
        description='Rekpercentage DSS:',
        layout=widgets.Layout(width='400px')
    )
    dropdown_verzameling = widgets.Dropdown(
        options=pv_txt_lijst,
        value=pv_txt_lijst[0] if pv_txt_lijst else None,
        description='Verzameling:',
        layout=widgets.Layout(width='400px')
    )
    multi_select_verzameling = widgets.SelectMultiple(
        options=pv_txt_lijst,
        value=[pv_txt_lijst[0]] if pv_txt_lijst else [],
        description='Vergelijk met:',
        layout=widgets.Layout(width='400px', height='150px')
    )
    # Outputs
    container_rekpercentage = widgets.Output()
    output_rekpercentage = widgets.Output()

    return (dropdown_type_proef, dropdown_rekpercentage_txt, dropdown_rekpercentage_dss,
            dropdown_verzameling, multi_select_verzameling, container_rekpercentage, output_rekpercentage)


def koppel_callbacks(
    dropdown_type_proef, dropdown_rekpercentage_txt, dropdown_rekpercentage_dss,
    dropdown_verzameling, multi_select_verzameling, container_rekpercentage, output_rekpercentage,
    pv_txt_lijst, pv_dss_lijst, gekozen_rekpercentage
):
    """Koppelt interacties tussen widgets en zorgt dat de juiste opties getoond worden."""
    def update_verzamelings_dropdowns(change=None):
        with container_rekpercentage:
            clear_output()
            if dropdown_type_proef.value in ['TXT_CPhi', 'TXT_SH']:
                dropdown_verzameling.options = pv_txt_lijst
                dropdown_verzameling.value = pv_txt_lijst[0]
                multi_select_verzameling.options = pv_txt_lijst
                multi_select_verzameling.value = [pv_txt_lijst[0]]
                display(dropdown_rekpercentage_txt)
            else:
                dropdown_verzameling.options = pv_dss_lijst
                dropdown_verzameling.value = pv_dss_lijst[0]
                multi_select_verzameling.options = pv_dss_lijst
                multi_select_verzameling.value = [pv_dss_lijst[0]]
                display(dropdown_rekpercentage_dss)
        update_rekpercentage_output(None)

    def update_rekpercentage_output(change=None):
        nonlocal gekozen_rekpercentage
        with output_rekpercentage:
            clear_output()
            if dropdown_type_proef.value == 'TXT_CPhi':
                gekozen_rekpercentage = dropdown_rekpercentage_txt.value
            else:
                gekozen_rekpercentage = dropdown_rekpercentage_dss.value

    dropdown_type_proef.observe(update_verzamelings_dropdowns, names='value')
    dropdown_rekpercentage_txt.observe(update_rekpercentage_output, names='value')
    dropdown_rekpercentage_dss.observe(update_rekpercentage_output, names='value')

    # Initialiseren container
    with container_rekpercentage:
        clear_output()
        display(dropdown_rekpercentage_txt)
    with output_rekpercentage:
        clear_output()
    return update_verzamelings_dropdowns, update_rekpercentage_output


def toon_widgets(
    dropdown_type_proef, dropdown_verzameling, container_rekpercentage, output_rekpercentage, multi_select_verzameling
):
    """Toont alle widgets netjes onder elkaar."""
    display(Markdown("**Kies type proef:**"))
    display(dropdown_type_proef)
    display(Markdown("**Kies verzameling voor statistische analyse:**"))
    display(dropdown_verzameling)
    display(Markdown("**Kies rekpercentage s'en t:**"))
    display(container_rekpercentage)
    display(output_rekpercentage)
    display(Markdown("**Kies één of meerdere verzamelingen om naast de gekozen verzameling voor de statistische analyse te tonen:**"))
    display(multi_select_verzameling)


def dropdown_widgets(dbase):
    # Lijsten aanmaken
    dbase_df = dbase.dbase_df
    PV_txt_lijst, PV_dss_lijst = maak_verzamelings_lijsten(dbase_df)

    # Widgets aanmaken
    (dropdown_type_proef, dropdown_rekpercentage_txt, dropdown_rekpercentage_dss,
     dropdown_verzameling, multi_select_verzameling, container_rekpercentage,
     output_rekpercentage) = maak_proef_widgets(PV_txt_lijst, PV_dss_lijst)

    gekozen_rekpercentage = ['eindsterkte']

    # Koppel callbacks
    koppel_callbacks(
        dropdown_type_proef, dropdown_rekpercentage_txt, dropdown_rekpercentage_dss,
        dropdown_verzameling, multi_select_verzameling, container_rekpercentage, output_rekpercentage,
        PV_txt_lijst, PV_dss_lijst, gekozen_rekpercentage)

    # Toon alles
    toon_widgets(
        dropdown_type_proef, dropdown_verzameling, container_rekpercentage, output_rekpercentage,
        multi_select_verzameling
    )
    return (dropdown_type_proef, dropdown_verzameling, dropdown_rekpercentage_txt, dropdown_rekpercentage_dss,
            container_rekpercentage, output_rekpercentage, multi_select_verzameling, gekozen_rekpercentage)


def toon_cphi_tabel(
        PV_A2_PHI_GEM_benadering,
        PV_A1_COH_GEM_benadering,
        PV_A2_PHI_KAR_benadering,
        PV_A1_COH_KAR_benadering,
        PV_A1_COH_GEM_handmatig_ref,
        PV_A2_PHI_KAR_handmatig_ref,
        PV_A1_COH_KAR_handmatig_ref,
        dropdown_verzameling_txt,
        gekozen_rekpercentage
):
    """
    Toont een interactieve tabel voor C-phi invoer.
    """

    grid = widgets.GridspecLayout(5, 3)
    grid[0, 0] = widgets.Label('Beschrijving')
    grid[0, 1] = widgets.Label('Benadering')
    grid[0, 2] = widgets.Label('Invoer')

    descriptions = [
        'a2gem (phi gemiddeld)',
        'a1gem =snijpunt y-as (cohesie gemiddeld)',
        'a2kar (phi karakteristiek)',
        'a1kar =snijpunt y-as (cohesie karakteristiek)',
    ]

    benadering_values = [
        PV_A2_PHI_GEM_benadering,
        PV_A1_COH_GEM_benadering,
        PV_A2_PHI_KAR_benadering,
        PV_A1_COH_KAR_benadering,
    ]

    # De referenties naar de lijstjes voor live bijwerken
    invoer_refs = [
        None,
        PV_A1_COH_GEM_handmatig_ref,
        PV_A2_PHI_KAR_handmatig_ref,
        PV_A1_COH_KAR_handmatig_ref,
    ]

    def on_value_change(change, ref):  # TODO: ref geeft een waarschuwing. De code werkt, maar oplossen
        if ref is not None:
            try:
                ref[0] = float(change['new'])
            except Exception as e:
                print(f"Fout bij het bijwerken van de waarde: {e}")

    for i, (desc, benadering, ref) in enumerate(zip(descriptions, benadering_values, invoer_refs)):
        grid[i + 1, 0] = widgets.Label(desc)
        grid[i + 1, 1] = widgets.Label(str(benadering))
        if i == 0:
            grid[i + 1, 2] = widgets.Label('-')
        else:
            input_widget = widgets.FloatText(value=ref[0])
            grid[i + 1, 2] = input_widget
            input_widget.observe(lambda change, ref=ref: on_value_change(change, ref), names='value')

    display(Markdown(
        f"**Verzameling en rekpercentage: {dropdown_verzameling_txt.value}, s'-t bij: {gekozen_rekpercentage}**"

    ))
    display(Markdown("**Opgeven invoer effectieve schuifsterkteparameters (fit):**"))
    display(grid)


def voer_cphi_analyse_uit(
    dbase,
    import_dropdown,
    import_filechooser,
    dropdown_verzameling,
    dropdown_type_proef,
    dropdown_rekpercentage_txt,
    dropdown_rekpercentage_dss,
    gekozen_rekpercentage,
    toon_cphi_tabel,
    partphi_widget,
    alpha_widget,
    partcoh_widget=None,
    export_dir_widget=None,
    export_name_widget=None,
):
    """Voert de C-Phi analyse uit en toont het resultaat in een interactieve tabel."""
    verzameling = dropdown_verzameling.value
    rekpercentage = dropdown_rekpercentage_txt.value if dropdown_type_proef.value.startswith(
        'TXT') else dropdown_rekpercentage_dss.value

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

    # C-phi analyse uitvoeren
    analyse = CPhiAnalyse(
        dbase=dbase,
        investigation_groups=[verzameling],
        effective_stress=rekpercentage,
        analysis_type=dropdown_type_proef.value
    )

    if dropdown_type_proef.value in ['TXT_CPhi', 'DSS_CPhi']:
        analyse._run()

        # Benaderingswaarden ophalen
        PV_A2_PHI_GEM_benadering = round(analyse.eerste_benadering_a2_gem, 2)
        PV_A1_COH_GEM_benadering = round(analyse.eerste_benadering_a1_gem, 2)
        PV_A2_PHI_KAR_benadering = round(analyse.eerste_benadering_a2_kar, 2)
        PV_A1_COH_KAR_benadering = round(analyse.eerste_benadering_a1_kar, 2)

    # Ophalen handmatige waardes of defaults
        laatste_resultaten = analyse.get_previous_results(path=export_dir, file_name=export_name)
        if (
            laatste_resultaten is not None and
            not laatste_resultaten.empty and
            'PV_A1_COH_GEM' in laatste_resultaten
        ):
            PV_A1_COH_GEM_handmatig = [laatste_resultaten['PV_A1_COH_GEM']]
            PV_A2_PHI_KAR_handmatig = [laatste_resultaten['PV_A2_TAN_PHI_KAR']]
            PV_A1_COH_KAR_handmatig = [laatste_resultaten['PV_A1_COH_KAR']]
        else:
            PV_A1_COH_GEM_handmatig = [PV_A1_COH_GEM_benadering]
            PV_A2_PHI_KAR_handmatig = [PV_A2_PHI_KAR_benadering]
            PV_A1_COH_KAR_handmatig = [PV_A1_COH_KAR_benadering]

    # Toelichting tonen
        display(Markdown("**Stel de raaklijnen voor de gemiddelde en karakteristieke waarden van de cohesie en hoek van inwendige wrijving vast:**"))
        display(Markdown("Op basis van regressie wordt een eerste benadering gegeven voor het snijpunt met de y-as (a1) en de helling (a2) voor de gemiddelde en karakteristieke waarde."))
        display(Markdown("Toets in de volgende stap bij het genereren van de grafieken of de raaklijnen juist zijn gekozen en pas deze aan naar eigen inzicht"))
        display(Markdown("De invoer wordt automatisch opgehaald uit het template_PVtool5_0.xlsx [resultaten] indien er eerder resultaten zijn opgeslagen voor de betreffende verzameling."))
        print()

        # Tabel tonen
        toon_cphi_tabel(
            PV_A2_PHI_GEM_benadering,
            PV_A1_COH_GEM_benadering,
            PV_A2_PHI_KAR_benadering,
            PV_A1_COH_KAR_benadering,
            PV_A1_COH_GEM_handmatig,
            PV_A2_PHI_KAR_handmatig,
            PV_A1_COH_KAR_handmatig,
            dropdown_verzameling,
            gekozen_rekpercentage
        )
        return analyse, PV_A1_COH_GEM_handmatig, PV_A2_PHI_KAR_handmatig, PV_A1_COH_KAR_handmatig
    elif dropdown_type_proef.value in ['TXT_SH', 'DSS_SH']:
        analyse._run_sh()
        display(Markdown("Geen extra invoer nodig voor de SH-proeven."))
        print()
        return analyse, None, None, None


def show_cphi_analysis(
    dbase,
    dropdown_verzameling,
    dropdown_type_proef,
    dropdown_rekpercentage_txt,
    dropdown_rekpercentage_dss,
    coh_gem,
    phi_kar,
    coh_kar,
    multi_select_verzameling,
    alpha_widget,
    partphi_widget,
    partcoh_widget=None,
):
    """
    Voer C-Phi analyse uit, toon resultaten, figuren en tabel.
    """
    # Kies rekpercentage afhankelijk van type proef
    if dropdown_type_proef.value.startswith('TXT'):
        rekpercentage = dropdown_rekpercentage_txt.value
    else:
        rekpercentage = dropdown_rekpercentage_dss.value

    if dropdown_type_proef.value in ['TXT_CPhi', 'DSS_CPhi']:
        # Initialiseer en configureer analyse
        analyse = CPhiAnalyse(
            dbase=dbase,
            investigation_groups=[dropdown_verzameling.value],
            effective_stress=rekpercentage,
            analysis_type=dropdown_type_proef.value
        )
        analyse.apply_parameters(
            cohesie_gem=coh_gem[0],
            phi_kar=phi_kar[0],
            cohesie_kar=coh_kar[0]
        )
        analyse.apply_settings(
            material_factor_cohesion=partcoh_widget.value,
            material_factor_tan_phi=partphi_widget.value,
            alpha=alpha_widget.value
        )

        # Toon resultaten
        output_df = analyse.get_short_results()
        print(output_df)
        # Figuur tonen
        extra_verzamelingen_tonen = list(multi_select_verzameling.value)
        analyse.show_figure(plot_extra_dataset=extra_verzamelingen_tonen)
        analyse.show_figure(plot_spanningspaden=True)

        return analyse, output_df
    elif dropdown_type_proef.value in ['TXT_SH', 'DSS_SH']:
        analyse = CPhiAnalyse(
            dbase=dbase,
            investigation_groups=[dropdown_verzameling.value],
            effective_stress=rekpercentage,
            analysis_type=dropdown_type_proef.value
        )
        # pas instellingen aan
        analyse.apply_settings(alpha=alpha_widget.value)
        # Print en exporteer resultaten
        print('\nResultaten TXT C-phi analyse (schematiseringshandleiding):')
        output_df = analyse.get_short_results()
        print(output_df)

        # Figuur tonen
        extra_verzamelingen_tonen = list(multi_select_verzameling.value)
        analyse.show_figure(plot_extra_dataset=extra_verzamelingen_tonen, plot_spanningspaden=True)
        return analyse, output_df


def export_results(analyse,
                   dropdown_verzameling,
                   dropdown_type_proef,
                   import_dropdown,
                   import_filechooser,
                   export_dir_widget=None,
                   export_name_widget=None):
    """Export de resultaten"""
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

    # resultaten toevoegen aan template
    analyse.add_results_to_template(path=export_dir, export_name=export_name)
    # exporteer figuren als plotly
    analyse.save_fig_html(path=export_dir)
    # export to pdf
    analyse.save_to_pdf(path=export_dir)



