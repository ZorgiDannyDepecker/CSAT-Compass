# CSAT-Compass - Handover Fase 3c

**Versie:** 1.0  
**Laatst bijgewerkt:** 23/03/2026  

**Doel:** Contextoverdracht voor nieuwe conversatie — start van Fase 3c (EvolutionExporter)  
**Type:** Reference  
**Auteur:** Danny Depecker + GHC  
**Status:** Compleet  

**Bestandsnaam:** handover-fase3c-2026-03-23.md  
**Path:** WIP/

---

## 1. Projectcontext

**Project:** CSAT-Compass — geautomatiseerde klanttevredenheidsanalyse voor ZORGI  
**Doel:** Maandelijkse CSAT-rapporten (NL + FR) voor 4 pijlers + ZORGI-aggregaat  
**Stack:** Python 3.13 · pandas · SQLAlchemy · Jinja2 · matplotlib · Streamlit  
**Databron:** SQL Server view `[dbo].[V_CSAT_1]` op `ZRG0014WI/Lerni_DB`  
**Repo:** `C:\Users\danndepe\Documents\AI\CSAT-Compass`

---

## 2. Alle vorige fasen — volledig afgerond ✅

### Teststand na Fase 3b

- **418 tests** — 100% coverage op alle src/ bestanden
- CI: GitHub Actions stabiel (Python 3.11 / 3.12 / 3.13)

### Fase 1 — Compleet

Hybride loader (SQL + CSV fallback), BaseAnalyser + KpiResult, PillarAnalyser, PharmaAnalyser, config (settings + pillars), export_data.py script.

### Fase 2 — Compleet

i18n NL/FR (nl.json + fr.json), Jinja2 templates, ReportExporter, maandelijkse rapporten `rapport-YYYY-MM-{lang}.md`.

### Fase 3a — Compleet

MatrixExporter, matrix-templates NL/FR (11 secties: maand + kwartaal + jaar), generate_matrix.py CLI runner.

### Fase 3b — Compleet

`EvolutionResult` dataclass + `EvolutionAnalyser` — de pure data-laag voor evolutie-analyse.

**Nieuwe bestanden:**

| Bestand | Beschrijving |
|---|---|
| `src/csat/core/analysers/evolution_result.py` | EvolutionResult dataclass + 7 helper-klassen |
| `src/csat/core/analysers/evolution_analyser.py` | EvolutionAnalyser — berekent alles |
| `src/csat/i18n/nl.json` | Uitgebreid met `evolution`-sectie |
| `src/csat/i18n/fr.json` | Uitgebreid met `evolution`-sectie (FR) |
| `tests/core/test_evolution_analyser.py` | 100 tests — 100% coverage |
| `docs/02-tactisch/fasen/fase3b-evolutie-analyser.md` | Fase-document |

---

## 3. EvolutionAnalyser — huidige interface (Fase 3b output)

```python
from csat.core.analysers import EvolutionAnalyser, EvolutionResult

analyser = EvolutionAnalyser(df, pillar_key="pharma")
result: EvolutionResult = analyser.analyse(
    baseline_periods=["2025-01", "2025-02", ..., "2025-12"],
    current_periods=["2026-01", "2026-02", "2026-03"],
    baseline_label="2025",          # optioneel
    current_label="jan-mrt 2026",   # optioneel
)
```

**EvolutionResult bevat:**

- Kerncijfers: `baseline_avg_score`, `current_avg_score`, `delta_avg_score`, `pct_positive/negative`, `hc_ratio`, `avg_response_days`, `n_hospitals`
- `monthly_timeline`: list[MonthlyDataPoint] — per maand: avg_score, total, pct_neg, fase
- `by_issue_type`: list[IssueTypeComparison] — baseline vs current per type
- `by_priority`: list[PriorityComparison] — baseline vs current per prioriteit
- `response_time_by_score`: dict[int, ResponseTimeRow] — responstijd per score-niveau (1-5)
- `hospital_comparison`: list[HospitalComparison] — per ziekenhuis
- `hospitals_disappeared` / `hospitals_new`: list[str]
- `negative_themes`: list[ThemeEvolution] — keyword-matching op `comment` (score ≤ 2)
- `kpi_status`: dict[str, KpiStatus] — OK / WARNING / AT_RISK / UNKNOWN
- `trend_is_structural`: bool — True als delta ≥ 0,5
- `trend_breadth`: str — "breed" / "beperkt" / "gemengd"

---

## 4. Fase 3c — te starten

**Doel:** `EvolutionExporter` — genereert `evolutie-YYYY-nl.md` + `evolutie-YYYY-fr.md` uit een `EvolutionResult`  
**T-shirt:** L (24–48u) — UX, conditionele templates, executive summary, tweetaligheid  
**Document:** `docs/02-tactisch/fasen/fase3c-evolution-exporter.md` — aan te maken bij start

