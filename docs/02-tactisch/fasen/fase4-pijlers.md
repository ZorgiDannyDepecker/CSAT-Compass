# Fase 4 — CARE / CARE ADMIN / ERP4HC Pijleranalysers

**Versie:** 1.0
**Datum:** 19/04/2026

**Doel:** Implementatie van de drie resterende pijleranalysers voor ZORGI-breed CSAT-gebruik
**Type:** Implementatiedocument
**Auteur:** Danny Depecker + GHC
**Status:** 🔄 In voorbereiding

**Bestandsnaam:** fase4-pijlers.md
**Path:** docs/02-tactisch/fasen/

---

## Context

Na de volledige afronding van Fase 5 (PHARMA-dashboard) worden de drie resterende
pijlers geïmplementeerd. De architectuur is pijler-agnostisch gebouwd in Fase 1/5a,
zodat elke nieuwe pijler een **flip-the-switch uitbreiding** is.

### Bestaande referentie: PHARMA-pijler

| Bestand | Rol |
|---|---|
| `src/csat/pillars/pharma/config.py` | Pijlerspecifieke categorieën, KPI-drempels, SD-nummer |
| `src/csat/pillars/pharma/analyser.py` | Thin wrapper op `PillarAnalyser` |
| `src/csat/pillars/pharma/__init__.py` | Publieke exports |

---

## Scope

### 3 nieuwe pijlers

| Pijler | SD-nummer | Doelgroep | Status |
|---|---|---|---|
| **CARE** | TBD | Zorgpersoneel applicaties | ⏳ Te implementeren |
| **CARE ADMIN** | TBD | Administratie zorgpersoneel | ⏳ Te implementeren |
| **ERP4HC** | TBD | ERP-applicaties ziekenhuizen | ⏳ Te implementeren |

### Per pijler te leveren

1. `src/csat/pillars/{pijler}/config.py` — categorieën, KPI-drempels, SD-nummer
2. `src/csat/pillars/{pijler}/analyser.py` — thin wrapper op `PillarAnalyser`
3. `src/csat/pillars/{pijler}/__init__.py` — publieke exports
4. Tests in `tests/pillars/test_{pijler}_analyser.py`
5. Dashboard-integratie: pijler toevoegen aan sidebar-selectie in `app.py`

---

## Architectuurprincipe

```text
PillarAnalyser (generiek)
    ↑ erft
CareAnalyser          ← config: CARE-categorieën + SD-nummer
CareAdminAnalyser     ← config: CARE ADMIN-categorieën + SD-nummer
Erp4hcAnalyser        ← config: ERP4HC-categorieën + SD-nummer
PharmaAnalyser        ← config: PHARMA-categorieën (al geïmplementeerd)
```

Elke pijleranalyser erft volledig van `PillarAnalyser` — geen duplicatie van logica.
Enkel `config.py` is pijlerspecifiek.

---

## Vereiste informatie (voor implementatie)

| Item | Pijler | Status |
|---|---|---|
| SD-projectnummer | CARE | ❓ Nog te bevestigen |
| SD-projectnummer | CARE ADMIN | ❓ Nog te bevestigen |
| SD-projectnummer | ERP4HC | ❓ Nog te bevestigen |
| Ticketcategorieën | CARE | ❓ Nog te bevestigen |
| Ticketcategorieën | CARE ADMIN | ❓ Nog te bevestigen |
| Ticketcategorieën | ERP4HC | ❓ Nog te bevestigen |
| KPI-drempels (score, H/C ratio) | Alle 3 | ❓ Zelfde als PHARMA of pijlerspecifiek? |

---

## Acceptatiecriteria

- [ ] Alle 3 pijlers laden CSV/SQL data correct via de hybride loader
- [ ] `analyse()` en `analyse_ytd()` werken identiek aan PHARMA
- [ ] Dashboard toont pijler correct via sidebar-selectie
- [ ] Tests: minimum 30 tests per pijler (analoog aan `test_pillar_analyser.py`)
- [ ] Coverage: 100% voor nieuwe bronbestanden
- [ ] CI: alle pre-commit hooks slagen na implementatie

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
