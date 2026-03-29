# CSAT-Compass — Fase 3g: Evolutierapport verfijning

**Versie:** 3.0
**Laatst bijgewerkt:** 29/03/2026

**Doel:** Implementatie van release 1 voor de verfijning en verrijking van de evolutie-markdown-rapporten
**Type:** Implementatie
**Auteur:** Danny Depecker + Claude Desktop + GHC
**Status:** In planning — scope bevestigd en gecorrigeerd

**Bestandsnaam:** fase3g-evolutie-rapport-verfijning.md
**Path:** docs/02-tactisch/fasen/

---

## 1. Overzicht

Fase 3g verfijnt de **evolutie-markdown-rapporten** (NL + FR) die worden gegenereerd door
`EvolutionExporter` en de Jinja2-templates in `docs/templates/`. De rapporten zijn functioneel
maar kunnen op vlak van context, leesbaarheid en informatiedichtheid nog worden verrijkt.

De inhoudelijke keuzes voor deze fase werden vastgelegd in
`docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md` (v3.0) en vormen het **verplichte** besliskader
voor alle implementatiestappen in deze fase.

**T-shirt:** M
**Afhankelijkheid:** Fase 3f (advieskader v3.0) + Fase 3c (EvolutionExporter + templates) + Fase 3b (EvolutionResult)
**Teststand bij start:** 570 tests — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## 2. Deliverables

| Component | Bestand | Status |
|---|---|---|
| Advieskader | `docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md` | ✅ Input bevestigd (v3.0) |
| Template Nederlands | `docs/templates/evolutie-nl.md.j2` | 🔄 Te verfijnen |
| Template Frans | `docs/templates/evolutie-fr.md.j2` | 🔄 Te verfijnen |
| i18n-sleutels NL | `src/csat/i18n/nl.json` | 🔄 Uitbreiden (zinsvariatie + narratief) |
| i18n-sleutels FR | `src/csat/i18n/fr.json` | 🔄 Uitbreiden (zinsvariatie + narratief) |
| EvolutionResult | `src/csat/core/analysers/evolution_result.py` | 🔄 Uitbreiden (nieuwe dataklassen) |
| EvolutionAnalyser | `src/csat/core/analysers/evolution_analyser.py` | 🔄 Uitbreiden (nieuwe metrics) |
| EvolutionExporter | `src/csat/core/exporters/evolution_exporter.py` | 🔄 Uitbreiden (context) |
| InsightsGenerator | `src/csat/core/insights/insights_generator.py` | ➕ Nieuw — gedeeld met maandrapport |
| Tests insights | `tests/core/test_insights_generator.py` | ➕ Nieuw |
| Tests exporter | `tests/core/test_evolution_exporter.py` | 🔄 Bijwerken |
| Tests analyser | `tests/core/test_evolution_analyser.py` | 🔄 Bijwerken |
| Fase-document | `docs/02-tactisch/fasen/fase3g-evolutie-rapport-verfijning.md` | ✅ Dit bestand |

---

## 3. Huidige rapportstructuur (baseline voor Fase 3g)

De template `evolutie-nl.md.j2` bevat momenteel 8 secties:

| # | Sectie | Inhoud |
|---|---|---|
| 1 | Samenvatting | KPI-tabel: tickets, avg score, % pos/neg, HC-ratio, responstijd, # ziekenhuizen |
| 2 | Maandelijkse tijdlijn | Score, % negatief, totaal tickets, fase per maand |
| 3 | KPI-status | OK / WARNING / AT_RISK per KPI, baseline vs huidig |
| 4 | Per issue type | Avg score + % negatief, baseline vs huidig |
| 5 | Per prioriteit + responstijd | Score per prioriteit + responstijd per score-niveau |
| 6 | Per ziekenhuis | Score delta per ziekenhuis + nieuwe/verdwenen ziekenhuizen |
| 7 | Feedbackthema's | % negatieve comments per thema, OPGELOST / NIEUW / NOG_AANWEZIG |
| 8 | Conclusie | Automatische narratief + HC-waarschuwingen + thema-samenvatting |

---

## 4. Bevestigde scope release 1

De scope van fase 3g is bevestigd via het advieskader in fase 3f (v3.0). Release 1 focust op de
hoogste managementwaarde en volgt expliciet een 80/20-aanpak.

