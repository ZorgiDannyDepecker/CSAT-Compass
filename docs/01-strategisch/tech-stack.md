# CSAT-Compass - Tech Stack Referentie  

**Versie:** 1.1
**Laatst bijgewerkt:** 26/08/2026

**Doel:** Compact architectuuroverzicht van de gebruikte technologieën, kernbestanden en gekende beperkingen
**Type:** Reference
**Auteur:** Danny Depecker + Claude
**Status:** Approved

**Bestandsnaam:** tech-stack.md
**Path:** docs/01-strategisch/

> **Herkomst:** oorspronkelijk opgesteld tijdens Fase 5a (21/04/2026) als
> `WIP/csat_stack.md`; op 26/08/2026 verplaatst naar `docs/01-strategisch/` als
> permanente architectuurreferentie (i.p.v. eenmalig hand-over-document), en
> aangevuld met Fase 6 en Fase 7.

---

## 1. Frontend Framework

| Component | Technologie | Opmerkingen |
|-----------|-------------|-------------|
| UI rendering | **Streamlit** | Layout, widgets, navigatie, tabs |
| CSS injectie | `st.markdown()` met `unsafe_allow_html=True` | ZORGI Design System kleuren en Poppins font |
| JavaScript injectie | `st.components.v1.html()` | Sidebar toggle, DOM-manipulaties — moet aan het einde van `main()` worden aangeroepen |

---

## 2. Data & Logica

| Component | Technologie | Opmerkingen |
|-----------|-------------|-------------|
| Dataverwerking | **pandas** | Filtering, aggregatie, berekeningen |
| Databaseconnectie | **SQLAlchemy** | Verbinding met `ZRG0014WI/Lerni_DB`, view `V_CSAT_1` |
| Fallback data | **CSV** | In `data/fallback/` — actief in DEMO-modus |

---

## 3. Visualisaties

| Component | Technologie | Opmerkingen |
|-----------|-------------|-------------|
| Statische charts | **matplotlib** | PNG-output voor rapporten; embedded in dashboard via `st.pyplot()` |
| Metrics / KPI-tiles | `st.metric()` (Streamlit native) | T1–T8 in Samenvatting-tab; beperkte CSS-override mogelijk |

> **Bekende beperking (T8):** `st.metric()` met `delta_color="normal"` forceert een rood neerwaartse pijl + min-prefix op de ziekenhuisnamen string. Geen clean workaround gevonden tot nu toe.

---

## 4. Rapporten & PDF Pipeline

| Component | Technologie | Opmerkingen |
|-----------|-------------|-------------|
| HTML templating | **Jinja2** | Renderen van rapport-templates |
| PDF generatie | **WeasyPrint** (v60+) | Vervangt pdfkit/wkhtmltopdf; master script in `Q&A-Lab/code/md_to_pdf.py` |

---

## 5. Internationalisatie (i18n)

| Component | Technologie | Opmerkingen |
|-----------|-------------|-------------|
| UI-strings | **JSON** (`nl.json` / `fr.json`) | Volledig NL/FR tweetalig; beheerd in `src/csat/i18n/` |

---

## 6. Branding & Design

| Component | Locatie | Opmerkingen |
|-----------|---------|-------------|
| CSS / JS / brandfuncties | `src/csat/utils/branding.py` | Python f-string double-brace escaping doorheen het hele bestand |
| ZORGI Design System | `docs/01-strategisch/zorgi_design_system.md` | Golden source voor kleuren, typografie, componenten |

**ZORGI kleurenpalet (dashboard):**

| Naam | HEX |
|------|-----|
| Dark Blue | `#003a70` |
| Red | `#dc2b26` |
| Purple | `#7f4267` |
| Grey Blue | `#5f8495` |
| Light Blue | `#609fce` |
| Ultra Light Blue | `#d7e7f3` |
| Functioneel groen | retained — semantische uitzondering voor positieve delta bars |

---

## 7. Kernbestanden Dashboard

| Bestand | Rol |
|---------|-----|
| `src/dashboard/app.py` | Streamlit entry point; `_APP_VERSION = "v0.4"` |
| `src/csat/utils/branding.py` | Alle CSS, JS en brandfuncties |
| `src/csat/i18n/nl.json` | NL UI-strings |
| `src/csat/i18n/fr.json` | FR UI-strings |
| `src/csat/core/insights/insights_generator.py` | Gedeelde InsightsGenerator (evolutie- en maandrapport) |

---

## 8. Bekende Streamlit Beperkingen

- Native `st.metric()` tiles kunnen niet volledig overschreven worden met custom HTML zonder visuele inconsistentie.
- `st.components.v1.html()` is vereist voor JavaScript-injectie (niet `st.markdown()`); moet aangeroepen worden aan het einde van `main()` om Streamlit's rendering pipeline niet te blokkeren.

---

## 9. Fase 6 en Fase 7 — Aanvullingen (26/08/2026)

**Fase 6 — ZORGI-aggregatie:**

| Component | Technologie | Opmerkingen |
|-----------|-------------|-------------|
| ZORGI-analyse | `ZorgiAnalyser` | Aggregeert alle 4 sub-pijlers (PHARMA, CARE, CARE ADMIN, ERP4HC) geaggregeerd; actief in `_ACTIVE_PILLARS` |

**Fase 7 — Maandelijkse distributie-automatisering:**

| Component | Technologie | Opmerkingen |
|-----------|-------------|-------------|
| Instelbare tendensvenster-analyse | `scripts/run_special.py` | Instelbare begindatum via `--start YYYY-MM`, standaard 2025-07 |
| Deel A: generatie + PDF | `_run_maandelijks.bat` + Windows Taakplanner | Dag 2, 07:00; combineert `run_monthly.py` + `md_to_pdf.py` |
| Deel B: narratieve samenvatting | Claude Cowork-taak `csat-onepager-maandelijks` | Daily-trigger (09:00) + interne datumcontrole (enkel dag 2 actief); genereert `onepager-<periode>-nl.md` + `tendens-<periode>-nl.md` |
| Deel C: mail-distributie | `scripts/mail_maandelijks.py` (`win32com`) | Taakplanner dag 2, 09:30; converteert onepager/tendens naar PDF en verstuurt via Outlook naar Tom/Thomas/Erwin, Danny in CC |

**Volledige details:** zie `docs/02-tactisch/fasen/fase7-maandelijkse-distributie.md` en
`docs/03-operationeel/cowork-onepager.md`.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| --- | --- | --- | --- |
| 1.0 | 21/04/2026 | Initiële versie, opgesteld tijdens Fase 5a als WIP-referentie | Danny Depecker |
| 1.1 | 26/08/2026 | Verplaatst van WIP/ naar docs/01-strategisch/ als permanente referentie; sectie 9 toegevoegd (Fase 6 + Fase 7) | Danny Depecker + Claude |
