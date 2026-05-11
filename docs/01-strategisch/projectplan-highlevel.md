# CSAT-Compass - Projectplan High-Level

**Versie:** 1.9
**Laatst bijgewerkt:** 11/05/2026

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

### 3.1 Per maandelijkse run: 30 bestanden + dashboard

| # | Matrix NL | Matrix FR | Evolutie NL | Evolutie FR | PNG NL | PNG FR |
|---|---|---|---|---|---|---|
| 1 | `matrix-zorgi-YYYY-nl.md` | `matrix-zorgi-YYYY-fr.md` | `evolutie-zorgi-YYYY-nl.md` | `evolutie-zorgi-YYYY-fr.md` | `.png` | `.png` |
| 2 | `matrix-pharma-YYYY-nl.md` | `matrix-pharma-YYYY-fr.md` | `evolutie-pharma-YYYY-nl.md` | `evolutie-pharma-YYYY-fr.md` | `.png` | `.png` |
| 3 | `matrix-care-YYYY-nl.md` | `matrix-care-YYYY-fr.md` | `evolutie-care-YYYY-nl.md` | `evolutie-care-YYYY-fr.md` | `.png` | `.png` |
| 4 | `matrix-care_admin-YYYY-nl.md` | `matrix-care_admin-YYYY-fr.md` | `evolutie-care_admin-YYYY-nl.md` | `evolutie-care_admin-YYYY-fr.md` | `.png` | `.png` |
| 5 | `matrix-erp4hc-YYYY-nl.md` | `matrix-erp4hc-YYYY-fr.md` | `evolutie-erp4hc-YYYY-nl.md` | `evolutie-erp4hc-YYYY-fr.md` | `.png` | `.png` |

**Totaal:** 10 matrices + 10 evolutierapporten + 10 PNG's = **30 bestanden** + Streamlit dashboard

**Mappenstructuur:** `output/YYYY-MM-DD/{pijler}/` — per pijler een eigen submap

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

Selectielogica in woorden:

- als een DB-connectie beschikbaar is, gebruikt de `DataLoader` de SQL-bron;
- anders schakelt de loader over naar de CSV-fallback;
- bij fallback wordt een waarschuwing gelogd zodat de run traceerbaar blijft.

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
| **Fase 1** | Hybride loader + PHARMA-analyser | Data ingeladen, KPI's berekend | ✅ Compleet |
| **Fase 2** | Jinja2-templates + i18n NL/FR | Eerste rapporten PHARMA NL+FR | ✅ Compleet |
| **Fase 3** | Matrix + Evolutie + Visualisatie + Batch-runner | Fasen 3a–3e voltooid | ✅ Compleet |
| **Fase 3f** | Evolutie-advieskader | Gap-analyse, beslisrecord, release 1 scope | ✅ Compleet |
| **Fase 3g** | Evolutierapport verfijning | Implementatie release 1 op basis van fase 3f | ✅ Compleet |
| **Fase 4** | CARE / CARE ADMIN / ERP4HC | Alle 4 pillar-analysers actief | ✅ Compleet |
| **Fase 5a** | Streamlit dashboard PHARMA-only | Dashboard PHARMA volledig (6 tabs, NL/FR, pijler-agnostisch) | ✅ Compleet |
| **Fase 5b** | Dashboard UI-verfijning | Tabbalk, samenvatting-tab polish, mini-signaalkaart, vergelijkingstabel | ✅ Compleet |
| **Fase 5c** | Streamlit dashboard overige pijlers | CARE / CARE ADMIN / ERP4HC actief in dashboard | ✅ Compleet |
| **Fase 6** | ZORGI overall aggregatie | ZORGI-rapport + ZORGI-matrix + ZORGI dashboard tab | ✅ Compleet |
| **Fase 7** | Special runner + instelbare begindatum | `run_special.py` — alle pijlers, instelbare startdatum, identieke outputstructuur | ✅ Compleet |

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
| 1.1 | 26/03/2026 | Fase-statussen bijgewerkt: fasen 1 t/m 3 compleet | Danny Depecker + GHC |
| 1.2 | 27/03/2026 | Fase 3f toegevoegd als aparte rij (in planning) | Danny Depecker + GHC |
| 1.3 | 29/03/2026 | Fase 3f hergedefinieerd als advieskader; implementatiefase doorgeschoven naar 3g | Danny Depecker + GHC |
| 1.4 | 31/03/2026 | Fase 3g status bijgewerkt naar Compleet | Danny Depecker + GHC |
| 1.5 | 01/04/2026 | Fase 5 opgesplitst in 5a (PHARMA dashboard) en 5b (overige pijlers); Fase 5a status → In voorbereiding; Fase 6 uitgebreid met ZORGI dashboard tab | Danny Depecker + CD |
| 1.6 | 10/04/2026 | Fase 5a status → In uitvoering; Fase 5b hergedefinieerd als Dashboard UI-verfijning; Fase 5c hernoemd naar overige pijlers; fasering bijgewerkt (5a/5b In uitvoering) | Danny Depecker + GHC |
| 1.7 | 21/04/2026 | Fase 4 + 5a + 5b + 5c → ✅ Compleet; outputspecificatie bijgewerkt naar 30 bestanden + pijler-submappen; bestandsnaamconventie matrix gecorrigeerd | Danny Depecker + GHC |
| 1.8 | 23/04/2026 | Fase 6 status → 🔄 In uitvoering (ZorgiAnalyser actief, dashboard-tab In uitvoering) | Danny Depecker + GHC |
| 1.9 | 11/05/2026 | Fase 6 → ✅ Compleet (ZORGI actief in dashboard + _ACTIVE_PILLARS); Fase 7 toegevoegd (run_special.py operationeel, v0.9.0) | Danny Depecker + GHC |
