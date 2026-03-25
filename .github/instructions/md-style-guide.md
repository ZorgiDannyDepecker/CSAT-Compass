# Documentatie Style Guide

**Versie:** 4.0
**Laatst bijgewerkt:** 17/03/2026
**Overgedragen naar PHARMA-Conventions:** 24/03/2026

**Doel:** Consistente opmaak en stijl voor alle projectdocumentatie
**Type:** Reference
**Auteur:** Danny Depecker + Claude
**Status:** Approved

**Bestandsnaam:** md-style-guide.md
**Path:** pharma/

> **Golden source:** Dit bestand wordt beheerd in `PHARMA-Conventions\pharma\`.
> Overgenomen van: `CSAT-Compass/.github/docs/md-style-guide.md` v4.0

---

## Inhoudsopgave

1. [Document Header Structuur](#1-document-header-structuur)
2. [Algemene Richtlijnen](#2-algemene-richtlijnen)
3. [Koppen Hiërarchie](#3-koppen-hiërarchie)
4. [Tekstopmaak](#4-tekstopmaak)
5. [Lijsten](#5-lijsten)
6. [Code Blokken](#6-code-blokken)
7. [Links en Referenties](#7-links-en-referenties)
8. [Tabellen](#8-tabellen)
9. [Afbeeldingen](#9-afbeeldingen)
10. [Speciale Elementen](#10-speciale-elementen)
11. [Bestandsnamen](#11-bestandsnamen)
12. [Git Commit Messages](#12-git-commit-messages)
13. [YAML Frontmatter](#13-yaml-frontmatter)

---

## 1. Document Header Structuur

### 1.1 Verplichte Header Template

Elk markdown document begint met deze gestandaardiseerde header:

```markdown
# [Project] - [Document Titel]

**Versie:** [X.Y]
**Laatst bijgewerkt:** [DD/MM/YYYY]

**Doel:** [Korte beschrijving van document doel]
**Type:** [Document type]
**Auteur:** [Naam auteur]
**Status:** [Huidige status]

**Bestandsnaam:** [filename.md]
**Path:** [relatief/pad/naar/bestand]

---
```

### 1.2 Verplichte Velden

| Veld                  | Formaat                 | Beschrijving                                     |
| --------------------- | ----------------------- | ------------------------------------------------ |
| **Document Titel**    | `# [Project] - [Titel]` | H1 header, altijd voorafgegaan door projectnaam  |
| **Versie**            | `X.Y`                   | Semantic versioning (0.1 = draft, 1.0 = release) |
| **Laatst bijgewerkt** | `DD/MM/YYYY`            | Nederlandse datumnotatie                         |
| **Doel**              | Vrije tekst (1 zin)     | Korte beschrijving van het document doel         |
| **Type**              | Enum                    | Document categorie (zie 1.3)                     |
| **Auteur**            | Naam of tool            | Primaire auteur of AI-tool (zie 1.2a)            |
| **Status**            | Enum                    | Huidige document status (zie 1.4)                |
| **Bestandsnaam**      | `filename.md`           | Exacte bestandsnaam (lowercase, hyphens)         |
| **Path**              | `relatief/pad/`         | Relatief pad vanaf project root                  |

#### 1.2a Auteur Veld

| Situatie                 | Waarde                 |
| ------------------------ | ---------------------- |
| Menselijke auteur        | `Danny Depecker`       |
| GitHub Copilot           | `GHC`                  |
| Claude (Anthropic)       | `Claude`               |
| Gemini (Google)          | `Gemini`               |
| Samenwerking mens + AI   | `Danny Depecker + GHC` |
| Samenwerking meerdere AI | `GHC + Claude`         |

### 1.3 Type Waarden

| Type            | Gebruik Voor                               |
| --------------- | ------------------------------------------ |
| `Implementatie` | Fase documenten, setup guides              |
| `ADR`           | Architecture Decision Records              |
| `Runbook`       | Daily operations, maintenance procedures   |
| `Reference`     | Naslagwerk, API docs, style guides         |
| `Guide`         | Gebruikershandleidingen, tutorials         |
| `Planning`      | Project plans, roadmaps                    |
| `Retrospective` | Lessons learned, post-mortems              |
| `Convention`    | Project-specifieke afspraken en conventies |

### 1.4 Status Waarden

| Status        | Beschrijving                        |
| ------------- | ----------------------------------- |
| `Draft`       | Work in progress, niet compleet     |
| `In Review`   | Klaar voor review door team         |
| `In Progress` | Actief in ontwikkeling              |
| `Approved`    | Goedgekeurd door stakeholders       |
| `Compleet`    | Afgerond en geïmplementeerd         |
| `Gepland`     | Nog niet gestart (placeholder)      |
| `Deprecated`  | Niet langer actueel/geldig          |
| `Archived`    | Bewaard voor historische doeleinden |

---

## 2. Algemene Richtlijnen

### 2.1 Taal

- Alle markdown documentatie in **Nederlands**
- Code comments in **Nederlands**
- Variabele/functie namen in **Engels**
- Technische termen in Engels waar Nederlands onnatuurlijk klinkt

### 2.2 Datumnotatie

