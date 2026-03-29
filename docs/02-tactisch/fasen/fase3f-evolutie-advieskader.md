# CSAT-Compass — Fase 3f: Evolutie-advieskader

> **Versie:** 3.0 — 29/03/2026
> **Status:** Definitief advieskader — bevestigde beslissingen DDP
> **Doel:** Normatief besliskader voor Fase 3g (implementatie evolutierapport verfijning)
> **Auteur:** Danny Depecker + Claude Desktop + GHC (samengevoegd)
> **Bestandsnaam:** `fase3f-evolutie-advieskader.md`
> **Path:** `docs/02-tactisch/fasen/`
>
> Dit document is de **single source of truth** voor alle implementatiebeslissingen in fase 3g.
> Het combineert het CD-advies (v2.0, alle 12 DDP-beslissingen correct verwerkt) met
> nuttige structuurtoevoegingen uit het GHC-advies (v2.0).

---

## Beslissingenregister

Onderstaande beslissingen zijn bevestigd op 27/03/2026 en vormen het kader voor dit verbeterplan.

| # | Vraag | Beslissing |
| --- | --- | --- |
| 1 | Interpretatie-engine aanpak | **A — Regelgebaseerd in Python**, zo dicht mogelijk bij referentiekwaliteit |
| 2 | Klantcomments citeren | **A — Volledig**, net zoals in referentie A |
| 3 | Ticket-ID's in rapport | **A — Zichtbaar** met ticket-ID + ziekenhuis + comment |
| 4 | Scope eerste versie | **B — Kern eerst**: Executive Summary + Keerpunt-analyse + Aanbevelingen + Conclusie |
| 5 | KPI-targets | **A — Uitgebreid**: 7 targets uit settings + referentie A/B |
| 6 | Implementatietool | **A — GHC via gestructureerde prompts**, Claude levert de prompts |
| 7 | Maandrapport mee verbeteren | **A — Parallel**, InsightsGenerator hergebruiken |
| 8 | Visualisaties meenemen | **A — Visuele Analyse sectie** met beschrijving per subplot |
| 9 | Aanbevelingen-engine | **A — Zeer specifiek** met impact, tijdlijn en eigenaar |
| 10 | Validatie | **A — Vergelijk output C-nieuw naast referentie A/B**, checklist per sectie |
| 11 | Vergelijkingsmatrix positionering | **A — Integreer output B's inhoud** in het evolutierapport |
| 12 | Scoreverdeling presentatie | **A — Compacte rij** in kerncijfertabel + inline tekst in Executive Summary |

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
- [`docs/templates/rapport-nl.md.j2`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/docs/templates/rapport-nl.md.j2)
- [`src/csat/i18n/nl.json`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/src/csat/i18n/nl.json)
- [`src/csat/config/pillars.py`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/src/csat/config/pillars.py)
- [`src/csat/config/settings.py`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/src/csat/config/settings.py)

---

## Positionering t.o.v. andere rapporttypes

De evolutie-output in CSAT-Compass zit vandaag inhoudelijk tussen twee oude rapportvormen in:

- het **tendensrapport** levert managementduiding, cases, aanbevelingen en follow-up;
- de **vergelijkingsmatrix** levert benchmark- en targettracking over meerdere referentiekaders;
- het huidige **evolutierapport** levert vooral deterministische tabellen en een korte conclusie.

Dat betekent: de huidige evolutie-output is **sterk als data-export**, maar **zwak als managementrapport**.

**Beslissing 11:** De inhoud van de vergelijkingsmatrix (output B) wordt geïntegreerd in het verbeterde evolutierapport. De MatrixExporter hoeft niet apart verbeterd te worden — het evolutierapport wordt het primaire managementrapport dat zowel duidt als benchmarkt.

**Beslissing 7:** Het maandrapport (`rapport-nl.md.j2`) wordt parallel meegenomen. De `InsightsGenerator` wordt zo ontworpen dat zowel het evolutierapport als het maandrapport er gebruik van maken.

---

## Gap-analyse per rapportsectie

| Sectie | Referentie-output | Huidig | Gap-niveau |
| --- | --- | --- | --- |
| Rapportkader / metadata | Referentie noemt periode, organisatie, project, product, rapportagedatum expliciet | Huidig toont enkel titel + baseline/current labels | MEDIUM |
| Executive Summary | Referentie A start met kerncijfers + expliciete kernboodschap | Huidig start met een KPI-tabel zonder managementsamenvatting | KRITIEK |
| Kritieke bevindingen | Referentie A bevat 4 uitgewerkte bevindingen met causaliteit en ernst | Huidig heeft geen aparte bevindingensectie | KRITIEK |
| Kerncijfers vergelijking | Beide tonen baseline vs huidig; referentie voegt mediaan, std dev, neutraal %, periode en interpretatie toe | Huidig toont avg, pos/neg, HC-ratio, responstijd, # ziekenhuizen | MEDIUM |
| Scoreverdeling | Referentie A toont verdeling per score-niveau met aandeel | Huidig toont alleen gemiddelde + % positief/negatief | HOOG |
| Tijdlijn / trendduiding | Referentie B benoemt dieptepunten, doorbraak, topmaanden, fase-overgangen | Huidig toont maandtabel, maar geen status of keerpuntanalyse | HOOG |
| Analyse per issue type | Referentie geeft aantal, gemiddelde, std dev, aandeel en interpretatie | Huidig toont enkel gemiddelde en % negatief | HOOG |
| Analyse per prioriteit | Referentie geeft aantal, gemiddelde, std dev en interpretatie | Huidig toont gemiddelde en delta, geen volume of duiding | HOOG |
| Responstijd-analyse | Referentie A/B bevat gemiddelde, mediaan, min/max, correlatie en positief-vs-negatief vergelijking | Huidig toont alleen responstijd per score-niveau | KRITIEK |
| Ziekenhuisanalyse | Referentie filtert relevante cases, geeft statuslabels en interpretatie | Huidig toont lange tabel met delta's, weinig prioritering | MEDIUM |
| Verdwenen / nieuwe ziekenhuizen | Huidig detecteert dit correct en expliciet | Referentie heeft minder systematische detectie | LAAG |
| Analyse negatieve feedback | Referentie A bevat ticketcases met ID + ziekenhuis + comment, probleemclassificatie, recurring themes en voorbeelden | Huidig toont enkel thema-percentages via keyword matching | KRITIEK |
| Thema-evolutie | Referentie B toont opgelost / nog aanwezig / nieuw thema | Huidig doet dit ook, maar veel soberder en zonder voorbeelden | MEDIUM |
| KPI target tracking | Referentie B koppelt baseline, target 2026, realisatie en status | Huidig heeft alleen KPI-status o.b.v. thresholds | HOOG |
| Positieve ontwikkelingen | Referentie A benoemt expliciet wat goed gaat | Huidig doet dit bijna niet apart | MEDIUM |
| Visuele analyse | Referentie A beschrijft elke grafiek met narratief | Huidig heeft geen tekstuele duiding bij de PNG | HOOG |
| Strategische aanbevelingen | Referentie A geeft 6 geprioriteerde acties met impact, tijdlijn en eigenaar | Huidig heeft slechts 2-4 generieke conclusieblokken | KRITIEK |
| Follow-up acties | Referentie A sluit af met checklist per tijdshorizon | Huidig bevat geen actieplan | KRITIEK |
| Totaalbeoordeling / structureel vs tijdelijk | Referentie B onderbouwt dat via criteria-matrix | Huidig noemt "structureel/gemengd" met beperkte bewijsvoering | MEDIUM |

