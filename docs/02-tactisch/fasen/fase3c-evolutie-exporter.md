# CSAT-Compass - Fase 3c: EvolutionExporter + templates

**Versie:** 1.0
**Laatst bijgewerkt:** 26/03/2026

**Doel:** Implementatie van EvolutionExporter, Jinja2-templates NL/FR en CLI-runners voor evolutierapporten
**Type:** Implementatie
**Auteur:** Danny Depecker + GHC
**Status:** Compleet

**Bestandsnaam:** fase3c-evolutie-exporter.md
**Path:** docs/02-tactisch/fasen/

---

## 1. Overzicht

Fase 3c voegt de **exportlaag** toe aan de evolutie-infrastructuur van CSAT-Compass.
De `EvolutionExporter` vertaalt een `EvolutionResult`-object (Fase 3b) naar volledige
Nederlandstalige en Franstalige markdown-rapporten via Jinja2-templates en het i18n-systeem.

Twee CLI-runners maken de generatie toegankelijk vanuit de commandoregel:
`generate_evolution.py` (één pijler) en `generate_all_evolutions.py` (alle pijlers).

**T-shirt:** M (8–24u)
**Afhankelijkheid:** Fase 3b (EvolutionResult + EvolutionAnalyser) + Fase 2 (ReportExporter patroon + i18n)
**Teststand:** 472 tests — 100% coverage — CI stabiel

---

## 2. Deliverables

| Component | Bestand | Status |
|---|---|---|
| `EvolutionExporter` | `src/csat/core/exporters/evolution_exporter.py` | ✅ Compleet |
| Template Nederlands | `docs/templates/evolutie-nl.md.j2` | ✅ Compleet |
| Template Frans | `docs/templates/evolutie-fr.md.j2` | ✅ Compleet |
| CLI enkelvoudig | `scripts/generate_evolution.py` | ✅ Compleet |
| CLI batch | `scripts/generate_all_evolutions.py` | ✅ Compleet |
| Tests | `tests/core/test_evolution_exporter.py` | ✅ 54 tests |
| Fase-document | `docs/02-tactisch/fasen/fase3c-evolutie-exporter.md` | ✅ Dit bestand |

### 2.1 Bestandsnaamconventie output

```text
evolutie-{pillar}-{jaar}-{lang}.md

Voorbeelden:
  evolutie-pharma-2026-nl.md
  evolutie-pharma-2026-fr.md
  evolutie-zorgi-2026-nl.md
```

---

## 3. Architectuur

### 3.1 EvolutionExporter — klasse-interface

```python
class EvolutionExporter:
    def __init__(
        self,
        lang: str = "nl",
        templates_path: Path | None = None,
        output_path: Path | None = None,
    ) -> None:
        """
        lang:            Taalcode — 'nl' (standaard) of 'fr'
        templates_path:  Pad naar Jinja2-templates (standaard TEMPLATES_PATH)
        output_path:     Uitvoermap (standaard OUTPUT_PATH)
        """

    def render(self, result: EvolutionResult) -> str:
        """Render het rapport als markdown-string (geen bestandsschrijving)."""

    def export(self, result: EvolutionResult, year: str | None = None) -> Path:
        """Schrijft rapport → output_path/evolutie-{pillar}-{jaar}-{lang}.md"""
```

### 3.2 Helperfuncties

| Functie | Beschrijving |
|---|---|
| `_fmt_delta(value, decimals)` | Delta formatteren met +/- prefix (ZORGI-getalnotatie) |

### 3.3 Template-context — variabelen

De `_build_context()` methode vult de Jinja2-context met alle benodigde data:

