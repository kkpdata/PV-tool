![Coverage](./readme_images/coverage.svg)

# STOWA Proevenverzameling tool v5.0

De PV-tool (Proevenverzameling tool) is een Python-gebaseerde tooling voor het opstellen van lokale of regionale proevenverzamelingen voor het bepalen van geotechnische parameters. De methode is ontwikkeld voor het uitvoeren van analyses in relatie tot de geotechnische stabiliteit van dijken, maar kan ook breder worden toegepast.

Met de PV-tool kunnen zowel **gedraineerde** als **ongedraineerde** sterkteparameters worden berekend alsmede enkele 
**samendrukkingsparameters**. Van deze parameters worden verwachtingswaarde, karakteristieke waarde en rekenwaarde 
bepaald.

De functies zijn opgesteld conform de werkwijze beschreven in *Statistische methoden t.b.v. proevenverzamelingen, 
DIV, v1.0*. 

Zie tevens: https://publicwiki.deltares.nl/spaces/HWBPMacro/pages/217120830/Sterkte+van+grond#Sterktevangrond-150

De tool bevat tevens hulpmiddelen voor het onderscheiden of samenvoegen van groepen in een verzameling op basis van 
verschillende kenmerken.

De onderliggende data om een proevenverzameling samen te stellen is beschreven in een vaste structuur. Deze structuur 
is vastgelegd in een uitwisselformat. Het **uitwisselformat-database-proevenverzameling_versie_4_2x.xlsx**. 

De geotechnische laboratoria zijn bekend met deze database en kunnen deze database vullen met resultaten van 
grond- en laboratoriumonderzoek. Op deze wijze ontstaat er uniformering op het gebied van data-uitwisseling en –opslag 
van proefresultaten.

## Inhoudsopgave
[Installatie](#installatie)<br>
[Functionaliteiten??](#functionaliteiten)<br>
[Gebruik](#gebruik)<br>
[Referenties](#referenties)<br>

## Installatie
Indien je de tool niet via Jupiter Notebook wil gebruiken, dien je volgende stappen te volgen voor de installatie 
van de tool.

1. Clone the repository

```bash
git clone https://github.com/PVorganization/PV-tool.git
```

2. Install requirements for package management

```bash
pip install -r requirements.txt
```

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

## Gebruik
In Jupyter Notebook is een werkomgeving ontwikkeld, waardoor het mogelijk is om de PV-tool te gebruiken zonder kennis 
van Python. 

De Notebook is te vinden onder:

```bash
jupyter notebook PV_tool0.4.ipynb
```

Daarnaast is het ook mogelijk om de tool direct te gebruiken met de ontwikkelde python code. Hieronder worden in 
verschillende stappen het gebruik van de code beschreven.

### Stap 1: Importeren en valideren van benodigde data

Voor de import kunnen verschillende bronbestanden gebruikt worden: 
1. proevenverzamelingstool (versie 4.2n of hoger)
2. uitwisselformat-database-proevenverzameling_versie_4_2x.xlsx
3. proevenverzamelingstool 5.0 (product van de huidige PV-tool)

De proevenverzamelingstool of het uitwisselformat worden omgezet naar het template proevenverzamelingstool 5.0, deze 
bestaat uit de data conform het uitwisselformat 4.2 aangevuld met de benodigde in en uitvoerdata van voorliggende 
tooling.

De validatie bestaat uit:
- Controle op volledigheid en correctheid van ingevulde velden
- Onderscheid tussen 'critical errors' en 'warnings'
- Export van validatieresultaten naar Excel-bestanden
- Automatische conversie naar Template_PVtool5_0.xlsx (is dit niet hetzelfde als vorig punt?)

```python
from pv_tool.imports.import_data import Dbase

dbase = Dbase()
dbase.import_data(source="Dbase", source_dir="pad/naar/bestand.xlsx")
dbase.validate_data(export_path="pad/naar/export-bestand.xlsx")
```

## import_dbase_short?

### Stap 2: Analyse van gedraineerde parameters
- C-phi Analyse (cohesie en hoek van inwendige wrijving):
  - Analyse van triaxiaalproeven (TXT)
  - Analyse van Direct Simple Shear proeven (DSS)
  - Keuze van rekpercentages: 2%, 5%, 10%, 15%, 20%, eindsterkte of pieksterkte
  - Bepaling van verwachtingswaarde, karakteristieke waarde, en rekenwaarde
  - Visualisatie van spanningspaden en Mohr-cirkels
  - Export naar PDF en Excel


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
