# 📋 CHANGELOG — CSAT-Compass

Alle noemenswaardige wijzigingen aan dit project worden hier gedocumenteerd.
Formaat gebaseerd op [Keep a Changelog](https://keepachangelog.com/nl/1.0.0/).

---

## [Unreleased]

### Toegevoegd

- Initile projectstructuur aangemaakt
- README.md, .gitignore, requirements.txt
- Mappenstructuur voor 4 pijlers (PHARMA, CARE, CARE ADMIN, ERP4HC)

---

## [Post fase 3g — visualisatie-verfijning + output-structuur] — 01/04/2026

### Toegevoegd

- `data/fallback/` — nieuwe volledige fallback CSV aangemaakt met datum/tijdstempel in bestandsnaam
- `output/2026-04-01/` — eerste datumsubmap automatisch aangemaakt via `dated_output_dir()`
- NL-rapport + FR-rapport + 2 PNG's (NL/FR) gegenereerd voor PHARMA in `output/2026-04-01/`

### Gewijzigd

**EvolutionVisualiser — `src/csat/core/exporters/evolution_visualiser.py`:**

- **Subplot 3 vervangen:** HC-ratio staafdiagram → gestapeld prioriteitscompositiediagram
  (Blocker/Critical/Major/Minor/Trivial) per maand; HC-ratio als lijndiagram bovenop
- **Taalondersteuning:** `lang`-parameter toegevoegd aan constructor (`'nl'` / `'fr'`);
  `_TRANSLATIONS`-dict voor alle teksten in de figuur
- **Module-constanten:** `PRIORITY_ORDER` en `PRIORITY_COLORS` op moduleniveau
- **Ticket-annotaties:** totaal tickets boven elk datapunt (subplot 1) en boven elke staaf (subplot 2)
- **Legenda uitgebreid:** `# tickets` dummy-handle toegevoegd aan subplots 1 en 2
- **Y-as subplot 1:** `ylim(0, 6.0)` (was 0–5.5) voor ruimte boven annotaties
- **Y-as subplot 2:** extra headroom voor ticket-annotaties
- **`export()` signature:** `ts_suffix`-parameter toegevoegd voor consistente bestandsnamen
  bij batch-runs (MD-rapport en PNG dragen exact dezelfde tijdstempel)
- **Bestandsnaamconventie:** taalcode in naam → `evolutie-{pillar}-{jaar}-{lang}[_{ts}].png`
- **Figuurachtergrond:** `ZORGI_CHART_BG` (`#f7fbfe`) i.p.v. `ZORGI_ULTRA_LIGHT` (`#d7e7f3`)

**EvolutionAnalyser — `src/csat/core/analysers/evolution_analyser.py`:**

- Lint-fix Ruff N806: `_MIN_TICKETS_TOP` → `_min_tickets_top`, `_MIN_TICKETS_BOTTOM` → `_min_tickets_bottom`, `_MIN_TICKETS` → `_min_tickets`
- MyPy-fix: `-(h.current_score or 0.0)` i.p.v. `-(h.current_score)` — `float | None` unary minus

**Output-structuurwijziging — `scripts/generate_evolution.py` + `scripts/run_monthly.py`:**

- Output altijd in datumsubmap `output/YYYY-MM-DD/` via `dated_output_dir()`
- `--no-timestamp` CLI-vlag toegevoegd aan `generate_evolution.py`
- `ts_suffix` centraal berekend en doorgegeven aan zowel `EvolutionExporter` als `EvolutionVisualiser`
  zodat MD-rapport en PNG-bestanden exact dezelfde tijdstempel dragen

**Tests — `tests/core/test_evolution_visualiser.py`:**

- Uitgebreid van 44 naar **61 tests**
- Nieuw: `TestRandgevallenBranchCoverage` (3 tests) — branch-coverage `_style_legend(None)`,
  negatieve delta ticket-label, legenda-kleuren subplot 4
- Subplot 1 & 2: ticket-annotaties, `# tickets` legenda, ylim-asserties
- Subplot 3: gestapelde staven, i18n NL/FR, lege priority_counts, drempellijn
- `test_export_ts_suffix_wordt_gebruikt` — expliciete ts_suffix overschrijft automatische timestamp
- `test_export_bestandsnaam_pharma` — bevestigt taalcode (`-nl`) in bestandsnaam

**Documentatie:**

- `docs/02-tactisch/fasen/fase3d-evolutie-visualisatie.md` → v1.7: volledig bijgewerkt
  (subplot 3, i18n, bestandsnaamconventie, output-structuur, testoverzicht 61 tests)
- `docs/CHANGELOG.md` → deze entry
- `docs/project-journal.md` → v2.2: journaalentry 01/04/2026
- `docs/02-tactisch/implementatie-gids.md` → v2.3

**Teststand:** 727 passed — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## [Fase 3g afsluiting] — 31/03/2026

### Toegevoegd

- `src/csat/core/insights/insights_generator.py` — correlatie-omslag detectie + KPI-achievement narrative in executive summary
- `WIP/handover-fase5a-2026-03-31.md` — handover voor Fase 5a (Streamlit dashboard PHARMA-only)
- `WIP/conversatie-opener-fase5a.md` — klaar-om-te-plakken conversatietekst voor Fase 5a

### Gewijzigd

**Taalcorrecties NL:**

- `src/csat/i18n/nl.json` — `"Standaard deviatie"` → `"Standaarddeviatie"`, `"deep-dive"` → `"diepgaande analyse"`, `"ticketworkflow"` → `"ticketstroom"`, `"manuele"` → `"handmatige"`, trend breadth labels lowercase
- `src/csat/core/insights/insights_generator.py` — `"responses"` → `"antwoorden"` (3×), ontbrekend `"is"` in scoretrend, `"Correlatie-omslag"` → `"Omslag in correlatie"` (2×), `"zijn nu de nieuwe oorzaak"` → `"vormen nu de belangrijkste oorzaak"`, `"deep-dive"` → `"diepgaande analyse"` (3×), `"Score-evolutie over analyseperiode"` → `"over de analyseperiode"`, `"ziekenhuisen"` spelfout → `"ziekenhuizen"` (2×), verborgen soft-hyphen in `"Scoreverbetering"` verwijderd
- `src/csat/core/analysers/evolution_analyser.py` — `"responses"` → `"antwoorden"` in `ScoreDistribution.narrative` (3 varianten + lege fallback)
- `docs/templates/evolutie-nl.md.j2` — `"Causale factor:"` → `"Oorzaak:"`, `"sanitizing"` → `"anonimisering"`, drempel 25% → KPI-target 15%, em dash → en dash in trendlijn, `{{ loop.index }}.` → `14.{{ loop.index }}.`

**Taalcorrecties FR:**

- `src/csat/i18n/fr.json` — `"workflow de tickets"` → `"flux de tickets"`, trend breadth labels lowercase
- `docs/templates/evolutie-fr.md.j2` — `"Facteur causal :"` → `"Cause :"`, `"sanitization"` → `"anonymisation"`, seuil 25% → objectif KPI 15%, em dash → en dash, `14.{{ loop.index }}.` nummering

**Testfixes (na CI-falen):**

- `tests/core/test_evolution_exporter.py` — `"Standaard deviatie"` → `"Standaarddeviatie"` (2×)
- `tests/core/test_insights_generator.py` — `"Geen gescoorde responses"` → `"Geen gescoorde antwoorden"`
- `src/csat/core/analysers/evolution_result.py` — docstring bijgewerkt

**Documentatie:**

- `docs/02-tactisch/implementatie-gids.md` → v2.2: fase 3g status Compleet
- `docs/02-tactisch/fasen/fase3g-evolutie-rapport-verfijning.md` → v5.0: status Compleet
- `docs/01-strategisch/projectplan-highlevel.md` → v1.4: fase 3g status Compleet
- `docs/project-journal.md` → v2.1: fase 3g afsluiting

**Teststand:** 727 passed — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## [Fase 3f/3g documentatieherstructurering] — 29/03/2026

### Toegevoegd

- `docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md` — formeel advies- en besliskader voor de verfijning van het evolutierapport

### Gewijzigd

- `docs/02-tactisch/fasen/fase3g-evolutie-rapport-verfijning.md` — oude fase 3f doorgeschoven naar 3g, met bevestigde release-1 scope
- `docs/02-tactisch/implementatie-gids.md` — fasering opgesplitst naar 3f (advieskader) en 3g (implementatie)
- `docs/01-strategisch/projectplan-highlevel.md` — high-level fasering aangepast naar 3f/3g
- `docs/project-journal.md` — nieuwe logentry voor de fasehernummering en documentatieopkuis
- `WIP/handover-fase3g-2026-03-27.md` — handover hernoemd en bijgewerkt naar fase 3g
- `WIP/conversatie-opener-fase3g.md` — opener hernoemd en concreet gemaakt op basis van fase 3f

### Opgeruimd

- `WIP/ghc_advies-evolutie-verbetering_v2.md` verplaatst naar `docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md`
- `WIP/cd_advies-evolutie-verbetering_v2.md` gearchiveerd naar `archive/WIP/20260329-documentatieopkuis/`

---

## [Documentatieopkuis] — 26/03/2026

### Toegevoegd

- `docs/02-tactisch/fasen/fase3c-evolutie-exporter.md` — retrospectief gedocumenteerd
- `docs/02-tactisch/fasen/fase3e-run-monthly.md` — batch-runner documentatie
- `docs/03-operationeel/operations-runbook.md` — operationele procedures
- `docs/03-operationeel/tools/run-monthly.md` — tool-gebruiksgids batch-runner

### Bijgewerkt

- `docs/02-tactisch/implementatie-gids.md` → v1.7: Fase 3e toegevoegd, mermaid diagram bijgewerkt
- `docs/01-strategisch/projectplan-highlevel.md` → v1.1: fasen 1–3 als Compleet gemarkeerd
- `docs/project-journal.md` → v1.8: alle fasen 2 t/m 3e retrospectief toegevoegd

### Opgeruimd

- WIP-map volledig gearchiveerd naar `archive/WIP/20260326-1645/` (23 bestanden)
- `WIP/__pycache__` verwijderd

---

## [Fase 3d verfijning + Fase 3f opstart] — 27/03/2026

### Toegevoegd

- `docs/02-tactisch/fasen/fase3f-evolutie-rapport-verfijning.md` — fase-framework (inhoud TBD, later hernoemd naar `fase3g-evolutie-rapport-verfijning.md`)
- `WIP/handover-fase3f-2026-03-27.md` — volledige contextoverdracht voor nieuwe conversatie (later hernoemd naar `handover-fase3g-2026-03-27.md`)
- `WIP/conversatie-opener-fase3f.md` — klaar-om-te-plakken conversatietekst (later hernoemd naar `conversatie-opener-fase3g.md`)

### Gewijzigd

- `src/csat/core/exporters/evolution_visualiser.py` — subplot 3 volledig vervangen:
  - Oud: HC-ratio staafdiagram (baseline vs huidig)
  - Nieuw: gestapeld prioriteitscompositiediagram (Blocker/Critical/Major/Minor/Trivial) per maand
  - HC-ratio als lijndiagram bovenop de staven
  - Ticket-annotaties boven elke staaf (`# tickets`)
  - Legenda op één rij met `99` marker als uitleg voor de annotaties
  - Subplot 2 legenda verplaatst naar rechtsboven (consistent met subplot 4)
  - `ylim(0, 118)` voor ruimte boven 100%-grens
  - `PRIORITY_COLORS` module-niveau constante + `PRIORITY_ORDER`
- `tests/core/test_evolution_visualiser.py` — bijgewerkt voor subplot 3 wijzigingen:
  - `ylim`-assertie bijgewerkt van 112 naar 118
  - `×` (Unicode) vervangen door `x` in docstrings + comments
- `.github/copilot-instructions.md` → v3.3: CVE-herinnering toegevoegd als stap 6
  in `/git` Flow 1 + Flow 3 na succesvolle commit

**Teststand:** 570 passed — 100% coverage — CI stabiel

---

## [Fase 3e] — 26/03/2026

### Toegevoegd

- `scripts/run_monthly.py` — maandelijkse batch-runner die in één commando alle output
  genereert: matrix (NL + FR) + evolutierapporten + PNG-visualisaties voor alle pijlers
  - Argumenten: `--month`, `--pillar`, `--no-charts`, `--force-csv`
  - Periodelogica: automatisch vorige maand als standaard, baseline = volledig vorig jaar
  - Consolefeedback: stapsgewijze voortgang + samenvatting (totaal bestanden + duur)
- `tests/scripts/test_run_monthly.py` — 37 unit tests (pure functies + subprocess-mocks)
  - `TestDerivePeriodsFunc` — periodeafleiding (10 tests)
  - `TestMonthLabelNl` — maandlabels NL (5 tests)
  - `TestMainMatrixStap` — matrix-aanroepargumenten (5 tests)
  - `TestMainEvolutieStap` — evolutie-aanroepargumenten (8 tests)
  - `TestVlaggen` — `--no-charts` / `--force-csv` (5 tests)
  - `TestFoutafhandeling` — sys.exit bij subprocess-fouten (3 tests)
  - `TestAanroepvolgorde` — matrix vóór evolutie (1 test)

**Teststand:** 563 passed — CI stabiel (Python 3.11 / 3.12 / 3.13)

---
*ZORGI — Danny Depecker — 2026*
