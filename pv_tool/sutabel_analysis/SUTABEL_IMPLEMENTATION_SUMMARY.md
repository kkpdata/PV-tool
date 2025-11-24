# SHANSEP Sutabel-m Methode Implementatie

## Overzicht
De sutabel-m methode is succesvol geïmplementeerd in de SHANSEP klasse. Deze methode is gescheiden van de bestaande su tabel code en werkt parallel aan de S-POP analyse methode.

## Wat is geïmplementeerd

### 1. Variables (pv_tool/shansep_analysis/variables.py)

Een nieuwe sectie "sutabel-m methode" is toegevoegd met de volgende variabelen:

#### Basis statistieken:
- `count_ln_sv_sutabel()` - Telt het aantal ln(s'v) waarden
- `sum_ln_sv_sutabel()` - Som van ln(s'v) waarden
- `sum_ln_su_sutabel()` - Som van ln(su) waarden
- `sum_sv_tt_sutabel()` - Som van s_tt waarden (voor regressie)
- `sum_sv_ty_sutabel()` - Som van s_ty waarden (voor regressie)

#### Regressie parameters:
- `e_a2_sutabel()` - Helling (a2) van lineaire regressie
- `e_a1_sutabel()` - Snijpunt (a1) van lineaire regressie
- `sum_chi_2_sutabel()` - Som van chi-kwadraat waarden

#### Variantie en standaarddeviatie:
- `var_a2_sutabel()` - Variantie van a2
- `var_a1_sutabel()` - Variantie van a1
- `cov_a1_a2_sutabel()` - Covariantie tussen a1 en a2
- `rho_a1_a2_sutabel()` - Correlatie tussen a1 en a2
- `sigma_a2_sutabel()` - Standaarddeviatie van a2
- `sigma_a1_sutabel()` - Standaarddeviatie van a1
- `t_n_2_sutabel()` - t-waarde voor betrouwbaarheidsintervallen

#### Effectieve spanning en grenzen:
- `sum_s_eff_sutabel()` - Som van effectieve spanning waarden
- `count_s_eff_sutabel()` - Aantal effectieve spanning waarden
- `sum_5_pr_ondergrens_sutabel()` - Som van 5% ondergrens
- `sum_stt_ondergrens_sutabel()` - Som van s_tt ondergrens
- `sum_sty_ondergrens_sutabel()` - Som van s_ty ondergrens

#### Karakteristieke waarden:
- `a2_kar_sutabel()` - Karakteristieke helling
- `a1_kar_sutabel()` - Karakteristiek snijpunt

#### Extra parameter:
- `steyx_sutabel()` - STEYX (standaardfout van de schatting) voor ln(s'v) en ln(su) data

### 2. Expand Analysis (pv_tool/shansep_analysis/expand_analysis.py)

Nieuwe berekeningsfuncties toegevoegd voor sutabel analyse:

#### Basis transformaties:
- `calculate_ln_sv_sutabel()` - Berekent ln(s'v) kolom
- `calculate_ln_su_sutabel()` - Berekent ln(su) kolom

#### Regressie berekeningen:
- `calculate_sv_tt_sutabel()` - Berekent s_tt voor lineaire regressie
- `calculate_sv_ty_sutabel()` - Berekent s_ty voor lineaire regressie
- `calculate_chi_2_sutabel()` - Berekent chi-kwadraat waarden

#### Effectieve spanning:
- `s_min_sutabel()` - Minimum ln(s'v) waarde
- `s_max_sutabel()` - Maximum ln(s'v) waarde
- `calculate_sv_eff_sutabel()` - Berekent s' waarden met gelijke intervallen

#### Betrouwbaarheidsgrenzen:
- `calculate_5pr_ondergrens_sutabel()` - Berekent 5% ondergrens
- `calculate_5pr_bovengrens_sutabel()` - Berekent 5% bovengrens

#### Ondergrens berekeningen:
- `calculate_sv_tt_ondergrens_sutabel()` - s_tt voor ondergrens
- `calculate_sv_ty_ondergrens_sutabel()` - s_ty voor ondergrens
- `calculate_chi_2_ondergrens_sutabel()` - chi-kwadraat voor ondergrens

### 3. SHANSEP Class (pv_tool/shansep_analysis/shansep_analysis.py)

#### Nieuwe attributen in __init__:
```python
# Sutabel parameters
self.e_a2_sutabel: Optional[float] = None
self.e_a1_sutabel: Optional[float] = None
self.a2_kar_sutabel: Optional[float] = None
self.a1_kar_sutabel: Optional[float] = None
self.steyx_sutabel: Optional[float] = None

# Dataframe
self.shansep_data_df_sutabel: Optional[DataFrame] = None
```

#### Geïmplementeerde methode:
```python
def expand_analysis_df_sutabel(self):
    """
    Berekent alle benodigde parameters per monster voor de sutabel-m analyse.
    Filtert op OC proeven en creëert kolommen voor ln(s'v) en ln(su).
    """
```

Deze methode:
1. Filtert `self.shansep_data_df` op alleen OC (overgeconsolideerde) proeven
2. Creëert `self.shansep_data_df_sutabel` dataframe
3. Berekent `ln(s'v)` en `ln(su)` kolommen
4. Voert lineaire regressie analyse uit
5. Berekent alle afgeleide waarden en betrouwbaarheidsgrenzen

#### Aangepaste methoden:
- `get_shansep_parameters()` - Nu met conditie voor sutabel vs S-POP analyse
- `write_analysis_to_excel()` - Bevat nu sutabel dataframe
- `_run_shansep()` - Roept `expand_analysis_df_sutabel()` aan voor TXT_su_tabel en DSS_su_tabel

## Gebruik

### Initialisatie voor sutabel analyse:
```python
from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
from pv_tool.imports.import_data import Dbase

# Laad de database
dbase = Dbase('pad/naar/database.xlsx')

# Maak SHANSEP instantie met sutabel analyse type
shansep = SHANSEP(
    dbase=dbase,
    analysis_type='TXT_su_tabel',  # of 'DSS_su_tabel'
    investigation_groups=['PV_NAAM_1'],
    effective_stress='15% rek'
)

# Voer analyse uit
shansep._run_shansep()

# Check resultaten
print(f"e_a2_sutabel: {shansep.e_a2_sutabel}")
print(f"e_a1_sutabel: {shansep.e_a1_sutabel}")
print(f"STEYX: {shansep.steyx_sutabel}")

# Bekijk sutabel dataframe
print(shansep.shansep_data_df_sutabel.head())
```

### Kolommen in shansep_data_df_sutabel:
De sutabel dataframe bevat alle oorspronkelijke kolommen plus:
- `ln(s'v)` - Natuurlijk logaritme van verticale effectieve spanning
- `ln(su)` - Natuurlijk logaritme van ongedraineerde schuifsterkte
- `s_tt` - Component voor lineaire regressie
- `s_ty` - Component voor lineaire regressie
- `chi_2` - Chi-kwadraat waarde
- `s'` - Effectieve spanning waarden
- `5_pr_ondergrens` - 5% ondergrens
- `5_pr_bovengrens` - 5% bovengrens
- `s_tt_ondergrens` - s_tt voor ondergrens
- `s_ty_ondergrens` - s_ty voor ondergrens
- `chi_2_ondergrens` - chi-kwadraat voor ondergrens

## Belangrijke verschillen met S-POP methode

| Aspect | S-POP Methode | Sutabel-m Methode |
|--------|---------------|-------------------|
| Data | NC en OC proeven | Alleen OC proeven |
| X-as | LN(OCR) | ln(s'v) |
| Y-as | LN(su/svc) | ln(su) |
| Parameters | e_a1_oc, e_a2_oc, e_a1_nc_oc, e_a2_nc_oc, POP | e_a1_sutabel, e_a2_sutabel, STEYX |
| Dataframe | shansep_data_df_oc, shansep_data_df_nc_oc | shansep_data_df_sutabel |

## Validatie

De implementatie is getest en alle componenten zijn correct geïmporteerd:
- ✓ Alle 23 sutabel variabelen
- ✓ Alle 11 sutabel berekeningsfuncties
- ✓ SHANSEP class updates
- ✓ Correcte imports in shansep_analysis.py

## Volgende stappen

1. Test met echte data door een SHANSEP instantie te maken met `analysis_type='TXT_su_tabel'` of `'DSS_su_tabel'`
2. Verifieer dat alle kolommen correct worden berekend
3. Controleer de parameters: `e_a2_sutabel`, `e_a1_sutabel`, `a2_kar_sutabel`, `a1_kar_sutabel`, `steyx_sutabel`
4. Optioneel: Voeg visualisatie toe voor sutabel analyse (zoals `set_figure_sutabel()`)
5. Optioneel: Voeg export functionaliteit toe specifiek voor sutabel resultaten

## Notities

- De formules voor sutabel zijn identiek aan NC_OC methode, maar werken op ln(s'v) en ln(su) in plaats van LN(OCR) en LN(su/svc)
- De analyse filtert automatisch op OC proeven in `expand_analysis_df_sutabel()`
- Alle docstrings zijn in het Nederlands zoals gevraagd
- Variabele en functienamen zijn in het Engels
- STEYX is toegevoegd als extra parameter specifiek voor sutabel analyse

