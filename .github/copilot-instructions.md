---
applyTo: '**/*'
---

# CSAT-Compass - Copilot Instructions

**Versie:** 3.0
**Laatst bijgewerkt:** 24/03/2026

**Doel:** CSAT-Compass projectspecifieke GHC-instructies
**Type:** Reference
**Auteur:** Danny Depecker + Claude
**Status:** Approved

**Bestandsnaam:** copilot-instructions.md
**Path:** .github/

> **Gedeelde basisinstructies:** `.github/instructions/copilot-base.instructions.md`
> Dit bestand bevat uitsluitend de CSAT-Compass specifieke aanvullingen.
> Alle algemene ZORGI PHARMA-instructies (taal, interactie, code, platform,
> custom commands) staan in het basisbestand en gelden onverkort voor dit project.
>
> Branding & Design System: `.github/docs/zorgi_design_system.md`
> Generieke conventies: `.github/instructions/project-conventies.md`

---

## Project Context

### Workspace Purpose

This project focuses on automated Customer Satisfaction (CSAT) analysis for ZORGI's hospital
pharmacy clients. The goal is to process monthly ticketing data (project SD30) from Belgian
hospitals using Python (pandas, matplotlib), generate structured markdown reports, and produce
data visualizations. Results are reported to senior leadership (CEO, COO) and discussed within
the PHARMA team. ZORGI operates bilingually (Dutch/French) — all CSAT output is always
delivered in both languages.

### Project: CSAT-Compass

- **Project:** CSAT-Compass - Customer Satisfaction Analyse & Rapportage
- **Manager:** Danny Depecker
- **Team:** Tom De Laere, Wilfried Mertens, Frédéric Robinet, Thomas Desmet
- **Data source:** Maandelijkse ticketing exports (project SD30) van Belgische ziekenhuizen
- **Stack:** Python, pandas, matplotlib, Markdown
- **Output:** `rapport-YYYY-MM-nl.md` (Nederlands) + `rapport-YYYY-MM-fr.md` (Frans)
- **Rapportage:** Senior leadership (CEO Eric, COO Christian) + intern PHARMA-team
- **Status:** Actief — AI-gedreven CSAT-automatisering in ontwikkeling

### Projectspecifieke afkortingen

- **CSAT** = Customer Satisfaction (klanttevredenheidsanalyse)
- **SD30** = ZORGI ticketing project (databron voor CSAT)

### Evolutie-template

Voor maandelijkse CSAT-vergelijkingen wordt een **evolutie-prompt** gebruikt die:

- de **2025-baseline** (referentiejaar) vergelijkt met
- de **cumulatieve 2026-data** (lopend jaar)
- trends, uitschieters en verbeterpunten benoemt per ziekenhuis/categorie

When the user asks for a CSAT prompt or analysis, always apply the CREATE or CARE framework
(see project-conventies) and suggest which one fits best if not specified.

---

## Tweetaligheid (NL/FR)

ZORGI is een tweetalige organisatie. Alle CSAT-output wordt altijd in beide talen gedeeld.

- **Rapporten:** Altijd twee bestanden per rapportageperiode
  - `rapport-YYYY-MM-nl.md` — Nederlandstalige versie (primair)
  - `rapport-YYYY-MM-fr.md` — Franstalige vertaling
- **Vertaaltaal:** Professioneel zakelijk Frans, afgestemd op ziekenhuisomgeving
- **Volgorde:** Eerst NL volledig afwerken, daarna FR genereren
- **Consistentie:** Cijfers, tabellen en visualisatietitels identiek in beide versies
- **Waarschuwing:** Als GHC slechts één taalversie genereert, dit expliciet vermelden

| Versie | Patroon | Voorbeeld |
|---|---|---|
| Nederlands | `rapport-YYYY-MM-nl.md` | `rapport-2026-03-nl.md` |
| Frans | `rapport-YYYY-MM-fr.md` | `rapport-2026-03-fr.md` |

