# CSAT-Compass - Fase 3b: EvolutionAnalyser

**Versie:** 1.0  
**Laatst bijgewerkt:** 23/03/2026  

**Doel:** Implementatiebeschrijving van de EvolutionAnalyser — pure data-laag voor evolutievergelijking baseline vs huidig jaar  
**Type:** Implementatie  
**Auteur:** Danny Depecker + GHC  
**Status:** Compleet  

**Bestandsnaam:** fase3b-evolutie-analyser.md  
**Path:** docs/02-tactisch/fasen/

> Vorige fase: [fase3a-matrix.md](fase3a-matrix.md)  
> Volgende fase: fase3c-evolution-exporter.md *(gepland)*  
> Architectuurbeslissingen: [architectuur-beslissingen.md](../../01-strategisch/architectuur-beslissingen.md)

---

## 1. Doelstelling

Fase 3b voegt de `EvolutionAnalyser` toe — de **pure data-laag** voor evolutie-analyse.
Ze vergelijkt twee periodegroepen (baseline vs huidig jaar) en berekent alle KPI's,
breakdowns, ziekenhuisvergelijkingen en feedbackthema's.

**T-shirt:** M (8–24u) — nieuw systeem, meerdere berekeningen, 100% test coverage vereist.

Fase 3b genereert **geen output** (geen templates, geen bestanden).
Dat is de taak van Fase 3c (`EvolutionExporter`).

---

## 2. Deliverables

| Component | Bestand | Status |
|---|---|---|
| EvolutionResult dataclass | `src/csat/core/analysers/evolution_result.py` | ✅ Compleet |
| EvolutionAnalyser | `src/csat/core/analysers/evolution_analyser.py` | ✅ Compleet |
| i18n uitbreiding NL | `src/csat/i18n/nl.json` | ✅ Compleet |
| i18n uitbreiding FR | `src/csat/i18n/fr.json` | ✅ Compleet |
| Tests | `tests/core/test_evolution_analyser.py` | ✅ 100 tests, 100% coverage |
| evolution_df fixture | `tests/conftest.py` | ✅ Compleet |

**Testresultaat na Fase 3b:** 418 tests geslaagd — 100% coverage — CI stabiel.

---

## 3. Architectuur

### 3.1 Positie in de stack

```text
V_CSAT_1 (SQL / CSV)
    ↓
HybridLoader                    ← Fase 1
    ↓
EvolutionAnalyser               ← Fase 3b (NIEUW)
    ↓
EvolutionResult                 ← Fase 3b (NIEUW)
    ↓
EvolutionExporter + templates   ← Fase 3c (gepland)
    ↓
evolutie-YYYY-nl.md + fr.md
```

### 3.2 Designkeuzes

**EvolutionAnalyser erft niet van BaseAnalyser.** De ABC-methode `analyse(period: str)` heeft een andere signatuur dan de evolutie-interface `analyse(baseline_periods, current_periods)`. De gedeelde KPI-berekeningen (`_calc_avg_score`, `_calc_high_critical`) zijn gerepliceerd in de klasse met verwijzing naar BaseAnalyser in de docstrings. Zie ADR-verwijzing in sectie 7.

**Geen reactiegraad (ADR-006).** V_CSAT_1 bevat enkel gescoorde tickets — reactiegraad is niet berekend in EvolutionAnalyser.

**Baseline start 01/01/2025 (ADR-007).** `_filter_start_date` past `ANALYSE_START_DATE` toe op `created`.

**`satisfaction_date` als periodegroepering (ADR-011).** Alle periodefiltering (maand/jaar) gebruikt `satisfaction_date` — de datum waarop de klant zijn score gaf. `created` wordt uitsluitend gebruikt als poortwachter in `_filter_start_date()`. Dit betekent dat een ticket aangemaakt in december maar gescoord in januari meetelt in de **januari**-cijfers. Een lege maand in de grafiek is correct gedrag: geen klanten hebben die maand een score ingediend.

```python
_PERIOD_DATE_COL: str = "satisfaction_date"  # ADR-011
```

**KPI OK = score ≥ 4,00 (ADR-009).** `_calc_kpi_status` gebruikt `AVG_SCORE_MIN` uit settings.

---

## 4. EvolutionResult — structuur

De dataclass bevat alle vergelijkingsdata in één object:

| Veld | Type | Beschrijving |
|---|---|---|
| `pillar` | str | Pijlersleutel (bv. "pharma") |
| `baseline_label` | str | Label baseline (bv. "2025") |
| `current_label` | str | Label huidig (bv. "2026") |
| `baseline_total` | int | Totaal tickets baseline |
| `current_total` | int | Totaal tickets huidig |
| `baseline_avg_score` | float | Gem. CSAT-score baseline |
| `current_avg_score` | float | Gem. CSAT-score huidig |
| `delta_avg_score` | float | current − baseline |
| `baseline_pct_positive` | float | % score ≥ 4 (baseline) |
| `current_pct_positive` | float | % score ≥ 4 (huidig) |
| `baseline_pct_negative` | float | % score ≤ 2 (baseline) |
| `current_pct_negative` | float | % score ≤ 2 (huidig) |
| `baseline_avg_response_days` | float | Gem. responstijd baseline |
| `current_avg_response_days` | float | Gem. responstijd huidig |
| `baseline_n_hospitals` | int | Aantal ziekenhuizen baseline |
| `current_n_hospitals` | int | Aantal ziekenhuizen huidig |
| `baseline_hc_ratio` | float | % High/Critical baseline |
| `current_hc_ratio` | float | % High/Critical huidig |
| `trend_is_structural` | bool | True als delta ≥ 0,5 |
| `trend_breadth` | str | "breed" / "beperkt" / "gemengd" |
| `monthly_timeline` | list[MonthlyDataPoint] | Maandelijkse tijdlijn |
| `by_issue_type` | list[IssueTypeComparison] | Vergelijking per issue type |
| `by_priority` | list[PriorityComparison] | Vergelijking per prioriteit |
| `response_time_by_score` | dict[int, ResponseTimeRow] | Responstijd per score-niveau |
| `hospital_comparison` | list[HospitalComparison] | Vergelijking per ziekenhuis |
| `hospitals_disappeared` | list[str] | In baseline, niet in huidig |
| `hospitals_new` | list[str] | Niet in baseline, wel in huidig |
| `negative_themes` | list[ThemeEvolution] | Feedbackthema's (keyword matching) |
| `kpi_status` | dict[str, KpiStatus] | KPI-status per metriek |

