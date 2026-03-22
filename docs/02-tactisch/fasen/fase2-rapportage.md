# CSAT-Compass - Fase 2: Rapportage — Jinja2-templates + i18n NL/FR

**Versie:** 1.0  
**Laatst bijgewerkt:** 20/03/2026  

**Doel:** Uitwerking van Fase 2 — tweetalige markdown-rapportage via Jinja2 en i18n  
**Type:** Implementatie  
**Auteur:** Danny Depecker + GHC  
**Status:** In Progress  

**Bestandsnaam:** fase2-rapportage.md  
**Path:** docs/02-tactisch/fasen/  

---

## Inhoudsopgave

1. [Doelstelling](#1-doelstelling)
2. [Deliverables](#2-deliverables)
3. [Architectuur en ontwerpbeslissingen](#3-architectuur-en-ontwerpbeslissingen)
4. [Implementatiestappen](#4-implementatiestappen)
5. [i18n-structuur NL/FR](#5-i18n-structuur-nlfr)
6. [Template-structuur](#6-template-structuur)
7. [Acceptatiecriteria](#7-acceptatiecriteria)
8. [Open punten](#8-open-punten)
9. [Afhankelijkheden](#9-afhankelijkheden)

---

## 1. Doelstelling

Fase 2 bouwt voort op de hybride dataloader en PHARMA-analyser uit Fase 1.
Het doel is het automatisch genereren van **maandelijkse CSAT-rapporten** in twee talen
vanuit een `KpiResult`-object.

Na Fase 2 kan de pipeline:

- Een `KpiResult` omzetten naar een volledig opgemaakt markdown-rapport
- Rapporten genereren in zowel Nederlands als Frans
- De output opslaan als `rapport-YYYY-MM-nl.md` en `rapport-YYYY-MM-fr.md`

Rapportage-output is bestemd voor:

- **Senior leadership:** CEO Eric, COO Christian — ontvangen beide taalversies
- **PHARMA-team:** interne opvolging en bespreking

---

## 2. Deliverables

| Bestand | Beschrijving | Status |
| --- | --- | --- |
| `src/csat/i18n/nl.json` | Nederlandse labels en teksten | ✅ |
| `src/csat/i18n/fr.json` | Franse labels en teksten | ✅ |
| `src/csat/i18n/__init__.py` | `load_translations(lang)` loader | ✅ |
| `docs/templates/rapport-nl.md.j2` | Jinja2-template NL | ✅ |
| `docs/templates/rapport-fr.md.j2` | Jinja2-template FR | ✅ |
| `src/csat/core/exporters/report_exporter.py` | `ReportExporter` klasse | ✅ |
| `src/csat/core/exporters/__init__.py` | Pakket-exports | ✅ |
| `tests/core/test_report_exporter.py` | Unit tests exporter + hulpfuncties | ✅ |
| `docs/02-tactisch/fasen/fase2-rapportage.md` | Dit document | ✅ |

**T-shirt schatting:** M (8–24u)

---

## 3. Architectuur en ontwerpbeslissingen

### 3.1 Tweetaligheid via i18n JSON

ZORGI is een tweetalige organisatie — alle CSAT-output wordt in NL en FR gedeeld.
De vertaalstrategie gebruikt JSON-bestanden per taal:

- `nl.json` — primaire taal (volledig uitgewerkt)
- `fr.json` — professioneel zakelijk Frans

Beide templates (`rapport-nl.md.j2` / `rapport-fr.md.j2`) zijn structureel identiek
en laden hun teksten via de `t`-context-variabele die door `ReportExporter` wordt
gevuld vanuit de juiste JSON.

### 3.2 Jinja2 Environment configuratie

```python
Environment(
    loader=FileSystemLoader(templates_path),
    autoescape=select_autoescape([]),  # Markdown — geen HTML-escaping
    trim_blocks=True,                  # Geen lege regels door bloktags
    lstrip_blocks=True,                # Geen inspringen door bloktags
    keep_trailing_newline=True,
)
```

`trim_blocks=True` en `lstrip_blocks=True` zijn essentieel voor schone tabel-output
in markdown zonder extra lege regels.

### 3.3 Getalformattering (ZORGI-standaard)

Conform copilot-instructions.md:

- Duizendtalscheider: **punt** (.)
- Decimaalteken: **komma** (,)
- Voorbeeld: `1.234,5` | `3,80` | `+0,2`

Geïmplementeerd als Jinja2-filters: `fmt(decimals)` en `fmt_mom`.

### 3.4 Pillarernamen

De volledige weergavenamen (bv. "ZORGI PHARMA") worden opgeslagen in `PILLAR_REGISTRY`
als `report_name` en `report_name_fr` velden (toegevoegd in Fase 2).

---

## 4. Implementatiestappen

### 4.1 Stap 1 — i18n JSON-bestanden

- `src/csat/i18n/nl.json` aangemaakt met secties: months, report, sections, kpi, status, thresholds, table, notes, history
- `src/csat/i18n/fr.json` als volledige Franstalige vertaling
- `src/csat/i18n/__init__.py` met `load_translations(lang: str) -> dict`

### 4.2 Stap 2 — Jinja2-templates

- `docs/templates/rapport-nl.md.j2` — NL-template met 3 genummerde secties
- `docs/templates/rapport-fr.md.j2` — FR-template (identieke structuur)
- Secties: 1. Samenvatting | 2. Uitsplitsing per ziekenhuis | 3. Opmerkingen

### 4.3 Stap 3 — ReportExporter

- `src/csat/core/exporters/report_exporter.py` — klasse + 4 hulpfuncties
- `render(result: KpiResult) -> str` — markdown-string zonder schrijven
- `export(result: KpiResult) -> Path` — schrijft naar `output/rapport-YYYY-MM-{lang}.md`
- `_build_context(result)` — bouwt de template-context op

### 4.4 Stap 4 — Unit tests

- `tests/core/test_report_exporter.py` — unit tests voor alle componenten
- Dekt: hulpfuncties, `load_translations()`, `render()`, `export()`, `_build_context()`

---

## 5. i18n-structuur NL/FR

De JSON-bestanden volgen deze structuur:

```json
{
  "months": ["januari", ..., "december"],
  "report": { "subtitle": "...", "doel": "...", ... },
  "sections": { "summary": "...", "hospital_breakdown": "...", "notes": "..." },
  "kpi": { "label": "...", "total_tickets": "...", ... },
  "status": { "ok": "✅ OK", "warning": "⚠️ ...", "tbd": "⏳ TBD" },
  "thresholds": { "avg_score_min": "TBD", "high_critical_max": "≤ 15%" },
  "table": { "hospital": "...", "total_tickets": "...", ... },
  "notes": { "reactiegraad_na": "...", "avg_score_tbd": "...", "onbekend_hospitals": "..." },
  "history": { "initial": "..." }
}
```

---

## 6. Template-structuur

Elk gegenereerd rapport volgt de md-style-guide (document header + versiehistorie):

```text
# CSAT-Compass — CSAT Maandrapportage {maand jaar}

[document header — verplichte velden]

---

## 1. Samenvatting
  → KPI-tabel + ADR-006 waarschuwing

## 2. Uitsplitsing per ziekenhuis
  → Tabel per ziekenhuis, ONBEKEND altijd onderaan

## 3. Opmerkingen
  → TBD-drempel, eventueel ONBEKEND-melding

---

## Versiehistorie
```

---

## 7. Acceptatiecriteria

| Criterium | Verificatie | Status |
| --- | --- | --- |
| NL-rapport gegenereerd voor PHARMA jan 2026 | `render()` retourneert string met NL-labels | ✅ |
| FR-rapport gegenereerd voor PHARMA jan 2026 | `render()` retourneert string met FR-labels | ✅ |
| Bestandsnamen conform conventie | `export()` schrijft `rapport-YYYY-MM-{lang}.md` | ✅ |
| ONBEKEND onderaan in ziekenhuizentabel | Context sortering `(x[0]=="ONBEKEND", x[0])` | ✅ |
| H/C-status ✅ OK bij ratio ≤ 15% | `hc_ok = ratio <= 15.0` in context | ✅ |
| H/C-status ⚠️ bij ratio > 15% | `hc_ok = False` → template toont warning | ✅ |
| ZORGI-getalnotatie (punt/komma) | `_format_number()` filter | ✅ |
| MoM-trend met +/− prefix | `_format_mom()` filter | ✅ |
| ADR-006 waarschuwing aanwezig | Template bevat `ADR-006`-referentie | ✅ |
| Versiehistorie aanwezig | Template sluit af met versiehistorie | ✅ |
| Alle unit tests geslaagd | `pytest tests/core/test_report_exporter.py` | ✅ |

---

## 8. Open punten

| Punt | Prioriteit | Eigenaar | Beschrijving |
| --- | --- | --- | --- |
| AVG_SCORE_MIN drempel | 🔴 Hoog | Danny Depecker | Bepalen met PHARMA-team — nu TBD in rapport |
| NULL hospitals (9 stuks) | 🟡 Medium | PHARMA-team | Opvolgen data-kwaliteit — nu ONBEKEND in rapport |
| Fase 3: visualisaties | ⏳ Gepland | GHC | matplotlib/plotly charts toevoegen aan rapport |

---

## 9. Afhankelijkheden

| Package | Versie | Gebruik |
| --- | --- | --- |
| `jinja2` | ≥ 3.1.0 | Template-rendering |
| `loguru` | ≥ 0.7.0 | Logging in export() |
| `pandas` | ≥ 2.3.0 | KpiResult-invoer (via analyser) |

**Interne afhankelijkheden:**

- `csat.core.analysers.base_analyser.KpiResult` — invoertype
- `csat.config.pillars.PILLAR_REGISTRY` — pijlerweergavenamen
- `csat.config.settings.TEMPLATES_PATH` / `OUTPUT_PATH` — standaardpaden
- `csat.i18n.load_translations()` — i18n JSON-loader

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| --- | --- | --- | --- |
| 1.0 | 20/03/2026 | Initiële versie — Fase 2 volledig uitgewerkt | Danny Depecker + GHC |
