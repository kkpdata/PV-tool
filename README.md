# STOWA Proevenverzameling tool v5.0

De PV-tool (Proevenverzameling tool) is een Python-gebaseerde tooling voor het opstellen van lokale of regionale proevenverzamelingen voor het bepalen van geotechnische parameters. De methode is ontwikkeld voor het uitvoeren van analyses in relatie tot de geotechnische stabiliteit van dijken, maar kan ook breder worden toegepast.

## Overzicht

Met de PV-tool kunnen zowel **gedraineerde** als **ongedraineerde** sterkteparameters worden berekend alsmede enkele **samendrukkingsparameters**. Van deze parameters worden verwachtingswaarde, karakteristieke waarde en rekenwaarde bepaald.

De functies zijn opgesteld conform de werkwijze beschreven in *Statistische methoden t.b.v. proevenverzamelingen, DIV, v1.0*. Zie tevens: https://publicwiki.deltares.nl/spaces/HWBPMacro/pages/217120830/Sterkte+van+grond#Sterktevangrond-150

De tool bevat tevens hulpmiddelen voor het onderscheiden of samenvoegen van groepen in een verzameling op basis van verschillende kenmerken.

## Functionaliteiten

### 1. Data-import en Validatie
- **Ondersteunde formaten:**
  - Excel versie van de proevenverzamelingtool (vanaf versie 4.2n of hoger)
  - Excel Uitwisselformat-database-proevenverzameling versie 4.2x
  - Template Proevenverzamelingtool 5.0

- **Validatie:**
  - Controle op volledigheid en correctheid van ingevulde velden
  - Onderscheid tussen 'critical errors' en 'warnings'
  - Export van validatieresultaten naar Excel-bestanden
  - Automatische conversie naar Template_PVtool5_0.xlsx

### 2. Analyse van Gedraineerde Parameters
- **C-phi Analyse (Cohesie en hoek van inwendige wrijving):**
  - Analyse van triaxiaalproeven (TXT)
  - Analyse van Direct Simple Shear proeven (DSS)
  - Keuze van rekpercentages: 2%, 5%, 10%, 15%, 20%, eindsterkte of pieksterkte
  - Bepaling van verwachtingswaarde, karakteristieke waarde en rekenwaarde
  - Visualisatie van spanningspaden en Mohr-cirkels
  - Export naar PDF en Excel

### 3. Analyse van Ongedraineerde Parameters
- **SHANSEP Analyse:** Voor het bepalen van ongedraineerde schuifsterkte parameters
- **Su-tabel Analyse:** Voor het opstellen van su-tabellen

### 4. Analysekolommen
De tool voegt automatisch analysekolommen (ANA) toe die benodigd zijn voor de analyses:
- `ANA_TERREINSPANNING`
- `ANA_TXT_MAX_VERTICALE_CONSOLIDATIE_SPANNING`
- `ANA_DSS_MAX_CONSOLIDATIE_SPANNING`
- `ANA_TXT_CONSOLIDATIE_TYPE_VOORSTEL / HANDMATIG / REKEN`
- `ANA_DSS_CONSOLIDATIE_TYPE_VOORSTEL / HANDMATIG / REKEN`
- `ANA_GRENSSPANNING_VOORSTEL / HANDMATIG / REKEN`
- `ANA_POP_VELD / POP_VELD_GEMIDDELD`
- `OCR_TXT / OCR_DSS`

Deze kolommen helpen bij het classificeren van proeven als normaal geconsolideerd (NC) of overgeconsolideerd (OC).

## Installatie

### Vereisten
```bash
pip install -r requirements.txt
```

### Benodigde packages
- pandas
- openpyxl
- ipyfilechooser
- pandas_schema
- xlsxwriter
- ipywidgets
- reportlab
- kaleido
- plotly
- numpy
- scipy
- ipywidgets
- ipyfilechooser
- ipython

### Installatie van de PV-tool package
```bash
pip install -e .
```

## Gebruik

### Via Jupyter Notebook (aanbevolen)
De tool is primair ontworpen voor gebruik via Jupyter Notebook voor een interactieve workflow:

