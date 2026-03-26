# CSAT-Compass - run_monthly.py

**Versie:** 1.0
**Laatst bijgewerkt:** 26/03/2026

**Doel:** Operationele gebruiksgids voor de maandelijkse batch-runner
**Type:** Tool-documentatie
**Auteur:** Danny Depecker + GHC
**Status:** Actief

**Bestandsnaam:** run-monthly.md
**Path:** docs/03-operationeel/tools/

---

## Samenvatting

`scripts/run_monthly.py` is de **maandelijkse batch-runner** van CSAT-Compass.
Eén commando genereert alle output voor een opgegeven maand:

- Vergelijkingsmatrix PHARMA (NL + FR)
- Evolutierapporten voor alle 5 pijlers (NL + FR)
- PNG-visualisaties per pijler (NL + FR) — standaard aan

**Normale maandelijkse run:**

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03
```

---

## Gebruik

### Standaardrun (vorige maand automatisch)

```powershell
.venv\Scripts\python.exe scripts/run_monthly.py
```

### Specifieke maand

```powershell
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03
```

### Selectie van pijlers

```powershell
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --pillar pharma care
```

### Zonder PNG-visualisaties

```powershell
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --no-charts
```

### Noodrun (SQL niet beschikbaar)

```powershell
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --force-csv
```

Vereist dat `data/fallback/` een recente CSV-export bevat (zie `export_data.py`).

---

## Argumenten

| Argument | Beschrijving | Standaard |
|---|---|---|
| `--month YYYY-MM` | Doelmaand voor rapportage | vorige maand |
| `--pillar ...` | Pijlers (een of meer) | alle 5: zorgi pharma care care_admin erp4hc |
| `--no-charts` | Sla PNG-visualisaties over | uit (charts AAN) |
| `--force-csv` | SQL omzeilen, CSV-fallback forceren | uit |

---

## Output

Alle bestanden worden weggeschreven naar een **datumstempel-submap** in `output/`:

```text
output/
  YYYY-MM-DD_HHMM/
    matrix-{jaar}-nl.md
    matrix-{jaar}-fr.md
    evolutie-zorgi-{jaar}-nl.md      evolutie-zorgi-{jaar}-fr.md
    evolutie-pharma-{jaar}-nl.md     evolutie-pharma-{jaar}-fr.md
    evolutie-care-{jaar}-nl.md       evolutie-care-{jaar}-fr.md
    evolutie-care_admin-{jaar}-nl.md evolutie-care_admin-{jaar}-fr.md
    evolutie-erp4hc-{jaar}-nl.md     evolutie-erp4hc-{jaar}-fr.md
    evolutie-zorgi-{jaar}-nl.png     evolutie-zorgi-{jaar}-fr.png
    evolutie-pharma-{jaar}-nl.png    evolutie-pharma-{jaar}-fr.png
    evolutie-care-{jaar}-nl.png      evolutie-care-{jaar}-fr.png
    evolutie-care_admin-{jaar}-nl.png evolutie-care_admin-{jaar}-fr.png
    evolutie-erp4hc-{jaar}-nl.png    evolutie-erp4hc-{jaar}-fr.png
```

**Totaal standaard:** 22 bestanden (2 matrix + 10 rapporten + 10 PNG)

---

## Periodelogica

| Parameter | Afleiding | Voorbeeld (--month 2026-03) |
|---|---|---|
| Matrix van | `{huidig_jaar}-01` | `2026-01` |
| Matrix tot | `target_month` | `2026-03` |
| Baseline van | `{vorig_jaar}-01` | `2025-01` |
| Baseline tot | `{vorig_jaar}-12` | `2025-12` |
| Current van | `{huidig_jaar}-01` | `2026-01` |
| Current tot | `target_month` | `2026-03` |

---

## Probleemoplossing

| Symptoom | Oorzaak | Oplossing |
|---|---|---|
| `ConnectionError` bij start | SQL Server niet bereikbaar | Gebruik `--force-csv` |
| CSV niet gevonden | `data/fallback/` leeg | Voer eerst `export_data.py --snapshot` uit |
| `0 rijen geladen` | Verkeerde periode of lege CSV | Controleer `--month` en de CSV-inhoud |
| Script stopt bij stap 1 | Matrix-fout | Controleer `logs/` voor details |
| Ontbrekende pijler in output | Pijler config leeg (Fase 4 nog niet compleet) | Beperk met `--pillar pharma` |

---

## Gerelateerde scripts

| Script | Gebruik |
|---|---|
| `scripts/generate_matrix.py` | Enkel de matrix genereren |
| `scripts/generate_evolution.py` | Evolutierapport voor één pijler |
| `scripts/generate_all_evolutions.py` | Evolutierapporten voor alle pijlers |
| `scripts/export_data.py` | CSV-snapshot aanmaken voor fallback |

---

## Implementatiedocumentatie

Zie `docs/02-tactisch/fasen/fase3e-run-monthly.md` voor de volledige technische beschrijving.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 26/03/2026 | Initiële versie | Danny Depecker + GHC |
