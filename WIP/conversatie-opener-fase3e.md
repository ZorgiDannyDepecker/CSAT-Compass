# CSAT-Compass — Nieuwe conversatie: Fase 3e

**Bestand:** WIP/conversatie-opener-fase3e.md  
**Datum:** 24/03/2026

---

## Tekst om te plakken in de nieuwe conversatie

---

Lees het handover-document `WIP/handover-fase3e-2026-03-24.md` en implementeer daarna **Fase 3e: `run_monthly.py`**.

**Context:**
- Project: CSAT-Compass (`C:\Users\danndepe\Documents\AI\CSAT-Compass`)
- Alle fasen 1 t/m 3d zijn compleet — **515 tests, 100% coverage**
- Fase 3d heeft `--chart` toegevoegd aan de bestaande CLI-scripts

**Wat er gebouwd moet worden:**
`scripts/run_monthly.py` — één commando dat voor een opgegeven maand alle output genereert:

```powershell
# Standaard: vorige maand, alle pijlers, met charts
.venv\Scripts\python.exe scripts/run_monthly.py

# Specifieke maand
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03

# Zonder visualisaties
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --no-charts
```

**Volgorde:**
1. `generate_matrix.py` — matrix pharma, begin jaar t/m doelmaand
2. `generate_all_evolutions.py` — alle pijlers, baseline vorig jaar, current YTD, + `--chart`

**Verwachte teststand na implementatie:** 515 + nieuwe tests, 100% coverage

Start met het lezen van het handover-document, dan implementatie.

---

