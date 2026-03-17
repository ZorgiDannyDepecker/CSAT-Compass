---
applyTo: '**/*'
---

# CSAT-Compass - Copilot Instructions

**Versie:** 2.0  
**Laatst bijgewerkt:** 17/03/2026

**Doel:** GHC-gedragsinstructies en CSAT-projectcontext voor de CSAT-Compass repository  
**Type:** Reference  
**Auteur:** Danny Depecker + Claude  
**Status:** Approved

**Bestandsnaam:** copilot-instructions.md  
**Path:** .github/

> Generieke ZORGI PHARMA-conventies: `.github/instructions/project-conventies.instructions.md`  
> Opmaakregels: `.github/docs/md-style-guide.md`

---

## Number Formatting

When displaying numbers in Dutch text and documentation:

- **Thousands separator:** Use a **dot (.)** to separate thousands
  - ✅ Correct: 1.000, 10.000, 135.687, 1.234.567
  - ❌ Incorrect: 1,000, 10,000, 135,687, 1,234,567
- **Decimal separator:** Use a **comma (,)** for decimals
  - ✅ Correct: 3,14 | 12,5 | 99,99
  - ❌ Incorrect: 3.14 | 12.5 | 99.99
- **Examples in context:**
  - "De analyse bevat 75.224 tickets"
  - "Klanttevredenheid verbeterde met 7,7%"
  - "Gemiddelde afhandelingstijd: 43,5 minuten"

---

## Project Context

## User Information

- **Name:** Danny Depecker
- **Role:** Senior Advisor
- **Company:** ZORGI
- **Department:** PHARMA

## User Role Details

The user is a Senior Advisor at a company that develops hospital software. Their department/pillar is responsible for hospital pharmacy applications. They work on strategic projects, architecture decisions, and technical guidance for the pharmacy software team.

## Workspace Purpose

This project focuses on automated Customer Satisfaction (CSAT) analysis for ZORGI's hospital pharmacy clients. The goal is to process monthly ticketing data (project SD30) from Belgian hospitals using Python (pandas, matplotlib), generate structured markdown reports, and produce data visualizations. Results are reported to senior leadership (CEO, COO) and discussed within the PHARMA team. ZORGI operates bilingually (Dutch/French) — all CSAT output is always delivered in both languages.

## Project: CSAT-Compass

- **Project:** CSAT-Compass - Customer Satisfaction Analyse & Rapportage
- **Manager:** Danny Depecker
- **Team:** Tom De Laere, Wilfried Mertens, Frédéric Robinet, Thomas Desmet
- **Data source:** Maandelijkse ticketing exports (project SD30) van Belgische ziekenhuizen
- **Stack:** Python, pandas, matplotlib, Markdown
- **Output:** Maandelijkse markdown-rapporten + visualisaties — altijd twee bestanden: `rapport-YYYY-MM-nl.md` (Nederlands) + `rapport-YYYY-MM-fr.md` (Frans)
- **Rapportage:** Senior leadership (CEO Eric, COO Christian) + intern PHARMA-team
- **Status:** Actief — AI-gedreven CSAT-automatisering in ontwikkeling

## Projectspecifieke Afkortingen

- **CSAT** = Customer Satisfaction (klanttevredenheidsanalyse)
- **SD30** = ZORGI ticketing project (databron voor CSAT)

## Evolutie-template

Voor maandelijkse CSAT-vergelijkingen wordt een **evolutie-prompt** gebruikt die:

- de **2025-baseline** (referentiejaar) vergelijkt met
- de **cumulatieve 2026-data** (lopend jaar)
- trends, uitschieters en verbeterpunten benoemt per ziekenhuis/categorie

When the user asks for a CSAT prompt or analysis, always apply the CREATE or CARE framework (see project-conventies) and suggest which one fits best if not specified.

## Tweetaligheid (NL/FR)

ZORGI is een tweetalige organisatie (Nederlands/Frans). Alle CSAT-output wordt altijd in
beide landstalen gedeeld met stakeholders.

### Gedragsregels voor GHC

- **Rapporten:** Altijd twee afzonderlijke bestanden genereren per rapportageperiode
  - `rapport-YYYY-MM-nl.md` — Nederlandstalige versie (primair)
  - `rapport-YYYY-MM-fr.md` — Franstalige vertaling (gegenereerd door GHC)
- **Taal van de vertaling:** Professioneel zakelijk Frans, afgestemd op een ziekenhuisomgeving
- **Volgorde:** Eerst NL volledig afwerken, daarna FR genereren als volledige vertaling
- **Consistentie:** Cijfers, tabellen en visualisatietitels identiek in beide versies
- **Documentheader:** Beide bestanden krijgen een volledige header — enkel de taal verschilt
- **Waarschuwing:** Als GHC een rapport genereert in slechts één taal, moet hij expliciet
  aangeven dat de tweede taalversie nog ontbreekt

### Bestandsnaamconventie rapporten

