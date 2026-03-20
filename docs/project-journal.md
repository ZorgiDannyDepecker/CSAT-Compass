# 📓 CSAT-Compass - Project Journal

**Versie:** 1.2  
**Laatst bijgewerkt:** 20/03/2026

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

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur               |
| ------ | ---------- | ------------------------------------------------------- |----------------------|
| 1.0 | 17/03/2026 | Initiële versie — projectstart + architectuur-sessie | Danny Depecker       |
| 1.1 | 18/03/2026 | ADR-001 t/m ADR-005 toegevoegd | Danny Depecker       |
| 1.2 | 20/03/2026 | Fase 1 afsluiting — live DB-validatie, ADR-007, exports | Danny Depecker + GHC |

---
*ZORGI — Danny Depecker*