### Wat nu al goed is

Het huidige evolutierapport heeft wel degelijk sterke fundamenten:

- de vergelijking baseline vs huidig is consistent opgebouwd;
- `EvolutionAnalyser` berekent al bruikbare kernmetingen zoals avg score, pos/neg %, HC-ratio, responstijd, hospitals en negatieve thema's;
- `EvolutionExporter` en `evolutie-nl.md.j2` leveren een stabiele, reproduceerbare structuur;
- de detectie van verdwenen en nieuwe ziekenhuizen is waardevol;
- de conclusie bevat al eerste rule-based narratieve logica.

Met andere woorden: **de datafundering is niet slecht**. De kloof zit vooral in **informatiedichtheid, interpretatie en actiegerichtheid**.

---

## Kernprobleem-diagnose

De fundamentele oorzaak van het kwaliteitsverschil zit op **drie niveaus tegelijk**.

### 1. Ontbrekende metrics

De referentie-output gebruikt managementrelevante maten die vandaag niet in `EvolutionResult` zitten, zoals:

- mediaan score
- standaarddeviatie
- neutraal %
- scoreverdeling per niveau (5★ t/m 1★ met aandeel)
- responstijd-correlatie
- min/max/mediaan responstijd
- counts per issue type/prioriteit
- aandeel per issue type
- ticket-level negatieve cases (met ID, ziekenhuis, comment)
- target tracking (7 KPI's)
- kwalitatieve recurring themes met voorbeelden

`EvolutionResult` bevat vandaag vooral vergelijkingsvelden voor gemiddelden, ratios, thema-status en tabellen, maar niet de rijke analysematen die nodig zijn voor managementduiding.

### 2. Ontbrekende interpretatielaag

In de oude workflow werd interpretatie geleverd door de prompt + Claude.
In CSAT-Compass is die laag grotendeels verdwenen.

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
- eigenaar per actie,
- follow-up acties per tijdshorizon.

De huidige output stopt bij observatie. Voor managementgebruik is dat te zwak.

### Kernconclusie

De kloof is **niet** primair een templateprobleem.
De kloof zit in deze keten:

```text
te dunne metrics
→ te arm result-model
→ geen volwaardige insight-laag
→ te sobere template-output
```

---

## Regelgebaseerd vs LLM — haalbaarheid

**Beslissing 1:** Volledig regelgebaseerd in Python — de Claude API is niet beschikbaar.

### Kan regelgebaseerd de referentiekwaliteit evenaren?

Dit is geen utopie, maar vergt wel een **andere soort investering** dan een LLM-oplossing. Niet in complexe NLP, maar in goed ontworpen templatezinnen en compositielogica.

### Waar zit het verschil precies?

De referentie-output (tendens_2026_03_03.md) leest vloeiend omdat Claude drie dingen doet die regelgebaseerde code niet vanzelf doet:

**1. Verbindende zinnen** — Claude schrijft "Hoewel de gemiddelde score licht daalde, blijft het positieve percentage stabiel, wat suggereert dat..." Een regelgebaseerd systeem genereert standaard losse constaterende zinnen: "De score daalde van 4,50 naar 4,43. Het positieve percentage bleef stabiel op 83,3%."

**2. Contextuele nuancering** — Claude kiest woordkeuze op basis van ernst. Bij een daling van 0,07 schrijft het "lichte terugval", bij 0,40 "significante daling". Een regelgebaseerd systeem moet die drempels expliciet definiëren.

**3. Adhoc-observaties** — Claude merkt soms iets op dat geen voorgedefinieerde regel voorziet, bv. "Opvallend is dat drie van de vijf negatieve scores uit dezelfde maand komen."

De eerste twee zijn **volledig oplosbaar** met regelgebaseerde code. De derde is de enige echte beperking, en die is kleiner dan verwacht.

### Oplossing 1 — Compositiepatronen in plaats van vaste strings

Het verschil tussen mechanische en vloeiende output zit niet in AI, maar in hoe je zinnen opbouwt:

```python
# ❌ Mechanisch — één vaste string per conditie
if delta < 0:
    text = f"De score daalde van {baseline} naar {current}."

# ✅ Compositiepatroon — fragmenten combineren
def build_score_observation(baseline, current, delta, pct_positive):
    severity = classify_severity(delta)  # "licht" | "matig" | "significant"
    direction = "daalde" if delta < 0 else "steeg"
    
    # Hoofdzin met ernst-afhankelijke woordkeuze
    main = TEMPLATES[severity]["score_change"].format(
        direction=direction, baseline=baseline, current=current
    )
    
    # Optionele nuancering op basis van context
    if abs(delta) < 0.1 and pct_positive > 80:
        nuance = random.choice([
            f"Het positieve percentage van {pct_positive}% relativeert deze beweging.",
            f"Bij {pct_positive}% positieve scores is dit een beperkte verschuiving.",
        ])
    else:
        nuance = ""
    
    return f"{main} {nuance}".strip()
```

Met dit patroon krijg je output als: *"De gemiddelde score kende een lichte terugval van 4,50 naar 4,43. Het positieve percentage van 83,3% relativeert deze beweging."*

Dat is functioneel gelijkwaardig aan wat Claude schrijft.

### Oplossing 2 — Ernst-afhankelijke woordkeuze via drempeltabellen

```python
SEVERITY_WORDS = {
    "score_decline": {
        "licht":       {"verb": "kende een lichte terugval", "adj": "beperkte"},
        "matig":       {"verb": "daalde merkbaar",           "adj": "noemenswaardige"},
        "significant": {"verb": "daalde significant",        "adj": "zorgwekkende"},
    },
    "response_time": {
        "licht":       {"verb": "nam licht toe",             "adj": "marginale"},
        "matig":       {"verb": "liep op",                   "adj": "aanzienlijke"},
        "significant": {"verb": "liep sterk op",             "adj": "alarmerende"},
    },
}

def classify_severity(delta: float, thresholds: tuple = (0.1, 0.3)) -> str:
    """Classificeer de ernst van een afwijking."""
    abs_delta = abs(delta)
    if abs_delta < thresholds[0]:
        return "licht"
    elif abs_delta < thresholds[1]:
        return "matig"
    return "significant"
```

Dit is exact wat Claude impliciet doet — het kiest woorden op basis van de grootte van de afwijking. Het enige verschil is dat de drempels expliciet gedefinieerd worden. Dat is tegelijk een **voordeel**: de output is reproduceerbaar en testbaar.

### Oplossing 3 — Verbindende zinnen via connectors

```python
CONNECTORS = {
    "contrast":    ["Hoewel", "Ondanks", "Tegelijkertijd"],
    "causal":      ["Dit suggereert dat", "Een mogelijke verklaring is",
                    "Dit hangt samen met"],
    "reinforcing": ["Dit wordt bevestigd door", "In lijn hiermee", "Bovendien"],
    "concluding":  ["Samenvattend", "De kernboodschap is", "Dit betekent concreet"],
}

def connect_observations(obs1: str, obs2: str, relation: str) -> str:
    """Verbind twee observaties met een contextuele connector."""
    connector = random.choice(CONNECTORS[relation])
    return f"{obs1} {connector} {obs2[0].lower() + obs2[1:]}"
```

### Wat niet haalbaar is (en waarom dat oké is)

De enige echte beperking is de **adhoc-observatie**: een LLM kan onverwachte patronen opmerken die geen regel voorziet. Maar in de praktijk is dit minder relevant dan het lijkt:

- De referentie-output bevat ~20-25 inhoudelijke observaties per rapport
- Daarvan zijn er ~18-20 afleidbaar uit voorgedefinieerde regels (score daalt, correlatie, HC-ratio stijgt, etc.)
- Slechts 2-3 zijn echt "vrije" observaties

Die 2-3 vrije observaties zijn deels op te vangen door **meer regels** te definiëren dan nu voorzien — bv. "als 3+ negatieve scores uit dezelfde maand komen, meld dat" of "als één ziekenhuis >50% van de negatieve scores levert, benoem dat."

### Verwacht resultaat

| Aspect | LLM-output | Regelgebaseerd (goed ontworpen) | Gap |
| --- | --- | --- | --- |
| Cijfers, KPI's, tabellen | 100% | 100% | Geen |
| Structurele secties (summary, bevindingen) | 100% | 95% | Minimaal |
| Ernst-afhankelijke woordkeuze | Impliciet | Expliciet via drempels | Geen (zelfs beter: reproduceerbaar) |
| Verbindende proza | Vloeiend | Goed, soms iets formulairder | Klein |
| Adhoc-observaties | Sterk | Beperkt tot voorgedefinieerde regels | Reëel maar klein |
| Reproduceerbaarheid | Zwak (niet-deterministisch) | Perfect | Voordeel regelgebaseerd |
| Testbaarheid | Moeilijk | Volledig | Voordeel regelgebaseerd |

**Inschatting: 85-90% van de referentiekwaliteit is haalbaar.** De resterende 10-15% is het verschil tussen "goed geschreven rapport" en "alsof een senior analist het met de hand geschreven heeft." Voor een CS board is dat verschil verwaarloosbaar.

### Concrete investering

De investering zit in drie bouwblokken voor de `InsightsGenerator`:

1. **Zinsvariatie-bibliotheek** in `nl.json` / `fr.json` — 2-3 alternatieven per regeltype, zodat het rapport niet telkens dezelfde openingszin hergebruikt
2. **Ernst-drempeltabellen** — eenmalig definiëren per metrictype (score, responstijd, HC-ratio, etc.), daarna herbruikbaar voor alle secties
3. **Connector-logica** — een kleine hulpfunctie die observaties verbindt op basis van hun onderlinge relatie (contrast, causaal, versterkend)

Geschatte omvang: 200-300 regels code in de `InsightsGenerator`. Geen raketwetenschap, maar het maakt het verschil tussen "data-export" en "rapport."

---

## Verbeterplan met architectuurvoorstel

### Doelarchitectuur

Respecteer de bestaande flow, maar verrijk ze inhoudelijk:

```text
EvolutionAnalyser / MonthlyAnalyser
    ↓
EvolutionResult / MonthlyResult (verrijkte dataklassen)
    ↓
InsightsGenerator (regelgebaseerde interpretatie — gedeeld)
    ↓
EvolutionExporter / MonthlyExporter
    ↓
evolutie-nl.md.j2 / rapport-nl.md.j2 (+ FR-varianten)
```

### Waarom dit past bij het project

Dit sluit aan bij de huidige architectuur én bij de projectrichting in [`docs/02-tactisch/implementatie-gids.md`](file:///C:/Users/danndepe/Documents/AI/CSAT-Compass/docs/02-tactisch/implementatie-gids.md), waar Fase 3a–3d expliciet als **standalone, zonder externe AI** is opgezet.

**Beslissing 7** verankerd: de `InsightsGenerator` wordt gedeeld tussen evolutie- en maandrapport. Gedeelde logica omvat executive summary-opbouw, bevindingenselectie, aanbevelingenformulering en KPI-tracking. Rapporttype-specifieke logica (bv. keerpuntanalyse alleen in evolutie) zit in aparte methoden.

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

#### B. Scoreverdeling

**Beslissing 12:** Compacte rij in kerncijfertabel + inline tekst in Executive Summary.

Voeg toe:

- aantal tickets per score (1-5)
- percentage per score
- presentatieformaat: `5★:30 (62,5%) | 4★:10 (20,8%) | 3★:2 (4,2%) | 2★:1 (2,1%) | 1★:3 (6,3%)`
- narratieve samenvatting: *"Van de 48 responses scoort 62,5% een volle 5★"*

**Waarom:** de verdeling vertelt meer dan alleen het gemiddelde — een 4,2 met 60% vijven en enkele uitschieters is fundamenteel anders dan een 4,2 met een gelijkmatige spreiding.

#### C. Responstijd-insights

Vandaag is er enkel `response_time_by_score`.
Voeg toe:

- gemiddelde responstijd totaal
- mediaan responstijd
- minimum / maximum
- correlatie responstijd ↔ score
- gemiddelde responstijd bij positieve scores
- gemiddelde responstijd bij negatieve scores

**Waarom:** de correlatie `r = +0,118` is in de referentie-output een van de sterkste managementinzichten. Deze ontbreekt nu volledig.

#### D. Breakdown-verrijking per issue type en prioriteit

De huidige dataklassen bevatten score en negatief %, maar missen:

- aantal tickets
- aandeel van totaal
- standaarddeviatie
- eventueel top/bottom markering

**Waarom:** zonder volume en spreiding kun je geen robuuste interpretatie geven.

#### E. Negatieve feedback deep-dive

**Beslissingen 2 + 3:** Volledige klantcomments en ticket-ID's worden opgenomen.

Voeg een lijst toe met de meest relevante negatieve cases:

- ticket-ID (bv. SD30-36770)
- ziekenhuis
- issue type
- score
- responstijd
- geclassificeerd probleem
- volledige comment uit V_CSAT_1

Geen limiet op quotelengte, geen anonimisering van ziekenhuisnamen. De enige sanitizing betreft eventuele medewerker-namen van ZORGI-personeel in de comments.

**Waarom:** de referentie-output is sterk juist omdat ze cijfers koppelt aan concrete, herkenbare gevallen. Het CS board kent de ziekenhuizen en wil weten welk ticket bij welk ziekenhuis hoort.

#### F. Hospital insights

Naast de exhaustieve vergelijking:

- shortlist van ziekenhuizen met minimum responsdrempel
- top/bottom movers
- benchmarks
- aandachtspunten

**Waarom:** management wil niet 40 rijen lezen; het wil weten waar het echt schuurt.

#### G. KPI target tracking

**Beslissing 5:** 7 targets worden geconfigureerd.

| KPI | Target | Bron |
| --- | --- | --- |
| `avg_score_min` | ≥ 4,00 | Reeds in `settings.py` |
| `high_critical_max` | ≤ 15,0% | Reeds in `settings.py` |
| `pct_positive_min` | ≥ 75% | Nieuw — uit referentie A/B |
| `pct_negative_max` | ≤ 15% | Nieuw — uit referentie A/B |
| `avg_response_days_max` | ≤ 10,0 dagen | Nieuw — uit referentie A/B |
| `pct_with_comment_min` | ≥ 40% | Nieuw — klantbetrokkenheid (ref B: 19,1% → 43,8%) |
| `hospital_retention_min` | ≥ 50% | Nieuw — minimum retentie baseline-ziekenhuizen |

Deze targets worden opgenomen in `settings.py` (of een apart `targets.py`-configbestand) en zijn per pijler overschrijfbaar.

#### H. Visuele analyse

**Beslissing 8:** Een "Visuele Analyse" sectie wordt toegevoegd met beschrijvende tekst per subplot.

De `InsightsGenerator` genereert een beschrijving per subplot van de `evolution_visualiser.py`-output op basis van de beschikbare data:

- Subplot 1 (scoretrend): narratief over dalende/stijgende lijn, keerpunten
- Subplot 2 (maandvolume): narratief over responsaantallen, pieken
- Subplot 3 (prioriteitscompositie): narratief over verschuivingen in HC-ratio
- Subplot 4 (ziekenhuisbenchmark): narratief over top/bottom performers

Het template refereert naar het bestandspad van de gegenereerde PNG.

#### I. Dubbele benchmarklogica

*Bron: GHC-advies — nuttige structuurtoevoeging.*

Voeg expliciet benchmarklagen toe voor:

- volledig 2025 (baseline)
- H2 2025 (verfijnde benchmark)
- current 2026 (huidige periode)

De dubbele benchmark maakt het mogelijk om te onderscheiden of een verschuiving al in H2 2025 begon of pas in 2026. Dit sluit aan bij de keerpuntanalyse in de tijdlijnsectie.

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
class ScoreDistribution:
    """Verdeling per scoreniveau 1-5."""
    counts: dict[int, int]      # {5: 30, 4: 10, 3: 2, 2: 1, 1: 3}
    percentages: dict[int, float]
    compact_label: str          # "5★:30 (62,5%) | 4★:10 (20,8%) | ..."
    narrative: str              # "Van de 48 responses scoort 62,5% een volle 5★"

@dataclass
class ResponseTimeInsight:
    avg_days: float
    median_days: float
    min_days: float
    max_days: float
    correlation_score: float | None
    avg_positive_days: float | None
    avg_negative_days: float | None

@dataclass
class NegativeCase:
    ticket_id: str              # "SD30-36770"
    hospital: str               # volledige naam
    issue_type: str
    score: int
    response_days: float | None
    category: str               # geclassificeerd probleem
    comment: str                # volledige quote uit V_CSAT_1

@dataclass
class KpiTarget:
    name: str
    baseline: float
    target: float
    current: float
    status: str                 # "op_schema" | "aandacht" | "kritiek"
    on_track: bool
```

---

## Laag 2 — `EvolutionResult` verrijken

Vandaag is `EvolutionResult` vooral een transportobject voor tabellen.
Het moet een rijker analysecontract worden.

### Aanbevolen nieuwe dataklassen

- `SummaryStats`
- `ScoreDistribution`
- `ResponseTimeInsight`
- `IssueTypeInsight`
- `PriorityInsight`
- `HospitalInsight`
- `NegativeCase`
- `ThemeInsight`
- `KpiTarget`
- `RecommendationSeed`
- `VisualAnalysis`
- `BenchmarkComparison` *(GHC-verrijking — voor dubbele benchmark: 2025 / H2 2025 / current)*
- `PositiveDevelopment` *(GHC-verrijking — voor vaste sectie positieve ontwikkelingen)*
- `FollowUpAction` *(GHC-verrijking — voor gestructureerde follow-up acties)*

### Belangrijk ontwerpprincipe

Bewaar in `EvolutionResult` **feiten en geclassificeerde signalen**, niet volledige proza.

Dus wel:

- `correlation_score = 0.118`
- `top_risk_issue_type = "Incident"`
- `negative_case_category = "gesloten_zonder_feedback"`
- `score_distribution.compact_label = "5★:30 (62,5%) | ..."`

Maar niet de finale narratieve zin zelf. Die hoort thuis in de `InsightsGenerator`.

---

## Laag 3 — regelgebaseerde interpretatie-engine

### Aanbeveling

Aparte helpermodule: `src/csat/core/insights/insights_generator.py`

**Beslissing 7** verankerd: deze module wordt gedeeld tussen evolutie- en maandrapport. De klasse ontvangt een `EvolutionResult` of `MonthlyResult` en produceert een `InsightsBundle` met alle narratieve secties.

### Waarom aparte module

De huidige template bevat al veel if/else-logica in sectie 8. Als je alle gewenste narratief in Jinja stopt, wordt de template te complex en moeilijk testbaar.

### Taken van deze laag

- Executive summary opbouwen (met scoreverdeling-narratief)
- 3-5 kritieke bevindingen selecteren
- positieve ontwikkelingen detecteren
- visuele analyse-beschrijvingen genereren per subplot
- strategische aanbevelingen formuleren met **impact, tijdlijn en eigenaar** (beslissing 9)
- follow-up acties genereren per tijdshorizon
- target tracking interpreteren (7 KPI's)
- keerpuntanalyse voor tijdlijn
- caveats bij kleine steekproeven toevoegen

### Aanbevelingen-engine detail

**Beslissing 9:** Zeer specifieke aanbevelingen.

Elke gegenereerde aanbeveling bevat:

- **titel** — korte actienaam
- **beschrijving** — wat en waarom
- **verwachte impact** — kwantitatief waar mogelijk (bv. "verwachte scoreverbetering +0,15")
- **tijdlijn** — korte/middellange/lange termijn
- **eigenaar** — Service Manager / Team Lead / specifieke rol
- **prioriteit** — hoog/midden/laag

De regels voor aanbevelingengeneratie worden afgeleid uit de data:

- correlatie responstijd → aanbeveling over responstijd
- hoge HC-ratio → aanbeveling over prioriteitsmanagement
- dalende maandtrend → aanbeveling over interventie
- specifieke negatieve cases → aanbeveling over klantspecifiek herstel

### Pseudocode

```python
@dataclass
class Recommendation:
    title: str
    description: str
    expected_impact: str
    timeline: str              # "kort" | "middellang" | "lang"
    owner: str                 # "Service Manager" | "Team Lead" | ...
    priority: str              # "hoog" | "midden" | "laag"

def build_recommendations(result: EvolutionResult) -> list[Recommendation]:
    recs = []
    if result.response_time.correlation_score and result.response_time.correlation_score > 0.1:
        recs.append(Recommendation(
            title="Responstijd optimaliseren",
            description="Positieve correlatie tussen responstijd en score ...",
            expected_impact="Verwachte scoreverbetering +0,10 bij halvering responstijd",
            timeline="kort",
            owner="Service Manager",
            priority="hoog",
        ))
    # ... meer regels
    return sorted(recs, key=lambda r: {"hoog": 0, "midden": 1, "laag": 2}[r.priority])

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

### Zinsvariatie-strategie

Om mechanisch klinkende output te voorkomen, worden de drie bouwblokken uit de haalbaarheidsanalyse hier verankerd in het ontwerp van de `InsightsGenerator`:

#### Bouwblok 1 — Zinsvariatie-bibliotheek in i18n

Alle narratieve fragmenten worden opgeslagen in `nl.json` / `fr.json` als arrays met 2-3 alternatieven:

```json
{
  "insights": {
    "score_decline": {
      "licht": [
        "De gemiddelde score kende een lichte terugval van {baseline} naar {current}.",
        "Met een verschuiving van {baseline} naar {current} blijft de daling beperkt.",
        "De score bewoog licht neerwaarts: van {baseline} naar {current}."
      ],
      "matig": [
        "De gemiddelde score daalde merkbaar van {baseline} naar {current}.",
        "Een noemenswaardige daling: de score zakte van {baseline} naar {current}."
      ],
      "significant": [
        "De gemiddelde score daalde significant van {baseline} naar {current}.",
        "Een zorgwekkende terugval: de score ging van {baseline} naar {current}."
      ]
    },
    "connectors": {
      "contrast": ["Hoewel", "Ondanks", "Tegelijkertijd"],
      "causal": ["Dit suggereert dat", "Een mogelijke verklaring is", "Dit hangt samen met"],
      "reinforcing": ["Dit wordt bevestigd door", "In lijn hiermee", "Bovendien"],
      "concluding": ["Samenvattend", "De kernboodschap is", "Dit betekent concreet"]
    }
  }
}
```

**Selectielogica:** `random.choice()` met een optionele seed (rapportdatum) voor reproduceerbaarheid bij herhaalde runs.

#### Bouwblok 2 — Ernst-drempeltabellen

Eenmalig definiëren per metrictype, configureerbaar per pijler:

```python
SEVERITY_THRESHOLDS = {
    "score_delta":    {"licht": 0.10, "matig": 0.30},  # abs(delta)
    "hc_ratio_delta": {"licht": 2.0,  "matig": 5.0},   # procentpunten
    "response_days":  {"licht": 2.0,  "matig": 5.0},   # dagen verschil
    "pct_negative":   {"licht": 5.0,  "matig": 10.0},  # absolute waarde
}
```

#### Bouwblok 3 — Connector-logica

Observaties worden niet los achter elkaar geplakt, maar verbonden op basis van hun onderlinge relatie:

```python
def connect_observations(obs1: str, obs2: str, relation: str, i18n: dict) -> str:
    """Verbind twee observaties met een contextuele connector."""
    connector = random.choice(i18n["insights"]["connectors"][relation])
    return f"{obs1} {connector} {obs2[0].lower() + obs2[1:]}"
```

Voorbeeld output: *"De gemiddelde score kende een lichte terugval van 4,50 naar 4,43. Tegelijkertijd bleef het positieve percentage stabiel op 83,3%, wat de impact relativeert."*

#### Voorbeeld: samengestelde executive summary

```python
def build_executive_summary(result: EvolutionResult, i18n: dict) -> str:
    """Bouw een executive summary op uit samengestelde fragmenten."""
    parts = []
    
    # Kerncijfer-observatie met ernst-afhankelijke woordkeuze
    severity = classify_severity(result.score_delta, SEVERITY_THRESHOLDS["score_delta"])
    score_text = random.choice(i18n["insights"]["score_decline"][severity]).format(
        baseline=result.baseline_avg, current=result.current_avg
    )
    parts.append(score_text)
    
    # Scoreverdeling-narratief
    parts.append(result.score_distribution.narrative)
    
    # Contextuele nuancering (als relevant)
    if abs(result.score_delta) < 0.1 and result.current_pct_positive > 80:
        nuance = random.choice(i18n["insights"]["nuance"]["stable_positive"]).format(
            pct=result.current_pct_positive
        )
        parts[-1] = connect_observations(parts[-1], nuance, "contrast", i18n)
    
    # Responstijd-correlatie (als berekend)
    if result.response_time.correlation_score is not None:
        corr_text = random.choice(i18n["insights"]["correlation"]).format(
            r=result.response_time.correlation_score
        )
        parts.append(corr_text)
    
    return "\n\n".join(parts)
```

#### Geschatte omvang

- Zinsvariatie-entries in `nl.json`: ~50-80 entries (2-3 per regeltype × ~25 regeltypes)
- Ernst-drempeltabellen: ~20 regels configuratie
- Connector- en compositielogica: ~100-150 regels in `InsightsGenerator`
- Totaal: **200-300 regels code** + **50-80 i18n-entries**

---

## Laag 4 — template herontwerpen

### Aanbevolen nieuwe structuur (evolutierapport)

**Beslissing 4 (scope):** De eerste implementatieronde focust op de **vetgedrukte** secties. Overige secties worden in een volgende ronde opgepakt.

1. **Executive Summary** (met scoreverdeling-narratief)
2. **Kritieke bevindingen**
3. Kerncijfers vergelijking (met scoreverdeling-rij)
4. **Tijdlijn en keerpunten**
5. Analyse per issue type
6. Analyse per prioriteit
7. Responstijd-analyse
8. Ziekenhuizen — focuslijst + veranderingen
9. Analyse negatieve feedback (met ticket-ID's + volledige comments)
10. Recurring themes
11. Positieve ontwikkelingen
12. KPI target tracking (7 targets)
13. **Visuele analyse** (beschrijving per subplot + PNG-referentie)
14. **Strategische aanbevelingen** (met impact, tijdlijn, eigenaar)
15. **Follow-up acties**
16. **Conclusie**

### Vergelijkingsmatrix-integratie

**Beslissing 11:** De inhoud van output B wordt geabsorbeerd in het evolutierapport. Concreet:

- Benchmark-tabel (baseline, H2 2025, target 2026, huidig) → sectie 3 "Kerncijfers vergelijking"
- Target tracking met statuslabels → sectie 12 "KPI target tracking"
- Structureel vs tijdelijk-beoordeling → sectie 16 "Conclusie"
- Periode-vergelijking over H1/H2 → sectie 4 "Tijdlijn en keerpunten"

De MatrixExporter blijft bestaan als optioneel rapport, maar het evolutierapport is voortaan het primaire managementdocument.

### Maandrapport parallel

**Beslissing 7:** `rapport-nl.md.j2` hergebruikt dezelfde `InsightsGenerator` voor:

- Executive summary
- Bevindingen (gefilterd op maandcontext)
- Aanbevelingen
- KPI-status

De maand-specifieke secties (maanddetail, geen keerpuntanalyse) blijven apart.

### Templateprincipe

Niet alle ruwe tabellen moeten verdwijnen. Wel:

- lange exhaustieve tabellen naar onder of bijlage-logica
- bovenaan: duiding
- onderaan: detail

---

## Implementatievolgorde

**Beslissing 4:** Kern eerst. De fasering is daarom als volgt:

| Fase | Inhoud | Afhankelijkheden | Omvang | Ronde |
| --- | --- | --- | --- | --- |
| 1 | Metric-semantieken harmoniseren (responses vs tickets, perioden, targets) | Geen | S | 1 |
| 2 | `EvolutionAnalyser` + `EvolutionResult` verrijken: summary stats, scoreverdeling, correlatie, negative cases met volledige quotes + ticket-ID's | Fase 1 | M | 1 |
| 3 | `InsightsGenerator` opzetten: executive summary, bevindingen, aanbevelingen (met impact/tijdlijn/eigenaar), keerpuntanalyse, visuele analyse, follow-up | Fase 2 | L | 1 |
| 4 | KPI target tracking: 7 targets in config, tracking-logica in analyser + insights | Fase 2 | S | 1 |
| 5 | `EvolutionExporter` context uitbreiden + NL-template herwerken (kernsecties) | Fase 3+4 | M | 1 |
| 6 | Matrix-inhoud integreren in evolutietemplate (benchmark-tabel, structureel/tijdelijk) | Fase 5 | M | 1 |
| 7 | `MonthlyExporter` + `rapport-nl.md.j2` aansluiten op `InsightsGenerator` | Fase 3 | M | 1 |
| 8 | Overige secties: issue type, prioriteit, hospital detail, recurring themes, positieve ontwikkelingen | Fase 5 | M | 2 |
| 9 | FR-template en i18n gelijk trekken | Fase 5-8 | S | 2 |
| 10 | Tests uitbreiden: analyser + exporter + insights snapshots/keyword assertions | Fase 2-8 | M | doorlopend |
| 11 | Valideren tegen referentie A/B — checklist per sectie (beslissing 10) | Fase 5+ | S | doorlopend |

### Praktische prioriteit binnen ronde 1

1. Correlatie + responstijd-insights
2. Executive summary met scoreverdeling-narratief
3. Kritieke bevindingen
4. KPI target tracking (7 targets)
5. Aanbevelingen met impact/tijdlijn/eigenaar
6. Follow-up acties
7. Visuele analyse-beschrijvingen
8. Keerpuntanalyse

---

## Implementatieaanpak

**Beslissing 6:** GHC via gestructureerde prompts. Claude levert de prompts, GHC implementeert.

Per fase worden de volgende deliverables opgeleverd:

- **GHC-prompt**: gestructureerde implementatie-instructie per methode/klasse, scope beperkt tot één module per prompt
- **Verwachte output**: beschrijving van het resultaat zodat Danny kan valideren
- **Testscenario**: wat GHC moet testen na implementatie

De prompts volgen het bestaande patroon: chirurgisch (één methode), zonder `render()` of shared utilities aan te raken, met expliciete scope-afbakening.

---

## Ontwerpkeuzes en bedenkingen

### 1. Regelgebaseerd als enige optie

**Beslissing 1 — bevestigd.** Zie de haalbaarheidsanalyse hierboven. De 80-90% pariteit is realistisch; de investering zit in zinsvariatie en compositiepatronen.

### 2. Exhaustieve tabel vs managementfocus

De huidige ziekenhuistabel is volledig, maar niet prioritair leesbaar.

Combineer beide:

- bovenaan: shortlist "benchmark / stabiel / aandacht"
- onderaan of bijlage: volledige tabel

### 3. Klantcomments en ticket-ID's

**Beslissingen 2 + 3 — bevestigd.** Volledige comments en ticket-ID's worden opgenomen, inclusief ziekenhuisnaam. Enige sanitizing: eventuele ZORGI-medewerkersnamen in comments.

Dit betekent voor de `NegativeCase`-dataklasse:

- `comment` bevat de volledige tekst uit V_CSAT_1
- `ticket_id` wordt als-is overgenomen
- `hospital` wordt als-is overgenomen
- een optionele `sanitize_comment()`-methode verwijdert alleen ZORGI-medewerkersnamen

### 4. Target tracking

**Beslissing 5 — bevestigd.** 7 concrete targets.

Het onderscheid threshold vs target blijft relevant:

- **Threshold** (`AVG_SCORE_MIN`, `HIGH_CRITICAL_MAX` in `settings.py`) = technisch minimum voor KPI-statuskleuring
- **Target** (de 7 waarden uit beslissing 5) = managementdoel voor target tracking-sectie

Beide worden in `settings.py` opgenomen. De target tracking-sectie toont: baseline → target → huidig → status → "op schema?".

### 5. Vergelijkingsmatrix wordt geabsorbeerd

**Beslissing 11 — bevestigd.** Het evolutierapport neemt de kerninhoud van output B over. De MatrixExporter blijft als optioneel rapport, maar is niet langer de primaire benchmark-bron voor het CS board.

### 6. Scoreverdeling

**Beslissing 12 — bevestigd.** Compact formaat in kerncijfertabel + narratieve zin in executive summary. Geen aparte sectie.

---

## Validatie-aanpak

**Beslissing 10:** Vergelijk output C-nieuw naast referentie A/B met een checklist per sectie.

### Validatiechecklist

| Sectie | Criterium | Bron |
| --- | --- | --- |
| Executive Summary | Kernboodschap + kerncijfers + scoreverdeling aanwezig | Ref A |
| Kritieke bevindingen | 3-5 bevindingen met causaliteit en ernst | Ref A |
| Keerpuntanalyse | Dieptepunten + doorbraak + fase-overgangen benoemd | Ref B |
| Negatieve feedback | Ticket-ID + ziekenhuis + volledige comment aanwezig | Ref A |
| Responstijd-analyse | Correlatie + positief/negatief vergelijking aanwezig | Ref A+B |
| KPI target tracking | 7 targets met baseline/target/huidig/status | Ref B |
| Visuele analyse | Narratieve beschrijving per subplot aanwezig | Ref A |
| Aanbevelingen | Impact + tijdlijn + eigenaar per aanbeveling | Ref A |
| Follow-up acties | Acties per tijdshorizon | Ref A |
| Conclusie | Structureel/tijdelijk-beoordeling onderbouwd | Ref B |
| Managementleesbaarheid | Leest als rapport, niet als data-export | Ref A+B |

---

## 80/20-check

Met de beslissingen als kader haal je met **ronde 1** het grootste deel van de managementwaarde:

1. **Executive Summary met kernboodschap + scoreverdeling**
2. **Kritieke bevindingen-sectie**
3. **Responstijd-correlatie + positief/negatief vergelijking**
4. **Negatieve feedback deep-dive met ticket-ID's + volledige comments**
5. **KPI target tracking met 7 targets**
6. **Visuele analyse met beschrijving per subplot**
7. **Strategische aanbevelingen met impact/tijdlijn/eigenaar**
8. **Follow-up actielijst per horizon**
9. **Keerpuntanalyse in tijdlijn**

### Laaghangend fruit metrics

Deze zijn relatief goedkoop en leveren veel meerwaarde:

- mediaan score
- standaarddeviatie
- neutraal %
- scoreverdeling per niveau met compact label
- correlation score
- counts per issue type/prioriteit
- top negatieve cases met volledige context
- maand-op-maand delta laatste maand
- minimum responsdrempel voor ziekenhuisduiding

### Wat in ronde 2 komt

- Issue type / prioriteit detail-analyse
- Hospital detail-sectie
- Recurring themes verdieping
- Positieve ontwikkelingen als vaste sectie
- FR-template
- Uitgebreide tests

---

## Risico's en mitigatie

| Risico | Impact | Mitigatie |
| --- | --- | --- |
| Apples-vs-oranges vergelijking met legacy outputs | Hoog | Eerst definities harmoniseren: responses, tickets, periodes, filters (fase 1) |
| Te veel logica in Jinja-template | Hoog | Interpretatie naar `InsightsGenerator` verplaatsen |
| Rapport wordt te lang en verliest focus | Medium | Management-first structuur, detailtabellen lager plaatsen |
| Pharma-specifieke regels lekken naar andere pijlers | Hoog | Pijlerneutrale dataklassen + configureerbare targets per pijler |
| NL/FR drift | Hoog | NL eerst (ronde 1), FR in ronde 2, i18n-sleutels centraal |
| Volledige comments bevatten ZORGI-medewerkersnamen | Medium | `sanitize_comment()` verwijdert interne namen |
| Reproduceerbaarheid van narratief | Medium | Rule-based regels, zinsvariatie via i18n, testbare templates |
| InsightsGenerator wordt te complex voor twee rapporttypes | Medium | Gedeelde basis + rapporttype-specifieke methoden, geen monolithische klasse |
| GHC-prompts worden te breed | Hoog | Chirurgische scope per prompt: één methode, één module |
| Scope creep in release 1 | Hoog | Strikt vasthouden aan bevestigde ronde 1 scope *(GHC-verrijking)* |
| Validatie tegen referentie is subjectief | Medium | Checklist per sectie met objectieve criteria (aanwezig/niet aanwezig) |

---

## Samenvatting

De huidige evolutie-output van CSAT-Compass is **technisch degelijk, maar inhoudelijk nog geen managementrapport**. De kern van de kloof is niet dat de data fout zou zijn, maar dat de output nog te veel stopt bij tabellen en te weinig doet aan:

- interpretatie,
- prioritering,
- causaliteit,
- actiegerichtheid.

Met de 12 bevestigde beslissingen is het pad helder:

1. `EvolutionAnalyser` verrijken met ontbrekende metrics (incl. scoreverdeling, correlatie, 7 KPI-targets),
2. `EvolutionResult` uitbreiden met rijkere analyse-objecten (incl. `NegativeCase` met volledige quotes en ticket-ID's),
3. een **gedeelde `InsightsGenerator`** bouwen voor zowel evolutie- als maandrapport,
4. de template herstructureren naar executive summary → bevindingen → keerpunten → aanbevelingen (met impact/tijdlijn/eigenaar) → follow-up,
5. de inhoud van de vergelijkingsmatrix absorberen in het evolutierapport,
6. een visuele analyse-sectie toevoegen met narratief per subplot.

**Kern eerst (ronde 1)**, overige secties in ronde 2. Implementatie via GHC-prompts, validatie via checklist per sectie naast referentie A/B.

Regelgebaseerd is haalbaar: de investering zit in drie concrete bouwblokken (zinsvariatie-bibliotheek in i18n, ernst-drempeltabellen, connector-logica — samen ~200-300 regels code + ~50-80 i18n-entries). De verwachte pariteit met de referentie-output is 85-90% — een grote sprong vooruit ten opzichte van de huidige output.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| --- | --- | --- | --- |
| 1.0 | 27/03/2026 | Initiële gap-analyse en verbeteradvies (CD) | Claude Desktop |
| 2.0 | 28/03/2026 | 12 DDP-beslissingen verwerkt, haalbaarheidsanalyse, zinsvariatie-strategie (CD) | Claude Desktop |
| 2.0-ghc | 29/03/2026 | Parallelle versie met dubbele benchmark, scope creep-bewaking, extra dataklassen (GHC) | GitHub Copilot |
| 3.0 | 29/03/2026 | Samengevoegde versie: CD v2.0 als basis + GHC-verrijkingen. Alle 12 DDP-beslissingen correct verwerkt. Geïnstalleerd als normatief kader voor fase 3g | Danny Depecker + CD + GHC |
