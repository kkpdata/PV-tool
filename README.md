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
[Functionaliteiten??](#functionaliteiten)<br>
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

```python
from pv_tool.imports.import_data import Dbase

dbase = Dbase()
dbase.import_data(source="Dbase", source_dir="pad/naar/bestand.xlsx")
dbase.validate_data(export_path="pad/naar/export-bestand.xlsx")

dbase.export_dbase_to_template(export_dir="pad/naar/exportlocatie")
```

### Stap 2: Analyse van gedraineerde parameters
In deze stap worden op basis van de opgegeven data gedraineerde parameters bepaald. De analyse vindt plaats op de 
opgegeven verzameling(en) (investigation_groups).

Voor de analyse wordt een rekpercentage (effective_stress) gehanteerd. Voor de analyse op de TXT-proeven is er keuze 
tussen een analyse bij 2%, 5%, 15%, pieksterkte en eindsterkte. Voor de DSS-analyse is keuze tussen 2%, 5%, 10%, 15%, 
20%, eindsterkte of pieksterkte.

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

# Pas de parameters aan om een betere fit te vinden
analyse.apply_parameters(cohesie_gem=8.0, phi_kar=0.53, cohesie_kar=6.72)

# print results???
analyse.print_short_results()

# Exporteer de resultaten van de c-phi analyse naar het template en pdf
export_dir = 'path/to/export_location'
analyse.add_results_to_template(path=export_dir)
analyse.save_to_pdf(path=export_dir)

# Plot de figuur van de c-phi analyse
analyse.show_figure()
```

### Stap 3: Analyse van ongedraineerde parameters (SHANSEP)
In deze stap worden op basis van de opgegeven data ongedraineerde parameters bepaald volgens de methode vastgelegd in 
de schematiseringshandleiding macrostabiliteit. De analyse vindt plaats op de 
opgegeven verzameling(en) (investigation_groups).

Voor de analyse wordt een rekpercentage (effective_stress) gehanteerd. Voor de analyse op de TXT-proeven is er keuze 
tussen een analyse bij 2%, 5%, 15%, pieksterkte en eindsterkte. Voor de DSS-analyse is keuze tussen 2%, 5%, 10%, 15%, 
20%, eindsterkte of pieksterkte.

```python
from pv_tool.shansep_analysis.shansep_analysis import SHANSEP

# Stel de onderzoeksgroep(en) in (PV_NAAM)
investigation_groups = ['TXT_SAFE_klei_licht_16_175']

# Kies de spanningstoestand (PV_REK)
effective_stress = '15% rek'  # Mogelijke keuzes: '2% rek', '5% rek', '10% rek', '15% rek', '20% rek', 'pieksterkte', 'eindsterkte'

# Kies het analysetype
analysis_type = 'TXT_S_POP'  # Mogelijke keuzes: 'TXT_CPhi', 'TXT_SH', 'DSS_CPhi', 'DSS_SH'

# Initialiseer de analyse
analyse = SHANSEP(
    dbase=dbase,
    investigation_groups=investigation_groups,
    effective_stress=effective_stress,
    analysis_type=analysis_type
)

# Pas de alpha-waarde aan (bijvoorbeeld 0.75 voor regionale kering en 1.0 voor primaire kering)
analyse.apply_settings(alpha=0.75)

# Pas de parameters aan om een betere fit te vinden
analyse.set_parameters_handmatig(
                    snijpunt_gem=0.25, s_gem=0.8, m_gem=0.9,
                    snijpunt_kar=0.20, s_kar=0.7, m_kar=0.8

# get results
analyse.get_short_results()

# Exporteer de resultaten van de c-phi analyse naar het template en pdf
export_dir = 'path/to/export_location'
analyse.add_results_to_template(path=export_dir)
analyse.save_to_pdf(path=export_dir)

# Plot de figuur van de c-phi analyse
analyse.show_figure_sv_su()
```

### Stap 4: Analyse van ongedraineere parameters (SU-tabel)
...









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