| Versie     | Patroon                 | Voorbeeld               |
| ---------- | ----------------------- | ----------------------- |
| Nederlands | `rapport-YYYY-MM-nl.md` | `rapport-2026-03-nl.md` |
| Frans      | `rapport-YYYY-MM-fr.md` | `rapport-2026-03-fr.md` |

---

## Documentation Structure (3-Layer)

The `/docs/` folder follows a 3-layer structure:

1. **Strategisch (WAAROM)** - `docs/01-strategisch/`: High-level planning and architecture
   - `projectplan-highlevel.md` - Project overview and roadmap
   - `architectuur-beslissingen.md` - Architecture Decision Records (ADRs)
2. **Tactisch (HOE)** - `docs/02-tactisch/`: Implementation guides and phase documentation
   - `implementatie-gids.md` - Implementation guide index
   - `fasen/` - Detailed phase documentation (fase1-data-analyse.md, fase2-automatisering.md, enz.)
3. **Operationeel (DAGELIJKS)** - `docs/03-operationeel/`: Daily operations and troubleshooting
   - `operations-runbook.md` - Operational procedures
   - `troubleshooting-guide.md` - Common issues and solutions
   - `tools/` - Tool-specific documentation

---

## User Interaction Preferences

## Automatic Monitoring

- **DO NOT** automatically monitor or trace progress of background processes unless explicitly asked
- **DO NOT** ask "wil je dat ik de voortgang monitor?" or similar questions
- **DO NOT** use `Start-Sleep` or wait commands to check progress automatically
- Only check status when the user explicitly requests it
- Provide the process ID or relevant information so the user can check manually if needed

## Terminal Command Efficiency

- **Combine multiple commands** into a single terminal call whenever possible to minimize the number of "Continue" confirmations
- Group related operations together (e.g., multiple file moves, multiple git operations)
- Use PowerShell command chaining with `;` or `&&` where appropriate
- Only split into separate calls when commands have dependencies on previous results
- **DO NOT** ask confirmation questions like "Zal ik...", "Wil je dat ik...", "Mag ik..." before executing actions
- Execute autonomously based on clear user requests without asking permission first

## Terminal Feedback

- **DO NOT** provide terminal feedback/confirmation after every action when the decision-making and results are already visible in the conversation
- Terminal output is only needed when:
  - Actual command output is required for next steps
  - User explicitly asks for verification
  - Debugging or troubleshooting is needed
- **Avoid** unnecessary "✅ Done", "🎯 Success", or summary messages in terminal when the action is self-evident
- The conversation itself serves as confirmation - no need for duplicate terminal confirmations
- **DO NOT** use show_content tool to display findings that are already presented in the conversation

## Git Operations

- **DO NOT** automatically commit, push, or perform git operations unless explicitly requested
- When files are modified, mention the changes but don't auto-commit
- Only use git commands when user specifically asks: "commit dit", "push naar remote", "git add", etc.
- Exception: User may enable auto-commit for a session by saying "git mag automatisch"
- Let the user decide when and how to commit their work
- **ALWAYS use `--no-pager`** flag for git log, diff, show commands to prevent pager issues
  - Example: `git --no-pager log --oneline -5`
  - Example: `git --no-pager diff`
  - Example: `git --no-pager show --stat`
  - Reason: Prevents user from getting stuck in less/more pager requiring 'q' to exit

## Advice vs Action Mode

- **When user asks for advice** ("advies?", "wat denk je?", "aanbeveling?", "wat raad je aan?"):
  - Provide analysis with multiple options (A, B, C)
  - **DO NOT** automatically execute any actions
  - **DO NOT** ask "Zal ik beginnen?" - just wait for user's choice
  - Wait for explicit confirmation: "doe optie A", "implementeer dit", "ga verder", etc.
- **When user gives direct instruction** ("test dit", "fix dit", "implementeer X", "start de test"):
  - Execute immediately without confirmation questions
  - Take autonomous action as requested
  - No "Zal ik beginnen?" or "Wil je dat ik..." confirmations needed

---

## Prompt Quality Analysis

Analyze every user question/instruction internally for clarity and completeness.

**Only when Duidelijkheid = Nee/Gedeeltelijk OR Volledigheid = Nee/Gedeeltelijk**, add this section at the END of your response:

---
**⚠️ Prompt kan verbeterd worden**

- **Duidelijkheid:** ✅ Ja / ⚠️ Gedeeltelijk / ❌ Nee
- **Volledigheid:** ✅ Ja / ⚠️ Gedeeltelijk / ❌ Nee  
- **Belangrijkheid:** 🔴 High / 🟡 Medium / 🟢 Low

**💡 Wat kan beter:**
[Concrete suggesties wat er ontbreekt of onduidelijk is]

**🔍 Verdieping opties:**

- Type **"Q"** voor gedetailleerde uitleg en voorbeelden.
- Type **"MCQ"** voor maximum 10 kritische/praktische multiple choice vragen (één per één) om je prompt te verbeteren.

---

---

## Security & Data Guidelines

## Security Rules (CRITICAL)

