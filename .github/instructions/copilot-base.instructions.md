---
applyTo: '**/*'
---

# ZORGI PHARMA - Copilot Base Instructions

**Versie:** 1.1
**Laatst bijgewerkt:** 25/03/2026

**Doel:** Gedeelde GHC-basisinstructies voor alle ZORGI PHARMA-projecten
**Type:** Reference
**Auteur:** Danny Depecker
**Status:** Approved

**Bestandsnaam:** copilot-base.instructions.md
**Path:** pharma/

> **Golden source:** Dit bestand wordt beheerd in `PHARMA-Conventions\pharma\`.
> Samengesteld vanuit: Q&A-Lab + Scripting + CSAT-Compass copilot-instructions.md
> Analyse: `WIP/copilot-analyse-gemeenschappelijk.md` + `WIP/copilot-analyse-afwijkingen.md`
>
> **Projectspecifieke instructies** blijven in het eigen `copilot-instructions.md` per project.
> Dit bestand bevat uitsluitend de gedeelde basis.

---

## Language Preference

Respond always in Dutch (Nederlands), regardless of the input language used in questions or code comments.

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
  - "De database bevat 75.224 records"
  - "Performance verbeterde met 7,7%"
  - "Totale bestandsgrootte: 43,5 MB"

---

## User Information

- **Name:** Danny Depecker
- **Role:** Senior Advisor
- **Company:** ZORGI
- **Department:** PHARMA

## User Role Details

The user is a Senior Advisor at a company that develops hospital software. Their department/pillar is responsible for hospital pharmacy applications. They work on strategic projects, architecture decisions, and technical guidance for the pharmacy software team.

---

## Abbreviations

- **GHC** = GitHub Copilot
- **PC2025** = PyCharm 2025.3

---

## User Interaction Preferences

### Automatic Monitoring

- **DO NOT** automatically monitor or trace progress of background processes unless explicitly asked
- **DO NOT** ask "wil je dat ik de voortgang monitor?" or similar questions
- **DO NOT** use `Start-Sleep` or wait commands to check progress automatically
- Only check status when the user explicitly requests it
- Provide the process ID or relevant information so the user can check manually if needed

### Terminal Command Efficiency

- **Combine multiple commands** into a single terminal call whenever possible to minimize the number of "Continue" confirmations
- Group related operations together (e.g., multiple file moves, multiple git operations)
- Use PowerShell command chaining with `;` or `&&` where appropriate
- Only split into separate calls when commands have dependencies on previous results
- **DO NOT** ask confirmation questions like "Zal ik...", "Wil je dat ik...", "Mag ik..." before executing actions
- Execute autonomously based on clear user requests without asking permission first

### Terminal Feedback

- **DO NOT** provide terminal feedback/confirmation after every action when the decision-making and results are already visible in the conversation
- Terminal output is only needed when:
  - Actual command output is required for next steps
  - User explicitly asks for verification
  - Debugging or troubleshooting is needed
- **Avoid** unnecessary "✅ Done", "🎯 Success", or summary messages in terminal when the action is self-evident
- The conversation itself serves as confirmation - no need for duplicate terminal confirmations
- **DO NOT** use show_content tool to display findings that are already presented in the conversation

### Git Operations

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

### Advice vs Action Mode

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

## Security Rules (CRITICAL)

- **NEVER** commit credentials to Git (use environment variables or secure vaults)
- **NO** patient data (patiëntdata) in Git, logs, or documentation
- **NO** persoonlijk identificeerbare informatie (PII) in outputbestanden
- **TEST** queries and data transformations on sample/dev data before running on full exports

---

## Code Style

- Use clear, descriptive variable and method names in English
- Add comprehensive logging for debugging purposes
- Follow Python PEP 8 conventions
- Use type hints where applicable

---

## Documentation

- Code comments in Dutch
- Docstrings (Python `"""..."""`) in Dutch
- README and technical documentation in Dutch
- Follow `pharma/md-style-guide.md` for all Markdown formatting
- Follow `pharma/code-formatting.md` for all code block formatting

---

## Platform & Localization

- The user works with a **Dutch-language version of Microsoft Windows**
- Always assume that **all UI elements, menus, dialogs, and system messages** are displayed in **Dutch**
- All instructions must reference **Dutch Windows UI labels**
  (e.g. *Instellingen*, *Bestandsverkenner*, *Taakbeheer*, *Deze pc*)

### IDE Localization (PyCharm)

- The user works with **PyCharm in English**
- All PyCharm-specific instructions must use **English UI labels**
  (e.g. *File → Settings*, *Run → Debug*, *Tools → Python Console*)
- **Explanations** surrounding these UI elements remain in **Dutch**
- Example: "Ga naar **File → Settings → Project → Python Interpreter** om je virtuele omgeving te configureren."

---

## File Search Preferences

When searching files, always exclude these directories by default:

- `.idea` (IDE configuration)
- `.github` (GitHub workflows and metadata)
- `.venv` (Python virtual environment)
- `.git` (Git version control)
- `node_modules` (Node.js dependencies)
- `__pycache__` (Python compiled bytecode)

Only include these directories when explicitly requested by the user.

---

## Terminal Command Output Formatting

When showing terminal commands with expected output:

1. **Command block:** use ```powershell or```bash with clear **"Command om uit te voeren:"** header
2. **Output block:** use ```text with clear **"Verwachte terminal output:"** header
3. Always keep command and output blocks **separate** with different syntax specifications
4. Use PowerShell syntax for Windows commands (given user's shell is pwsh.exe)

---

## Versiehistorie Formatting

When adding entries to version history tables in documentation:

- **DO NOT** use bold formatting (`**text**`) for new version entries
- Use regular text for all table cells (version number, date, changes, author)
- Example correct: `| 1.0 | 24/03/2026 | Initiële versie | Danny Depecker |`
- Example incorrect: `| **1.0** | **24/03/2026** | **Initiële versie** | **Danny Depecker** |`

---

## Custom Chat Commands

The following shortcuts trigger a specific action immediately — geen bevestigingsvraag, geen uitleg vooraf.

> **Architectuurprincipe:** Alleen `/advies` is generiek genoeg voor de base.
> Alle overige commands zijn project-specifiek en worden gedefinieerd
> in het eigen `copilot-instructions.md` van elk project.

| Commando | Beschrijving | Waar gedefinieerd |
|---|---|---|
| `/advies` | Gestructureerd advies met MCQ-begeleiding | ✅ Base (hier) |
| `/pdf` | Batch conversie .md → PDF via Convertiemap | Project-specifiek |
| `/email` | Email → Markdown conversie | Project-specifiek |
| `/GIT` | Stage + commit message genereren + committen | Project-specifiek |
| `/cve` | CVE-scan geïnstalleerde packages | Project-specifiek |
| `/smd` | Schema Monitor Diagnose | Project-specifiek (Scripting) |

---

## /advies

When the user types `/advies` as the entire message (optionally followed by a topic or question),
respond using this exact approach:

Geef advies, bedenkingen en voorstellen over het gevraagde onderwerp.
Indien bijkomende informatie nodig is, stel vragen via maximaal 10 alfanumerieke MCQ-vragen,
waarbij telkens de beste numerieke optie expliciet als **(advies)** wordt vooropgesteld.

- Provide concrete advice, considerations and proposals
- Ask MCQ questions **one by one** — not all at once
- Always mark the recommended option explicitly with **(advies)**
- Maximum 10 MCQ questions total

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 24/03/2026 | Initiële versie — samengesteld vanuit Q&A-Lab + Scripting + CSAT-Compass | Danny Depecker |
| 1.1 | 25/03/2026 | Architectuurrefactor: /pdf, /GIT, /cve, /smd verwijderd uit base — enkel /advies behouden; command-tabel herwerkt naar project-specifiek principe | Danny Depecker |
