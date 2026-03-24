nda# CSAT-Compass - Handover Fase 3d + 3e

**Versie:** 1.0  
**Laatst bijgewerkt:** 23/03/2026  

**Doel:** Contextoverdracht voor nieuwe conversatie — Fase 3d (Matplotlib visualisaties) + Fase 3e (run_monthly)  
**Type:** Reference  
**Auteur:** Danny Depecker + GHC  
**Status:** Approved  

**Bestandsnaam:** handover-fase3d-2026-03-23.md  
**Path:** WIP/

---

## 1. Projectcontext

**Project:** CSAT-Compass — geautomatiseerde klanttevredenheidsanalyse voor ZORGI  
**Doel:** Maandelijkse CSAT-rapporten (NL + FR) voor 4 pijlers + ZORGI-aggregaat  
**Stack:** Python 3.13 · pandas · SQLAlchemy · Jinja2 · matplotlib · Streamlit  
**Databron:** SQL Server view `[dbo].[V_CSAT_1]` op `ZRG0014WI/Lerni_DB`  
**Repo:** `C:\Users\danndepe\Documents\AI\CSAT-Compass`

### Omgeving activeren

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\activate
.venv\Scripts\python.exe -m pytest --no-cov   # verwacht: 472 passed
```

---

## 2. Alle voltooide fasen

**Teststand:** 472 tests — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

| Fase | Inhoud | Status |
|---|---|---|
| Fase 1 | Hybride loader · BaseAnalyser · PillarAnalyser · config | ✅ Compleet |
| Fase 2 | i18n NL/FR · Jinja2 templates · ReportExporter | ✅ Compleet |
| Fase 3a | MatrixExporter · matrix-templates NL/FR · generate_matrix.py | ✅ Compleet |
| Fase 3b | EvolutionResult dataclass · EvolutionAnalyser (data-laag) | ✅ Compleet |
| Fase 3c | EvolutionExporter · templates NL/FR · CLI runners | ✅ Compleet |

### Fase 3b — sleutelbestanden

| Bestand | Beschrijving |
|---|---|
| `src/csat/core/analysers/evolution_result.py` | EvolutionResult + 7 helper-klassen + KpiStatus enum |
| `src/csat/core/analysers/evolution_analyser.py` | EvolutionAnalyser — volledige data-laag |
| `src/csat/core/analysers/__init__.py` | Exports voor alle nieuwe klassen |
| `src/csat/i18n/nl.json` | Uitgebreid met `evolution`-sectie |
| `src/csat/i18n/fr.json` | Uitgebreid met `evolution`-sectie (FR) |
| `tests/core/test_evolution_analyser.py` | 100 tests — 100% coverage |
| `tests/conftest.py` | `evolution_df` fixture toegevoegd |

### Fase 3c — sleutelbestanden

| Bestand | Beschrijving |
|---|---|
| `src/csat/core/exporters/evolution_exporter.py` | EvolutionExporter — render() + export() |
| `docs/templates/evolutie-nl.md.j2` | Jinja2 template NL — 8 secties + conditionele conclusie |
| `docs/templates/evolutie-fr.md.j2` | Jinja2 template FR — idem |
| `scripts/generate_evolution.py` | CLI per pijler: `--pillar`, `--baseline`, `--current`, `--lang` |
| `scripts/generate_all_evolutions.py` | Batch: genereert NL + FR voor alle 5 pijlers in één run |
| `WIP/preview_evolution.py` | Terminal preview (kleurig, geen bestandsschrijving) |
| `tests/core/test_evolution_exporter.py` | 54 tests — 100% coverage |

### Bestandsnaamconventie output

```
evolutie-{pillar}-{jaar}-{lang}.md    bv. evolutie-pharma-2026-nl.md
```

> ⚠️ In `/output/` staan twee stale bestanden `evolutie-2026-nl.md` + `evolutie-2026-fr.md`
> (aangemaakt vóór de pillar-naamfix). Kunnen verwijderd worden.

### Resultaten alle pijlers (baseline 2025 volledig, current jan-mrt 2026)

| Pijler | Baseline avg | Huidig avg | Delta | Trend |
|---|---|---|---|---|
| ZORGI totaal | 4,08 | 4,66 | +0,58 | Structureel · Breed |
| PHARMA | 3,51 | 4,43 | +0,92 | Structureel · Gemengd |
| CARE | 4,36 | 4,76 | +0,40 | Onduidelijk · Gemengd |
| OAZIS | 4,25 | 4,71 | +0,46 | Onduidelijk · Breed |
| ERP4HC²·⁰ | 3,70 | 4,58 | +0,88 | Structureel · Breed |

---

## 3. EvolutionResult — interface (input voor Fase 3d)

```python
from csat.core.analysers import EvolutionAnalyser, EvolutionResult

