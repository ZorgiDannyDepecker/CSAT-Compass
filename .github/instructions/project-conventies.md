---
applyTo: '**/*'
---

# ZORGI PHARMA - Project Conventies  

**Versie:** 2.8
**Laatst bijgewerkt:** 26/05/2026
**Overgedragen naar PHARMA-Conventions:** 24/03/2026

**Doel:** Gedeelde afspraken en conventies voor alle ZORGI PHARMA-projecten
**Type:** Convention
**Auteur:** Danny Depecker + Claude-P
**Status:** Approved
**Bestandsnaam:** project-conventies.md
**Path:** conventions\instructions\

---

## Inhoudsopgave  

1. [Relatie tot Style Guide](#1-relatie-tot-style-guide)
2. [Taal en Communicatie](#2-taal-en-communicatie)
3. [Bestandsnamen en Datumnotatie](#3-bestandsnamen-en-datumnotatie)
4. [Document Header en Metadata](#4-document-header-en-metadata)
5. [Visuele Hiërarchie en Stijl](#5-visuele-hiërarchie-en-stijl)
6. [Code Conventies](#6-code-conventies)
7. [Diagrammen en Visualisaties](#7-diagrammen-en-visualisaties)
8. [Navigatie en Traceerbaarheid](#8-navigatie-en-traceerbaarheid)
9. [Prompt Frameworks](#9-prompt-frameworks)
10. [Afkortingen](#10-afkortingen)
11. [T-shirt schattingen](#11-t-shirt-schattingen)
12. [Branding & productnamen](#12-branding--productnamen)
13. [Code documentatie](#13-code-documentatie)

---

## 1. Relatie tot Style Guide  

Deze conventies zijn een **aanvulling op** — niet een vervanging van — de generieke
`md-style-guide.md`. De hiërarchie is als volgt:

| Niveau    | Bestand                   | Doel                                             |
| --------- | ------------------------- | ------------------------------------------------ |
| Generiek  | `md-style-guide.md`       | Universele markdown- en opmaakregels             |
| Project   | `project-conventies.md`   | ZORGI PHARMA-specifieke afspraken (dit document) |
| Instantie | `copilot-instructions.md` | Projectspecifieke GHC-instructies                |

Bij conflict tussen niveaus geldt: **project-conventies > style guide** voor ZORGI PHARMA-projecten.

---

## 2. Taal en Communicatie  

- **Documentatie:** Nederlands — alle markdown-bestanden, README's, commentaren en docstrings
- **Code-entiteiten:** Engels — variabelen, functies, klassen, SQL-tabellen, kolomnamen
- **Technische termen:** Engels waar Nederlands onnatuurlijk klinkt
  - Voorbeelden: *commit*, *repository*, *pull request*, *merge*, *branch*
- **Doel:** Uniformiteit waarborgen over alle ZORGI PHARMA-projecten

---

## 3. Bestandsnamen en Datumnotatie  

### 3.1 Bestandsnamen  

- **Kebab-case:** Altijd lowercase met hyphens — geen underscores, geen spaties
  - ✅ Correct: `operations-runbook.md`, `fase1-omgevingsinrichting.md`
  - ❌ Fout: `Operations_Runbook.md`, `Fase1 Omgevingsinrichting.md`
- **Meta-bestanden:** UPPERCASE voor speciale projectbestanden
  - `README.md`, `CHANGELOG.md`, `LICENSE.md`, `CONTRIBUTING.md`

### 3.2 Datumnotatie  

| Context                      | Formaat      | Voorbeeld                                     |
| ---------------------------- | ------------ | --------------------------------------------- |
| In tekst en document headers | `DD/MM/YYYY` | `17/03/2026`                                  |
| In bestandsnamen             | `YYYY-MM-DD` | `2026-03-17-meeting-notes.md`                 |
| In archief-bestandsnamen     | `YYYYMMDD`   | `implementatie-gids-ARCHIEF-v3.0-20260317.md` |

**Rationale bestandsnamen:** ISO-formaat sorteert chronologisch in Bestandsverkenner en PyCharm.

---

## 4. Document Header en Metadata  

### 4.1 Verplichte Header  

Elk markdown-document volgt de verplichte header uit `md-style-guide.md` sectie 1.
Projectspecifieke aanvulling: de H1-titel volgt altijd het patroon:

```text
# [PROJECTNAAM] - [Document Titel]
```

Voorbeelden: `# CSAT - Maandrapportage Januari 2026`, `# Scriptorium - ADR-003: DBHub Keuze`

### 4.2 Auteur Veld — ZORGI PHARMA Standaard  

Het **Auteur** veld registreert transparant wie of wat het document heeft opgesteld.
AI-tools zijn volwaardige auteurs binnen ZORGI PHARMA-projecten.

| Situatie               | Waarde                      |
| ---------------------- | --------------------------- |
| Menselijke auteur      | `Danny Depecker`            |
| GitHub Copilot         | `GHC`                       |
| Claude Pro (Anthropic) | `Claude-P`                  |
| Gemini (Google)        | `Gemini`                    |
| Mens + GitHub Copilot  | `Danny Depecker + GHC`      |
| Mens + Claude Pro      | `Danny Depecker + Claude-P` |
| Meerdere AI-tools      | `GHC + Claude-P`            |

### 4.3 Versiehistorie  

**Elk document eindigt met een versiehistorie tabel** — geen uitzonderingen.

```markdown
## Versiehistorie

| Versie | Datum      | Wijzigingen     | Auteur         |
| ------ | ---------- | --------------- | -------------- |
| 1.0    | 17/03/2026 | Initiële versie | Danny Depecker |
```

**Opmaakregel:** Geen bold-formatting (`**tekst**`) in tabelcellen van de versiehistorie.

---

## 5. Visuele Hiërarchie en Stijl  

### 5.1 Emoji Gebruik  

Gebruik emoji als **visuele ankers** voor snelle oriëntatie in documenten.

> ⚠️ **Gebruik altijd de codepoints uit onderstaande tabel.** Visueel identieke emoji
> kunnen uit verschillende Unicode-blokken komen en anders renderen in PDF.

#### 5.1a Statusemoji  

| Emoji | Unicode | Betekenis             | Gebruik                      |
| ----- | ------- | --------------------- | ---------------------------- |
| ⚠️    | U+26A0  | Risico / Waarschuwing | Kritieke aandachtspunten     |
| ✅     | U+2705  | Voltooid / Correct    | Bevestiging, good practices  |
| ❌     | U+274C  | Fout / Incorrect      | Fouten, don'ts               |
| 🚀     | U+1F680 | Release / Go-live     | Mijlpalen, deployments       |
| 💡     | U+1F4A1 | Idee / Tip            | Suggesties, hints            |
| 🎯     | U+1F3AF | Focus / Doel          | Prioriteiten, doelstellingen |
| 🔍     | U+1F50D | Analyse / Onderzoek   | Bevindingen, inspecties      |
| 🔄     | U+1F504 | In progress           | Work in progress secties     |
| ⏳     | U+23F3  | Gepland               | Nog te implementeren         |
| 📋     | U+1F4CB | Checklist / Overzicht | Lijsten, samenvattingen      |

#### 5.1b Richtingspijlen  

Gebruik uitsluitend pijlen uit het **Arrows-blok** (U+2190–U+21FF):

| Emoji | Unicode | Richting | Pijler     |
| ----- | ------- | -------- | ---------- |
| ↑     | U+2191  | Noord    | PHARMA     |
| →     | U+2192  | Oost     | CARE       |
| ↓     | U+2193  | Zuid     | ERP4HC     |
| ←     | U+2190  | West     | CARE ADMIN |

### 5.2 Headers  

- Alleen het **eerste woord** van een header krijgt een hoofdletter (Nederlandse conventie)
  - ✅ Correct: `## Algemene richtlijnen`
  - ❌ Fout: `## Algemene Richtlijnen`
- Uitzondering: eigennamen, afkortingen en productnamen

### 5.3 Lijsten  

- Ongeordende lijsten: altijd `-` als bullet
- Geordende lijsten: nummering start altijd bij `1`
- Maximale diepte: 3 niveaus

---

## 6. Code Conventies  

### 6.1 Code Block Formatting  

1. **Taalspecificatie:** `bash` (ongeacht de werkelijke programmeertaal)
2. **Eerste regel:** absoluut bestandspad voorafgegaan door `#` en één spatie
3. **Tweede regel:** volledig leeg
4. **Vanaf regel 3:** volledige, uitvoerbare code zonder omissies

```bash
# C:\Users\danndepe\Documents\AI\[PROJECT]\code\script.py

[volledige code hier]
```

### 6.2 Commentaren en Docstrings  

- **Inline commentaren:** Nederlands
- **Docstrings** (Python `"""..."""`): Nederlands
- **Variabele- en functienamen:** Engels

### 6.3 Veelgebruikte Talen per Project  

| Taal         | Code Block Tag | Primair gebruik                      |
| ------------ | -------------- | ------------------------------------ |
| Python       | `python`       | Analyse, rapportage, automatisering  |
| PowerShell   | `powershell`   | Windows scripting, hulptools         |
| SQL          | `sql`          | Databasequeries, validatie           |
| Bash         | `bash`         | Code block formatting (zie 6.1)      |
| Mermaid      | `mermaid`      | Diagrammen en planningsvisualisaties |
| Tekst/Output | `text`         | Verwachte terminal output            |

---

## 7. Diagrammen en Visualisaties  

### 7.1 Mermaid als standaard  

Gebruik **Mermaid** voor alle diagrammen die in versiebeheer worden beheerd.

### 7.2 Aanbevolen diagramtypes  

| Situatie                        | Mermaid Type            |
| ------------------------------- | ----------------------- |
| Projectplanning en fasering     | `gantt`                 |
| Procesflows en beslisbomen      | `graph TD` / `graph LR` |
| Systeeminteracties en API-calls | `sequenceDiagram`       |
| Databaseschema's                | `erDiagram`             |
| Statusovergangen                | `stateDiagram-v2`       |

---

## 8. Navigatie en Traceerbaarheid  

### 8.1 Relatieve Links  

Gebruik **altijd relatieve paden** voor interne documentlinks.

### 8.2 Archief Traceerbaarheid  

Bij verplaatsing naar `archive/` blijven **Bestandsnaam** en **Path** ongewijzigd.

### 8.3 Documentatielagen  

| Laag         | Map                     | Inhoud                      |
| ------------ | ----------------------- | --------------------------- |
| Strategisch  | `docs/01-strategisch/`  | WAAROM — ADR's, projectplan |
| Tactisch     | `docs/02-tactisch/`     | HOE — fasen, implementatie  |
| Operationeel | `docs/03-operationeel/` | DAGELIJKS — runbook, tools  |

---

## 9. Prompt Frameworks  

### 9.1 CREATE Framework  

| Letter | Element               | Beschrijving                                   |
| ------ | --------------------- | ---------------------------------------------- |
| **C**  | Context               | Projectcontext en doelstelling meegeven        |
| **R**  | Role                  | Rol van de AI definiëren                       |
| **E**  | Explicit instructions | Concrete taakomschrijving                      |
| **A**  | Audience              | Doelpubliek van de output                      |
| **T**  | Tone                  | Gewenste toon                                  |
| **E**  | Examples              | Voorbeeldoutput of referentiedocument meegeven |

### 9.2 CARE Framework  

| Letter | Element | Beschrijving                           |
| ------ | ------- | -------------------------------------- |
| **C**  | Context | Situatieschets en achtergrond          |
| **A**  | Action  | Gewenste actie of taak                 |
| **R**  | Result  | Verwachte uitkomst of format           |
| **E**  | Example | Concreet voorbeeld ter verduidelijking |

### 9.3 Wanneer welk framework  

| Situatie                         | Framework |
| -------------------------------- | --------- |
| Complexe analyse met doelpubliek | CREATE    |
| Rapportage voor leadership       | CREATE    |
| Gerichte taakuitvoering          | CARE      |
| Codewijziging of debugging       | CARE      |

---

## 10. Afkortingen  

| Afkorting    | Voluit                              | Toelichting                              |
| ------------ | ----------------------------------- | ---------------------------------------- |
| GHC          | GitHub Copilot                      | AI-coding assistent in PyCharm           |
| GHD          | GitHub Desktop                      | GUI-client voor Git-operaties op Windows |
|              | PyCharm 2026.x                      | Primaire IDE                             |
| ADR          | Architecture Decision Record        | Architectuurbeslissing                   |
| NVT          | Niet Van Toepassing                 | Leeg verplicht veld                      |
| TBD          | To Be Defined                       | Nog in te vullen veld                    |
| PII          | Personally Identifiable Information | Persoonsgegevens                         |
| Claude-P     | Claude Pro (Anthropic)              | AI-assistent voor analyse en redactie    |
| M365 Copilot | Microsoft 365 Copilot               | AI-integratie in Microsoft 365-suite     |

---

## 11. T-shirt schattingen  

| Maat  | Uurbandbreedte | Gewicht (t.o.v. XS) | Typisch gebruik                                       |
| ----- | -------------- | ------------------- | ----------------------------------------------------- |
| XS    | 1–4u           | 1×                  | Kleine aanpassing, bugfix, config-wijziging           |
| S     | 4–8u           | 2×                  | Eenvoudige feature, bouwt op bestaande infrastructuur |
| M     | 8–24u          | 5×                  | Nieuwe module of systeem, meerdere bestanden          |
| L     | 24–48u         | 10×                 | Complexe feature, meerdere afhankelijkheden, UX-werk  |
| XL    | 48–80u         | 20×                 | Grote deeloplossing, cross-module impact              |
| XXL   | 80–120u        | 30×                 | Volledige fase of subsysteem                          |
| XXXL  | >120u          | >40×                | Heel project of meerdere fasen gecombineerd           |

---

## 12. Branding & productnamen  

> Volledig referentiedocument: `PHARMA-Conventions\zorgi\zorgi_design_system.md`

### 12.1 Productnamen — verplichte schrijfwijze  

| Product            | Correcte spelling | Fout                        |
| ------------------ | ----------------- | --------------------------- |
| Bedrijfsnaam       | ZORGI             | Zorgi / zorgi               |
| Care-product       | CARE              | Care / care                 |
| Care Admin-product | OAZIS             | Oazis / oazis               |
| Pharma-product     | ZORGI PHARMA      | Zorgi Pharma / ZORGI pharma |
| ERP-product        | ERP4HC²·⁰         | ERP4HC / erp4hc             |

### 12.2 Kleuren — referentie  

| Variabele                  | HEX       | Gebruik                      |
| -------------------------- | --------- | ---------------------------- |
| `--zorgi-dark-blue`        | `#003a70` | Primaire kleur, H1, H4       |
| `--zorgi-red`              | `#dc2b26` | Accent, gradient einde       |
| `--zorgi-purple`           | `#7f4267` | Gradient midden, titelbalken |
| `--zorgi-grey-blue`        | `#5f8495` | H2, secundaire tekst         |
| `--zorgi-light-blue`       | `#609fce` | H3, H5, accenten             |
| `--zorgi-ultra-light-blue` | `#d7e7f3` | Achtergronden, kaarten       |

### 12.3 Design System — beheer en synchronisatie  

#### Golden source  

```text
PHARMA-Conventions\zorgi\zorgi_design_system.md   ← ENIGE bewerkbare versie
```

- Wijzigingen aan kleuren, typografie of branding **altijd** hier doorvoeren
- Elk project beheert een **read-only kopie** in `.github/docs/zorgi_design_system.md`
- Die kopie **nooit rechtstreeks bewerken** — aanpassingen gaan verloren bij volgende sync

#### Kopieën per project  

| Project                   | Pad read-only kopie                   |
| ------------------------- | ------------------------------------- |
| CSAT-Compass              | `.github/docs/zorgi_design_system.md` |
| *(toekomstige projecten)* | `.github/docs/zorgi_design_system.md` |

#### Sync-workflow  

Wanneer de golden source gewijzigd wordt:

1. Pas `PHARMA-Conventions\zorgi\zorgi_design_system.md` aan
2. Voer het sync-script uit in elk betrokken project:

   ```powershell
   # Vanuit de projectroot (bv. CSAT-Compass):
   .\tools\sync-design-system.ps1
   ```

3. Commit de bijgewerkte kopie via `/git`

#### Sync-script — minimale implementatie  

Elk project levert een `tools/sync-design-system.ps1` met deze structuur:

```powershell
# sync-design-system.ps1
# Kopieert de golden source naar de lokale read-only kopie.
$bron  = "C:\Users\danndepe\Documents\AI\PHARMA-Conventions\zorgi\zorgi_design_system.md"
$doel  = "$PSScriptRoot\..\github\docs\zorgi_design_system.md"
Copy-Item -Path $bron -Destination $doel -Force
Write-Host "[OK] zorgi_design_system.md gesynchroniseerd vanuit PHARMA-Conventions"
```

> **Waarom geen symlink?** Symlinks werken niet over machines en werken niet offline.
> Het sync-script is bewust manueel — zo is elke update een bewuste, gedocumenteerde actie.

---

## 13. Code documentatie  

### 13.1 Twee niveaus  

Elk project met niet-triviale code hanteert twee documentatieniveaus die elkaar aanvullen:

| Niveau | Vorm | Locatie | Doelgroep |
| --- | --- | --- | --- |
| Inline | JSDoc / sectiecommentaar | In de broncode zelf | Developer die de code bewerkt |
| Referentie | Markdown-document | `docs/02-tactisch/code-documentatie.md` | Developer die functionaliteit opzoekt zonder de code te openen |

> ⚠️ Bij elke codewijziging **beide** niveaus bijwerken.  
> De twee documenten verwijzen naar elkaar voor traceerbaarheid.

### 13.2 Wanneer verplicht  

| Situatie | Inline JSDoc | Referentiedoc |
| --- | --- | --- |
| JavaScript met meer dan 3 functies | ✅ Verplicht | ✅ Verplicht |
| Python-module met publieke functies | ✅ Verplicht (docstrings) | ⚠️ Aanbevolen |
| Eenvoudig hulpscript (< 30 regels) | ⚠️ Aanbevolen | ❌ Niet vereist |
| Configuratiebestand | ❌ Niet vereist | ❌ Niet vereist |

### 13.3 JSDoc-structuur voor JavaScript  

Zie `code-formatting.md` §3 voor de volledige JSDoc-specificatie.  
Samenvatting:

- Beschrijving in **Nederlands**
- Tags: `@param`, `@returns`, `@note`
- Parameternamen in **Engels**
- Sectiecommentaar in CSS: `/* --- Sectienaam --- */`
- Blokcommentaar in HTML: `<!-- === SECTIENAAM === -->`

### 13.4 Structuur van het referentiedoc  

Het referentiedocument (`docs/02-tactisch/code-documentatie.md`) volgt deze vaste structuur:

| Sectie | Inhoud |
| --- | --- |
| §1 Overzicht | Architectuurschema en gegevensflow (Mermaid) |
| §2 Externe afhankelijkheden | Bibliotheken, versies, doel |
| §3 Toestandsvariabelen | Naam, type, beginwaarde, beschrijving |
| §4 Initialisatie | Wat er bij het laden van de pagina / module gebeurt |
| §5+ Functionele groepen | Per logische groep: naam, beschrijving, parameters, neveneffecten |
| Laatste sectie | Versiehistorie |

### 13.5 Referentie-implementatie  

MD-Converter is de referentie-implementatie voor deze aanpak binnen ZORGI PHARMA:

- Inline JSDoc: `src/md-converter.html`
- Referentiedoc: `docs/02-tactisch/code-documentatie.md`

---

## Versiehistorie  

| Versie | Datum      | Wijzigingen                                                                                   | Auteur                    |
| ------ | ---------- | --------------------------------------------------------------------------------------------- | ------------------------- |
| 1.0    | 01/01/2026 | Initiële versie                                                                               | Danny Depecker            |
| 2.0    | 17/03/2026 | Volledige herziening                                                                          | Danny Depecker + Claude-P |
| 2.1    | 19/03/2026 | T-shirt schattingen toegevoegd                                                                | Danny Depecker + GHC      |
| 2.2    | 19/03/2026 | T-shirt schaal herzien                                                                        | Danny Depecker + GHC      |
| 2.3    | 19/03/2026 | Branding sectie toegevoegd                                                                    | Danny Depecker + GHC      |
| 2.4    | 24/03/2026 | Gecentraliseerd in PHARMA-Conventions; referentie naar zorgi_design_system bijgewerkt         | Danny Depecker            |
| 2.5    | 25/03/2026 | §12.3 toegevoegd: Design System sync-conventie (golden source, read-only kopie, sync-script) | Danny Depecker + GHC      |
| 2.6    | 26/05/2026 | MD032: blanco regels rond lijst in §12.3 sync-workflow gefixed                               | Danny Depecker            |
| 2.7    | 26/05/2026 | §4.2: Claude → Claude-P; §10: Claude-P + M365 Copilot toegevoegd — gemerged vanuit CSAT v2.7 | Danny Depecker            |
| 2.8    | 26/05/2026 | §13 Code documentatie toegevoegd: twee niveaus, wanneer verplicht, JSDoc-structuur, referentiedoc-structuur, referentie-implementatie | Danny Depecker + Claude-P |
