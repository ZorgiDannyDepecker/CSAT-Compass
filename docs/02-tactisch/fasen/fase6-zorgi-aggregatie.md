# Fase 6 — ZORGI Overall Aggregatie

**Versie:** 1.0
**Aangemaakt:** 21/04/2026

**Doel:** Implementatiegids voor de ZORGI-pijler als organisatiebrede aggregator
**Type:** Planning + Technische Spec
**Auteur:** Danny Depecker + GHC
**Status:** Gepland — klaar om te starten

**Bestandsnaam:** fase6-zorgi-aggregatie.md
**Path:** docs/02-tactisch/fasen/

---

## Inhoudsopgave

1. [Context & Doelstelling](#1-context--doelstelling)
2. [Architectuurprincipe](#2-architectuurprincipe)
3. [Huidige toestand](#3-huidige-toestand-per-21042026)
4. [Deliverables Fase 6](#4-deliverables-fase-6)
5. [Technische specificatie](#5-technische-specificatie)
6. [Dashboard — ZORGI-tab](#6-dashboard--zorgi-tab)
7. [Implementatievolgorde](#7-implementatievolgorde)
8. [Testplan](#8-testplan)
9. [Open vragen](#9-open-vragen)

---

## 1. Context & Doelstelling

ZORGI is de **centrale pijler** die de 4 pillar-analysers (PHARMA, CARE, CARE ADMIN, ERP4HC)
combineert tot een organisatiebrede CSAT-weergave. Zie projectplan §2 + §4.3.

**Doel van Fase 6:**

- Een ZORGI-analyser die de output van de 4 pijlers aggregeert
- Een ZORGI dashboard-tab die de organisatiebrede scores toont
- Optioneel: een ZORGI-rapport (NL + FR) als executive summary

**Doelgroep output:**

- CEO Eric (executive samenvatting — geen technische details)
- COO Christian (operationele KPI's — vergelijking pijlers)
- Intern PHARMA-team (context voor eigen pijler t.o.v. organisatie)

---

## 2. Architectuurprincipe

```text
PHARMA analyser  ─┐
CARE analyser    ─┤
                  ├─→  ZorgiAnalyser.aggregate()  →  ZorgiResult  →  ZORGI-tab
CARE ADMIN       ─┤
ERP4HC analyser  ─┘
```

**Kernregel:** `ZorgiAnalyser` verwerkt **geen ruwe data** zelf.
Het ontvangt 4 `EvolutionResult`-objecten en combineert ze.
Geen nieuwe datalaadlogica nodig — alles hergebruikt.

---

## 3. Huidige toestand (per 21/04/2026)

### Wat al bestaat

| Component | Status | Locatie |
|---|---|---|
| `PILLAR_REGISTRY` met ZORGI entry | ✅ | `src/csat/config/pillars.py` |
| ZORGI als `selected_pillar` in sidebar | ✅ | `src/dashboard/app.py` |
| `_ACTIVE_PILLARS` bevat ZORGI **niet** | ✅ (bewust) | `src/dashboard/app.py` |
| "Coming soon" pagina voor ZORGI | ✅ | `src/dashboard/app.py` |
| `src/csat/pillars/zorgi/` map | ✅ (leeg) | `src/csat/pillars/zorgi/` |
| `ZorgiAnalyser` klasse | ❌ Nog niet | — |
| `ZorgiResult` datastructuur | ❌ Nog niet | — |
| ZORGI dashboard-tab | ❌ Nog niet | — |
| ZORGI i18n-strings | ❌ Nog niet | `nl.json` / `fr.json` |

### Wat de "Coming soon"-pagina nu toont

Wanneer ZORGI geselecteerd is in de sidebar, toont het dashboard een placeholder
via `_render_coming_soon_tab()`. Dit is de ingang voor Fase 6.

---

## 4. Deliverables Fase 6

### Fase 6a — ZorgiAnalyser (kern)

- [ ] `src/csat/pillars/zorgi/analyser.py` — `ZorgiAnalyser` klasse
- [ ] `src/csat/pillars/zorgi/result.py` — `ZorgiResult` datastructuur
- [ ] `src/csat/pillars/zorgi/__init__.py` — exports
- [ ] Unit tests: `tests/pillars/test_zorgi_analyser.py`

### Fase 6b — ZORGI Dashboard-tab

- [ ] `src/dashboard/app.py` — `_render_zorgi_tab()` functie
- [ ] ZORGI toevoegen aan `_ACTIVE_PILLARS`
- [ ] i18n-strings ZORGI in `nl.json` + `fr.json`
- [ ] Unit tests: `tests/utils/test_zorgi_tab.py`

### Fase 6c — ZORGI Rapport (optioneel)

- [ ] `docs/templates/rapport-zorgi.md.j2` — Executive summary template
- [ ] `scripts/generate_zorgi_report.py` — CLI-runner
- [ ] Integratie in `scripts/run_monthly.py`

---

## 5. Technische specificatie

### 5.1 ZorgiResult datastructuur

```python
@dataclass
class ZorgiResult:
    """Organisatiebrede CSAT-aggregatie van alle 4 pijlers."""

    pillar: str = "zorgi"
    baseline_label: str = ""
    current_label: str = ""

    # Per-pijler EvolutionResults (None als pijler geen data heeft)
    pillar_results: dict[str, EvolutionResult | None] = field(default_factory=dict)

    # Gewogen gemiddelden organisatie-breed
    org_avg_score: float = 0.0
    org_delta_avg_score: float = 0.0
    org_pct_positive: float = 0.0
    org_pct_negative: float = 0.0
    org_total_tickets: int = 0
    org_n_hospitals: int = 0

    # Top/Bottom pijler
    best_pillar: str = ""
    worst_pillar: str = ""

    # Trend over alle pijlers
    pillars_improving: int = 0
    pillars_stable: int = 0
    pillars_declining: int = 0
```

### 5.2 ZorgiAnalyser interface

```python
class ZorgiAnalyser:
    """Aggregeert EvolutionResults van alle 4 pillar-analysers."""

    def __init__(self, pillar_results: dict[str, EvolutionResult]) -> None:
        ...

    def aggregate(self) -> ZorgiResult:
        """Combineert 4 pijlers tot 1 ZorgiResult."""
        ...

    @staticmethod
    def _weighted_avg(results: list[EvolutionResult], attr: str) -> float:
        """Gewogen gemiddelde op basis van current_total (ticket-volume)."""
        ...
```

### 5.3 Gewicht per pijler

Aggregatie gewogen op **ticketvolume** (`current_total`) per pijler — niet simpel gemiddelde.
Pijler met 100 tickets weegt zwaarder dan pijler met 10 tickets.

---

## 6. Dashboard — ZORGI-tab

### 6.1 Gewenste weergave

De ZORGI-tab toont een **organisatiebrede samenvatting** — compacter dan een pijler-tab.

**Sectie 1 — KPI-kaarten (organisatie-breed)**

| KPI | Waarde | Delta |
|---|---|---|
| Gem. CSAT score | 4,32★ | +0,15 t.o.v. baseline |
| % Positief | 82% | +3% |
| % Negatief | 8% | -2% |
| Totaal tickets | 234 | — |

**Sectie 2 — Pijler-vergelijking (horizontale bar chart)**

```text
PHARMA      ████████████ 4,55★
CARE        ██████████   4,20★
CARE ADMIN  █████████    4,10★
ERP4HC      ████████     3,95★
```

**Sectie 3 — Trend per pijler**

Tabel: pijler | baseline | huidig | delta | trend-icoon (↑↓→)

**Sectie 4 — Aandachtspunten**

- Welke pijler heeft de laagste score?
- Welke pijler daalt het meest?
- Welke pijler heeft de hoogste High/Critical ratio?

### 6.2 Geen ziekenhuis-tab voor ZORGI

De ZORGI-tab heeft **geen ziekenhuis-level detail** — dat staat per pijler.
ZORGI = executive niveau.

---

## 7. Implementatievolgorde

```text
Stap 1 — ZorgiResult datastructuur (30 min)
  → src/csat/pillars/zorgi/result.py

Stap 2 — ZorgiAnalyser kern (1u)
  → src/csat/pillars/zorgi/analyser.py
  → gewogen gemiddelden
  → best/worst pijler detectie
  → trend-telling

Stap 3 — Unit tests ZorgiAnalyser (45 min)
  → tests/pillars/test_zorgi_analyser.py

Stap 4 — i18n ZORGI strings (20 min)
  → nl.json + fr.json

Stap 5 — Dashboard ZORGI-tab (2u)
  → _render_zorgi_tab() in app.py
  → KPI-kaarten
  → Pijler-vergelijking chart
  → Trend-tabel
  → Aandachtspunten

Stap 6 — ZORGI toevoegen aan _ACTIVE_PILLARS (5 min)
  → app.py: _ACTIVE_PILLARS

Stap 7 — /pytest 3 + commit
```

**Geschatte totale tijd:** 4–5 uur

---

## 8. Testplan

| Test | Type | Bestand |
|---|---|---|
| `ZorgiAnalyser.aggregate()` met 4 pijlers | Unit | `test_zorgi_analyser.py` |
| `ZorgiAnalyser.aggregate()` met 1 pijler (rest None) | Unit | `test_zorgi_analyser.py` |
| Gewogen gemiddelde correctheid | Unit | `test_zorgi_analyser.py` |
| Best/worst pijler detectie | Unit | `test_zorgi_analyser.py` |
| Lege input → ZorgiResult met nullen | Unit | `test_zorgi_analyser.py` |
| i18n ZORGI-strings aanwezig in nl.json + fr.json | Unit | `test_zorgi_i18n.py` |

---

## 9. Open vragen

| # | Vraag | Beslissing |
|---|---|---|
| 1 | Heeft de ZORGI-tab een tijdlijn-grafiek (org-breed)? | ❓ Nader te bepalen |
| 2 | Wordt ZORGI ook meegenomen in `run_monthly.py`? | ❓ Nader te bepalen |
| 3 | Is er een apart ZORGI-rapport (NL/FR) gewenst als PDF? | ❓ Nader te bepalen |
| 4 | Welke drempelwaarden gelden voor ZORGI (KPI targets)? | ❓ Zelfde als pillar of apart? |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| --- | --- | --- | --- |
| 1.0 | 21/04/2026 | Initiële versie — handover Fase 6 | Danny Depecker + GHC |