---

## Documentation Structure (3-Layer)

The `/docs/` folder follows a 3-layer structure:

1. **Strategisch (WAAROM)** - `docs/01-strategisch/`
   - `projectplan-highlevel.md` - Project overview and roadmap
   - `architectuur-beslissingen.md` - Architecture Decision Records (ADRs)
2. **Tactisch (HOE)** - `docs/02-tactisch/`
   - `implementatie-gids.md` - Implementation guide index
   - `fasen/` - fase1-data-analyse.md, fase2-automatisering.md, enz.
3. **Operationeel (DAGELIJKS)** - `docs/03-operationeel/`
   - `operations-runbook.md` - Operational procedures
   - `troubleshooting-guide.md` - Common issues and solutions
   - `tools/` - Tool-specific documentation

---

## Documentation Standards

- Follow `.github/instructions/md-style-guide.md` for all Markdown formatting
- Follow `.github/instructions/code-formatting.md` for all code block formatting

---

## Security & Data Guidelines (aanvulling op basisbestand)

- **NO** PII van ziekenhuismedewerkers in outputbestanden
- **ALWAYS** work with anonymized or aggregated ticketing data in reports
- **TEST** data transformations on sample datasets before running on full exports

### Data Sources

- **Primaire bron:** Maandelijkse ticketing exports vanuit project SD30 (CSV/Excel)
- **Referentieperiode:** 2025 als baseline, cumulatief 2026 als lopend jaar
- **Granulariteit:** Per ziekenhuis, per categorie, per maand
- **Opslag:** Lokale werkmap — geen ticketingdata in Git committen

### Repository Structure

- `.github/` - GitHub configuration, instructions, docs, workflows
- `archive/` - Oude versies van documenten/code/scripts
- `data/` - Lokale databestanden (uitgesloten van Git)
- `docs/` - Documentation (3-layer structure)
- `scripts/` - CLI-entrypoints en runners
- `src/` - Python broncode (analyse, rapportage, visualisatie)
- `tools/` - Dev-tooling (lint.ps1)
- `output/` - Gegenereerde rapporten en visualisaties (uitgesloten van Git)
- `tests/` - Unit tests en testdata
- `WIP/` - Work In Progress

### File Search — extra exclusies

Naast de standaard exclusies uit het basisbestand ook uitsluiten:

- `data/` (ruwe ticketingdata — nooit indexeren)
- `output/` (gegenereerde rapporten — alleen op expliciete vraag)

---

## Branding

> Volledig referentiedocument: `.github/docs/zorgi_design_system.md`
> Productnamen & kleuren: `.github/docs/product-names.md`
> Tone of voice: `.github/docs/tone-of-voice.md`

Bij elke branded output (rapport, dashboard, visualisatie) de design checklist
in `zorgi_design_system.md § 12` raadplegen.

---

## Custom Commands — Overzicht

| Commando | Scripting | Q&A-Lab | CSAT-Compass | Opmerking |
|---|:---:|:---:|:---:|---|
| `/pdf` | ✅ | ✅ | ✅ | Alle projecten |
| `/advies` | ✅ | ✅ | ✅ | Alle projecten |
| `/GIT` | ✅ | ✅ | ✅ | Alle projecten |
| `/cve` | ✅ | ✅ | ✅ | Alle projecten |
| `/smd` | ✅ | ❌ | ❌ | Scripting-specifiek |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 01/01/2026 | Initiële versie | Danny Depecker |
| 2.0 | 17/03/2026 | Herstructurering en uitbreiding | Danny Depecker + Claude |
| 2.7 | 19/03/2026 | /GIT flows, /cve, branding sectie | Danny Depecker + GHC |
| 3.0 | 24/03/2026 | Afgeslankt — gedeelde instructies verplaatst naar copilot-base.instructions.md | Danny Depecker |
