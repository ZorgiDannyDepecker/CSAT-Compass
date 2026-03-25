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

```text
evolutie-{pillar}-{jaar}[_{YYYYMMDD-HHMM}].png

Standaard (timestamp=True):   evolutie-pharma-2026_20260325-1524.png
Zonder timestamp (timestamp=False): evolutie-pharma-2026.png
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

    def export(self, output_path: Path, year: str | None = None, timestamp: bool = True) -> Path:
        """Schrijft PNG → output_path/evolutie-{pillar}-{jaar}[_{ts}].png
        timestamp=True voegt _YYYYMMDD-HHMM toe aan de bestandsnaam."""
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

```text
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

### 3.5 rcParams override (ZORGI Design System)

Na `apply_matplotlib_theme()` worden de volgende globale instellingen overschreven
via `plt.rcParams.update()`. DejaVu Sans heeft volledige Unicode-dekking (pijl ↠, delta Δ)
die Poppins mist op Windows — vandaar de prioriteitvolgorde.

```python
plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.sans-serif":   ["DejaVu Sans", "Verdana", "Poppins"],
    "font.weight":       "normal",
    "axes.titleweight":  "bold",
    "axes.labelweight":  "normal",
    "text.color":        "#1a1a1a",   # ZORGI_BODY_TEXT
    "axes.labelcolor":   "#1a1a1a",
    "xtick.color":       "#1a1a1a",
    "ytick.color":       "#1a1a1a",
    "axes.facecolor":    "#d7e7f3",   # ZORGI_ULTRA_LIGHT
    "figure.facecolor":  "#d7e7f3",
    "axes.titlesize":    11,
    "axes.labelsize":    9,
    "xtick.labelsize":   8.5,
    "ytick.labelsize":   8.5,
    "legend.fontsize":   8.5,
})
```

---

## 4. Subplot-specificaties

### 4.1 Subplot 1 — maandelijkse score-evolutie

> **Datumbasis (ADR-011):** periodegroepering op `satisfaction_date`. Een lege maand
> betekent dat geen klanten die maand een score indienden — geen data-fout.

- **X-as:** jaar geïntegreerd als ticklabel op positie "01" via `_build_tick_labels()`,
  maandnummer (MM) op alle andere posities — `rotation=0`, `ha="center"`
