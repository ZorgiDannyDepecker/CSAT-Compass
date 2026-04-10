# CSAT-Compass — Fase 5b: Dashboard UI-verfijning

**Versie:** 1.0
**Laatst bijgewerkt:** 10/04/2026

**Doel:** UI-verfijning van het Streamlit-dashboard — vaste tabbalk, datapanel secties, vergelijkingstabel
**Type:** Implementatie
**Auteur:** Danny Depecker + GHC
**Status:** In uitvoering

**Bestandsnaam:** fase5b-dashboard-ui-verfijning.md
**Path:** docs/02-tactisch/fasen/

---

## 1. Overzicht

Fase 5b is de directe opvolger van Fase 5a en focust op de **UI/UX-kwaliteit** van het dashboard.
De functionaliteitslaag (datamodel, analysers, exporters) is stabiel — Fase 5b verfijnt
de presentatielaag voor dagelijks gebruik door management.

**T-shirt:** M
**Afhankelijkheid:** Fase 5a volledig afgerond (v1.3, 810 tests, 99% coverage, commit `1437102`)
**Teststand bij start:** 810 tests — 99% coverage — v0.2.8

De fase is opgesplitst in drie sprints:

| Sprint | Inhoud | Status |
|---|---|---|
| Sprint 1 | Vaste tabbalk + layout-vergrendeling | ✅ Afgerond (commit `1437102`) |
| Sprint 2 | Datapanel sectie 2 — Tijdlijn + Tickets + Responstijd | ⏳ Gepland |
| Sprint 3 | Datapanel sectie 3 — Ziekenhuizen + KPI Targets | ⏳ Gepland |

---

## 2. Deliverables

| Component | Bestand | Status |
|---|---|---|
| Streamlit app (layout) | `src/dashboard/app.py` | 🔄 In uitvoering |
| ZORGI CSS (tabbalk, tegels) | `src/csat/utils/branding.py` | 🔄 In uitvoering |
| i18n NL/FR (nieuwe labels) | `src/csat/i18n/nl.json` / `fr.json` | 🔄 In uitvoering |
| Fase-document | `docs/02-tactisch/fasen/fase5b-dashboard-ui-verfijning.md` | ✅ Dit bestand |

---

## 3. Sprint 1 — Vaste tabbalk + layout-vergrendeling ✅

**Afgerond:** 10/04/2026 — commit `1437102` — versie `0.2.8`

### 3.1 Probleemstelling

Bij scrollen verdween de tabbalk, waardoor de gebruiker niet meer kon wisselen
van tab zonder eerst terug naar boven te scrollen. Bijkomend:

- Tabbalk reageerde niet op sidebar-toggle (links-positie bleef vast)
- Tabbalk klonk 2 rijen bij kleiner venster
- Doorkijkruimte van 8px tussen topbalk en tabbalk bij scrollen

### 3.2 Oplossingen

| Probleem | Oorzaak | Oplossing |
|---|---|---|
| `sticky` werkt niet | Streamlit `overflow: hidden` op ancestor | `position: fixed` |
| Sidebar-toggle reageert niet | `~`-selector vereist directe siblings | `:has([aria-expanded])` + `transition: 0.3s` |
| Knoppen niet links-uitgelijnd | Streamlit `wideSidePadding` = 5rem | `padding-left: 5rem` (gevonden in JS-bundle) |
| Tabs wrappen naar 2e rij | `flex-wrap: wrap` (default) | `flex-wrap: nowrap` + `overflow-x: auto` |
| Doorkijkruimte | `top: 118px` vs topbar `110px` | `top: 110px` |

### 3.3 CSS-architectuur (`branding.py`)

```css
/* Vaste tabbalk */
[data-testid="stTabs"] > div:first-child {
    position: fixed;
    top: 110px;
    left: 21rem;          /* sidebar open */
    right: 0;
    padding-left: 5rem;
    transition: left 0.3s ease;
    flex-wrap: nowrap;
    overflow-x: auto;
}

/* Sidebar gesloten → tabbalk schuift mee */
body:has([data-testid="stSidebar"][aria-expanded="false"])
    [data-testid="stTabs"] > div:first-child {
    left: 0;
}

/* Tab-paneel compensatie */
[data-baseweb="tab-panel"] {
    padding-top: 68px;
}
```

### 3.4 Sidebar expand/collapse knoppen

`_BTN_TOP_PX = 123` — handmatig bijgesteld voor visuele uitlijning net onder topbalk.

---

