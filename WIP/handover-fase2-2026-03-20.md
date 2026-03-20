# CSAT-Compass - Handover Fase 2

**Versie:** 1.0  
**Laatst bijgewerkt:** 20/03/2026

**Doel:** Contextoverdracht voor nieuwe conversatie — start van Fase 2  
**Type:** Reference  
**Auteur:** GHC  
**Status:** Draft

**Bestandsnaam:** handover-fase2-2026-03-20.md  
**Path:** WIP/

---

## 1. Projectcontext

**Project:** CSAT-Compass — geautomatiseerde klanttevredenheidsanalyse voor ZORGI  
**Doel:** Maandelijkse CSAT-rapporten (NL + FR) voor 4 pijlers + ZORGI-aggregaat  
**Stack:** Python 3.13 · pandas · SQLAlchemy · Jinja2 · Streamlit · WeasyPrint  
**Databron:** SQL Server view `[dbo].[V_CSAT_1]` op `ZRG0014WI/Lerni_DB`  
**Repo:** `C:\Users\danndepe\Documents\AI\CSAT-Compass`  
**Laatste commit:** `e86ca31` — test: ADR-007 coverage, ONBEKEND hospital, avg score threshold + lint exit fix

---

## 2. Fase 1 — volledig afgerond ✅

### Wat is opgeleverd

| Component | Bestand | Status |
|---|---|---|
| Abstracte loader | `src/csat/core/loaders/base_loader.py` | ✅ |
| SQL-loader | `src/csat/core/loaders/sql_loader.py` | ✅ |
| CSV-loader | `src/csat/core/loaders/csv_loader.py` | ✅ |
| Loader factory | `src/csat/core/loaders/__init__.py` | ✅ |
| Base-analyser | `src/csat/core/analysers/base_analyser.py` | ✅ |
| Pijler-analyser | `src/csat/core/analysers/pillar_analyser.py` | ✅ |
| PHARMA config | `src/csat/pillars/pharma/config.py` | ✅ |
| PHARMA analyser | `src/csat/pillars/pharma/analyser.py` | ✅ |
| Instellingen | `src/csat/config/settings.py` | ✅ |
| Pijler-definities | `src/csat/config/pillars.py` | ✅ |
| Logger | `src/csat/utils/logger.py` | ✅ |
| Datumhulpfuncties | `src/csat/utils/date_utils.py` | ✅ |
| Branding | `src/csat/utils/branding.py` | ✅ |
| Export script | `scripts/export_data.py` | ✅ |
| Unit tests | `tests/` — 151 tests, 100% coverage | ✅ |

### Live DB-validatie (20/03/2026)

- 6.000 tickets in V_CSAT_1
- 854 PHARMA-tickets — 64 ziekenhuizen (9 met NULL hospital → ONBEKEND)
- Score-bereik: 1–5 (integer)
- Filterkolom: `product_domain` (bevestigd)
- Prioriteitsschaal: Blocker > Critical > Major > Minor > Trivial
- Reactiegraad: N/A — view bevat enkel gescoorde tickets (ADR-006)

### Architectuurbeslissingen (ADR-001 t/m ADR-007)

| ADR | Beslissing |
|---|---|
| ADR-001 | Hybride databron: SQL primair, CSV fallback |
| ADR-002 | Streamlit als dashboard |
| ADR-003 | Jinja2 + i18n JSON voor NL/FR tweetaligheid |
| ADR-004 | Selectieve migratie vanuit Customer Satisfaction |
| ADR-005 | PHARMA-first ontwikkelingsstrategie |
| ADR-006 | Reactiegraad KPI N/A — view is pre-gefilterd op gescoorde tickets |
| ADR-007 | ANALYSE_START_DATE = 2025-01-01 · NULL hospitals = ONBEKEND |

### KPI-status PHARMA

| KPI | Drempel | Status |
|---|---|---|
| High/Critical ratio | ≤ 15% | ✅ Actief |
| Gemiddelde CSAT-score | TBD | ⚠️ Te bepalen met PHARMA-team |
| Reactiegraad | N/A | ❌ Niet meetbaar (ADR-006) |
| Trend MoM | Informatief | ✅ Berekend |

---

## 3. Fase 2 — te starten

**Doel:** Jinja2-templates + i18n NL/FR → maandelijkse markdown/PDF-rapporten genereren  
**T-shirt:** M (8–24u)  
**Document:** `docs/02-tactisch/fasen/fase2-rapportage.md` — nog aan te maken

### Deliverables Fase 2

| Component | Bestand | Beschrijving |
|---|---|---|
| i18n NL | `src/csat/i18n/nl.json` | Nederlandse labels en teksten |
| i18n FR | `src/csat/i18n/fr.json` | Franse labels en teksten |
| Rapport-template NL | `docs/templates/rapport-nl.md.j2` | Jinja2-template NL |
| Rapport-template FR | `docs/templates/rapport-fr.md.j2` | Jinja2-template FR |
| Report exporter | `src/csat/core/exporters/report_exporter.py` | Genereert rapport vanuit KpiResult |
| Output NL | `output/rapport-YYYY-MM-nl.md` | Nederlandstalig rapport |
| Output FR | `output/rapport-YYYY-MM-fr.md` | Franstalig rapport |
| Tests | `tests/core/test_report_exporter.py` | Unit tests exporter |

### Bestandsnaamconventie rapporten

| Versie | Patroon | Voorbeeld |
|---|---|---|
| Nederlands | `rapport-YYYY-MM-nl.md` | `rapport-2026-03-nl.md` |
| Frans | `rapport-YYYY-MM-fr.md` | `rapport-2026-03-fr.md` |

---

## 4. Open punten voor Fase 2

| Punt | Prioriteit | Beschrijving |
|---|---|---|
| AVG_SCORE_MIN | 🔴 Hoog | Drempelwaarde bepalen met PHARMA-team voor gemiddelde score |
| NULL hospitals | 🟡 Medium | 9 tickets zonder ziekenhuisnaam — opvolgen met PHARMA-team (data-kwaliteit) |
| fase2-rapportage.md | 🔴 Hoog | Fase 2-plandocument nog aan te maken |

---

## 5. Technische context

### Virtuele omgeving

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\activate
```

### Tests draaien

```powershell
.venv\Scripts\python.exe -m pytest --tb=short
# Verwacht: 151 passed, coverage 100%
```

### Lint uitvoeren

```powershell
.\tools\lint.ps1
# Verwacht: EXIT CODE 0 — alle checks geslaagd
```

### Data exporteren

```powershell
# 2025 + 2026 tot vandaag (meest gebruikt voor analyse)
.venv\Scripts\python.exe scripts/export_data.py --since 2025
# Output: output/v_csat_1_2025-heden.csv (2.188 rijen)
```

### Mapstructuur (relevant voor Fase 2)

```text
src/csat/
├── core/exporters/report_exporter.py   ← implementeren in Fase 2
├── i18n/                               ← nl.json + fr.json aanmaken
│   └── __init__.py
docs/
├── templates/                          ← Jinja2-templates aanmaken
output/
├── v_csat_1_2025-heden.csv            ← beschikbaar als referentiedata
```

---

## 6. Codecov

- URL: https://app.codecov.io/
- Token: ingesteld als GitHub secret `CODECOV_TOKEN`
- Badge actief na elke push naar master
- Doel: ≥ 95% coverage (huidig: 100%)

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 20/03/2026 | Initiële versie | GHC |

