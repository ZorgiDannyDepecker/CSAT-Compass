# CSAT-Compass - Architectuurbeslissingen

**Versie:** 1.0  
**Laatst bijgewerkt:** 18/03/2026  

**Doel:** Architecture Decision Records (ADRs) voor alle fundamentele keuzes in CSAT-Compass  
**Type:** ADR  
**Auteur:** Danny Depecker + GHC  
**Status:** Approved  

**Bestandsnaam:** architectuur-beslissingen.md  
**Path:** docs/01-strategisch/  

---

## Inhoudsopgave

1. [ADR-001 — Hybride databron](#1-adr-001--hybride-databron)
2. [ADR-002 — Streamlit dashboard](#2-adr-002--streamlit-dashboard)
3. [ADR-003 — Jinja2 + i18n voor tweetaligheid](#3-adr-003--jinja2--i18n-voor-tweetaligheid)
4. [ADR-004 — Selectieve migratie vanuit Customer Satisfaction](#4-adr-004--selectieve-migratie-vanuit-customer-satisfaction)
5. [ADR-005 — PHARMA-first ontwikkelingsstrategie](#5-adr-005--pharma-first-ontwikkelingsstrategie)
6. [ADR-006 — Reactiegraad KPI niet meetbaar via V_CSAT_1](#6-adr-006--reactiegraad-kpi-niet-meetbaar-via-v_csat_1)

---

## 1. ADR-001 — Hybride databron

**Datum:** 18/03/2026  
**Status:** ✅ Approved

### Context

De databron voor CSAT-Compass evolueert van handmatige CSV-exports (PHARMA-project)
naar een databaseview gegenereerd vanuit PowerBI. Er moet een robuuste en flexibele
datalaarstrategie gekozen worden die beide scenario's ondersteunt.

### Beslissing

**Hybride databron:** SQL als primaire bron, CSV als fallback.

- **SQL (primair):** directe connectie via `sqlalchemy` + `pyodbc` naar de PowerBI-databaseview
- **CSV (fallback):** lokale exports in `data/` — bruikbaar wanneer DB niet bereikbaar is

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| A | SQL only | Fragiel bij DB-uitval of onderhoud |
| B | CSV only | Manueel, niet schaalbaar voor 5 pijlers |
| C | PowerBI REST API | Vereist Azure AD + service principal, te complex |
| **D** | **Hybride SQL + CSV** | **Gekozen — robuust en flexibel** |

### Consequenties

- `core/loaders/` bevat `base_loader.py`, `sql_loader.py` en `csv_loader.py`
- `settings.py` bevat DB-connectiestring (via `.env`, nooit in Git)
- Logging waarschuwt expliciet wanneer fallback actief is
- `data/`-map uitgesloten van Git via `.gitignore`

---

## 2. ADR-002 — Streamlit dashboard

**Datum:** 18/03/2026  
**Status:** ✅ Approved

### Context

CSAT-Compass genereert maandelijks 20 statische MD/PDF-bestanden. Voor management
en pijlerteams is een interactief overzicht gewenst dat trends en vergelijkingen
visueel toegankelijk maakt zonder technische kennis.

### Beslissing

**Streamlit** als dashboardtechnologie.

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| **A** | **Streamlit** | **Gekozen — Python-native, snel, lokaal + deploybaar** |
| B | Plotly Dash | Krachtiger maar steiler leercurve, overkill voor huidige scope |
| C | Statische HTML | Niet interactief, beperkte filteropties |
| D | PowerBI dashboard | Python genereert dan enkel rapporten, verliest controle over UX |

### Consequenties

- `src/dashboard/app.py` is de Streamlit-applicatie
- Dashboard bevat NL/FR-taaltoggle in de sidebar
- Pijlers zijn filterbaar via sidebar (ZORGI / PHARMA / CARE / CARE ADMIN / ERP4HC)
- Visualisaties via `plotly` voor interactiviteit, `matplotlib` voor statische exports
- Lokaal starten: `streamlit run src/dashboard/app.py`
- Afhankelijkheid: `streamlit>=1.32.0` + `plotly>=5.20.0` in `requirements.txt`

---

## 3. ADR-003 — Jinja2 + i18n voor tweetaligheid

**Datum:** 18/03/2026  
**Status:** ✅ Approved

### Context

ZORGI is een tweetalige organisatie (NL/FR). Alle CSAT-output moet beschikbaar zijn
in beide landstalen. Met 5 rapporten + 5 matrices per maand is een schaalbare,
onderhoudbare aanpak vereist.

### Beslissing

**Jinja2-templates gekoppeld aan i18n-woordenboeken** (`nl.json` + `fr.json`).

- Eén template per outputtype
- Labels en teksten volledig in JSON-woordenboeken
- Python vult de template in voor elke taal → 2 outputbestanden per run

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| **A** | **Jinja2 + i18n JSON** | **Gekozen — onderhoudbaar, schaalbaar, geen externe dienst** |
| B | GHC-vertaling post-hoc | Niet geautomatiseerd, vereist handmatige tussenkomst |
| C | DeepL API | Kosten per teken, externe afhankelijkheid, minder controle over vakterminologie |
| D | Dubbele templates | Manueel synchroon houden van 2 templates per outputtype — foutgevoelig |

### Consequenties

- `src/csat/i18n/nl.json` — alle labels, titels, teksten in het Nederlands
- `src/csat/i18n/fr.json` — alle labels, titels, teksten in het Frans
- `docs/templates/` bevat Jinja2-templates (`.md.j2`)
- Nieuwe term toevoegen = aanpassing in beide JSON-bestanden
- Cijfers, tabellen en visualisatietitels zijn identiek in NL en FR
- `Babel>=2.14.0` voor datumnotatie en lokalisatie

---

## 4. ADR-004 — Selectieve migratie vanuit Customer Satisfaction

**Datum:** 18/03/2026  
**Status:** ✅ Approved

### Context

Er bestaat een werkende PHARMA-gerichte CSAT-analyse in
`C:\Users\danndepe\Documents\AI\Customer Satisfaction`. De vraag is of en hoe
deze code wordt overgebracht naar CSAT-Compass.

### Beslissing

**Selectieve migratie:** enkel de bewezen analyselogica wordt overgenomen,
herschreven conform de nieuwe `core/`-architectuur. Geen copy-paste, geen submodule.

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| **A** | **Selectieve migratie + herschrijven** | **Gekozen — schone architectuur, geen technische schuld** |
| B | Copy-paste + refactor later | Technische schuld, inconsistente stijl |
| C | Volledig vers beginnen | Verlies van bewezen logica zonder reden |
| D | Git submodule | Koppeling aan oud project, afhankelijkheidsbeheer complex |

### Consequenties

- `Customer Satisfaction` blijft bestaan als leesreferentie
- Migratie verloopt per logisch blok: berekeningen, KPI-definities, drempelwaarden
- Alle gemigreerde logica wordt herschreven met Nederlandse docstrings en Engelse variabelenamen
- Unit tests worden geschreven voor elke gemigreerde functie (in `tests/`)

---

## 5. ADR-005 — PHARMA-first ontwikkelingsstrategie

**Datum:** 18/03/2026  
**Status:** ✅ Approved

### Context

Het project omvat 5 pijlers (ZORGI + 4 pillar-analysers). De volgorde van
implementatie bepaalt hoe snel waarde wordt geleverd en hoe herbruikbaar
de architectuur is voor de volgende pijlers.

### Beslissing

**PHARMA-first:** PHARMA wordt volledig uitgewerkt als referentie-implementatie.
De andere pijlers volgen als kopie + aanpassing van de PHARMA-module.

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| **A** | **PHARMA-first piloot** | **Gekozen — snelste waardeoplevering, bewezen basis voor andere pijlers** |
| B | Core-first | Vertraagt time-to-value, abstractie-risico zonder concrete use case |
| C | Alle 4 pijlers parallel | Te brede scope tegelijk, geen focuspunt |
| D | Dashboard-first | Mockdata vereist, echte pipeline ontbreekt nog |

### Volgorde pijlerimplementatie

1. **PHARMA** — referentie-implementatie (Fase 1–2)
2. **CARE** — kopie PHARMA + aanpassing categorieën (Fase 4)
3. **CARE ADMIN** — kopie PHARMA + aanpassing (Fase 4)
4. **ERP4HC** — kopie PHARMA + aanpassing (Fase 4)
5. **ZORGI** — aggregatie van de 4 pijlers (Fase 6)

### Consequenties

- `src/csat/pillars/pharma/` is het meest uitgewerkte pijler-pakket
- Nieuwe pijler toevoegen = PHARMA kopiëren + `config.py` aanpassen
- `zorgi/analyser.py` wordt als laatste uitgewerkt (afhankelijk van alle andere pijlers)
- Documentatie voor elke pijler volgt hetzelfde stramien als PHARMA

---

---

## 6. ADR-006 — Reactiegraad KPI niet meetbaar via V_CSAT_1

**Datum:** 20/03/2026  
**Status:** ✅ Approved

### Context

Bij de initiële KPI-definitie voor CSAT-Compass werd de **reactiegraad** opgenomen
als kernindicator: het percentage tickets waarbij een klant effectief een CSAT-score
invulde ten opzichte van het totaal aantal tickets waarvoor een uitnodiging werd verstuurd.

De drempelwaarde was vastgelegd op ≥ 85% voor de PHARMA-pijler.

Tijdens de eerste DB-exploratie op 20/03/2026 bleek dat de databron `[dbo].[V_CSAT_1]`
uitsluitend tickets bevat die **reeds een CSAT-score hebben**. Van alle 6.000 records
in de view heeft 100% een ingevulde scorewaarde.

### Beslissing

**Reactiegraad KPI wordt niet opgenomen in CSAT-Compass.**

De meting is technisch onuitvoerbaar met de beschikbare databron:

- `V_CSAT_1` is een **pre-gefilterde view** — enkel gescoorde tickets zijn zichtbaar
- Het **totaal aantal verstuurde uitnodigingen** is niet beschikbaar in deze view
- Zonder de noemer (totaal uitgenodigd) is het percentage niet berekbaar

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| A | Reactiegraad via V_CSAT_1 | ❌ View bevat enkel gescoorde tickets — teller = noemer = 100% altijd |
| B | Reactiegraad via ruwe ticketing-export | ❌ Geen toegang tot de uitnodigingstabel op dit moment |
| C | Reactiegraad schatten via historische patronen | ❌ Te onnauwkeurig voor rapportage aan CEO/COO |
| **D** | **KPI weglaten — eerlijk communiceren** | **✅ Gekozen — integriteit boven volledigheid** |

### Consequenties

- `REACTIEGRAAD_MIN` wordt verwijderd als actieve drempelwaarde uit `pharma/config.py`
- `_calc_reactiegraad()` blijft beschikbaar in `BaseAnalyser` voor toekomstig gebruik
  als de databron uitgebreid wordt met uitnodigingsdata
- Rapporten en dashboards vermelden deze KPI **niet**
- Indien in de toekomst toegang komt tot de ruwe ticketingdata (alle tickets, ook
  niet-gescoorde), kan de reactiegraad alsnog worden geactiveerd zonder architectuurwijziging
- Deze beslissing wordt gecommuniceerd aan de stakeholders (CEO Eric, COO Christian)
  bij de eerste rapportage

### 💡 Toekomstige activering

Zodra een databron beschikbaar is met alle tickets (gescoord + niet-gescoord), volstaat:

1. `REACTIEGRAAD_MIN` terug instellen in `pharma/config.py` (en andere pijler-configs)
2. De loader aanpassen om beide views te joinen of de ruwe export te laden
3. `PharmaAnalyser._evaluate_thresholds()` activeert de check automatisch

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------------------------------------------- | -------------------- |
| 1.0 | 18/03/2026 | Initiële versie — 5 ADRs op basis van MCQ-sessie | Danny Depecker + GHC |
| 1.1 | 20/03/2026 | ADR-006 toegevoegd: reactiegraad niet meetbaar via V_CSAT_1 | Danny Depecker |
