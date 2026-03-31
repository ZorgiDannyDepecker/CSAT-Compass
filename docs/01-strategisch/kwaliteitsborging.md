# CSAT-Compass - Kwaliteitsborging - Q²

**Versie:** 1.1  
**Laatst bijgewerkt:** 31/03/2026

**Doel:** Automatische bewaking van codekwaliteit, typeconformiteit, veiligheid en testdekking op elke codewijziging — vóór én na commit  
**Type:** Reference  
**Auteur:** Danny Depecker  
**Status:** Approved

**Bestandsnaam:** kwaliteitsborging.md  
**Path:** docs/01-strategisch/

---

## Inhoudsopgave

1. [Lokale kwaliteitslaag — pre-commit hooks](#1-lokale-kwaliteitslaag--pre-commit-hooks)
2. [Cloud kwaliteitslaag — GitHub Actions](#2-cloud-kwaliteitslaag--github-actions)
3. [Testen & coverage — pytest + Codecov](#3-testen--coverage--pytest--codecov)
4. [Versiebeheer — GitHub Desktop + GitHub.com](#4-versiebeheer--github-desktop--githubcom)
5. [Codekwaliteit — Interrogate & Vulture](#5-codekwaliteit--interrogate--vulture)
6. [Dependency-bewaking — Dependabot](#6-dependency-bewaking--dependabot)

---

## 1. Lokale kwaliteitslaag — pre-commit hooks

Bij elke `git commit` worden de volgende checks automatisch uitgevoerd:

| Tool | Rol |
| --- | --- |
| **Ruff lint** | Stijl, imports, complexiteit (max C901=10), veiligheidspatronen, pandas best practices — met auto-fix waar mogelijk |
| **Ruff format** | Uniforme opmaak (vervangt Black) — regellengte 100 |
| **MyPy** | Statische typecontrole op `src/` — blokkeert type-fouten voor ze in de repo belanden |
| **Bandit** | Beveiligingsscan — detecteert hardcoded secrets, onveilige functies en SQL-kwetsbaarheden |
| **AST syntax check** | Python-syntaxvalidatie — vangt parse-fouten op vóór uitvoering |
| **Merge-conflict check** | Blokkeert commits met onopgeloste conflict-markers (zie `kwaliteitscontrole.md §2.6`) |

Installatie (eenmalig):

```powershell
.venv\Scripts\python.exe -m pre_commit install
```

---

## 2. Cloud kwaliteitslaag — GitHub Actions

Bij elke push of pull request naar `master` worden twee workflows geactiveerd:

**CI — Tests & Coverage** (`ci.yml`)  
Draait de volledige testsuite op Python **3.11, 3.12 en 3.13** parallel.  
Triggers niet op wijzigingen in `docs/`, `WIP/` of Markdown-bestanden.

**Markdown Lint** (`markdown-lint.yml`)  
Valideert alle `.md`-bestanden via `markdownlint-cli2` bij elke documentwijziging.  
Enforceert o.a. ATX-headings, codetaalvermelding en max. 1 lege regel.

---

## 3. Testen & coverage — pytest + Codecov

**pytest** — volledig geautomatiseerde testsuite in `tests/`, met drie markercategorieën: `unit`, `integration` en `slow`.  
Strikte markers voorkomen ongetagde tests.

**Coverage.py** — meet testdekking op `src/csat/` en rapporteert als terminal-output, HTML én XML.  
Huidig niveau: **100%**.

**Codecov** — ontvangt de `coverage.xml` na elke succesvolle CI-run op Python 3.13 en visualiseert de dekking over tijd.  
Maakt regressies in testdekking zichtbaar bij pull requests.

---

## 4. Versiebeheer — GitHub Desktop + GitHub.com

**GitHub Desktop** — lokale Git-interface voor commit, branch en push.  
Werkafspraak: commit vóór elke grote wijziging als vangnet, met conventionele commit-berichten (`feat:`, `fix:`, `refactor:`, `docs:`).

**GitHub.com** — centrale repository met beschermde `master`-branch.  
Alle CI-workflows draaien hier; pull requests kunnen pas gemerged worden na groene checks.  
Codecov-status is zichtbaar als extra check op elke PR.

---

## 5. Codekwaliteit — Interrogate & Vulture

**Interrogate** bewaakt docstring-coverage op `src/csat/`.  
Drempel: 80% — publieke methodes en klassen moeten gedocumenteerd zijn.  
Private methodes, `__init__`, magic methods en `__init__.py`-bestanden zijn uitgesloten.  
Draait als pre-commit hook bij elke commit.

**Vulture** detecteert dode code: functies, klassen en variabelen die nooit aangeroepen worden.  
Minimale betrouwbaarheid 80% om valse positieven te beperken.  
Een `vulture_whitelist.py` vangt bekende uitzonderingen op: Jinja2-template velden, dataclass-attributen die via de exporter-context doorgegeven worden, design system constanten en publieke API-functies.  
Draait als pre-commit hook bij elke commit.

---

## 6. Dependency-bewaking — Dependabot

**Dependabot** controleert wekelijks (maandag 06:00 CET) of pip-packages en GitHub Actions-versies verouderd zijn.  
Bij een update opent het automatisch een PR waarop de CI-suite direct mee draait.  
Dev-tools (ruff, mypy, pytest, ...) worden gebundeld in één PR om ruis te beperken.  
Major-versiewijzigingen van `pandas` en `sqlalchemy` worden bewust uitgesloten — die vragen manuele evaluatie.

---

*Twee lagen, één doel: fouten zo vroeg mogelijk onderscheppen — bij voorkeur vóór de commit, anders vóór de merge.*

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 31/03/2026 | Initiële versie | Danny Depecker |
| 1.1 | 31/03/2026 | Opgemaakt conform md-style-guide | GHC |
