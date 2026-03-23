# CSAT-Compass - Handover Fase 3

**Versie:** 1.0  
**Laatst bijgewerkt:** 22/03/2026  

**Doel:** Contextoverdracht voor nieuwe conversatie — start van Fase 3  
**Type:** Reference  
**Auteur:** GHC  
**Status:** Draft  

**Bestandsnaam:** handover-fase3-2026-03-22.md  
**Path:** WIP/

---

## 1. Projectcontext

**Project:** CSAT-Compass — geautomatiseerde klanttevredenheidsanalyse voor ZORGI  
**Doel:** Maandelijkse CSAT-rapporten (NL + FR) voor 4 pijlers + ZORGI-aggregaat  
**Stack:** Python 3.13 · pandas · SQLAlchemy · Jinja2 · Streamlit · WeasyPrint  
**Databron:** SQL Server view `[dbo].[V_CSAT_1]` op `ZRG0014WI/Lerni_DB`  
**Repo:** `C:\Users\danndepe\Documents\AI\CSAT-Compass`  
**Laatste commit:** `457afa1` — feat: set AVG_SCORE_MIN threshold to 4.0 (ADR-009)

---

## 2. Fase 1 en Fase 2 — volledig afgerond ✅

### Fase 1 — afgerond 20/03/2026

| Component | Bestand | Status |
|---|---|---|
| Abstracte loader | `src/csat/core/loaders/base_loader.py` | ✅ |
| SQL-loader | `src/csat/core/loaders/sql_loader.py` | ✅ |
| CSV-loader | `src/csat/core/loaders/csv_loader.py` | ✅ |
| Base-analyser + KpiResult | `src/csat/core/analysers/base_analyser.py` | ✅ |
| Pijler-analyser | `src/csat/core/analysers/pillar_analyser.py` | ✅ |
| PHARMA config + analyser | `src/csat/pillars/pharma/` | ✅ |
| Instellingen | `src/csat/config/settings.py` | ✅ |
| Pijler-definities | `src/csat/config/pillars.py` | ✅ |
| Export script | `scripts/export_data.py` | ✅ |
| Tests Fase 1 | `tests/` — 151 tests, 100% coverage | ✅ |

### Fase 2 — afgerond 22/03/2026

| Component | Bestand | Status |
|---|---|---|
| i18n NL | `src/csat/i18n/nl.json` | ✅ |
| i18n FR | `src/csat/i18n/fr.json` | ✅ |
| Rapport-template NL | `docs/templates/rapport-nl.md.j2` | ✅ |
| Rapport-template FR | `docs/templates/rapport-fr.md.j2` | ✅ |
| ReportExporter | `src/csat/core/exporters/report_exporter.py` | ✅ |
| Tests Fase 2 | `tests/core/test_report_exporter.py` | ✅ |
| ADR-008 mapstructuur | `docs/01-strategisch/architectuur-beslissingen.md` | ✅ |
| ADR-009 AVG_SCORE_MIN | `docs/01-strategisch/architectuur-beslissingen.md` | ✅ |

### Teststand na Fase 2

- **218 tests** — 100% coverage
- CI: GitHub Actions stabiel (Python 3.11 / 3.12 / 3.13)
- Codecov: badge actief

### KPI-status PHARMA — definitief na Fase 2

| KPI | Drempel | Status |
|---|---|---|
| High/Critical ratio | ≤ 15% | ✅ Actief |
| Gemiddelde CSAT-score | ≥ 4,00 | ✅ Actief (ADR-009) |
| Reactiegraad | N/A | ❌ Niet meetbaar (ADR-006) |
| Trend MoM | Informatief | ✅ Berekend |

### Live PHARMA-data (productie, 22/03/2026)

| Periode | Tickets | Gem. score | H/C % | Status |
|---|---|---|---|---|
| Januari 2026 | 25 | 4,36 | 40,0% | ✅ Boven drempel |
| Februari 2026 | 21 | 4,33 | 42,9% | ✅ Boven drempel |
| Maart 2026 (YTD) | 20 | 4,60 | 55,0% | ✅ Boven drempel |

> ⚠️ H/C-ratio is structureel hoog (40–55%) — aandachtspunt voor Fase 3-matrices en latere rapportage aan leadership.

---

## 3. Architectuurbeslissingen — volledig overzicht

| ADR | Beslissing | Status |
|---|---|---|
| ADR-001 | Hybride databron: SQL primair, CSV fallback | ✅ |
| ADR-002 | Streamlit als dashboard | ✅ |
| ADR-003 | Jinja2 + i18n JSON voor NL/FR tweetaligheid | ✅ |
| ADR-004 | Selectieve migratie vanuit Customer Satisfaction | ✅ |
| ADR-005 | PHARMA-first ontwikkelingsstrategie | ✅ |
| ADR-006 | Reactiegraad KPI N/A — view is pre-gefilterd | ✅ |
| ADR-007 | ANALYSE_START_DATE = 2025-01-01 · NULL hospitals = ONBEKEND | ✅ |
| ADR-008 | Mapstructuur: src/ = library · scripts/ = runners · tools/ = dev | ✅ |
| ADR-009 | AVG_SCORE_MIN = 4,00 — configureerbaar via env | ✅ |

---

## 4. Fase 3 — te starten

