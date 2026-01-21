from typing import TYPE_CHECKING, List
from pandas import ExcelWriter, concat
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, LongTable
import plotly.graph_objects as go
from PIL import Image as PILImage
from reportlab.platypus import Image as RLImage

if TYPE_CHECKING:
    from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse


def save_total_to_excel(self: "CPhiAnalyse", path: str):
    """
    Exporteert alle analysegegevens naar Excel.

    Slaat de volledige dataset met alle berekende kolommen op in een Excel bestand.
    De bestandsnaam wordt automatisch gegenereerd op basis van de analyse-instellingen.

    Parameters
    ----------
    path: str
        Map locatie waar het Excel-bestand moet worden opgeslagen
    self: CPhiAnalyse
        Instantie van de CPhiAnalyse klasse
    """
    # pas de effective stress naam aan zodat het weggeschreven kan worden in de bestandsnaam
    effective_stress = str(self.effective_stress).replace('%', 'procent_')
    effective_stress = str(effective_stress).replace(' ', '')

    # exporteer onder de juiste naam
    file_name = f"c_phi_export_test_{self.investigation_groups[0]}_{self.analysis_type}_{effective_stress}.xlsx"
    file_path = f"{path}/{file_name}"

    # Hernoem de kolommen voor een ander analyse type
    if self.analysis_type in ['DSS_CPhi', 'DSS_SH']:
        self.cphi_analyses_data_df = self.cphi_analyses_data_df.rename(columns={'S\'': '\u03C3 \'', 'T': '\u03C4'})

    # schrijf het totaal weg
    df_totaal = self.cphi_analyses_data_df
    with ExcelWriter(file_path, engine='openpyxl') as writer:
        df_totaal.to_excel(writer)


def _df_to_table_with_index(df, index_name='Index'):
    """
    Zet een DataFrame om naar een lijst voor gebruik in een PDF-tabel. Gebruikt in save_to_pdf.

    Parameters
    ----------
    df : DataFrame
        De DataFrame die moet worden omgezet
    index_name : str, optioneel
        Naam voor de index kolom (default='Index')

    Returns
    -------
    list
        Lijst met header en data rijen voor een PDF-tabel
    """
    header = [df.index.name or index_name] + df.columns.tolist()
    data = [[idx] + row.tolist() for idx, row in df.iterrows()]
    return [header] + data


