---
description: "Generate a weekly progress summary for CSAT-Compass project"
name: "summarize-csat-week"
agent: "github-copilot"
---

# CSAT-Compass - Weekly Summary Generator

**Versie:** 1.0  
**Laatst bijgewerkt:** 17/03/2026

**Doel:** Gestructureerd wekelijks voortgangsrapport genereren voor het CSAT-Compass project  
**Type:** Guide  
**Auteur:** Danny Depecker + Claude  
**Status:** Approved

**Bestandsnaam:** summarize-week.md  
**Path:** .github/prompts/

---

## Timing & Frequentie

- **Wanneer:** Elke **maandagmorgen**
- **Periode:** Rapportage over de **vorige week** (maandag t/m zondag, 7 dagen)
- **Planning:** Inclusief planning voor de **huidige week** (deze maandag t/m zondag)

## Datum Berekening

- **Vandaag:** Huidige datum (maandag)
- **Rapportage periode:** Vorige maandag t/m vorige zondag (7 dagen terug)
- **Bestandsnaam datum:** Zondag van vorige week (YYYY-MM-DD formaat)

**Voorbeeld:**

```text
Als vandaag = maandag 16/03/2026:
├─ Rapportage periode = ma 09/03 t/m zo 15/03
└─ Bestandsnaam = week-2026-03-15.md
```

---

## Context

Analyseert voortgang van vorige week, lessons learned, en planning voor huidige week.
Het rapport wordt altijd **tweetalig** aangeleverd: Nederlands (primair) en Frans (vertaling door GHC).

## Doelgroepen

1. **Danny Depecker (Project Manager):** Voortgang tracking, beslissingen
2. **Senior Leadership (CEO Eric, COO Christian):** Status, risico's, tijdlijn
3. **PHARMA-team (Tom, Wilfried, Frédéric, Thomas):** Operationele voortgang
4. **Toekomstig team:** Historisch overzicht

---

## Bronnen

- `docs/01-strategisch/projectplan-highlevel.md` - Planning baseline
- `docs/01-strategisch/architectuur-beslissingen.md` - Strategische keuzes
- `docs/02-tactisch/implementatie-gids.md` - Technische voortgang
- `docs/03-operationeel/operations-runbook.md` - Dagelijkse uitvoering
- `docs/progression/week-*.md` - Vorige weekrapporten (voor trends)
- Git commit history - Concrete deliverables (indien beschikbaar)
- **Git diff voor markdown bestanden** - Documentatie wijzigingen tracking

---

## Markdown Documentatie Tracking

**Doel:** Wekelijks overzicht van wijzigingen in documentatie zodat de afgedrukte set actueel blijft.

**Scope:**

- **Inclusief:** Alle `.md` bestanden in `docs/` (recursief)
- **Exclusief:** `docs/archive/`, `WIP/`

**Git Commando's:**

```powershell
# Krijg zondag van vorige week
$lastSunday = (Get-Date).AddDays(-((Get-Date).DayOfWeek.value__ % 7) - 7)
$lastSundayStr = $lastSunday.ToString("yyyy-MM-dd")

# Git diff voor markdown bestanden sinds vorige zondag
git --no-pager diff --name-status HEAD@{$lastSundayStr} HEAD -- "docs/*.md" ":(exclude)docs/archive/" ":(exclude)WIP/"
```

**Output formaat:**

```text
A = Added    (nieuw bestand)
M = Modified (aangepast bestand)
D = Deleted  (verwijderd bestand)
R = Renamed  (hernoemd bestand)
```

**Sectie in weekrapport** — toevoegen aan DEEL 1: RETROSPECTIEF, na "Deliverables Status":

### 📄 Documentatie wijzigingen (afdruk update lijst)

**Nieuwe bestanden (A):**

- [ ] `docs/pad/naar/nieuw-bestand.md` - Korte beschrijving

**Aangepaste bestanden (M):**

- [ ] `docs/pad/naar/aangepast-bestand.md` - Wat er gewijzigd is

**Verwijderde bestanden (D):**

- [ ] `docs/pad/naar/verwijderd-bestand.md` - Reden van verwijdering

**Acties voor gebruiker:**

- ✅ Print nieuwe bestanden
- ✅ Print aangepaste bestanden (vervang oude versie)
- ✅ Verwijder verwijderde bestanden uit fysieke map

**Geen wijzigingen:** *Geen documentatie wijzigingen deze week — afgedrukte set is up-to-date* ✅

---

## Output Structuur

### DEEL 1: RETROSPECTIEF (vorige week)

1. Executive summary (voor management)
2. Tijdlijn vergelijking (gepland vs werkelijk)
3. Deliverables status (compleet / in uitvoering / pending)
4. 📄 Documentatie wijzigingen (afdruk update lijst)
5. Kritieke wijzigingen en beslissingen
6. Lessons learned (wat ging goed / wat kan beter)
7. Voortgang CSAT-analyse per ziekenhuis/categorie
8. Risico's & mitigaties

### DEEL 2: PLANNING (huidige week)

1. Planning huidige week (ma-vr, per dag indien mogelijk)
2. Focus areas & prioriteiten
3. Verwachte deliverables
4. Potentiële blockers

### DEEL 3: METRICS

1. Metrics dashboard (voortgang, velocity, openstaande items)

---

## Tweetaligheid

Het rapport wordt altijd in **twee afzonderlijke bestanden** aangeleverd:

| Versie    | Bestandsnaam            | Taal                         |
| --------- | ----------------------- | ---------------------------- |
| Primair   | `week-YYYY-MM-DD-nl.md` | Nederlands                   |
| Vertaling | `week-YYYY-MM-DD-fr.md` | Frans (gegenereerd door GHC) |

**Volgorde:** Eerst NL volledig afwerken, daarna FR genereren als volledige vertaling.  
**Stijl FR:** Professioneel zakelijk Frans, afgestemd op ziekenhuisomgeving.

---

## Bestandsnamen en Pad

**Pad:** `docs/progression/`

**Patroon:** `week-YYYY-MM-DD-[taal].md`  
waarbij `YYYY-MM-DD` = zondag van de **vorige week**

**Voorbeelden:**

- Maandag 16/03/2026 → `week-2026-03-15-nl.md` + `week-2026-03-15-fr.md`
- Maandag 23/03/2026 → `week-2026-03-22-nl.md` + `week-2026-03-22-fr.md`

---

## Toon in Rapportage

- **Retrospectief deel:** Verleden tijd (wat is er gebeurd, wat hebben we geleerd)
- **Planning deel:** Toekomende tijd (wat gaan we doen, wat verwachten we)
- **Metrics:** Tegenwoordige tijd (huidige status)

---

## Versiehistorie

| Versie | Datum      | Wijzigingen                                                                                                                                | Auteur |
| ------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------ |
| 1.0    | 17/03/2026 | Aangepast vanuit Scriptorium summarize-week.md naar CSAT-Compass; tweetaligheid NL/FR toegevoegd; bronnen, doelgroepen en paden bijgewerkt | Claude |
