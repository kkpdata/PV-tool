from typing import TYPE_CHECKING, List
from pandas import ExcelWriter, concat, DataFrame, read_excel
from datetime import datetime
from openpyxl import load_workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, LongTable
from pv_tool.imports.excel_utils import format_excel_sheet

if TYPE_CHECKING:
    from pv_tool.shansep_analysis.shansep_analysis import SHANSEP


def add_results_to_dbase(self: "SHANSEP", path: str, file_name: str = 'Template_PVtool5_0.xlsx'):
    """
    Voegt de SHANSEP analyseresultaten toe aan de database Excel-bestand.

    Parameters
    ----------
    self : SHANSEP
        Instantie van de SHANSEP analyse klasse
    path : str
        Pad naar de map waar het Excel-bestand staat
    file_name : str
        Naam van het Excel-bestand

    Returns
    -------
    DataFrame
        Bijgewerkte DataFrame met alle resultaten
    """
    file_path = f"{path}/{file_name}"

    # Run analysis to get results
    df_gem, df_kar = self.get_result_values_shansep()

    # Expected columns structure voor SHANSEP resultaten
    expected_columns = [
        'PVNAAM', 'PV_REK', 'PV_TYPE_PROEF', 'PV_ANALYSE', 'PV_RESULTAAT_ID', 'PV_TYPEVERZAMELING',
        'PV_A1_SNIJPUNT_YAS_GEM [-]', 'PV_A2_S_GEM [-]', 'PV_m_GEM [-]', 'PV_POP_GEM [kPa]',
        'PV_A1_SNIJPUNT_YAS_KAR [-]', 'PV_A2_S_KAR [-]', 'PV_m_KAR [-]', 'PV_POP_KAR [kPa]',
        'PV_S_SD_DSTAB [-]', 'PV_m_SD_DSTAB [-]', 'PV_POP_SD_DSTAB [-]',
        'PV_VGWNAT_GEM [kN/m3]', 'PV_VGWNAT_SD [kN/m3]', 'PV_WATERGEHALTE_GEM', 'PV_WATERGEHALTE_SD',
        'Timestamp'
    ]

    # Bereken standard deviaties voor DSTAB
    s_sd_dstab = None
    m_sd_dstab = None
    pop_sd_dstab = None

    if (df_gem['Schuifsterkteratio S [-]'].iloc[0] is not None and
        df_kar['Schuifsterkteratio S [-]'].iloc[0] is not None):
        s_sd_dstab = abs(df_gem['Schuifsterkteratio S [-]'].iloc[0] - df_kar['Schuifsterkteratio S [-]'].iloc[0]) / 2

    if (df_gem['sterkte toename exponent = m [-]'].iloc[1] is not None and
        df_kar['sterkte toename exponent = m [-]'].iloc[1] is not None):
        m_sd_dstab = abs(df_gem['sterkte toename exponent = m [-]'].iloc[1] - df_kar['sterkte toename exponent = m [-]'].iloc[1]) / 2

    if (df_gem['POP [kPa]'].iloc[0] is not None and
        df_kar['POP [kPa]'].iloc[0] is not None):
        pop_sd_dstab = abs(df_gem['POP [kPa]'].iloc[0] - df_kar['POP [kPa]'].iloc[0]) / 2

    # Maak nieuwe row met resultaten
    new_row = {
        'PVNAAM': self.investigation_groups[0],
        'PV_REK': self.effective_stress,
        'PV_TYPE_PROEF': self.analysis_type.split('_')[0],
        'PV_ANALYSE': '_'.join(self.analysis_type.split('_')[1:]),
        'PV_RESULTAAT_ID': f"{self.investigation_groups[0]}_{self.effective_stress}_{self.analysis_type}",
        'PV_TYPEVERZAMELING': self.alpha,
        'PV_A1_SNIJPUNT_YAS_GEM [-]': round(df_gem['snijpunt y-as [kPa]'].iloc[0], 3) if df_gem['snijpunt y-as [kPa]'].iloc[0] is not None else None,
        'PV_A2_S_GEM [-]': round(df_gem['Schuifsterkteratio S [-]'].iloc[0], 3) if df_gem['Schuifsterkteratio S [-]'].iloc[0] is not None else None,
        'PV_m_GEM [-]': round(df_gem['sterkte toename exponent = m [-]'].iloc[1], 3) if df_gem['sterkte toename exponent = m [-]'].iloc[1] is not None else None,
        'PV_POP_GEM [kPa]': round(df_gem['POP [kPa]'].iloc[0], 3) if df_gem['POP [kPa]'].iloc[0] is not None else None,
        'PV_A1_SNIJPUNT_YAS_KAR [-]': round(df_kar['snijpunt y-as [kPa]'].iloc[0], 3) if df_kar['snijpunt y-as [kPa]'].iloc[0] is not None else None,
        'PV_A2_S_KAR [-]': round(df_kar['Schuifsterkteratio S [-]'].iloc[0], 3) if df_kar['Schuifsterkteratio S [-]'].iloc[0] is not None else None,
        'PV_m_KAR [-]': round(df_kar['sterkte toename exponent = m [-]'].iloc[1], 3) if df_kar['sterkte toename exponent = m [-]'].iloc[1] is not None else None,
        'PV_POP_KAR [kPa]': round(df_kar['POP [kPa]'].iloc[0], 3) if df_kar['POP [kPa]'].iloc[0] is not None else None,
        'PV_S_SD_DSTAB [-]': round(s_sd_dstab, 3) if s_sd_dstab is not None else None,
        'PV_m_SD_DSTAB [-]': round(m_sd_dstab, 3) if m_sd_dstab is not None else None,
        'PV_POP_SD_DSTAB [-]': round(pop_sd_dstab, 3) if pop_sd_dstab is not None else None,
        'PV_VGWNAT_GEM [kN/m3]': round(self.calc_vgwnat_gem, 3) if self.calc_vgwnat_gem is not None else None,
        'PV_VGWNAT_SD [kN/m3]': round(self.calc_vgwnat_sd, 3) if self.calc_vgwnat_sd is not None else None,
        'PV_WATERGEHALTE_GEM': round(self.calc_watergehalte_gem, 3) if self.calc_watergehalte_gem is not None else None,
        'PV_WATERGEHALTE_SD': round(self.calc_watergehalte_sd, 3) if self.calc_watergehalte_sd is not None else None,
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    workbook = load_workbook(file_path)

    if 'Resultaten SHANSEP' in workbook.sheetnames:
        print('Tabblad resultaten SHANSEP in dbase excel bestaat al en wordt aangevuld')
        df_existing = read_excel(file_path, sheet_name='Resultaten SHANSEP')
        # Filter out empty rows and ensure consistent types before concatenation
        df_existing = df_existing.dropna(how='all')
        new_row_df = DataFrame([new_row], columns=df_existing.columns)
        df_updated = concat([df_existing, new_row_df], ignore_index=True)
    else:
        print('Tabblad resultaten SHANSEP in dbase excel bestaat nog niet en wordt aangemaakt')
        df_updated = DataFrame([new_row], columns=expected_columns)

    # Write data to Excel
    with ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_updated.to_excel(writer, sheet_name='Resultaten SHANSEP', index=False)

    # Formatting
    num_columns = df_updated.shape[1]
    num_rows = df_updated.shape[0]
    format_excel_sheet(
        file_path=file_path,
        sheet_name='Resultaten SHANSEP',
        num_columns=num_columns,
        num_rows=num_rows,
        table_name='ResultatenSHANSEPTable',
        index=False
    )

    return df_updated


def save_total_to_excel(self: "SHANSEP", path: str):
    """
    Exporteert alle SHANSEP analysegegevens naar Excel.

    Slaat de volledige dataset met alle berekende kolommen op in een Excel bestand.
    De bestandsnaam wordt automatisch gegenereerd op basis van de analyse-instellingen.

    Parameters
    ----------
    path : str
        Map locatie waar het Excel-bestand moet worden opgeslagen
    self : SHANSEP
        Instantie van de SHANSEP klasse
    """
    # Pas de effective stress naam aan zodat het weggeschreven kan worden in de bestandsnaam
    effective_stress = str(self.effective_stress).replace('%', 'procent_')
    effective_stress = str(effective_stress).replace(' ', '')

    # Exporteer onder de juiste naam
    file_name = f"shansep_export_{self.investigation_groups[0]}_{self.analysis_type}_{effective_stress}.xlsx"
    file_path = f"{path}/{file_name}"

    # Run analysis to ensure data is available
    self._run_shansep()

    # Get results
    df_gem, df_kar = self.get_result_values_shansep()

    # Write all data to Excel
    with ExcelWriter(file_path, engine='openpyxl') as writer:
        # Main analysis data
        if self.shansep_data_df_nc_oc is not None:
            self.shansep_data_df_nc_oc.to_excel(writer, sheet_name='Analyse Data', index=False)

        # Results
        df_gem.to_excel(writer, sheet_name='Resultaten Gemiddeld', index=True)
        df_kar.to_excel(writer, sheet_name='Resultaten Karakteristiek', index=True)

        # Su tabel if available
        if hasattr(self, 'sutabel') and self.sutabel is not None:
            self.sutabel.to_excel(writer, sheet_name='Su Tabel', index=False)

    print(f"SHANSEP Excel export voltooid: {file_path}")


def _df_to_table_with_index(df, index_name='Index'):
    """
    Zet een DataFrame om naar een lijst voor gebruik in een PDF tabel.

    Parameters
    ----------
    df : DataFrame
        De DataFrame die moet worden omgezet
    index_name : str, optioneel
        Naam voor de index kolom (default='Index')

    Returns
    -------
    list
        Lijst met header en data rijen voor een PDF tabel
    """
    header = [df.index.name or index_name] + df.columns.tolist()
    data = [[idx] + row.tolist() for idx, row in df.iterrows()]
    return [header] + data


def _create_input_table(self: "SHANSEP") -> Table:
    """
    Maakt een tabel met de invoerselectie informatie voor SHANSEP analyse.

    Returns
    -------
    Table
        ReportLab tabel object met de invoerselectie informatie
    """
    if self.shansep_data_df_nc_oc is None:
        return Table([['Geen invoerdata beschikbaar']], hAlign='LEFT')

    # Selecteer relevante kolommen
    columns_base = ['PV_NAAM', 'BORING_POSITIE', 'MONSTER_NIVEAU_NAP_VANAF', 'MONSTER_NIVEAU_NAP_TOT']

    if self.analysis_type.startswith('TXT'):
        columns_extra = ['TXT_SS_VOLUMEGEWICHT_NAT', 'TXT_SS_VOLUMEGEWICHT_DRG', 'TXT_SS_WATERGEHALTE_VOOR']
    else:
        columns_extra = ['DSS_VOLUMEGEWICHT_NAT', 'DSS_VOLUMEGEWICHT_DRG', 'DSS_WATERGEHALTE_VOOR']

    # Check welke kolommen bestaan in de dataframe
    available_columns = [col for col in columns_base + columns_extra if col in self.total_shansep_data_df.columns]

    if not available_columns:
        return Table([['Geen invoerdata kolommen beschikbaar']], hAlign='LEFT')

    table_df = self.total_shansep_data_df[available_columns].copy()

    # Hernoem kolommen voor leesbaarheiđ
    column_mapping = {
        'PV_NAAM': 'Groep',
        'BORING_POSITIE': 'Positie',
        'MONSTER_NIVEAU_NAP_VANAF': 'NAP Vanaf [m]',
        'MONSTER_NIVEAU_NAP_TOT': 'NAP Tot [m]',
        'TXT_SS_VOLUMEGEWICHT_NAT': 'VGW nat',
        'TXT_SS_VOLUMEGEWICHT_DRG': 'VGW droog',
        'TXT_SS_WATERGEHALTE_VOOR': 'Watergehalte voor',
        'DSS_VOLUMEGEWICHT_NAT': 'VGW nat',
        'DSS_VOLUMEGEWICHT_DRG': 'VGW droog',
        'DSS_WATERGEHALTE_VOOR': 'Watergehalte voor'
    }

    table_df = table_df.rename(columns={k: v for k, v in column_mapping.items() if k in table_df.columns})
    table_df = table_df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) else x)

    t1_data = _df_to_table_with_index(table_df, index_name="Monster ID")
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