### 4.1 Verplicht in scope

- **Executive Summary** met kernboodschap + scoreverdeling-narratief (beslissing 12)
- **Kritieke bevindingen** — 3-5 bevindingen met causaliteit en ernst
- **Responstijd-correlatie** en positief-vs-negatief vergelijking
- **Scoreverdeling** als compacte rij in kerncijfertabel (beslissing 12)
- **Visuele analyse** met narratieve beschrijving per subplot (beslissing 8)
- **Negatieve feedback deep-dive** met ticket-ID's + volledige comments (beslissingen 2+3)
- **KPI target tracking** met 7 targets (beslissing 5)
- **Strategische aanbevelingen** met impact, tijdlijn en eigenaar (beslissing 9)
- **Follow-up acties** per tijdshorizon
- **Keerpuntanalyse** in tijdlijn
- **Dubbele benchmark**: volledig 2025 + H2 2025
- **Shortlist ziekenhuizen** boven de volledige tabel
- **Matrix-inhoud integreren** — benchmark-tabellen en target tracking uit output B absorberen (beslissing 11)
- **Positieve ontwikkelingen** als vaste sectie
- **Recurring themes** met voorbeeld en actiehint

### 4.2 Bewust buiten scope van release 1

- Volledige legacy-pariteit sectie per sectie (80/20 volstaat)
- Nieuwe NLP-classificatie of semantische analyse-engine
- LLM als basisarchitectuur
- FR-template (ronde 2)
- Uitgebreide issue type / prioriteit detail-analyse (ronde 2)

### 4.3 Bevestigde comment-policy

**Beslissingen 2 + 3:** Klantcomments en ticket-ID's worden **volledig** opgenomen in het rapport, net zoals in referentie A:

- `comment` bevat de volledige tekst uit V_CSAT_1 — geen limiet op lengte
- `ticket_id` (bv. SD30-36770) wordt als-is overgenomen en is zichtbaar in het rapport
- `hospital` wordt als-is overgenomen — geen anonimisering van ziekenhuisnamen
- Enige sanitizing: eventuele ZORGI-medewerkersnamen worden verwijderd via `sanitize_comment()`

### 4.4 Bevestigde KPI-targets

**Beslissing 5:** 7 targets worden geconfigureerd in `settings.py`:

| KPI | Target | Bron |
|---|---|---|
| `avg_score_min` | ≥ 4,00 | Reeds in `settings.py` |
| `high_critical_max` | ≤ 15,0% | Reeds in `settings.py` |
| `pct_positive_min` | ≥ 75% | Nieuw |
| `pct_negative_max` | ≤ 15% | Nieuw |
| `avg_response_days_max` | ≤ 10,0 dagen | Nieuw |
| `pct_with_comment_min` | ≥ 40% | Nieuw — klantbetrokkenheid |
| `hospital_retention_min` | ≥ 50% | Nieuw — retentie baseline-ziekenhuizen |

---

## 5. Architectuur — betrokken componenten

```text
EvolutionAnalyser.analyse() / MonthlyAnalyser
    └─► EvolutionResult / MonthlyResult (verrijkte dataklassen)
            └─► InsightsGenerator (regelgebaseerd — gedeeld, beslissing 7)
                    └─► EvolutionExporter.export() / MonthlyExporter
                            └─► Jinja2 template
                                    └─► output/evolutie-{pillar}-{jaar}-{lang}.md
```

**Beslissing 7:** De `InsightsGenerator` is een **gedeelde module** die zowel door het evolutierapport als het maandrapport wordt gebruikt. Gedeelde logica omvat executive summary, bevindingenselectie, aanbevelingenformulering en KPI-tracking. Rapporttype-specifieke logica (bv. keerpuntanalyse alleen in evolutie) zit in aparte methoden.

**Beslissing 11:** De matrix-inhoud (benchmark-tabel, target tracking, structureel/tijdelijk-beoordeling) wordt geabsorbeerd in het evolutierapport. De MatrixExporter blijft als optioneel rapport maar is niet langer het primaire managementdocument.

### 5.1 Relevante bestanden