def _create_input_table(self: "CPhiAnalyse") -> Table:
    """
    Maakt een tabel met de invoerselectie informatie. Gebruikt in save_to_pdf.

    Returns
    -------
    Table
        ReportLab tabel object met de invoerselectie informatie
    """
    columns_base = [
        'PV_NAAM', 'BORING_POSITIE', 'MONSTER_NIVEAU_NAP_VANAF', 'MONSTER_NIVEAU_NAP_TOT'
    ]
    if self.analysis_type in ['TXT_CPhi', 'TXT_SH']:
        columns_extra = ['TXT_SS_VOLUMEGEWICHT_NAT', 'TXT_SS_VOLUMEGEWICHT_DRG', 'TXT_SS_WATERGEHALTE_VOOR']
    else:
        columns_extra = ['DSS_VOLUMEGEWICHT_NAT', 'DSS_VOLUMEGEWICHT_DRG', 'DSS_WATERGEHALTE_VOOR']

    columns_data = self.cphi_analyses_data_df.iloc[:, 1:3].copy()
    table1_cols = columns_base + columns_extra
    table1_df = self.total_cphi_analyses_data_df[table1_cols].copy()
    table1_df.columns = ['Groep', 'Positie', 'NAP Vanaf [m]', 'NAP Tot [m]', 'VGW nat', 'VGW droog',
                         'Watergehalte voor']
    table1_df = concat([table1_df, columns_data], axis=1)
    table1_df = table1_df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) else x)

    t1_data = _df_to_table_with_index(table1_df, index_name="alg_boring_monsternummer_id")
    t1 = LongTable(t1_data, repeatRows=1, hAlign='LEFT')
    t1.setStyle(TableStyle([

        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    return t1


def _create_initial_values_table(self: "CPhiAnalyse") -> Table:
    """
    Maakt een tabel met de initiële waarden van de analyse. Gebruikt in save_to_pdf.

    Returns
    -------
    Table
        ReportLab tabel object met de initiële waarden
    """
    name_phi_kar_onder = 'a2 kar onder = tan(phi) karakteristiek ondergrens'
    name_phi_kar_boven = 'a2 kar boven = tan(phi) karakteristiek bovengrens'

    initial_values: List[list] = []

    if self.cohesie_gem_handmatig is not None:
        initial_values.append(['a1 gem = cohesie gemiddeld (handmatig)', round(self.cohesie_gem_handmatig, 3)])
    elif self.gem_a1 is not None:
        initial_values.append(['a1 gem = snijpunt y-as (cohesie gemiddeld)', round(self.gem_a1, 3)])

    if self.gem_a2 is not None:
        initial_values.append(['a2 gem = tan(phi) gemiddeld', round(self.gem_a2, 3)])

    if self.cohesie_kar_handmatig is not None:
        initial_values.append(['a1 kar = cohesie karakteristiek (handmatig)', round(self.cohesie_kar_handmatig, 3)])
    elif self.kar_a1 is not None:
        initial_values.append(['a1 kar = snijpunt y-as (cohesie karakteristiek)', round(self.kar_a1, 3)])

    if self.phi_kar_handmatig is not None:
        initial_values.append(['a2 kar = tan(phi) karakteristiek (handmatig)', round(self.phi_kar_handmatig, 3)])
    elif self.kar_a2 is not None:
        initial_values.append(['a2 kar = tan(phi) karakteristiek', round(self.kar_a2, 3)])

    if hasattr(self, 'a2_phi_kar_onder') and self.a2_phi_kar_onder is not None:
        initial_values.append([name_phi_kar_onder, round(self.a2_phi_kar_onder, 3)])
    if hasattr(self, 'a2_phi_kar_boven') and self.a2_phi_kar_boven is not None:
        initial_values.append([name_phi_kar_boven, round(self.a2_phi_kar_boven, 3)])

    initial_values.append(['Type verzameling: lokaal = 1.0; regionaal = 0.75', self.alpha])
    initial_values.append(['Partiële materiaalfactor cohesie [-]', self.material_cohesie])
    initial_values.append(['Partiële materiaalfactor tan phi [-]', self.material_tan_phi])

    t3 = Table([['Parameter', 'Waarde']] + initial_values, hAlign='LEFT')
    t3.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    return t3


def _create_results_table(self: "CPhiAnalyse") -> Table:
    """
    Maakt een tabel met de eindresultaten van de analyse. Gebruikt in save_to_pdf.

    Returns
    -------
    Table
        ReportLab tabel object met de resultaten
    """
    output_table_df = self.get_short_results().copy()
    output_table_df.index.name = 'Parameter'
    output_table_df = output_table_df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) else x)
    output_table_data = _df_to_table_with_index(output_table_df)
    output_table = Table(output_table_data, repeatRows=1, hAlign='LEFT')
    output_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    return output_table


def _get_manual_values_paragraphs(self: "CPhiAnalyse", styles) -> list:
    """
    Maakt een lijst van paragrafen met handmatig opgegeven waarden.

    Parameters
    ----------
    styles : dict
        ReportLab stylesheet met opmaakstijlen

    Returns
    -------
    list
        Lijst met ReportLab Paragraph objecten
    """
    paragraphs = []
    manual_texts = []
    if self.cohesie_gem_handmatig is not None:
        manual_texts.append(f"handmatig opgegeven: cohesie_gem_handmatig = {self.cohesie_gem_handmatig}")
    if self.phi_kar_handmatig is not None:
        manual_texts.append(f"handmatig opgegeven: phi_kar_handmatig = {self.phi_kar_handmatig}")
    if self.cohesie_kar_handmatig is not None:
        manual_texts.append(f"handmatig opgegeven: cohesie_kar_handmatig = {self.cohesie_kar_handmatig}")

    if manual_texts:
        paragraphs.append(Paragraph("Handmatig opgegeven waarden:", styles['Heading3']))
        for txt in manual_texts:
            paragraphs.append(Paragraph(txt, styles['Normal']))
    else:
        paragraphs.append(
            Paragraph("Geen handmatig opgegeven waarden, figuur gebaseerd op eerste inschatting",
                      styles['Normal']))

    return paragraphs


def save_to_pdf(self: "CPhiAnalyse", path: str) -> str:
    """
    Slaat de analyseresultaten op in een PDF-document, inclusief figuren, datatabellen en numerieke resultaten.

    De PDF bevat:
    - Titel met details van analyse
    - Overzichtsfiguur van de analyse
    - Tabel met invoerselectie informatie
    - Tabel met initiële waarden
    - Eventueel handmatig opgegeven waarden
    - Tabel met eindresultaten

    Parameters
    ----------
    path: str
        Map locatie waar het PDF-bestand moet worden opgeslagen

    self: CPhiAnalyse
        Instantie van de CPhiAnalyse klasse

    Returns
    -------
    str
        Het absolute pad naar het bestand van het aangemaakte PDF-bestand
    """
    # Maak titel en bestandsnaam
    title = (f"{self.analysis_type.split('_')[0]} {self.analysis_type.split('_')[1]} analyse met "
             f"{self.effective_stress} op {self.investigation_groups[0]}")
    file_name = (f"c_phi_pdf_export_{self.investigation_groups[0]}_{self.analysis_type}_"
                 f"{str(self.effective_stress).replace('%', 'procent_').replace(' ', '')}.pdf")
    file_path = f"{path}/{file_name}"

    # Maak en bewaar de figuur alleen als deze nog niet bestaat
    fig_path = f"{path}/temp_plot.png"
    if not hasattr(self, 'figure') or len(self.figure.data) == 0:
        self.show_title = False
        self.figure = go.Figure()
        self.set_figure()

    self.show_title = True
    fig_width = 1280
    fig_height = 720
    self.figure.write_image(fig_path, width=fig_width, height=fig_height, scale=4, format="png")

    # Maak het PDF-document
    doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Left', parent=styles['Normal'], alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='TitleLeft', parent=styles['Title'], alignment=TA_LEFT))
    story = [Paragraph(title, styles['TitleLeft']), Spacer(width=1, height=12)]

    # Voeg figuur toe met aangepaste grootte
    fig_path = f"{path}/temp_plot.png"

    # Laad PNG en bepaal pixelafmetingen
    with PILImage.open(fig_path) as im:
        img_width_px, img_height_px = im.size

    # Stel gewenste breedte in punten (bijv. 95% van PDF-breedte)
    max_width_pt = doc.width * 0.95

    # Bereken hoogte zodat verhouding gelijk blijft
    aspect = img_height_px / img_width_px
    img_width_pt = min(max_width_pt, doc.width)  # niet breder dan pagina
    img_height_pt = img_width_pt * aspect

    # Maak ReportLab Image aan
    img = RLImage(fig_path)
    img.drawWidth = img_width_pt
    img.drawHeight = img_height_pt
    img.hAlign = 'LEFT'

    story.append(img)
    story.append(Spacer(width=1, height=12))

    # Voeg initiële waarden toe
    story.append(
        Paragraph("Parameter bepaling fysisch realiseerbare ondergrens en gemiddelde waarden", styles['Heading2']))
    story.append(_create_initial_values_table(self))
    story.append(Spacer(1, 12))

    # Voeg resultaten toe
    story.append(Paragraph("Resultaten", styles['Heading2']))
    story.append(_create_results_table(self))
    story.append(Spacer(1, 12))

    # Voeg invoertabel toe
    story.append(Paragraph("Informatietabel invoerselectie", styles['Heading2']))
    story.append(_create_input_table(self))
    story.append(Spacer(1, 12))

    # Bouw de PDF
    doc.build(story)

    # Ruim tijdelijke plot bestanden op
    import os
    try:
        if os.path.exists(fig_path):
            os.remove(fig_path)
    except Exception as e:
        print(f"Waarschuwing: Kon tijdelijk plot bestand niet verwijderen {fig_path}: {e}")

    print(f"PDF succesvol opgeslagen op: {file_path}")
    return file_path
