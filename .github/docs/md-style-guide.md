# Documentatie Style Guide

**Versie:** 4.0  
**Laatst bijgewerkt:** 17/03/2026

**Doel:** Consistente opmaak en stijl voor alle projectdocumentatie  
**Type:** Reference  
**Auteur:** Danny Depecker + Claude  
**Status:** Approved

**Bestandsnaam:** md-style-guide.md  
**Path:** .github/docs/

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

**Elk markdown document begint met deze gestandaardiseerde header:**

````markdown
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
````

**Belangrijk:** Bij verplaatsing naar `archive/` blijven Bestandsnaam en Path ongewijzigd
(tonen originele locatie voor traceerbaarheid).

### 1.2 Verplichte Velden

**Alle velden zijn verplicht.** Gebruik `NVT` (Niet Van Toepassing) of `TBD` (To Be Defined)
indien geen waarde beschikbaar.

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

Het **Auteur** veld geeft de primaire eigenaar of opsteller van het document aan.
Dit kan een persoon zijn, een AI-tool, of een combinatie:

| Situatie                 | Waarde                 |
| ------------------------ | ---------------------- |
| Menselijke auteur        | `Danny Depecker`       |
| GitHub Copilot           | `GHC`                  |
| Claude (Anthropic)       | `Claude`               |
| Gemini (Google)          | `Gemini`               |
| Samenwerking mens + AI   | `Danny Depecker + GHC` |
| Samenwerking meerdere AI | `GHC + Claude`         |

**Rationale:** AI-tools kunnen volwaardige auteurs zijn van documentatie.
Transparantie over de opsteller verhoogt traceerbaarheid en betrouwbaarheid.

**Speciale regel voor Archive:**

- Bij verplaatsing naar `archive/` blijven Bestandsnaam en Path **ongewijzigd**
- Ze tonen de **originele locatie** voor traceerbaarheid
- Voorbeeld: Path blijft `docs/03-operationeel/tools/` ook al staat bestand in `docs/archive/`

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

**Speciale waarden:** `NVT`, `TBD`

### 1.5 Header Voorbeelden

**Implementatie Document:**

````markdown
# ProjectX - Fase 1: Omgevingsinrichting

**Versie:** 1.0  
**Laatst bijgewerkt:** 17/03/2026

**Doel:** Installatie en configuratie van de ontwikkelomgeving  
**Type:** Implementatie  
**Auteur:** Danny Depecker  
**Status:** In Progress

**Bestandsnaam:** fase1-omgevingsinrichting.md  
**Path:** docs/02-tactisch/fasen/

---
````

**ADR Document:**

````markdown
# ProjectX - ADR-001: Keuze van dataopslagformaat

**Versie:** 1.0  
**Laatst bijgewerkt:** 17/03/2026

**Doel:** Motivatie voor de keuze tussen CSV, SQLite en SQL Server  
**Type:** ADR  
**Auteur:** Danny Depecker + GHC  
**Status:** Approved

**Bestandsnaam:** architectuur-beslissingen.md  
**Path:** docs/01-strategisch/

---
````

**Gearchiveerd Document:**

````markdown
# ProjectX - Implementatie Gids

**Versie:** 3.0  
**Laatst bijgewerkt:** 01/02/2026

**Doel:** Fase-gebaseerde implementatie instructies (originele versie)  
**Type:** Guide  
**Auteur:** Danny Depecker  
**Status:** Archived

**Bestandsnaam:** implementatie-gids-ARCHIEF-v3.0-20260201.md  
**Path:** docs/02-tactisch/

---
````

> ⚠️ **Let op:** Path toont `docs/02-tactisch/` (originele locatie), ook al staat bestand nu
> in `docs/archive/`. Dit behoudt traceerbaarheid.

### 1.6 Optionele Footer (Implementatie Docs)

**Voor documenten met een duidelijke completion date en volgende stap:**

````markdown
---

**Voltooid op:** 17/03/2026  
**Volgende stap:** [Fase 2: Database Connectivity](fase2-database-connectivity.md) →
````