analyser = EvolutionAnalyser(df, pillar_key="pharma")
result: EvolutionResult = analyser.analyse(
    baseline_periods=["2025-01", ..., "2025-12"],
    current_periods=["2026-01", "2026-02", "2026-03"],
)
```

### Velden relevant voor visualisaties

| Veld | Type | Gebruik in grafiek |
|---|---|---|
| `pillar` | str | Titel + kleur opzoeken in PILLAR_REGISTRY |
| `baseline_label` | str | Legende |
| `current_label` | str | Legende |
| `monthly_timeline` | list[MonthlyDataPoint] | Subplot 1 (score) + Subplot 2 (pct_neg) |
| `hospital_comparison` | list[HospitalComparison] | Subplot 4 (delta per ziekenhuis) |
| `baseline_hc_ratio` / `current_hc_ratio` | float | Subplot 3 referentie |
| `delta_avg_score` | float | Annotatie in titel |
| `trend_is_structural` | bool | Kleur/icoon in figuur-titel |

```python
@dataclass
class MonthlyDataPoint:
    period: str          # "YYYY-MM" — X-as
    avg_score: float     # subplot 1 — lijndiagram
    pct_negative: float  # subplot 2 — staafdiagram
    total_tickets: int
    fase: str            # "H1 2025" / "H2 2025" / "H1 2026" — kleurgroep
```

### Pijlerkleuren (ZORGI Design System — ADR-010)

```python
from csat.config.pillars import PILLAR_REGISTRY
kleur = PILLAR_REGISTRY["pharma"]["color"]  # "#609fce"
```

| Pijler | HEX | Naam |
|---|---|---|
| zorgi | `#003a70` | Dark Blue |
| pharma | `#609fce` | Light Blue |
| care | `#5f8495` | Grey Blue |
| care_admin | `#a06b8a` | Light Purple |
| erp4hc | `#7f4267` | Purple |

> ❌ Rood (`#dc2b26`) is **gereserveerd** voor alarmen/trend-down — nooit als pijlerkleur.

---

## 4. Fase 3d — te implementeren: Matplotlib visualisaties

**T-shirt:** M (8–24u)  
**Document:** `docs/02-tactisch/fasen/fase3d-evolutie-visualisatie.md` — aan te maken bij start

### Deliverables

| Component | Bestand | Beschrijving |
|---|---|---|
| EvolutionVisualiser | `src/csat/core/exporters/evolution_visualiser.py` | 4-subplot PNG via matplotlib |
| CLI update | `scripts/generate_evolution.py` | `--chart` vlag toevoegen |
| CLI update | `scripts/generate_all_evolutions.py` | `--chart` vlag doorgeven |
| Tests | `tests/core/test_evolution_visualiser.py` | Doel: 100% coverage |
| Fase-document | `docs/02-tactisch/fasen/fase3d-evolutie-visualisatie.md` | Aan te maken bij start |

### Bestandsnaamconventie output

```
evolutie-{pillar}-{jaar}.png    bv. evolutie-pharma-2026.png
```

