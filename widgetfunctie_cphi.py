import ipywidgets as widgets
from ipyfilechooser import FileChooser
from IPython.display import display, Markdown, clear_output
import importlib.util
import subprocess
import sys
from pathlib import Path
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse


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
    display(widgets.VBox([dir_chooser, name_box]))
    return dir_chooser, name_box


def process_import_and_validate(dbase, template_name, file_path, export_dir):
    """Importeert, valideert en exporteert validatierapporten."""
    template_code = determine_template_code(template_name)
    display(Markdown(f"**Template-code:** {template_code}"))
    dbase.import_data(source=template_code, source_dir=file_path)
    dbase.validate_data(export_path=export_dir)
    display(Markdown(f"**Validatierapporten geëxporteerd naar:** {export_dir}"))


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
        options=['TXT_CPhi', 'DSS_CPhi'],
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
    dropdown_verzameling = widgets.Dropdown(  # TODO: moet hier ook DSS in kunnen?
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
            if dropdown_type_proef.value == 'TXT_CPhi':
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


def toon_cphi_tabel(
        PV_A2_PHI_GEM_benadering,
        PV_A1_COH_GEM_benadering,
        PV_A2_PHI_KAR_benadering,
        PV_A1_COH_KAR_benadering,
        PV_A1_COH_GEM_handmatig_ref,
        PV_A2_PHI_KAR_handmatig_ref,
        PV_A1_COH_KAR_handmatig_ref,
        PV_PARTPHI_ref,
        PV_PARTCOH_ref,
        PV_TYPEVERZAMELING_ref,
        dropdown_verzameling_txt,
        gekozen_rekpercentage
):
    """
    Toont een interactieve tabel voor C-phi invoer.
    """

    grid = widgets.GridspecLayout(8, 3)
    grid[0, 0] = widgets.Label('Beschrijving')
    grid[0, 1] = widgets.Label('Benadering')
    grid[0, 2] = widgets.Label('Invoer')

    descriptions = [
        'a2gem (phi gemiddeld)',
        'a1gem =snijpunt y-as (cohesie gemiddeld)',
        'a2kar (phi karakteristiek)',
        'a1kar =snijpunt y-as (cohesie karakteristiek)',
        'partiele materiaalfactor tan phi [-]',
        'partiele materiaalfactor cohesie [-]',
        'type verzameling: lokaal = 1,0; regionaal = 0,75',
    ]

    benadering_values = [
        PV_A2_PHI_GEM_benadering,
        PV_A1_COH_GEM_benadering,
        PV_A2_PHI_KAR_benadering,
        PV_A1_COH_KAR_benadering,
        '-', '-', '-',
    ]

    # De referenties naar de lijstjes voor live bijwerken
    invoer_refs = [
        None,
        PV_A1_COH_GEM_handmatig_ref,
        PV_A2_PHI_KAR_handmatig_ref,
        PV_A1_COH_KAR_handmatig_ref,
        PV_PARTPHI_ref,
        PV_PARTCOH_ref,
        PV_TYPEVERZAMELING_ref,
    ]

    def on_value_change(change, ref):  # TODO: ref geeft een waarschuwing. De code werkt, maar oplossen
        if ref is not None:
            try:
                ref[0] = float(change['new'])
            except Exception:
                pass  # eventueel kun je hier validatie toevoegen

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
    dropdown_verzameling,
    dropdown_type_proef,
    dropdown_rekpercentage_txt,
    dropdown_rekpercentage_dss,
    export_dir_widget,
    export_name_widget,
    gekozen_rekpercentage,
    toon_cphi_tabel
):
    """Voert de C-Phi analyse uit en toont het resultaat in een interactieve tabel."""
    verzameling = dropdown_verzameling.value
    rekpercentage = dropdown_rekpercentage_txt.value if dropdown_type_proef.value.startswith(
        'TXT') else dropdown_rekpercentage_dss.value

    # Ophalen van directory en bestandsnaam uit widgets
    export_dir = export_dir_widget.selected_path
    export_name = export_name_widget.value
    if not export_name.lower().endswith('.xlsx'):
        export_name += '.xlsx'

    # C-phi analyse uitvoeren
    analyse = CPhiAnalyse(
        dbase=dbase,
        investigation_groups=[verzameling],
        effective_stress=rekpercentage,
        analysis_type=dropdown_type_proef.value
    )
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
        PV_PARTPHI = [laatste_resultaten['PV_PARTPHI']]
        PV_PARTCOH = [laatste_resultaten['PV_PARTCOH']]
        PV_TYPEVERZAMELING = [laatste_resultaten['PV_TYPEVERZAMELING']]
    else:
        PV_A1_COH_GEM_handmatig = [PV_A1_COH_GEM_benadering]
        PV_A2_PHI_KAR_handmatig = [PV_A2_PHI_KAR_benadering]
        PV_A1_COH_KAR_handmatig = [PV_A1_COH_KAR_benadering]
        PV_PARTPHI = [1]
        PV_PARTCOH = [1]
        PV_TYPEVERZAMELING = [0.75]

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
        PV_PARTPHI,
        PV_PARTCOH,
        PV_TYPEVERZAMELING,
        dropdown_verzameling,
        gekozen_rekpercentage
    )

    # Handig voor vervolg
    return analyse, PV_A1_COH_GEM_handmatig, PV_A2_PHI_KAR_handmatig, PV_A1_COH_KAR_handmatig, PV_PARTPHI, PV_PARTCOH, PV_TYPEVERZAMELING










