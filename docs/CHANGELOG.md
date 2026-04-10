# 📋 CHANGELOG — CSAT-Compass

Alle noemenswaardige wijzigingen aan dit project worden hier gedocumenteerd.
Formaat gebaseerd op [Keep a Changelog](https://keepachangelog.com/nl/1.0.0/).

---

## [Fase 5a — Dashboard implementatie + sidebar verfijning] — 06/04/2026

### Toegevoegd

- **`src/dashboard/app.py`** — Streamlit entry point volledig geïmplementeerd:
  - 6 tabs: Samenvatting, Tijdlijn, Tickets & Prioriteit, Responstijd, Ziekenhuizen, KPI Targets
  - Sidebar: Pijler (radio), Weergave-modus (Volledig venster / Tendensvenster), Periode (informatief), Taal (NL/FR)
  - ZORGI branded topbalk (gradient, logo, datum) via `render_topbar()`
  - `@st.cache_data` op dataloader + EvolutionAnalyser (TTL 1u) voor performantie
  - DEMO/PROD modus via `CSAT_DASHBOARD_MODE` omgevingsvariabele
- **`src/csat/core/exporters/dashboard_exporter.py`** — DashboardExporter volledig geïmplementeerd:
  - `DashboardData` dataclass: `window_start`, KPI-berekeningen, tijdlijn, ziekenhuizen, targets
  - `prepare(result, window_start)` — pure data-transformatie, niet gecached
  - Volledig venster: `window_start=None` / Tendensvenster: `window_start="2025-07-01"`
- **Pure CSS hover-tooltip** voor Weergave-modus sectie:
  - `.zorgi-help-tip` — ronde badge (16×16px, ZORGI_GREY_BLUE) identiek aan Streamlit native ?-knop
  - `.zorgi-help-tip-content` — ZORGI_DARK_BLUE popup, `white-space: nowrap`, `width: max-content`
  - Sidebar `overflow: visible` zodat tooltip de zijbalk kan verlaten zonder clipping
  - `position: absolute; left: 0; top: 100%` relatief aan `<p>` (niet aan het icoon) voor correcte uitlijning
- **Per-taal dubbele punt** via `"colon"` i18n-sleutel: NL `":"` / FR `" :"` (Franse typografie)
- **ZORGI badge CSS** voor Streamlit `[role="tooltip"]` en `[data-baseweb="popover"]`
- **Sidebar `[data-testid="stWidgetLabel"]`** CSS voor consistente label-stijl

### Gewijzigd

**Sidebar — `src/dashboard/app.py`:**

- Weergave-modus label van `st.radio(label_visibility="visible")` naar `st.markdown(**bold**)` +
  `st.radio(label_visibility="collapsed")` — zelfde visuele stijl als Pijler en Taal
- Tooltip teksten NL: `"Alle data van"` → `"Data van"`, `"S2 2025 (jul)"` → `"juli 2025"`
- Tooltip teksten FR: `"Toutes les données"` → `"Données"`, `"S2 2025 (juil.)"` → `"juillet 2025"`
- `import html` toegevoegd voor veilige HTML-injectie in Streamlit markdown
- Ongebruikte `SIDEBAR_DEFAULT_MAX / _MIN / MAX_WIDTH / MIN_WIDTH` imports verwijderd

**Branding — `src/csat/utils/branding.py`:**

- `LOGO_ASSETS`: `heartbeat_*.png` (verwijderd) → `Logo-icoon *.png` (hernoemde assets)
  Sleutelnamen bewaard voor backward-compatibiliteit (`add_watermark`, `render_topbar`, tests)
- Sidebar inner wrapper: `overflow: visible !important` op `[data-testid="stSidebar"] > div:first-child`
  en `[data-testid="stSidebarContent"]`
- Tooltip-achtergrond CSS: `[role="tooltip"]` + `[data-baseweb="popover"]` — `ZORGI_DARK_BLUE`
- Widget-label CSS: `[data-testid="stWidgetLabel"] p, label` — `font-weight: 700` + `1rem`

**i18n — `src/csat/i18n/nl.json` + `fr.json`:**

- `"colon"` sleutel toegevoegd: `":"` (NL) en `" :"` (FR)
- `"mode_full_help"`: NL `"Alle data van"` → `"Data van"` / FR `"Toutes les données"` → `"Données"`
- `"mode_trend_help"`: NL `"S2 2025 (jul)"` → `"juli 2025"` / FR `"S2 2025 (juil.)"` → `"juillet 2025"`

### Opgelost

- CI-failures (Python 3.11 / 3.12 / 3.13): `LOGO_ASSETS` verwees naar verwijderde `heartbeat_*.png`
  → bijgewerkt naar `Logo-icoon *.png` (commit `a23336e`)

**Teststand:** 790 tests — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## [Fase 5b — Dashboard UI-verfijning: tabbalk + layout] — 10/04/2026

### Toegevoegd

- **Vaste tabbalk** (`branding.py` — `STREAMLIT_CSS`):
  - `position: fixed; top: 110px` — tabbalk vergrendeld bij scrollen (sticky werkte niet door Streamlit `overflow:hidden`)
  - `:has([aria-expanded="false"])` + `~`-sibling selector voor robuuste sidebar-detectie
  - `transition: left 0.3s ease` — vloeiende animatie bij sidebar in/uitklappen
  - `padding-left: 5rem` — uitlijning met Streamlit 1.55 `wideSidePadding` (gevonden in JS-bundle)
  - `flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none` — geen 2e rij bij smaller venster
  - `padding-top: 12px; padding-bottom: 12px` — verhoogde balk
  - Verborgen WebKit-scrollbar via `::-webkit-scrollbar { display: none }`
- **Tab-paneel compensatie:** `[data-baseweb="tab-panel"] { padding-top: 68px }` voor vaste tabbalk
- **Gap-fix:** `top: 110px` (was 118px) — sluit naadloos aan op topbalk, geen doorkijkruimte bij scrollen

### Gewijzigd

- **Tab-knoppen** (`branding.py`):
  - `font-size: 1.1rem` → `1rem`
  - `padding: 0.55rem 1.5rem` → `0.45rem 1.2rem`
  - `gap: 8px` → `6px`
  - `white-space: nowrap; flex-shrink: 0` toegevoegd
- **Sidebar expand/collapse knoppen:** `_BTN_TOP_PX` bijgesteld van 130 → 123
- **Prod-modus:** `.env` omgeschakeld naar `CSAT_DASHBOARD_MODE=prod`
- **Versie:** `0.2.3` → `0.2.8` (7 incrementele patch-bumps)

### Opgelost

- Tabbalk scrolt mee bij pagina-scroll → opgelost via `position: fixed`
- Tabbalk reageert niet op sidebar-toggle → opgelost via `:has()` + CSS transition
- Knoppen niet links-uitgelijnd met content → opgelost via `padding-left: 5rem` (= Streamlit `wideSidePadding`)
- Tabbalk springt naar 2 rijen bij kleiner venster → opgelost via `flex-wrap: nowrap + overflow-x: auto`
- Doorkijkruimte tussen topbalk en tabbalk bij scrollen → opgelost via `top: 110px`

**Teststand:** 810 tests — 99% coverage — commit `1437102`

---

## [Fase 5a — Samenvatting-tab tegel-herwerking + account-categorisering] — 08/04/2026

### Toegevoegd

- **`DashboardData`** — 10 nieuwe velden:
  `kpi_high_critical_ratio`, `kpi_recent_month_label/score/name/target_delta`,
  `kpi_responses_baseline_monthly_avg`, `kpi_responses_current_period_months`,
  `kpi_streak_current_year/baseline_pct`, `current_year`,
  `kpi_attention_accounts`, `kpi_critical_account_names`, `zh_attention_list`
- **`DashboardExporter`** — 10 nieuwe helper-methoden:
  `_get_hc_ratio`, `_recent_month`, `_calc_streak_current_year`, `_calc_streak_baseline_pct`,
  `_calc_responses_baseline_monthly_avg`, `_recent_month_name`, `_count_attention_accounts`,
  `_get_critical_account_names`, `_build_attention_list`, `_build_kpi_suffixes`
- **`_tab_summary()`** — volledig herwerkt naar 2 rijen:
  - Rij A (T1–T4): Prestatie-KPIs met target-label + vs-baseline delta + suffix (baseline gemiddelde)
  - Rij B (T5–T8): Context & Risico — recente maand, responses, streak, accounts
  - Individuele suffixen per KPI: trend-modus → vs H2 2025 gem.; volledig → vs baseline 2025 gem.
  - T6/T7: absolute delta (tickets/mnd resp. %) vs baseline maandgemiddelde
  - T8: `st.metric()` met kritieke namen als delta-tekst
  - ppt-verklaring als `st.markdown()` HTML-blok
- **ZORGI fade-rand + tegelhoogte** (`branding.py`):
  - `[data-testid="stMetric"]`: blauwe links-fade, `min-height: 110px`, flex layout, `border: 2px`
  - `.zorgi-crit`: rode tekst voor kritieke-woorden in labels
  - `stMetricDelta` / `stMetricLabel`: `white-space: normal`, `font-size: 0.78rem`
  - `stHorizontalBlock`: `align-items: stretch` + flex voor gelijke tegelhoogte
- **Account-categorisering kritiek/aandacht**:
  - `_CRITICAL_SCORE_THRESHOLD`: 2.5 → 3.0
  - `_ATTENTION_SCORE_THRESHOLD`: 4.0 (nieuw)
  - `_tab_hospitals()`: aandachtsaccounts-sectie als dataframe
- **i18n nl/fr** — 14 nieuwe dashboard-sleutels:
  `kpi_high_critical`, `kpi_recent_month`, `kpi_target_above/below`,
  `kpi_accounts_label`, `kpi_critical_names_prefix`, `kpi_attention_accounts_title`,
  `kpi_no_attention_accounts`, `kpi_vs_monthly_avg`, `kpi_streak_vs`,
  `kpi_streak_unit_short`, `kpi_responses_unit_short`, `kpi_avg_abbrev`,
  `kpi_accounts_label_html`, `ppt_explanation`

### Opgelost

- T4/T6/T7 referentie: volledig jaar 2025 → correcte S2 2025 (H2) in trend-modus
- Elapsed months T6/T7: enkel maanden van huidig jaar (was: alle periodes)

**Teststand:** 810 tests — 99% coverage — commit `e51c8b4`

---

## [Unreleased]

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
