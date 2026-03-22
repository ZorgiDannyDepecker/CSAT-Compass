# CSAT-Compass 🧭

> **Customer SATisfaction** — analyse en rapportage voor alle ZORGI-pijlers

## 📋 Overzicht

CSAT-Compass is een Python-gedreven tool voor het analyseren van klanttevredenheidsdata
over alle ZORGI-pijlers: **PHARMA**, **CARE**, **CARE ADMIN** en **ERP4HC**.

Het project genereert automatisch tendensrapporten, visualisaties en vergelijkingsmatrices
op basis van maandelijkse ticketingdata.

## 🏗️ Projectstructuur

```text
CSAT-Compass/
├── src/csat/               # Python-library — herbruikbare modules (importeerbaar)
│   ├── config/             # Pijlerdefinities en globale instellingen
│   ├── core/
│   │   ├── loaders/        # Data inladen: SQL (primair) of CSV (fallback)
│   │   ├── analysers/      # KPI-berekeningen per pijler
│   │   └── exporters/      # Rapport- en dashboardgeneratie
│   ├── pillars/            # Pijlerspecifieke config + analysers (pharma, care, ...)
│   ├── i18n/               # Vertalingen NL/FR (nl.json, fr.json)
│   └── utils/              # Gedeelde hulpfuncties (logger, datumnotatie, branding)
├── scripts/                # CLI-entrypoints — roepen src/ aan, bevatten geen library-code
│   └── export_data.py      # Data exporteren uit V_CSAT_1 naar CSV
├── tools/                  # Dev-tooling — niet projectspecifiek, voor ontwikkelaars
│   └── lint.ps1            # Ruff + mypy + pytest (kwaliteitscheck voor commit)
├── tests/                  # Unit tests — spiegelt src/csat/ structuur
├── docs/
│   ├── 01-strategisch/     # WAAROM — projectplan, ADRs (architectuurbeslissingen)
│   ├── 02-tactisch/        # HOE — implementatiegids, fasedocumentatie
│   ├── 03-operationeel/    # DAGELIJKS — runbook, troubleshooting, tool-manuals
│   └── templates/          # Jinja2-templates voor NL/FR rapporten
├── data/                   # Ruwe ticketingdata — nooit in Git (zie .gitignore)
├── output/                 # Gegenereerde rapporten en CSV-exports — niet in Git
├── logs/                   # Applicatielogs — niet in Git
├── archive/                # Oude versies van bestanden — ter referentie bewaard
└── WIP/                    # Work In Progress — niet productierijp
```

> 💡 **Nieuwe collega?** De bewuste keuze achter deze structuur staat in
> [ADR-008](docs/01-strategisch/architectuur-beslissingen.md#8-adr-008--mapstructuur-en-mapfilosofie).
> Kernregel: `src/` = library, `scripts/` = runners, `tools/` = dev-hulp.

## 🚀 Snelstart

```bash
# Virtuele omgeving aanmaken
python -m venv .venv
.venv\Scripts\activate

# Afhankelijkheden installeren
pip install -r requirements.txt

# Analyse uitvoeren
python scripts/run_analysis.py
```

## 🧩 Pijlers

| Pijler     | Beschrijving                     |
| ---------- | -------------------------------- |
| PHARMA     | Ziekenhuisapotheek applicaties   |
| CARE       | Verpleegkundige zorgtoepassingen |
| CARE ADMIN | Administratieve zorgtoepassingen |
| ERP4HC     | ERP voor de gezondheidssector    |

## 🤝 Bijdragen

Dit project wordt beheerd met GitHub Copilot en volgt de ZORGI-codeerstandaarden.

---
*ZORGI — Danny Depecker — 2026*
