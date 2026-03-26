# CSAT-Compass - Fase 3e: run_monthly.py

**Versie:** 1.0
**Laatst bijgewerkt:** 26/03/2026

**Doel:** Implementatie van de maandelijkse batch-runner die alle output in één commando genereert
**Type:** Implementatie
**Auteur:** Danny Depecker + GHC
**Status:** Compleet

**Bestandsnaam:** fase3e-run-monthly.md
**Path:** docs/02-tactisch/fasen/

---

## 1. Overzicht

Fase 3e sluit de evolutie-infrastructuur af met een **batch-runner**. Met één commando
genereert `run_monthly.py` alle maandelijkse output: matrix (NL + FR), evolutierapporten
voor alle pijlers (NL + FR) en optionele PNG-visualisaties (NL + FR per pijler).

De periodelogica is volledig automatisch: `--month` is optioneel en standaard de vorige maand.

**T-shirt:** S (4–8u)
**Afhankelijkheid:** Fase 3a (generate_matrix.py) + Fase 3d (generate_all_evolutions.py + `--chart`)
**Teststand:** 563 tests — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## 2. Deliverables

| Component | Bestand | Status |
|---|---|---|
| Batch-runner | `scripts/run_monthly.py` | ✅ Compleet |
| Tests | `tests/scripts/test_run_monthly.py` | ✅ 43 tests |
| Tool-doc | `docs/03-operationeel/tools/run-monthly.md` | ✅ Compleet |
| Fase-document | `docs/02-tactisch/fasen/fase3e-run-monthly.md` | ✅ Dit bestand |

---

## 3. CLI-interface

```powershell
# Standaard: automatisch vorige maand, alle pijlers, met charts
.venv\Scripts\python.exe scripts/run_monthly.py

# Specifieke maand
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03

# Selectie van pijlers
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --pillar pharma care

# Zonder visualisaties
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --no-charts

# Noodrun bij DB-storing
.venv\Scripts\python.exe scripts/run_monthly.py --month 2026-03 --force-csv
```

| Argument | Type | Beschrijving | Standaard |
|---|---|---|---|
| `--month` | `YYYY-MM` | Doelmaand voor rapportage | `previous_period(today_period())` |
| `--pillar` | lijst | Pijlers voor evolutierapporten | alle 5 |
| `--no-charts` | vlag | Sla PNG-visualisaties over | `False` (charts AAN) |
| `--force-csv` | vlag | SQL omzeilen | `False` |

---

## 4. Periodelogica

De `_derive_periods()` hulpfunctie leidt alle periodestrings automatisch af uit `target_month`:

```python
def _derive_periods(target_month: str) -> dict[str, str]:
    huidig_jaar = target_month[:4]           # "2026"
    vorig_jaar  = str(int(huidig_jaar) - 1) # "2025"
    return {
        "matrix_from":    f"{huidig_jaar}-01",  # "2026-01"
        "matrix_to":      target_month,          # "2026-03"
        "baseline_from":  f"{vorig_jaar}-01",    # "2025-01"
        "baseline_to":    f"{vorig_jaar}-12",    # "2025-12"
        "current_from":   f"{huidig_jaar}-01",   # "2026-01"
        "current_to":     target_month,          # "2026-03"
    }
```

---

## 5. Uitvoeringsvolgorde

```
Stap 1 — Matrix (generate_matrix.py)
         --from {huidig_jaar}-01 --to {target_month}
         --pillar pharma
         --lang both

Stap 2 — Evolutierapporten (generate_all_evolutions.py)
         --baseline {vorig_jaar}-01 {vorig_jaar}-12
         --current {huidig_jaar}-01 {target_month}
         --pillar {args.pillar of alle 5}
         --year {huidig_jaar}
         [--chart indien niet --no-charts]
         [--force-csv indien meegegeven]

Stap 3 — Samenvatting tonen (totaal bestanden + duur)
```

---

## 6. Verwachte output (--month 2026-03, alle pijlers)

```
[CSAT-Compass] Maandelijkse run — maart 2026
============================================
Doelmaand  : 2026-03
Baseline   : 2025-01 → 2025-12
Current    : 2026-01 → 2026-03
Pijlers    : zorgi, pharma, care, care_admin, erp4hc
Charts     : aan (NL + FR)

[1/2] Matrix genereren (pharma) ...
      output\2026-03-26_HHMM\matrix-2026-nl.md
      output\2026-03-26_HHMM\matrix-2026-fr.md

[2/2] Evolutierapporten genereren (5 pijlers) ...
      [OK] [NL] zorgi       → evolutie-zorgi-2026-nl.md
      [OK] [FR] zorgi       → evolutie-zorgi-2026-fr.md
      [OK] [PNG-NL] zorgi   → evolutie-zorgi-2026-nl.png
      [OK] [PNG-FR] zorgi   → evolutie-zorgi-2026-fr.png
      ...

============================================
Totaal: 22 bestanden gegenereerd
Duur  : 18,5 seconden
```

