# CSAT-Compass - Fase 3d: evolutie-visualisatie

**Versie:** 1.1  
**Laatst bijgewerkt:** 24/03/2026  

**Doel:** Implementatie van matplotlib 4-subplot PNG-visualisaties voor evolutierapporten  
**Type:** Implementatie  
**Auteur:** Danny Depecker + GHC  
**Status:** Compleet  

**Bestandsnaam:** fase3d-evolutie-visualisatie.md  
**Path:** docs/02-tactisch/fasen/

---

## 1. Overzicht

Fase 3d voegt **matplotlib-visualisaties** toe aan de evolutie-analyse van CSAT-Compass.
Voor elke pijler wordt een 4-subplot PNG gegenereerd die de vergelijking tussen
baseline (2025) en huidig jaar (2026) visueel samenvat.

**T-shirt:** M (8–24u)  
**Afhankelijkheid:** Fase 3b (EvolutionResult) + Fase 3c (EvolutionExporter)  
**Teststand:** 515 tests — 100% coverage — CI stabiel

---

## 2. Deliverables

| Component | Bestand | Status |
|---|---|---|
| `EvolutionVisualiser` | `src/csat/core/exporters/evolution_visualiser.py` | ✅ Compleet |
| Exporters `__init__.py` | `src/csat/core/exporters/__init__.py` | ✅ Bijgewerkt |
| CLI `--chart` vlag | `scripts/generate_evolution.py` | ✅ Bijgewerkt |
| CLI `--chart` vlag batch | `scripts/generate_all_evolutions.py` | ✅ Bijgewerkt |
| Tests | `tests/core/test_evolution_visualiser.py` | ✅ 43 tests |
| Fase-document | `docs/02-tactisch/fasen/fase3d-evolutie-visualisatie.md` | ✅ Dit bestand |

### 2.1 Bestandsnaamconventie output

```
evolutie-{pillar}-{jaar}.png    bv. evolutie-pharma-2026.png
```

Taalversie-onafhankelijk — één PNG per pijler.

---

## 3. Architectuur

### 3.1 Klasse-interface

```python
class EvolutionVisualiser:
    def __init__(self, result: EvolutionResult) -> None: ...

    def render(self) -> plt.Figure:
        """Retourneert matplotlib Figure — geen bestandsschrijving."""

    def export(self, output_path: Path, year: str | None = None) -> Path:
        """Schrijft PNG → output_path/evolutie-{pillar}-{jaar}.png"""
```

### 3.2 Module-level helperfuncties

| Functie | Beschrijving |
|---|---|
| `_fmt_delta(value, decimals)` | Delta formatteren met +/- prefix (ZORGI-getalnotatie) |
| `_extract_year(label)` | Viercijferig jaar extraheren uit een periodeomschrijving |
| `_build_tick_labels(pts)` | X-as labels: jaar op positie "01", maandnummer (MM) elders |
| `_style_ax(ax)` | Leesbare tick-kleuren + `alpha=1.0` forceren op alle ticklabels |
| `_style_legend(legend)` | Witte legenda-achtergrond + donkere tekst op alle legendaitems |

### 3.3 4-subplot layout

```
┌──────────────────────────────────────────────────────────────┐
│  CSAT-Compass — ZORGI PHARMA  |  2025 → 2026  |  Δ +0,93   │
├───────────────────────┬──────────────────────────────────────┤
│  Subplot 1            │  Subplot 2                           │
│  Gem. CSAT-score      │  % Negatief per maand                │
│  per maand            │  Staafdiagram                        │
│  Lijndiagram          │  rood > 15%, pijlerkleur ≤ 15%       │
│  baseline vs huidig   │  baseline vs current (gap)           │
├───────────────────────┼──────────────────────────────────────┤
│  Subplot 3            │  Subplot 4                           │
│  HC-ratio             │  Δ score per ziekenhuis              │
│  2 staven             │  Horizontaal, max 15                 │
│  (baseline + current) │  groen > 0, rood ≤ 0                 │
│  oranje drempellijn   │  gesorteerd beste → slechtste        │
└───────────────────────┴──────────────────────────────────────┘
```

### 3.4 Technische specs

