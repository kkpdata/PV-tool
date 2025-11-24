# 🎉 SUTABEL Handmatige Parameters - COMPLEET!

## ✅ Status: Volledig Geïmplementeerd en Getest

Gebruikers kunnen nu iteratief parameters aanpassen, exact zoals in SHANSEP!

---

## 🆕 Nieuwe Functionaliteit

### Handmatige Parameters Instellen

Gebruikers kunnen nu de volgende parameters handmatig aanpassen:
- **a1_kar** - Karakteristiek snijpunt in ln-ruimte
- **a2_kar** - Karakteristieke helling in ln-ruimte  
- **CV_fit_kar** - Coefficient of Variation voor fit

---

## 💻 Gebruik

### Basisworkflow:

```python
from pv_tool.sutabel_analysis import SUTABEL
from pv_tool.imports.import_data import Dbase

# 1. Maak SUTABEL instantie
dbase = Dbase('database.xlsx')
sutabel = SUTABEL(
    dbase=dbase,
    analysis_type='TXT_su_tabel',
    investigation_groups=['PVNAAM'],
    effective_stress='15% rek',
    alpha=0.75
)

# 2. Eerste analyse met BEREKENDE parameters
sutabel._run_sutabel()
sutabel.get_sutabel_parameters(CV_fit_kar_sutabel=0.2)
sutabel.calculate_sutabel_grafiek()
sutabel.show_figure_sv_su_sutabel()  # Toon grafiek met berekende parameters

# Bekijk de berekende waarden
print(f"Berekend a1_kar: {sutabel.a1_kar_sutabel:.6f}")
print(f"Berekend a2_kar: {sutabel.a2_kar_sutabel:.6f}")

# 3. Pas parameters HANDMATIG aan - ITERATIE 1
sutabel.set_manual_parameters(
    a1_kar=0.85,
    a2_kar=0.70,
    CV_fit_kar=0.25
)
sutabel.show_figure_sv_su_sutabel()  # Toon grafiek met HANDMATIGE parameters

# 4. Pas opnieuw aan - ITERATIE 2 (alleen CV)
sutabel.set_manual_parameters(CV_fit_kar=0.15)
sutabel.show_figure_sv_su_sutabel()  # Grafiek met nieuwe CV

# 5. Pas opnieuw aan - ITERATIE 3 (alleen a2_kar)
sutabel.set_manual_parameters(a2_kar=0.68)
sutabel.show_figure_sv_su_sutabel()  # Grafiek met aangepaste a2_kar
```

---

## 🔧 Nieuwe Methoden

### 1. `set_manual_parameters()`

```python
def set_manual_parameters(self, 
                         a1_kar: Optional[float] = None,
                         a2_kar: Optional[float] = None,
                         CV_fit_kar: Optional[float] = None):
    """
    Stelt handmatige parameters in voor de sutabel analyse.
    
    Parameters
    ----------
    a1_kar : float, optioneel
        Handmatig ingesteld karakteristiek snijpunt in ln-ruimte
    a2_kar : float, optioneel
        Handmatig ingestelde karakteristieke helling in ln-ruimte
    CV_fit_kar : float, optioneel
        Handmatig ingestelde Coefficient of Variation voor fit
    """
```

**Functionaliteit**:
- ✅ Slaat handmatige waarden op
- ✅ Zet `parameters_handmatig` flag op `True`
- ✅ Roept automatisch `_update_parameters_from_manual()` aan
- ✅ Herberekent afgeleide parameters

**Gebruik**:
```python
# Alle parameters tegelijk
sutabel.set_manual_parameters(a1_kar=0.85, a2_kar=0.70, CV_fit_kar=0.25)

# Of selectief
sutabel.set_manual_parameters(CV_fit_kar=0.15)  # Alleen CV
sutabel.set_manual_parameters(a2_kar=0.68)       # Alleen a2_kar
```

### 2. `_update_parameters_from_manual()` (private)

```python
def _update_parameters_from_manual(self):
    """
    Update de gebruikte parameters op basis van handmatige input.
    
    Automatisch aangeroepen door set_manual_parameters().
    """
```

**Functionaliteit**:
- ✅ Controleert welke parameters handmatig zijn ingesteld
- ✅ Gebruikt handmatige waarden indien beschikbaar
- ✅ Behoudt berekende waarden voor niet-ingestelde parameters
- ✅ Herberekent afgeleide parameters:
  - `svgm_kar = exp(a1_kar)`
  - `m_kar = 1 - a2_kar`
  - `STDEV_logn_CV = sqrt(ln(1 + CV²))`
