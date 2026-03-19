# CSAT-Compass - Projectplan High-Level

**Versie:** 1.0  
**Laatst bijgewerkt:** 18/03/2026  

**Doel:** Fundament en referentiedocument voor de volledige CSAT-Compass opzet  
**Type:** Planning  
**Auteur:** Danny Depecker + GHC  
**Status:** Approved  

**Bestandsnaam:** projectplan-highlevel.md  
**Path:** docs/01-strategisch/  

---

## Inhoudsopgave

1. [Projectvisie](#1-projectvisie)
2. [De 5 pijlers](#2-de-5-pijlers)
3. [Outputspecificatie](#3-outputspecificatie)
4. [Architectuuroverzicht](#4-architectuuroverzicht)
5. [Technologiestack](#5-technologiestack)
6. [Ontwikkelingsfasering](#6-ontwikkelingsfasering)
7. [Mappenstructuur](#7-mappenstructuur)
8. [Team en rapportage](#8-team-en-rapportage)

---

## 1. Projectvisie

**CSAT-Compass** is een Python-gedreven automatiseringstool die maandelijkse
klanttevredenheidsanalyses genereert voor alle ZORGI-pijlers en voor ZORGI als geheel.

> *"De klanttevredenheidswijzer die richting geeft aan elke ZORGI-pijler."*

### 1.1 Oorsprong

Het project is een evolutie van de bestaande PHARMA-gerichte CSAT-analyse
(`Customer Satisfaction`). De bewezen analyselogica wordt selectief gemigreerd
en herschreven conform de nieuwe multi-pijler architectuur.

### 1.2 Scope uitbreiding

| Was | Is nu |
|---|---|
| 1 pijler (PHARMA) | 5 pijlers (ZORGI + PHARMA + CARE + CARE ADMIN + ERP4HC) |
| Handmatige CSV-input | Hybride: SQL live + CSV fallback |
| Rapporten via GHC | Geautomatiseerde Jinja2-templates + i18n |
| Geen dashboard | Streamlit interactief dashboard |
| 2 outputbestanden/maand | 20 outputbestanden/maand + dashboard |

---

## 2. De 5 pijlers

```text
                    ↑ NOORD
                    PHARMA
              Ziekenhuisapotheek

    ← WEST                        OOST →
    CARE ADMIN                     CARE
    Administratie                  Verpleging

                    ↓ ZUID
                    ERP4HC
              Enterprise systemen

              [centrum: ZORGI overall]
```

| Pijler | Richting | Domein | Analyser-rol |
|---|---|---|---|
| ZORGI | Centrum 🧭 | Organisatie-breed | Aggregeert de 4 pillar-analysers |
| PHARMA | ↑ Noord | Ziekenhuisapotheek | Referentie-implementatie (piloot) |
| CARE | → Oost | Verpleegkundige zorgtoepassingen | Kopie PHARMA + aanpassing |
| CARE ADMIN | ← West | Administratieve zorgtoepassingen | Kopie PHARMA + aanpassing |
| ERP4HC | ↓ Zuid | Enterprise systemen | Kopie PHARMA + aanpassing |

---

## 3. Outputspecificatie

### 3.1 Per maandelijkse run: 20 bestanden + dashboard

| # | Rapport NL | Rapport FR | Matrix NL | Matrix FR |
|---|---|---|---|---|
| 1 | `rapport-YYYY-MM-zorgi-nl.md` | `rapport-YYYY-MM-zorgi-fr.md` | `matrix-YYYY-MM-zorgi-nl.md` | `matrix-YYYY-MM-zorgi-fr.md` |
| 2 | `rapport-YYYY-MM-pharma-nl.md` | `rapport-YYYY-MM-pharma-fr.md` | `matrix-YYYY-MM-pharma-nl.md` | `matrix-YYYY-MM-pharma-fr.md` |
| 3 | `rapport-YYYY-MM-care-nl.md` | `rapport-YYYY-MM-care-fr.md` | `matrix-YYYY-MM-care-nl.md` | `matrix-YYYY-MM-care-fr.md` |
| 4 | `rapport-YYYY-MM-care-admin-nl.md` | `rapport-YYYY-MM-care-admin-fr.md` | `matrix-YYYY-MM-care-admin-nl.md` | `matrix-YYYY-MM-care-admin-fr.md` |
| 5 | `rapport-YYYY-MM-erp4hc-nl.md` | `rapport-YYYY-MM-erp4hc-fr.md` | `matrix-YYYY-MM-erp4hc-nl.md` | `matrix-YYYY-MM-erp4hc-fr.md` |

**Totaal:** 10 rapporten + 10 matrices = **20 MD/PDF-bestanden** + Streamlit dashboard

### 3.2 Matrix scope

| Matrix | Assen | Type |
|---|---|---|
| `zorgi` | Pijler (rij) × Maand/periode (kolom) | Cross-pijler vergelijking |
| `pharma` / `care` / `care_admin` / `erp4hc` | Ziekenhuis (rij) × Categorie (kolom) | Intra-pijler vergelijking |

### 3.3 Tweetaligheid

Alle output wordt geproduceerd in **Nederlands (primair)** en **Frans (vertaling)**.
De vertaling verloopt via Jinja2-templates gekoppeld aan `i18n/nl.json` + `i18n/fr.json`.
Cijfers, tabellen en visualisatietitels zijn identiek in beide versies.

---

## 4. Architectuuroverzicht

```text
databron
  ├── SqlLoader     (live: sqlalchemy → PowerBI DB view)
  └── CsvLoader     (fallback: lokale export in data/)
        ↓
  DataLoader        (gemeenschappelijke interface, kiest automatisch)
        ↓
  PillarAnalyser    (core-logica + pillar-specifieke regels)
        ↓
  ├── ReportExporter    → Jinja2 + i18n → rapport-YYYY-MM-[pijler]-[taal].md
  ├── MatrixExporter    → Jinja2 + i18n → matrix-YYYY-MM-[pijler]-[taal].md
  └── DashboardExporter → Streamlit app met NL/FR toggle
```

### 4.1 Databron — hybride strategie

```python
# Selectie-logica DataLoader (pseudocode)
if db_connection_available():
    loader = SqlLoader(connection_string=settings.DB_CONN)
else:
    loader = CsvLoader(path=settings.CSV_FALLBACK_PATH)
    logger.warning("SQL niet bereikbaar — fallback naar CSV")
```

- **SQL (primair):** directe connectie via `pyodbc` / `sqlalchemy` naar de PowerBI-databaseview
- **CSV (fallback):** handmatige of geplande exports in `data/` (niet in Git)

### 4.2 Tweetaligheid — i18n strategie

Eén Jinja2-template per outputtype. Labels en teksten in `i18n/nl.json` en `i18n/fr.json`.
Eén template aanpassen = beide talen automatisch bijgewerkt.

### 4.3 ZORGI-pijler als aggregator

`zorgi/analyser.py` verwerkt geen ruwe data zelf. Het combineert de output
van de 4 pillar-analysers tot een organisatiebrede analyse.

---

## 5. Technologiestack

| Categorie | Technologie | Versie | Doel |
|---|---|---|---|
| Taal | Python | 3.11+ | Alle analyse- en exportlogica |
| Data | pandas | ≥2.0 | Datamanipulatie |
| Data | sqlalchemy + pyodbc | ≥2.0 / ≥5.0 | SQL-connectie naar DB view |
| Visualisatie | matplotlib + seaborn | ≥3.7 / ≥0.12 | Statische grafieken |
| Visualisatie | plotly | ≥5.20 | Interactieve grafieken (dashboard) |
| Templates | Jinja2 | ≥3.1 | Rapportgeneratie |
| i18n | Babel | ≥2.14 | Datumnotatie, lokalisatie |
| Dashboard | Streamlit | ≥1.32 | Interactief dashboard NL/FR |
| Rapportage | weasyprint | ≥60.0 | MD → PDF conversie |
| Logging | loguru | ≥0.7 | Gestructureerde logging |
| Testing | pytest + pytest-cov | ≥7.4 | Unit tests |

---

## 6. Ontwikkelingsfasering

### 6.1 Fasering — PHARMA-first

PHARMA is de **referentie-implementatie**. Elke volgende pijler is een kopie + aanpassing.

| Fase | Inhoud | Deliverables | Status |
|---|---|---|---|
| **Fase 1** | Hybride loader + PHARMA-analyser | Data ingeladen, KPI's berekend | ⏳ Gepland |
| **Fase 2** | Jinja2-templates + i18n NL/FR | Eerste rapporten PHARMA NL+FR | ⏳ Gepland |
| **Fase 3** | Matrix-exporter | Cross-pijler vergelijking | ⏳ Gepland |
| **Fase 4** | CARE / CARE ADMIN / ERP4HC | Alle 4 pillar-analysers actief | ⏳ Gepland |
| **Fase 5** | Streamlit dashboard | Interactief dashboard NL/FR | ⏳ Gepland |
| **Fase 6** | ZORGI overall aggregatie | ZORGI-rapport + ZORGI-matrix | ⏳ Gepland |

### 6.2 Migratieaanpak

Uit het bestaande `Customer Satisfaction`-project wordt enkel de **bewezen analyselogica**
overgenomen. Deze wordt herschreven conform de nieuwe `core/`-architectuur.
Het oude project blijft beschikbaar als referentie, niet als codebase.

---

## 7. Mappenstructuur

```text
CSAT-Compass/
├── src/
│   ├── csat/
│   │   ├── config/
│   │   │   ├── settings.py          ← DB-connectie, paden, constanten
│   │   │   └── pillars.py           ← pijler-definities (naam, kleur, richting)
│   │   ├── core/
│   │   │   ├── loaders/
│   │   │   │   ├── base_loader.py   ← abstracte interface
│   │   │   │   ├── sql_loader.py    ← pyodbc/sqlalchemy
│   │   │   │   └── csv_loader.py    ← pandas read_csv/read_excel
│   │   │   ├── analysers/
│   │   │   │   ├── base_analyser.py   ← gedeelde logica (trends, KPI's)
│   │   │   │   └── pillar_analyser.py ← pillar-specifieke berekeningen
│   │   │   └── exporters/
│   │   │       ├── report_exporter.py    ← Jinja2 → MD + PDF
│   │   │       ├── matrix_exporter.py    ← vergelijkingsmatrix
│   │   │       └── dashboard_exporter.py ← Streamlit helpers
│   │   ├── pillars/
│   │   │   ├── zorgi/         ← aggregeert de 4 andere pijlers
│   │   │   ├── pharma/        ← referentie-implementatie (piloot)
│   │   │   ├── care/
│   │   │   ├── care_admin/
│   │   │   └── erp4hc/
│   │   ├── i18n/
│   │   │   ├── nl.json        ← alle labels/teksten Nederlands
│   │   │   └── fr.json        ← alle labels/teksten Frans
│   │   └── utils/
│   │       ├── logger.py      ← loguru wrapper
│   │       └── date_utils.py  ← datumhelpers
│   └── dashboard/
│       └── app.py             ← Streamlit dashboard (NL/FR toggle)
├── docs/
│   ├── templates/
│   │   ├── rapport-pijler.md.j2   ← Jinja2 rapport-template
│   │   ├── rapport-zorgi.md.j2    ← Jinja2 ZORGI overall-template
│   │   └── matrix.md.j2           ← vergelijkingsmatrix template
│   ├── 01-strategisch/
│   ├── 02-tactisch/fasen/
│   └── 03-operationeel/
├── data/                 ← ticketingdata (niet in Git)
├── output/               ← gegenereerde rapporten (niet in Git)
├── tests/
├── scripts/
│   └── run_analysis.py
├── logs/
├── archive/
└── WIP/
```

---

## 8. Team en rapportage

### 8.1 Projectteam

| Rol | Naam |
|---|---|
| Project Manager | Danny Depecker |
| Teamlid | Tom De Laere |
| Teamlid | Wilfried Mertens |
| Teamlid | Frédéric Robinet |
| Teamlid | Thomas Desmet |

### 8.2 Rapportagekanalen

| Doelpubliek         | Frequentie | Format                           |
|---------------------|---|----------------------------------|
| ZORGI management    | Maandelijks | Rapport NL + FR                  |
| Alle pijlerteams    | Maandelijks | Pijler-specifiek rapport NL + FR |
| Management overview | Maandelijks | Streamlit dashboard NL/FR        |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur               |
| ------ | ---------- | ----------------------------------------------- |----------------------|
| 1.0 | 18/03/2026 | Initiële versie — basis advies MCQ-sessie verwerkt | Danny Depecker + GHC |