### 4.1 Helper-dataklassen

```python
MonthlyDataPoint   # period, avg_score, total_tickets, pct_negative, fase
IssueTypeComparison  # issue_type, baseline_score/pct_neg, current_score/pct_neg
PriorityComparison   # priority, baseline_score/pct_neg, current_score/pct_neg
HospitalComparison   # hospital, baseline_score/total, current_score/total
ThemeEvolution       # theme_key, pct_baseline, pct_current, status
ResponseTimeRow      # score_level, baseline_days, current_days
KpiStatus (Enum)     # OK / WARNING / AT_RISK / UNKNOWN
```

---

## 5. EvolutionAnalyser — interface

```python
from csat.core.analysers.evolution_analyser import EvolutionAnalyser

analyser = EvolutionAnalyser(df, pillar_key="pharma")
result = analyser.analyse(
    baseline_periods=["2025-01", "2025-02", ..., "2025-12"],
    current_periods=["2026-01", "2026-02", "2026-03"],
)
# → EvolutionResult

# Labels kunnen manueel worden overschreven:
result = analyser.analyse(
    baseline_periods=["2025-01", ..., "2025-12"],
    current_periods=["2026-01", "2026-02"],
    baseline_label="Volledig 2025",
    current_label="jan-feb 2026",
)
```

---

## 6. Negatieve feedbackthema's — keyword-configuratie

Keyword matching wordt uitgevoerd op het `comment`-veld van **negatieve tickets** (score ≤ 2).
De configuratie staat in `THEME_KEYWORDS` in `evolution_analyser.py`:

| Thema | Voorbeeldkeywords |
|---|---|
| responstijd | te lang, wachttijd, traag, délai |
| onvolledig | niet opgelost, deels, incomplet |
| communicatie | geen update, onduidelijk, flou |
| urgentie | dringend, spoed, urgent |
| automatisering | automatisch, script, automatique |

**Status per thema:**

- `OPGELOST` — aanwezig in baseline, afwezig in huidig
- `NOG_AANWEZIG` — aanwezig in beide
- `NIEUW` — afwezig in baseline, aanwezig in huidig

---

## 7. ADR-verwijzingen

| ADR | Beslissing | Implementatie |
|---|---|---|
| ADR-006 | Reactiegraad N/A | Niet berekend in EvolutionAnalyser |
| ADR-007 | Baseline start 01/01/2025 | `_filter_start_date` past `ANALYSE_START_DATE` toe op `created` |
| ADR-009 | KPI OK = score ≥ 4,00 | `_calc_kpi_status` gebruikt `AVG_SCORE_MIN` (4,0) |
| ADR-011 | `satisfaction_date` als periodegroepering | `_PERIOD_DATE_COL = "satisfaction_date"` — `created` enkel als start-datumfilter |

---

## 8. Testdekking

**100 tests** in `tests/core/test_evolution_analyser.py`:

| Klasse | Onderwerp |
|---|---|
| TestEvolutionAnalyserInit | pijlervalidatie, filter, startdatum |
| TestEvolutionAnalyserRetourtype | retourtype, labels, auto/custom |
| TestKerncijfers | avg_score, delta, pct_pos/neg, HC, responstijd, ziekenhuizen |
| TestLegeData | lege baseline, lege current, beide leeg, lege periodes |
| TestMonthlyTimeline | count, sortering, fase H1/H2, avg_score, pct_neg |
| TestIssueTypeComparison | alle types, scores, pct_neg, sortering |
| TestPriorityComparison | per prioriteit, alleen baseline, beide periodes |
| TestResponseTimeByScore | per score-niveau, None-waarden |
| TestHospitalComparison | disappeared, new, scores, types |
| TestNegativeThemes | OPGELOST, NOG_AANWEZIG, NIEUW, geen keywords |
| TestKpiStatus | OK / WARNING / AT_RISK / UNKNOWN per metriek |
| TestTrendClassificatie | structureel, breed/beperkt/gemengd |
| TestKpiStatusEnum | enum-waarden en str-subtype |
| TestDataclassInstantiatie | directe instantiatie alle dataklassen |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 23/03/2026 | Initiële versie — Fase 3b volledig geïmplementeerd | Danny Depecker + GHC |
| 1.1 | 25/03/2026 | ADR-011 toegevoegd: satisfaction_date als periodegroepering; designkeuze gedocumenteerd in §3.2 | Danny Depecker + GHC |
