# 📋 CHANGELOG — CSAT-Compass

Alle noemenswaardige wijzigingen aan dit project worden hier gedocumenteerd.
Formaat gebaseerd op [Keep a Changelog](https://keepachangelog.com/nl/1.0.0/).

---

## [0.5.8] — 15/04/2026

### Opgelost

- **`src/csat/utils/branding.py:820`** (RUF001): `×` (MULTIPLICATION SIGN) vervangen door `x` in CSS-commentaar
- **`src/dashboard/app.py:764–767`** (N806): lokale constanten `_BL_W`, `_TG_W`, `_RE_W`, `_TOTAL` hernoemd naar lowercase `_bl_w`, `_tg_w`, `_re_w`, `_total`; alle referenties bijgewerkt
- **`src/dashboard/app.py:1926`** (RUF003): en-dash `–` vervangen door koppelteken `-` in commentaar
- **`src/dashboard/app.py:1977–1978`** (F841): ongebruikte variabelen `col_last_date` en `col_first_date` verwijderd
- **`src/dashboard/app.py` — `_d_sort`/`_g_sort`** (MyPy attr-defined): type hint `hc: object` → `hc: HospitalComparison`; onnodige `# type: ignore[union-attr]` comments verwijderd
- **`src/dashboard/app.py` — df_d comprehension`** (MyPy operator):`(hc.current_score or 0.0)` gebruikt voor `float | None` arithmetiek
- **`src/csat/core/exporters/dashboard_exporter.py:828`** (MyPy operator): `hc.current_score is not None and ...` None-guard toegevoegd bij `disengagement_risk`

### Gewijzigd

- **`src/dashboard/app.py` — `_tab_hospitals`** (C901): secties E (verdwenen) en F (nieuwe ziekenhuizen) geëxtraheerd naar nieuwe helper `_render_migration_tables()`; McCabe-complexiteit verlaagd van 11 naar 9

GHC (automatische lint-fixes na `/git 2` + manuele fix-sessie)

---

## [0.5.7] — 15/04/2026

### Gewijzigd

- **Tabel E (Verdwenen)**: `col_tickets_cu` (2026) verwijderd — 3 kolommen: Ziekenhuis | Tickets ({bl}) | Datum
- **Tabel F (Nieuw)**: `col_tickets_bl` (S2 2025) verwijderd — 3 kolommen: Ziekenhuis | Tickets ({cu}) | Datum
- **Tabel E + F**: `col_widths=["55%", "20%", "25%"]` — identieke kolombreedtes voor beide tabellen
- **`_render_sortable_table()`**: `col_widths: list[str] | None = None` parameter toegevoegd; sort-pijl vergroot (`font-size 0.7→0.95rem`, `opacity 0.6→0.85`); gesorteerde kolom krijgt lichtere achtergrond (`#003a70→#1a5faf`)

CD (specificatie) + GHC (implementatie)

---

## [0.5.6] — 15/04/2026

### Toegevoegd

- **`_windowed_hospital_comparison()`** (`src/dashboard/app.py`): nieuwe helper die per-ziekenhuis scores berekent op basis van het venster (`'volledig'` = vol jaar / `'tendens'` = S2 jul-dec). Hergebruikt `_make_kc_dataframes()` voor consistente pilaar- en datumfiltering. Geeft `list[HospitalComparison]` terug.
- **`HospitalComparison`** toegevoegd aan import uit `evolution_result`

### Gewijzigd

- **Tabel D (Score-evolutie) + Tabel G (Volledig overzicht)** (`_tab_hospitals`): nu venster-aware:
  - Volledig venster → baseline = vol 2025, kolomlabels `Score 2025` / `Tickets 2025`
  - Tendensvenster → baseline = S2 2025, kolomlabels `Score S2 2025` / `Tickets S2 2025`
- **Tabel E (Verdwenen) + Tabel F (Nieuw)**: kolommen analoog aan elkaar — beide 4 kolommen: Ziekenhuis | Tickets ({bl}) | Tickets ({cu}) | Datum. Verdwenen toont 0 voor {cu}, Nieuw toont 0 voor {bl}
- **`_chart_kpi_targets_h()`**: `modebar` aangepast van `{"orientation": "h"}` naar `modebar_remove=["pan2d", "autoScale2d"]` — analoog aan `_chart_hospitals()`

CD (specificatie) + GHC (implementatie)

---

## [0.5.5] — 15/04/2026

### Verwijderd

- **Tab 7 — 🧪 KPI Preview** (`src/dashboard/app.py`): tijdelijk preview-tabblad verwijderd — `_PREVIEW_LABEL`, `tab7` in `st.tabs()` en het volledige `with tab7:` blok weggehaald; `_chart_kpi_targets_h()` blijft behouden (actief in tab 6)

CD (specificatie) + GHC (implementatie)

---

## [0.5.4] — 15/04/2026

### Gewijzigd

- **`_tab_targets()`** (`src/dashboard/app.py`): `_chart_kpi_targets()` (verticale bar) vervangen door `_chart_kpi_targets_h()` (horizontale 3-balkjes) — lijst `render_kpi_targets()` ongewijzigd

CD (specificatie) + GHC (implementatie)

---

## [0.5.3] — 15/04/2026

### Gewijzigd

- **`_chart_kpi_targets_h()`** (`src/dashboard/app.py`) — drie visuele bijsturingen:
  - **Balkbreedte**: `0.24/0.14/0.24` → `0.28/0.16/0.28` (dikkere balken); hoogte `500→560px` om tussenruimte (~20px per KPI-groep) te bewaren
  - **Modebar ruimte**: `margin.t` `30→50px` — meer ademruimte boven de grafiek
  - **Legenda**: boven gecentreerd (`y=1.02, x=0.5`) — modebar rechts en legenda gecentreerd overlappen niet; één entry `"Realisatie (groen/rood)"` met Plotly `square-open` marker (kleurloos omlijnd blokje); `margin.b` terug naar `10px`
- **`nl.json` / `fr.json`**: `legend_realization_combined` toegevoegd (NL: `"Realisatie (groen/rood)"` · FR: `"Réalisation (vert/rouge)"`)

CD (specificatie) + GHC (implementatie)

---

## [0.5.2] — 15/04/2026

### Gewijzigd

- **`_chart_kpi_targets_h()`** (`src/dashboard/app.py`) — drie visuele verbeteringen:
  - **Hoogte** 820px → 500px: de 7 KPI-elementen staan dichter bij elkaar
  - **Legenda onderaan**: `y=1.02` (boven) → `y=-0.12` (onder, gecentreerd) — modebar boven heeft nu vrij spel, geen overlapping meer
  - **Legenda Realisatie**: één emoji-dummy vervangen door twee aparte Scatter-dummies — groen `✅ Gehaald` / rood `❌ Niet gehaald` — kleuren consistent met balkkleur
  - `margin` bijgesteld: `t=30` (modebar), `b=70` (ruimte voor legenda onderaan)
- **`src/csat/i18n/nl.json`** + **`fr.json`**: `legend_target_ok` en `legend_target_nok` toegevoegd (NL: Gehaald/Niet gehaald · FR: Atteint/Non atteint)

CD (specificatie) + GHC (implementatie)

---

## [0.5.1] — 15/04/2026

### Opgelost

- **`_chart_grouped_bar()`** en **`_chart_kpi_targets()`** (`src/dashboard/app.py`):
  - Contaminatie verwijderd: Scatter-traces met `_fmt`/`target_vals`/`d["col_target"]` waren ten onrechte in beide functies terechtgekomen door een niet-unieke `replace_string_in_file`-match
  - `_chart_grouped_bar()`: hersteld naar 2 Bar-traces (baseline + huidig) + hline 4,0★
  - `_chart_kpi_targets()`: hersteld als verticale grouped bar met 3 Bar-traces (baseline / target outline / realisatie); `yaxis autorange=reversed` en `_fmt`-referentie verwijderd

CD (specificatie) + GHC (implementatie)

---

## [0.5.0] — 15/04/2026

### Gewijzigd

- **`_chart_kpi_targets_h()`** (`src/dashboard/app.py`) — target-balk omgezet van Scatter(line-ns) naar `go.Bar`:
  - Drie echte balken per KPI: Baseline (0.24) | Target (0.14, amber, iets smaller) | Realisatie (0.24)
  - `barmode="overlay"` met expliciete `width` + `offset` per trace → balken zijn naadloos aansluitend, geen overlap, geen gap
  - Target-balk toont waarde rechts via `textposition="outside"` — zelfde patroon als de andere twee
  - `bargroupgap` en `bargap` verwijderd (niet relevant bij overlay + handmatige offsets)
  - Legenda-dummy-scatter voor Realisatie (🟩🟥) behouden

CD (specificatie) + GHC (implementatie)

---

## [0.4.9] — 15/04/2026

### Gewijzigd

- **`_chart_kpi_targets_h()`** (`src/dashboard/app.py`) — drie visuele verbeteringen:
  - **Legenda**: onzichtbare scatter-legenda vervangen door zichtbaar groen vierkantje voor Realisatie — `itemsizing="constant"` voor consistente icoontjesgrootte (`itemwidth` weggelaten: Plotly minimum is 30, gelijk aan default)
  - **Modebar in data-vlak**: figuur-titel verwijderd (`title=""`), top-marge teruggebracht naar 5px (`margin={"t": 5, "r": 5}`) — modebar overlapt nu het blauwe data-vlak i.p.v. de witte titelmarge; `uniformtext` verwijderd zodat target-waarden zichtbaar zijn
  - **Balkjes aansluiten**: `bargroupgap=0.02` → `bargroupgap=0` (drie balken sluiten aan); target-balk `width=0.07` → `width=0.18` (duidelijk zichtbaar maar iets smaller dan auto ~0.24)
- **tab7 preview-blok** (`src/dashboard/app.py`): subtitel "Baseline / Target / Realisatie" als ZORGI-gestijlde `<p>` boven de grafiek — vervangt de verwijderde figuur-titel

---

## [0.4.8] — 15/04/2026

### Gewijzigd

- **`_chart_kpi_targets_h()`** (`src/dashboard/app.py`):
  - Modebar horizontaal gezet via `modebar={"orientation": "h"}` — knoppen in één rij bovenaan grafiek
  - Legenda-entry Realisatie: `🟩🟥 Realisatie` (geen ruimte tussen groen en rood) via onzichtbare scatter-trace als legendadrager
  - Target-balk (`width=0.07` → `width=0.10`): zichtbaarder maar nog duidelijk dunner dan baseline/realisatie (~43% van auto-breedte)

---

## [0.4.7] — 14/04/2026

### Gewijzigd

- **Secties A/B/C in `_tab_hospitals()`** (`src/dashboard/app.py`):
  - `st.dataframe()` vervangen door `_render_sortable_table()` voor alle drie secties
  - Kolomkoppen krijgen nu ZORGI donkerblauw (`#003a70`) achtergrond met witte tekst — uniform met D/E/F/G
  - Sortering op kolomkop en CSV-export beschikbaar in alle secties
  - Disengagement-alerts (A) en voetnoot (C) blijven buiten het iframe
  - Expliciete `<h4>` titelstijl niet meer nodig — titel zit in iframe via `_render_sortable_table()`

- **`WIP/tab5-ziekenhuizen-panelen.md`**:
  - Rendertype A/B/C bijgewerkt van `st.dataframe()` naar `_render_sortable_table()`
  - Vergelijkingstabel vereenvoudigd: alle 7 secties gebruiken nu hetzelfde rendertype

---

## [0.4.6] — 14/04/2026

### Gewijzigd

- **Secties A/B/C in `_tab_hospitals()`** (`src/dashboard/app.py`):
  - Tickets-kolom: `h.tickets` (int) → `str(h.tickets)` — Streamlit aligneert strings links, integers rechts
  - Titels: `st.markdown("#### ...")` → expliciete HTML `<h4 style='color:#003a70;...'>` — ZORGI donkerblauw, Poppins font, identiek aan de sorteerbare tabellen D/E/F/G

---

## [0.4.5] — 14/04/2026

### Gewijzigd

- **`_render_sortable_table()`** (`src/dashboard/app.py`):
  - Titelkleur: `#0e1117` → `#003a70` — matcht nu exact de ZORGI donkerblauwe `####`-sectiestijl
  - Tabelcellen: expliciete `text-align:left` als inline stijl op elke `<td>` — voorkomt browser-overschrijving van de CSS-klasseregel

---

## [0.4.4] — 14/04/2026

### Toegevoegd

- **`_render_sortable_table()`** (`src/dashboard/app.py`):
  - Nieuwe module-level helperfunctie voor sorteerbare HTML-tabellen in een iframe
  - Parameters: `df`, `title`, `delta_col`, `max_body_height`, `export_filename`, `export_label`
  - Titel matcht visueel met `st.markdown('#### ...')` — Poppins font via Google Fonts
  - Alle kolomkoppen: ZORGI donkerblauw (`#003a70`), witte tekst — uniforme styling
  - Delta-kolom: positieve waarden groen, negatieve rood
  - Exportknop: download als CSV via data-URI (werkt zonder server-roundtrip)
  - Klikbare kolomkoppen voor sortering (toggle asc/desc)

### Gewijzigd

- **`_chart_hospitals()`** (`src/dashboard/app.py`):
  - Herschreven: gebruikt nu `hospital_top10`, `hospital_bottom10`, `hospital_attention`
  - Kleur per balk op basis van score: groen (≥ 4,0★) / amber (3,0–4,0★) / rood (< 3,0★)
  - Hoogte dynamisch: `max(300, len(hospitals) * 30 + 80)`
  - Disengagement-lijn label via i18n (`hospital_disengagement_label`)

- **`_tab_hospitals()`** (`src/dashboard/app.py`):
  - Volledig herschreven — verwijderd: top5/bottom5 logica (verouderd)
  - Sectie A: Bottom 10 (< 3,0★) met disengagement-alerts
  - Sectie B: Aandachtsaccounts (3,0★ – 4,0★)
  - Sectie C: Top 10 (≥ 4,0★) met voetnoot min. 5 tickets
  - Sectie D: Score-evolutie sorteerbare tabel (`_render_sortable_table`)
  - Sectie E: Verdwenen ziekenhuizen sorteerbare tabel (📤 icoon)
  - Sectie F: Nieuwe ziekenhuizen sorteerbare tabel (🆕 icoon) — alle headers gelijke donkerblauwe kleur (fix PNG 5)
  - Sectie G: Volledig ziekenhuizenoverzicht sorteerbare tabel met max_body_height=520
  - Imports uitgebreid: `base64`, `csv`, `io` toegevoegd

- **Tests** (`tests/core/test_dashboard_exporter.py`):
  - `TestBuildHospitalBottom5` hernoemd naar `TestBuildHospitalBottom10`
  - Tests aangepast aan nieuwe `_build_hospital_bottom10()` API (geen `NegativeCase` meer)
  - `NegativeCase` import verwijderd uit testbestand

---

### Gewijzigd

- **Tabel D — Score-evolutie: Tendensvenster-ondersteuning** (`_tab_hospitals`, `src/dashboard/app.py`):
  - Shifts-berekening refactored naar mode-aware aanpak: Tendensvenster gebruikt `_trend_bl_data`/`_trend_cu_data`; Volledig venster gebruikt `raw.hospital_comparison`
  - Kolomlabels (baseline-periode) volgen nu `bl_lbl` in Tendensvenster en `_bl_lbl_raw` in Volledig venster
- **Tabel E — Verdwenen ziekenhuizen** (`_tab_hospitals`):
  - Icoon gewijzigd: 🔍 → 📤 (beter aanduiding van "vertrokken/niet meer aanwezig")
  - Kolombreedtes gefixeerd met `table-layout:fixed` + `width:50%/25%/25%` → identiek aan tabel F
- **Tabel F — Nieuwe ziekenhuizen** (`_tab_hospitals`):
  - `table-layout:fixed` + gelijke kolombreedtes toegepast → gelijk aan tabel E
  - `_TH_HUIDIG` styling op Tickets ({cu_lbl}) kolomhoofd toegevoegd
- **Scheidingslijn tabel D** (`_tab_hospitals`):
  - `margin-top` verhoogd van `-2.0rem` naar `-3.0rem`
  - Tijdelijke rode zichtbaarlijn (3px solid red) + label toegevoegd voor positie-kalibratie
- **`_render_sortable_table`** (`src/dashboard/app.py`):
  - Google Fonts `<link>` voor Poppins toegevoegd in iframe-HTML → font matcht nu met Streamlit-pagina wanneer netwerk beschikbaar
  - Titel `margin-bottom`: `8px` → `4px` (dichter bij kolomhoofden)

---

## [0.4.2] — 14/04/2026

### Gewijzigd

- **Tabellen D & G — spacing definitief hersteld** (`_tab_hospitals`, `src/dashboard/app.py`):
  - Kalibratielijnen (A/B/C/D) verwijderd — overlapping door gestapelde negatieve marges in Streamlit
  - Titel + knop teruggezet **binnen het iframe** via `_render_sortable_table` parameters (enige betrouwbare methode voor volledige CSS-controle)
  - `title_html` margin-bottom: `2px` → `8px` — titel iets dichter bij kolom-headers maar met voldoende ademruimte
  - `st.divider()` vervangen door custom `<hr style='margin-top:-2.0rem'>` → bottom-gap tabel D ↔ scheidingslijn significant verkleind
  - Aanpasbaar via enkel één waarde: `margin-top` in de custom hr (huidig: `-2.0rem`)

---

## [0.4.1] — 14/04/2026

### Gewijzigd

- **Tabellen D & G — titel/knop terug buiten iframe** (`_tab_hospitals`, `src/dashboard/app.py`):
  - Titel + exportknop gerenderd via externe `st.markdown(<h4>)` → zelfde Streamlit-native h4-font als 🟢 Top 10 best / 🔴 Top 10 minst
  - `<h4 style='margin:0'>` erft Streamlit's CSS → font-family, font-size, font-weight en kleur identiek aan alle andere sectietitels
  - Negatieve-marge-brug `margin-top:-0.75rem` ingevoegd tussen titel en iframe om iframe-top-padding te compenseren → spatie titel↔tabel gelijkgetrokken met overige tabellen
  - `_render_sortable_table` aangeroepen zonder `title`/`export_b64`/`export_filename` params (enkel tabel in iframe)

---

## [0.4.0] — 14/04/2026

### Gewijzigd

- **Tabellen D & G layout** (`_tab_hospitals`, `src/dashboard/app.py`):
  - Titel + exportknop verhuisd van externe `st.markdown()` naar **binnen het iframe** (`_render_sortable_table` `title`/`export_b64`/`export_filename` parameters) — gap tussen titel en lijst geëlimineerd
  - CSS `html, body` uitgebreid met `width:100%;box-sizing:border-box` → lijst strekt nu tot rechterrand conform overige tabellen
  - Scrollbare wrapper (`max_body_height`) krijgt `width:100%` — sluit rechtermarginafwijking bij tabel G
  - Titel-font in iframe verhoogd naar `1.25rem` en marge teruggebracht naar `2px` — visueel identiek aan h4-titels van tabellen A/B/C/E/F
  - Dode `styled_d` en `styled_g` (ongebruikte Styler-objecten) verwijderd

---

## [0.3.9] — 14/04/2026

### Gewijzigd

- **Exportknop D & G** (`_tab_hospitals`, `src/dashboard/app.py`):
  - `st.download_button` + `st.columns` vervangen door `st.markdown()` flex-div met `<a href='data:text/csv;base64,...'>` — knop nu exact rechts uitgelijnd met tabelrand
  - Titel als `<h4>` inline in dezelfde flex-div → zelfde hoogte en stijl als andere paginatitels
  - CSS-injectie voor `stDownloadButton` verwijderd (niet meer nodig)
  - `import base64` toegevoegd aan module-imports

---

## [0.3.8] — 14/04/2026

### Gewijzigd

- **Exportknop D & G** (`_tab_hospitals`, `src/dashboard/app.py`):
  - Knop uiterst rechts op titelhoogte via `st.columns([7, 2])` + 0.55rem spacer voor verticale uitlijning
  - ZORGI-stijl via CSS-injectie: donkerblauwe achtergrond, witte tekst, Poppins 0.76rem bold, `border-radius:6px`, hover = lichtblauw — bewust anders dan tabbladknoppen

---

## [0.3.7] — 14/04/2026

### Toegevoegd

- **CSV-exportknop** boven tabellen D en G (`_tab_hospitals`): `st.download_button()` met `⬇️`-label, genereert `score_evolutie_{jaar}.csv` resp. `ziekenhuizenoverzicht_{jaar}.csv`

### Gewijzigd

- **`_render_sortable_table()`**: nieuw optioneel parameter `max_body_height` — tabel G: scrollbare body (540px) met sticky header; tabel D: ongewijzigd (volledig zichtbaar)
- **Kolomranden D & G**: `#ccd9e3` → `#e0e8f0` (lichter, zelfde gewicht als HTML-tabellen E/F); header transparantie `0.25` → `0.15`

---

## [0.3.6] — 14/04/2026

### Gewijzigd

- **`_render_sortable_table()`** (`_tab_hospitals`, `src/dashboard/app.py`):
  - Alle kolomkoppen uniform `ZORGI_DARK_BLUE` (geen `ZORGI_LIGHT_BLUE` varianten voor huidig-kolommen)
  - Verticale lijnen toegevoegd: `border-left/right` op `th` (wit, 25% opacity) en `td` (`#ccd9e3`)

---

## [0.3.5] — 14/04/2026

### Toegevoegd

- **`_render_sortable_table()` lokale helper** (`_tab_hospitals`, `src/dashboard/app.py`):
  - JavaScript klik-om-te-sorteren op elke kolomkop (▲/▼ indicator)
  - ZORGI dark blue headers met witte tekst (Poppins 0.82rem) — via `_stc.html()`
  - Huidig-kolommen: lichtblauwe header + achtergrond
  - Gekleurde Δ-tekst (groen/rood/grijs)
  - Alle cellen links uitgelijnd
  - Hoogte dynamisch berekend op basis van rijcount (max 620px)

### Gewijzigd

- **Tabellen D & G**: `st.dataframe()` vervangen door `_render_sortable_table()` — combineert ZORGI-headers met klik-sortering
- **`pyproject.toml`**: versie bijgewerkt van 0.3.0 naar 0.3.5 (sync met CHANGELOG)

---

## [0.3.4] — 14/04/2026

### Verwijderd

- **Tabellen D & G** (`_tab_hospitals`, `src/dashboard/app.py`): filterrijen + reset-knop verwijderd op vraag Danny Depecker

### Gewijzigd

- **Tabellen D & G**: terug naar `st.dataframe()` voor native kolomsortering (klik op kolomkop); HTML-rendering via `.to_html()` vervangen
- **`_style_zh_df`**: cel-styling (huidig-kolommen lichtblauw, Δ-kleuren) behouden

---

## [0.3.3] — 14/04/2026

### Gewijzigd

- **Tabellen D & G** (`_tab_hospitals`, `src/dashboard/app.py`):
  - `st.dataframe()` vervangen door `pandas Styler.to_html()` + `st.markdown()` — kolomhoofden nu correct ZORGI dark blue (canvas-renderer negeerde `set_table_styles`)
  - `_style_zh_df`: tabel-breedte 100%, datacellen links uitgelijnd (`td: text-align left`), huidig-kolomhoofden `ZORGI_LIGHT_BLUE` via per-kolom `set_table_styles`
  - CSS-injectie voor AG Grid headers verwijderd (dode code)
  - Reset-knop 🔄 toegevoegd boven beide filterrijen (`st.session_state.pop` + `st.rerun()`)
  - Δ-selectbox: `label_visibility` niet meer collapsed → "Δ" label zichtbaar

### Opgelost

- Deprecation warning `use_container_width` → `width='stretch'` (vorige release)

---

### Toegevoegd

- **`_style_zh_df()` lokale helper** (`src/dashboard/app.py`, `_tab_hospitals`):
  - Pandas Styler met ZORGI-branded kolomhoofden (donkerblauw, Poppins 0.82rem)
  - Lichtblauwe achtergrond (`ZORGI_ULTRA_LIGHT`) voor "huidig"-kolommen
  - Gekleurde Δ-tekst (groen / rood / grijs) via `styler.map()`

### Gewijzigd

- **Tabel D — Score-evolutie** (`_tab_hospitals`): statische HTML-tabel vervangen door `st.dataframe()` met `_style_zh_df` — native kolomsortering beschikbaar
- **Tabel G — Volledig ziekenhuizenoverzicht** (`_tab_hospitals`): zelfde refactor als Tabel D

---

## [0.3.1] — 13/04/2026

### Toegevoegd

- **`_tab_hospitals()`** — titel "Ziekenhuisscores" boven de grafiek als `####` Markdown-kop (zelfde stijl als tabel-titels)
- **Disengagement-caption** gecombineerd met `<hr>` in één `st.markdown()`-blok voor precieze ruimtecontrole

### Gewijzigd

- **`_chart_hospitals()`** (`src/dashboard/app.py`):
  - `title={"text": ""}` toegevoegd → voorkomt "undefined" Plotly.js rendering via `PLOTLY_LAYOUT["title"]`
  - `margin={"t": 10, "b": 10}` — minimale boven/ondermarge
  - Verticale lijn op 4,0★ verwijderd (enkel disengagement-lijn op 2,5★ behouden)
- **Disengagement-caption** `margin-bottom` op `2rem` ingesteld voor gewenste afstand tot `<hr>`

---

## [0.3.0] — 13/04/2026

### Toegevoegd

- **`_chart_kpi_targets()` — horizontale grouped bar chart** (`src/dashboard/app.py`):
  - Verticale bar chart vervangen door horizontale layout (`orientation="h"`)
  - Semantische kleurlogica via `_KPI_HIGHER_IS_BETTER` dict + `_kpi_realization_color()` helper
  - Targetlijn per KPI-rij via `fig.add_shape` (verticale stippellijn enkel over eigen rij, niet door hele grafiek)
  - Neutrale legenda via dummy `go.Scatter` entries (geen rood/groen in legenda zichtbaar)
  - Rijen 8 (Incident CSAT) en 9 (Critical Priority CSAT) toegevoegd via `df_huidig`/`df_baseline` DataFrames
  - Hoogte dynamisch schalen: `max(560, n_kpis * 70)`
- **`_PLOTLY_CONFIG`** — module-niveau constante met `modeBarButtonsToRemove`:
  - Pan, Reset axes, Zoom box, Select (rechthoek) en Lasso verwijderd uit alle grafieken
  - Toegepast op alle 7 `st.plotly_chart` aanroepen in `app.py`
- **`_KPI_HIGHER_IS_BETTER`** uitgebreid met `incident_csat` en `critical_priority_csat`

### Gewijzigd

- **`_tab_targets()`** — `_make_kc_dataframes` éénmalig aangeroepen; DFs gedeeld met `_chart_kpi_targets()`
- **`_chart_kpi_targets()` signatuur** uitgebreid met `df_huidig` + `df_baseline` parameters

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

## [Bugfix — ISSUE-001: CsvLoader + SqlLoader pillar-filter] — 13/04/2026

### Opgelost

- **`src/csat/core/loaders/csv_loader.py`** — `load(pillar=...)` filterde op kolom `product`
  i.p.v. `product_domain` → retourneerde 0 rijen voor `pillar="PHARMA"`.
  Gefixte regel: `df["product_domain"].str.upper() == pillar.strip().upper()`
- **`src/csat/core/loaders/sql_loader.py`** — SQL WHERE-clausule gebruikte `product = '...'`
  i.p.v. `product_domain = '...'`.
  Gefixte regel: `conditions.append(f"product_domain = '{pillar.strip()}'")`
- Docstrings van beide `load()`-methoden bijgewerkt: `"product-kolom"` → `"product_domain-kolom"`
- **`docs/issues/ISSUE-001-csvloader-pillar-filter.md`** — Status bijgewerkt naar Resolved

Zie: `docs/issues/ISSUE-001-csvloader-pillar-filter.md`

CD (specificatie) + GHC (implementatie)

---

## [Fase 5c — KPI-Targets nazorg: invariant-isolatie + bug-documentatie] — 13/04/2026

### Gewijzigd

- **`src/dashboard/app.py`** — Taak 1: bevestigd geen dode banner-code (`adjusted_targets_note` nooit aangemaakt)
- **`src/dashboard/app.py`** — Taak 2 (Optie A): `_make_kc_dataframes()` docstring uitgebreid met INVARIANT-waarschuwing;
  inline comment toegevoegd in `_tab_targets()` die expliciet vastlegt dat KPI-Targets altijd
  `"volledig"` gebruikt, ongeacht venster-modus-instelling

### Toegevoegd

- **`docs/issues/ISSUE-001-csvloader-pillar-filter.md`** — CsvLoader pillar-filter bug gedocumenteerd:
  `CsvLoader.load(pillar="PHARMA")` filtert op kolom `product` i.p.v. `product_domain` → 0 rijen.
  Severity: Medium (productie-aanroepen in `app.py` en scripts gebruiken `loader.load()` zonder
  `pillar`-argument; handmatige FILTER_COLUMN-filtering in `_make_kc_dataframes()` niet getroffen)

CD (specificatie) + GHC (implementatie)

---

## [Fase 5c — KPI-Targets uitbreiding 7→9 rijen] — 12/04/2026

### Gewijzigd

- **`src/dashboard/app.py`** — `render_kpi_targets()` uitgebreid van 7 naar 9 rijen:
  - Rij 8: Incident CSAT — filter `issue_type == "Incident"`, target ≥ 4,00★, edge-case n=0/n<5 afgedekt
  - Rij 9: Critical Priority CSAT — filter `HIGH_CRITICAL_PRIORITIES` uit `pillars.py`, target ≥ 4,50★, edge-case afgedekt
  - Footnote ¹ bij rij 7 (Ziekenhuisretentie) met i18n-key `kpi_targets.footnote_ziekenhuisretentie`
  - Info-banner bijgewerkt naar i18n-key `kpi_targets.banner_bijgestelde_targets`
  - Functiesignatuur: `render_kpi_targets(df_huidig, df_baseline, lang)` — vaste "volledig" semantiek
  - `_CRITICAL_PRIORITY_CSAT_TARGET = 4.5` als module-constante

CD (specificatie) + GHC (implementatie)

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