**Doel:** MatrixExporter — vergelijkingsmatrices per pijler over meerdere periodes  
**T-shirt:** S (4–8u)  
**Afhankelijkheden:** Fase 1 (KpiResult) + Fase 2 (i18n, Jinja2-infrastructuur)  
**Document:** `docs/02-tactisch/fasen/fase3-matrix.md` — nog aan te maken

### Wat is een matrix?

Een matrix is een overzichtstabel over **meerdere periodes tegelijk** — ter aanvulling op het maandrapport (dat één periode toont). Doel: trends en uitschieters in één oogopslag tonen aan leadership.

### Deliverables Fase 3

| Component | Bestand | Beschrijving |
|---|---|---|
| MatrixExporter | `src/csat/core/exporters/matrix_exporter.py` | Genereert matrix vanuit lijst van KpiResult |
| Matrix-template NL | `docs/templates/matrix-nl.md.j2` | Jinja2-template NL |
| Matrix-template FR | `docs/templates/matrix-fr.md.j2` | Jinja2-template FR |
| i18n uitbreiding NL | `src/csat/i18n/nl.json` | Matrix-labels toevoegen |
| i18n uitbreiding FR | `src/csat/i18n/fr.json` | Matrix-labels toevoegen |
| Output NL | `output/matrix-YYYY-nl.md` | Nederlandstalige matrix |
| Output FR | `output/matrix-YYYY-fr.md` | Franstalige matrix |
| Tests | `tests/core/test_matrix_exporter.py` | Unit tests — doel: 100% coverage |
| Fase 3-plandocument | `docs/02-tactisch/fasen/fase3-matrix.md` | Aan te maken bij start |

> ⚠️ `matrix_exporter.py` en `dashboard_exporter.py` bestaan al als **lege placeholders** — enkel implementeren, niet hernoemen.

### Inhoud van de matrix (5 secties)

| # | Sectie | Beschrijving |
|---|---|---|
| 1 | Overzicht gemiddelde score | Hospitals (rijen) × periodes (kolommen) — gem. score per cel |
| 2 | H/C-ratio overzicht | Hospitals (rijen) × periodes (kolommen) — H/C % per cel |
| 3 | Ticketvolume | Hospitals (rijen) × periodes (kolommen) — aantal tickets per cel |
| 4 | Top/bottom performers | Ranking ziekenhuizen op gemiddelde score over alle periodes |
| 5 | Trend samenvatting | MoM-evolutie per ziekenhuis — stijging / stabiel / daling |

### Bestandsnaamconventie matrices

| Versie | Patroon | Voorbeeld |
|---|---|---|
| Nederlands | `matrix-YYYY-nl.md` | `matrix-2026-nl.md` |
| Frans | `matrix-YYYY-fr.md` | `matrix-2026-fr.md` |

### Interface MatrixExporter

```python
# Verwachte interface — ter illustratie, niet bindend
from csat.core.exporters import MatrixExporter

exporter = MatrixExporter(lang="nl")
exporter.export(results=[kpi_jan, kpi_feb, kpi_mrt])
# → output/matrix-2026-nl.md
```

- **Input:** `list[KpiResult]` — meerdere periodes van dezelfde pijler
- **Output:** `output/matrix-YYYY-{lang}.md`
- **Patroon:** volgt `ReportExporter` — zelfde `__init__`, `render()`, `export()` structuur

---

## 5. Open punten voor Fase 3

| Punt | Prioriteit | Beschrijving |
|---|---|---|
| NULL hospitals communicatie | 🟡 Medium | 9 tickets pre-2025, gefilterd door ANALYSE_START_DATE — geen technische actie, wel communiceren naar PHARMA-team |
| `implementatie-gids.md` update | 🟡 Medium | Fase 2 → Compleet, Fase 3 → In Progress |
| `project-journal.md` update | 🟢 Laag | Sessie 22/03/2026 toevoegen |

---

## 6. Technische context

### Virtuele omgeving activeren

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\activate
```

### Tests draaien

```powershell
.venv\Scripts\python.exe -m pytest --tb=short
# Verwacht: 218 passed, coverage 100%
```

### Lint uitvoeren

```powershell
.\tools\lint.ps1
# Verwacht: EXIT CODE 0 — alle checks geslaagd
```

### Data exporteren

```powershell
.venv\Scripts\python.exe scripts/export_data.py --since 2025
# Output: output/v_csat_1_2025-heden.csv
```

### Relevante mapstructuur voor Fase 3

```text
src/csat/
├── core/exporters/
│   ├── report_exporter.py      ← Fase 2 — referentie voor MatrixExporter
│   ├── matrix_exporter.py      ← Fase 3 — lege placeholder, hier implementeren
│   └── dashboard_exporter.py   ← Fase 5 — nog niet aanraken
├── i18n/
│   ├── nl.json                 ← matrix-labels toevoegen
│   └── fr.json                 ← matrix-labels toevoegen
docs/
├── templates/
│   ├── rapport-nl.md.j2        ← Fase 2 — referentie voor matrix-templates
│   ├── matrix-nl.md.j2         ← Fase 3 — nog aan te maken
│   └── matrix-fr.md.j2         ← Fase 3 — nog aan te maken
tests/
└── core/
    ├── test_report_exporter.py ← Fase 2 — referentie voor test-structuur
    └── test_matrix_exporter.py ← Fase 3 — nog aan te maken
```

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 22/03/2026 | Initiële versie | GHC |

