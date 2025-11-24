# ✅ Sutabel-m VOLLEDIGE Implementatie - COMPLEET!

## Status: 🎉 100% GEÏMPLEMENTEERD EN GETEST

Alle functionaliteit voor de sutabel-m methode is nu volledig geïmplementeerd, inclusief beide plots met alle lijnen!

---

## Nieuwe Parameters Geïmplementeerd

### In SHANSEP Class (`__init__`):

```python
# Sutabel basis parameters
self.e_a2_sutabel: Optional[float] = None
self.e_a1_sutabel: Optional[float] = None
self.a2_kar_sutabel: Optional[float] = None
self.a1_kar_sutabel: Optional[float] = None
self.steyx_sutabel: Optional[float] = None

# Sutabel afgeleide parameters voor grafieken
self.svgm_gem_sutabel: Optional[float] = None   # exp(e_a1)
self.m_gem_sutabel: Optional[float] = None      # 1 - e_a2
self.svgm_kar_sutabel: Optional[float] = None   # exp(a1_kar)
self.m_kar_sutabel: Optional[float] = None      # 1 - a2_kar
self.CV_fit_kar_sutabel: Optional[float] = None # User input
self.STDEV_logn_CV_sutabel: Optional[float] = None # sqrt(LN(1 + CV^2))

# Sutabel dataframes voor grafieken
self.sutabel_grafiek: Optional[DataFrame] = None
self.su_fit_constante_CV: Optional[DataFrame] = None
```

---

## Berekeningen

### 1. Basis Parameters (uit regressie)
- **e_a2_sutabel** = 0.627925 (helling gemiddeld)
- **e_a1_sutabel** = 1.339025 (snijpunt gemiddeld)
- **a2_kar_sutabel** = 0.685802 (helling karakteristiek)
- **a1_kar_sutabel** = 0.804164 (snijpunt karakteristiek)
- **steyx_sutabel** = 0.246166

### 2. Afgeleide Parameters
- **svgm_gem** = exp(e_a1) = 3.8153 kPa
- **m_gem** = 1 - e_a2 = 0.3721
- **svgm_kar** = exp(a1_kar) = 2.2348 kPa
- **m_kar** = 1 - a2_kar = 0.3142

### 3. CV Parameters (user input = 0.2)
- **CV_fit_kar** = 0.2000 (20%)
- **STDEV_logn_CV** = sqrt(LN(1 + 0.2²)) = 0.1980

### 4. Sutabel_grafiek Dataframe

| s'v [kPa] | su_gem [kPa] | su_kar [kPa] |
|-----------|--------------|--------------|
| 1.00      | 3.82         | 2.23         |
| 5.00      | 10.48        | 6.74         |
| 10.00     | 16.20        | 10.84        |
| 20.00     | 25.03        | 17.44        |
| 30.00     | 32.29        | 23.03        |
| 40.00     | 38.68        | 28.05        |
| 93.42     | 65.89        | 50.19        |

**Formules**:
- `su_gem = svgm_gem × (s'v)^(1-m_gem) = 3.8153 × (s'v)^0.6279`
- `su_kar = svgm_kar × (s'v)^(1-m_kar) = 2.2348 × (s'v)^0.6858`

### 5. Su_fit_constante_CV Dataframe

| s'v [kPa] | ln(su_gem) | ln(su_kar) | su_kar fit CV [kPa] |
|-----------|------------|------------|---------------------|
| 1.00      | 1.319      | 0.785      | 2.70                |
| 5.00      | 2.330      | 1.888      | 7.42                |
| 10.00     | 2.765      | 2.364      | 11.47               |
| 20.00     | 3.201      | 2.839      | 17.72               |
| 30.00     | 3.455      | 3.117      | 22.86               |
| 40.00     | 3.636      | 3.314      | 27.39               |
| 93.42     | 4.168      | 3.896      | 46.65               |

**Formules**:
- `ln(su_gem) = LN(su_gem) - 0.5 × STDEV_logn_CV²`
- `ln(su_kar) = LN(su_kar) - 0.5 × STDEV_logn_CV²`
- `su_kar_fit_CV = LOGNORM.INV(0.05; ln(su_gem); STDEV_logn_CV)`

