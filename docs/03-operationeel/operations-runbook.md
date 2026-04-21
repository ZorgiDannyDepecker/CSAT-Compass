# CSAT-Compass - Operations Runbook

**Versie:** 1.1
**Laatst bijgewerkt:** 21/04/2026

**Doel:** Operationele procedures voor de dagelijkse en maandelijkse werking van CSAT-Compass
**Type:** Runbook
**Auteur:** Danny Depecker + GHC
**Status:** Actief

**Bestandsnaam:** operations-runbook.md
**Path:** docs/03-operationeel/

---

## 1. Omgeving activeren

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\Activate.ps1
```

Verifieer de teststand na grote wijzigingen:

```powershell
.venv\Scripts\python.exe -m pytest --no-cov -q
```

---

## 2. Maandelijkse run — standaardprocedure

### Stap 1 — Voer de batch-runner uit

```powershell
.venv\Scripts\python.exe scripts/run_monthly.py --month YYYY-MM
```

### Stap 2 — Controleer de output

- Verwacht: **30 bestanden** in `output/YYYY-MM-DD/{pijler}/` (per pijler een submap)
  - 10 matrices (NL + FR per pijler)
  - 10 evolutierapporten (NL + FR per pijler)
  - 10 PNG-visualisaties (NL + FR per pijler)
- Controleer de consolefeedback op fouten (`[FOUT]`)

### Stap 3 — Verspreid de rapporten

- NL-rapporten: intern PHARMA-team
- FR-rapporten: Franstalige ziekenhuiscontacten
- Dashboard: CEO Eric + COO Christian (Fase 5 — gepland)

---

## 3. Noodprocedure — SQL niet beschikbaar

Als de connectie naar `ZRG0014WI/Lerni_DB` niet beschikbaar is:

### 3a — Controleer de fallback-CSV

```powershell
Get-ChildItem data\fallback\ | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

### 3b — Maak een verse snapshot als de CSV verouderd is

```powershell
.venv\Scripts\python.exe scripts/export_data.py --snapshot
```

### 3c — Voer de maandelijkse run uit met CSV-fallback

```powershell
.venv\Scripts\python.exe scripts/run_monthly.py --month YYYY-MM --force-csv
```

---

## 4. Individuele scripts

### Matrix alleen

```powershell
.venv\Scripts\python.exe scripts/generate_matrix.py `
    --from 2026-01 --to 2026-03 --pillar pharma --lang both
```

### Evolutierapport één pijler

```powershell
.venv\Scripts\python.exe scripts/generate_evolution.py `
    --pillar pharma `
    --baseline 2025-01 2025-12 `
    --current 2026-01 2026-03 `
    --chart
```

### Evolutierapporten alle pijlers

```powershell
.venv\Scripts\python.exe scripts/generate_all_evolutions.py `
    --baseline 2025-01 2025-12 `
    --current 2026-01 2026-03 `
    --chart
```

### Data exporteren (snapshot)

```powershell
.venv\Scripts\python.exe scripts/export_data.py --snapshot
.venv\Scripts\python.exe scripts/export_data.py --year 2025
.venv\Scripts\python.exe scripts/export_data.py --all
```

---

## 5. Databron

| Parameter | Waarde |
|---|---|
| Server | `ZRG0014WI/Lerni_DB` |
| View | `[dbo].[V_CSAT_1]` |
| Filterkolom | `product_domain` |
| Fallback-pad | `data/fallback/` |
| CSV-omgevingsvariabele | `CSAT_CSV_FALLBACK_PATH` |

**Fallback activeren via omgevingsvariabele:**

```powershell
$env:CSAT_CSV_FALLBACK_PATH = "data\fallback"
```

---

## 6. Logs

Logbestanden staan in `logs/`. Bij onverwachte fouten:

```powershell
Get-ChildItem logs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 3
Get-Content logs\<recentste-logbestand>.log | Select-Object -Last 50
```

---

## 7. CI/CD

GitHub Actions voert bij elke push uit:

- `pytest` op Python 3.11, 3.12 en 3.13
- Coverage-rapport naar Codecov

Lokale lint voor commit:

```powershell
.\tools\lint.ps1
```

---

## 8. Referenties

| Document | Beschrijving |
|---|---|
| `docs/03-operationeel/tools/run-monthly.md` | Gebruiksgids batch-runner |
| `docs/03-operationeel/tools/export-data.md` | Gebruiksgids data-export |
| `docs/03-operationeel/kwaliteitscontrole.md` | Kwaliteitscontroles op output |
| `docs/02-tactisch/implementatie-gids.md` | Overzicht alle implementatiefasen |
| `docs/01-strategisch/architectuur-beslissingen.md` | ADRs — alle architectuurkeuzes |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 26/03/2026 | Initiële versie — fasen 1 t/m 3e operationeel | Danny Depecker + GHC |
