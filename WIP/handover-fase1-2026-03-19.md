# CSAT-Compass - Handover Fase 1

**Versie:** 1.0  
**Laatst bijgewerkt:** 19/03/2026

**Doel:** Contextoverdracht voor nieuwe conversatie — stand van zaken Fase 1  
**Type:** Reference  
**Auteur:** GHC  
**Status:** Draft

**Bestandsnaam:** handover-fase1-2026-03-19.md  
**Path:** WIP/

---

## 1. Projectcontext

**Project:** CSAT-Compass — geautomatiseerde klanttevredenheidsanalyse voor ZORGI  
**Doel:** Maandelijkse CSAT-rapporten (NL + FR) voor 4 pijlers + ZORGI-aggregaat  
**Stack:** Python 3.13 · pandas · SQLAlchemy · Jinja2 · Streamlit · WeasyPrint  
**Databron:** SQL Server view `[dbo].[V_CSAT_1]` op `ZRG0014WI/Lerni_DB`  
**Repo:** `C:\Users\danndepe\Documents\AI\CSAT-Compass`  
**Laatste commit:** `b7c8fcd` — chore: tooling restructure, pre-commit setup and loader improvements

---

## 2. Wat is al gedaan

### Infrastructuur (volledig klaar)

- `.venv` Python 3.13 — alle packages geïnstalleerd (`requirements.txt` + `requirements-dev.txt`)
- `.pre-commit-config.yaml` — Ruff, Mypy, Bandit, syntax check actief bij elke commit
- `pyproject.toml` — Ruff config (max 100 tekens), Mypy strict, Bandit, pytest
- `tools/lint.ps1` — manuele lint runner (5 checks incl. pip-audit met ZORGI-proxy fallback)
- `.env` — DB-connectiegegevens aanwezig incl. wachtwoord (nooit in Git)
- `.env.example` — template zonder wachtwoord (wel in Git)
- `.gitattributes` — line endings correct geconfigureerd

### Broncode — geïmplementeerd

| Bestand | Inhoud | Status |
|---------|--------|--------|
| `src/csat/config/settings.py` | DB-conn string, paden, log-niveau uit `.env` | ✅ |
| `src/csat/config/pillars.py` | PILLAR_REGISTRY met 5 pijlers (incl. zorgi) | ✅ |
| `src/csat/core/loaders/base_loader.py` | Abstracte BaseLoader met `load()` + `is_available()` | ✅ |
| `src/csat/core/loaders/csv_loader.py` | CSV/Excel loader via pandas | ✅ |
| `src/csat/core/loaders/sql_loader.py` | SQL Server loader via SQLAlchemy + pyodbc | ✅ |
| `src/csat/core/loaders/__init__.py` | `get_loader()` factory — kiest SQL of CSV automatisch | ✅ |
| `src/csat/utils/branding.py` | ZORGI kleurconstanten, klaspalet, markdown helpers | ✅ |

### Documentatie

| Document | Status |
|----------|--------|
| `docs/02-tactisch/implementatie-gids.md` | ✅ Volledig — 6 fasen, T-shirt schattingen, Mermaid diagram |
| `docs/02-tactisch/fasen/fase1-data-analyse.md` | ✅ Volledig — DB-params, kolomnamen, KPI-definities, acceptatiecriteria |
| `.github/copilot-instructions.md` | ✅ v2.7 — /GIT (1/2/3 flows), /cve, /advies, /pdf commands |

---

## 3. Wat ontbreekt nog — Fase 1

Dit zijn de **lege stubs** die nog geïmplementeerd moeten worden:

### Prioriteit 1 — Kernanayse (blokkeerders voor Fase 2)

| Bestand | Te implementeren |
|---------|-----------------|
| `src/csat/utils/logger.py` | Loguru-configuratie met bestandsrotatie naar `logs/` |
| `src/csat/utils/date_utils.py` | Hulpfuncties voor periode-filtering (maand, jaar, MoM) |
| `src/csat/core/analysers/base_analyser.py` | Gedeelde KPI-berekeningen: reactiegraad, High/Critical ratio, trend MoM |
| `src/csat/core/analysers/pillar_analyser.py` | Pillar-filtering op `product`-kolom + aggregatie per ziekenhuis |
| `src/csat/pillars/pharma/config.py` | PHARMA-drempelwaarden: reactiegraad ≥ 85%, High/Critical ≤ 15% |
| `src/csat/pillars/pharma/analyser.py` | PharmaAnalyser — erft PillarAnalyser, gebruikt pharma/config |

