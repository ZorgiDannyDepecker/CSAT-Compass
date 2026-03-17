---
applyTo: '**/*.py,**/*.ps1,**/*.sql'
---

# ZORGI PHARMA - Code Formatting Instructions

**Versie:** 2.0  
**Laatst bijgewerkt:** 17/03/2026

**Doel:** GHC-instructies voor consistente code block opmaak in alle ZORGI PHARMA-projecten  
**Type:** Reference  
**Auteur:** Danny Depecker + Claude  
**Status:** Approved

**Bestandsnaam:** code-formatting.instructions.md  
**Path:** .github/instructions/

---

## Code Block Specifications

When providing code files for modification or review, always use the following strict format:

1. **Language specification:** Always use `bash` as the language for the code block, regardless of the actual programming language.
   > Reason: ensures consistent rendering and syntax highlighting independent of file type.

2. **First line — file path:**
   - Start with a hash symbol (`#`)
   - Followed by exactly one space
   - Then the complete **absolute** path including filename, without a leading slash
   - Example: `# C:\Users\danndepe\Documents\AI\CSAT-Compass\src\analyse.py`

3. **Second line:** Always completely empty (blank line).

4. **From line 3 onwards:** The complete, modified code without any further comments or explanations within the code block.

5. **Completeness:** Always show the complete, executable code — no omissions, no placeholder comments such as:
   - `# ... rest of the code`
   - `# other methods here`
   - `# TODO: implement`

6. **Comments and docstrings:**
   - All inline comments in code files must be written in **Dutch**
   - All docstrings (Python `"""..."""`) must be written in **Dutch**
   - Example of correct inline comment: `# Berekening van het maandgemiddelde`
   - Example of incorrect inline comment: `# Calculate the monthly average`

---

## Versiehistorie

| Versie | Datum      | Wijzigingen                                                                                                                                                        | Auteur                  |
| ------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| 1.0    | 01/01/2026 | Initiële versie                                                                                                                                                    | GHC                     |
| 2.0    | 17/03/2026 | Document header toegevoegd; applyTo beperkt tot code-extensies; absoluut pad voorbeeld; rationale bash; docstrings toegevoegd; versiehistorie sectiekop toegevoegd | Danny Depecker + Claude |
