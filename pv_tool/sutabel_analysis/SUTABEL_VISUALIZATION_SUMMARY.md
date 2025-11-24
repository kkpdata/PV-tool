# Sutabel-m Visualisatie - Implementatie Samenvatting

## ✅ Geïmplementeerd

### Plot 1: ln(s'v) vs ln(su) - VOLLEDIG WERKEND

Deze plot toont de sutabel analyse in de logaritmische ruimte en bevat:

1. **Proefresultaten** (blauwe markers)
   - 9 OC datapunten
   - Met hover info voor boring/monsternummer

2. **Lineaire fit** (groene lijn)
   - Formule: `ln(su) = 1.339025 + 0.627925 × ln(s'v)`
   - Berekend met `e_a1_sutabel` en `e_a2_sutabel`

3. **5% bovengrens** (zwarte streepjeslijn)
   - Betrouwbaarheidsinterval bovengrens
   - Berekend met t-distributie

4. **5% ondergrens** (zwarte streepjeslijn)
   - Betrouwbaarheidsinterval ondergrens
   - Berekend met t-distributie

5. **Fysische realiseerbare ondergrens** (zwarte lijn)
   - Karakteristieke lijn: `ln(su) = 0.804164 + 0.685802 × ln(s'v)`
   - Berekend met `a1_kar_sutabel` en `a2_kar_sutabel`

#### Geïmplementeerde functies:
```python
# In visualization_shansep.py:
- add_proefresultaten_ln_sv_ln_su_sutabel()
- add_lineair_fit_ln_sv_ln_su_sutabel()
- add_5pr_bovengrens_ln_sv_ln_su_sutabel()
- add_5pr_ondergrens_ln_sv_ln_su_sutabel()
- add_fysische_realiseerbare_ondergrens_ln_sv_ln_su_sutabel()
- set_layout_ln_sv_ln_su_sutabel()

# In shansep_analysis.py:
- set_figure_ln_sv_ln_su_sutabel()
- show_figure_ln_sv_ln_su_sutabel()
```

### Plot 2: s'v vs su - DEELS GEÏMPLEMENTEERD

Deze plot toont de sutabel analyse in de normale ruimte en bevat:

1. **Proefresultaten** ✅ (blauwe markers)
   - 9 OC datapunten
   - Met hover info voor boring/monsternummer

2. **Sutabel_kar lijn** ⚠️ TODO
   - Karakteristieke su als functie van s'v
   - Transformatie van ln-ruimte naar normale ruimte nodig

3. **Sutabel_gem lijn** ⚠️ TODO
   - Gemiddelde su als functie van s'v
   - Transformatie van ln-ruimte naar normale ruimte nodig

4. **Su_kar fit met constante VC** ⚠️ TODO
   - Su relatie bij constante verticale consolidatiespanning
   - Specifieke formule/logica vereist

#### Geïmplementeerde functies:
```python
# In visualization_shansep.py:
- add_proefresultaten_sv_su_sutabel()  ✅
- add_sutabel_kar_line()               ⚠️ TODO (leeg)
- add_sutabel_gem_line()               ⚠️ TODO (leeg)
- add_su_kar_fit_constante_vc()        ⚠️ TODO (leeg)
- set_layout_sv_su_sutabel()           ✅

# In shansep_analysis.py:
- set_figure_sv_su_sutabel()           ✅
- show_figure_sv_su_sutabel()          ✅
```

## Gebruik

### Met echte SHANSEP data:
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

# Toon plot 1: ln(s'v) vs ln(su)
shansep.show_figure_ln_sv_ln_su_sutabel()

# Toon plot 2: s'v vs su (met alleen data, andere lijnen TODO)
shansep.show_figure_sv_su_sutabel()
```

### Met test data:
```python
# Run het test script
python test_sutabel_visualization.py
```

## Test Resultaten

### Plot 1 Output:
- ✅ 5 traces correct weergegeven
- ✅ HTML bestand opgeslagen: `test_sutabel_plot1_ln_ln.html`
- ✅ Plot opent in browser
- ✅ Alle lijnen en markers correct

### Plot 2 Output:
- ✅ 1 trace (proefresultaten) correct weergegeven
- ✅ HTML bestand opgeslagen: `test_sutabel_plot2_sv_su.html`
- ✅ Plot opent in browser
- ⚠️ 3 lijnen nog te implementeren

## TODO: Implementatie van ontbrekende lijnen

Voor **Plot 2 (s'v vs su)** moeten de volgende 3 functies nog geïmplementeerd worden:

### 1. `add_sutabel_kar_line()`
**Doel**: Plot de karakteristieke sutabel lijn in s'v-su ruimte

**Mogelijke implementatie**:
```python
def add_sutabel_kar_line(self: SHANSEP):
    """Voegt de karakteristieke sutabel lijn toe."""
    from pv_tool.shansep_analysis.variables import a2_kar_sutabel, a1_kar_sutabel
    
    # Maak range van s'v waarden
    sv_min = self.shansep_data_df_sutabel['S\'v'].min()
    sv_max = self.shansep_data_df_sutabel['S\'v'].max()
    sv_range = np.linspace(sv_min, sv_max, 100)
    
    # Transformeer naar normale ruimte: su = exp(a1_kar + a2_kar * ln(s'v))
    a1_kar = a1_kar_sutabel(self)
    a2_kar = a2_kar_sutabel(self)
    
    su_kar = np.exp(a1_kar + a2_kar * np.log(sv_range))
    # Dit is gelijk aan: su_kar = exp(a1_kar) * sv_range^a2_kar
    
    self.figure.add_trace(
        go.Scatter(
            x=sv_range,
            y=su_kar,
            mode='lines',
            name='Sutabel karakteristiek',
            line=dict(color='black', width=2)
        )
    )
