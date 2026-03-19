---
applyTo: '**/*'
---

# ZORGI PHARMA - Markdown Style — GHC Instructies

**Versie:** 1.1  
**Laatst bijgewerkt:** 19/03/2026

**Doel:** Compacte GHC-instructies afgeleid van md-style-guide.md  
**Type:** Reference  
**Auteur:** Danny Depecker + Claude  
**Status:** Approved

**Bestandsnaam:** md-style-guide.instructions.md  
**Path:** .github/instructions/

> Volledig referentiedocument: `.github/docs/md-style-guide.md`

---

## Document Header

Every markdown document MUST start with this exact header structure:

```markdown
# [Project] - [Document Titel]

**Versie:** [X.Y]  
**Laatst bijgewerkt:** [DD/MM/YYYY]

**Doel:** [Korte beschrijving — 1 zin]  
**Type:** [zie toegestane waarden hieronder]  
**Auteur:** [zie toegestane waarden hieronder]  
**Status:** [zie toegestane waarden hieronder]

**Bestandsnaam:** [filename.md]  
**Path:** [relatief/pad/]

---
```

All fields are REQUIRED. Use `NVT` or `TBD` if no value is available.

> ⚠️ **Trailing spaces:** Every header field line MUST end with **two spaces** (2× spatie)
> before the line break — otherwise markdown viewers render all fields on one line.
>
> ✅ Correct: `**Versie:** 1.0` (two trailing spaces)
> ❌ Incorrect: `**Versie:** 1.0` (no trailing spaces)

**Type — toegestane waarden:**
`Implementatie` | `ADR` | `Runbook` | `Reference` | `Guide` | `Planning` | `Retrospective` | `Convention`

**Auteur — toegestane waarden:**

| Situatie           | Waarde                    |
| ------------------ | ------------------------- |
| Menselijke auteur  | `Danny Depecker`          |
| GitHub Copilot     | `GHC`                     |
| Claude (Anthropic) | `Claude`                  |
| Gemini (Google)    | `Gemini`                  |
| Mens + GHC         | `Danny Depecker + GHC`    |
| Mens + Claude      | `Danny Depecker + Claude` |
| Meerdere AI        | `GHC + Claude`            |

**Status — toegestane waarden:**
`Draft` | `In Review` | `In Progress` | `Approved` | `Compleet` | `Gepland` | `Deprecated` | `Archived`

---

## Datumnotatie

| Context                      | Formaat      | Voorbeeld                       |
| ---------------------------- | ------------ | ------------------------------- |
| In tekst en document headers | `DD/MM/YYYY` | `17/03/2026`                    |
| In bestandsnamen             | `YYYY-MM-DD` | `2026-03-17-meeting-notes.md`   |
| In archief-bestandsnamen     | `YYYYMMDD`   | `gids-ARCHIEF-v3.0-20260317.md` |

---

## Headers

- H1: uitsluitend voor de document titel (1× per document)
- H2: hoofdsecties — nummeren (1, 2, 3...)
- H3: subsecties — nummeren (1.1, 1.2...)
- NOOIT levels overslaan (H1 → H3 is fout)
- **Hoofdletter:** alleen het eerste woord — eigennamen en afkortingen uitgezonderd
  - ✅ `## Algemene richtlijnen`
  - ✅ `## DBHub configuratie`
  - ❌ `## Algemene Richtlijnen`

---

## Lijsten

- Ongeordende lijsten: ALTIJD `-` als bullet — nooit `*` of `+`
- Geordende lijsten: nummering start bij `1`
- Maximale diepte: 3 niveaus

---

## Admonitions

Use emoji as visual anchors — consistent across all documents:

| Emoji | Betekenis             |
| ----- | --------------------- |
| ⚠️    | Risico / Waarschuwing |
| ✅     | Voltooid / Correct    |
| ❌     | Fout / Incorrect      |
| 🚀     | Release / Go-live     |
| 💡     | Idee / Tip            |
| 🎯     | Focus / Doel          |
| 🔍     | Analyse / Onderzoek   |
| 🔄     | In progress           |
| ⏳     | Gepland               |
| 📋     | Checklist / Overzicht |

---

## Versiehistorie — verplicht template

Every document MUST end with a version history table:

```markdown
## Versiehistorie

| Versie | Datum      | Wijzigingen     | Auteur         |
| ------ | ---------- | --------------- | -------------- |
| 1.0    | 17/03/2026 | Initiële versie | Danny Depecker |
```

**Opmaakregels:**

- NEVER use bold formatting (`**text**`) in version history table cells
- Plain text only in all cells

---

## Bestandsnamen

- Kebab-case: altijd lowercase met hyphens
  - ✅ `fase1-data-analyse.md`
  - ❌ `Fase1_Data_Analyse.md`
- Meta-bestanden: UPPERCASE (`README.md`, `CHANGELOG.md`)
- Archieven: `[naam]-ARCHIEF-v[X.Y]-[YYYYMMDD].md`

---

## Mermaid

- Use `mermaid` code block tag for all diagrams
- Always include a descriptive `title`
- Add a short description ABOVE the code block
- Preferred diagram types:

| Situatie                | Type              |
| ----------------------- | ----------------- |
| Projectplanning         | `gantt`           |
| Procesflow / beslisboom | `graph TD`        |
| Systeeminteracties      | `sequenceDiagram` |
| Databaseschema          | `erDiagram`       |
| Statusovergangen        | `stateDiagram-v2` |

---

## Versiehistorie

| Versie | Datum      | Wijzigingen                        | Auteur                  |
| ------ | ---------- | ---------------------------------- | ----------------------- |
| 0.1    | 17/03/2026 | Placeholder aangemaakt             | Claude                  |
| 1.0    | 17/03/2026 | Volledige GHC-instructies ingevuld | Danny Depecker + Claude |
| 1.1    | 19/03/2026 | MD038 fix: code span met spaties vervangen door leesbare notatie | Danny Depecker + GHC |