**Gebruik:** Alleen voor seriële documenten zoals fase implementatie guides.

---

## 2. Algemene Richtlijnen

### 2.1 Taal

**Nederlandse voorkeur voor documentatie:**

- Alle markdown documentatie in **Nederlands**
- Code comments in **Nederlands**
- Variabele/functie namen in **Engels** (best practice)
- Technische termen in Engels waar Nederlands onnatuurlijk klinkt
  - Voorbeelden: *commit*, *repository*, *pull request*, *merge*

**Uitzonderingen Engels:**

- README.md bestanden (indien open source / internationaal team)
- API documentatie (indien externe consumers)
- Error messages in code (Engels = standaard)

### 2.2 Datumnotatie

**In tekst:** ALTIJD `DD/MM/YYYY`

- ✅ Correct: 10/02/2026
- ❌ Fout: 02/10/2026, 2026-02-10

**In bestandsnamen:** `YYYY-MM-DD` (ISO formaat voor sortering)

- ✅ Correct: `2026-02-10-meeting-notes.md`
- ❌ Fout: `10-02-2026-meeting-notes.md`

**Rationale:** ISO formaat sorteert chronologisch in bestandsverkenner en PyCharm.

### 2.3 Regellengte

**Aanbevolen:** 80-100 karakters per regel voor leesbaarheid.

**Uitzonderingen:**

- Lange URL's (niet wrappen)
- Tabellen (mogen breder)
- Code blokken (formatting behouden)

### 2.4 Lege Regels

**Tussen secties:** 1 lege regel

````markdown
## Sectie 1

Content hier.

## Sectie 2
````

**Tussen paragrafen:** 1 lege regel

````markdown
Eerste paragraaf tekst hier.

Tweede paragraaf tekst hier.
````

**Voor/na code blokken:** 1 lege regel

````markdown
Tekst voor code.

```python
code hier
```text
Tekst na code.
````

---

## 3. Koppen Hiërarchie

### 3.1 Header Levels

**Gebruik ATX-style headers** (met `#` symbolen):

````markdown
# H1 - Document Titel (1× per document)
## H2 - Hoofdsecties
### H3 - Subsecties
#### H4 - Sub-subsecties
##### H5 - Zelden gebruiken
###### H6 - Vermijden (te diep)
````

**Regels:**

- **H1:** Alleen voor document titel
- **H2:** Hoofdsecties (nummeren met 1, 2, 3...)
- **H3:** Subsecties (nummeren met 1.1, 1.2, 2.1...)
- **H4+:** Alleen indien echt nodig

**Geen skippen van levels:**

- ✅ Correct: H1 → H2 → H3
- ❌ Fout: H1 → H3 (H2 overgeslagen)

### 3.2 Header Nummering

**Implementatie documenten:** Nummering gebruiken

````markdown
## 1. Omgevingsinrichting
### 1.1 Lokale Setup
### 1.2 Remote Configuratie

## 2. Database Connectivity
### 2.1 Driver Installatie
````

**Andere documenten:** Nummering optioneel

````markdown
## Inleiding
## Gebruik
## Troubleshooting
````

### 3.3 Anchor Links

**Headers genereren automatisch anchors:**

````markdown
## 3. Koppen Hiërarchie

