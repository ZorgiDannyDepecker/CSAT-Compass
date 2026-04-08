# CSAT-Compass - Kwaliteitsborging - Q²

**Versie:** 2.1
**Laatst bijgewerkt:** 02/04/2026

**Doel:** Strategisch overzicht van de kwaliteitsarchitectuur — welke tools, welke lagen, waarom
**Type:** Reference
**Auteur:** Danny Depecker
**Status:** Approved

**Bestandsnaam:** kwaliteitsborging.md
**Path:** docs/01-strategisch/

> **Operationele procedures:** `docs/03-operationeel/kwaliteitscontrole.md`
> Dit bestand beschrijft de architectuur en tool-keuzes.
> Dagelijkse commando's, /git, /cve en FAQ staan in het operationele runbook.

---

## Inhoudsopgave

1. [Architectuurbeslissing — twee lagen](#1-architectuurbeslissing--twee-lagen)
2. [Laag 1 — lokaal: pre-commit hooks](#2-laag-1--lokaal-pre-commit-hooks)
3. [Laag 2 — cloud: GitHub Actions](#3-laag-2--cloud-github-actions)
4. [Volledig tool-overzicht](#4-volledig-tool-overzicht)

---

## 1. Architectuurbeslissing — twee lagen

**Principe:** fouten zo vroeg mogelijk onderscheppen — bij voorkeur vóór de commit, anders vóór de merge.

```text
Developer schrijft code
        ↓
[Laag 1 — lokaal]   pre-commit hooks     ← blokkeert de commit bij fout
        ↓
[Laag 2 — cloud]    GitHub Actions CI    ← blokkeert de merge bij fout
        ↓
Code staat in master ✅
```

De twee lagen zijn bewust **onafhankelijk**: een commit die lokaal slaagt, wordt nog eens
gevalideerd in de cloud op een schone Ubuntu-omgeving met drie Python-versies.

---

## 2. Laag 1 — lokaal: pre-commit hooks

Draait automatisch bij elke `git commit`. Scope: alleen de gewijzigde bestanden.

| Tool | Rol | Blokkeert bij |
|---|---|---|
| **Ruff lint** | Stijl, imports, complexiteit, pandas best practices | lint-fouten |
| **Ruff format** | Uniforme opmaak (Black-stijl), regellengte 100 | opmaakafwijking |
| **MyPy** | Statische typecontrole op `src/` | type-fouten |
| **Bandit** | Beveiligingsscan: secrets, onveilige functies, SQL-injectie | beveiligingsrisico |
| **AST syntax check** | Python-syntaxvalidatie | parse-fouten |
| **Merge-conflict check** | Detecteert onopgeloste conflict-markers | conflict-markers |
| **Interrogate** | Docstring-coverage op `src/csat/` — drempel 80% | te weinig docstrings |
| **Vulture** | Dode code — functies/klassen die nooit aangeroepen worden | dode code (min. 80% betrouwbaarheid) |

Installatie (eenmalig):

```powershell
.venv\Scripts\python.exe -m pre_commit install
```

---

## 3. Laag 2 — cloud: GitHub Actions

Draait automatisch bij elke push of pull request naar `master`.

| Workflow | Wat | Wanneer |
|---|---|---|
| **CI — Tests & Coverage** (`ci.yml`) | Testsuite op Python 3.11, 3.12 en 3.13 + coverage via Codecov | Elke push/PR — niet op `.md`, `docs/`, `WIP/` |
| **Markdown Lint** (`markdown-lint.yml`) | Markdownlint op alle `.md`-bestanden | Elke wijziging in `.md`-bestanden |

**Codecov** ontvangt de `coverage.xml` na elke CI-run op Python 3.13 en visualiseert
dekking over tijd. Huidig niveau: **100%**.

**Dependabot** controleert wekelijks (maandag 06:00 CET) pip-packages en GitHub Actions-versies.
Bij een update opent het automatisch een PR. Major-versiewijzigingen van `pandas` en `sqlalchemy`
worden bewust uitgesloten — die vragen manuele evaluatie.

---

## 4. Volledig tool-overzicht

| Tool | Laag | Trigger | Doel |
|---|---|---|---|
| Ruff lint + format | Lokaal | git commit | Stijl, opmaak |
| MyPy | Lokaal | git commit | Typeconformiteit |
| Bandit | Lokaal | git commit | Beveiliging |
| AST syntax check | Lokaal | git commit | Syntaxvalidatie |
| Merge-conflict check | Lokaal | git commit | Conflictdetectie |
| Interrogate | Lokaal | git commit | Docstring-coverage |
| Vulture | Lokaal | git commit | Dode code |
| pytest + Coverage.py | Cloud | push/PR | Testdekking |
| pytest-randomly | Lokaal + Cloud | pytest run | Willekeurige testvolgorde — detecteert volgorde-afhankelijke tests |
| Codecov | Cloud | push (3.13) | Dekkingstrend |
| Markdown Lint | Cloud | push `.md` | Documentkwaliteit |
| Dependabot | Cloud | wekelijks | Dependency-updates |
| pip-audit | Lokaal (optioneel) | lint.ps1 / manueel | CVE-scan geïnstalleerde packages (ZORGI-proxy: gebruik `/cve`) |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 31/03/2026 | Initiële versie | Danny Depecker |
| 1.1 | 31/03/2026 | Opgemaakt conform md-style-guide | GHC |
| 2.0 | 31/03/2026 | Herschreven als strategisch document — operationele details verplaatst naar kwaliteitscontrole.md | GHC |
| 2.1 | 02/04/2026 | §4: pytest-randomly en pip-audit toegevoegd aan tool-overzicht | Danny Depecker + GHC |
