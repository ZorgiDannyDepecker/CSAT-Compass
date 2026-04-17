# CSAT-Compass — Fase 5c: Tickets & Prioriteit — Insights & Productie

**Versie:** 1.0
**Laatst bijgewerkt:** 18/04/2026

**Doel:** Implementatie van insight-boxes, feedbackthema's en productiezetting van het tabblad Tickets & Prioriteit
**Type:** Implementatie
**Auteur:** Danny Depecker + GHC
**Status:** Afgerond

**Bestandsnaam:** fase5c-tickets-prioriteit-insights.md
**Path:** docs/02-tactisch/fasen/

---

## 1. Overzicht

Fase 5c is de directe opvolger van Fase 5b en implementeert de volledige inhoud van het tabblad
**Tickets & Prioriteit** inclusief AI-gegenereerde inzichtteksten, feedbackthema-detectie en
productiezetting. Na deze fase is het DEV-tabblad verwijderd en is de nieuwe implementatie
actief in productie.

### Scope

| Component | Beschrijving |
|---|---|
| `render_tab_tickets_prioriteit()` | Hernoemd van `render_tab_dev_tickets()` — volledige tab-implementatie |
| `_generate_issue_type_insight()` | Inzichttekst voor issue type sectie (stap 3) |
| `_generate_priority_insight()` | Inzichttekst voor prioriteit sectie (stap 5) |
| `_generate_feedback_themes()` | Feedbackthema-detectie via keyword matching (stap 6) |
| `_render_feedback_themas()` | UI-helper voor thema-kaartjes (stap 6) |

---

## 2. Implementatiestappen

### Stap 1–2: Hero-metrics + grafieken

- Hero-metrics (4 KPI's) voor issue type en prioriteit
- Grouped bar charts per issue type en prioriteit
- Vergelijkingstabellen met delta-kleuring

### Stap 3: Issue type insight-box (oranje)

- `InsightsGenerator._generate_issue_type_insight()` toegevoegd
- Detecteert laagst scorend type, beste verbetering, hoog negatief%
- Typespecifieke aanbevelingen (Incident, RFC, RFI, RFI)
- NL/FR tweetalig via `_ls()`

### Stap 4: Prioriteit grafiek + tabel

- `calc_priority_comparison()` geïntegreerd
- Legenda met uitleg % Negatief en Δ Negatief

### Stap 5: Prioriteit insight-box (oranje)

- `InsightsGenerator._generate_priority_insight()` toegevoegd
- Identificeert prioriteit met laagste score_curr
- Lange tekst bij >10% negatief (verklaring + kwaliteitsreview)
- Kwartaalnotatie Q/T per taal

### Stap 6: Feedbackthema's

- `InsightsGenerator._generate_feedback_themes()` toegevoegd
- Keyword matching op `comment` kolom (score ≤ 2)
- Hergebruikt `THEME_KEYWORDS` + `THEME_ACTION_HINTS` uit `evolution_analyser`
- Max 4 thema's, gesorteerd op percentage
- UI: lichtblauwe kaartjes met donkerblauwe naam + grijze beschrijving

### Stap 7: Swap naar productie

- `render_tab_dev_tickets` hernoemd naar `render_tab_tickets_prioriteit`
- DEV-tabblad verwijderd uit tab-lijst (7 → 6 tabs)
- Originele `_tab_tickets()` bewaard als stille backup

---

## 3. Technische beslissingen

| Beslissing | Motivatie |
|---|---|
| `_generate_feedback_themes()` retourneert `list[dict]` | Eenvoudig te testen, geen extra dataklasse nodig |
| `_render_feedback_themas()` als aparte helper | C901 complexiteitslimiet; beter testbaar |
| `_tab_tickets()` bewaard als backup | Rollback in < 5 min mogelijk zonder git-revert |
| Unicode escapes buiten f-string expressies | Python 3.11 compatibiliteit (backslash in f-strings pas in 3.12) |
| `datetime.now(UTC)` ipv `date.today()` | DTZ011 compliance — timezone-aware |

---

## 4. Bugfixes in deze fase

| Fix | Bestand | Commit |
|---|---|---|
| Tab FOSC (font-size krimp bij opstart) | `branding.py`, `app.py` | v0.5.45 |
| Versie `pyproject.toml` out-of-sync | `pyproject.toml` | v0.5.45 |
| `inject_tab_font_css` ongebruikte import | `app.py` | v0.5.45 |

---

## 5. Testdekking

| Component | Tests | Coverage |
|---|---|---|
| `_generate_issue_type_insight()` | 5 tests (`TestGenerateIssueTypeInsight`) | 100% |
| `_generate_priority_insight()` | 9 tests (`TestGeneratePriorityInsight`) | 100% |
| `_generate_feedback_themes()` | 12 tests (`TestGenerateFeedbackThemes`) | 100% |
| `render_tab_tickets_prioriteit()` | Niet getest (Streamlit UI) | — |

---

## 6. Versiehistorie

| Versie | Datum | Wijzigingen |
|---|---|---|
| 1.0 | 18/04/2026 | Initieel — stap 1 t/m 7 volledig gedocumenteerd |