| Variabele | Type | Beschrijving |
|---|---|---|
| `t` | dict | i18n-vertalingen voor de gekozen taal |
| `pillar_name` | str | Weergavenaam pijler (NL of FR) |
| `baseline_label` / `current_label` | str | Periodeomschrijving (bv. "2025", "jan-mrt 2026") |
| `baseline_total` / `current_total` | int | Totaal tickets per periode |
| `baseline_avg_score` / `current_avg_score` | float | Gemiddelde CSAT-score |
| `delta_avg_score` | float | Verschil in gemiddelde score |
| `baseline_hc_ratio` / `current_hc_ratio` | float | % High/Critical tickets |
| `monthly_timeline` | list[MonthlyDataPoint] | Maandelijkse tijdlijn |
| `by_issue_type` | list[IssueTypeComparison] | Analyse per tickettype |
| `by_priority` | list[PriorityComparison] | Analyse per prioriteit |
| `hospital_comparison` | list[HospitalComparison] | Ziekenhuisvergelijking |
| `hospitals_disappeared` / `hospitals_new` | list[str] | Verdwenen / nieuwe ziekenhuizen |
| `negative_themes` | list[ThemeEvolution] | Negatieve feedbackthema's |
| `kpi_status_*` | str | KPI-statuslabel (✅ OK / ⚠️ Aandacht / 🔴 Risico) |

### 3.4 Template-structuur

De Jinja2-templates volgen de 8-sectie structuur van het evolutierapport:

```text
1. Kerncijfers        — KPI-tabel baseline vs huidig
2. Maandelijkse tijdlijn
3. KPI-status         — tabel per KPI met status baseline en huidig
4. Analyse per type   — issue_type breakdown
5. Analyse per prioriteit + responstijd per score-niveau
6. Ziekenhuisvergelijking + verdwenen/nieuwe
7. Negatieve feedbackthema's
8. Conclusie en aanbevelingen
```

Tweetaligheid is volledig gestuurd via `i18n/nl.json` en `i18n/fr.json`.
Één templatewijziging = beide taalversies bijgewerkt.

---

## 4. CLI-runners

### 4.1 generate_evolution.py — enkelvoudig

```powershell
# Standaard: pharma, both, vorige maand
.venv\Scripts\python.exe scripts/generate_evolution.py

# Specifieke pijler en periode
.venv\Scripts\python.exe scripts/generate_evolution.py `
    --pillar pharma `
    --baseline 2025-01 2025-12 `
    --current 2026-01 2026-03

# Alleen NL
.venv\Scripts\python.exe scripts/generate_evolution.py --pillar pharma --lang nl

# Met aangepaste labels
.venv\Scripts\python.exe scripts/generate_evolution.py `
    --pillar pharma `
    --baseline-label "Volledig 2025" `
    --current-label "jan-mrt 2026"

# Noodrun — CSV-fallback forceren
.venv\Scripts\python.exe scripts/generate_evolution.py --pillar pharma --force-csv
```

| Argument | Beschrijving | Standaard |
|---|---|---|
| `--pillar` | Pijlersleutel | `pharma` |
| `--baseline` | VAN TOT voor baseline | vorig jaar volledig |
| `--current` | VAN TOT voor huidig | lopend jaar t/m vorige maand |
| `--baseline-label` | Aangepast label baseline | afgeleid van periodes |
| `--current-label` | Aangepast label huidig | afgeleid van periodes |
| `--lang` | `nl` / `fr` / `both` | `both` |
| `--year` | Jaarlabel bestandsnaam | afgeleid van current_label |
| `--output` | Uitvoermap | `OUTPUT_PATH` |
| `--chart` | Genereer ook PNG (Fase 3d) | `False` |
| `--force-csv` | SQL omzeilen | `False` |

### 4.2 generate_all_evolutions.py — batch

```powershell
# Alle 5 pijlers, standaard periodes
.venv\Scripts\python.exe scripts/generate_all_evolutions.py

# Met expliciete periodes
.venv\Scripts\python.exe scripts/generate_all_evolutions.py `
    --baseline 2025-01 2025-12 `
    --current 2026-01 2026-03

# Selectie van pijlers
.venv\Scripts\python.exe scripts/generate_all_evolutions.py --pillar pharma care

# Met visualisaties (Fase 3d)
.venv\Scripts\python.exe scripts/generate_all_evolutions.py --chart
```