### Referentie-output

`WIP/Tendens_Vergelijkingsmatrix.md` — de bestaande Claude-output die CSAT-Compass moet **vervangen**.  
Dit is de gewenste output voor Fase 3c templates.

### Deliverables Fase 3c

| Component | Bestand | Beschrijving |
|---|---|---|
| Jinja2 templates NL | `docs/templates/evolutie-nl.j2` | Nederlandstalig template |
| Jinja2 templates FR | `docs/templates/evolutie-fr.j2` | Franstalig template |
| EvolutionExporter | `src/csat/core/exporters/evolution_exporter.py` | Genereert twee .md bestanden |
| CLI runner | `scripts/generate_evolution.py` | `--from YYYY-MM --to YYYY-MM --pillar pharma` |
| Tests | `tests/core/test_evolution_exporter.py` | Doel: 100% coverage |
| Fase 3c-document | `docs/02-tactisch/fasen/fase3c-evolution-exporter.md` | Aan te maken bij start |

### Bestandsnaamconventie output

| Versie | Patroon | Voorbeeld |
|---|---|---|
| Nederlands | `evolutie-YYYY-nl.md` | `evolutie-2026-nl.md` |
| Frans | `evolutie-YYYY-fr.md` | `evolutie-2026-fr.md` |

### Templatestructuur (9 secties)

| Sectie | Inhoud | EvolutionResult-velden |
|---|---|---|
| 1 | Kerncijfers + delta | `baseline/current_avg_score`, `delta_avg_score`, `pct_positive/negative` |
| 2 | Maandelijkse tijdlijn | `monthly_timeline` |
| 3 | KPI-status overzicht | `kpi_status`, `hc_ratio` |
| 4 | Vergelijking per issue type | `by_issue_type` |
| 5 | Vergelijking per prioriteit + responstijd | `by_priority`, `response_time_by_score` |
| 6 | Trend classificatie | `trend_is_structural`, `trend_breadth` |
| 7 | Ziekenhuisvergelijking | `hospital_comparison`, `disappeared/new` |
| 8 | Negatieve feedbackthema's | `negative_themes` |
| 9 | Executive summary + aanbevelingen | Conditionele narratief op basis van KPI's + trend |

### Executive summary — conditionele logica (sectie 9)

De EvolutionExporter genereert een **narratief** op basis van de data — geen vaste tekst:

```text
Als delta >= +0,5 EN trend_breadth == "breed":
    → "Structurele verbetering over {n} ziekenhuizen — positief signaal voor..."
Als current_avg_score < 4,0 EN trend_is_structural == False:
    → "Aandacht vereist: huidige score ({current_avg_score}) onder drempel..."
Als hospitals_disappeared niet leeg:
    → "Let op: {n} ziekenhuis/ziekenhuizen heeft/hebben geen tickets meer ingediend..."
```

---

## 5. Technische context

### Virtuele omgeving activeren

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\activate
```

### Tests draaien

```powershell
.venv\Scripts\python.exe -m pytest --tb=short
# Verwacht: 418 passed, coverage 100%
```

### Lint uitvoeren

```powershell
.\tools\lint.ps1
# Ruff + mypy clean op nieuwe Fase 3b bestanden
# Bekende pre-existente mypy-fout in matrix_exporter.py (uit Fase 3a — niet in scope)
```

### Bestaande exporters als referentie

| Bestand | Patroon | Gebruik |
|---|---|---|
| `src/csat/core/exporters/report_exporter.py` | ReportExporter | Template-structuur kopiëren |
| `src/csat/core/exporters/matrix_exporter.py` | MatrixExporter | Multi-sectie template-logica |
| `docs/templates/rapport-nl.j2` | Jinja2 NL template | Stijl en opmaak navolgen |
| `docs/templates/rapport-fr.j2` | Jinja2 FR template | Stijl en opmaak navolgen |

### Data beschikbaar voor testen

```powershell
$env:CSAT_CSV_FALLBACK_PATH = "C:\Users\danndepe\Documents\AI\CSAT-Compass\output"
# Bestanden: v_csat_1_2025-heden.csv, v_csat_1_2025.csv, v_csat_1_volledig.csv
```

---

## 6. ADR-beslissingen die Fase 3c beïnvloeden

| ADR | Beslissing | Impact op Fase 3c |
|---|---|---|
| ADR-006 | Reactiegraad N/A | Niet renderen in templates |
| ADR-007 | ANALYSE_START_DATE = 2025-01-01 | Baseline-disclaimer toevoegen in sectie 1 |
| ADR-009 | AVG_SCORE_MIN = 4,00 | KPI-status kleuren in templates |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 23/03/2026 | Initiële versie — handover voor Fase 3c | Danny Depecker + GHC |

