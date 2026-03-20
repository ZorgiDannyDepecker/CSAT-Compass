# CSAT-Compass - Kwaliteitscontrole overzicht

**Versie:** 1.0  
**Laatst bijgewerkt:** 20/03/2026

**Doel:** Overzicht van alle kwaliteitscontroles — wat doet het systeem automatisch, wat doe je manueel  
**Type:** Runbook  
**Auteur:** Danny Depecker
**Status:** Approved

**Bestandsnaam:** kwaliteitscontrole.md  
**Path:** docs/03-operationeel/

---

## 1. Overzicht — één oogopslag

```text
Jij schrijft code
      ↓
[MANUEEL — optioneel]   .\tools\lint.ps1        ← 5 checks, altijd beschikbaar
      ↓
[MANUEEL — via /GIT]    keuze 1 / 2 / 3         ← lint alleen / commit alleen / lint + commit
      ↓
[AUTOMATISCH]           git commit               ← pre-commit hooks lopen altijd
      ↓                                             bij commit — blokkeert bij fout
[AUTOMATISCH]           commit geslaagd ✅
      ↓
[MANUEEL — optioneel]   /cve in Copilot Chat    ← CVE-scan packages (proxy-proof)
```

---

## 2. De tools — wat doet elk?

### 2.1 Ruff — linting + opmaak

**Wat is het?** Één tool die zowel `flake8`, `isort` als `black` vervangt — maar dan 10–100× sneller.

| Functie | Wat het doet | Voorbeeld |
|---------|-------------|-----------|
| **Linting** | Fouten, slechte patronen, ongebruikte imports | `import os` zonder gebruik → fout |
| **Opmaak** | Inspringing, witruimte, aanhalingstekens | 2 spaties → 4 spaties |
| **Regellengte** | Max 100 tekens per regel | Lange regel → afkappen |
| **Import-volgorde** | `isort`-stijl — stdlib → third-party → local | `from csat import x` altijd als laatste |
| **Security** | Eenvoudige security-patronen (Bandit-lite) | `eval()` → waarschuwing |
| **Pandas-stijl** | Best practices voor DataFrames | `.values` → `.to_numpy()` |

> 💡 **Black gebruiken we niet apart** — Ruff-formatter doet hetzelfde. Één tool, geen conflict.

### 2.2 Mypy — typecontrole

**Wat is het?** Controleert of type-annotaties in je code kloppen zonder de code uit te voeren.

```python
def load(pillar: str) -> pd.DataFrame:  ← Mypy checkt: geeft de functie echt een DataFrame terug?
```

| Vindt het? | Voorbeeld |
|------------|-----------|
| ✅ Ja | Functie verwacht `str`, krijgt `int` |
| ✅ Ja | `None` meegeven waar iets verplicht is |
| ✅ Ja | Methode aanroepen op verkeerd type |
| ❌ Nee | Runtime-fouten, logicafouten, performance |

### 2.3 Bandit — security scan

**Wat is het?** Scant Python-code op bekende beveiligingsrisico's.

| Vindt het? | Voorbeeld |
|------------|-----------|
| ✅ Ja | Wachtwoord hardcoded in code |
| ✅ Ja | `subprocess` met shell=True |
| ✅ Ja | `pickle.load()` op onbetrouwbare data |
| ✅ Ja | SQL-injectie via string-concatenatie |
| ❌ Nee | Logicafouten, typefouten |

### 2.4 pip-audit — CVE-scan packages

**Wat is het?** Vergelijkt geïnstalleerde packages met de publieke CVE-database.

> ⚠️ **Werkt niet op het ZORGI-netwerk** — corporate proxy blokkeert de SSL-verbinding.
> Alternatief: typ `/cve` in GitHub Copilot Chat — werkt altijd, ook achter de proxy.

### 2.5 Pre-commit syntax check

**Wat is het?** Controleert of elk Python-bestand syntactisch geldig is (`py_compile`).

```python
def load(   ← ontbrekende sluithaak → pre-commit blokkeert de commit
```

### 2.6 Pre-commit merge conflict check

**Wat is het?** Controleert of er geen onopgeloste merge-conflicten in bestanden zitten.

```text
<<<<<<< HEAD       ← dit patroon → pre-commit blokkeert de commit
=======
>>>>>>> main
```

---

## 3. Twee lagen van bescherming

Het systeem heeft **twee onafhankelijke lagen** — ze vullen elkaar aan:

### Laag 1 — Manueel: `tools\lint.ps1`

- **Wanneer:** Wanneer jíj het wil — geen automatisme
- **Hoe:** `.\tools\lint.ps1` in de terminal
- **Scope:** Alle bestanden in `src/` en `tests/` altijd
- **Checks:** Ruff lint · Ruff opmaak · Mypy · Bandit · pip-audit (met ZORGI-fallback)
- **Optie:** `.\tools\lint.ps1 -Fix` → past Ruff-problemen automatisch aan

