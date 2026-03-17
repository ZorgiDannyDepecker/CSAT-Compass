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
├── src/csat/
│   ├── config/        # Instellingen per pijler
│   ├── core/
│   │   ├── loaders/   # Data inladen (xlsx/csv)
│   │   ├── analysers/ # Berekeningen & tendensen
│   │   └── exporters/ # PNG, MD, PDF output
│   ├── pillars/       # pharma / care / care_admin / erp4hc
│   └── utils/
├── tests/
├── data/              # Input bestanden (niet in Git)
├── output/            # Gegenereerde rapporten (niet in Git)
├── docs/
│   ├── 01-strategisch/
│   ├── 02-tactisch/
│   ├── 03-operationeel/
│   └── templates/
├── scripts/
├── logs/
├── archive/
└── WIP/
```

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