```bash
jupyter notebook PV_tool0.4.ipynb
```

### Via Python script
```python
from pv_tool.imports.import_data import Dbase
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse

# Importeren van data
dbase = Dbase()
dbase.import_data(source="Dbase", source_dir="pad/naar/bestand.xlsx")

# C-phi analyse uitvoeren
analyse = CPhiAnalyse(
    dbase=dbase,
    investigation_groups=['verzameling_naam'],
    effective_stress='eindsterkte',
    analysis_type='TXT_CPhi'
)
analyse._run()
analyse.show_figure()
```

## Workflow

### Stap 1: Data Importeren
1. Kies het juiste template-formaat
2. Selecteer het Excel-bestand
3. Voer validatie uit
4. Controleer validatieresultaten

### Stap 2: Analysekolommen Controleren
1. Controleer voorgestelde consolidatietypen (NC/OC)
2. Controleer grensspanningen
3. Pas indien nodig handmatig aan

### Stap 3: Proevenverzamelingen Definiëren
1. Onderscheid verzamelingen op basis van:
   - Grondsoort
   - Diepte
   - Locatie
   - Andere kenmerken
2. Wijs verzamelingsnamen toe in kolom `PV_NAAM`

### Stap 4: Parameters Bepalen
#### Voor gedraineerde parameters (C-phi):
1. Kies verzameling voor analyse
2. Selecteer type proef (TXT of DSS)
3. Kies rekpercentage
4. Bekijk automatisch berekende raaklijnen
5. Pas raaklijnen indien nodig handmatig aan
6. Controleer resultaten in grafiek en tabel
7. Exporteer naar PDF en Excel

#### Voor ongedraineerde parameters (SHANSEP/Su-tabel):
Zie specifieke modules in de notebook

## Uitwisselformat

De onderliggende data voor het samenstellen van een proevenverzameling is beschreven in een vaste structuur vastgelegd in het **Uitwisselformat-database-proevenverzameling versie 4.2x**. Geotechnische laboratoria kennen deze database en kunnen deze vullen met resultaten van grond- en laboratoriumonderzoek.

Dit zorgt voor uniformering op het gebied van:
- Data-uitwisseling
- Opslag van proefresultaten
- Reproduceerbaarheid van analyses

## Project Structuur

```
pv_tool/
├── cphi_analysis/         # C-phi analyse functionaliteit
│   ├── c_phi_analysis.py  # Hoofdmodule voor C-phi berekeningen
│   ├── calc_parameters.py # Parameterberekeningen
│   ├── visualization.py   # Visualisaties en grafieken
│   └── save_and_export.py # Export functionaliteit
├── imports/               # Data import en validatie
│   ├── import_data.py     # Hoofdmodule voor import
│   ├── create_dbase.py    # Database creatie
│   └── add_ana_columns.py # Toevoegen analysekolommen
├── shansep_analysis/      # SHANSEP analyse
└── sutabel_analysis/      # Su-tabel analyse
```

## Output

De tool genereert verschillende output-bestanden:
- **Excel-bestanden:**
  - `Template_PVtool5_0.xlsx` - Gevalideerde dataset met analysekolommen
  - `Validation_log_##_critical_errors.xlsx` - Kritieke fouten
  - `Validation_log_##_warnings.xlsx` - Waarschuwingen
  - `c_phi_data_geforceerd.xlsx` - Tussenresultaten C-phi analyse

- **PDF-bestanden:**
  - `c_phi_pdf_export_[verzameling]_[type]_[rek].pdf` - Grafische rapportage

- **HTML-bestanden:**
  - Interactieve Plotly visualisaties van spanningspaden

## Referenties

- STOWA Proevenverzameling methodiek
- Deltares wiki: https://publicwiki.deltares.nl/spaces/HWBPMacro/pages/217120830/Sterkte+van+grond
- GitHub repository: https://github.com/kkpdata/Proevenverzamelingentool/

## Licentie

Zie LICENSE bestand voor details.

## Contact en Ondersteuning

Voor vragen, suggesties of problemen kunt u een issue aanmaken in de GitHub repository.