def _create_parameters_table(self: "SHANSEP") -> Table:
    """
    Maakt een tabel met de SHANSEP parameters.

    Returns
    -------
    Table
        ReportLab tabel object met de SHANSEP parameters
    """
    parameters: List[list] = []

    # Voeg parameters toe
    if hasattr(self, 'e_a1_oc') and self.e_a1_oc is not None:
        parameters.append(['Snijpunt y-as gemiddeld [kPa]', round(self.e_a1_oc, 3)])
    if hasattr(self, 'e_a2_oc') and self.e_a2_oc is not None:
        parameters.append(['S gemiddeld [-]', round(self.e_a2_oc, 3)])
    if hasattr(self, 'e_a2_nc_oc') and self.e_a2_nc_oc is not None:
        parameters.append(['m gemiddeld [-]', round(self.e_a2_nc_oc, 3)])
    if hasattr(self, 'pop_gem_oc') and self.pop_gem_oc is not None:
        parameters.append(['POP gemiddeld [kPa]', round(self.pop_gem_oc, 3)])

    if hasattr(self, 'a1_kar_oc') and self.a1_kar_oc is not None:
        parameters.append(['Snijpunt y-as karakteristiek [kPa]', round(self.a1_kar_oc, 3)])
    if hasattr(self, 'a2_kar_oc') and self.a2_kar_oc is not None:
        parameters.append(['S karakteristiek [-]', round(self.a2_kar_oc, 3)])
    if hasattr(self, 'a2_kar_nc_oc') and self.a2_kar_nc_oc is not None:
        parameters.append(['m karakteristiek [-]', round(self.a2_kar_nc_oc, 3)])
    if hasattr(self, 'pop_kar_oc') and self.pop_kar_oc is not None:
        parameters.append(['POP karakteristiek [kPa]', round(self.pop_kar_oc, 3)])

    parameters.append(['Type verzameling: lokaal = 1.0; regionaal = 0.75', self.alpha])

    if hasattr(self, 'calc_vgwnat_gem') and self.calc_vgwnat_gem is not None:
        parameters.append(['VGW nat gemiddeld [kN/m3]', round(self.calc_vgwnat_gem, 3)])
    if hasattr(self, 'calc_watergehalte_gem') and self.calc_watergehalte_gem is not None:
        parameters.append(['Watergehalte gemiddeld', round(self.calc_watergehalte_gem, 3)])

    t = Table([['Parameter', 'Waarde']] + parameters, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    return t


def _create_results_table(self: "SHANSEP") -> Table:
    """
    Maakt een tabel met de SHANSEP resultaten.

    Returns
    -------
    Table
        ReportLab tabel object met de SHANSEP resultaten
    """
    df_gem, df_kar = self.get_result_values_shansep()

    # Combineer gemiddelde en karakteristieke resultaten
    combined_df = DataFrame({
        'Analyse methode': df_gem.index,
        'Snijpunt y-as gem [kPa]': df_gem['snijpunt y-as [kPa]'].values,
        'S gemiddeld [-]': df_gem['Schuifsterkteratio S [-]'].values,
        'm gemiddeld [-]': df_gem['sterkte toename exponent = m [-]'].values,
        'POP gemiddeld [kPa]': df_gem['POP [kPa]'].values,
        'Snijpunt y-as kar [kPa]': df_kar['snijpunt y-as [kPa]'].values,
        'S karakteristiek [-]': df_kar['Schuifsterkteratio S [-]'].values,
        'm karakteristiek [-]': df_kar['sterkte toename exponent = m [-]'].values,
        'POP karakteristiek [kPa]': df_kar['POP [kPa]'].values,
    })

    # Format numeric values
    for col in combined_df.columns:
        if col != 'Analyse methode':
            combined_df[col] = combined_df[col].apply(
                lambda x: f"{x:.3f}" if isinstance(x, (float, int)) and x is not None else "[-]"
            )

    t_data = _df_to_table_with_index(combined_df, index_name="Resultaat type")
    t = LongTable(t_data, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    return t


def save_to_pdf(self: "SHANSEP", path: str) -> str:
    """
    Slaat de SHANSEP analyseresultaten op in een PDF-document.

    De PDF bevat:
    - Titel met analysedetails
    - Beide overzichtsfiguren van de analyse (sv-su en ln(OCR)-ln(su/svc))
    - Su tabel
    - Tabel met gemiddelde en karakteristieke resultaten
    - Tabel met invoerselectie informatie

    Parameters
    ----------
    path : str
        Map locatie waar het PDF-bestand moet worden opgeslagen

    Returns
    -------
    str
        Het absolute bestandspad van het aangemaakte PDF-bestand
    """
    # Maak titel en bestandsnaam
    title = f"SHANSEP {self.analysis_type} analyse met {self.effective_stress} op {self.investigation_groups[0]}"
    file_name = f"shansep_pdf_export_{self.investigation_groups[0]}_{self.analysis_type}_{str(self.effective_stress).replace('%', 'procent_').replace(' ', '')}.pdf"
    file_path = f"{path}/{file_name}"

    # Ensure analysis is run
    self._run_shansep()

    # Generate figures if not already done
    if not hasattr(self, 'figure') or len(self.figure.data) == 0:
        self.show_title = False
        # We would need to implement show_figure methods similar to c_phi analysis
        # For now, we'll skip the figure generation and add a placeholder

    # Maak het PDF document
    doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Left', parent=styles['Normal'], alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='TitleLeft', parent=styles['Title'], alignment=TA_LEFT))
    story = []

    # Voeg titel toe
    story.append(Paragraph(title, styles['TitleLeft']))
    story.append(Spacer(width=1, height=12))

    # TODO: Add figure export when visualization functions are ready
    # For now, add placeholder text
    story.append(Paragraph("Figuren: (implementatie volgt wanneer visualisatie functies beschikbaar zijn)", styles['Heading2']))
    story.append(Spacer(width=1, height=12))

    # Voeg parameters toe
    story.append(Paragraph("SHANSEP Parameters", styles['Heading2']))
    story.append(_create_parameters_table(self))
    story.append(Spacer(1, 12))

    # Voeg resultaten toe
    story.append(Paragraph("SHANSEP Resultaten", styles['Heading2']))
    story.append(_create_results_table(self))
    story.append(Spacer(1, 12))

    # Voeg Su tabel toe indien beschikbaar
    if hasattr(self, 'sutabel') and self.sutabel is not None:
        story.append(Paragraph("Su Tabel", styles['Heading2']))
        sutabel_data = _df_to_table_with_index(self.sutabel, index_name="Index")
        sutabel_table = LongTable(sutabel_data, repeatRows=1, hAlign='LEFT')
        sutabel_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        story.append(sutabel_table)
        story.append(Spacer(1, 12))

    # Voeg invoerselectie toe
    story.append(Paragraph("Invoerselectie Informatie", styles['Heading2']))
    story.append(_create_input_table(self))

    # Maak PDF
    doc.build(story)
    print(f"SHANSEP PDF export voltooid: {file_path}")

    return file_path
