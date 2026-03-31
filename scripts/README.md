# scripts/ — CLI-entrypoints

**Doel:** Dunne CLI-wrappers die `src/csat/` aanroepen en maandelijkse workflows orkestreren.
**Patroon:** runner/library — zie [ADR-013](../docs/01-strategisch/architectuur-beslissingen.md#13-adr-013--runnerlibrary-structuur-scripts-vs-src-vs-tools).

---

## Overzicht

| Script | Rol | Manual |
| --- | --- | --- |
| `run_monthly.py` | Maandelijkse batch-runner (matrix + alle evoluties + charts) | [run-monthly.md](../docs/03-operationeel/tools/run-monthly.md) |
| `generate_evolution.py` | Evolutierapport voor één pijler (NL/FR + optionele PNG) | — |
| `generate_all_evolutions.py` | Evolutierapporten voor alle pijlers in één run | — |
| `generate_and_print.py` | Evolutierapport genereren + rechtstreeks afdrukken via PDF | — |
| `generate_matrix.py` | Vergelijkingsmatrix exporteren (NL/FR) | [generate-matrix.md](../docs/03-operationeel/tools/generate-matrix.md) |
| `export_data.py` | Ruwe V_CSAT_1-data exporteren naar CSV | [export-data.md](../docs/03-operationeel/tools/export-data.md) |

---

## Regels

- Scripts bevatten **geen** business logic — alle analyse, export en visualisatie zit in `src/csat/`.
- Scripts importeren altijd vanuit `src/csat/` via `sys.path.insert(0, ROOT / "src")`.
- Nieuwe scripts horen hier **alleen** als ze een CLI-entrypoint zijn.
- Business logic **altijd** in `src/csat/` plaatsen — nooit rechtstreeks in een script.

---

## Verwante mappen

| Map | Inhoud |
| --- | --- |
| `src/csat/` | Alle herbruikbare business logic (analyse, export, visualisatie, i18n) |
| `tools/` | Dev-tooling in PowerShell (`lint.ps1`, `sync-design-system.ps1`) |
