# CSAT-Compass - Fase 1: Data-analyse en hybride loader

**Versie:** 1.1  
**Laatst bijgewerkt:** 19/03/2026  

**Doel:** Uitwerking van Fase 1 — hybride dataloader en PHARMA-analyser als referentie-implementatie  
**Type:** Implementatie  
**Auteur:** Danny Depecker + GHC  
**Status:** In Progress  

**Bestandsnaam:** fase1-data-analyse.md  
**Path:** docs/02-tactisch/fasen/  

---

## Inhoudsopgave

1. [Doelstelling](#1-doelstelling)
2. [Deliverables](#2-deliverables)
3. [Databron en connectie](#3-databron-en-connectie)
4. [Implementatiestappen](#4-implementatiestappen)
5. [KPI-definities PHARMA](#5-kpi-definities-pharma)
6. [Acceptatiecriteria](#6-acceptatiecriteria)
7. [Afhankelijkheden](#7-afhankelijkheden)

---

## 1. Doelstelling

Fase 1 legt de **datalaadfundamenten** van CSAT-Compass:

- Een hybride loader die automatisch kiest tussen SQL en CSV
- De PHARMA-pillar-analyser als referentie-implementatie voor alle andere pijlers
- Verifieerbare KPI-berekeningen met unit tests

Na Fase 1 kan de pipeline PHARMA-data inladen en de basisanalyse uitvoeren,
klaar voor rapportage in Fase 2.

---

## 2. Deliverables

| Bestand | Beschrijving | Status |
|---|---|---|
| `src/csat/core/loaders/base_loader.py` | Abstracte loader-interface | ⏳ |
| `src/csat/core/loaders/sql_loader.py` | SQL-connectie via sqlalchemy | ⏳ |
| `src/csat/core/loaders/csv_loader.py` | CSV/Excel loader via pandas | ⏳ |
| `src/csat/core/analysers/base_analyser.py` | Gedeelde analyselogica | ⏳ |
| `src/csat/core/analysers/pillar_analyser.py` | Pillar-specifieke berekeningen | ⏳ |
| `src/csat/pillars/pharma/config.py` | PHARMA KPI-configuratie | ⏳ |
| `src/csat/pillars/pharma/analyser.py` | PHARMA-analyser (erft base) | ⏳ |
| `src/csat/config/settings.py` | DB-connectie, paden, constanten | ⏳ |
| `src/csat/config/pillars.py` | Pijler-definities | ⏳ |
| `tests/core/test_loaders.py` | Unit tests voor loaders | ⏳ |
| `tests/pillars/test_pharma_analyser.py` | Unit tests PHARMA-analyser | ⏳ |

---

## 3. Databron en connectie

### 3.1 PowerBI databaseview

### 3.1 PowerBI databaseview

| Parameter | Waarde |
|---|---|
| Server | `ZRG0014WI` |
| Database | `Lerni_DB` |
| View | `V_CSAT_1` |
| Schema | `dbo` |
| Authenticatie | SQL Server authenticatie |
| Gebruiker | `csat_user` |
| ODBC Driver | `ODBC Driver 18 for SQL Server` (18 en 17 beide geïnstalleerd) |
| Connectiestring | Via `.env` — nooit in Git |

### 3.2 Omgevingsvariabelen (.env)

```text
# .env — nooit committen naar Git (uitgesloten via .gitignore)
CSAT_DB_SERVER=ZRG0014WI
CSAT_DB_NAME=Lerni_DB
CSAT_DB_SCHEMA=dbo
CSAT_DB_VIEW=V_CSAT_1
CSAT_DB_USER=csat_user
CSAT_DB_PASSWORD=          ← in te vullen door Danny
CSAT_DB_DRIVER=ODBC Driver 18 for SQL Server
CSAT_CSV_FALLBACK_PATH=data/fallback/
CSAT_OUTPUT_PATH=output/
CSAT_LOG_LEVEL=INFO
```

Template beschikbaar in `.env.example` (wel in Git).

### 3.3 Kolomnamen V_CSAT_1 (bevestigd)

```sql
SELECT [key], [issue_type], [priority], [summary], [score], [comment],
       [satisfaction_date], [created], [hospital], [product],
       [product_domain], [project_key]
FROM [lerni_db].[dbo].[V_CSAT_1]
```

| Kolom | Type | Beschrijving |
|---|---|---|
| `key` | string | Uniek ticket-ID (bv. SD30-1234) |
| `issue_type` | string | Type ticket |
| `priority` | string | Low / Medium / High / Critical |
| `summary` | string | Korte omschrijving ticket |
| `score` | numeric | CSAT-tevredenheidsscore (bereik TBD na eerste exploratie) |
| `comment` | string | Klantcommentaar bij de score |
| `satisfaction_date` | date | Datum waarop de score werd ingegeven |
| `created` | date | Aanmaakdatum ticket |
| `hospital` | string | Ziekenhuisnaam |
| `product` | string | Pijler-identificatie (PHARMA / CARE / CARE ADMIN / ERP4HC) |
| `product_domain` | string | Productdomein / categorie |
| `project_key` | string | Projectsleutel (bv. SD30) |

> 💡 **Opmerking:** De view bevat geen `status`- of `resolved_date`-kolom.
> De **sluitingsratio** wordt geherdefinieerd als het percentage tickets
> dat een `score` heeft gekregen (reactiegraad). Dit wordt bevestigd na
> de eerste data-exploratie.

---

## 4. Implementatiestappen

### 4.1 Omgeving voorbereiden

```powershell
# Virtuele omgeving activeren
.venv\Scripts\activate

# Nieuwe afhankelijkheden installeren
pip install sqlalchemy pyodbc streamlit plotly babel
pip freeze > requirements.txt
```

### 4.2 Loader-hiërarchie opbouwen

Volgorde van implementatie:

```text
1. base_loader.py      ← abstracte klasse met load() methode
2. csv_loader.py       ← eenvoudigste, direct testbaar
3. sql_loader.py       ← bouwt op base_loader
4. __init__.py         ← exporteert DataLoader factory-functie
```

De factory-functie selecteert automatisch de juiste loader:

```python
# Pseudocode factory
def get_loader(settings) -> BaseLoader:
    if settings.db_available():
        return SqlLoader(settings.DB_CONN)
    logger.warning("DB niet bereikbaar — fallback naar CSV")
    return CsvLoader(settings.CSV_FALLBACK_PATH)
```

### 4.3 PHARMA-analyser opbouwen

Volgorde van implementatie:

```text
1. base_analyser.py            ← gedeelde KPI-berekeningen
2. pillar_analyser.py          ← pillar-filtering + aggregatie
3. pillars/pharma/config.py    ← PHARMA-specifieke drempelwaarden
4. pillars/pharma/analyser.py  ← erft pillar_analyser, gebruikt pharma/config
```

### 4.4 Configuratie vastleggen

```text
config/settings.py  ← DB-conn (via os.environ), paden, logging-niveau
config/pillars.py   ← PILLAR_REGISTRY dict met naam, kleur, richting per pijler
```

---

## 5. KPI-definities PHARMA

| KPI | Berekening | Drempel | Status |
|---|---|---|---|
| Gemiddelde CSAT-score | `AVG(score)` | TBD na exploratie | ⚠️ |
| Score-distributie | `COUNT per score-waarde / total * 100` | TBD | ⚠️ |
| Reactiegraad (sluitingsratio) | `tickets met score / totaal tickets * 100` | ≥ 85% | ✅ |
| High/Critical ratio | `COUNT priority IN (High, Critical) / total * 100` | ≤ 15% | ✅ |
| Trend MoM (gemiddelde score) | Verschil `AVG(score)` t.o.v. vorige maand | TBD na exploratie | ⚠️ |
| Baseline vergelijking | Verschil t.o.v. 2025-gemiddelde | TBD | ⚠️ |

> 💡 Score-bereik en drempelwaarden voor gemiddelde score en trend
> worden afgeleid na de eerste data-exploratie op V_CSAT_1.

---

## 6. Acceptatiecriteria

Fase 1 is **afgerond** wanneer:

- [ ] `CsvLoader` laadt een PHARMA-testbestand correct in een pandas DataFrame
- [ ] `SqlLoader` maakt verbinding met `ZRG0014WI/Lerni_DB` en levert een DataFrame
- [ ] Fallback-logica schakelt automatisch van SQL naar CSV bij connectiefout
- [ ] `PharmaAnalyser` berekent reactiegraad en High/Critical ratio correct op testdata
- [ ] Alle unit tests slagen (`pytest tests/ -v`)
- [ ] Logging toont duidelijk welke loader actief is

---

## 7. Afhankelijkheden

| Afhankelijkheid | Type | Status |
|---|---|---|
| Wachtwoord `csat_user` invullen in `.env` | Configuratie | ⚠️ Te doen door Danny |
| ODBC Driver 18 for SQL Server geïnstalleerd | Software | ✅ Bevestigd |
| Score-bereik V_CSAT_1 bepalen (exploratie) | Inhoudelijk | ⚠️ Na eerste connectie |
| Drempelwaarden gemiddelde score + trend MoM | Inhoudelijk | ⚠️ Na eerste exploratie |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ------------------------------------------------------------ | -------------------- |
| 1.0 | 18/03/2026 | Initiële versie | Danny Depecker + GHC |
| 1.1 | 19/03/2026 | DB-gegevens, kolomnamen V_CSAT_1 en KPI-tabel ingevuld | Danny Depecker + GHC |

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------------------- | -------------------- |
| 1.0 | 18/03/2026 | Initiële versie | Danny Depecker + GHC |
