# 📓 Project Journal — CSAT-Compass

Chronologisch logboek van beslissingen, bevindingen en voortgang.

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
*ZORGI — Danny Depecker*
