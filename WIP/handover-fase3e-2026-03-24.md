# CSAT-Compass - Handover Fase 3e

**Versie:** 1.0  
**Laatst bijgewerkt:** 24/03/2026  

**Doel:** Contextoverdracht voor nieuwe conversatie — Fase 3e (run_monthly.py)  
**Type:** Reference  
**Auteur:** Danny Depecker + GHC  
**Status:** Approved  

**Bestandsnaam:** handover-fase3e-2026-03-24.md  
**Path:** WIP/

---

## 1. Projectcontext

**Project:** CSAT-Compass — geautomatiseerde klanttevredenheidsanalyse voor ZORGI  
**Doel:** Maandelijkse CSAT-rapporten (NL + FR) voor 4 pijlers + ZORGI-aggregaat  
**Stack:** Python 3.13 · pandas · SQLAlchemy · Jinja2 · matplotlib · Streamlit  
**Databron:** SQL Server view `[dbo].[V_CSAT_1]` op `ZRG0014WI/Lerni_DB`  
**Repo:** `C:\Users\danndepe\Documents\AI\CSAT-Compass`

### Omgeving activeren

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\activate
.venv\Scripts\python.exe -m pytest --no-cov   # verwacht: 515 passed
```

---

## 2. Alle voltooide fasen

**Teststand:** 515 tests — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

| Fase | Inhoud | Status |
|---|---|---|
| Fase 1 | Hybride loader · BaseAnalyser · PillarAnalyser · config | ✅ Compleet |
| Fase 2 | i18n NL/FR · Jinja2 templates · ReportExporter | ✅ Compleet |
| Fase 3a | MatrixExporter · matrix-templates NL/FR · generate_matrix.py | ✅ Compleet |
| Fase 3b | EvolutionResult dataclass · EvolutionAnalyser (data-laag) | ✅ Compleet |
| Fase 3c | EvolutionExporter · templates NL/FR · CLI runners | ✅ Compleet |
| Fase 3d | EvolutionVisualiser · 4-subplot PNG · `--chart` vlag in CLI | ✅ Compleet |

---

## 3. Overzicht bestaande CLI-scripts (input voor Fase 3e)

Fase 3e combineert de volgende scripts in één batch-runner:

### 3.1 generate_matrix.py

```powershell
.venv\Scripts\python.exe scripts/generate_matrix.py `
    --from 2026-01 --to 2026-03 `
    --pillar pharma `
    --lang both
```

| Argument | Beschrijving | Standaard |
|---|---|---|
| `--from` | Startperiode (verplicht) | — |
| `--to` | Eindperiode | huidige maand |
| `--pillar` | Pijlersleutel | `pharma` |
| `--lang` | `nl` / `fr` / `both` | `both` |

**Output:** `output/matrix-{YYYY}-{lang}.md`

### 3.2 generate_all_evolutions.py

```powershell
.venv\Scripts\python.exe scripts/generate_all_evolutions.py `
    --baseline 2025-01 2025-12 `
    --current 2026-01 2026-03 `
    --chart
```

| Argument | Beschrijving | Standaard |
|---|---|---|
| `--baseline` | VAN TOT voor baseline | vorig jaar volledig |
| `--current` | VAN TOT voor huidig | lopend jaar t/m vorige maand |
| `--pillar` | Één of meer pijlers | alle 5 |
| `--year` | Jaarlabel bestandsnaam | afgeleid van current |
| `--chart` | Genereer ook PNG per pijler | False |

**Output per pijler:** `output/evolutie-{pillar}-{jaar}-{lang}.md` + optioneel `evolutie-{pillar}-{jaar}.png`

---

## 4. Fase 3e — te implementeren: run_monthly.py

**T-shirt:** S (4–8u)  
**Doel:** Één commando genereert alle output voor een opgegeven maand

### 4.1 Deliverables

| Component | Bestand |
|---|---|
| Batch runner | `scripts/run_monthly.py` |
| Tests | `tests/scripts/test_run_monthly.py` |

### 4.2 CLI-interface

```powershell
# Standaard: automatisch vorige maand, alle pijlers, met charts
.venv\Scripts\python.exe scripts/run_monthly.py

# Specifieke maand
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03

# Specifieke pijlers
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --pillar pharma care

# Zonder visualisaties
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --no-charts
```

### 4.3 Argumenten

| Argument | Type | Beschrijving | Standaard |
|---|---|---|---|
| `--month` | `YYYY-MM` | Doelmaand voor rapportage | `previous_period(today_period())` |
| `--pillar` | lijst | Pijlers voor evolutierapporten | alle 5 |
| `--no-charts` | vlag | Sla PNG-visualisaties over | False (charts AAN) |

### 4.4 Periodelogica

```python
from csat.utils.date_utils import previous_period, today_period

# --month wordt opgegeven of afgeleid
target_month = args.month or previous_period(today_period())
# bv. "2026-03"

# Jaar afleiden uit target_month
huidig_jaar = target_month[:4]   # "2026"
vorig_jaar = str(int(huidig_jaar) - 1)  # "2025"