**Volledige outputlijst (22 bestanden):**

| Type | NL | FR |
|---|---|---|
| Matrix | `matrix-2026-nl.md` | `matrix-2026-fr.md` |
| Evolutie zorgi | `evolutie-zorgi-2026-nl.md` | `evolutie-zorgi-2026-fr.md` |
| Evolutie pharma | `evolutie-pharma-2026-nl.md` | `evolutie-pharma-2026-fr.md` |
| Evolutie care | `evolutie-care-2026-nl.md` | `evolutie-care-2026-fr.md` |
| Evolutie care_admin | `evolutie-care_admin-2026-nl.md` | `evolutie-care_admin-2026-fr.md` |
| Evolutie erp4hc | `evolutie-erp4hc-2026-nl.md` | `evolutie-erp4hc-2026-fr.md` |
| PNG zorgi | `evolutie-zorgi-2026-nl.png` | `evolutie-zorgi-2026-fr.png` |
| PNG pharma | `evolutie-pharma-2026-nl.png` | `evolutie-pharma-2026-fr.png` |
| PNG care | `evolutie-care-2026-nl.png` | `evolutie-care-2026-fr.png` |
| PNG care_admin | `evolutie-care_admin-2026-nl.png` | `evolutie-care_admin-2026-fr.png` |
| PNG erp4hc | `evolutie-erp4hc-2026-nl.png` | `evolutie-erp4hc-2026-fr.png` |

---

## 7. Architectuur

```python
# Interne sleutelfuncties
_derive_periods(target_month)  → dict  # pure functie, geen I/O
_month_label_nl(period)        → str   # "2026-03" → "maart 2026"
_run_script(cmd, beschrijving) → None  # subprocess.run + foutafhandeling
parse_args()                   → Namespace
main()                         → None
```

`run_monthly.py` roept `generate_matrix.py` en `generate_all_evolutions.py` aan via `subprocess.run`
— geen directe Python-imports van de generator-functies. Dit houdt de runner onafhankelijk en
testbaar via subprocess-mocks.

---

## 8. Testoverzicht

| Klasse | Tests | Beschrijving |
|---|---|---|
| `TestDerivePeriodsFunc` | 10 | Periodeafleiding: jaren, maanden, grenscases |
| `TestMonthLabelNl` | 5 | Maandlabels NL: jan t/m dec, jaargrens |
| `TestMainMatrixStap` | 5 | Matrix-aanroepargumenten geverifieerd |
| `TestMainEvolutieStap` | 8 | Evolutie-aanroepargumenten + pijlerselectie |
| `TestVlaggen` | 5 | `--no-charts` / `--force-csv` correct doorgegeven |
| `TestFoutafhandeling` | 3 | `sys.exit` bij subprocess returncode ≠ 0 |
| `TestAanroepvolgorde` | 1 | Matrix altijd vóór evolutie |
| **Totaal** | **37** | 100% coverage |

> Testpatroon: `subprocess.run` gemockt, `sys.argv` gemanipuleerd.
> Geen echte bestanden of DB vereist.

---

## 9. Referentiebestanden

| Bestand | Rol |
|---|---|
| `scripts/generate_matrix.py` | Stap 1 — matrix NL + FR |
| `scripts/generate_all_evolutions.py` | Stap 2 — evolutie + chart |
| `src/csat/utils/date_utils.py` | `previous_period()`, `today_period()`, `parse_period()` |
| `src/csat/config/pillars.py` | `PILLAR_REGISTRY` — volgorde en sleutels |
| `src/csat/config/settings.py` | `OUTPUT_PATH`, `LOG_PATH` |
| `tests/scripts/test_run_monthly.py` | 37 unit tests |
| `docs/03-operationeel/tools/run-monthly.md` | Operationele gebruiksdocumentatie |

---

## 10. Relatie tot andere fasen

```text
Fase 3a ──► generate_matrix.py ──┐
Fase 3d ──► generate_all_evolutions.py + --chart ──┤
                                                    ▼
                                         Fase 3e: run_monthly.py
                                         (één commando → alle output)
```

**Volgende stap:** Fase 4 — CARE / CARE ADMIN / ERP4HC pijlerspecifieke config

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 26/03/2026 | Initiële versie | Danny Depecker + GHC |