- **Xlim:** beperkt tot datapunten (`x_b[0]-0.5` … `x_c[-1]+0.5`) — geen lege ruimte
- **Y-as:** gemiddelde CSAT-score, vast bereik 0–5,5
- **Baseline-lijn:** `ZORGI_LIGHT_BLUE` (#609fce), `alpha=0.85`, gestippeld (`--`), `linewidth=1.5`, `markersize=4`
- **Current-lijn:** `ZORGI_DARK_BLUE` (#003a70), `alpha=1.0`, vol (`-`), `linewidth=2.0`, `markersize=5`
- **Verbindingssegment:** `ZORGI_GREY_BLUE` (#5f8495), `alpha=0.5`, vol (`-`), `linewidth=1.2` — verbindt het laatste baselinepunt met het eerste current-punt voor één doorgaande lijn
- **Drempellijn:** `AVG_SCORE_MIN` = 4,0 — `ZORGI_GREY_BLUE` gestippeld, `zorder=4`
- **Jaargrens-lijn:** `ZORGI_DARK_BLUE` (#003a70), stippellijn (`:`), `linewidth=1.4`, `alpha=0.6` — op beide bovenste subplots identiek
- **Legenda:** `bbox_to_anchor=(0.01, 0.99)`, `framealpha=0.92`, witte achtergrond

### 4.2 Subplot 2 — % negatief per maand

> **Datumbasis (ADR-011):** zelfde `satisfaction_date`-groepering als subplot 1.
> Een maand met 0% negatief toont een nul-bar — correct gedrag.

- **X-as:** zelfde opbouw als subplot 1 via `_build_tick_labels()`; direct aansluitend (geen gap)
- **Xlim:** beperkt tot datapunten (`x_b[0]-0.5` … `x_c[-1]+0.5`)
- **Y-as:** dynamisch — `max(HIGH_CRITICAL_MAX × 2, min(100, max_pct + 15))` zodat kleine waarden (< 20%) proportioneel leesbaar blijven; minimum 30% om de drempellijn altijd zichtbaar te houden
- **Kleur:** `ZORGI_RED` (#dc2b26) als pct > 15%; `ZORGI_LIGHT_BLUE` (#609fce) als ≤ 15%
- **Opacity:** baseline 0.6, current 1.0
- **Drempellijn:** 15% — `ZORGI_RED` gestippeld, `zorder=5`
- **Jaargrens-lijn:** identiek aan subplot 1

### 4.3 Subplot 3 — HC-ratio samenvatting

> **Definitie HC-ratio:** `(Blocker + Critical + Major tickets) ÷ (alle tickets) × 100`
> HC-ratio gebruikt **alle** tickets — niet alleen gescoorde. Drempel: 15%.
> **Datumbasis (ADR-011):** `_get_df_for_periods()` filtert op `satisfaction_date`.

- **Staven:** 2 staven, `width=0.45` — baseline (links, `alpha=0.6`), current (rechts, `alpha=1.0`)
- **Xlim:** `(-0.75, 1.75)` — staven gecentreerd, geen dode ruimte
- **Kleur:** altijd `ZORGI_RED` (#dc2b26) — HC-ratio is per definitie een aandachtspunt, geen conditionele kleur
- **Y-as:** dynamisch — `max(HIGH_CRITICAL_MAX × 2, min(100, max_val + 20))` — zelfde principe als subplot 2
- **Drempellijn:** `HIGH_CRITICAL_MAX` = 15% — `ZORGI_PURPLE` (#7f4267) gestippeld, `zorder=5`
- **Annotaties:** procentwaarden (`fontsize=11`, `ZORGI_BODY_TEXT`) boven elke staaf

### 4.4 Subplot 4 — delta per ziekenhuis

> **Datumbasis (ADR-011):** zelfde `satisfaction_date`-groepering als subplots 1–3.

- **Type:** horizontaal staafdiagram (`barh`)
- **Selectie:** alleen ziekenhuizen aanwezig in **beide** periodes **én** met `baseline_total > 0`
- **Uitsluiting nieuwe instappers (ADR-012):** ziekenhuizen zonder baseline-data
  (`baseline_total == 0`) worden **niet** in de delta-ranking opgenomen. Hun delta
  zou vergeleken worden met de default `0.0`-score, wat statistisch misleidend is
  (bv. BONHEIDEN_IMELDA: 0 PHARMA-tickets in 2025 → baseline 0,00 → delta +5,00 door
  één goed ticket). Ze worden gelogd via `logger.info` als "nieuwe instappers".
- **Sortering:** beste delta bovenaan (descending)
- **Beperking:** max. 15 ziekenhuizen (top 7 + bottom 8 bij meer)
- **Kleur:** `FUNC_POSITIVE` = `#2e7d32` (groen) als delta > 0; `ZORGI_RED` (#dc2b26) als delta ≤ 0 — groen is bewuste uitzondering op ZORGI Design System (Optie B, semantische waarde)
- **Xlim:** `min_delta - 0.5` … `max_delta + 0.8` — exact op werkelijke data
- **Annotaties:** `clip_on=False` zodat waarden nooit afgesneden worden
- **Y-as tick-streepjes:** `length=0` — labels zichtbaar, streepjes onzichtbaar

> **📋 Backlog — toekomstige verbetering:**
> Nieuwe instappers apart tonen als een extra sectie of tabel onder de delta-ranking,
> met vermelding van hun huidige score (zonder vergelijking).
> Geregistreerd als backlog-item in `docs/01-strategisch/architectuur-beslissingen.md` (ADR-012).

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

# Noodrun bij DB-storing — CSV-fallback forceren (ADR-011)
.venv\Scripts\python.exe scripts/generate_evolution.py --pillar pharma --chart --force-csv
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
| `src/csat/utils/zorgi_theme.py` | **Golden source Python** — alle ZORGI-kleurconstanten en typografie |
| `src/csat/utils/branding.py` | Framework-theming (Plotly, Streamlit, matplotlib) — importeert uit `zorgi_theme` |
| `src/csat/config/pillars.py` | `PILLAR_REGISTRY` — kleur + naam per pijler |
| `src/csat/config/settings.py` | `AVG_SCORE_MIN` (4,0), `HIGH_CRITICAL_MAX` (15,0) |
| `src/csat/core/analysers/evolution_result.py` | Input-dataklassen |
| `src/csat/core/exporters/evolution_exporter.py` | Patroon render()/export() |
| `tests/core/test_evolution_visualiser.py` | 44 unit tests |

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
| **Totaal** | **44** | 100% coverage (`# pragma: no cover` op defensieve fallbacks) |

> Versie 44 tests: `test_subplot4_nieuwe_instappers_uitgesloten` toegevoegd (ADR-012).

---

## 8. Relatie tot andere fasen

```text
Fase 3b ──► EvolutionResult ──► Fase 3d: EvolutionVisualiser
Fase 3c ──► EvolutionExporter              │
                                           ▼
                                   evolutie-{pillar}-{jaar}.png
```

**Volgende stap:** Fase 3e — `run_monthly.py` (alles in één run)

---

## 9. Kleurarchitectuur — ZORGI Theme-laag

Alle kleurconstanten voor visualisaties volgen een **3-laagse architectuur**:

```text
PHARMA-Conventions/zorgi/zorgi_design_system.md    ← golden source (read-only)
         │
         │  (Python-representatie)
         ▼
src/csat/utils/zorgi_theme.py                      ← pure constanten, geen framework-deps
         │                                            Primaire + secundaire kleuren (Design System §2)
         │                                            Typografie (Design System §3)
         │                                            Functionele uitbreidingen (ZORGI_BORDEAUX, ...)
         │
         ├──► src/csat/utils/branding.py            ← framework-theming
         │         Plotly layout, Streamlit CSS,       importeert uit zorgi_theme
         │         matplotlib rcParams,                backward-compatible COLORS dict
         │         LOGO_ASSETS, watermark
         │
         └──► src/csat/core/exporters/              ← visualisatie-modules
                  evolution_visualiser.py              importeert rechtstreeks uit zorgi_theme
                  (toekomstige dashboards/rapporten)
```

### Regels

| Regel | Omschrijving |
|---|---|
| **Golden source** | `PHARMA-Conventions/zorgi/zorgi_design_system.md` — nooit aanpassen |
| **Read-only kopie** | `.github/docs/zorgi_design_system.md` — read-only, nooit aanpassen |
| **Python-bron** | `zorgi_theme.py` — enige plek waar hex-waarden gedefinieerd staan |
| **Framework-theming** | `branding.py` — importeert uit `zorgi_theme`, voegt Plotly/Streamlit/matplotlib toe |
| **Geen duplicatie** | Nooit hex-waarden hardcoden buiten `zorgi_theme.py` |
| **Functionele kleuren** | Uitzonderingen gedocumenteerd in `zorgi_theme.py` onder "Functionele uitbreidingen" |

### Functionele uitbreidingen (niet in officieel Design System)

| Constante | Waarde | Gebruik | Ref |
|---|---|---|---|
| `ZORGI_BORDEAUX` | `#722F37` | Drempel- en referentielijnen alle 4 subplots | ADR-012 |
| `ZORGI_LIGHT_PURPLE` | `#a06b8a` | OAZIS/care_admin pijlerkleur | PILLAR_REGISTRY |
| `ZORGI_FUNC_POSITIVE` | `#2e7d32` | Positieve delta-bars (Optie B, semantisch groen) | §4.4 Optie B |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 24/03/2026 | Initiële versie — Fase 3d compleet | Danny Depecker + GHC |
| 1.1 | 24/03/2026 | Visuele verfijning: helpers `_style_ax`, `_style_legend`, `_build_tick_labels`; rcParams override `font.weight`; GridSpec proporties; jaar geïntegreerd op x-as; jaargrens-lijn op beide bovenste subplots; spine/grid styling; xlim-beperkingen alle subplots | Danny Depecker + GHC |
| 1.2 | 25/03/2026 | ADR-011 verwerkt: satisfaction_date als datumbasis gedocumenteerd op alle 4 subplots; ZORGI Design System kleuren gecorrigeerd (subplot 1–4); rcParams §3.5 geactualiseerd (DejaVu Sans, ZORGI_BODY_TEXT); subplot 3 drempellijn ZORGI_PURPLE + altijd rood; dynamische y-as subplot 2 & 3; timestamp export; --force-csv CLI | Danny Depecker + GHC |
| 1.3 | 25/03/2026 | ADR-012 verwerkt: nieuwe instappers (baseline_total=0) uitgesloten uit delta-ranking subplot 4; backlog-noot toegevoegd voor toekomstige apart-weergave | Danny Depecker + GHC |
| 1.4 | 25/03/2026 | §9 Kleurarchitectuur toegevoegd: 3-laagse theme-structuur (zorgi_theme → branding → visualiser); §6 uitgebreid met zorgi_theme.py; testoverzicht 44 tests | Danny Depecker + GHC |