Taalversie-onafhankelijk — één PNG per pijler.

### 4-subplot structuur

```
┌──────────────────────────────────────────────────────────┐
│  CSAT-Compass — ZORGI PHARMA  |  2025 → jan-mrt 2026    │
├────────────────────────┬─────────────────────────────────┤
│  Subplot 1             │  Subplot 2                      │
│  Maandelijkse score    │  % Negatief per maand           │
│  Lijndiagram           │  Staafdiagram                   │
│  baseline vs huidig    │  rood > 15%, pijlerkleur ≤ 15%  │
├────────────────────────┼─────────────────────────────────┤
│  Subplot 3             │  Subplot 4                      │
│  HC-ratio per maand    │  Top/bottom ziekenhuizen        │
│  Staafdiagram          │  Horizontaal, gesorteerd delta  │
│  drempellijn 15%       │  max. 15 ziekenhuizen           │
└────────────────────────┴─────────────────────────────────┘
```

### Subplot-specificaties

**Subplot 1 — maandelijkse score-evolutie (lijndiagram)**
- X-as: `monthly_timeline[].period`
- Y-as: `avg_score` (bereik 0–5, vaste schaal)
- Lijn baseline: pijlerkleur, opacity 0.5, gestippeld
- Lijn huidig: pijlerkleur, vol
- Horizontale drempellijn: `AVG_SCORE_MIN` (4.0), grijs gestippeld
- Verticale scheidingslijn tussen laatste baseline-maand en eerste current-maand

**Subplot 2 — % negatief per maand (staafdiagram)**
- X-as: periodes
- Y-as: `pct_negative` (0–100%)
- Kleur: `#dc2b26` (rood) als > 15%, pijlerkleur als ≤ 15%
- Baseline en current als aparte groepen met gap ertussen

**Subplot 3 — HC-ratio (staafdiagram)**
- X-as: periodes (samengevoegd baseline + current)
- Y-as: HC-ratio (0–100%)
- Drempellijn: `HIGH_CRITICAL_MAX` (15.0%), oranje gestippeld
- Boven drempel: rood; onder: pijlerkleur

**Subplot 4 — top/bottom ziekenhuizen (horizontale balk)**
- Enkel ziekenhuizen in **beide** periodes (`h.current_score is not None`)
- Gesorteerd op delta (beste bovenaan)
- Groen (`#00aa44`) als delta > 0, rood (`#dc2b26`) als delta < 0
- Max. 15 ziekenhuizen

### Interface

```python
class EvolutionVisualiser:
    def __init__(self, result: EvolutionResult) -> None: ...

    def render(self) -> plt.Figure:
        """Retourneert matplotlib Figure — geen bestandsschrijving."""

    def export(self, output_path: Path, year: str | None = None) -> Path:
        """Schrijft PNG → output_path/evolutie-{pillar}-{jaar}.png"""
```

### Stijlregels (ZORGI Design System)

- **Fonts:** `apply_matplotlib_theme()` in `src/csat/utils/branding.py` → Poppins/Verdana
- **Achtergrond:** `#d7e7f3` (Ultra Light Blue) als figuurachtergrond
- **DPI:** 150 voor scherm, 300 voor PDF
- **Formaat:** 14×10 inch (A4 landscape ratio)
- **Gridlijnen:** licht grijs, opacity 0.3
- Referentie branding: `src/csat/utils/branding.py`, `src/csat/config/pillars.py`

### Testpatroon (navolgen van test_evolution_exporter.py)

```python
from unittest.mock import patch
import matplotlib.pyplot as plt

def test_render_retourneert_figure(evolution_result):
    vis = EvolutionVisualiser(evolution_result)
    fig = vis.render()
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_export_schrijft_png(evolution_result, tmp_path):
    vis = EvolutionVisualiser(evolution_result)
    pad = vis.export(tmp_path, year="2026")
    assert pad.exists()
    assert pad.suffix == ".png"
    assert pad.name == "evolutie-pharma-2026.png"
```