Python implementatie:
```python
su_kar_fit_cv = lognorm.ppf(0.05, s=STDEV_logn_CV, scale=exp(ln_su_gem))
```

---

## Plots

### 📊 Plot 1: ln(s'v) vs ln(su) - 100% COMPLEET

**5 Traces**:
1. ✅ Proefresultaten (blauwe markers)
2. ✅ Lineaire fit (groene lijn): `ln(su) = 1.339 + 0.628 × ln(s'v)`
3. ✅ 5% bovengrens (zwarte streepjes)
4. ✅ 5% ondergrens (zwarte streepjes)
5. ✅ Fysische realiseerbare ondergrens (zwarte lijn): `ln(su) = 0.804 + 0.686 × ln(s'v)`

### 📊 Plot 2: s'v vs su - 100% COMPLEET

**4 Traces**:
1. ✅ Proefresultaten (blauwe markers)
2. ✅ Sutabel gemiddeld (paarse stippellijn): `su = 3.82 × (s'v)^0.628`
3. ✅ Sutabel karakteristiek (zwarte lijn): `su = 2.23 × (s'v)^0.686`
4. ✅ Su kar fit met constante CV (rode streeplijn)

---

## Nieuwe Methoden

### In shansep_analysis.py:

```python
def get_shansep_parameters(self, CV_fit_kar_sutabel: Optional[float] = None):
    """
    Berekent parameters inclusief sutabel-specifieke afgeleide waarden.
    
    Parameters:
        CV_fit_kar_sutabel: Coefficient of Variation voor sutabel fit
    """
```

```python
def calculate_sutabel_grafiek(self):
    """
    Berekent de dataframes voor sutabel grafiek lijnen:
    - sutabel_grafiek: su_gem en su_kar lijnen
    - su_fit_constante_CV: CV fit lijn (als CV opgegeven)
    """
```

```python
def set_figure_ln_sv_ln_su_sutabel(self):
    """Plot 1: ln(s'v) vs ln(su)"""
```

```python
def show_figure_ln_sv_ln_su_sutabel(self):
    """Toon Plot 1"""
```

```python
def set_figure_sv_su_sutabel(self):
    """Plot 2: s'v vs su met alle lijnen"""
```

```python
def show_figure_sv_su_sutabel(self):
    """Toon Plot 2"""
```

### In visualization_shansep.py:

```python
# Plot 1 (ln-ruimte)
def add_proefresultaten_ln_sv_ln_su_sutabel(self)
def add_lineair_fit_ln_sv_ln_su_sutabel(self)
def add_5pr_bovengrens_ln_sv_ln_su_sutabel(self)
def add_5pr_ondergrens_ln_sv_ln_su_sutabel(self)
def add_fysische_realiseerbare_ondergrens_ln_sv_ln_su_sutabel(self)
def set_layout_ln_sv_ln_su_sutabel(self)

# Plot 2 (normale ruimte)
def add_proefresultaten_sv_su_sutabel(self)
def add_sutabel_gem_line(self)          # NIEUW GEÏMPLEMENTEERD
def add_sutabel_kar_line(self)          # NIEUW GEÏMPLEMENTEERD
def add_su_kar_fit_constante_vc(self)   # NIEUW GEÏMPLEMENTEERD
def set_layout_sv_su_sutabel(self)
```

---

## Gebruik

### Met echte data:

```python
from pv_tool.shansep_analysis.shansep_analysis import SHANSEP
from pv_tool.imports.import_data import Dbase

# Laad database
dbase = Dbase('database.xlsx')

# Maak SHANSEP instantie
shansep = SHANSEP(
    dbase=dbase,
    analysis_type='TXT_su_tabel',
    investigation_groups=['PV_NAAM'],
    effective_stress='15% rek'
)

# Voer analyse uit met optionele CV parameter
shansep._run_shansep()
shansep.get_shansep_parameters(CV_fit_kar_sutabel=0.2)  # 20% CV

# Toon Plot 1: ln(s'v) vs ln(su)
shansep.show_figure_ln_sv_ln_su_sutabel()

# Toon Plot 2: s'v vs su (met alle 4 lijnen!)
shansep.show_figure_sv_su_sutabel()

# Bekijk de berekende dataframes
print(shansep.sutabel_grafiek)
print(shansep.su_fit_constante_CV)
```