Link: [Zie Koppen Hiërarchie](#3-koppen-hiërarchie)
````

**Conversie regels:**

- Lowercase
- Spaties → hyphens
- Speciale karakters verwijderen
- Nummering blijft

---

## 4. Tekstopmaak

### 4.1 Nadruk

**Italic:** Lichte nadruk (gebruik `*` of `_`)

````markdown
Dit is *italic* of _italic_ tekst.
````

**Bold:** Sterke nadruk (gebruik `**` of `__`)

````markdown
Dit is **bold** of __bold__ tekst.
````

**Bold + Italic:** Zeer sterke nadruk

````markdown
Dit is ***zeer belangrijk*** of ___zeer belangrijk___.
````

**Voorkeur:** Gebruik `*` voor italic en `**` voor bold (consistency).

### 4.2 Inline Code

**Voor korte code snippets, variabelen, commando's:**

````markdown
Gebruik de `git commit` command.
Variabele `$configPath` bevat het pad.
````

### 4.3 Citaten

**Gebruik blockquotes voor citaten of callouts:**

````markdown
> Dit is een blockquote of callout tekst.

> **⚠️ KRITIEK:** Gebruik alleen echte productiedata met toestemming!
````

### 4.4 Horizontale Lijnen

**Gebruik `---` voor sectie-scheiders:**

````markdown
---
````

**Gebruik spaarzaam** — primair na document header en tussen grote secties.

---

## 5. Lijsten

### 5.1 Ongeordende Lijsten

**Gebruik `-` voor bullet points (geen `*` of `+`):**

````markdown
- Item één
- Item twee
  - Sub-item A
  - Sub-item B
- Item drie
````

### 5.2 Geordende Lijsten

**Gebruik nummers voor stappen of volgorde:**

````markdown
1. Eerste stap
2. Tweede stap
3. Derde stap
````

**Tip:** Gebruik altijd `1.` voor elk item (markdown rendert automatisch correct):

````markdown
1. Item
1. Item
1. Item
````

### 5.3 Checklists

**Voor to-do's of status tracking:**

````markdown
- [x] Voltooid item
- [ ] Nog te doen item
- [ ] Nog een openstaand item
````

### 5.4 Nesting

**Maximaal 2-3 niveaus diep:**

````markdown
- Hoofditem
  - Sub-item
    - Sub-sub-item (maximaal diepte)
````

---

## 6. Code Blokken

### 6.1 Taalspecificatie

**Altijd taal specificeren voor syntax highlighting:**

````markdown
```python
def hello_world():
    print("Hello, World!")
```text
```powershell
Get-Process | Select-Object Name, CPU
```text
```sql
SELECT id, naam FROM tabel WHERE actief = 1;
```text
```bash
cd /project && git status
```text
````

### 6.2 Veelgebruikte Talen

| Taal         | Code Block Tag |
| ------------ | -------------- |
| Python       | `python`       |
| PowerShell   | `powershell`   |
| SQL          | `sql`          |
| Bash/Shell   | `bash`         |
| JSON         | `json`         |
| YAML         | `yaml`         |
| Markdown     | `markdown`     |
| Mermaid      | `mermaid`      |
| Tekst/Output | `text`         |

### 6.3 Generiek SQL Voorbeeld

````markdown
```sql
SELECT id, omschrijving, einddatum
FROM artikel
WHERE einddatum IS NULL
ORDER BY id;
```text
````

### 6.4 Inline vs Block

**Inline code:** Voor korte snippets in tekst

````markdown
Gebruik `Get-Process` om processen te tonen.
````

**Block code:** Voor multi-line of formattering

````markdown
```powershell
Get-Process |
    Where-Object { $_.CPU -gt 100 } |
    Select-Object Name, CPU
```text
````

### 6.5 Mermaid Diagrammen

**Gebruik `mermaid` als taalspecificatie:**

````markdown
```mermaid
graph TD
    A[Start] --> B{Beslissing}
    B -->|Ja| C[Actie A]
    B -->|Nee| D[Actie B]
```text
````

**Ondersteunde diagramtypes:**

| Type             | Tag                     | Gebruik Voor                  |
| ---------------- | ----------------------- | ----------------------------- |
| Flowchart        | `graph TD` / `graph LR` | Procesflows, beslisbomen      |
| Sequentiediagram | `sequenceDiagram`       | API-calls, systeeminteracties |
| Gantt chart      | `gantt`                 | Projectplanning, fasering     |
| Klassendiagram   | `classDiagram`          | Datamodellen, OOP-structuur   |
| Entiteit-relatie | `erDiagram`             | Databaseschema's              |
| Toestandsdiagram | `stateDiagram-v2`       | Statusovergangen              |

**Gantt voorbeeld (projectplanning):**

````markdown
```mermaid
gantt
    title Projectplanning 2026
    dateFormat  YYYY-MM-DD
    section Fase 1
    Analyse           :done,    f1a, 2026-01-01, 2026-01-31
    section Fase 2
    Implementatie     :active,  f2a, 2026-02-01, 2026-03-31
    section Fase 3
    Go-live           :         f3a, 2026-04-01, 2026-04-30
```text
````

**Richtlijnen:**

- Gebruik Mermaid voor diagrammen die in versiebeheer beheerd worden (tekst = diffbaar)
- Geef elk diagram een beschrijvende `title`
- Voeg een korte omschrijving toe boven het codeblok

---

## 7. Links en Referenties

### 7.1 Interne Links (Relatief)

**Links binnen een project:**

````markdown
[Zie Fase 1](docs/02-tactisch/fasen/fase1-omgevingsinrichting.md)
[Troubleshooting](#troubleshooting)
[Architectuur Beslissingen](../architectuur-beslissingen.md)
````

**Regels:**

- Gebruik relatieve paden
- Gebruik lowercase voor bestandsnamen
- Gebruik hyphens in namen (geen spaties)

### 7.2 Externe Links

**URLs met beschrijving:**

````markdown
[GitHub Repository](https://github.com/organisatie/project)
[Projectdocumentatie](https://docs.project.example.com)
````

**Directe URLs (indien nodig):**

````markdown
https://docs.microsoft.com/powershell
````

### 7.3 Referentie-Style Links

**Voor herhaalde links of lange URLs:**

````markdown
Dit is een [link naar GitHub][github] en nog een [link naar GitHub][github].

[github]: https://github.com/organisatie/project
````

### 7.4 Anchor Links

**Naar headers binnen document:**

````markdown
Zie [Koppen Hiërarchie](#3-koppen-hiërarchie) voor details.
````

---

## 8. Tabellen

### 8.1 Basis Tabel Syntax

````markdown
| Header 1    | Header 2    | Header 3    |
| ----------- | ----------- | ----------- |
| Row 1 Col 1 | Row 1 Col 2 | Row 1 Col 3 |
| Row 2 Col 1 | Row 2 Col 2 | Row 2 Col 3 |
````

### 8.2 Kolom Alignment

````markdown
| Left Aligned | Center Aligned | Right Aligned |
| :----------- | :------------: | ------------: |
| Links        | Center         | Rechts        |
| Text         | Text           | 123           |
````

**Alignment codes:**

- `:---` = Links
- `:---:` = Center
- `---:` = Rechts

### 8.3 Complexe Tabellen

**Voor complexe layouts, gebruik HTML:**

````html
<table>
  <tr>
    <th rowspan="2">Header</th>
    <th colspan="2">Spanned Header</th>
  </tr>
  <tr>
    <td>Cell 1</td>
    <td>Cell 2</td>
  </tr>
</table>
````

### 8.4 Tabel Formatting

**Consistent spatiëring voor leesbaarheid:**

````markdown
| Veld         | Type     | Beschrijving             |
| ------------ | -------- | ------------------------ |
| id           | INT      | Primaire sleutel         |
| omschrijving | VARCHAR  | Nederlandse omschrijving |
| einddatum    | DATETIME | Einddatum van het record |
````

---

## 9. Afbeeldingen

### 9.1 Basis Image Syntax

````markdown
![Alt text](path/to/image.png)
![Alt text](path/to/image.png "Optional title")
````

### 9.2 Image Locatie

**Aanbevolen projectstructuur:**

````text
docs/
├── images/
│   ├── architecture-diagram.png
│   └── workflow-screenshot.png
└── 02-tactisch/
    └── fase1-omgevingsinrichting.md
````

**Relatief pad vanuit fase1-omgevingsinrichting.md:**

````markdown
![Architecture Diagram](../images/architecture-diagram.png)
````

### 9.3 Image Sizing (HTML)

**Markdown ondersteunt geen native sizing, gebruik HTML:**

````html
<img src="../images/screenshot.png" width="600" alt="Screenshot">
````

### 9.4 Alt Text

**Altijd alt text voor toegankelijkheid:**

````markdown
✅ Goed: ![Dashboard Screenshot](../images/dashboard.png)
❌ Slecht: ![](../images/dashboard.png)
````

---

## 10. Speciale Elementen

### 10.1 Admonitions (Waarschuwingen)

**Gebruik emoji voor visuele cues:**

````markdown
⚠️ **BELANGRIJK:** Dit is kritieke informatie.

✅ **TIP:** Handig om te weten.

❌ **FOUT:** Veelgemaakte fout om te vermijden.

🔄 **IN PROGRESS:** Work in progress sectie.

⏳ **GEPLAND:** Nog te implementeren.
````

**Alternatief (blockquote style):**

````markdown
> **⚠️ KRITIEK:** Gebruik alleen échte database, niet localhost!
````

### 10.2 Collapse Sections (GitHub)

**Voor lange details:**

````markdown
<details>
<summary>Klik om details te tonen</summary>

Verborgen content hier.
Kan markdown bevatten.

</details>
````

### 10.3 Badges (Optioneel)

**Voor status indicaties:**

````markdown
![Status: In Progress](https://img.shields.io/badge/status-in%20progress-yellow)
![Version: 1.0](https://img.shields.io/badge/version-1.0-blue)
````

### 10.4 Keyboard Keys

**Voor toetsencombinaties:**

````markdown
Druk <kbd>Ctrl</kbd>+<kbd>C</kbd> om te kopiëren.
Gebruik <kbd>Enter</kbd> om te bevestigen.
````

---

## 11. Bestandsnamen

### 11.1 Naamgeving Conventies

**Algemene regels:**

- Lowercase (kleine letters)
- Hyphens voor spaties (geen underscores)
- Beschrijvende namen (geen afkortingen tenzij duidelijk)
- Extensie: `.md`

**Voorbeelden:**

- ✅ Goed: `fase1-omgevingsinrichting.md`, `troubleshooting-guide.md`, `adr-001-database-keuze.md`
- ❌ Slecht: `Fase1_Omgevingsinrichting.md`, `trblsht.md`, `doc1.md`

### 11.2 Datum Prefixes

**Voor chronologische sortering:**

````text
2026-03-17-meeting-notes.md
2026-03-17-sprint-retrospective.md
````

**Gebruik:** Meeting notes, retrospectives, changelogs.

### 11.3 Versioning in Filenames

**Archieven met versie:**

````text
implementatie-gids-ARCHIEF-v3.0-20260201.md
````

**Patroon:** `[naam]-ARCHIEF-v[X.Y]-[YYYYMMDD].md`

### 11.4 Speciale Bestanden

**Altijd hoofdletters:**

- `README.md` - Project/folder intro
- `CHANGELOG.md` - Versie historie
- `LICENSE.md` - Licentie informatie
- `CONTRIBUTING.md` - Bijdrage richtlijnen

---

## 12. Git Commit Messages

### 12.1 Commit Message Structuur

````text
<type>: <korte beschrijving> (max 50 chars)

[Optionele langere uitleg na lege regel]
````

### 12.2 Type Prefixes

| Type        | Gebruik                                  |
| ----------- | ---------------------------------------- |
| `docs:`     | Documentatie wijzigingen                 |
| `feat:`     | Nieuwe feature                           |
| `fix:`      | Bug fix                                  |
| `refactor:` | Code refactoring (geen nieuwe features)  |
| `test:`     | Test toevoegingen/wijzigingen            |
| `chore:`    | Maintenance taken (dependencies, config) |
| `style:`    | Code formatting (geen functionaliteit)   |

### 12.3 Voorbeelden

**Documentatie update:**

````text
docs: update fase2 met implementatieresultaten
````

**Script toevoeging:**

````text
feat: add monthly report generation script
````

**Bug fix:**

````text
fix: correct date parsing in data import module
````

**Meerdere wijzigingen:**

````text
docs: split implementatie-gids into fase documents

- Created fase1-omgevingsinrichting.md
- Created fase2-data-analyse.md
- Created fase3-rapportage.md
- Archived old implementatie-gids.md as v3.0
````

### 12.4 Commit Message Tips

**Do's:**

- ✅ Gebruik imperatieve vorm: "add" niet "added"
- ✅ Eerste letter lowercase (na type prefix)
- ✅ Geen punt aan einde van subject line
- ✅ Beschrijf WHAT en WHY, niet HOW

**Don'ts:**

- ❌ Vage messages: "update", "fix stuff", "changes"
- ❌ Te lang (>50 chars in subject line)
- ❌ Meerdere ongerelateerde wijzigingen in 1 commit

---

## 13. YAML Frontmatter

### 13.1 Wat is YAML Frontmatter?

YAML frontmatter is een blok metadata bovenaan een bestand, afgesloten met `---`.
Het wordt verwerkt door tools zoals GitHub Copilot, Jekyll, MkDocs, en diverse CI/CD-systemen —
maar **niet** gerenderd als zichtbare inhoud in GitHub of markdown previewers.

````markdown
---
applyTo: '**/*.py'
---

# Document inhoud begint hier
````

### 13.2 Wanneer Gebruiken

| Situatie                               | Gebruik Frontmatter                                  |
| -------------------------------------- | ---------------------------------------------------- |
| `.instructions.md` voor GitHub Copilot | ✅ Verplicht (`applyTo`)                              |
| Standaard projectdocumentatie          | ❌ Niet nodig (gebruik document header, zie sectie 1) |
| MkDocs of Jekyll sites                 | ✅ Indien vereist door platform                       |
| README.md bestanden                    | ❌ Niet aanbevolen                                    |

### 13.3 Copilot Instructions (`applyTo`)

**Het `applyTo` veld bepaalt op welke bestanden de instructies van toepassing zijn:**

````yaml
---
applyTo: '**/*'              # Alle bestanden (gebruik spaarzaam)
applyTo: '**/*.py'           # Alleen Python bestanden
applyTo: '**/*.py,**/*.ps1'  # Python én PowerShell bestanden
applyTo: 'src/**/*'          # Alles onder de src/ map
---
````

> ⚠️ **Let op:** `applyTo: '**/*'` past de instructies toe op **alle** bestanden inclusief
> markdown, YAML en JSON. Beperk dit altijd tot relevante extensies.

### 13.4 Combinatie met Document Header

**YAML frontmatter en de document header sluiten elkaar niet uit:**

````markdown
---
applyTo: '**/*.py,**/*.ps1'
---

# ProjectX - Code Formatting Instructions

**Versie:** 1.0  
**Laatst bijgewerkt:** 17/03/2026
...
````

**Volgorde:** Frontmatter altijd als **eerste** blok, daarna de document header.

---

## Versiehistorie

| Versie | Datum      | Wijzigingen                                                                                                                                                                           | Auteur                  |
| ------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| 1.0    | 03/02/2026 | Initial release                                                                                                                                                                       | Danny Depecker          |
| 1.1    | 09/02/2026 | ISO-datum uitzondering voor bestandsnamen toegevoegd                                                                                                                                  | Gemini                  |
| 2.0    | 10/02/2026 | Complete herziening: nieuwe header structuur, verplichte velden, uitgebreide secties                                                                                                  | Danny Depecker          |
| 2.1    | 16/02/2026 | Bestandsnaam en Path velden toegevoegd aan header template                                                                                                                            | Danny Depecker + GHC    |
| 2.2    | 18/02/2026 | Standaard auteur personalia toegevoegd                                                                                                                                                | GHC                     |
| 3.0    | 02/03/2026 | Gegeneraliseerde template structuur toegepast; secties 4–5 uitgebreid                                                                                                                 | Danny Depecker + Claude |
| 4.0    | 17/03/2026 | Generiek gemaakt (projectnaam-agnostisch); auteur-veld uitgebreid met AI-tools; Mermaid sectie (6.5) toegevoegd; YAML Frontmatter sectie (13) toegevoegd; voorbeelden geneutraliseerd | Danny Depecker + Claude |

---

**Laatst Gereviewd:** 17/03/2026  
**Volgende Review:** Bij significante workflow wijzigingen