## 4. Sprint 2 — Datapanel secties 2, 3, 4 ⏳

**Scope:** Tab 2 (Tijdlijn), Tab 3 (Tickets & Prioriteit), Tab 4 (Responstijd)

### 4.1 Tab 2 — Tijdlijn

- Plotly combo-grafiek: maandelijkse score (lijn) + volume (bar, dual y-as)
  - Volledig venster: 15 maanden, fasegebaseerde puntkleur (rood H1 / groen H2 / paars Q1)
  - Tendensvenster: 9 maanden + 3-maands rolgemiddelde
  - Referentielijn: 4.0★ gestippeld
- Maandoverzichtstabel (scrollable): score + volume + fase-badge
- Vergelijkingsbalk (grouped bar): H1 2025 / H2 2025 / Q1 2026

### 4.2 Tab 3 — Tickets & Prioriteit

Volgorde conform Thomas Wyckstandt-feedback (feedbackthema's eerst):

1. Feedbackthema's actiekaarten (4 `st.container`-blokken, kleurgecodeerd)
2. Issue type analyse — grouped bar (Incident/RfC/RfI) + detailtabel
3. Prioriteit analyse — grouped bar (Blocker→Trivial) + detailtabel

### 4.3 Tab 4 — Responstijd

- Correlatie-ommekeer panel (3 tekstblokken)
- Lijn-grafiek: responstijd per score-niveau (baseline vs huidig)
- Detailtabel: responstijd + evolutie + interpretatie

---

## 5. Sprint 3 — Datapanel secties 5 en 6 ⏳

**Scope:** Tab 5 (Ziekenhuizen), Tab 6 (KPI Targets)

### 5.1 Tab 5 — Ziekenhuizen

- Horizontal grouped bar-chart: baseline vs huidig, kleurgecodeerd
- Top-5 tabel met kolom "Leerpunt"
- Bottom-5 tabel met kolom "Voornaamste klacht"
- Disengagement-alert (`st.error()`) bij score < 2.5★ + < 6 Q1-tickets
- Aandachtsaccounts-sectie (score 3.0★–4.0★) als dataframe

### 5.2 Tab 6 — KPI Targets

- Grouped bar-chart: baseline / target / realisatie per KPI
- Detailtabel: status per KPI + badge
- Bijgestelde targets-sectie (aanbevelingen opwaartse herziening)
- Interactieve targetaanpassing via `st.number_input`

---

## 6. Bewust buiten scope fase 5b

| Functionaliteit | Reden | Wanneer |
|---|---|---|
| CARE / CARE ADMIN / ERP4HC data | Pijleranalysers zijn stubs | Fase 5c (na Fase 4) |
| ZORGI overall aggregatie | Vereist Fase 4 + 5c | Fase 6 |
| PDF-export vanuit dashboard | Complexiteit | Ronde 2 |
| Klikbare per-ZH filtering | Complexiteit | Ronde 2 |
| Tendensvenster instelbare startdatum | Complexiteit | Ronde 2 |

---

## 7. Technische aandachtspunten

- **Streamlit `position: fixed`** — versie-afhankelijk: `wideSidePadding` (5rem) gevonden in
  `index.RuhrnD1v.js` (Streamlit 1.55). Bij update controleren op `padding-left` aanpassing.
- **`:has()` selector** — niet ondersteund in Firefox < 121; dashboard is gericht op Chrome/Edge.
- **Plotly-grafieken** — nog niet geïmplementeerd in sprint 2/3; tijdelijk `st.info("Coming soon")`
- **`@st.cache_data`** — alle DashboardExporter-aanroepen via cache; TTL 1u.

---

## 8. Referenties

| Document | Pad |
|---|---|
| Fase 5a (afgerond) | `docs/02-tactisch/fasen/fase5a-streamlit-dashboard.md` |
| Handover fase 5a | `WIP/handover-fase5a-2026-03-31.md` |
| Tendensvenster referentieontwerp | `Customer Satisfaction/dashboard_tendens_jul2025.html` |
| CHANGELOG | `docs/CHANGELOG.md` |
| Project Journal | `docs/project-journal.md` |
| Implementatiegids | `docs/02-tactisch/implementatie-gids.md` |
| ZORGI Design System | `docs/01-strategisch/ZORGI_Design_System.md` |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
|---|---|---|---|
| 1.0 | 10/04/2026 | Initiële versie — sprint 1 afgerond (vaste tabbalk); sprint 2+3 gepland | Danny Depecker + GHC |
