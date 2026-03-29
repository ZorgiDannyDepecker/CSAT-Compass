# GHC Advies Evolutie-Verbetering — Verwerkte Beslissingen DDP

**Versie:** 2.0  
**Datum:** 29/03/2026  
**Status:** Definitief advieskader op basis van DDP-antwoorden  
**Doel:** Geactualiseerd adviesdocument voor Fase 3f — evolutierapport verfijning in `CSAT-Compass`

---

## Leeswijzer

Deze analyse vergelijkt:

- **Referentie A:** [`tendens_2026_03_03.md`](file:///C:/Users/danndepe/Documents/AI/Customer%20Satisfaction/tendens_2026_03_03.md)
- **Referentie B:** [`Tendens_Vergelijkingsmatrix.md`](file:///C:/Users/danndepe/Documents/AI/Customer%20Satisfaction/Tendens_Vergelijkingsmatrix.md)
- **Huidige output C:** [`output/evolutie-pharma-2026-nl.md`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/output/evolutie-pharma-2026-nl.md)

Geanalyseerde code en templates:

- [`src/csat/core/analysers/evolution_analyser.py`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/src/csat/core/analysers/evolution_analyser.py)
- [`src/csat/core/analysers/evolution_result.py`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/src/csat/core/analysers/evolution_result.py)
- [`src/csat/core/exporters/evolution_exporter.py`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/src/csat/core/exporters/evolution_exporter.py)
- [`docs/templates/evolutie-nl.md.j2`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/docs/templates/evolutie-nl.md.j2)
- [`src/csat/i18n/nl.json`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/src/csat/i18n/nl.json)
- [`docs/templates/rapport-nl.md.j2`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/docs/templates/rapport-nl.md.j2)
- [`src/csat/config/pillars.py`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/src/csat/config/pillars.py)
- [`src/csat/config/settings.py`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/src/csat/config/settings.py)

Dit document is een **bijgewerkte en aangescherpte versie** van het eerdere advies.  
Het verschil is dat de architecturale en inhoudelijke keuzes nu niet meer hypothetisch zijn, maar worden behandeld als **bevestigde beslissingen van DDP**.

---

## Positionering t.o.v. andere rapporttypes

De evolutie-output in `CSAT-Compass` zit vandaag inhoudelijk tussen twee oude rapportvormen in:

- het **tendensrapport** levert managementduiding, cases, aanbevelingen en follow-up;
- de **vergelijkingsmatrix** levert benchmark- en targettracking over meerdere referentiekaders;
- het huidige **evolutierapport** levert vooral deterministische tabellen en een korte conclusie.

Dat betekent: de huidige evolutie-output is **sterk als data-export**, maar **zwak als managementrapport**.

De matrix hoeft niet gedupliceerd te worden.  
De matrix moet benchmarken; het evolutierapport moet **verklaren, duiden en prioriteren**.

### Definitieve positionering op basis van DDP-keuze

Deze keuze ligt nu expliciet vast:

- **Matrix = benchmarkrapport**
- **Evolutie = interpretatie- en veranderduidingsrapport**

Dat is een belangrijke beslissing, omdat het voorkomt dat Fase 3f ontspoort in een poging om zowel matrix als tendens als evolutie in één rapporttype te proppen.

---

## Beslisrecord — verwerkte antwoorden DDP

Op basis van de beantwoorde MCQ-vragen geldt voor Fase 3f voortaan het volgende besliskader.

### Architectuur

- De nieuwe insight-logica komt in een **aparte helpermodule**
- Nieuwe analyseelementen worden gemodelleerd via **expliciete dataklassen**
- KPI-targets worden centraal beheerd in **config/settings per pijler**
- De oplossing blijft **regelgebaseerd als basisarchitectuur**
- Een LLM-gedreven laag is **niet uitgesloten op termijn**, maar **niet aanbevolen als fundament van release 1**

### Inhoud

- Primair doel van het vernieuwde evolutierapport = **managementduiding en prioritering**
- Doel = **80/20-pariteit met de oude referentie-output**
- Negatieve feedbackvoorbeelden = **korte, gesaniteerde quotes zonder PII**
- Ziekenhuissectie = **eerst shortlist, daarna volledige tabel**
- Referentiebasis = **volledig 2025 én H2 2025 als dubbele benchmark**
- `Positieve Ontwikkelingen` wordt een **vaste sectie**
- Keyword-thema's blijven bestaan, maar worden uitgebreid met **voorbeelden en actiehint**

### Scope release 1

Release 1 focust op:

- Executive Summary
- Kritieke Bevindingen
- Responstijd-correlatie
- Strategische aanbevelingen
- Follow-up acties

### Validatie

Acceptatie gebeurt via:

- unit tests
- snapshot/keyword assertions
- manuele business review

Deze beslissingen zijn essentieel: ze zetten Fase 3f om van een open verkenning naar een **gericht implementatiekader**.

---

## Gap-analyse per rapportsectie

| Sectie | Referentie-output | Huidig | Gap-niveau |
| --- | --- | --- | --- |
| Rapportkader / metadata | Referentie noemt periode, organisatie, project, product, rapportagedatum expliciet | Huidig toont enkel titel + baseline/current labels | MEDIUM |
| Executive Summary | Referentie A start met kerncijfers + expliciete kernboodschap | Huidig start met een KPI-tabel zonder managementsamenvatting | KRITIEK |
| Kritieke bevindingen | Referentie A bevat 4 uitgewerkte bevindingen met causaliteit en ernst | Huidig heeft geen aparte bevindingensectie | KRITIEK |
| Kerncijfers vergelijking | Beide tonen baseline vs huidig; referentie voegt mediaan, std dev, neutraal %, periode en interpretatie toe | Huidig toont avg, pos/neg, HC-ratio, responstijd, # ziekenhuizen | MEDIUM |
| Tijdlijn / trendduiding | Referentie B benoemt dieptepunten, doorbraak, topmaanden, fase-overgangen | Huidig toont maandtabel, maar geen status of keerpuntanalyse | HOOG |
| Analyse per issue type | Referentie geeft aantal, gemiddelde, std dev, aandeel en interpretatie | Huidig toont enkel gemiddelde en % negatief | HOOG |
| Analyse per prioriteit | Referentie geeft aantal, gemiddelde, std dev en interpretatie | Huidig toont gemiddelde en delta, geen volume of duiding | HOOG |
| Responstijd-analyse | Referentie A/B bevat gemiddelde, mediaan, min/max, correlatie en positief-vs-negatief vergelijking | Huidig toont alleen responstijd per score-niveau | KRITIEK |
| Ziekenhuisanalyse | Referentie filtert relevante cases, geeft statuslabels en interpretatie | Huidig toont lange tabel met delta's, weinig prioritering | MEDIUM |
| Verdwenen / nieuwe ziekenhuizen | Huidig detecteert dit correct en expliciet | Referentie heeft minder systematische detectie | LAAG |
| Analyse negatieve feedback | Referentie A bevat ticketcases, probleemclassificatie, recurring themes en voorbeelden | Huidig toont enkel thema-percentages via keyword matching | KRITIEK |
| Thema-evolutie | Referentie B toont opgelost / nog aanwezig / nieuw thema | Huidig doet dit ook, maar veel soberder en zonder voorbeelden | MEDIUM |
| KPI target tracking | Referentie B koppelt baseline, target 2026, realisatie en status | Huidig heeft alleen KPI-status o.b.v. thresholds | HOOG |
| Positieve ontwikkelingen | Referentie A benoemt expliciet wat goed gaat | Huidig doet dit bijna niet apart | MEDIUM |
| Strategische aanbevelingen | Referentie A geeft 6 geprioriteerde acties met impact en timing | Huidig heeft slechts 2-4 generieke conclusieblokken | KRITIEK |
| Follow-up acties | Referentie A sluit af met checklist per tijdshorizon | Huidig bevat geen actieplan | KRITIEK |
| Totaalbeoordeling / structureel vs tijdelijk | Referentie B onderbouwt dat via criteria-matrix | Huidig noemt "structureel/gemengd" met beperkte bewijsvoering | MEDIUM |

### Wat nu al goed is

Het huidige evolutierapport heeft wel degelijk sterke fundamenten:

- de vergelijking baseline vs huidig is consistent opgebouwd;
- `EvolutionAnalyser` berekent al bruikbare kernmetingen zoals avg score, pos/neg %, HC-ratio, responstijd, hospitals en negatieve thema's;
- `EvolutionExporter` en `evolutie-nl.md.j2` leveren een stabiele, reproduceerbare structuur;
- de detectie van verdwenen en nieuwe ziekenhuizen is waardevol;
- de conclusie bevat al eerste rule-based narratieve logica.

Met andere woorden: **de datafundering is niet slecht**.  
De kloof zit vooral in **informatiedichtheid, interpretatie en actiegerichtheid**.

---

## Kernprobleem-diagnose

De fundamentele oorzaak van het kwaliteitsverschil zit op **drie niveaus tegelijk**.

### 1. Ontbrekende metrics

De referentie-output gebruikt managementrelevante maten die vandaag niet in `EvolutionResult` zitten, zoals:

- mediaan score
- standaarddeviatie
- neutraal %
- responstijd-correlatie
- min/max/mediaan responstijd
- counts per issue type/prioriteit
- aandeel per issue type
- ticket-level negatieve cases
- target tracking
- kwalitatieve recurring themes met voorbeelden

`EvolutionResult` bevat vandaag vooral vergelijkingsvelden voor gemiddelden, ratios, thema-status en tabellen, maar niet de rijke analysematen die nodig zijn voor managementduiding.

### 2. Ontbrekende interpretatielaag

In de oude workflow werd interpretatie geleverd door de prompt + Claude.  
In `CSAT-Compass` is die laag grotendeels verdwenen.

Concreet:

- `evolution_analyser.py` berekent feiten;
- `evolution_result.py` bewaart feiten;
- `evolution_exporter.py` geeft feiten door;
- `evolutie-nl.md.j2` rendert feiten;
- alleen in de conclusie is beperkte conditionele narratief aanwezig.

**Het rapport mist dus een echte interpretatielaag: tabellen zonder duiding zijn data, geen analyse.**

### 3. Ontbrekende actiegerichtheid

De referenties eindigen in:

- concrete prioriteiten,
- verwachte impact,
- timing,
- follow-up acties.

De huidige output stopt bij observatie.  
Voor managementgebruik is dat te zwak.

### Bijgestelde kernconclusie op basis van DDP-keuzes

De kloof is **niet** primair een templateprobleem.  
De kloof zit in deze keten:

```text
te dunne metrics
→ te arm result-model
→ geen volwaardige insight-laag
→ te sobere template-output
```

Op basis van de beantwoorde vragen mag daar nu nog één belangrijke verduidelijking aan worden toegevoegd:

```text
de oplossing is niet: "meer Jinja"
de oplossing is: "meer betekenisvolle analyse + aparte insight-laag + beter geordende output"
```

---

## Verbeterplan met architectuurvoorstel

### Doelarchitectuur

Respecteer de bestaande flow, maar verrijk ze inhoudelijk:

```text
EvolutionAnalyser
    ↓
EvolutionResult (verrijkte dataklassen)
    ↓
EvolutionInsightsBuilder / evolution_insights.py
    ↓
EvolutionExporter
    ↓
evolutie-nl.md.j2 / evolutie-fr.md.j2
```

### Waarom dit past bij het project

Dit sluit aan bij de huidige architectuur én bij de projectrichting in [`docs/02-tactisch/implementatie-gids.md`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/docs/02-tactisch/implementatie-gids.md), waar Fase 3a–3d expliciet als **standalone, zonder externe AI** is opgezet.

Mijn advies blijft dus:

- **geen LLM-afhankelijkheid als basisoplossing**
- eerst **regelgebaseerde interpretatie in Python**
- eventueel later een optionele AI-laag bovenop, maar niet als core

### Verwerking van DDP-keuzes

De architectuur is nu inhoudelijk aangescherpt door vier bevestigde keuzes:

1. **Aparte insight-helpermodule**
2. **Expliciete dataklassen als analysecontract**
3. **KPI-targets in config**
4. **Managementduiding als primair rapportdoel**

Daardoor verschuift Fase 3f van “inhoud TBD” naar een duidelijk kader:

- data verzamelen
- analyse structureren
- inzichten afleiden
- managementoutput renderen

---

## Detailontwerp per laag

## Laag 1 — `EvolutionAnalyser` uitbreiden

### Aan te vullen metricgroepen

#### A. Samenvattingsstatistieken

Voeg naast gemiddelden ook toe:

- mediaan score
- standaarddeviatie score
- neutraal %
- begin- en einddatum van de huidige periode
- aantal gescoorde tickets expliciet

**Waarom:** referentie A opent hiermee en het maakt de executive summary veel sterker.

#### B. Responstijd-insights

Vandaag is er enkel `response_time_by_score`.  
Voeg toe:

- gemiddelde responstijd totaal
- mediaan responstijd
- minimum / maximum
- correlatie responstijd ↔ score
- gemiddelde responstijd bij positieve scores
- gemiddelde responstijd bij negatieve scores

**Waarom:** de correlatie is in de referentie-output een van de sterkste managementinzichten.  
DDP heeft bevestigd dat deze expliciet in release 1 moet worden opgenomen.

#### C. Breakdown-verrijking per issue type en prioriteit

De huidige dataklassen bevatten score en negatief %, maar missen:

- aantal tickets
- aandeel van totaal
- standaarddeviatie
- eventueel top/bottom markering

**Waarom:** zonder volume en spreiding kun je geen robuuste interpretatie geven.

#### D. Negatieve feedback deep-dive

Voeg een kleine lijst toe met maximaal 3-5 relevante negatieve cases:

- ticket-id
- ziekenhuis
- issue type
- score
- responstijd
- geclassificeerd probleem
- korte, gesaniteerde quote

**Waarom:** DDP koos expliciet voor **gesaniteerde quotes zonder PII**.  
Dit betekent dat deze laag bewust rijker mag worden, maar alleen binnen duidelijke veiligheidsregels.

#### E. Hospital insights

Naast de exhaustieve vergelijking:

- shortlist van ziekenhuizen met minimum responsdrempel
- top/bottom movers
- benchmarks
- aandachtspunten

**Waarom:** DDP koos expliciet voor:

- **shortlist bovenaan**
- **volledige tabel daaronder**

Dat maakt de ziekenhuissectie beter bruikbaar voor management.

#### F. KPI target tracking

Voeg een aparte set toe:

- baseline
- H2 2025 benchmark
- target
- current
- status
- eventueel "op schema?"

Targets moeten volgens DDP **centraal in config/settings per pijler** beheerd worden, niet hardcoded in exporter of template.

#### G. Dubbele benchmarklogica

Voeg expliciet benchmarklagen toe voor:

- volledig 2025
- H2 2025
- current 2026

**Waarom:** deze keuze is nu bevestigd en is cruciaal om de evolutie-output beter te laten aansluiten bij de vergelijkingsmatrix.

### Pseudocode-voorbeeld

```python
@dataclass
class SummaryStats:
    total_responses: int
    avg_score: float
    median_score: float
    std_dev_score: float
    pct_positive: float
    pct_neutral: float
    pct_negative: float
    period_start: date
    period_end: date

@dataclass
class ResponseTimeInsight:
    avg_days: float
    median_days: float
    min_days: float
    max_days: float
    correlation_score: float | None
    avg_positive_days: float | None
    avg_negative_days: float | None
```

---

## Laag 2 — `EvolutionResult` verrijken

Vandaag is `EvolutionResult` vooral een transportobject voor tabellen.  
Het moet een rijker analysecontract worden.

### Aanbevolen nieuwe dataklassen

- `SummaryStats`
- `IssueTypeInsight`
- `PriorityInsight`
- `HospitalInsight`
- `NegativeCase`
- `ThemeInsight`
- `KpiTargetRow`
- `RecommendationSeed`
- `PositiveDevelopment`
- `FollowUpAction`
- `BenchmarkComparison`

### Belangrijk ontwerpprincipe

Bewaar in `EvolutionResult` **feiten en geclassificeerde signalen**, niet volledige proza.

Dus wel:

- `correlation_score = 0.118`
- `top_risk_issue_type = "Incident"`
- `negative_case_category = "gesloten_zonder_feedback"`
- `benchmark_h2_2025_delta = +0.32`

Maar niet de finale managementzin zelf.  
Die hoort thuis in de insight-/exportlaag.

### Waarom deze keuze nu extra belangrijk is

DDP koos expliciet voor:

- aparte insight-logica
- expliciete dataklassen
- testbare architectuur
- business review als acceptatiecriterium

Dat maakt een **rijk maar gestructureerd result-model** noodzakelijk.

---

## Laag 3 — regelgebaseerde interpretatie-engine

### Aanbeveling

Voeg een aparte helper toe, bijvoorbeeld:

- `src/csat/core/exporters/evolution_insights.py`

Mijn voorkeur blijft: **aparte helpermodule**.

### Waarom

De huidige template bevat al veel if/else-logica in sectie 8.  
Als je alle gewenste narratief in Jinja stopt, wordt de template te complex en moeilijk testbaar.

### Taken van deze laag

- Executive summary opbouwen
- 3-5 kritieke bevindingen selecteren
- positieve ontwikkelingen detecteren
- strategische aanbevelingen formuleren
- follow-up acties genereren
- target tracking interpreteren
- benchmarkvergelijking duiden
- caveats bij kleine steekproeven toevoegen

### Extra consequentie van DDP-keuzes

Deze helperlaag moet nu ook expliciet kunnen omgaan met:

- **dubbele benchmark** (`volledig 2025` + `H2 2025`)
- **positieve ontwikkelingen als vaste sectie**
- **theme-action-hints**
- **shortlist-logica ziekenhuizen**
- **release 1 focus op executive narrative**

### Pseudocode

```python
def build_critical_findings(result: EvolutionResult) -> list[Finding]:
    findings = []

    if result.monthly_trend.last_month_delta <= -0.2:
        findings.append(...)

    if result.response_time.correlation_score is not None:
        findings.append(...)

    if result.current_pct_negative > 8.0:
        findings.append(...)

    return findings[:5]
```

### Waarom regelgebaseerd de beste start is

- reproduceerbaar
- testbaar
- offline bruikbaar
- geen afhankelijkheid van externe API
- past bij de bestaande standalone-architectuur

---

## Laag 4 — template herontwerpen

De huidige template [`docs/templates/evolutie-nl.md.j2`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/docs/templates/evolutie-nl.md.j2) bevat 8 secties.  
Voor managementkwaliteit moet dat evolueren naar een structuur die dichter bij de referentie-output ligt.

### Aanbevolen nieuwe structuur

1. Executive Summary
2. Kritieke bevindingen
3. Kerncijfers vergelijking
4. Tijdlijn en keerpunten
5. Analyse per issue type
6. Analyse per prioriteit
7. Responstijd-analyse
8. Ziekenhuizen — shortlist
9. Ziekenhuizen — volledige tabel
10. Analyse negatieve feedback
11. Recurring themes
12. Positieve ontwikkelingen
13. KPI target tracking
14. Strategische aanbevelingen
15. Follow-up acties
16. Conclusie

### Templateprincipe

Niet alle ruwe tabellen moeten verdwijnen. Wel:

- lange exhaustieve tabellen naar onder of bijlage-logica
- bovenaan: duiding
- onderaan: detail

### Verwerking van DDP-keuzes

De template moet nu expliciet rekening houden met:

- **shortlist + volledige ziekenhuislijst**
- **vaste sectie positieve ontwikkelingen**
- **KPI target tracking**
- **dubbele benchmark in presentatie**
- **80/20-pariteit zonder 1-op-1 legacy-copy**

Belangrijk:  
De template mag rijker worden, maar mag **niet** de plaats worden waar de interpretatie zelf leeft.

---

## Implementatievolgorde

| Fase | Inhoud | Afhankelijkheden | Omvang |
| --- | --- | --- | --- |
| 1 | Metric-semantieken harmoniseren (responses vs tickets, perioden, targets, H2 benchmark) | Geen | S |
| 2 | `EvolutionAnalyser` + `EvolutionResult` verrijken met summary, correlation, counts, cases, benchmarkdata | Fase 1 | M |
| 3 | Rule-based insight builder toevoegen | Fase 2 | M |
| 4 | `EvolutionExporter` context uitbreiden + NL-template herwerken | Fase 3 | M |
| 5 | FR-template en i18n gelijk trekken | Fase 4 | S |
| 6 | Tests uitbreiden: analyser + exporter snapshots/keyword assertions | Fase 2-5 | M |
| 7 | Valideren tegen referentie-output + business review | Fase 6 | S |

### Praktische prioriteit — aangepast aan DDP-keuzes

Voor release 1 is de juiste volgorde:

1. **correlation**
2. **executive summary**
3. **kritieke bevindingen**
4. **positieve ontwikkelingen**
5. **aanbevelingen + follow-up**
6. **benchmarking + shortlist ziekenhuis**
7. **thema-verdieping met voorbeelden en actiehint**

Dat is de beste 80/20-volgorde.

---

## Ontwerpkeuzes en bedenkingen

### 1. Regelgebaseerd vs LLM

**Definitief advies:** regelgebaseerd als default.

**Waarom:**

- consistent
- testbaar
- veilig
- passend bij huidige projectarchitectuur
- in lijn met DDP-keuze

**Wanneer eventueel LLM later?**

- alleen als optionele verrijking voor vrije tekstsamenvattingen
- nooit voor kernberekeningen of kritieke KPI-conclusies
- niet als basis voor release 1

### 2. Kunnen we met GHC LLM-gedreven gaan werken?

**Antwoord:** ja, technisch kan dat. Maar niet als aanbevolen basisarchitectuur voor deze fase.

#### Wat technisch mogelijk is

Met GHC kan in principe een LLM-laag worden toegevoegd via:

- API-integratie
- optionele enrichment-stap
- externe modelprompting op basis van `EvolutionResult`
- post-processing van managementnarratief

#### Waarom ik het nu niet aanraad als fundament

- Fase 3a–3d zijn bewust opgebouwd als standalone traject zonder externe AI
- Fase 3f moet eerst de inhoudelijke kloof dichten, niet de systeemarchitectuur omgooien
- LLM-output is minder stabiel testbaar
- governance, kosten en reproduceerbaarheid worden complexer
- de gekozen release-1 scope is perfect haalbaar zonder LLM

#### Definitieve aanbeveling

```text
Release 1 = rule-based als kern
Later mogelijk = optionele LLM-verrijking als bijkomende laag
```

### 3. Exhaustieve tabel vs managementfocus

De huidige ziekenhuistabel is volledig, maar niet prioritair leesbaar.

DDP koos hier expliciet voor de juiste hybride oplossing:

- bovenaan: shortlist "benchmark / stabiel / aandacht"
- onderaan: volledige tabel

Dat is inhoudelijk sterk en praktisch verdedigbaar.

### 4. Gebruik van commentquotes

De referenties gebruiken letterlijke klantquotes. Dat maakt rapporten sterk, maar let op projectregels:

- geen PII
- geen medewerker-namen
- sanitizen waar nodig

DDP koos expliciet voor:

- korte quotes
- gesaniteerd
- zonder namen

Dat betekent concreet:

- maximaal 3-5 quotes
- alleen functioneel relevante fragmenten
- liefst beperkt in lengte
- nooit onbewerkte rauwe comment dumps

### 5. Target tracking

De oude matrix toont targets.  
De huidige evolutie-output werkt vooral met thresholds. Dat is niet hetzelfde.

**Threshold** = technisch minimum  
**Target** = managementdoel

DDP koos expliciet voor targetbeheer in config/settings per pijler.  
Dat is de juiste oplossing.

### 6. Overlap met matrix

De matrix-template [`docs/templates/matrix-nl.md.j2`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/docs/templates/matrix-nl.md.j2) is sterk in vergelijking over periodes, rankings en benchmarkweergave.

Het evolutierapport moet daarom niet nog eens een volledige matrix imiteren.  
Het moet eerder:

- veranderingen verklaren,
- risico's benoemen,
- acties aanbevelen.

Deze keuze is nu expliciet bevestigd en moet architecturaal bewaakt blijven.

---

## 80/20-check

Met onderstaande verbeteringen haal je waarschijnlijk het grootste deel van de managementwaarde:

1. **Executive Summary met kernboodschap**
2. **Kritieke bevindingen-sectie**
3. **Responstijd-correlatie + positief/negatief vergelijking**
4. **Negatieve feedback deep-dive met gesaniteerde cases**
5. **Positieve ontwikkelingen als vaste sectie**
6. **Strategische aanbevelingen met prioriteit/tijdlijn**
7. **Follow-up actielijst per horizon**
8. **Dubbele benchmark 2025 + H2 2025**
9. **Shortlist ziekenhuizen boven volledige tabel**
10. **Recurring themes met voorbeeld en actiehint**

### Laaghangend fruit metrics

Deze zijn relatief goedkoop en leveren veel meerwaarde:

- mediaan score
- standaarddeviatie
- neutraal %
- correlation score
- counts per issue type/prioriteit
- top 3 negatieve cases
- maand-op-maand delta laatste maand
- minimum responsdrempel voor ziekenhuisduiding
- H2 2025 benchmarkdelta

### Wat later kan

- uitgebreide positieve quotes
- geavanceerde benchmark engines
- semantische classificatie van comments
- optionele LLM-verrijking

---

## Risico's en mitigatie

| Risico | Impact | Mitigatie |
| --- | --- | --- |
| Apples-vs-oranges vergelijking met legacy outputs | Hoog | Eerst definities harmoniseren: responses, tickets, periodes, filters |
| Te veel logica in Jinja-template | Hoog | Interpretatie naar aparte Python helper verplaatsen |
| Rapport wordt te lang en verliest focus | Medium | Management-first structuur, detailtabellen lager plaatsen |
| Pharma-specifieke regels lekken naar andere pijlers | Hoog | Pijlerneutrale dataklassen + configureerbare thresholds/targets |
| NL/FR drift | Hoog | NL eerst, daarna FR, i18n-sleutels centraal |
| Gebruik van rauwe commentquotes met PII | Hoog | Sanitizing en quote-policy invoeren |
| Reproduceerbaarheid van narratief | Medium | Rule-based regels en testbare templates |
| Dubbele benchmark verhoogt complexiteit | Medium | Benchmarkmodellering expliciet en gescheiden houden |
| Scope creep in release 1 | Hoog | Strikt vasthouden aan gekozen executive scope |

---

## Bijgestelde acceptatiecriteria

Release 1 is pas “goed genoeg” als aan **alle** onderstaande voorwaarden voldaan is:

### Inhoudelijk

- er is een volwaardige executive summary
- er zijn kritieke bevindingen met duiding
- correlation is zichtbaar en geïnterpreteerd
- positieve ontwikkelingen zijn expliciet opgenomen
- recurring themes bevatten voorbeelden en actiehints
- aanbevelingen en follow-up acties zijn aanwezig
- dubbele benchmark is inhoudelijk zichtbaar

### Architecturaal

- inzichtlogica zit in aparte helperlaag
- `EvolutionResult` is verrijkt met expliciete structuren
- KPI-targets zitten in config/settings
- template is rijker, maar niet de primaire interpretatielaag

### Validatie

- unit tests slagen
- keyword/snapshot asserts dekken nieuwe output
- Danny kan de output inhoudelijk vergelijken met referentie A/B en bevestigen dat het rapport managementwaardig leest

---

## Samenvatting

De huidige evolutie-output van `CSAT-Compass` is **technisch degelijk, maar inhoudelijk nog geen managementrapport**.  
De kern van de kloof is niet dat de data fout zou zijn, maar dat de output nog te veel stopt bij tabellen en te weinig doet aan:

- interpretatie
- prioritering
- causaliteit
- benchmarkduiding
- actiegerichtheid

Op basis van de verwerkte DDP-antwoorden is het advies nu scherper en definitiever geworden.

### De snelste route naar referentiekwaliteit is

1. `EvolutionAnalyser` verrijken met ontbrekende metrics én benchmarklogica  
2. `EvolutionResult` uitbreiden met rijkere analyse-objecten  
3. een **aparte regelgebaseerde insight builder** toevoegen  
4. de template herstructureren naar executive summary → bevindingen → analyse → aanbevelingen → follow-up  
5. de matrixrol zuiver houden als benchmarkreferentie  
6. LLM voorlopig **niet** als basisarchitectuur invoeren

### Mijn finaal hoofdadvies

Voer Fase 3f niet op als louter "template polish", maar als een gerichte uitbreiding van:

- **metrics**
- **benchmarking**
- **insights**
- **template-ordening**

Als je dat doet, kan `CSAT-Compass` de kloof met de oude Claude-output grotendeels dichten zonder zijn deterministische, offline bruikbare en testbare architectuur te verliezen.

### Eindoordeel in één zin

**Fase 3f moet release 1 van het evolutierapport transformeren van een degelijke vergelijkingstabel naar een managementwaardig duidingsrapport, op basis van rule-based insights, expliciete datamodellen, dubbele benchmarklogica en een strikt bewaakte 80/20-scope.**