| Parameter | Waarde |
|---|---|
| Figuurformaat | 15×10 inch |
| DPI export | 150 (scherm) — 300 beschikbaar via `_DPI_PRINT` |
| Figuurachtergrond | `#d7e7f3` (Ultra Light Blue — ZORGI Design System) |
| Font | `sans-serif` (Poppins indien aanwezig in `static/fonts/`, anders Verdana) |
| Tekstkleur | `#1a1a1a` (`_LABEL_COLOR`) op alle labels, ticks en annotaties |
| GridSpec kolommen | `width_ratios=[1, 1.2]` — rechterkolom ~55% |
| GridSpec rijen | `height_ratios=[1, 1]` — gelijke hoogte |
| `hspace` / `wspace` | 0.50 / 0.40 |

### 3.5 rcParams override

Na `apply_matplotlib_theme()` worden de volgende globale instellingen overschreven
om `font.weight: light` (de hoofdoorzaak van leesbaarheidsklachten) te neutraliseren:

```python
plt.rcParams.update({
    "font.weight":       "normal",   # was 'light' in apply_matplotlib_theme()
    "axes.labelweight":  "bold",
    "axes.titleweight":  "bold",
    "font.family":       "sans-serif",
    "text.color":        _LABEL_COLOR,
    "axes.labelcolor":   _LABEL_COLOR,
    "xtick.color":       _LABEL_COLOR,
    "ytick.color":       _LABEL_COLOR,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "legend.fontsize":   9,
    "legend.labelcolor": _LABEL_COLOR,
})
```

---

## 4. Subplot-specificaties

### 4.1 Subplot 1 — maandelijkse score-evolutie

- **X-as:** jaar geïntegreerd als ticklabel op positie "01" via `_build_tick_labels()`,
  maandnummer (MM) op alle andere posities — `rotation=0`, `ha="center"`
- **Xlim:** beperkt tot datapunten (`x_b[0]-0.5` … `x_c[-1]+0.5`) — geen lege ruimte
- **Y-as:** gemiddelde CSAT-score, vast bereik 0–5,5
- **Baseline-lijn:** pijlerkleur, `alpha=0.6`, gestippeld (`--`), `linewidth=2`
- **Current-lijn:** pijlerkleur, `alpha=1.0`, vol (`-`), `linewidth=2.5`
- **Drempellijn:** `AVG_SCORE_MIN` = 4,0 — grijs gestippeld, `zorder=4`
- **Jaargrens-lijn:** `color="#888888"`, stippellijn (`:`) op beide bovenste subplots identiek
- **Legenda:** `bbox_to_anchor=(0.01, 0.99)`, `framealpha=0.92`, witte achtergrond

### 4.2 Subplot 2 — % negatief per maand

- **X-as:** zelfde opbouw als subplot 1 via `_build_tick_labels()`;
  lege positie (gap=1) als visuele scheiding tussen baseline en current
- **Xlim:** beperkt tot datapunten (`x_b[0]-0.5` … `x_c[-1]+0.5`)
- **Y-as:** percentage negatieve scores (0 … max + 15%)
- **Kleur:** `#dc2b26` (rood) als pct > 15%, pijlerkleur als ≤ 15%
- **Opacity:** baseline 0.6, current 1.0
- **Drempellijn:** 15% — rood gestippeld, `zorder=5`
- **Jaargrens-lijn:** identiek aan subplot 1

### 4.3 Subplot 3 — HC-ratio samenvatting

- **Staven:** 2 staven, `width=0.45` — baseline (links, `alpha=0.6`), current (rechts, `alpha=1.0`)
- **Xlim:** `(-0.75, 1.75)` — staven gecentreerd, geen dode ruimte
- **Kleur:** rood als > 15%, pijlerkleur als ≤ 15%
- **Drempellijn:** `HIGH_CRITICAL_MAX` = 15% — oranje gestippeld, `zorder=5`
- **Annotaties:** procentwaarden (`fontsize=11`) boven elke staaf

### 4.4 Subplot 4 — delta per ziekenhuis

- **Type:** horizontaal staafdiagram (`barh`)
- **Selectie:** alleen ziekenhuizen aanwezig in **beide** periodes
- **Sortering:** beste delta bovenaan (descending)
- **Beperking:** max. 15 ziekenhuizen (top 7 + bottom 8 bij meer)
- **Kleur:** `#00aa44` (groen) als delta > 0, `#dc2b26` (rood) als delta ≤ 0
- **Xlim:** `min_delta - 0.5` … `max_delta + 0.8` — exact op werkelijke data
- **Annotaties:** `clip_on=False` zodat waarden nooit afgesneden worden
- **Y-as tick-streepjes:** `length=0` — labels zichtbaar, streepjes onzichtbaar

