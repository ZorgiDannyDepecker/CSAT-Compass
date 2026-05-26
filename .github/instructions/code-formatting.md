---
applyTo: '**/*.py,**/*.ps1,**/*.sql,**/*.js,**/*.html'
---

# ZORGI PHARMA - Code Formatting Instructions  

**Versie:** 2.1
**Laatst bijgewerkt:** 26/05/2026

**Doel:** GHC-instructies voor consistente code block opmaak en code documentatie in alle ZORGI PHARMA-projecten
**Type:** Reference
**Auteur:** Danny Depecker + Claude-P
**Status:** Approved
**Bestandsnaam:** code-formatting.md
**Path:** conventions\instructions\

---

## Inhoudsopgave  

1. [Code block specificaties](#1-code-block-specificaties)
2. [Commentaren en docstrings](#2-commentaren-en-docstrings)
3. [JSDoc voor JavaScript](#3-jsdoc-voor-javascript)
4. [Referentiedocument](#4-referentiedocument)

---

## 1. Code block specificaties  

Wanneer code bestanden worden aangeleverd voor aanpassing of review, altijd dit strikte formaat gebruiken:

1. **Taalspecificatie:** Altijd `bash` als taalcode gebruiken, ongeacht de werkelijke programmeertaal.
   > Reden: garandeert consistente rendering en syntaxiskleuring onafhankelijk van het bestandstype.

2. **Eerste regel — bestandspad:**
   - Begin met een hekje (`#`)
   - Gevolgd door exact één spatie
   - Dan het volledige **absolute** pad inclusief bestandsnaam, zonder leading slash
   - Voorbeeld: `# C:\Users\danndepe\Documents\AI\CSAT-Compass\src\analyse.py`

3. **Tweede regel:** Altijd volledig leeg (blanco regel).

4. **Vanaf regel 3:** De volledige, uitvoerbare code zonder verdere commentaren of uitleg binnen het code block.

5. **Volledigheid:** Altijd de volledige, uitvoerbare code tonen — geen omissies, geen plaatshoudercommentaren zoals:
   - `# ... rest of the code`
   - `# other methods here`
   - `# TODO: implement`

---

## 2. Commentaren en docstrings  

- Alle inline commentaren in code bestanden in **Nederlands**
- Alle docstrings (Python `"""..."""`) in **Nederlands**
- Voorbeeld correct inline commentaar: `# Berekening van het maandgemiddelde`
- Voorbeeld incorrect inline commentaar: `# Calculate the monthly average`

---

## 3. JSDoc voor JavaScript  

### 3.1 Wanneer verplicht  

JSDoc-commentaar is verplicht voor:

- Alle JavaScript-functies (ook korte hulpfuncties)
- Alle IIFE's (Immediately Invoked Function Expressions) met meer dan één statement
- Complexe gebeurtenisluisteraars met niet-triviale logica

JSDoc is **niet** vereist voor:

- Enkelvoudige inline event handlers in HTML (`onclick="clearEditor()"`)
- Triviale één-regel variabeledeclaraties

### 3.2 Verplichte structuur  

```text
/**
 * Korte beschrijving van wat de functie doet (één zin, Nederlands).
 * Uitgebreidere toelichting indien nodig (optioneel, tweede alinea).
 *
 * @param  {type}    naam  - Beschrijving van de parameter
 * @returns {type}          - Beschrijving van de returnwaarde (weglaten indien void)
 * @note   Bijzondere opmerking over gedrag, beperkingen of afhankelijkheden (optioneel)
 */
```

### 3.3 Ondersteunde tags  

| Tag | Gebruik | Verplicht |
| --- | --- | --- |
| `@param {type} naam` | Parameter beschrijving | Ja, bij elke parameter |
| `@returns {type}` | Returnwaarde beschrijving | Ja, tenzij `void` |
| `@note` | Bijzondere opmerking | Nee, enkel bij relevante uitzonderingen |

### 3.4 Typering  

Gebruik JavaScript-typenamen in lowercase:

| Type | Schrijfwijze |
| --- | --- |
| Tekst | `{string}` |
| Getal | `{number}` |
| Boolean | `{boolean}` |
| DOM-element | `{HTMLElement}` |
| Bestandsobject | `{File}` |
| Muisgebeurtenis | `{MouseEvent}` |
| Toetsenbordgebeurtenis | `{KeyboardEvent}` |
| Geen returnwaarde | *(tag weglaten)* |

### 3.5 Taal  

- De **beschrijving** (eerste regel en toelichting) in **Nederlands**
- De **parameternamen** (`naam`) in **Engels** — consistent met de code zelf
- De **parameterbeschrijvingen** in **Nederlands**

### 3.6 Sectiecommentaar in CSS  

CSS-blokken worden gegroepeerd met sectiecommentaar:

```css
/* --- Sectienaam --- */
```

Elke logische CSS-groep krijgt een eigen sectiecommentaar direct erboven.

### 3.7 Sectiecommentaar in HTML  

Grote HTML-secties (header, toolbar, werkruimte) krijgen een blokcommentaar:

```html
<!-- ============================================================
     SECTIENAAM
     Korte beschrijving van de inhoud van deze sectie.
     ============================================================ -->
```

---

## 4. Referentiedocument  

### 4.1 Wanneer een apart referentiedoc  

Een apart referentiedocument (`docs/02-tactisch/code-documentatie.md`) is vereist wanneer:

- Het bestand JavaScript-logica bevat die niet triviaal is
- De codebase functies bevat die door anderen hergebruikt of aangepast worden
- Het project de ZORGI PHARMA-professionaliseringsstandaard volgt

### 4.2 Relatie tussen inline JSDoc en referentiedoc  

| | Inline JSDoc | Referentiedoc |
| --- | --- | --- |
| **Locatie** | In de broncode | `docs/02-tactisch/code-documentatie.md` |
| **Doelgroep** | Developer die de code bewerkt | Developer die functionaliteit opzoekt zonder de code te openen |
| **Onderhoud** | Bij elke codewijziging | Bij elke codewijziging |
| **Gegenereerd** | Nee — handmatig | Nee — handmatig |

> ⚠️ Bij wijzigingen aan de code **altijd** beide bijwerken.  
> De twee documenten verwijzen naar elkaar voor traceerbaarheid.

### 4.3 Referentie-implementatie  

MD-Converter (`src/md-converter.html` + `docs/02-tactisch/code-documentatie.md`)  
is de referentie-implementatie voor deze aanpak binnen ZORGI PHARMA.

---

## Versiehistorie  

| Versie | Datum | Wijzigingen | Auteur |
| --- | --- | --- | --- |
| 1.0 | 01/01/2026 | Initiële versie | GHC |
| 2.0 | 17/03/2026 | Document header toegevoegd; applyTo beperkt tot code-extensies; absoluut pad voorbeeld; rationale bash; docstrings toegevoegd | Danny Depecker + Claude |
| 2.1 | 26/05/2026 | Inhoudsopgave toegevoegd; §3 JSDoc voor JavaScript toegevoegd; §4 Referentiedocument toegevoegd; applyTo uitgebreid met .js en .html; auteur bijgewerkt naar Claude-P | Danny Depecker + Claude-P |