- ✅ Herberekent grafiek dataframes (`sutabel_grafiek`, `su_fit_constante_CV`)

---

## 📊 Wat Wordt Automatisch Herberekend?

### Bij Aanpassen van a1_kar:
```python
sutabel.set_manual_parameters(a1_kar=0.85)
```
**Herberekend**:
- ✅ `svgm_kar = exp(0.85) = 2.3396 kPa`
- ✅ `sutabel_grafiek` dataframe (su_kar lijn)
- ✅ `su_fit_constante_CV` dataframe (indien CV ingesteld)

### Bij Aanpassen van a2_kar:
```python
sutabel.set_manual_parameters(a2_kar=0.70)
```
**Herberekend**:
- ✅ `m_kar = 1 - 0.70 = 0.30`
- ✅ `sutabel_grafiek` dataframe (su_kar lijn)
- ✅ `su_fit_constante_CV` dataframe (indien CV ingesteld)

### Bij Aanpassen van CV_fit_kar:
```python
sutabel.set_manual_parameters(CV_fit_kar=0.25)
```
**Herberekend**:
- ✅ `STDEV_logn_CV = sqrt(ln(1 + 0.25²)) = 0.2462`
- ✅ `su_fit_constante_CV` dataframe (CV fit lijn)

---

## 🔄 Iteratieve Workflow

### Scenario: Gebruiker past parameters meerdere keren aan

#### Iteratie 1: Alle parameters
```python
sutabel._run_sutabel()  # Berekende: a1=0.804, a2=0.686, CV=0.20
sutabel.show_figure_sv_su_sutabel()

sutabel.set_manual_parameters(a1_kar=0.85, a2_kar=0.70, CV_fit_kar=0.25)
sutabel.show_figure_sv_su_sutabel()  # Handmatig: a1=0.85, a2=0.70, CV=0.25
```

#### Iteratie 2: Alleen CV aanpassen
```python
sutabel.set_manual_parameters(CV_fit_kar=0.15)
sutabel.show_figure_sv_su_sutabel()  # Handmatig: a1=0.85, a2=0.70, CV=0.15
```
**Resultaat**: a1 en a2 blijven 0.85 en 0.70, alleen CV wordt 0.15

#### Iteratie 3: Alleen a2_kar aanpassen
```python
sutabel.set_manual_parameters(a2_kar=0.68)
sutabel.show_figure_sv_su_sutabel()  # Handmatig: a1=0.85, a2=0.68, CV=0.15
```
**Resultaat**: a1 en CV blijven ongewijzigd, a2 wordt 0.68

---

## 🆕 Nieuwe Attributen

### In `__init__`:
```python
# Handmatige parameters
self.parameters_handmatig: bool = False
self.a1_kar_handmatig: Optional[float] = None
self.a2_kar_handmatig: Optional[float] = None
self.CV_fit_kar_handmatig: Optional[float] = None
```

---

## 📈 Test Resultaten

### ✅ Test met 9 OC samples

**Berekende parameters**:
- a1_kar = 0.804164
- a2_kar = 0.685802
- svgm_kar = 2.2348 kPa
- m_kar = 0.3142

**Na Iteratie 1** (alle parameters handmatig):
- a1_kar = 0.850000 (verschil: +0.0458)
- a2_kar = 0.700000 (verschil: -0.0058)
- svgm_kar = 2.3396 kPa (herberekend)
- m_kar = 0.3000 (herberekend)
- CV = 0.25 (was 0.20)

**Na Iteratie 2** (alleen CV):
- a1_kar = 0.850000 (onveranderd)
- a2_kar = 0.700000 (onveranderd)
- CV = 0.15 (aangepast)
- STDEV = 0.1492 (herberekend)

**Na Iteratie 3** (alleen a2):
- a1_kar = 0.850000 (onveranderd)
- a2_kar = 0.680000 (aangepast)
- m_kar = 0.3200 (herberekend)

---

## 🎯 Voordelen

### 1. **Flexibiliteit**
- ✅ Gebruikers kunnen elk van de 3 parameters apart aanpassen
- ✅ Of allemaal tegelijk
- ✅ Meerdere iteraties mogelijk

### 2. **Automatische Herberekening**
- ✅ Afgeleide parameters worden automatisch geüpdatet
- ✅ Grafiek dataframes worden automatisch herberekend
- ✅ Geen handmatige stappen nodig

