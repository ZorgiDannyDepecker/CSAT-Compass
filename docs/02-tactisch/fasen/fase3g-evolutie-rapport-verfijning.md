# CSAT-Compass — Fase 3g: Evolutierapport verfijning

**Versie:** 5.0
**Laatst bijgewerkt:** 31/03/2026

**Doel:** Implementatie van release 1 voor de verfijning en verrijking van de evolutie-markdown-rapporten
**Type:** Implementatie
**Auteur:** Danny Depecker + Claude Desktop + GHC
**Status:** Compleet

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

## 9. Implementatiestatus (30/03/2026)

Na volledige pipeline-review op 30/03/2026 is vastgesteld dat GHC alle release 1 scope
reeds heeft geïmplementeerd. De onderstaande tabel toont de werkelijke status per component.

### 9.1 Voltooide componenten

| Component | Bestand | Status |
|---|---|---|
| KPI-targets (7) | `src/csat/config/settings.py` | ✅ Geïmplementeerd |
| Dataklassen fase 3g | `src/csat/core/analysers/evolution_result.py` | ✅ Geïmplementeerd |
| Alle berekeningen fase 3g | `src/csat/core/analysers/evolution_analyser.py` | ✅ Geïmplementeerd |
| Interpreterende laag | `src/csat/core/insights/insights_generator.py` | ✅ Geïmplementeerd |
| InsightsGenerator integratie | `src/csat/core/exporters/evolution_exporter.py` | ✅ Geïmplementeerd |
| NL template (alle secties) | `docs/templates/evolutie-nl.md.j2` | ✅ Geïmplementeerd |
| i18n NL (insights-sleutels) | `src/csat/i18n/nl.json` | ✅ Geïmplementeerd |

### 9.2 Resterende aanvullingen

De 3 resterende gaps zijn gedocumenteerd in `WIP/ghc-prompts-fase3g-interpreterende-laag.md`.

| Gap | Bestand | Impact |
|---|---|---|
| `baseline_correlation_score` veld ontbreekt | `evolution_result.py` | Basisvereiste voor omslag-detectie |
| Baseline-correlatie niet berekend | `evolution_analyser.py` | Basisvereiste voor omslag-detectie |
| Correlatie-omslag bevinding + KPI-achievement narrative | `insights_generator.py` | Sectie 2 + executive summary |

Na uitvoering stijgt de kwaliteitspariteit met de CD-referentiedocumenten van ~60% naar ~75-80%.

### 9.3 Template-uitbreidingen (30/03/2026 — rechtstreeks via CD)

Na vergelijking van de gegenereerde output met de CD-referentiedocumenten zijn 3 aanvullende
template-aanpassingen doorgevoerd. Alle wijzigingen zijn rechtstreeks toegepast (geen GHC-prompt
nodig) omdat het zuivere template- en i18n-wijzigingen zijn zonder Python-logica.

| Element | Sectie | Wijziging |
|---|---|---|
| Mediaan + Std. deviatie + % Neutraal | §3 Kerncijfers | 3 rijen toegevoegd (conditioneel op `baseline_summary`) |
| Delta score kolom | §5 Analyse per type | Extra kolom `(current_score - baseline_score)` |
| % Negatief baseline + huidig | §6 Analyse per prioriteit | 2 extra kolommen `baseline_pct_neg` / `current_pct_neg` |

Betrokken bestanden: `docs/templates/evolutie-nl.md.j2`, `src/csat/i18n/nl.json`,
`src/csat/i18n/fr.json`, `tests/core/test_evolution_exporter.py` (klasse `TestKerncijfersUitbreidingen`).
De resterende ~20-25% is het inherente verschil tussen keyword-matching thema-percentages
en de NLP-gedreven thema-analyse van de CD-versie — een bewuste architectuurkeuze (beslissing 1).

---

## 10. Referenties

- Fase 3f: `docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md` **(v3.0 — normatief kader)**
- Fase 3b: `docs/02-tactisch/fasen/fase3b-evolutie-analyser.md`
- Fase 3c: `docs/02-tactisch/fasen/fase3c-evolutie-exporter.md`
- EvolutionResult: `src/csat/core/analysers/evolution_result.py`
- InsightsGenerator: `src/csat/core/insights/insights_generator.py` (gedeeld — fase 3g)
- Templates: `docs/templates/evolutie-nl.md.j2` + `evolutie-fr.md.j2`
- i18n: `src/csat/i18n/nl.json` + `fr.json`
- GHC-prompts: `WIP/ghc-prompts-fase3g-interpreterende-laag.md`

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| --- | --- | --- | --- |
| 1.0 | 27/03/2026 | Initiële versie — framework aangemaakt, inhoud TBD | Danny Depecker |
| 2.0 | 29/03/2026 | Hernoemd van fase 3f naar fase 3g; scope bevestigd op basis van GHC-advies | Danny Depecker + GHC |
| 3.0 | 29/03/2026 | Scope gecorrigeerd op basis van alle 12 DDP-beslissingen: volledige comments + ticket-ID's (besl. 2+3), scoreverdeling (besl. 12), visuele analyse (besl. 8), eigenaar per aanbeveling (besl. 9), matrix-absorptie (besl. 11), 7 KPI-targets (besl. 5), gedeelde InsightsGenerator (besl. 7), comment-policy geëxpliciteerd | Danny Depecker + CD + GHC |
| 4.0 | 30/03/2026 | Implementatiestatus bijgewerkt na pipeline-review: alle 7 lagen geïmplementeerd; 3 resterende aanvullingen gedocumenteerd in §9 en WIP/ghc-prompts-fase3g-interpreterende-laag.md | Danny Depecker + CD |
| 5.0 | 31/03/2026 | Fase afgesloten: alle resterende aanvullingen geïmplementeerd (baseline correlatie, omslag-detectie, NL/FR taalcorrecties, 14.N nummering); status → Compleet; 727 tests, 100% coverage, CI stabiel | Danny Depecker + GHC |
