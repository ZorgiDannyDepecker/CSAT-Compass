# CSAT-Compass - Handover Fase 3b

**Versie:** 1.0  
**Laatst bijgewerkt:** 23/03/2026  

**Doel:** Contextoverdracht voor nieuwe conversatie — start van Fase 3b (EvolutionAnalyser)  
**Type:** Reference  
**Auteur:** Danny Depecker + GHC  
**Status:** Compleet  

**Bestandsnaam:** handover-fase3b-2026-03-23.md  
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

### Teststand na Fase 3a

- **318 tests** — 100% coverage op alle src/ bestanden
- CI: GitHub Actions stabiel (Python 3.11 / 3.12 / 3.13)

### Fase 1 — Compleet

Hybride loader (SQL + CSV fallback), BaseAnalyser + KpiResult, PillarAnalyser, PharmaAnalyser, config (settings + pillars), export_data.py script.

### Fase 2 — Compleet

i18n NL/FR (nl.json + fr.json), Jinja2 templates, ReportExporter, maandelijkse rapporten `rapport-YYYY-MM-{lang}.md`.

### Fase 3a — Compleet

MatrixExporter, matrix-templates NL/FR (11 secties: maand + kwartaal + jaar), generate_matrix.py CLI runner.

Output die al werkt:
```powershell
$env:CSAT_CSV_FALLBACK_PATH = "C:\Users\danndepe\Documents\AI\CSAT-Compass\output"
.venv\Scripts\python.exe scripts/generate_matrix.py --from 2025-01 --to 2026-03 --pillar pharma --lang both
# → output/matrix-2025-nl.md + output/matrix-2025-fr.md
```

---

## 3. Strategische beslissing — Option C

**Aanleiding:** De bestaande Claude-workflow (`PromptTemplate_CustomerSatisfactionEvolution.md`) genereert een volledige evolutie-analyse maar vereist externe AI-tooling. ZORGI wil één standalone systeem.

**Beslissing:** CSAT-Compass wordt uitgebreid met een volledige `EvolutionExporter` die dezelfde output genereert als de Claude-workflow — maar volledig autonoom, via conditionele Jinja2-templates.

**Referentie-output:** `WIP/Tendens_Vergelijkingsmatrix.md` — dit is wat de Claude-workflow nu produceert (tabellen ✅, narratief ⚠️ beperkt). CSAT-Compass moet dit volledig vervangen inclusief executive summary, aanbevelingen en eindconclusie.

**Vervangen workflow:**
```
Oud: tendens_2025.md + tendens_2026_MM_DD.md → Claude → evolutie.md + .png
Nieuw: V_CSAT_1 → CSAT-Compass → evolutie-YYYY-nl.md + evolutie-YYYY-fr.md + evolutie_analyse.png
```

---

## 4. Databeschikbaarheid — V_CSAT_1 kolommen

Alle kolommen die Fase 3b nodig heeft, zijn beschikbaar in V_CSAT_1:

| Kolom | Type | Gebruik in EvolutionAnalyser |
|---|---|---|
| `key` | string | Ticket-ID |
| `issue_type` | string | Sectie 4: vergelijking per issue type |
| `priority` | string | Sectie 5: vergelijking per priority level |
| `score` | float | Alle score-analyses |
| `comment` | string | Sectie 8: negatieve feedback thema's (keyword matching) |
| `satisfaction_date` | datetime | Responstijd = satisfaction_date - created |
| `created` | datetime | Tijdlijn + responstijd berekening |
| `hospital` | string | Sectie 7: terugkerende klanten |
| `product_domain` | string | Pijlerfilter (PHARMA / CARE / CARE ADMIN / ERP) |