- **NEVER** commit credentials to Git (use environment variables or secure vaults)
- **NO** patient data (patiëntdata) in Git, logs, or documentation
- **NO** persoonlijk identificeerbare informatie (PII) van ziekenhuismedewerkers in outputbestanden
- **ALWAYS** work with anonymized or aggregated ticketing data in reports
- **TEST** data transformations on sample datasets before running on full exports

## Data Sources

- **Primaire bron:** Maandelijkse ticketing exports vanuit project SD30 (CSV/Excel formaat)
- **Referentieperiode:** 2025 als baseline, cumulatief 2026 als lopend jaar
- **Granulariteit:** Per ziekenhuis, per categorie, per maand
- **Opslag:** Lokale werkmap — geen ticketingdata in Git committen

## Repository Structure

Respect the following folder structure:

- `.github/` - GitHub configuration, instructions, docs, workflows
- `archive/` - Oude versies van documenten/code/scripts voor referentie
- `data/` - Lokale databestanden (uitgesloten van Git via .gitignore)
- `docs/` - Documentation (3-layer structure: 01-strategisch, 02-tactisch, 03-operationeel)
- `scripts/` - PowerShell hulpscripts
- `src/` - Python scripts (analyse, rapportage, visualisatie)
- `output/` - Gegenereerde rapporten en visualisaties (uitgesloten van Git)
- `tests/` - Unit tests en testdata
- `WIP/` - Work In Progress documenten en scripts (niet klaar voor productie)

---

## Platform & Localization

- The user works with a **Dutch-language version of Microsoft Windows**.
- Always assume that **all UI elements, menus, dialogs, and system messages** are displayed in **Dutch**.
- All instructions and step-by-step guidance must reference **Dutch Windows UI labels**,
  not English equivalents (e.g. *Instellingen*, *Bestandsverkenner*, *Taakbeheer*, *Deze pc*).
- Use the terminology as it appears in **Dutch Windows interfaces**.
- If UI labels differ between Windows versions, explicitly mention the variation while staying within the Dutch localization context.

## IDE Localization (PyCharm)

- The user works with **PyCharm in English**.
- All PyCharm-specific instructions must use **English UI labels** for menus, settings, dialogs, and actions
  (e.g. *File → Settings*, *Run → Debug*, *Tools → Python Console*, *Project Structure*).
- However, **explanations and descriptions** surrounding these UI elements must remain in **Dutch**.
- Example format: "Ga naar **File → Settings → Project → Python Interpreter** om je virtuele omgeving te configureren."

---

## File Search Preferences

When searching files, always exclude these directories by default:

- `.idea` (IDE configuration)
- `.github` (GitHub workflows and metadata)
- `.venv` (Python virtual environment)
- `.git` (Git version control)
- `node_modules` (Node.js dependencies)
- `__pycache__` (Python compiled bytecode)
- `data/` (ruwe ticketingdata — nooit indexeren of doorzoeken)
- `output/` (gegenereerde rapporten — alleen op expliciete vraag)

Only include these directories when explicitly requested by the user.

---

## Terminal Command Output Formatting

When showing terminal commands with expected output:

1. **Command block**: use ```powershell or```bash with clear **"Command om uit te voeren:"** header
2. **Output block**: use ```text with clear **"Verwachte terminal output:"** header
3. Always keep command and output blocks **separate** with different syntax specifications
4. Use PowerShell syntax for Windows commands (given user's shell is pwsh.exe)

---

## Custom Chat Commands

The following shortcuts can be typed in the chat to trigger a specific terminal action.
GitHub Copilot executes the command **immediately** — geen bevestigingsvraag, geen uitleg vooraf.

| Shortcut | Beschrijving                                                                        |
| -------- | ----------------------------------------------------------------------------------- |
| `/pdf`   | Batch conversie van alle .md bestanden in Convertiemap/IN → PDF in Convertiemap/OUT |

## /pdf

When the user types `/pdf` as the entire message, immediately run this command in the terminal:

```powershell
python "C:\Users\danndepe\Documents\AI\CSAT-Compass\src\md_to_pdf.py" --batch "C:\Users\danndepe\Documents\Convertiemap\IN" "C:\Users\danndepe\Documents\Convertiemap\OUT" -p -d
```

- Execute autonomously, no confirmation needed
- Show the terminal output to the user
- Report how many files were converted

---

## Versiehistorie

| Versie | Datum      | Wijzigingen                                                                                                                                                                        | Auteur                  |
| ------ | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| 1.0    | 01/01/2026 | Initiële versie                                                                                                                                                                    | Danny Depecker          |
| 2.0    | 17/03/2026 | Herstructurering: document header, frontmatter, versiehistorie; overlappen met project-conventies verwijderd; CSAT/SD30 afkortingen gecentraliseerd; src/ en /pdf pad gecorrigeerd | Danny Depecker + Claude |
| 2.1    | 17/03/2026 | Tweetaligheid NL/FR toegevoegd: gedragsregels GHC, bestandsnaamconventie rapporten                                                                                                 | Danny Depecker          |