### 4.5 Globale opmaak — alle subplots

- **Spines:** `edgecolor="#cccccc"`, `linewidth=0.8` — subtiel kader op alle 4
- **Gridlines:** enkel horizontaal (`yaxis.grid`), `color="#dddddd"`, `linewidth=0.6`;
  `xaxis.grid(False)` expliciet uitgeschakeld op alle subplots
- **`set_axisbelow(True)`:** grid altijd achter de bars/lijnen

---

## 5. Gebruik

### 5.1 CLI — per pijler

```powershell
# Rapport + visualisatie
.venv\Scripts\python.exe scripts/generate_evolution.py --pillar pharma --chart

# Met specifieke periodes
.venv\Scripts\python.exe scripts/generate_evolution.py --pillar pharma --baseline 2025-01 2025-12 --current 2026-01 2026-03 --chart

# Alleen rapport NL + visualisatie
.venv\Scripts\python.exe scripts/generate_evolution.py --pillar pharma --lang nl --chart
```

### 5.2 CLI — alle pijlers

```powershell
# Rapporten + visualisaties voor alle 5 pijlers
.venv\Scripts\python.exe scripts/generate_all_evolutions.py --chart

# Met periodes
.venv\Scripts\python.exe scripts/generate_all_evolutions.py --baseline 2025-01 2025-12 --current 2026-01 2026-03 --chart
```

### 5.3 Python API

```python
from csat.core.analysers.evolution_analyser import EvolutionAnalyser
from csat.core.exporters.evolution_visualiser import EvolutionVisualiser
from pathlib import Path

analyser = EvolutionAnalyser(df, pillar_key="pharma")
result = analyser.analyse(
    baseline_periods=["2025-01", ..., "2025-12"],
    current_periods=["2026-01", "2026-02", "2026-03"],
)

vis = EvolutionVisualiser(result)

# Optie A: figuur zonder bestandsschrijving
fig = vis.render()

# Optie B: direct naar PNG
pad = vis.export(Path("output"), year="2026")
# → output/evolutie-pharma-2026.png
```

---

## 6. Referentiebestanden

| Bestand | Rol |
|---|---|
| `src/csat/utils/branding.py` | `apply_matplotlib_theme()`, `COLORS`, `PILLAR_COLORS` |
| `src/csat/config/pillars.py` | `PILLAR_REGISTRY` — kleur + naam per pijler |
| `src/csat/config/settings.py` | `AVG_SCORE_MIN` (4,0), `HIGH_CRITICAL_MAX` (15,0) |
| `src/csat/core/analysers/evolution_result.py` | Input-dataklassen |
| `src/csat/core/exporters/evolution_exporter.py` | Patroon render()/export() |
| `tests/core/test_evolution_visualiser.py` | 43 unit tests |

---

## 7. Testoverzicht

| Klasse | Tests | Beschrijving |
|---|---|---|
| `TestFmtDelta` | 5 | ZORGI-getalnotatie met +/- prefix |
| `TestExtractYear` | 5 | Jaar extraheren uit variabele labels |
| `TestEvolutionVisualiserInit` | 4 | Pijlerkleur- en naamlookup, fallback |
| `TestRender` | 9 | Figure, 4 assen, formaat, facecolor, titels |
| `TestExport` | 10 | PNG-schrijving, naam, map, logger, figuur sluiten |
| `TestSubplots` | 10 | Subplot-inhoud, drempellijnen, max 15 ziekenhuizen |
| **Totaal** | **43** | 100% coverage (`# pragma: no cover` op defensieve fallbacks) |

---

## 8. Relatie tot andere fasen

```
Fase 3b ──► EvolutionResult ──► Fase 3d: EvolutionVisualiser
Fase 3c ──► EvolutionExporter              │
                                           ▼
                                   evolutie-{pillar}-{jaar}.png
```

**Volgende stap:** Fase 3e — `run_monthly.py` (alles in één run)

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 24/03/2026 | Initiële versie — Fase 3d compleet | Danny Depecker + GHC |
| 1.1 | 24/03/2026 | Visuele verfijning: helpers `_style_ax`, `_style_legend`, `_build_tick_labels`; rcParams override `font.weight`; GridSpec proporties; jaar geïntegreerd op x-as; jaargrens-lijn op beide bovenste subplots; spine/grid styling; xlim-beperkingen alle subplots | Danny Depecker + GHC |