- **In tekst:** `DD/MM/YYYY` — ✅ `10/02/2026`
- **In bestandsnamen:** `YYYY-MM-DD` — ✅ `2026-02-10-meeting-notes.md`

### 2.3 Regellengte

Aanbevolen: 80-100 karakters per regel.

---

## 3. Koppen Hiërarchie

- **H1:** Alleen voor document titel
- **H2:** Hoofdsecties
- **H3:** Subsecties
- Geen levels overslaan: H1 → H2 → H3

---

## 4. Tekstopmaak

- **Italic:** `*tekst*` — lichte nadruk
- **Bold:** `**tekst**` — sterke nadruk
- **Inline code:** `` `commando` `` — voor code, variabelen, commando's
- **Blockquote:** `>` — voor citaten of callouts

---

## 5. Lijsten

- Ongeordende lijsten: `-` als bullet (geen `*` of `+`)
- Geordende lijsten: nummering start bij `1`
- Maximaal 3 niveaus diep
- Checklists: `- [ ]` en `- [x]`

---

## 6. Code Blokken

### 6.1 Taalspecificatie

Altijd taal specificeren:

| Taal         | Tag          |
| ------------ | ------------ |
| Python       | `python`     |
| PowerShell   | `powershell` |
| SQL          | `sql`        |
| Bash/Shell   | `bash`       |
| Mermaid      | `mermaid`    |
| Tekst/Output | `text`       |

### 6.2 Mermaid Diagrammen

| Type             | Tag                     | Gebruik Voor                  |
| ---------------- | ----------------------- | ----------------------------- |
| Flowchart        | `graph TD` / `graph LR` | Procesflows, beslisbomen      |
| Sequentiediagram | `sequenceDiagram`       | API-calls, systeeminteracties |
| Gantt chart      | `gantt`                 | Projectplanning, fasering     |
| Klassendiagram   | `classDiagram`          | Datamodellen                  |
| Entiteit-relatie | `erDiagram`             | Databaseschema's              |
| Toestandsdiagram | `stateDiagram-v2`       | Statusovergangen              |

---

## 7. Links en Referenties

- Gebruik **relatieve paden** voor interne links
- Gebruik beschrijvende linkteksten

---

## 8. Tabellen

- Consistente spatiëring voor leesbaarheid
- Alignment: `:---` links, `:---:` center, `---:` rechts

---

## 9. Afbeeldingen

- Altijd alt text voor toegankelijkheid
- Aanbevolen locatie: `docs/images/`
- HTML voor sizing: `<img src="..." width="600" alt="...">`

---

## 10. Speciale Elementen

### 10.1 Admonitions

```markdown
⚠️ **BELANGRIJK:** Kritieke informatie.
✅ **TIP:** Handig om te weten.
❌ **FOUT:** Veelgemaakte fout.
```

### 10.2 Collapse Sections

```markdown
<details>
<summary>Klik om details te tonen</summary>
Verborgen content hier.
</details>
```

### 10.3 Keyboard Keys

```markdown
Druk <kbd>Ctrl</kbd>+<kbd>C</kbd> om te kopiëren.
```

---

## 11. Bestandsnamen

- Lowercase, hyphens, beschrijvend
- Meta-bestanden in UPPERCASE: `README.md`, `CHANGELOG.md`
- Archief patroon: `[naam]-ARCHIEF-v[X.Y]-[YYYYMMDD].md`

---

## 12. Git Commit Messages

### 12.1 Structuur

```text
<type>: <korte beschrijving> (max 50 chars)
```

### 12.2 Type Prefixes

| Type        | Gebruik                                  |
| ----------- | ---------------------------------------- |
| `docs:`     | Documentatie wijzigingen                 |
| `feat:`     | Nieuwe feature                           |
| `fix:`      | Bug fix                                  |
| `refactor:` | Code refactoring                         |
| `test:`     | Test toevoegingen/wijzigingen            |
| `chore:`    | Maintenance taken                        |
| `style:`    | Code formatting                          |

---

## 13. YAML Frontmatter

### 13.1 Wanneer gebruiken

| Situatie                               | Gebruik Frontmatter   |
| -------------------------------------- | --------------------- |
| `.instructions.md` voor GitHub Copilot | ✅ Verplicht (`applyTo`) |
| Standaard projectdocumentatie          | ❌ Niet nodig          |
| README.md bestanden                    | ❌ Niet aanbevolen     |

### 13.2 applyTo waarden

```yaml
---
applyTo: '**/*'              # Alle bestanden
applyTo: '**/*.py'           # Alleen Python
applyTo: '**/*.py,**/*.ps1'  # Python én PowerShell
---
```

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 03/02/2026 | Initial release | Danny Depecker |
| 2.0 | 10/02/2026 | Complete herziening | Danny Depecker |
| 3.0 | 02/03/2026 | Gegeneraliseerde template structuur | Danny Depecker + Claude |
| 4.0 | 17/03/2026 | Generiek gemaakt; auteur-veld uitgebreid; Mermaid + YAML secties toegevoegd | Danny Depecker + Claude |
| 4.1 | 24/03/2026 | Gecentraliseerd in PHARMA-Conventions | Danny Depecker |
