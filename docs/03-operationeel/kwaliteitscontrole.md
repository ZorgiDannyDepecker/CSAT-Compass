# CSAT-Compass - Kwaliteitscontrole overzicht

**Versie:** 1.8
**Laatst bijgewerkt:** 18/04/2026

**Doel:** Operationeel runbook — dagelijkse kwaliteitscontroles, commando's en FAQ
**Type:** Runbook
**Auteur:** Danny Depecker
**Status:** Approved

**Bestandsnaam:** kwaliteitscontrole.md
**Path:** docs/03-operationeel/

> **Strategisch overzicht tools & architectuur:** `docs/01-strategisch/kwaliteitsborging.md`
> Dit bestand beschrijft uitsluitend de dagelijkse operatie: wanneer wat te doen, commando's en FAQ.

---

## Inhoudsopgave

1. [Dagelijkse flow — één oogopslag](#1-dagelijkse-flow--één-oogopslag)
2. [Twee lagen van bescherming](#2-twee-lagen-van-bescherming)
3. [Wat doet /git?](#3-wat-doet-git)
4. [Wat doet /cve?](#4-wat-doet-cve)
5. [Volledig overzicht — wat wanneer](#5-volledig-overzicht--wat-wanneer)
6. [Configuratie — waar staat wat?](#6-configuratie--waar-staat-wat)
7. [Veelgestelde vragen](#7-veelgestelde-vragen)

---

## 1. Dagelijkse flow — één oogopslag

```text
Jij schrijft code
      ↓
[MANUEEL — optioneel]   .\tools\lint.ps1        ← volledige sweep op src/ en tests/
      ↓
[MANUEEL — via /git]    keuze 1 / 2 / 3         ← lint alleen / commit alleen / lint + commit
      ↓
[AUTOMATISCH]           git commit               ← pre-commit hooks lopen altijd
      ↓                                             bij commit — blokkeert bij fout
[AUTOMATISCH]           commit geslaagd ✅
      ↓
[MANUEEL — optioneel]   /cve in Copilot Chat    ← CVE-scan packages (proxy-proof)
```

---

## 2. Twee lagen van bescherming

Het systeem heeft **twee onafhankelijke lagen** — ze vullen elkaar aan.
Zie `docs/01-strategisch/kwaliteitsborging.md` voor het volledig tool-overzicht en de architectuurkeuze.

### Laag 1 — Manueel: `tools\lint.ps1`

- **Wanneer:** Wanneer jíj het wil — geen automatisme
- **Hoe:** `.\tools\lint.ps1` in de terminal
- **Scope:** Alle bestanden in `src/` en `tests/` altijd
- **Checks:** Ruff lint · Ruff format · MyPy · Bandit · pip-audit (met ZORGI-fallback)
- **Optie:** `.\tools\lint.ps1 -Fix` → past Ruff-problemen automatisch aan

#### Parameters (v2.0)

| Parameter | Beschrijving | Voorbeeld |
|-----------|-------------|---------|
| *(geen)* | Read-only sweep op `src/` en `tests/` | `.\tools\lint.ps1` |
| `-Fix` | Ruff-issues automatisch herstellen | `.\tools\lint.ps1 -Fix` |
| `-Verbose` | Ruwe tool-output tonen, ook bij succes | `.\tools\lint.ps1 -Verbose` |
| `-Skip` | Eén of meerdere tools overslaan | `.\tools\lint.ps1 -Skip Bandit,PipAudit` |
| `-Target` | Alleen opgegeven map scannen | `.\tools\lint.ps1 -Target src/` |

Geldige waarden voor `-Skip`: `Ruff`, `RuffFormat`, `MyPy`, `Bandit`, `PipAudit`

> 💡 Parameters zijn combineerbaar: `.\tools\lint.ps1 -Fix -Verbose -Target src/`

#### Samenvatting-statussen in de output

| Status | Betekenis |
|--------|-----------|
| `[OK]` | Check geslaagd |
| `[FAIL]` | Check mislukt — actie vereist |
| `[SKIP]` | Overgeslagen via `-Skip` parameter |
| `[?]` | Tool niet geïnstalleerd (`pip install <tool>`) |
| `[PROXY]` | pip-audit geblokkeerd door ZORGI corporate proxy — geen echte fout |

### Laag 2 — Automatisch: pre-commit hooks

- **Wanneer:** Altijd, automatisch bij **elke** `git commit`
- **Hoe:** Niets doen — werkt vanzelf na `python -m pre_commit install`
- **Scope:** Alleen de **gewijzigde** bestanden in die commit
- **Checks:** Ruff lint · Ruff format · MyPy · Bandit · Interrogate · Vulture · syntax · merge-conflicten
- **Effect:** Bij fout → commit wordt **geblokkeerd** — je ziet welke check faalde

> 💡 **Verschil scope:** `lint.ps1` checkt altijd alles. Pre-commit checkt alleen wat je gewijzigd hebt.
> Beide zijn nuttig: lint.ps1 voor een brede sweep, pre-commit als vangnet bij elke commit.

---

## 3. Wat doet /git?

`/git` is een GitHub Copilot custom command dat het git-proces begeleidt:

```text
Jij typt: /git
      ↓
Copilot vraagt: keuze 1 / 2 / 3

  1 — Direct committen
        git add -A
        git diff --staged --stat   (Copilot analyseert de wijzigingen)
        git commit -m "..."        (Copilot genereert de commit message)
        → pre-commit hooks lopen automatisch mee

  2 — Alleen lint
        .\tools\lint.ps1           (volledige sweep)
        → geen commit

  3 — Lint, daarna committen
        .\tools\lint.ps1           (volledige sweep)
        → als slaagt: zelfde als keuze 1
        → als faalt: stop, geen commit
```

---

## 4. Wat doet /cve?

`/cve` is een GitHub Copilot custom command voor CVE-scans:

```text
Jij typt: /cve
      ↓
Copilot haalt packagelijst op: python -m pip list --format=freeze
      ↓
Copilot scant in batches van 20 via ingebouwde CVE-database (OSV/GitHub Advisory)
      ↓
Copilot toont tabel: Package | Versie | CVE | Ernst | Actie
  → Alleen packages MET CVE's worden getoond
  → Als alles schoon: één bevestigingsregel
```

> ✅ **Werkt altijd** — ook achter de ZORGI corporate proxy. Geen SSL-verbinding nodig.
>
> ⚠️ **pip-audit in lint.ps1 werkt niet op het ZORGI-netwerk** — corporate proxy blokkeert de SSL-verbinding.
> Gebruik `/cve` als alternatief.

---

## 5. Volledig overzicht — wat wanneer

### Wat het systeem automatisch doet

| Moment | Actie | Door wie |
|--------|-------|----------|
| Bij elke `git commit` | Ruff lint + Ruff format | pre-commit |
| Bij elke `git commit` | MyPy type checker | pre-commit |
| Bij elke `git commit` | Bandit security | pre-commit |
| Bij elke `git commit` | Interrogate docstring-coverage | pre-commit |
| Bij elke `git commit` | Vulture dode code | pre-commit |
| Bij elke `git commit` | Python syntax check | pre-commit |
| Bij elke `git commit` | Merge-conflict check | pre-commit |
| Bij elke push/PR | Tests op Python 3.11, 3.12, 3.13 | GitHub Actions |
| Bij elke push/PR | Tests in willekeurige volgorde (`pytest-randomly`) — seed verschilt per run | GitHub Actions |
| Bij elke push/PR (`.md`) | Markdown lint | GitHub Actions |
| Bij `/git` keuze 1 of 3 | Commit message genereren | Copilot |

### Wat jij manueel doet

| Wanneer | Actie | Commando |
|---------|-------|---------|
| Voor een grote commit | Brede kwaliteitscheck | `.\tools\lint.ps1` |
| Ruff-issues automatisch fixen | Opmaak herstellen | `.\tools\lint.ps1 -Fix` |
| Alleen een specifieke map checken | Gerichte sweep | `.\tools\lint.ps1 -Target src/` |
| Trage tools overslaan | Snellere sweep | `.\tools\lint.ps1 -Skip Bandit,PipAudit` |
| Uitgebreide diagnose | Volledige tool-output | `.\tools\lint.ps1 -Verbose` |
| Periodiek (maandelijks) | CVE-scan packages | `/cve` in Copilot Chat |
| Bij nieuwe packages | CVE-scan na `pip install` | `/cve` in Copilot Chat |
| Wanneer je wil committen | Git-workflow starten | `/git` in Copilot Chat |

---

## 6. Configuratie — waar staat wat?

| Wat | Bestand | Wat erin staat |
|-----|---------|---------------|
| Ruff-regels | `pyproject.toml` → `[tool.ruff]` | Regellengte 100, geselecteerde regels |
| MyPy-config | `pyproject.toml` → `[tool.mypy]` | Strictheid, uitzonderingen per map |
| Bandit-config | `pyproject.toml` → `[tool.bandit]` | Uitgesloten mappen |
| Pre-commit hooks | `.pre-commit-config.yaml` | Welke checks, op welke bestanden |
| Lint runner | `tools/lint.ps1` | Volgorde, parameters, ZORGI-proxy afhandeling |
| Ruff uitzonderingen | `pyproject.toml` → `per-file-ignores` | Tests mogen `assert` gebruiken |

---

## 7. Veelgestelde vragen

**Pre-commit blokkeert mijn commit — wat nu?**
Lees de foutmelding. Ruff-fouten kan je automatisch fixen: `.\tools\lint.ps1 -Fix`.
MyPy- of Bandit-fouten moet je zelf oplossen in de code.

**Kan ik pre-commit overslaan?**
Ja, maar doe dit alleen in noodgevallen: `git commit --no-verify -m "..."`.
Noteer altijd waarom je de checks overgeslagen hebt in de commit message.

**Ruff vs Black — welke gebruik ik?**
Alleen Ruff. Black is niet apart geïnstalleerd en niet nodig — Ruff-formatter doet hetzelfde.
De zichtbare labelnaam in de pre-commit output is **Ruff - formatter (ex Black)**.

**MyPy klaagt over een externe library zonder types?**
Voeg toe aan `pyproject.toml` onder `[[tool.mypy.overrides]]`:

```toml
[[tool.mypy.overrides]]
module = "naam_van_library.*"
ignore_missing_imports = true
```

**pip-audit geeft SSL-fout op kantoor?**
Normaal — ZORGI corporate proxy. Gebruik `/cve` in Copilot Chat als alternatief.

**Een tool geeft `[?]` in de samenvatting — wat nu?**
De tool is niet geïnstalleerd in de actieve virtual environment.
Activeer `.venv` en voer uit: `pip install <toolnaam>` (zie de melding in de output voor de exacte naam).

**Tests lopen elke keer in een andere volgorde — is dat normaal?**
Ja, dit is bewust. Het project gebruikt `pytest-randomly` om bij elke run de testvolgorde
te shuffelen. Doel: volgorde-afhankelijke tests opsporen (een test die slaagt omdat een
andere test eerst zijn state heeft klaargezet).

- **`--randomly-seed=last`** (ingesteld in `pyproject.toml`): herhaalt automatisch de seed
  van de vorige run. Zo reproduceer je een falende volgorde zonder de seed handmatig te noteren.
- **Manueel reproduceren:** `pytest --randomly-seed=<getal>` met het seed-getal uit de output.
- **In CI:** elke run krijgt een nieuwe seed → volgorde-afhankelijke tests worden vroeg of laat
  zichtbaar als ze falen.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 20/03/2026 | Initiële versie | Danny Depecker + GHC |
| 1.1 | 28/03/2026 | Terminologie bijgewerkt: Ruff 'opmaak' hernoemd naar 'formattering (Black-stijl)' | Danny Depecker + GHC |
| 1.2 | 28/03/2026 | Terminologie bijgewerkt: 'MyPy' hernoemd naar 'MyPy — type checker' | Danny Depecker + GHC |
| 1.3 | 28/03/2026 | Zichtbare toolinglabels afgestemd op CLI-output | Danny Depecker + GHC |
| 1.4 | 28/03/2026 | Formatter-label herzien naar 'Ruff - formatter (ex Black)' | Danny Depecker + GHC |
| 1.5 | 31/03/2026 | Opgemaakt conform md-style-guide | GHC |
| 1.6 | 31/03/2026 | §2 (tool-beschrijvingen) verwijderd — verplaatst naar kwaliteitsborging.md; secties hernummerd | GHC |
| 1.7 | 02/04/2026 | §5 testvolgorde-rij toegevoegd; FAQ pytest-randomly uitleg + seed-reproductie | Danny Depecker + GHC |
| 1.8 | 18/04/2026 | lint.ps1 v2.0 parameters gedocumenteerd (-Fix/-Verbose/-Skip/-Target); statustabel toegevoegd; §5 manuele tabel uitgebreid; FAQ [?]-status toegevoegd | Danny Depecker + Claude |
