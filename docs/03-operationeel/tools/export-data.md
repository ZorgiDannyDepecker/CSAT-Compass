# CSAT-Compass - export_data.py

**Versie:** 1.0  
**Laatst bijgewerkt:** 20/03/2026

**Doel:** Handleiding voor het data-exportscript — exporteert V_CSAT_1 naar CSV  
**Type:** Reference  
**Auteur:** Danny Depecker
**Status:** Approved

**Bestandsnaam:** export-data.md  
**Path:** docs/03-operationeel/tools/

---

## 1. Doel

`scripts/export_data.py` exporteert ticketdata vanuit de SQL Server view `[dbo].[V_CSAT_1]`
naar een CSV-bestand in de `output/`-map. Het script is bedoeld als verkennings- en
validatiehulpmiddel — bijvoorbeeld om pijlertoewijzingen te controleren of data in Excel
te analyseren voor een rapportageperiode.

Het script maakt gebruik van de standaard `get_loader()` factory: als de SQL-connectie
beschikbaar is, wordt die gebruikt; anders valt het script terug op de CSV-fallback in `data/`.

---

## 2. Locatie

```text
scripts/export_data.py
```

> 💡 `scripts/` bevat uitvoerbare runners. De onderliggende logica (loaders, filters)
> staat in `src/csat/` en wordt door dit script geïmporteerd.

---

## 3. Gebruik

Activeer eerst de virtuele omgeving en roep het script aan vanuit de projectroot:

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\python.exe scripts/export_data.py [opties]
```

---

## 4. Opties

| Optie | Type | Standaard | Beschrijving |
| ------------- | ----- | --------- | ------------------------------------------------- |
| `--year` | `int` | `2025` | Exporteer tickets aangemaakt in dit jaar |
| `--since` | `int` | — | Exporteer van 01/01/jaar tot vandaag (meerdere jaren) |
| `--all` | vlag | uit | Exporteer de volledige dataset zonder filter |
| `-h / --help` | vlag | — | Toon helpbericht en sluit af |

> ⚠️ De opties sluiten elkaar uit. Prioriteit: `--all` > `--since` > `--year`.  
> Als geen optie meegegeven wordt, is `--year 2025` de standaard.

---

## 5. Voorbeelden

### 5.1 2025-data exporteren (standaard)

```powershell
.venv\Scripts\python.exe scripts/export_data.py
```

**Output:** `output/v_csat_1_2025.csv`

### 5.2 Specifiek jaar exporteren

```powershell
.venv\Scripts\python.exe scripts/export_data.py --year 2026
```

**Output:** `output/v_csat_1_2026.csv`

### 5.3 Meerdere jaren exporteren — 01/01/2025 tot vandaag

```powershell
.venv\Scripts\python.exe scripts/export_data.py --since 2025
```

**Output:** `output/v_csat_1_2025-heden.csv`

> 💡 Gebruik dit voor de CSAT-baseline vs. lopend jaar analyse: bevat zowel de
> volledige 2025-data als alle beschikbare 2026-tickets.

### 5.4 Volledige dataset exporteren

```powershell
.venv\Scripts\python.exe scripts/export_data.py --all
```

**Output:** `output/v_csat_1_volledig.csv`

### 5.5 Help tonen

```powershell
.venv\Scripts\python.exe scripts/export_data.py --help
```

---

## 6. Uitvoerbestanden

Bestanden worden weggeschreven naar de `output/`-map (niet in Git via `.gitignore`):

| Commando | Bestandsnaam |
| ----------------------------------- | ----------------------------- |
| `--year 2025` (standaard) | `v_csat_1_2025.csv` |
| `--year 2026` | `v_csat_1_2026.csv` |
| `--since 2025` | `v_csat_1_2025-heden.csv` |
| `--all` | `v_csat_1_volledig.csv` |

**CSV-formaat:**

- Scheidingsteken: puntkomma (`;`)
- Codering: UTF-8 met BOM (`utf-8-sig`) — Excel opent dit zonder configuratie
- Kolommen: alle kolommen van `[dbo].[V_CSAT_1]`

**Openen in Excel:**  
`Gegevens → Uit tekst/CSV` — scheidingsteken wordt automatisch herkend dankzij de BOM.

---

## 7. Vereisten

- Virtuele omgeving actief (`.venv`)
- `.env` aanwezig met `CSAT_DB_PASSWORD` voor SQL-connectie
- Bij geen SQL-connectie: CSV-fallbackbestanden aanwezig in `data/fallback/`

---

## 8. Logging

Het script logt naar `logs/csat-compass_YYYY-MM-DD.log` via Loguru.  
Raadpleeg `docs/03-operationeel/operations-runbook.md` voor meer over de logstructuur.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------------------------------------------- | -------------------- |
| 1.0 | 20/03/2026 | Initiële versie | Danny Depecker + GHC |
| 1.1 | 20/03/2026 | --since optie toegevoegd voor meerjarige export | GHC |