| Argument | Beschrijving | Standaard |
|---|---|---|
| `--pillar` | Één of meer pijlers | alle 5 |
| `--baseline` | VAN TOT voor baseline | vorig jaar volledig |
| `--current` | VAN TOT voor huidig | lopend jaar t/m vorige maand |
| `--year` | Jaarlabel bestandsnaam | afgeleid van current_label |
| `--chart` | Genereer ook PNG per pijler NL + FR | `False` |
| `--force-csv` | SQL omzeilen | `False` |
| `--output` | Uitvoermap | `OUTPUT_PATH` |

---

## 5. Python API

```python
from csat.core.analysers.evolution_analyser import EvolutionAnalyser
from csat.core.exporters.evolution_exporter import EvolutionExporter
from pathlib import Path

# Analyse (Fase 3b)
analyser = EvolutionAnalyser(df, pillar_key="pharma")
result = analyser.analyse(
    baseline_periods=["2025-01", ..., "2025-12"],
    current_periods=["2026-01", "2026-02", "2026-03"],
)

# Export NL
exporter_nl = EvolutionExporter(lang="nl")
pad_nl = exporter_nl.export(result, year="2026")
# → output/evolutie-pharma-2026-nl.md

# Export FR
exporter_fr = EvolutionExporter(lang="fr")
pad_fr = exporter_fr.export(result, year="2026")
# → output/evolutie-pharma-2026-fr.md

# Render zonder schrijven
content = exporter_nl.render(result)
```

---

## 6. Referentiebestanden

| Bestand | Rol |
|---|---|
| `src/csat/core/analysers/evolution_analyser.py` | Input — EvolutionAnalyser.analyse() |
| `src/csat/core/analysers/evolution_result.py` | Input — EvolutionResult dataclass (Fase 3b) |
| `src/csat/core/exporters/report_exporter.py` | Patroon render()/export(), `_format_number`, `_format_date` |
| `src/csat/i18n/nl.json` / `fr.json` | i18n-vertalingen — labels en teksten |
| `docs/templates/evolutie-nl.md.j2` | Jinja2-template Nederlands |
| `docs/templates/evolutie-fr.md.j2` | Jinja2-template Frans |
| `src/csat/config/pillars.py` | `PILLAR_REGISTRY` — namen NL/FR per pijler |
| `tests/core/test_evolution_exporter.py` | 54 unit tests |

---

## 7. Testoverzicht

| Klasse | Tests | Beschrijving |
|---|---|---|
| `TestEvolutionExporterInit` | 6 | Taalvalidatie, padconfiguratie, ongeldige taal |
| `TestEvolutionExporterRender` | 12 | Markdown-output, pillaarnaam NL/FR, KPI-statuslabels, delta-formatting |
| `TestEvolutionExporterExport` | 14 | Bestandsschrijving, naamconventie, padaanmaak, logging |
| `TestFmtDelta` | 6 | Delta-formatting: positief, negatief, nul, decimalen |
| `TestBuildContext` | 16 | Context-keys aanwezig, delta-berekeningen, trend-labels, hospital-sortering |
| **Totaal** | **54** | 100% coverage |

---

## 8. Relatie tot andere fasen

```text
Fase 2  ──► ReportExporter (patroon) ──► Fase 3c: EvolutionExporter
Fase 3b ──► EvolutionResult/Analyser ──► Fase 3c: EvolutionExporter
                                                    │
                                                    ▼
                                         evolutie-{pillar}-{jaar}-{lang}.md
                                                    │
                                         Fase 3d: EvolutionVisualiser (PNG)
```

**Volgende stap:** Fase 3d — `EvolutionVisualiser` (matplotlib PNG)

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 26/03/2026 | Initiële versie — fase 3c retrospectief gedocumenteerd | Danny Depecker + GHC |