### 3. **Consistentie met SHANSEP**
- ✅ Zelfde workflow als SHANSEP
- ✅ Zelfde method naam: `set_manual_parameters()`
- ✅ Vergelijkbare implementatie

### 4. **Type Safety**
- ✅ Optional parameters - alleen wat nodig is
- ✅ Type hints voor IDE ondersteuning
- ✅ Duidelijke documentatie

---

## 🔍 Visualisatie Updates

### Plot 1: ln(s'v) vs ln(su)
**Fysische realiseerbare ondergrens** gebruikt handmatige parameters:

```python
# In visualization.py
def add_fysische_realiseerbare_ondergrens_ln_sv_ln_su_sutabel(self):
    # Gebruikt handmatige a1_kar en a2_kar als ingesteld
    if self.parameters_handmatig:
        a1_kar = self.a1_kar_handmatig or berekend_a1_kar
        a2_kar = self.a2_kar_handmatig or berekend_a2_kar
    # ...
```

### Plot 2: s'v vs su
Alle lijnen gebruiken geüpdatete parameters:
- **su_kar lijn**: Gebruikt `svgm_kar` en `m_kar` (herberekend)
- **CV fit lijn**: Gebruikt `STDEV_logn_CV` (herberekend)

---

## 📝 Code Voorbeelden

### Voorbeeld 1: Calibratie Workflow
```python
# Start met berekende parameters
sutabel = SUTABEL(...)
sutabel._run_sutabel()
sutabel.show_figure_sv_su_sutabel()

# Gebruiker ziet dat karakteristieke lijn te conservatief is
# Pas a1_kar aan voor hogere waarden
sutabel.set_manual_parameters(a1_kar=0.90)
sutabel.show_figure_sv_su_sutabel()

# Nog steeds niet goed, pas ook a2 aan
sutabel.set_manual_parameters(a1_kar=0.90, a2_kar=0.65)
sutabel.show_figure_sv_su_sutabel()

# Perfect! Export resultaten
sutabel.save_to_pdf(path="C:/output", CV_fit_kar=0.20)
```

### Voorbeeld 2: Gevoeligheidsanalyse CV
```python
sutabel = SUTABEL(...)
sutabel._run_sutabel()

# Test verschillende CV waarden
for cv in [0.15, 0.20, 0.25, 0.30]:
    sutabel.set_manual_parameters(CV_fit_kar=cv)
    sutabel.show_figure_sv_su_sutabel()
    # Gebruiker ziet effect van verschillende CV waarden
```

### Voorbeeld 3: Verificatie met Externe Bron
```python
# Externe bron geeft karakteristieke parameters
a1_extern = 0.82
a2_extern = 0.69

sutabel = SUTABEL(...)
sutabel._run_sutabel()

# Vergelijk berekend met extern
print(f"Berekend: a1={sutabel.a1_kar_sutabel:.3f}, a2={sutabel.a2_kar_sutabel:.3f}")
print(f"Extern:   a1={a1_extern:.3f}, a2={a2_extern:.3f}")

# Gebruik externe waarden
sutabel.set_manual_parameters(a1_kar=a1_extern, a2_kar=a2_extern)
sutabel.show_figure_sv_su_sutabel()
```

---

## ✅ Checklist

- [x] `set_manual_parameters()` methode geïmplementeerd
- [x] `_update_parameters_from_manual()` helper methode
- [x] Handmatige parameter attributen toegevoegd
- [x] Automatische herberekening van afgeleide parameters
- [x] Visualisaties gebruiken handmatige parameters
- [x] Test script werkt volledig
- [x] Iteratieve aanpassingen mogelijk
- [x] Consistent met SHANSEP implementatie
- [x] Type hints correct
- [x] Documentatie compleet

---

## 🎉 Conclusie

De **handmatige parameters functionaliteit** is volledig geïmplementeerd!

**Gebruikers kunnen nu**:
1. ✅ Eerste analyse uitvoeren met berekende parameters
2. ✅ Grafieken bekijken
3. ✅ Parameters handmatig aanpassen
4. ✅ Grafieken opnieuw genereren met nieuwe parameters
5. ✅ Meerdere iteraties uitvoeren
6. ✅ Resultaten exporteren

**Exact zoals in SHANSEP**, maar dan voor sutabel-m! 🚀

---

**Datum**: 2025-11-24  
**Status**: ✅ COMPLEET  
**Test**: ✅ PASSED  
**Methoden**: 2 nieuwe  
**Attributen**: 4 nieuwe  
**Gebruik**: Volledig gedocumenteerd

