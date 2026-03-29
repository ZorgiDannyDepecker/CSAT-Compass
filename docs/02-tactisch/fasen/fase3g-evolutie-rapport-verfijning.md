# CSAT-Compass - Fase 3g: Evolutierapport verfijning

**Versie:** 2.0
**Laatst bijgewerkt:** 29/03/2026

**Doel:** Implementatie van release 1 voor de verfijning en verrijking van de evolutie-markdown-rapporten
**Type:** Implementatie
**Auteur:** Danny Depecker + GHC
**Status:** In planning — scope bevestigd

**Bestandsnaam:** fase3g-evolutie-rapport-verfijning.md
**Path:** docs/02-tactisch/fasen/

---

## 1. Overzicht

Fase 3g verfijnt de **evolutie-markdown-rapporten** (NL + FR) die worden gegenereerd door
`EvolutionExporter` en de Jinja2-templates in `docs/templates/`. De rapporten zijn functioneel
maar kunnen op vlak van context, leesbaarheid en informatiedichtheid nog worden verrijkt.

De inhoudelijke keuzes voor deze fase zijn niet langer TBD. Ze werden vastgelegd in
`docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md` en vormen het verplichte besliskader
voor alle implementatiestappen in deze fase.

**T-shirt:** M
**Afhankelijkheid:** Fase 3f (advieskader) + Fase 3c (EvolutionExporter + templates) + Fase 3b (EvolutionResult)
**Teststand bij start:** 570 tests — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## 2. Deliverables

| Component | Bestand | Status |
|---|---|---|
| Advieskader | `docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md` | ✅ Input bevestigd |
| Template Nederlands | `docs/templates/evolutie-nl.md.j2` | 🔄 Te verfijnen |
| Template Frans | `docs/templates/evolutie-fr.md.j2` | 🔄 Te verfijnen |
| i18n-sleutels NL | `src/csat/i18n/nl.json` | 🔄 Mogelijk uitbreiden |
| i18n-sleutels FR | `src/csat/i18n/fr.json` | 🔄 Mogelijk uitbreiden |
| EvolutionResult | `src/csat/core/analysers/evolution_result.py` | 🔄 Mogelijk uitbreiden |
| EvolutionAnalyser | `src/csat/core/analysers/evolution_analyser.py` | 🔄 Mogelijk uitbreiden |
| EvolutionExporter | `src/csat/core/exporters/evolution_exporter.py` | 🔄 Mogelijk uitbreiden |
| Insights-helper | `src/csat/core/exporters/evolution_insights.py` | ➕ Nieuw |
| Tests templates | `tests/core/test_evolution_exporter.py` | 🔄 Bijwerken |
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

De scope van fase 3g is bevestigd via het advieskader in fase 3f. Release 1 focust op de
hoogste managementwaarde en volgt expliciet een 80/20-aanpak.

### 4.1 Verplicht in scope

- Executive Summary met kernboodschap
- Kritieke bevindingen
- Responstijd-correlatie en positief-vs-negatief vergelijking
- Positieve ontwikkelingen
- Strategische aanbevelingen
- Follow-up acties
- Dubbele benchmark: volledig 2025 + H2 2025
- Shortlist ziekenhuizen boven de volledige tabel
- Recurring themes met voorbeeld en actiehint

### 4.2 Bewust buiten scope van release 1

- Volledige legacy-pariteit sectie per sectie
- Nieuwe NLP-classificatie of semantische analyse-engine
- LLM als basisarchitectuur
- Duplicatie van matrix-functionaliteit in het evolutierapport

---

## 5. Architectuur — betrokken componenten

```text
EvolutionAnalyser.analyse()
    └─► EvolutionResult (dataclass)
            └─► EvolutionInsightsBuilder / evolution_insights.py
                    └─► EvolutionExporter.export()
                            └─► Jinja2 template (evolutie-nl.md.j2 / evolutie-fr.md.j2)
                                    └─► output/evolutie-{pillar}-{jaar}-{lang}.md
```

### 5.1 Relevante bestanden

| Bestand | Rol in fase 3g |
|---|---|
| `src/csat/core/analysers/evolution_analyser.py` | Bronberekeningen — uitbreiden indien nieuwe metrics |
| `src/csat/core/analysers/evolution_result.py` | Datacontainer — nieuwe velden toevoegen indien nodig |
| `src/csat/core/exporters/evolution_insights.py` | Nieuwe insight-laag — executive summary, findings, aanbevelingen |
| `src/csat/core/exporters/evolution_exporter.py` | Template-context bouwen — nieuwe variabelen doorgeven |
| `docs/templates/evolutie-nl.md.j2` | NL template — secties aanpassen/toevoegen |
| `docs/templates/evolutie-fr.md.j2` | FR template — idem in Frans |
| `src/csat/i18n/nl.json` + `fr.json` | Vertalingen — nieuwe sleutels |

---

## 6. Testprincipes

- Elke nieuwe berekening in `EvolutionAnalyser` krijgt een unit test
- Elke nieuwe insight-regel krijgt een gerichte assertion in exporter- of helpertests
- Template-wijzigingen worden getest via `test_evolution_exporter.py`
  (snapshot-test of keyword-assertions op de gerenderde output)
- Nieuwe `EvolutionResult`-velden krijgen default-waarden zodat bestaande tests blijven slagen
- Doelstand: **100% coverage behouden**

---

## 7. Werkwijze

1. **Lees fase 3f volledig** — `fase3f-evolutie-advieskader.md` is het normatieve besliskader
2. **Analyseer impact** — welke laag(en) moeten worden aangepast (data / insights / exporter / template)
3. **Pas EvolutionResult aan** — nieuwe velden met `field(default_factory=...)` zodat backward-compatible
4. **Pas EvolutionAnalyser aan** — berekeningen voor metrics, dubbele benchmark en shortlistlogica
5. **Bouw de insight-helper** — rule-based executive summary, findings, aanbevelingen, follow-up
6. **Pas templates aan** — NL eerst, daarna FR (tweetaligheidsbeginsel)
7. **Schrijf/update tests** — 100% coverage bewaken en nieuwe secties afdekken
8. **Genereer voorbeeldoutput** — `python scripts/generate_all_evolutions.py --pillar pharma`
9. **Valideer inhoudelijk** — Danny Depecker reviewt de gegenereerde MD en vergelijkt met referentie-output

---

## 8. Referenties

- Fase 3f: `docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md`
- Fase 3b: `docs/02-tactisch/fasen/fase3b-evolutie-analyser.md`
- Fase 3c: `docs/02-tactisch/fasen/fase3c-evolutie-exporter.md`
- EvolutionResult: `src/csat/core/analysers/evolution_result.py`
- Insights-helper: `src/csat/core/exporters/evolution_insights.py` (nieuw in fase 3g)
- Templates: `docs/templates/evolutie-nl.md.j2` + `evolutie-fr.md.j2`
- i18n: `src/csat/i18n/nl.json` + `fr.json`

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 27/03/2026 | Initiële versie — framework aangemaakt, inhoud TBD | Danny Depecker |
| 2.0 | 29/03/2026 | Hernoemd van fase 3f naar fase 3g; scope bevestigd op basis van fase 3f-advieskader; paden en werkwijze bijgewerkt | Danny Depecker + GHC |