```

### 2. `add_sutabel_gem_line()`
**Doel**: Plot de gemiddelde sutabel lijn in s'v-su ruimte

**Mogelijke implementatie**:
```python
def add_sutabel_gem_line(self: SHANSEP):
    """Voegt de gemiddelde sutabel lijn toe."""
    from pv_tool.shansep_analysis.variables import e_a2_sutabel, e_a1_sutabel
    
    # Maak range van s'v waarden
    sv_min = self.shansep_data_df_sutabel['S\'v'].min()
    sv_max = self.shansep_data_df_sutabel['S\'v'].max()
    sv_range = np.linspace(sv_min, sv_max, 100)
    
    # Transformeer naar normale ruimte: su = exp(a1 + a2 * ln(s'v))
    a1 = e_a1_sutabel(self)
    a2 = e_a2_sutabel(self)
    
    su_gem = np.exp(a1 + a2 * np.log(sv_range))
    # Dit is gelijk aan: su_gem = exp(a1) * sv_range^a2
    
    self.figure.add_trace(
        go.Scatter(
            x=sv_range,
            y=su_gem,
            mode='lines',
            name='Sutabel gemiddeld',
            line=dict(color='purple', width=2, dash='dot')
        )
    )
```

### 3. `add_su_kar_fit_constante_vc()`
**Doel**: Plot su_kar bij constante verticale consolidatiespanning

**Vraag**: Wat is de specifieke formule voor deze lijn?
- Is dit een lijn die door de NC punten gaat?
- Is dit gebaseerd op een specifieke s'vc waarde?
- Hoe verschilt dit van de sutabel_kar lijn?

**Mogelijke aanpak** (als dit vergelijkbaar is met S-POP methode):
```python
def add_su_kar_fit_constante_vc(self: SHANSEP):
    """Voegt su_kar fit met constante VC toe."""
    # TODO: Implementeer op basis van specificatie
    # Mogelijke opties:
    # 1. Als dit vergelijkbaar is met NC lijn in S-POP:
    #    su = S_kar * s'v waar S_kar een constante is
    # 2. Als dit gebaseerd is op een vaste s'vc:
    #    su = exp(a1_kar + a2_kar * ln(s'vc)) voor constante s'vc
    pass
```

## Formule Transformatie

De sutabel-m methode werkt in ln-ruimte:
```
ln(su) = a1 + a2 * ln(s'v)
```

Om naar normale ruimte te transformeren:
```
su = exp(ln(su))
su = exp(a1 + a2 * ln(s'v))
su = exp(a1) * exp(a2 * ln(s'v))
su = exp(a1) * (s'v)^a2
```

Dus de algemene formule in s'v-su ruimte is:
```
su = C * (s'v)^m
```
Waarbij:
- `C = exp(a1)` (constante)
- `m = a2` (exponent/macht)

## Status

✅ **Plot 1 volledig werkend** - Kan gebruikt worden voor sutabel analyse  
⚠️ **Plot 2 basis werkend** - Data wordt getoond, maar lijnen ontbreken  
📝 **Documentatie compleet** - Alle functies gedocumenteerd  
🧪 **Test succesvol** - Beide plots tonen correct

## Bestanden

- `visualization_shansep.py` - 10 nieuwe functies toegevoegd
- `shansep_analysis.py` - 4 nieuwe methoden toegevoegd
- `test_sutabel_visualization.py` - Volledig test script
- HTML outputs:
  - `test_sutabel_plot1_ln_ln.html` - Plot 1 visualisatie
  - `test_sutabel_plot2_sv_su.html` - Plot 2 visualisatie

---

**Datum**: 2025-11-24  
**Status**: Plot 1 ✅ VOLLEDIG | Plot 2 ⚠️ DEELS

