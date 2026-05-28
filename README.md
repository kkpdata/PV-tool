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
[Gebruik](#gebruik)<br>
[Functionaliteiten](#functionaliteiten)<br>
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

## Gebruik
In Jupyter Notebook is een werkomgeving ontwikkeld, waardoor het mogelijk is om de PV-tool te gebruiken zonder kennis 
van Python. 

De Notebook is te vinden onder:

```bash
jupyter notebook PV_tool1.0.ipynb
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

```python
from pv_tool_logic.imports.import_data import Dbase

dbase = Dbase()
dbase.import_data(source="Dbase", source_dir="pad/naar/bestand.xlsx")
dbase.validate_data(export_path="pad/naar/export-bestand.xlsx")

dbase.export_dbase_to_template(export_dir="pad/naar/exportlocatie")
```

### Stap 2: Analyse van geotechnische parameters
In deze stap worden op basis van de opgegeven data gedraineerde parameters bepaald. De analyse vindt plaats op de 
opgegeven verzameling(en) (investigation_groups). Voor de analyse wordt een rekpercentage (effective_stress) gehanteerd. Voor de analyse op de TXT-proeven is er keuze 
tussen een analyse bij 2%, 5%, 15%, pieksterkte en eindsterkte. Voor de DSS-analyse is keuze tussen 2%, 5%, 10%, 15%, 
20%, eindsterkte of pieksterkte.

#### Stap 2.1: Analyse van gedraineerde parameters (C-phi)
De C-phi analyse bepaalt cohesie en hoek van inwendige wrijving uit triaxiaal- of DSS-proeven.

```python
from pv_tool.cphi_analysis.c_phi_analysis import CPhiAnalyse

# Stel de onderzoeksgroep(en) in (PV_NAAM)
investigation_groups = ['TXT_SAFE_klei_licht_16_175']

# Kies de spanningstoestand (PV_REK)
effective_stress = '15% rek'  # Mogelijke keuzes: '2% rek', '5% rek', '10% rek', '15% rek', '20% rek', 'pieksterkte', 'eindsterkte'

# Kies het analysetype
analysis_type = 'TXT_CPhi'  # Mogelijke keuzes: 'TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH'

# Initialiseer de analyse
analyse = CPhiAnalyse(
    dbase=dbase,
    investigation_groups=investigation_groups,
    effective_stress=effective_stress,
    analysis_type=analysis_type
)

# Pas de alpha-waarde aan (bijvoorbeeld 0.75 voor regionale kering en 1.0 voor primaire kering)
analyse.apply_settings(alpha=0.75)

# Pas de parameters aan om een betere fit te vinden (optioneel)
analyse.apply_parameters(cohesie_gem=8.0, phi_kar=0.53, cohesie_kar=6.72)

# Toon resultaten en exporteer
analyse.print_short_results()
analyse.show_figure()
analyse.save_to_pdf(path='path/to/export_location')
```

#### Stap 2.2: Analyse van ongedraineerde parameters (SHANSEP)
De SHANSEP analyse bepaalt ongedraineerde schuifsterkteparameters op basis van de consolidatiegeschiedenis.
In deze stap worden op basis van de opgegeven data ongedraineerde parameters bepaald volgens de methode vastgelegd in 
de schematiseringshandleiding macrostabiliteit. De analyse vindt plaats op de 
opgegeven verzameling(en) (investigation_groups).

Voor de analyse wordt een rekpercentage (effective_stress) gehanteerd. Voor de analyse op de TXT-proeven is er keuze 
tussen een analyse bij 2%, 5%, 15%, pieksterkte en eindsterkte. Voor de DSS-analyse is keuze tussen 2%, 5%, 10%, 15%, 
20%, eindsterkte of pieksterkte.

```python
from pv_tool.shansep_analysis.shansep_analysis import SHANSEP

# Stel de onderzoeksgroep(en) in
investigation_groups = ['TXT_SAFE_klei_licht_16_175']

# Kies de spanningstoestand en analysetype
effective_stress = '15% rek'
analysis_type = 'TXT_S_POP'  # Mogelijke keuzes: 'TXT_S_POP', 'DSS_S_POP'

# Initialiseer de analyse
analyse = SHANSEP(
    dbase=dbase,
    investigation_groups=investigation_groups,
    effective_stress=effective_stress,
    analysis_type=analysis_type
)

# Pas instellingen toe
analyse.apply_settings(alpha=0.75)

# Haal geschatte parameters op en stel deze in
estimated_params = analyse.get_estimated_parameters()
if estimated_params:
    analyse.set_parameters_handmatig(
        snijpunt_gem=estimated_params['snijpunt_gem'],
        s_gem=estimated_params['s_gem'],
        m_gem=estimated_params['m_gem'],
        snijpunt_kar=estimated_params['snijpunt_kar'],
        s_kar=estimated_params['s_kar'],
        m_kar=estimated_params['m_kar']
    )

# Bereken sutabel en toon resultaten
analyse.calculate_sutabel()
analyse.show_figure_sv_su()
analyse.save_to_pdf(path='path/to/export_location')
```

#### Stap 2.3: Su-tabel analyse
De Su-tabel analyse stelt tabellen op voor ongedraineerde schuifsterkte als functie van de diepte.

```python
from pv_tool.sutabel_analysis.sutabel_analysis import SUTABEL

# Stel de onderzoeksgroep(en) in
investigation_groups = ['TXT_SAFE_klei_licht_16_175']

# Kies de spanningstoestand en analysetype
effective_stress = '15% rek'
analysis_type = 'TXT_su_tabel'  # Mogelijke keuzes: 'TXT_su_tabel', 'DSS_su_tabel'

# Initialiseer de analyse
analyse = SUTABEL(
    dbase=dbase,
    investigation_groups=investigation_groups,
    effective_stress=effective_stress,
    analysis_type=analysis_type
)

# Pas instellingen toe
analyse.apply_settings(alpha=0.75)

# Pas handmatige parameters toe (optioneel)
analyse.set_manual_parameters(a1_kar=0.489, a2_kar=0.683, vc_fit_kar=0.1)

# Toon resultaten en exporteer
analyse.show_figure_sv_su_sutabel()
analyse.save_to_pdf(path='path/to/export_location')
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

### 2. Geotechnische Parameter Analyses

#### 2.1 Gedraineerde Parameters (C-phi Analyse)
- **Cohesie en hoek van inwendige wrijving:**
  - Analyse van triaxiaalproeven (TXT)
  - Analyse van Direct Simple Shear proeven (DSS)
  - Keuze van rekpercentages: 2%, 5%, 10%, 15%, 20%, eindsterkte of pieksterkte
  - Bepaling van verwachtingswaarde, karakteristieke waarde, en rekenwaarde
  - Visualisatie van spanningspaden en Mohr-cirkels
  - Export naar PDF en Excel

#### 2.2 Ongedraineerde Parameters (SHANSEP Analyse)
- **SHANSEP methode voor ongedraineerde schuifsterkte:**
  - Bepaling van S en m parameters uit consolidatiegeschiedenis
  - Analyse van NC (normally consolidated) en OC (overconsolidated) proeven
  - Automatische parameter schatting en handmatige aanpassing mogelijk
  - Sutabel berekening voor verschillende dieptes
  - Visualisatie van σ'v-su relaties
  - Export naar PDF en Excel

#### 2.3 Su-tabel Analyse
- **Sutabel-m methode voor ongedraineerde schuifsterkte tabellen:**
  - Opstellen van su-tabellen als functie van diepte
  - Bepaling van gemiddelde en karakteristieke waarden
  - Handmatige parameter aanpassing (a1_kar, a2_kar, vc_fit_kar)
  - Visualisatie van ln(σ'v) vs ln(su) en σ'v vs su grafieken
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

#### Voor ongedraineerde parameters (SHANSEP):
1. Kies verzameling voor analyse
2. Selecteer type proef (TXT_S_POP of DSS_S_POP)
3. Kies rekpercentage
4. Haal geschatte parameters op en stel deze in
5. Bereken sutabel met ingestelde parameters
6. Controleer σ'v-su grafieken
7. Exporteer naar PDF en Excel

#### Voor su-tabellen (SUTABEL):
1. Kies verzameling voor analyse
2. Selecteer type proef (TXT_su_tabel of DSS_su_tabel)
3. Kies rekpercentage
4. Stel handmatige parameters in (optioneel)
5. Bekijk ln(σ'v) vs ln(su) en σ'v vs su grafieken
6. Controleer su-tabel resultaten
7. Exporteer naar PDF en Excel



## Output

De tool genereert verschillende output-bestanden:
- **Excel-bestanden:**
  - `Template_PVtool5_0.xlsx` - Gevalideerde dataset met analysekolommen
  - `Validation_log_##_critical_errors.xlsx` - Kritieke fouten
  - `Validation_log_##_warnings.xlsx` - Waarschuwingen

- **PDF-bestanden:**
  - `[type_analyse]_export_[verzameling]_[type]_[rek].pdf` - Grafische rapportage

- **HTML-bestanden:**
  - Interactieve Plotly visualisaties van spanningspaden

## Referenties

- STOWA Proevenverzameling methodiek
- Deltares wiki: https://publicwiki.deltares.nl/spaces/HWBPMacro/pages/217120830/Sterkte+van+grond
- GitHub repository: https://github.com/kkpdata/Proevenverzamelingentool/