# Matrix: begin van het lopende jaar t/m doelmaand
matrix_from = f"{huidig_jaar}-01"   # "2026-01"
matrix_to   = target_month          # "2026-03"

# Baseline: volledig vorig jaar
baseline_from = f"{vorig_jaar}-01"  # "2025-01"
baseline_to   = f"{vorig_jaar}-12"  # "2025-12"

# Current: begin van het lopende jaar t/m doelmaand
current_from = f"{huidig_jaar}-01"  # "2026-01"
current_to   = target_month         # "2026-03"
```

### 4.5 Volgorde uitvoering

```
Stap 1: Matrix (generate_matrix.py)
        --from {matrix_from} --to {matrix_to}
        --pillar pharma (altijd de primaire pijler)
        --lang both

Stap 2: Evolutierapporten (generate_all_evolutions.py)
        --baseline {baseline_from} {baseline_to}
        --current {current_from} {current_to}
        --pillar {args.pillar of alle 5}
        --year {huidig_jaar}
        [--chart indien niet --no-charts]

Stap 3: Voortgangssamenvatting tonen
```

### 4.6 Verwachte output (--month 2026-03, alle pijlers)

```
output/
  matrix-2026-nl.md
  matrix-2026-fr.md
  evolutie-zorgi-2026-nl.md
  evolutie-zorgi-2026-fr.md
  evolutie-pharma-2026-nl.md
  evolutie-pharma-2026-fr.md
  evolutie-care-2026-nl.md
  evolutie-care-2026-fr.md
  evolutie-care_admin-2026-nl.md
  evolutie-care_admin-2026-fr.md
  evolutie-erp4hc-2026-nl.md
  evolutie-erp4hc-2026-fr.md
  evolutie-zorgi-2026.png
  evolutie-pharma-2026.png
  evolutie-care-2026.png
  evolutie-care_admin-2026.png
  evolutie-erp4hc-2026.png
```

### 4.7 Consolefeedback

```
[CSAT-Compass] Maandelijkse run — maart 2026
============================================
Doelmaand  : 2026-03
Baseline   : 2025-01 → 2025-12
Current    : 2026-01 → 2026-03
Pijlers    : zorgi, pharma, care, care_admin, erp4hc
Charts     : aan

[1/2] Matrix genereren (pharma) ...
      output\matrix-2026-nl.md
      output\matrix-2026-fr.md

[2/2] Evolutierapporten genereren (5 pijlers) ...
      [OK] [NL] zorgi      → evolutie-zorgi-2026-nl.md
      [OK] [FR] zorgi      → evolutie-zorgi-2026-fr.md
      ...
      [OK] [PNG] pharma    → evolutie-pharma-2026.png
      ...

============================================
Totaal: 17 bestanden gegenereerd in output\
Duur  : 12,3 seconden
```

---

## 5. Testpatroon

Tests komen in `tests/scripts/test_run_monthly.py`.  
Patroon: mock de individuele generators, verifieer de aanroepargumenten.

```python
from unittest.mock import patch, call
import subprocess, sys

def test_run_monthly_roept_matrix_aan(tmp_path):
    """run_monthly.py roept generate_matrix.py aan met de juiste argumenten."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        # ... aanroep run_monthly.py met --month 2026-03
        # verifieer dat generate_matrix.py aangeroepen werd met juiste args
        ...
```

> ⚠️ **Alternatief testpatroon:** run_monthly.py kan de logica ook direct importeren
> (i.p.v. subprocess) door de `main()`-functies van de bestaande scripts aan te roepen.
> In dat geval mocken we de `get_loader()` en verifiëren we de geëxporteerde bestanden.
> Kies het patroon dat het best aansluit bij de implementatiekeuze.

---

## 6. Referentiebestanden voor Fase 3e

| Bestand | Relevantie |
|---|---|
| `scripts/generate_matrix.py` | Interface + periodelogica navolgen |
| `scripts/generate_all_evolutions.py` | Interface + pijler-loop navolgen |
| `src/csat/utils/date_utils.py` | `previous_period()`, `today_period()`, `parse_period()` |
| `src/csat/config/pillars.py` | `PILLAR_REGISTRY` — volgorde en sleutels |
| `src/csat/config/settings.py` | `OUTPUT_PATH`, `LOG_PATH` |
| `src/csat/utils/logger.py` | `setup_logger()` |

### Data voor testen

```powershell
$env:CSAT_CSV_FALLBACK_PATH = "output"
# v_csat_1_2025-heden.csv aanwezig in output\ — meest volledig

# Handmatig testen:
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03
```

---

## 7. Fasering na 3e

| Fase | Inhoud | T-shirt | Status |
|---|---|---|---|
| **3e** | run_monthly.py — alles in één run | S | **Volgende** |
| Fase 4 | CARE / OAZIS / ERP4HC pijlerspecifieke config | M | ⏳ |
| Fase 5 | Streamlit dashboard NL/FR | L | ⏳ |
| Fase 6 | ZORGI-aggregatie | S | ⏳ |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 24/03/2026 | Initiële versie — handover Fase 3e | Danny Depecker + GHC |