**Enige beperking:** Sectie 8 (negatieve feedback thema's) vereist tekstanalyse van `comment`. Aanpak: keyword matching op basis van een configureerbare woordenlijst (geen NLP vereist).

---

## 5. Fase 3b — te starten

**Doel:** `EvolutionResult` dataclass + `EvolutionAnalyser` — de data-laag voor de evolutie-analyse  
**T-shirt:** M (8–24u)  
**Document:** `docs/02-tactisch/fasen/fase3b-evolutie-analyser.md` — aan te maken bij start  

### Wat is Fase 3b NIET

Fase 3b genereert **geen output** (geen templates, geen bestanden). Het is de pure data-laag die Fase 3c (exporter) nodig heeft als input.

### Deliverables Fase 3b

| Component | Bestand | Beschrijving |
|---|---|---|
| EvolutionResult | `src/csat/core/analysers/evolution_result.py` | Rijke dataclass — alle vergelijkingsdata |
| EvolutionAnalyser | `src/csat/core/analysers/evolution_analyser.py` | Berekent alles vanuit twee DataFrames |
| i18n uitbreiding | `src/csat/i18n/nl.json` + `fr.json` | Thema-labels, KPI-labels voor evolutie |
| Tests | `tests/core/test_evolution_analyser.py` | Doel: 100% coverage |
| Fase 3b-document | `docs/02-tactisch/fasen/fase3b-evolutie-analyser.md` | Aan te maken bij start |

### EvolutionResult — verwachte structuur

```python
@dataclass
class EvolutionResult:
    """Container voor alle vergelijkingsdata baseline vs huidig."""

    pillar: str
    baseline_label: str          # bv. "2025"
    current_label: str           # bv. "jan-mrt 2026"

    # --- Kerncijfers (sectie 1 + 3) ---
    baseline_total: int
    current_total: int
    baseline_avg_score: float
    current_avg_score: float
    delta_avg_score: float       # current - baseline
    baseline_pct_positive: float # % score >= 4
    current_pct_positive: float
    baseline_pct_negative: float # % score <= 2
    current_pct_negative: float
    baseline_avg_response_days: float
    current_avg_response_days: float
    baseline_n_hospitals: int
    current_n_hospitals: int

    # --- Tijdlijn (sectie 2) ---
    monthly_timeline: list[MonthlyDataPoint]  # alle maanden chronologisch

    # --- Breakdowns (secties 4-5) ---
    by_issue_type: list[IssueTypeComparison]
    by_priority: list[PriorityComparison]

    # --- Responstijd (sectie 5) ---
    response_time_by_score: dict[int, ResponseTimeRow]  # score 1-5 → tijden

    # --- Ziekenhuizen (sectie 7) ---
    hospital_comparison: list[HospitalComparison]
    hospitals_disappeared: list[str]  # in baseline, niet in current
    hospitals_new: list[str]          # niet in baseline, wel in current

    # --- Thema's (sectie 8) ---
    negative_themes: list[ThemeEvolution]

    # --- KPI status (sectie 9) ---
    kpi_status: dict[str, KpiStatus]  # key → ✅/🟡/🔴

    # --- Trend classificatie ---
    trend_is_structural: bool         # True = structureel, False = tijdelijk/onduidelijk
    trend_breadth: str                # "breed" / "beperkt" / "gemengd"
```

### EvolutionAnalyser — verwachte interface

```python
from csat.core.analysers.evolution_analyser import EvolutionAnalyser

# Twee periodes definiëren
analyser = EvolutionAnalyser(df, pillar_key="pharma")
result = analyser.analyse(
    baseline_periods=["2025-01", ..., "2025-12"],   # lijst van YYYY-MM strings
    current_periods=["2026-01", "2026-02", "2026-03"]
)
# → EvolutionResult
```

### Referentie-analyse uit Claude-output

De `Tendens_Vergelijkingsmatrix.md` toont de verwachte output. Gebruik dit als referentie bij het testen:

| Metriek | Verwachte waarde (jan-feb 2026 vs 2025) |
|---|---|
| Baseline gem. score | 3,43★ |
| Current gem. score | 4,37★ |
| Delta | +0,94★ |
| Baseline negatief% | 35,5% |
| Current negatief% | 8,3% |
| Baseline responstijd | 18,8 dagen |
| Current responstijd | 7,1 dagen |
| Correlatie 2025 | -0,313 |
| Correlatie 2026 | +0,118 |

### Thema keyword-lijst (sectie 8 — te configureren)

Startpunt voor keyword matching op `comment`-veld:

| Thema | Keywords (NL) | Keywords (FR) |
|---|---|---|
| Responstijd | wachttijd, te lang, traag, wacht, dagen | attente, lent, tardif, délai |
| Onvolledig opgelost | niet opgelost, deels, onvolledig, nog steeds | non résolu, incomplet, partiellement |
| Communicatie | geen update, niet gecontacteerd, onduidelijk | pas de nouvelles, pas contacté, flou |
| Urgentie | dringend, prioriteit, spoed | urgent, priorité |
| Automatisering (nieuw) | automatisch, script, automatiseer | automatique, script |

---

## 6. Architectuurcontext

### Bestaande code die Fase 3b hergebruikt

| Bestand | Gebruik |
|---|---|
| `src/csat/core/analysers/base_analyser.py` | `_calc_avg_score()`, `_calc_high_critical()`, `_calc_reactiegraad()` — erven of aanroepen |
| `src/csat/core/analysers/pillar_analyser.py` | `_filter_pillar()`, `_filter_start_date()` — hergebruiken voor data-filtering |
| `src/csat/config/pillars.py` | `PILLAR_REGISTRY` — pijlernamen |
| `src/csat/config/settings.py` | `ANALYSE_START_DATE`, `AVG_SCORE_MIN`, `HIGH_CRITICAL_MAX` |
| `src/csat/utils/date_utils.py` | `parse_period()`, `filter_period()`, `filter_year()` |

### Nieuwe helper-klassen voor EvolutionResult

```python
@dataclass
class MonthlyDataPoint:
    period: str         # "YYYY-MM"
    avg_score: float
    total_tickets: int
    pct_negative: float
    fase: str           # "H1 2025" / "H2 2025" / "2026"

@dataclass
class IssueTypeComparison:
    issue_type: str
    baseline_score: float
    baseline_pct_neg: float
    current_score: float
    current_pct_neg: float

@dataclass
class PriorityComparison:
    priority: str
    baseline_score: float
    baseline_pct_neg: float
    current_score: float
    current_pct_neg: float

@dataclass
class HospitalComparison:
    hospital: str
    baseline_score: float
    baseline_total: int
    current_score: float | None
    current_total: int

@dataclass
class ThemeEvolution:
    theme_key: str      # "responstijd" / "onvolledig" / etc.
    pct_2025: float     # % van negatieve comments
    status: str         # "OPGELOST" / "NOG_AANWEZIG" / "NIEUW"

@dataclass
class ResponseTimeRow:
    score_level: int    # 1-5
    baseline_days: float | None
    current_days: float | None

class KpiStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    AT_RISK = "at_risk"
    UNKNOWN = "unknown"
```

---

## 7. Technische context

### Virtuele omgeving activeren

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\activate
```

### Tests draaien

```powershell
.venv\Scripts\python.exe -m pytest --tb=short
# Verwacht: 318 passed, coverage 100%
```

### Lint uitvoeren

```powershell
.\tools\lint.ps1
# Verwacht: EXIT CODE 0
```

### Data beschikbaar voor testen

```powershell
# SQL-connectie actief op ZRG0014WI/Lerni_DB
# CSV fallback:
$env:CSAT_CSV_FALLBACK_PATH = "C:\Users\danndepe\Documents\AI\CSAT-Compass\output"
# Bestanden: v_csat_1_2025-heden.csv, v_csat_1_2025.csv, v_csat_1_volledig.csv
```

### Relevante mapstructuur voor Fase 3b

```text
src/csat/
├── core/analysers/
│   ├── base_analyser.py          ← referentie — hergebruiken
│   ├── pillar_analyser.py        ← referentie — hergebruiken
│   ├── evolution_result.py       ← Fase 3b — NIEUW (dataclass + helper klassen)
│   └── evolution_analyser.py     ← Fase 3b — NIEUW
├── i18n/
│   ├── nl.json                   ← uitbreiden met evolutie-labels
│   └── fr.json                   ← uitbreiden met evolutie-labels
tests/
└── core/
    ├── test_evolution_analyser.py ← Fase 3b — NIEUW
```

---

## 8. ADR-beslissingen die Fase 3b beïnvloeden

| ADR | Beslissing | Impact op Fase 3b |
|---|---|---|
| ADR-006 | Reactiegraad N/A — view pre-gefilterd | Reactiegraad niet berekenen in EvolutionAnalyser |
| ADR-007 | ANALYSE_START_DATE = 2025-01-01 | Baseline-data start 01/01/2025 |
| ADR-009 | AVG_SCORE_MIN = 4,00 | KPI-status "OK" = score ≥ 4,00 |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 23/03/2026 | Initiële versie — handover voor Fase 3b | Danny Depecker + GHC |

