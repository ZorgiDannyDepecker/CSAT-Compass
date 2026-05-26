---
applyTo: 'none'
---

# ZORGI PHARMA - User Context Template  

**Versie:** 1.1
**Laatst bijgewerkt:** 26/05/2026

**Doel:** Persoonsgebonden context die elke gebruiker eenmalig invult in zijn eigen project-copilot-instructions.md
**Type:** Template (invullen per gebruiker, per project)
**Auteur:** Danny Depecker + Claude
**Status:** Approved
**Bestandsnaam:** user-context.template.md
**Path:** .github\

> **Gebruik:**
>
> 1. Kopieer de `## User Context` sectie hieronder
> 2. Plak ze in het eigen `copilot-instructions.md` van elk project
> 3. Vul alle `[PLACEHOLDER]` velden in
> 4. Herhaal per project waar je actief bent
>
> **Dit bestand zelf nooit bewerken** — het is een template, geen actief instructiebestand.
> Persoonsgebonden info hoort NIET in `copilot-base.instructions.md` of `persona-templates.md`.

---

## Architectuurprincipe  

```text
PHARMA-Conventions (gedeeld — persoonsONafhankelijk)
├── copilot-base.instructions.md   → Organisatie + gedrag + technische basis
├── persona-templates.md           → Domeinexpert per project (copy-paste blokken)
└── user-context.template.md       → DIT BESTAND — invulsjabloon per gebruiker

Project/.github/copilot-instructions.md (persoonlijk — per gebruiker)
├── ## Persona          ← uit persona-templates.md (project-override)
├── ## User Context     ← uit user-context.template.md (ingevuld)
└── ## Project Context  ← project-specifieke technische info
```

---

## Te kopiëren sectie — invullen per gebruiker en per project  

```markdown
## User Context

- **Name:** [Voornaam Achternaam]
- **Role:** [Functietitel — bv. Project Manager / Project Leader / Analyst]
- **Company:** ZORGI
- **Department:** PHARMA

### Role description

[Beschrijf in 1-2 zinnen wat jouw rol inhoudt binnen dit project.
Voorbeeld: "I work on strategic projects, architecture decisions, and
technical guidance for the pharmacy software team."]

### Active team members for this project

| Name | Role |
|---|---|
| [Naam 1] | [Rol 1] |
| [Naam 2] | [Rol 2] |
| [Naam 3] | [Rol 3] |

### Reporting line

- **Direct manager:** [Naam manager]
- **Reports to (for this project):** [Naam / functie van ontvanger rapporten]

### Local paths (this machine only)

> ⚠️ Lokale paden zijn machinegebonden — nooit committen naar Git.

- **Project root:** [bv. C:\Users\jouwgebruikersnaam\Documents\AI\ProjectNaam]
- **Convertiemap IN:** [bv. C:\Users\jouwgebruikersnaam\Documents\Convertiemap\IN]
- **Convertiemap OUT:** [bv. C:\Users\jouwgebruikersnaam\Documents\Convertiemap\OUT]

### Project-specific dates and milestones

| Mijlpaal | Datum |
|---|---|
| [bv. Go-live] | [DD/MM/YYYY] |
| [bv. Fase 1 afsluiting] | [DD/MM/YYYY] |

### Additional personal preferences (optional)

[Vul hier eventuele persoonlijke werkafspraken in die niet in de base staan.
Bv. voorkeurstaal voor commit messages, specifieke IDE-plugins, etc.]
```

---

## Ingevuld voorbeeld — Danny Depecker / Scripting  

> Dit voorbeeld toont hoe de sectie er uitziet NA het invullen.
> Gebruik dit als referentie bij het invullen van jouw eigen versie.

```markdown
## User Context

- **Name:** Danny Depecker
- **Role:** Senior Advisor
- **Company:** ZORGI
- **Department:** PHARMA

### Role description

I work on strategic projects, architecture decisions, and technical guidance
for the ZORGI PHARMA software team. I manage the Scriptorium tooling and
coordinate SQL script validation across DEV and PROD environments.

### Active team members for this project

| Name | Role |
|---|---|
| Thomas Desmet | Developer |
| Nick K. | Developer |

### Reporting line

- **Direct manager:** Tom De Laere
- **Reports to (for this project):** Tom De Laere

### Local paths (this machine only)

- **Project root:** C:\Users\danndepe\Documents\AI\Scripting
- **Convertiemap IN:** C:\Users\danndepe\Documents\Convertiemap\IN
- **Convertiemap OUT:** C:\Users\danndepe\Documents\Convertiemap\OUT

### Project-specific dates and milestones

| Mijlpaal | Datum |
|---|---|
| Fase 5 afsluiting | TBD |

### Additional personal preferences (optional)

- Commit messages altijd in het Engels
- Gebruik altijd `git --no-pager` voor log en diff commando's
```

---

## Versiehistorie  

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 26/03/2026 | Initiële versie — persoonsgebonden context gesplitst uit copilot-base | Danny Depecker + Claude |
| 1.1 | 26/05/2026 | MD032: blanco regel na blockquote toegevoegd; MD040: code block taal toegevoegd | Danny Depecker |