---

## 5. Fase 3e — te implementeren: run_monthly.py

**T-shirt:** S (4–8u)  
**Reden:** Niet in oorspronkelijke planning — logische aanvulling, combineert alle bestaande generators

### Deliverables

| Component | Bestand | Beschrijving |
|---|---|---|
| Batch runner | `scripts/run_monthly.py` | Genereert alles voor één maand |

### Interface

```powershell
# Standaard: automatisch vorige maand, alle pijlers
.venv\Scripts\python.exe scripts/run_monthly.py

# Specifieke maand
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03

# Specifieke pijlers
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --pillar pharma care

# Zonder visualisaties (vóór Fase 3d)
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --no-charts
```

### Volgorde uitvoering

```
1. generate_matrix.py          --from {begin_jaar} --to {maand}
2. generate_all_evolutions.py  --baseline {vorig_jaar}-01 {vorig_jaar}-12
                               --current {begin_jaar}-01 {maand}
3. (na Fase 3d) visualisaties  --chart per pijler
```

### Verwachte output per maandelijkse run (bv. --month 2026-03)

```
output/
  matrix-2026-nl.md / -fr.md
  evolutie-zorgi-2026-nl.md / -fr.md
  evolutie-pharma-2026-nl.md / -fr.md
  evolutie-care-2026-nl.md / -fr.md
  evolutie-care_admin-2026-nl.md / -fr.md
  evolutie-erp4hc-2026-nl.md / -fr.md
  evolutie-pharma-2026.png          ← na Fase 3d
  evolutie-care-2026.png            ← na Fase 3d
  ...
```

> ⚠️ Noot: de huidige `ReportExporter` genereert rapporten zonder pijlernaam
> (`rapport-2026-01-nl.md`). Uitlijnen naar `rapport-YYYY-MM-{pillar}-{lang}.md`
> conform projectplan sectie 3.1 is een kleine cleanup voor Fase 3e of later.

---

## 6. Fasering na 3d + 3e

| Fase | Inhoud | T-shirt | Status |
|---|---|---|---|
| **3d** | Matplotlib 4-subplot visualisaties | M | **Volgende** |
| **3e** | run_monthly.py — alles in één run | S | Daarna |
| Fase 4 | CARE / OAZIS / ERP4HC pijlerspecifieke config | M | ⏳ |
| Fase 5 | Streamlit dashboard NL/FR | L | ⏳ |
| Fase 6 | ZORGI-aggregatie | S | ⏳ |

---

## 7. Referentiebestanden voor Fase 3d

| Bestand | Relevantie |
|---|---|
| `src/csat/utils/branding.py` | `apply_matplotlib_theme()`, ZORGI-kleuren, LOGO_ASSETS |
| `src/csat/config/pillars.py` | `PILLAR_REGISTRY` — kleur + naam per pijler |
| `src/csat/config/settings.py` | `AVG_SCORE_MIN` (4.0), `HIGH_CRITICAL_MAX` (15.0), `OUTPUT_PATH` |
| `src/csat/core/analysers/evolution_result.py` | Input-dataklassen voor visualiser |
| `src/csat/core/exporters/evolution_exporter.py` | Patroon render() / export() navolgen |
| `tests/core/test_evolution_exporter.py` | Testpatroon navolgen |
| `tests/conftest.py` | `evolution_df` fixture beschikbaar voor tests |

### Data voor testen

```powershell
$env:CSAT_CSV_FALLBACK_PATH = "output"
# v_csat_1_2025-heden.csv aanwezig in output/ — meest volledig

# Snel de data controleren via preview:
.venv\Scripts\python.exe WIP/preview_evolution.py --pillar pharma --baseline 2025-01 2025-12 --current 2026-01 2026-03
```

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 23/03/2026 | Initiële versie — handover Fase 3d + 3e | Danny Depecker + GHC |