### Met test data:

```bash
python test_sutabel_complete.py
```

---

## Test Resultaten

### ✅ Test met 9 OC samples geslaagd

**Input data**:
- s'v: [48.28, 52.05, 85.72, 27.84, 79.82, 93.42, 31.64, 75.72, 12.90] kPa
- su: [60.18, 51.40, 67.77, 41.76, 59.79, 52.43, 31.67, 43.88, 14.44] kPa
- CV_fit_kar: 0.2 (20%)

**Output**:
- ✅ Plot 1: 5 traces correct
- ✅ Plot 2: 4 traces correct
- ✅ Beide plots openen in browser
- ✅ HTML bestanden opgeslagen
- ✅ Alle parameters correct berekend
- ✅ Alle dataframes correct berekend

---

## Bestanden

### Gewijzigd:
1. **shansep_analysis.py**:
   - Nieuwe parameters toegevoegd
   - `get_shansep_parameters()` uitgebreid
   - `calculate_sutabel_grafiek()` toegevoegd
   - `set_figure_sv_su_sutabel()` geïmplementeerd
   - `show_figure_sv_su_sutabel()` geïmplementeerd

2. **visualization_shansep.py**:
   - `add_sutabel_gem_line()` volledig geïmplementeerd
   - `add_sutabel_kar_line()` volledig geïmplementeerd
   - `add_su_kar_fit_constante_vc()` volledig geïmplementeerd

### Nieuw:
3. **test_sutabel_complete.py** - Volledig test script met alle lijnen

### Output:
4. **test_sutabel_complete_plot1.html** - Plot 1 visualisatie
5. **test_sutabel_complete_plot2.html** - Plot 2 visualisatie

---

## Formules Overzicht

### Van ln-ruimte naar normale ruimte:

**Regressie in ln-ruimte**:
```
ln(su) = a1 + a2 × ln(s'v)
```

**Transformatie naar normale ruimte**:
```
su = exp(ln(su))
su = exp(a1 + a2 × ln(s'v))
su = exp(a1) × (s'v)^a2
```

**Sutabel formule**:
```
su = svgm × (s'v)^(1-m)
```

Waarbij:
- `svgm = exp(a1)` - Sutabel parameter
- `m = 1 - a2` - Exponent parameter

**CV fit formule** (lognormaal):
```
ln(su_adjusted) = ln(su) - 0.5 × STDEV_logn_CV²
su_kar_fit = LOGNORM.INV(0.05; ln(su_adjusted); STDEV_logn_CV)
```

Python:
```python
su_kar_fit = lognorm.ppf(0.05, s=STDEV_logn_CV, scale=exp(ln_su_adjusted))
```

---

## Checklist

- [x] Sutabel basis parameters berekend
- [x] Afgeleide parameters (svgm, m) berekend
- [x] CV parameters berekend
- [x] sutabel_grafiek dataframe gemaakt
- [x] su_fit_constante_CV dataframe gemaakt
- [x] Plot 1: Alle 5 traces geïmplementeerd
- [x] Plot 2: Alle 4 traces geïmplementeerd
- [x] Lognormale CV fit correct geïmplementeerd
- [x] Test script werkt perfect
- [x] Beide plots tonen correct
- [x] HTML export werkt
- [x] Alle formules geverifieerd

---

## 🎉 Conclusie

**Beide plots zijn nu 100% compleet en functioneel!**

Alle lijnen zijn geïmplementeerd volgens de specificaties:
- ✅ su_gem lijn met formule: `su = 3.82 × (s'v)^0.628`
- ✅ su_kar lijn met formule: `su = 2.23 × (s'v)^0.686`
- ✅ su_kar fit met constante CV lijn (lognormale distributie)

De sutabel-m methode is nu volledig operationeel en kan gebruikt worden voor echte analyses! 🚀

---

**Implementatie**: GitHub Copilot  
**Datum**: 2025-11-24  
**Status**: ✅ VOLLEDIG COMPLEET
**Test**: ✅ GESLAAGD

