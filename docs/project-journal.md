# 📓 CSAT-Compass - Project Journal

**Versie:** 2.5
**Laatst bijgewerkt:** 17/04/2026

**Doel:** Chronologisch logboek van beslissingen, bevindingen en voortgang  
**Type:** Reference  
**Auteur:** Danny Depecker  
**Status:** In Progress

**Bestandsnaam:** project-journal.md  
**Path:** docs/

> ⚠️ **Opmaakafwijking (verantwoord):** H2-headers gebruiken datumnotatie (`YYYY-MM-DD`)
> in plaats van nummers — chronologische volgorde primeert hier boven de nummering.

---

## Inhoud

- [2026-03-17 — Projectstart](#2026-03-17--projectstart)
- [2026-03-18 — Architectuur MCQ-sessie](#2026-03-18--architectuur-mcq-sessie)
- [2026-03-20 — Fase 1 afsluiting + live DB-validatie](#2026-03-20--fase-1-afsluiting--live-db-validatie)
- [2026-03-22 — Fase 2 afsluiting: Jinja2 + i18n + ReportExporter](#2026-03-22--fase-2-afsluiting-jinja2--i18n--reportexporter)
- [2026-03-22 — Fase 3a afsluiting: MatrixExporter](#2026-03-22--fase-3a-afsluiting-matrixexporter)
- [2026-03-23 — Fase 3b + 3c afsluiting: EvolutionAnalyser + EvolutionExporter](#2026-03-23--fase-3b--3c-afsluiting-evolutionanalyser--evolutionexporter)
- [2026-03-25 — Fase 3d afsluiting: EvolutionVisualiser + aanvullingen](#2026-03-25--fase-3d-afsluiting-evolutionvisualiser--aanvullingen)
- [2026-03-26 — Fase 3e afsluiting: run_monthly.py](#2026-03-26--fase-3e-afsluiting-run_monthlypy)
- [2026-03-27 — Fase 3d verfijning + Fase 3f opstart](#2026-03-27--fase-3d-verfijning--fase-3f-opstart)
- [2026-03-29 — Fase 3f/3g herstructurering](#2026-03-29--fase-3f3g-herstructurering)
- [2026-03-31 — Fase 3g afsluiting](#2026-03-31--fase-3g-afsluiting)
- [2026-04-01 — Visualisatie-verfijning + output-structuur](#2026-04-01--visualisatie-verfijning--output-structuur)
- [2026-04-06 — Fase 5a Dashboard implementatie + sidebar verfijning](#2026-04-06--fase-5a-dashboard-implementatie--sidebar-verfijning)
- [2026-04-10 — Fase 5b sprint 1: vaste tabbalk + layout-verfijning](#2026-04-10--fase-5b-sprint-1-vaste-tabbalk--layout-verfijning)
- [2026-04-17 — Versiebeheer & Git-praktijken versterkt (Prioriteit 1)](#2026-04-17--versiebeheer--git-praktijken-versterkt-prioriteit-1)
- [Versiehistorie](#versiehistorie)

---

## 2026-03-17 — Projectstart

### Beslissingen

- Projectnaam: **CSAT-Compass** 🧭
- Basis gevormd door bestaand werk in `Customer Satisfaction`
- Architectuur geïnspireerd op Scriptorium + ProjectTemplate
- Volledig GitHub Copilot & Python-driven
- Toekomstige integratie: Microsoft Copilot Agent

### Structuur

- `src/csat/` als hoofdmodule
- Pijlers: PHARMA, CARE, CARE ADMIN, ERP4HC
- Docs-lagenmodel: 01-strategisch / 02-tactisch / 03-operationeel

### Volgende stappen

- [ ] GitHub repository aanmaken (publiek)
- [ ] Selectieve migratie uit `Customer Satisfaction`
- [ ] `.venv` aanmaken en `requirements.txt` installeren
- [ ] Eerste scripts uitwerken voor PHARMA als pilootpijler

---

## 2026-03-18 — Architectuur MCQ-sessie

### Beslissingen (ADR-001 t.e.m. ADR-005)

- **ADR-001:** Hybride databron — SQL (PowerBI view) als primair, CSV als fallback
- **ADR-002:** Streamlit als dashboardtechnologie (Python-native, lokaal + deploybaar)
- **ADR-003:** Jinja2-templates + i18n JSON-woordenboeken voor NL/FR tweetaligheid
- **ADR-004:** Selectieve migratie vanuit `Customer Satisfaction` — geen copy-paste
- **ADR-005:** PHARMA-first ontwikkelingsstrategie — referentie-implementatie voor andere pijlers

### Structuuruitbreidingen

- `zorgi/` toegevoegd als 5e pijler (aggregatie van de 4 andere)
- Output uitgebreid: 5 rapporten + 5 matrices = 20 bestanden/maand + dashboard
- `src/csat/i18n/` aangemaakt voor NL/FR woordenboeken
- `src/dashboard/app.py` aangemaakt voor Streamlit
- Volledige mappenstructuur aangemaakt (pillars, core modules, config, utils)

### Volgende stappen

- [ ] DB-connectiegegevens PowerBI-view opvragen en in `.env` zetten
- [ ] Kolomnamen CSV-export valideren
- [ ] PHARMA KPI-drempelwaarden valideren met PHARMA-team
- [ ] Starten met `base_loader.py` → `csv_loader.py` → `sql_loader.py`

---

## 2026-03-20 — Fase 1 afsluiting + live DB-validatie

### Bevindingen live DB-exploratie

- **6.000 tickets** aanwezig in V_CSAT_1
- **64 unieke ziekenhuizen** — 9 met `NULL` in hospital-kolom
- **Filterkolom bevestigd:** `product_domain` (niet `product`)
- **Prioriteitsschaal bevestigd:** Blocker > Critical > Major > Minor > Trivial
- **Score-bereik bevestigd:** 1 tot 5 (integer)
- **Reactiegraad N/A:** view bevat enkel gescoorde tickets — 100% heeft score (zie ADR-006)
- **PHARMA-pijler:** 854 tickets, 64 ziekenhuizen, live KPI-berekening geslaagd

### Beslissingen

- **ADR-007:** ANALYSE_START_DATE = 2025-01-01 (configureerbaar via env), NULL hospitals → ONBEKEND
- **AVG_SCORE_MIN:** blijft TBD — te bepalen met PHARMA-team bij eerste rapportage

### Technische afronding Fase 1

- 151 unit tests — 100% coverage
- CI/CD actief via GitHub Actions + Codecov
- `scripts/export_data.py` toegevoegd: exporteert V_CSAT_1 naar CSV (`--year`, `--since`, `--all`)
- `WIP/explore_products.py` verwijderd (achterhaald)
- ADR-007 gedocumenteerd in `architectuur-beslissingen.md`
- `fase1-data-analyse.md` bijgewerkt naar Status: Compleet

### Exportbestanden aangemaakt

| Bestand | Rijen | Periode |
|---|---|---|
| `output/v_csat_1_volledig.csv` | 6.000 | Volledige view |
| `output/v_csat_1_2025.csv` | 1.706 | Alleen 2025 |
| `output/v_csat_1_2025-heden.csv` | 2.188 | 01/01/2025 → 20/03/2026 |

### Volgende stappen (Fase 2)

- [ ] Jinja2-templates opzetten voor NL/FR rapport
- [ ] i18n JSON-woordenboeken aanmaken (`src/csat/i18n/`)
- [ ] `ReportExporter` implementeren
- [ ] AVG_SCORE_MIN bespreken met PHARMA-team
- [ ] NULL hospitals opvolgen met PHARMA-team (data-kwaliteit)

---

## 2026-03-22 — Fase 2 afsluiting: Jinja2 + i18n + ReportExporter

### Technische afronding

- `ReportExporter` geïmplementeerd — Jinja2 + i18n naar NL/FR markdown
- `src/csat/i18n/nl.json` en `fr.json` aangemaakt met alle labels en teksten
- `docs/templates/rapport-nl.md.j2` en `rapport-fr.md.j2` volledig uitgewerkt
- `scripts/generate_report.py` als CLI-runner voor enkelvoudige rapporten
- Eerste PHARMA-rapporten gegenereerd: `rapport-2026-01-nl.md` + `rapport-2026-01-fr.md`

### Beslissingen

- Tweetaligheid volledig via i18n JSON — nooit labels hardcoden in templates
- `_format_number()` en `_format_date()` als gedeelde helperfuncties in `report_exporter.py`

### Teststand

- Cumulatief einde Fase 2: **~250 tests** — 100% coverage

---

## 2026-03-22 — Fase 3a afsluiting: MatrixExporter

### Technische afronding

- `MatrixExporter` geïmplementeerd — genereert vergelijkingsmatrix NL + FR
- `docs/templates/matrix-nl.md.j2` en `matrix-fr.md.j2` aangemaakt
- `scripts/generate_matrix.py` als CLI-runner (`--from`, `--to`, `--pillar`, `--lang`)
- Output: `matrix-{jaar}-nl.md` / `matrix-{jaar}-fr.md`

### Beslissingen

- Matrix-scope: intra-pijler (ziekenhuis × categorie) voor PHARMA
- `--lang both` als standaard — altijd NL én FR genereren

### Teststand

- Cumulatief einde Fase 3a: **~300 tests** — 100% coverage

---

## 2026-03-23 — Fase 3b + 3c afsluiting: EvolutionAnalyser + EvolutionExporter

### Technische afronding Fase 3b (EvolutionAnalyser)

- `EvolutionResult` dataclass geïmplementeerd met alle vergelijkingsmetrieken
- `EvolutionAnalyser` berekent baseline vs. huidig jaar voor elke pijler:
  - Maandelijkse tijdlijn, issue_type breakdown, prioriteit, responstijd per score
  - Ziekenhuisvergelijking (verdwenen / nieuw / delta per ziekenhuis)
  - Negatieve feedbackthema's via keyword-matching
  - KPI-statusevaluatie (OK / Aandacht / Risico)
- **ADR-009** gedocumenteerd: KPI-drempel avg_score ≥ 4,0
- **ADR-010** gedocumenteerd: `satisfaction_date` als datumbasis voor periodefiltering
- 100 unit tests voor EvolutionAnalyser

### Technische afronding Fase 3c (EvolutionExporter)

- `EvolutionExporter` geïmplementeerd — Jinja2 + i18n naar NL/FR evolutierapport
- `docs/templates/evolutie-nl.md.j2` en `evolutie-fr.md.j2` — 8-sectie structuur:
  kerncijfers, tijdlijn, KPI-status, per type, per prioriteit, ziekenhuizen, thema's, conclusie
- `scripts/generate_evolution.py` — enkelvoudige pijler (`--pillar`, `--baseline`, `--current`, `--lang`)
- `scripts/generate_all_evolutions.py` — alle 5 pijlers in één run
- `_fmt_delta()` helperfunctie voor delta-weergave met +/- prefix (ZORGI-getalnotatie)
- 54 unit tests voor EvolutionExporter

### Teststand

- Cumulatief einde Fase 3b + 3c: **472 tests** — 100% coverage — CI stabiel

---

## 2026-03-25 — Fase 3d afsluiting: EvolutionVisualiser + aanvullingen

### Technische afronding Fase 3d (EvolutionVisualiser)

- `EvolutionVisualiser` geïmplementeerd — matplotlib 4-subplot PNG per pijler
- Subplots: gem. score tijdlijn / % negatief / HC-ratio / delta per ziekenhuis
- `--chart` vlag toegevoegd aan `generate_evolution.py` en `generate_all_evolutions.py`
- 44 unit tests

### Aanvullingen buiten originele scope (allemaal productierijp opgeleverd)

| Toevoeging | Bestand(en) | Reden |
|---|---|---|
| ZORGI huisstijl | `src/csat/utils/zorgi_theme.py` | Centrale kleurconstanten — single source of truth |
| NL + FR PNG | `evolution_visualiser.py` — `lang` parameter | Tweetaligheidsbeleid consequent doorgetrokken |
| CSV-fallback robuustheid | `loaders/__init__.py` · `csv_loader.py` | 0-rijen detectie + duidelijke foutmelding |
| `--force-csv` vlag | `generate_evolution.py` · `generate_all_evolutions.py` | Reproduceerbare runs bij SQL-storing |
| `--snapshot` vlag | `scripts/export_data.py` | Automatische kopie naar `data/fallback/` |
| Lokale tijdstempel | `evolution_visualiser.py` · `csv_loader.py` | UTC vervangen door lokale systeemtijd |

### Beslissingen

- **ADR-011** gedocumenteerd: `satisfaction_date` als datumbasis in alle 4 visualisatiesubplots
- **ADR-012** gedocumenteerd: nieuwe instappers (baseline_total=0) uitgesloten uit delta-ranking subplot 4 — statistisch misleidend zonder historische vergelijking
- PNG-bestandsnaam: `evolutie-{pillar}-{jaar}-{lang}.png` (NL + FR apart)

### Teststand

- Cumulatief einde Fase 3d: **515 tests** — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## 2026-03-26 — Fase 3e afsluiting: run_monthly.py

### Technische afronding

- `scripts/run_monthly.py` geïmplementeerd — maandelijkse batch-runner
- Argumenten: `--month`, `--pillar`, `--no-charts`, `--force-csv`
- Periodelogica volledig automatisch afgeleid uit doelmaand (`_derive_periods()`)
- Standaard: vorige maand, alle 5 pijlers, charts aan
- Consolefeedback: stapsgewijze voortgang + samenvatting (totaal bestanden + duur)
- 37 unit tests via subprocess-mocks

### Beslissingen

- `run_monthly.py` roept de generators aan via `subprocess.run` (geen directe imports)
  → onafhankelijk testbaar zonder DB of bestanden
- Output naar datumstempel-submap in `output/YYYY-MM-DD_HHMM/` (geen overschrijving)

### Documentatieopkuis (26/03/2026)

- WIP-map volledig gearchiveerd naar `archive/WIP/20260326-1645/` (23 bestanden)
- 4 nieuwe docs aangemaakt: `fase3c-evolutie-exporter.md`, `fase3e-run-monthly.md`,
  `operations-runbook.md`, `tools/run-monthly.md`
- `implementatie-gids.md` bijgewerkt: fase 3e toegevoegd (versie 1.7)
- `projectplan-highlevel.md` bijgewerkt: fase 1–3 als Compleet gemarkeerd (versie 1.1)

### Teststand

- Cumulatief einde Fase 3e: **563 tests** — 100% coverage — CI stabiel

---

## 2026-03-27 — Fase 3d verfijning + Fase 3f opstart

### Technische afronding — subplot 3 volledige herwerking

Subplot 3 van de `EvolutionVisualiser` (kwadrant linksonder in de PNG) werd volledig
vervangen: het eenvoudige HC-ratio staafdiagram maakte plaats voor een informatierijker
**gestapeld prioriteitscompositiediagram**.

**Nieuw subplot 3:**

- Gestapelde staven per maand: Blocker / Critical / Major / Minor / Trivial (% van totaal)
- HC-ratio lijndiagram bovenop de staven (Blocker + Critical)
- Ticket-annotaties boven elke staaf (absolute aantallen, grijs)
- Legenda op één rij met `99`-marker als uitleg voor de annotaties
- `ylim(0, 118)` — ruimte boven 100% voor annotaties + legenda
- Wit legenda-kader binnenin de plotruimte (consistent met kwadranten 1, 2 en 4)

**Layout-verbeteringen iteratief doorgevoerd:**

- Subplot 2 legenda verplaatst naar rechtsboven (consistent met subplot 4)
- Trivial-kleur aangepast naar `#b8cfe0` (zichtbaar zonder edgecolor)
- Annotaties: `fontsize=7`, `color=ZORGI_GREY_BLUE` (treedt terug)
- 5 lint-issues opgelost: `N806`, `C901 noqa`, `RUF005`, `RUF002/003`, `W605`

### Beslissingen

- `PRIORITY_COLORS` als module-niveau constante gedefinieerd (niet binnen methode)
- `noqa: C901` toegevoegd aan `_draw_subplot3_priority_composition`
  — complexiteit van 14 is aanvaardbaar voor één visualisatiemethode
- `ylim = 118` (niet 112): voldoende ruimte voor zowel ticket-annotaties als legenda

### Fase 3f opstart

- Fase-document aangemaakt: `docs/02-tactisch/fasen/fase3f-evolutie-rapport-verfijning.md`
  (later hernoemd naar `fase3g-evolutie-rapport-verfijning.md`)
- Handover aangemaakt: `WIP/handover-fase3f-2026-03-27.md`
  (later hernoemd naar `handover-fase3g-2026-03-27.md`)
- Conversatie-opener aangemaakt: `WIP/conversatie-opener-fase3f.md`
  (later hernoemd naar `conversatie-opener-fase3g.md`)
- Inhoud fase 3f (concrete verbeteringen) wordt aangeleverd door Danny Depecker

### Teststand

- Cumulatief einde 27/03: **570 tests** — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## 2026-03-29 — Fase 3f/3g herstructurering

### Beslissingen

- Het formele advies- en besliskader voor de evolutieverbetering wordt de **nieuwe fase 3f**
- De eerdere implementatiegerichte fase 3f schuift door naar **fase 3g**
- `fase3f` = gap-analyse, beslisrecord, architectuurkeuzes, release-1 scope
- `fase3g` = effectieve implementatie van de verfijning op basis van fase 3f

### Documentatieopkuis

- `WIP/ghc_advies-evolutie-verbetering_v2.md` verplaatst naar
  `docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md`
- `docs/02-tactisch/fasen/fase3f-evolutie-rapport-verfijning.md` hernoemd naar
  `docs/02-tactisch/fasen/fase3g-evolutie-rapport-verfijning.md`
- `WIP/handover-fase3f-2026-03-27.md` hernoemd naar `WIP/handover-fase3g-2026-03-27.md`
- `WIP/conversatie-opener-fase3f.md` hernoemd naar `WIP/conversatie-opener-fase3g.md`
- Verouderd alternatief adviesdocument gearchiveerd naar `archive/WIP/20260329-documentatieopkuis/`

### Bijgewerkte richting

- Fase 3f is nu **compleet als adviesfase**
- Fase 3g staat **in planning als implementatiefase**
- De implementatiegids en het high-level projectplan werden mee aangepast zodat de fasering opnieuw klopt

---

## 2026-03-31 — Fase 3g afsluiting

### Wat werd afgerond

Fase 3g is volledig afgerond. Alle deliverables uit het advieskader (fase 3f v3.0) zijn geïmplementeerd en gevalideerd.

**Resterende aanvullingen uit §9.2 (30/03/2026) — nu alsnog geïmplementeerd:**

| Aanvulling | Implementatie |
|---|---|
| `baseline_correlation_score` veld | `evolution_result.py` — nieuw veld toegevoegd |
| Baseline-correlatie berekening | `evolution_analyser.py` — Pearson r voor baseline |
| Correlatie-omslag detectie + KPI-achievement narrative | `insights_generator.py` — bevinding + executive summary |

**NL/FR taalcorrecties (31/03/2026):**

- `"responses"` → `"antwoorden"` (NL) — 4 locaties: `insights_generator.py`, `evolution_analyser.py`
- `"Standaard deviatie"` → `"Standaarddeviatie"` (NL) — `nl.json` + tests
- `"deep-dive"` → `"diepgaande analyse"` (NL/FR) — templates + generator + json
- `"Causale factor:"` → `"Oorzaak:"` (NL) / `"Facteur causal :"` → `"Cause :"` (FR)
- `"sanitizing"` → `"anonimisering"` (NL) / `"sanitization"` → `"anonymisation"` (FR)
- `"ticketworkflow"` → `"ticketstroom"`, `"manuele"` → `"handmatige"` (NL)
- `"workflow de tickets"` → `"flux de tickets"` (FR)
- Drempel-inconsistentie: `"drempel van 25%"` → `"KPI-target van 15%"` (NL/FR)
- Trendlijn: em dash → en dash + lowercase breadth labels (NL/FR)
- Hiërarchische nummering aanbevelingen: `1.` → `14.1.` t/m `14.5.` (NL/FR)
- Spelfout `"ziekenhuisen"` → `"ziekenhuizen"` — code-logica suffix (2 locaties)
- Verborgen soft-hyphen in `"Scoreverbeter­ing"` verwijderd

### Teststand eindstand

- **727 tests** — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)
- Na taalcorrecties: 2 tests bijgewerkt in `test_evolution_exporter.py` + `test_insights_generator.py`
- Na CI-falen: `evolution_analyser.py` + `evolution_result.py` ook bijgewerkt (narrative-veld)

### Commits

| Hash | Beschrijving |
|---|---|
| `77c99bf` | fix(i18n): correct NL/FR language quality in reports and templates |
| `afa11b6` | fix(tests): update assertions after NL language corrections |

### Beslissingen

- Fase 5a (Streamlit dashboard PHARMA-only) is de volgende stap — vóór Fase 4
- Rationale: PHARMA is de enige volledige pijler; verticale slice geeft directe managementwaarde
- Dashboard-architectuur pijler-agnostisch bouwen via `PILLAR_REGISTRY`; andere pijlers = "Coming soon"
- Handover aangemaakt: `WIP/handover-fase5a-2026-03-31.md`

---

## 2026-04-01 — Visualisatie-verfijning + output-structuur

### Wijzigingen

**EvolutionVisualiser — subplot 3 vervangen:**

- Oud: HC-ratio vergelijkingsdiagram (2 staven baseline/huidig)
- Nieuw: gestapeld prioriteitscompositiediagram (Blocker/Critical/Major/Minor/Trivial) per maand
- HC-ratio bewaard als lijndiagram bovenop de staven
- Ticket-annotaties boven elk datapunt (subplot 1) en elke staaf (subplot 2)
- `PRIORITY_ORDER` en `PRIORITY_COLORS` als module-constanten

**Taalondersteuning toegevoegd:**

- `lang`-parameter (`'nl'` / `'fr'`) in `EvolutionVisualiser.__init__`
- `_TRANSLATIONS`-dict voor alle teksten in de figuur (titels, labels, fallbacks)
- `generate_evolution.py` genereert nu NL én FR PNG bij `--lang both`

**Output-structuurwijziging:**

- Alle output (MD + PNG) gaat naar datumsubmap `output/YYYY-MM-DD/`
- `ts_suffix` centraal berekend en gedeeld tussen `EvolutionExporter` en `EvolutionVisualiser`
  voor consistente bestandsnamen
- Bestandsnaamconventie: `evolutie-{pillar}-{jaar}-{lang}[_{ts}].png`

**Lint-fixes `evolution_analyser.py`:**

- Ruff N806: `_MIN_TICKETS_TOP` / `_MIN_TICKETS_BOTTOM` / `_MIN_TICKETS` → lowercase
- MyPy: `float | None` unary minus opgelost via `or 0.0`

### Teststand

- **727 tests** — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)
- `test_evolution_visualiser.py`: uitgebreid van 44 naar 61 tests
- Nieuw: `TestRandgevallenBranchCoverage` voor branch-coverage edge cases

### Output gegenereerd (01/04/2026)

| Bestand | Locatie |
|---|---|
| `evolutie-pharma-2026-nl_20260401-*.md` | `output/2026-04-01/` |
| `evolutie-pharma-2026-fr_20260401-*.md` | `output/2026-04-01/` |
| `evolutie-pharma-2026-nl_20260401-*.png` | `output/2026-04-01/` |
| `evolutie-pharma-2026-fr_20260401-*.png` | `output/2026-04-01/` |
| Fallback CSV | `data/fallback/` (met datum/tijdstempel) |

---

## 2026-04-06 — Fase 5a Dashboard implementatie + sidebar verfijning

### Wijzigingen

**Fase 5a core implementatie:**

- `app.py` volledig gebouwd: ZORGI topbalk, 6 tabs, sidebar (Pijler/Modus/Periode/Taal),
  `@st.cache_data` op dataloader + EvolutionAnalyser (TTL 1u), DEMO/PROD modus
- `dashboard_exporter.py` volledig geïmplementeerd: `DashboardData` dataclass +
  `prepare(result, window_start)` — pure transformatie, niet gecached
- Volledig venster: `window_start=None` (jan 2025 → nu)
  Tendensvenster: `window_start="2025-07-01"` (jul 2025 → nu)
- 790 tests — CI stabiel op Python 3.11/3.12/3.13

**Sidebar Weergave-modus label + tooltip redesign:**

- Probleem: `st.radio(label_visibility="visible")` rendeert label in Streamlit-widget-stijl
  (lichter, andere spacing) — inconsistent met "Pijler" en "Taal" die via `st.markdown` bold renderen
- Oplossing: `st.markdown("<strong>Weergave-modus</strong>")` + `label_visibility="collapsed"` +
  pure CSS hover-tooltip via `.zorgi-help-tip` / `.zorgi-help-tip-content` klassen
- Sidebar `overflow: visible` gezet op inner wrapper → tooltip kan sidebar verlaten zonder clipping
- Tooltip positionering: `position: absolute; left: 0; top: 100%` relatief aan `<p>` met `position: relative`
  → popup start aan linkerrand van sidebar content (niet aan het icoon ~145px naar rechts)
- `white-space: nowrap; width: max-content` → elk item precies op één lijn

**i18n verfijning (NL + FR):**

- Per-taal dubbele punt: `"colon": ":"` (NL) / `"colon": " :"` (FR — Franse typografie)
- Tooltip teksten verkort en verduidelijkt: "Alle data van" → "Data van", "S2 2025 (jul)" → "juli 2025"
- Hetzelfde in FR: "Toutes les données" → "Données", "S2 2025 (juil.)" → "juillet 2025"

**Logo-assets fix (CI):**

- Oorzaak: `heartbeat_*.png` bestanden hernoemd naar `Logo-icoon *.png` maar `LOGO_ASSETS`
  in `branding.py` bleef verwijzen naar de oude namen → 2 test-failures op alle 3 Python-versies
- Fix: alle 6 sleutels bijgewerkt naar nieuwe bestandsnamen (sleutelnamen bewaard voor compatibiliteit)

### Beslissingen

- Pure CSS tooltip (`::hover` + `:hover` descendant) verkozen boven Streamlit `help=` parameter:
  CSS is versie-onafhankelijk, betrouwbaar bold via `<strong>`, positioneerbaar buiten sidebar-overflow
- `import html` (stdlib) voor veilige HTML-escape in Streamlit `unsafe_allow_html` calls
- ZORGI badge-stijl (16×16px ronde knop) consistent met Streamlit's native `?` help-knop
- `overflow: visible` op sidebar inner wrapper is veilig zolang sidebar-content op scherm past
  (geen scroll nodig — 4 secties passen altijd in de viewport)

### Teststand

- **790 tests** — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)
- Commits: `3218d7f` (feat: tooltip redesign + i18n) · `a23336e` (fix: LOGO_ASSETS CI-fix)

---

## 2026-04-10 — Fase 5b sprint 1: vaste tabbalk + layout-verfijning

### Context

Eerste sprint van Fase 5b. Focust op de UX van de vaste elementen bovenaan het dashboard
(topbalk + tabbalk + sidebar-knoppen) voordat de inhoud van de tabbladen wordt verfijnd.

### Beslissingen

- **`position: sticky` verlaten** — werkt niet in Streamlit door `overflow: hidden` op een
  voorouder-container; vervangen door `position: fixed` (gegarandeerd werkend)
- **`:has()`-selector** gekozen boven `~`-sibling selector voor sidebar-detectie —
  robuuster bij DOM-nesting variaties tussen Streamlit-versies
- **`padding-left: 5rem`** voor tabbalk — exact gelijk aan Streamlit 1.55 `wideSidePadding`
  (gevonden in JS-bundle `index.RuhrnD1v.js`, geldig bij viewport > 864px)
- **`flex-wrap: nowrap`** ipv `wrap` — voorkomt 2e rij die content afdekt bij kleiner venster;
  horizontale scroll als veiligheidsnet bij heel kleine vensters
- **`_BTN_TOP_PX = 123`** — handmatig bijgesteld via iteratieve feedback

### Technische bevindingen

| Probleem | Oorzaak | Oplossing |
|----------|---------|-----------|
| Sticky werkt niet | Streamlit overflow:hidden op ancestor | position: fixed |
| Sidebar-toggle reageert niet | ~ selector vereist directe siblings | :has() + transition |
| Knoppen niet uitgelijnd | 1rem ≠ Streamlit wideSidePadding | padding-left: 5rem |
| Tabs wrappen naar 2e rij | flex-wrap: wrap (default) | flex-wrap: nowrap |
| Content piept onder tabbalk | gap van 8px (top:118px vs topbar:110px) | top: 110px |

### Teststand

- **810 tests** — 99% coverage (dashboard_exporter 97%) — commit `1437102`
- Versie: `0.2.8`

### Volgende stap

**Fase 5b sprint 2** — mini-signaalkaart herwerking (`_tab_summary` sectie 2):
zie `WIP/handover-fase5b-signaalkaart.md`

---

## 2026-04-17 — Versiebeheer & Git-praktijken versterkt (Prioriteit 1)

### Aanleiding

Analyse van de Git-workflow wees op drie structurele hiaten: single-branch workflow,
ontbrekende Git-tags bij versie-mijlpalen, en geen branch protection op `master`.

### Uitgevoerde acties

- **`.github/pull_request_template.md`** aangemaakt — type-checkboxes, checklist (tests/lint/CHANGELOG/PII/screenshots), refs-veld voor BACKLOG/ISSUE-nummers
- **Annotated tags** aangemaakt en gepusht: `v0.5.0` (commit `c4898e0`) + `v0.5.38` (commit `b281bcd`) — koppeling CHANGELOG ↔ Git-history hersteld
- **Branch protection `master`** geconfigureerd via GitHub Settings:
  - PR verplicht vóór merge
  - 1 approval vereist + stale reviews automatisch dismissed
  - Status check `Python 3.13 — Tests` (GitHub Actions) verplicht
- **`BACKLOG-004-git-branching-strategie.md`** aangemaakt — develop-branch, squash-strategie, chore-conventie en rollback-procedure als Prioriteit 2

### Beslissingen

- Prioriteit 2 (branching strategie, develop-branch, squash) bewust uitgesteld naar backlog — solo-workflow loopt stabiel, uitbreiding pas zinvol bij actieve teamsamenwerking
- Tag-naamgeving: `v{major}.{minor}.{patch}` voor releases, `safety/{YYYY-MM-DD}-{beschrijving}` voor veiligheids-snapshots

### Resultaat

Versiebeheer-maturiteit van het project significant verhoogd: merge-controle actief,
release-history traceerbaar, PR-discipline geborgd voor toekomstige samenwerking.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur               |
| ------ | ---------- | ------------------------------------------------------- |----------------------|
| 1.0 | 17/03/2026 | Initiële versie — projectstart + architectuur-sessie | Danny Depecker       |
| 1.1 | 18/03/2026 | ADR-001 t/m ADR-005 toegevoegd | Danny Depecker       |
| 1.2 | 20/03/2026 | Fase 1 afsluiting — live DB-validatie, ADR-007, exports | Danny Depecker + GHC |
| 1.3 | 22/03/2026 | Fase 2 afsluiting — ReportExporter, i18n, templates | Danny Depecker + GHC |
| 1.4 | 22/03/2026 | Fase 3a afsluiting — MatrixExporter | Danny Depecker + GHC |
| 1.5 | 23/03/2026 | Fase 3b + 3c afsluiting — EvolutionAnalyser, EvolutionExporter, 472 tests | Danny Depecker + GHC |
| 1.6 | 25/03/2026 | Fase 3d afsluiting — EvolutionVisualiser, ADR-011/012, 515 tests | Danny Depecker + GHC |
| 1.7 | 26/03/2026 | Fase 3e afsluiting — run_monthly.py, 563 tests | Danny Depecker + GHC |
| 1.8 | 26/03/2026 | Documentatieopkuis: WIP gearchiveerd, 4 nieuwe docs, 3 docs bijgewerkt | Danny Depecker + GHC |
| 1.9 | 27/03/2026 | Fase 3d verfijning (subplot 3 herwerking, 570 tests) + Fase 3f opstart | Danny Depecker + GHC |
| 2.0 | 29/03/2026 | Fase 3f/3g herstructurering: advieskader formeel naar fase 3f, implementatie doorgeschoven naar 3g, documentatie opgeschoond | Danny Depecker + GHC |
| 2.1 | 31/03/2026 | Fase 3g afsluiting: NL/FR taalcorrecties, testfixes, 727 tests; beslissing Fase 5a PHARMA-first | Danny Depecker + GHC |
| 2.2 | 01/04/2026 | Visualisatie-verfijning: subplot 3 prioriteitscompositie, i18n, output-structuur datumsubmap, lint-fixes, 61 visualiser-tests | Danny Depecker + GHC |
| 2.3 | 06/04/2026 | Fase 5a dashboard implementatie + sidebar verfijning: pure CSS tooltip, i18n fixes, LOGO_ASSETS CI-fix, 790 tests | Danny Depecker + GHC |
| 2.4 | 10/04/2026 | Fase 5b sprint 1: vaste tabbalk (position:fixed), sidebar-responsiviteit, layout-verfijning, 810 tests; v0.2.8 | Danny Depecker + GHC |
| 2.5 | 17/04/2026 | Versiebeheer & Git-praktijken versterkt: PR-template, annotated tags v0.5.0+v0.5.38, branch protection master, BACKLOG-004 | Danny Depecker + GHC |

---
*ZORGI — Danny Depecker*
