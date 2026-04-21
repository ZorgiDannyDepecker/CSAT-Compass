# Fase 4 — CARE / CARE ADMIN / ERP4HC Pijleranalysers

**Versie:** 2.0
**Datum:** 19/04/2026 (afgerond: 20/04/2026)

**Doel:** Implementatie van de drie resterende pijleranalysers voor ZORGI-breed CSAT-gebruik
**Type:** Implementatiedocument
**Auteur:** Danny Depecker + GHC
**Status:** ✅ Voltooid — 20/04/2026

**Bestandsnaam:** fase4-pijlers.md
**Path:** docs/02-tactisch/fasen/

---

## Context

Na de volledige afronding van Fase 5 (PHARMA-dashboard) werden de drie resterende
pijlers geïmplementeerd. De architectuur is pijler-agnostisch gebouwd in Fase 1/5a,
zodat elke nieuwe pijler een **flip-the-switch uitbreiding** was.

### Bestaande referentie: PHARMA-pijler

| Bestand | Rol |
|---|---|
| `src/csat/pillars/pharma/config.py` | Pijlerspecifieke categorieën, KPI-drempels, SD-nummer |
| `src/csat/pillars/pharma/analyser.py` | Thin wrapper op `PillarAnalyser` |
| `src/csat/pillars/pharma/__init__.py` | Publieke exports |

---

## Scope

### 3 nieuwe pijlers

| Pijler | PRODUCT_FILTER | Doelgroep | Tests | Status |
|---|---|---|---|---|
| **CARE** | `"CARE"` | Zorgpersoneel applicaties | 38 | ✅ Geïmplementeerd |
| **CARE ADMIN** | `"CARE ADMIN"` | Administratie zorgpersoneel | 39 | ✅ Geïmplementeerd |
| **ERP4HC** | `"ERP"` | ERP-applicaties ziekenhuizen | 39 | ✅ Geïmplementeerd |

### Per pijler geleverd

1. `src/csat/pillars/{pijler}/config.py` — KPI-drempels, namen NL/FR, richting
2. `src/csat/pillars/{pijler}/analyser.py` — thin wrapper op `PillarAnalyser`
3. `src/csat/pillars/{pijler}/__init__.py` — publieke exports
4. Tests in `tests/pillars/test_{pijler}_analyser.py` (min. 30, gerealiseerd 38–39)
5. Dashboard-integratie: `_ACTIVE_PILLARS` uitgebreid, sidebar toont alle 4 pijlers

---

## Architectuurprincipe

```text
PillarAnalyser (generiek)
    ↑ erft
CareAnalyser          ← src/csat/pillars/care/       ✅ 38 tests
CareAdminAnalyser     ← src/csat/pillars/care_admin/  ✅ 39 tests
Erp4hcAnalyser        ← src/csat/pillars/erp4hc/      ✅ 39 tests
PharmaAnalyser        ← src/csat/pillars/pharma/      ✅ (referentie)
```

Elke pijleranalyser erft volledig van `PillarAnalyser` — geen duplicatie van logica.
Enkel `config.py` is pijlerspecifiek.

---

## Beslissingen — bevestigd 20/04/2026

| Item | Beslissing |
|---|---|
| SD-projectnummers | Niet opgenomen in code — irrelevant voor werking |
| Ticketcategorieën | Globaal — geen pijlerspecifieke filtering |
| KPI-drempels | Start met `HIGH_CRITICAL_MAX=15.0` (PHARMA-baseline), later bijstuurbaar per pijler |
| OAZIS-referenties | Verwijderd — vervangen door `"CARE ADMIN"` in `pillars.py` |

---

## Acceptatiecriteria

- [x] Alle 3 pijlers laden CSV/SQL data correct via de hybride loader
- [x] `analyse()` en `analyse_ytd()` werken identiek aan PHARMA
- [x] Dashboard toont alle 4 pijlers correct via sidebar-selectie
- [x] Tests: minimum 30 tests per pijler — gerealiseerd: CARE 38, CARE ADMIN 39, ERP4HC 39
- [x] Coverage: 100% voor nieuwe bronbestanden
- [x] CI: alle pre-commit hooks slagen — gevalideerd via `/pytest 3` (1.122 tests, 0 failures)

---

## Afhankelijkheden

| Vereiste | Status |
|---|---|
| `PillarAnalyser` (base) | ✅ Beschikbaar (`src/csat/core/analysers/pillar_analyser.py`) |
| `HybridLoader` | ✅ Beschikbaar (`src/csat/loaders/`) |
| Dashboard infrastructuur | ✅ Beschikbaar (`src/dashboard/app.py`) |
| i18n NL/FR | ✅ Beschikbaar (`src/csat/i18n/`) |
| ZORGI Theme | ✅ Beschikbaar (`src/csat/utils/zorgi_theme.py`) |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 19/04/2026 | Initiële versie — stub op basis van PHARMA-referentie | Danny Depecker + GHC |
| 2.0 | 21/04/2026 | Status bijgewerkt naar ✅ Voltooid — alle criteria gevalideerd (1.122 tests, v0.6.0) | Danny Depecker + GHC |
