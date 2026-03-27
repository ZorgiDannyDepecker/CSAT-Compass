# CSAT-Compass - Fase 3f: Evolutierapport verfijning

**Versie:** 1.0
**Laatst bijgewerkt:** 27/03/2026

**Doel:** Inhoudelijke verfijning en uitbreiding van de evolutie-markdown-rapporten
**Type:** Implementatie
**Auteur:** Danny Depecker + GHC
**Status:** In planning — inhoud TBD

**Bestandsnaam:** fase3f-evolutie-rapport-verfijning.md
**Path:** docs/02-tactisch/fasen/

---

## 1. Overzicht

Fase 3f verfijnt de **evolutie-markdown-rapporten** (NL + FR) die worden gegenereerd door
`EvolutionExporter` en de Jinja2-templates in `docs/templates/`. De rapporten zijn functioneel
maar kunnen op vlak van context, leesbaarheid en informatiedichtheid nog worden verrijkt.

De concrete verbeteringen worden aangeleverd door Danny Depecker en vormen de input voor deze fase.

**T-shirt:** S–M (afhankelijk van de specifieke vereisten)
**Afhankelijkheid:** Fase 3c (EvolutionExporter + templates) + Fase 3b (EvolutionResult)
**Teststand bij start:** 570 tests — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## 2. Deliverables

| Component | Bestand | Status |
|---|---|---|
| Template Nederlands | `docs/templates/evolutie-nl.md.j2` | 🔄 Te verfijnen |
| Template Frans | `docs/templates/evolutie-fr.md.j2` | 🔄 Te verfijnen |
| i18n-sleutels NL | `src/csat/core/i18n/nl.py` | 🔄 Mogelijk uitbreiden |
| i18n-sleutels FR | `src/csat/core/i18n/fr.py` | 🔄 Mogelijk uitbreiden |
| EvolutionResult | `src/csat/core/analysers/evolution_result.py` | 🔄 Mogelijk uitbreiden |
| EvolutionAnalyser | `src/csat/core/analysers/evolution_analyser.py` | 🔄 Mogelijk uitbreiden |
| EvolutionExporter | `src/csat/core/exporters/evolution_exporter.py` | 🔄 Mogelijk uitbreiden |
| Tests templates | `tests/core/test_evolution_exporter.py` | 🔄 Bijwerken |
| Fase-document | `docs/02-tactisch/fasen/fase3f-evolutie-rapport-verfijning.md` | ✅ Dit bestand |

---

## 3. Huidige rapportstructuur (baseline voor Fase 3f)

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

## 4. Gewenste verbeteringen

> ⚠️ **Inhoud TBD** — wordt aangeleverd door Danny Depecker.

De verbeteringen kunnen betrekking hebben op (niet-limitatief):

- Nieuwe secties of subsecties
- Aanvullende berekeningen in `EvolutionAnalyser`
- Nieuwe velden in `EvolutionResult` of helper-dataklassen
- Bijgestelde narratieven in sectie 8 (conclusie)
- Bijkomende i18n-sleutels NL + FR
- Verbeterde tabelopmaak of conditionals in de templates

---

## 5. Architectuur — betrokken componenten

```text
EvolutionAnalyser.analyse()
    └─► EvolutionResult (dataclass)
            └─► EvolutionExporter.export()
                    └─► Jinja2 template (evolutie-nl.md.j2 / evolutie-fr.md.j2)
                            └─► output/evolutie-{pillar}-{jaar}-{lang}.md
```

### 5.1 Relevante bestanden

| Bestand | Rol in fase 3f |
|---|---|
| `src/csat/core/analysers/evolution_analyser.py` | Bronberekeningen — uitbreiden indien nieuwe metrics |
| `src/csat/core/analysers/evolution_result.py` | Datacontainer — nieuwe velden toevoegen indien nodig |
| `src/csat/core/exporters/evolution_exporter.py` | Template-context bouwen — nieuwe variabelen doorgeven |
| `docs/templates/evolutie-nl.md.j2` | NL template — secties aanpassen/toevoegen |
| `docs/templates/evolutie-fr.md.j2` | FR template — idem in Frans |
| `src/csat/core/i18n/nl.py` + `fr.py` | Vertalingen — nieuwe sleutels |

---

## 6. Testprincipes

- Elke nieuwe berekening in `EvolutionAnalyser` krijgt een unit test
- Template-wijzigingen worden getest via `test_evolution_exporter.py`
  (snapshot-test of keyword-assertions op de gerenderde output)
- Nieuwe `EvolutionResult`-velden krijgen default-waarden zodat bestaande tests blijven slagen
- Doelstand: **100% coverage behouden**

---

## 7. Werkwijze

1. **Ontvang inhoud** — Danny Depecker bezorgt de gewenste verbeteringen
2. **Analyseer impact** — welke laag(en) moeten worden aangepast (data / exporter / template)
3. **Pas EvolutionResult aan** — nieuwe velden met `field(default_factory=...)` zodat backward-compatible
4. **Pas EvolutionAnalyser aan** — berekeningen voor nieuwe velden
5. **Pas templates aan** — NL eerst, daarna FR (tweetaligheidsbeginsel)
6. **Schrijf/update tests** — 100% coverage bewaken
7. **Genereer voorbeeldoutput** — `python scripts/generate_all_evolutions.py --pillar pharma`
8. **Valideer visueel** — Danny Depecker reviewt de gegenereerde MD + `/pdf`

---

## 8. Referenties

- Fase 3b: `docs/02-tactisch/fasen/fase3b-evolutie-analyser.md`
- Fase 3c: `docs/02-tactisch/fasen/fase3c-evolutie-exporter.md`
- EvolutionResult: `src/csat/core/analysers/evolution_result.py`
- Templates: `docs/templates/evolutie-nl.md.j2` + `evolutie-fr.md.j2`
- i18n: `src/csat/core/i18n/nl.py` + `fr.py`

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 27/03/2026 | Initiële versie — framework aangemaakt, inhoud TBD | Danny Depecker |