### Laag 2 — Automatisch: pre-commit hooks

- **Wanneer:** Altijd, automatisch bij **elke** `git commit`
- **Hoe:** Niets doen — werkt vanzelf na `python -m pre_commit install`
- **Scope:** Alleen de **gewijzigde** bestanden in die commit
- **Checks:** Ruff lint · Ruff opmaak · Mypy · Bandit · syntax · merge-conflicten
- **Effect:** Bij fout → commit wordt **geblokkeerd** — je ziet welke check faalde

> 💡 **Verschil scope:** `lint.ps1` checkt altijd alles. Pre-commit checkt alleen wat je gewijzigd hebt.
> Beide zijn nuttig: lint.ps1 voor een brede sweep, pre-commit als vangnet bij elke commit.

---

## 4. Wat doet /GIT?

`/GIT` is een GitHub Copilot custom command dat het git-proces begeleidt:

```text
Jij typt: /GIT
      ↓
Copilot vraagt: keuze 1 / 2 / 3

  1 — Direct committen
        git add -A
        git diff --staged --stat   (Copilot analyseert de wijzigingen)
        git commit -m "..."        (Copilot genereert de commit message)
        → pre-commit hooks lopen automatisch mee

  2 — Alleen lint
        .\tools\lint.ps1           (alle 5 checks)
        → geen commit

  3 — Lint, daarna committen
        .\tools\lint.ps1           (alle 5 checks)
        → als slaagt: zelfde als keuze 1
        → als faalt: stop, geen commit
```

---

## 5. Wat doet /cve?

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

---

## 6. Volledig overzicht — wat wanneer

### Wat het systeem automatisch doet

| Moment | Actie | Door wie |
|--------|-------|----------|
| Bij elke `git commit` | Ruff lint + opmaak | pre-commit |
| Bij elke `git commit` | Mypy typecontrole | pre-commit |
| Bij elke `git commit` | Bandit security | pre-commit |
| Bij elke `git commit` | Python syntax check | pre-commit |
| Bij elke `git commit` | Merge conflict check | pre-commit |
| Bij `/GIT` keuze 1 of 3 | Commit message genereren | Copilot |

### Wat jij manueel doet

| Wanneer | Actie | Commando |
|---------|-------|---------|
| Voor een grote commit | Brede kwaliteitscheck | `.\tools\lint.ps1` |
| Ruff-issues automatisch fixen | Opmaak herstellen | `.\tools\lint.ps1 -Fix` |
| Periodiek (maandelijks) | CVE-scan packages | `/cve` in Copilot Chat |
| Bij nieuwe packages | CVE-scan na `pip install` | `/cve` in Copilot Chat |
| Wanneer je wil committen | Git-workflow starten | `/GIT` in Copilot Chat |

---

## 7. Configuratie — waar staat wat?

| Wat | Bestand | Wat erin staat |
|-----|---------|---------------|
| Ruff-regels | `pyproject.toml` → `[tool.ruff]` | Regellengte 100, geselecteerde regels |
| Mypy-config | `pyproject.toml` → `[tool.mypy]` | Strictheid, uitzonderingen per map |
| Bandit-config | `pyproject.toml` → `[tool.bandit]` | Uitgesloten mappen |
| Pre-commit hooks | `.pre-commit-config.yaml` | Welke checks, op welke bestanden |
| Lint runner | `tools/lint.ps1` | Volgorde, ZORGI-proxy afhandeling |
| Ruff uitzonderingen | `pyproject.toml` → `per-file-ignores` | Tests mogen `assert` gebruiken |

---

## 8. Veelgestelde vragen

**Pre-commit blokkeert mijn commit — wat nu?**
Lees de foutmelding. Ruff-fouten kan je automatisch fixen: `.\tools\lint.ps1 -Fix`.
Mypy- of Bandit-fouten moet je zelf oplossen in de code.

**Kan ik pre-commit overslaan?**
Ja, maar doe dit alleen in noodgevallen: `git commit --no-verify -m "..."`.
Noteer altijd waarom je de checks overgeslagen hebt in de commit message.

**Ruff vs Black — welke gebruik ik?**
Alleen Ruff. Black is niet geïnstalleerd en niet nodig — Ruff-formatter doet hetzelfde.

**Mypy klaagt over een externe library zonder types?**
Voeg toe aan `pyproject.toml` onder `[[tool.mypy.overrides]]`:

```toml
[[tool.mypy.overrides]]
module = "naam_van_library.*"
ignore_missing_imports = true
```

**pip-audit geeft SSL-fout op kantoor?**
Normaal — ZORGI corporate proxy. Gebruik `/cve` in Copilot Chat als alternatief.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur               |
| ------ | ---------- | --------------- |----------------------|
| 1.0 | 20/03/2026 | Initiële versie | Danny Depecker + GHC |