### Prioriteit 2 — Tests

| Bestand | Te implementeren |
|---------|-----------------|
| `tests/core/test_loaders.py` | Unit tests CsvLoader + SqlLoader (mock voor SQL) |
| `tests/pillars/test_pharma_analyser.py` | Unit tests PharmaAnalyser op testdata |

### Prioriteit 3 — Lege `__init__.py` bestanden

Volgende bestanden zijn leeg maar worden pas later ingevuld:
`src/csat/__init__.py`, `src/csat/i18n/__init__.py`, alle pillar `__init__.py`'s

---

## 4. Openstaande actiepunten voor Danny

| Actie | Status | Opmerking |
|-------|--------|-----------|
| `.env` wachtwoord invullen | ✅ Gedaan | `CSAT_DB_PASSWORD` ingevuld |
| Eerste DB-connectietest uitvoeren | ⚠️ Te doen | Zie sectie 5 hieronder |
| Score-bereik V_CSAT_1 bepalen | ⚠️ Na connectie | Nodig voor KPI-drempelwaarden |
| Trend MoM drempel bepalen | ⚠️ Na exploratie | Afhankelijk van score-bereik |

---

## 5. Eerstvolgende concrete actie

**De DB-connectie testen** — dit is de logische eerste stap nu `.env` klaar is:

```python
# Snel testen via Python console in PyCharm
from src.csat.core.loaders import get_loader
from src.csat.config import settings

loader = get_loader(settings)
print(loader.is_available())   # Verwacht: True
df = loader.load(pillar="ZORGI PHARMA")
print(df.shape)                # Verwacht: (n_rows, 12)
print(df.head())
```

Als de connectie slaagt → score-bereik verkennen:

```python
print(df["score"].describe())          # min, max, gemiddelde, percentiles
print(df["product"].value_counts())    # welke pijlers zitten in de view?
print(df["priority"].value_counts())   # verdeling Low/Medium/High/Critical
```

---

## 6. Daarna — volgorde implementatie

```text
1. logger.py           ← Loguru setup (XS — 1–2u)
2. date_utils.py       ← periode-helpers (XS — 1–2u)
3. base_analyser.py    ← KPI-berekeningen (S — 4–6u)
4. pillar_analyser.py  ← filtering + aggregatie (S — 4–6u)
5. pharma/config.py    ← drempelwaarden (XS — 1u)
6. pharma/analyser.py  ← PharmaAnalyser (S — 3–4u)
7. test_loaders.py     ← unit tests loaders (S — 3–4u)
8. test_pharma.py      ← unit tests analyser (S — 3–4u)
```

Totaal resterende werk Fase 1: **~S+M = 20–30u**

---

## 7. Technische details voor nieuwe sessie

### Kolomnamen V_CSAT_1 (bevestigd)

```sql
[key], [issue_type], [priority], [summary], [score], [comment],
[satisfaction_date], [created], [hospital], [product],
[product_domain], [project_key]
```

### Pijler-mapping (product-kolom → pijler)

| `product`-waarde in DB | ZORGI-pijler |
|------------------------|-------------|
| ZORGI PHARMA | PHARMA (↑) |
| CARE | CARE (→) |
| OAZIS | CARE ADMIN (←) |
| ERP4HC²·⁰ | ERP4HC (↓) |

> ⚠️ De exacte waarden in de `product`-kolom moeten bevestigd worden na de eerste connectie.

### KPI-drempelwaarden — vastgesteld

| KPI | Drempel | Bron |
|-----|---------|------|
| Reactiegraad | ≥ 85% | Bevestigd team |
| High/Critical ratio | ≤ 15% | Bevestigd team |
| Gemiddelde CSAT-score | TBD | Na data-exploratie |
| Trend MoM | TBD | Na data-exploratie |

---

## 8. Custom commands beschikbaar in deze sessie

| Command | Functie |
|---------|---------|
| `/GIT` | Vraag lint-voorkeur (1/2/3) → commit |
| `/cve` | CVE-scan alle packages via ingebouwde tooling |
| `/advies` | Advies + MCQ één voor één |
| `/pdf` | Batch MD → PDF conversie |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 19/03/2026 | Initiële handover aangemaakt | GHC |

