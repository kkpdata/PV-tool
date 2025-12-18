import ipywidgets as widgets
from ipyfilechooser import FileChooser
from IPython.display import display, Markdown
import importlib.util
import subprocess
import sys


# Functie om te controleren of een package is geïnstalleerd
def check_package_install(package_name):
    package_spec = importlib.util.find_spec(package_name)
    if package_spec is None:
        print(f"{package_name} is niet geïnstalleerd. Installatie wordt gestart...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    else:
        print(f"{package_name} is al geïnstalleerd.")


def create_import_dropdown():
    return widgets.Dropdown(
        options=[
            'Proevenverzamelingtool 4.2n of hoger',
            'STOWA uitwisselingsformat 4.2x',
            'Proevenverzamelingtool 5.0'
        ],
        value='Proevenverzamelingtool 5.0',
        description='Template:',
        disabled=False,
        layout=widgets.Layout(width='400px')
    )


def create_file_chooser():
    return FileChooser(
        '/',
        title="Selecteer een bestand om te uploaden",
        show_hidden=False
    )


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
    Toont een interactieve tabel voor C-phi invoer. Elke parameter wordt als 1-elementige lijst doorgegeven,
    zodat de actuele waarde direct uitleesbaar blijft in de notebook.
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
        # ref is een 1-elementige lijst
        if ref is not None:
            try:
                ref[0] = float(change['new'])
            except Exception:
                pass  # eventueel kun je hier validatie toevoegen

    # Vul de tabel
    for i, (desc, benadering, ref) in enumerate(zip(descriptions, benadering_values, invoer_refs)):
        grid[i + 1, 0] = widgets.Label(desc)
        grid[i + 1, 1] = widgets.Label(str(benadering))
        if i == 0:
            grid[i + 1, 2] = widgets.Label('-')
        else:
            # Gebruik altijd ref[0] als startwaarde, nooit de hele lijst!
            input_widget = widgets.FloatText(value=ref[0])
            grid[i + 1, 2] = input_widget
            input_widget.observe(lambda change, ref=ref: on_value_change(change, ref), names='value')

    display(Markdown(
        f"**Verzameling en rekpercentage: {dropdown_verzameling_txt.value}, s'-t bij: {gekozen_rekpercentage}**"

    ))
    display(Markdown("**Opgeven invoer effectieve schuifsterkteparameters (fit):**"))
    display(grid)