| Bestand | Rol in fase 3g |
|---|---|
| `src/csat/core/analysers/evolution_analyser.py` | Bronberekeningen — uitbreiden met nieuwe metrics |
| `src/csat/core/analysers/evolution_result.py` | Datacontainer — nieuwe dataklassen toevoegen |
| `src/csat/core/insights/insights_generator.py` | **Nieuw** — gedeelde insight-laag (executive summary, findings, aanbevelingen) |
| `src/csat/core/exporters/evolution_exporter.py` | Template-context bouwen — nieuwe variabelen doorgeven |
| `docs/templates/evolutie-nl.md.j2` | NL template — secties aanpassen/toevoegen |
| `docs/templates/evolutie-fr.md.j2` | FR template — ronde 2 |
| `src/csat/i18n/nl.json` + `fr.json` | Vertalingen — zinsvariatie-bibliotheek + narratieve fragmenten |
| `src/csat/config/settings.py` | 7 KPI-targets opnemen |

---

## 6. Testprincipes

- Elke nieuwe berekening in `EvolutionAnalyser` krijgt een unit test
- Elke nieuwe insight-regel in `InsightsGenerator` krijgt een gerichte assertion
- Template-wijzigingen worden getest via `test_evolution_exporter.py`
  (snapshot-test of keyword-assertions op de gerenderde output)
- Nieuwe `EvolutionResult`-velden krijgen default-waarden zodat bestaande tests blijven slagen
- Doelstand: **100% coverage behouden**

---

## 7. Werkwijze

1. **Lees fase 3f volledig** — `fase3f-evolutie-advieskader.md` v3.0 is het normatieve besliskader
2. **Analyseer impact** — welke laag(en) moeten worden aangepast (data / insights / exporter / template)
3. **Pas EvolutionResult aan** — nieuwe velden met `field(default_factory=...)` zodat backward-compatible
4. **Pas EvolutionAnalyser aan** — berekeningen voor metrics, scoreverdeling, correlatie, dubbele benchmark, negatieve cases met volledige comments + ticket-ID's
5. **Bouw de InsightsGenerator** — gedeelde module in `src/csat/core/insights/`, rule-based executive summary, findings, aanbevelingen (met impact/tijdlijn/eigenaar), visuele analyse, follow-up
6. **Voeg 7 KPI-targets toe aan settings.py**
7. **Pas templates aan** — NL eerst, FR in ronde 2 (tweetaligheidsbeginsel)
8. **Schrijf/update tests** — 100% coverage bewaken en nieuwe secties afdekken
9. **Genereer voorbeeldoutput** — `python scripts/generate_all_evolutions.py --pillar pharma`
10. **Valideer inhoudelijk** — Danny Depecker reviewt de gegenereerde MD en vergelijkt met referentie A/B via de validatiechecklist uit fase 3f

---

## 8. Referenties

- Fase 3f: `docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md` **(v3.0 — normatief kader)**
- Fase 3b: `docs/02-tactisch/fasen/fase3b-evolutie-analyser.md`
- Fase 3c: `docs/02-tactisch/fasen/fase3c-evolutie-exporter.md`
- EvolutionResult: `src/csat/core/analysers/evolution_result.py`
- InsightsGenerator: `src/csat/core/insights/insights_generator.py` (nieuw in fase 3g — gedeeld)
- Templates: `docs/templates/evolutie-nl.md.j2` + `evolutie-fr.md.j2`
- i18n: `src/csat/i18n/nl.json` + `fr.json`

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| --- | --- | --- | --- |
| 1.0 | 27/03/2026 | Initiële versie — framework aangemaakt, inhoud TBD | Danny Depecker |
| 2.0 | 29/03/2026 | Hernoemd van fase 3f naar fase 3g; scope bevestigd op basis van GHC-advies | Danny Depecker + GHC |
| 3.0 | 29/03/2026 | Scope gecorrigeerd op basis van alle 12 DDP-beslissingen: volledige comments + ticket-ID's (besl. 2+3), scoreverdeling (besl. 12), visuele analyse (besl. 8), eigenaar per aanbeveling (besl. 9), matrix-absorptie (besl. 11), 7 KPI-targets (besl. 5), gedeelde InsightsGenerator (besl. 7), comment-policy geëxpliciteerd | Danny Depecker + CD + GHC |
