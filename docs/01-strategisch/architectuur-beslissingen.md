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
7. [ADR-007 — Analyseperiode en ONBEKEND hospital](#7-adr-007--analyseperiode-en-onbekend-hospital)
8. [ADR-008 — Mapstructuur en mapfilosofie](#8-adr-008--mapstructuur-en-mapfilosofie)
9. [ADR-009 — AVG_SCORE_MIN drempelwaarde](#9-adr-009--avg_score_min-drempelwaarde)
10. [ADR-010 — ZORGI Design System integratie en kleurbeleid](#10-adr-010--zorgi-design-system-integratie-en-kleurbeleid)
11. [ADR-011 — satisfaction_date als CSAT-periodegroepering](#11-adr-011--satisfaction_date-als-csat-periodegroepering)
12. [ADR-012 — Nieuwe instappers uitsluiten uit delta-ranking (subplot 4)](#12-adr-012--nieuwe-instappers-uitsluiten-uit-delta-ranking-subplot-4)
13. [ADR-013 — Runner/library-structuur (scripts vs src vs tools)](#13-adr-013--runnerlibrarystructuur-scripts-vs-src-vs-tools)

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

---

## 7. ADR-007 — Analyseperiode en ONBEKEND hospital

**Datum:** 20/03/2026  
**Status:** ✅ Approved

### Context

Twee praktische bevindingen uit de live DB-exploratie op 20/03/2026 vereisen een
expliciete architectuurkeuze:

1. **Analyseperiode:** V_CSAT_1 bevat historische data die teruggaat tot vóór 2025.
   Voor CSAT-Compass is enkel data vanaf 01/01/2025 relevant (baseline-jaar).
   Er moet een configureerbaar filter zijn dat oudere data uitsluit.

2. **NULL hospital:** 9 van de 64 ziekenhuizen in de view hebben geen
   ziekenhuisidentificatie (`hospital = NULL`). Bij aggregatie per ziekenhuis
   gaan deze tickets verloren als ze niet expliciet worden afgehandeld.

### Beslissing

**Analyseperiode:** configureerbaar via omgevingsvariabele `CSAT_ANALYSE_START_DATE` (standaard `2025-01-01`).

**NULL hospital:** tickets zonder ziekenhuisidentificatie worden weergegeven als `ONBEKEND`
zodat ze zichtbaar blijven in rapporten en dashboards.

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| A | Vaste startdatum hardcoded in broncode | ❌ Niet configureerbaar zonder codewijziging |
| B | Filter in SQL-query meegeven aan loader | ❌ CSV-fallback zou dan ander gedrag hebben |
| **C** | **Filter in PillarAnalyser via env-variabele** | **✅ Gekozen — consistent voor SQL en CSV** |
| A | NULL hospitals negeren / weggooien | ❌ Verlies van tickets — onzichtbaar in rapportage |
| B | NULL hospitals als aparte categorie | ❌ Moeilijk te communiceren |
| **C** | **NULL hospitals tonen als 'ONBEKEND'** | **✅ Gekozen — zichtbaar en actiebaar** |

### Consequenties

- `ANALYSE_START_DATE` is configureerbaar via `.env` (`CSAT_ANALYSE_START_DATE`)
- `PillarAnalyser._filter_start_date()` past het filter toe na de pijlerfilter
- `BaseAnalyser._group_by_hospital()` vult `NULL` aan met `"ONBEKEND"` via `fillna()`
- Rapporten tonen een `ONBEKEND`-rij als er tickets zijn zonder ziekenhuisnaam
- Aandachtspunt voor Fase 4: actie vereist om de 9 NULL-hospitals te identificeren
  en correct toe te wijzen (data-kwaliteitsissue aan ZORGI-zijde)

### 💡 Data-kwaliteitsopvolging

De 9 tickets met `NULL` hospital zijn in de huidige PHARMA-data zichtbaar als `ONBEKEND`.
Dit is een bekende data-kwaliteitslacune in V_CSAT_1 die buiten de scope van
CSAT-Compass valt maar moet worden gecommuniceerd aan het PHARMA-team.

---

## 8. ADR-008 — Mapstructuur en mapfilosofie

**Datum:** 22/03/2026  
**Status:** Approved  
**Beslissing:** Strikte scheiding tussen `src/` (library), `scripts/` (runners) en `tools/` (dev-hulp)

### Context

Naarmate het project groeit, worden meer Python-bestanden aangemaakt. Zonder een bewuste
mapfilosofie belandt alle code in één map en is het voor nieuwe collega's onduidelijk
waar iets thuishoort en waarom.

Drie vragen lagen aan de basis van deze beslissing:

1. Waar staat herbruikbare code die door andere modules wordt geïmporteerd?
2. Waar staan scripts die rechtstreeks via de terminal worden aangeroepen?
3. Waar staat tooling die niets weet van CSAT maar de ontwikkelaar helpt?

### Beslissing

| Map | Rol | Projectspecifiek | Voorbeeld |
|---|---|---|---|
| `src/csat/` | Python-library — importeerbare modules | ✅ Ja | `PharmaAnalyser`, `ReportExporter` |
| `scripts/` | CLI-entrypoints — roepen `src/` aan | ✅ Ja | `export_data.py` |
| `tools/` | Dev-hulpscripts — geen projectlogica | ❌ Nee | `lint.ps1` |

**Kernregel:** als je `tools/` naar een ander Python-project kopieert en het werkt er
ook — dan hoort het in `tools/`. Als het enkel zinvol is binnen CSAT-Compass — dan
hoort het in `scripts/` of `src/`.

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| A | Alles in `src/` | ❌ Mengt library-code met runners en dev-tooling |
| B | Alles in `scripts/` | ❌ Geen onderscheid tussen projectlogica en dev-tools |
| **C** | **src/ + scripts/ + tools/ als aparte lagen** | **✅ Gekozen — elke map heeft één duidelijke verantwoordelijkheid** |

### Consequenties

- `src/csat/` bevat uitsluitend importeerbare modules — geen `if __name__ == "__main__":` blokken
- `scripts/` bevat uitsluitend entrypoints — minimale logica, alles delegeren aan `src/`
- `tools/` is projectonafhankelijk — `lint.ps1` werkt op élk Python-project
- Eenmalige debug- of herstelscripts (bv. `fix_templates.py`) worden na gebruik **verwijderd**, niet bewaard
- `WIP/` is de tijdelijke opvangmap voor alles wat nog niet productierijp is

---

## 9. ADR-009 — AVG_SCORE_MIN drempelwaarde

**Datum:** 22/03/2026  
**Status:** Approved  
**Beslissing:** Minimale aanvaardbare gemiddelde CSAT-score = **4,00** (op schaal 1–5)

### Context

De gemiddelde CSAT-score is een kernKPI in alle PHARMA-rapporten. Om een zinvolle
OK/waarschuwing-status te tonen, is een drempelwaarde nodig.

Analyse van de historische PHARMA-data (V_CSAT_1) op 22/03/2026:

| Periode | Gem. score | Tickets |
|---|---|---|
| jan–mei 2025 | 2,10 – 2,91 | 136 |
| jun–dec 2025 | 4,18 – 4,87 | 111 |
| 2026 YTD | 4,43 | 67 |
| **2025 volledig** | **3,51** | **247** |

De sterke breuk rond juni 2025 wijst op een structurele verandering in het
ticketingproces of de scoremethode. Het volledige 2025-gemiddelde van 3,51 is
daardoor niet representatief als drempelwaarde.

### Beslissing

Drempel: **≥ 4,00** — configureerbaar via omgevingsvariabele `CSAT_AVG_SCORE_MIN`.

Redenering:

- Ligt bewust iets onder het huidig niveau (4,43) — ruimte voor tijdelijke schommelingen
- Gebaseerd op de stabiele periode jun–dec 2025 en 2026 YTD
- Één universele drempel voor alle ziekenhuizen (niet per ziekenhuis)

### Alternatieven overwogen

| Optie | Waarde | Reden verworpen |
|---|---|---|
| A | 3,51 (volledig 2025 gem.) | ❌ Vertekend door anomalie jan–mei 2025 |
| B | 4,50 (stabiel 2025 H2 gem.) | ❌ Te streng — geen marge bij tijdelijke dip |
| C | 4,43 (2026 YTD) | ❌ Fluctueert maandelijks — onbetrouwbaar als vaste drempel |
| **D** | **4,00** | **✅ Gekozen — praktisch, verdedigbaar, stabiel** |

### Consequenties

- `AVG_SCORE_MIN = 4.0` toegevoegd aan `src/csat/config/settings.py`
- `avg_score_ok` berekend in `ReportExporter._build_context()`
- KPI-tabel toont ✅ OK of ⚠️ Aandacht voor gemiddelde score
- `thresholds.avg_score_min` in nl.json + fr.json bijgewerkt van TBD naar "≥ 4,00"
- `notes.avg_score_tbd` verwijderd uit i18n en templates

---

## 10. ADR-010 — ZORGI Design System integratie en kleurbeleid

**Datum:** 23/03/2026
**Status:** ✅ Approved
**Beslissing:** Alle visuele output gebruikt uitsluitend ZORGI Design System kleuren; rood gereserveerd voor alarmen; logo-assets gebundeld; productnamen conform branding-tabel

### Context

Bij de start van CSAT-Compass werden pijlerkleuren ad hoc gekozen in `pillars.py` en
`branding.py`. Een review op 23/03/2026 bracht vijf off-brand kleuren aan het licht
(groen, oranje, willekeurig blauw) die nergens in het ZORGI Design System voorkomen.
Daarnaast ontbraken logo-assets, lokale fonts voor matplotlib, en was het Design System
zelf niet opgenomen in de repository.

Parallel werden productnamen inconsistent gebruikt: `ZORGI PHARMA` en `ZORGI CARE` als
`report_name` terwijl het Design System (§8) deze producten als `PHARMA` en `CARE`
benoemt. De interne naam `ERP4HC` miste het superscript `²·⁰`.

### Beslissingen

**1. Pijler-kleurschema (Optie A)**

Dark Blue is gereserveerd voor ZORGI als overkoepelend merk. De vier pijlers staan op
gelijk niveau en krijgen elk een eigen unieke kleur:

| Pijler | Kleur | HEX | Bron |
|---|---|---|---|
| ZORGI | Dark Blue | `#003a70` | Design System — primair |
| PHARMA | Light Blue | `#609fce` | Design System — secundair |
| CARE | Grey Blue | `#5f8495` | Design System — secundair |
| OAZIS | Light Purple | `#a06b8a` | Afgeleide (zie onder) |
| ERP4HC²·⁰ | Purple | `#7f4267` | Design System — primair |

**2. Rood gereserveerd voor alarmen**

Rood (`#dc2b26`) wordt **niet** als pijlerkleur gebruikt en is verwijderd uit
`PLOTLY_LAYOUT.colorway`. Het is uitsluitend beschikbaar voor `trend-down`,
KPI-waarschuwingen en alarmen. Dit voorkomt verwarring in dashboards en rapporten
waar rood "slecht" betekent.

**3. Afgeleide kleur Light Purple (#a06b8a)**

Het Design System biedt 6 kleuren. Met Dark Blue voor ZORGI en Red gereserveerd voor
alarmen, resteren 4 kleuren voor 4 pijlers. Omdat Purple naar ERP4HC gaat, heeft OAZIS
(CARE ADMIN) een afgeleide nodig. `#a06b8a` is het 60%-punt op de gradient van
Purple (#7f4267) naar Ultra Light Blue (#d7e7f3) — on-brand in feel, visueel goed
onderscheidbaar van Purple.

**4. Logo-assets gebundeld**

6 heartbeat-iconen opgenomen in `src/static/img/` met dev-friendly naamconventie
(`heartbeat_*`). Kanaal-toewijzing: wit-varianten voor gradient-headers (Streamlit, PDF),
kleur-varianten voor lichte achtergronden (favicon, sidebar), transparante variant voor
matplotlib-watermark.

**5. Poppins TTF lokaal gebundeld**

Poppins Light (300) en ExtraBold (800) opgenomen in `src/static/fonts/` zodat matplotlib
ze kan gebruiken onafhankelijk van de systeeminstallatie. Streamlit en WeasyPrint
gebruiken Google Fonts `@import`.

**6. Productnamen conform branding-tabel**

- `erp4hc.name` en `name_fr`: `ERP4HC` → `ERP4HC²·⁰` (superscript consistent)
- `pharma.report_name`: `ZORGI PHARMA` → `PHARMA` (conform Design System §8)
- `care.report_name`: `ZORGI CARE` → `CARE` (conform Design System §8)

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| Rood als ERP4HC-kleur | Maximaal contrast | ❌ Rood = "alarm" in dashboards — verwarrend |
| Bordeaux (#9e3347) als ERP4HC-kleur | Warm accent | ❌ Te dicht bij Purple in kleine grafieken |
| Ultra Light Blue als ERP4HC-kleur | 100% on-brand | ❌ Te licht voor lijngrafieken |
| Alle pijlerkleuren uit Design System (geen afgeleide) | Strikt compliant | ❌ Onvoldoende unieke kleuren na reservering van rood |

### Consequenties

- `PILLAR_REGISTRY[x]["color"]` in `pillars.py` bevat uitsluitend toegestane kleuren
- `PILLAR_COLORS` in `branding.py` is exact gesynchroniseerd met `pillars.py`
- `PLOTLY_LAYOUT.colorway` en matplotlib `axes.prop_cycle` gebruiken pijlerkleuren (geen rood)
- `LOGO_ASSETS` dict in `branding.py` centraliseert alle logo-paden
- Validatietests (`test_branding.py`) afdwingen:
  - Alle pijlerkleuren in toegestaan palet
  - Cross-check `pillars.py` ↔ `branding.py`
  - Alle logo-assets bestaan op schijf
  - Geen rood in colorways
  - CSS-kleuren consistent met `COLORS` dict
- Design System opgenomen als `docs/01-strategisch/ZORGI_Design_System.md`
- Wijziging aan `report_name` beïnvloedt enkel nieuw gegenereerde rapporten
- Validatie van `#a06b8a` door <marcom@zorgi.be> wordt aanbevolen

---

## 11. ADR-011 — satisfaction_date als CSAT-periodegroepering

**Datum:** 25/03/2026
**Status:** ✅ Approved
**Beslissing:** Periodegroepering (maand/jaar) in alle CSAT-analyses gebeurt op basis van
`satisfaction_date` — de datum waarop de klant zijn score gaf. `created` wordt uitsluitend
gebruikt als poortwachter voor ADR-007 (tickets vóór 01/01/2025 uitsluiten).

### Context

V_CSAT_1 bevat twee datumvelden met een verschillende semantiek:

| Veld | Betekenis |
|---|---|
| `created` | Datum waarop het ticket aangemaakt werd in het ticketingsysteem |
| `satisfaction_date` | Datum waarop de klant effectief zijn tevredenheidsscore invulde |

Beide velden komen in de meeste gevallen overeen, maar kunnen afwijken:
een ticket aangemaakt op 28 december kan pas gescoord worden op 5 januari van het
volgende jaar. Voor maandelijkse CSAT-rapportage is het essentieel om te kiezen welk
veld de maatstaf is.

### Beslissing

`satisfaction_date` is de CSAT-relevante tijdstempel voor alle periodegroepering:

- `_PERIOD_DATE_COL = "satisfaction_date"` in `EvolutionAnalyser`
- `filter_period(..., date_col="satisfaction_date")` in alle maandelijkse breakdowns
- `created` wordt enkel gebruikt in `_filter_start_date()` (ADR-007-filter)

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen |
|---|---|---|
| A | `created` als periodegroepering | ❌ Meet wanneer het ticket aangemaakt werd, niet wanneer de klant reageerde — irrelevant voor CSAT |
| **B** | **`satisfaction_date` als periodegroepering** | **✅ Gekozen — meet de klanttevredenheid op het moment van feedback** |
| C | Gemiddelde van `created` en `satisfaction_date` | ❌ Zinloos — geen statistisch voordeel, verhoogt complexiteit |

### Consequenties

- Een ticket aangemaakt in december maar gescoord in januari telt in de **januari**-cijfers
- Maanden zonder `satisfaction_date`-data tonen als lege of nul-bars in de visualisatie —
  dit is correct gedrag, geen data-fout
- `created` dient uitsluitend als poortwachter (ADR-007): tickets aangemaakt vóór
  `ANALYSE_START_DATE` worden volledig uitgesloten, ongeacht hun `satisfaction_date`
- Gevolg voor interpretatie: een lege maand in de grafiek betekent dat er in die maand
  geen klanten hun score hebben ingediend — niet dat er geen tickets waren

---

## 12. ADR-012 — Nieuwe instappers uitsluiten uit delta-ranking (subplot 4)

**Datum:** 25/03/2026
**Status:** ✅ Approved

### Context

Subplot 4 van de CSAT-evolutievisualisatie toont een delta (Δ = current_score −
baseline_score) per ziekenhuis. De `_hospital_comparison()`-methode in `EvolutionAnalyser`
stelt `baseline_score = 0.0` in wanneer een ziekenhuis **geen tickets** had in de
baseline-periode (`b_sub.empty`). Dit is een technische default, geen meetwaarde.

Concreet geval (25/03/2026 gedetecteerd): **BONHEIDEN_IMELDA** had 0 PHARMA-tickets in
2025 en 1 PHARMA-ticket (score 5) in januari 2026. De delta werd berekend als
5,0 − 0,0 = **+5,00**, waardoor dit ziekenhuis als absolute topper in het quadrant
verscheen — statistisch misleidend.

### Beslissing

Ziekenhuizen met `baseline_total == 0` worden **uitgesloten uit de delta-ranking**
in subplot 4. De selectiefunnel in `_draw_subplot4_hospitals()` bevat nu drie
voorwaarden:

```python
vergelijkbaar = [
    h for h in r.hospital_comparison
    if h.current_score is not None
    and h.baseline_score is not None
    and h.baseline_total > 0          # ← ADR-012
]
```

Uitgesloten ziekenhuizen worden gelogd via `logger.info` als "nieuwe instappers".

### Alternatieven overwogen

| Optie | Omschrijving | Reden verworpen/gekozen |
|---|---|---|
| A | Uitsluiten + loggen | ✅ **Gekozen** — eerlijk en transparant; geen vals beeld |
| B | Drempelwaarde: min. 3 baseline-tickets vereist | ❌ Arbitrair getal, moeilijk te onderbouwen |
| C | Delta tonen maar markeren met `*` (nieuw) | ❌ Verhoogt complexiteit rendering; misleidend voor lezers die noten missen |
| D | Niets doen | ❌ Leidt tot foutieve interpretaties in managementrapportage |

### Consequenties

- **Visueel:** ziekenhuizen die nieuw zijn in 2026 (voor een bepaalde pijler) verschijnen
  niet in de delta-ranking — dit is correct en eerlijk
- **Log:** bij elke render wordt een `logger.info`-regel aangemaakt met de namen van
  uitgesloten nieuwe instappers
- **Backlog:** een toekomstige verbetering kan nieuwe instappers **apart visualiseren**
  als een extra sectie of tabel (met huidige score, zonder delta-vergelijking).
  Zie `docs/02-tactisch/fasen/fase3d-evolutie-visualisatie.md §4.4` voor de backlog-noot.

### Betrokken bestanden

| Bestand | Wijziging |
|---|---|
| `src/csat/utils/zorgi_theme.py` | `ZORGI_BORDEAUX = "#722F37"` gedefinieerd als functionele uitbreiding |
| `src/csat/core/exporters/evolution_visualiser.py` | `_draw_subplot4_hospitals()` — filter uitgebreid met `baseline_total > 0`; importeert `ZORGI_BORDEAUX` uit `zorgi_theme` |
| `tests/core/test_evolution_visualiser.py` | Test `test_subplot4_nieuwe_instappers_uitgesloten` toegevoegd |
| `docs/02-tactisch/fasen/fase3d-evolutie-visualisatie.md` | §4.4 bijgewerkt; backlog-noot toegevoegd |

### Kleurverantwoording `ZORGI_BORDEAUX`

`ZORGI_BORDEAUX = "#722F37"` is een functionele uitbreiding op het officiële ZORGI Design System:

- **Niet** in `PHARMA-Conventions/zorgi/zorgi_design_system.md` opgenomen
- Bewust gekozen als visueel neutraal tussenpunt op de ZORGI-gradient
  (Dark Blue `#003a70` → Purple `#7f4267` → Red `#dc2b26`)
- Voldoende contrast op `ZORGI_ULTRA_LIGHT` (`#d7e7f3`) achtergrond
- Gedocumenteerd in `src/csat/utils/zorgi_theme.py` onder "Functionele uitbreidingen"

---

## 13. ADR-013 — Runner/library-structuur (scripts vs src vs tools)

**Datum:** 31/03/2026
**Status:** ✅ Approved

### Context

CSAT-Compass heeft drie mappen met uitvoerbare code: `scripts/`, `src/csat/` en `tools/`.
Zonder expliciete afbakening dreigt business logic te versnipperen over mappen,
wat hergebruik en testbaarheid belemmert.
De vraag stelde zich of alle `.py`-bestanden in `scripts/` niet eerder thuishoren in `src/csat/`.

### Beslissing

**Runner/library-patroon:** strikte scheiding van verantwoordelijkheden.

| Map | Rol | Taal |
| --- | --- | --- |
| `scripts/` | CLI-entrypoints — dunne wrappers, orkestratie, `argparse` | Python |
| `src/csat/` | Library — alle herbruikbare business logic, analyse, export, visualisatie | Python |
| `tools/` | Dev-tooling — lint, sync, geen productielogica | PowerShell |

**Richtlijn:**

- Scripts importeren vanuit `src/csat/` via `sys.path.insert(0, ROOT / "src")`.
- Scripts bevatten **geen** business logic — enkel argument-parsing en het aanroepen van `src/csat/`.
- `src/csat/` importeert **nooit** vanuit `scripts/`.
- `tools/` bevat geen Python-productiecode.

**Beslisregel voor nieuwe code:**

```text
Nieuwe functie/klasse/logica?      → src/csat/
Nieuw CLI-entrypoint (terminal)?   → scripts/
Nieuw dev-hulpmiddel (PowerShell)? → tools/
```

### Alternatieven overwogen

| Optie | Reden afgewezen |
| --- | --- |
| Alles in `src/csat/cli/` | `pyproject.toml`-entrypoints vereist; extra complexiteit zonder meerwaarde in huidige fase |
| Scripts rechtstreeks in root | Rommelig; geen duidelijke scheiding voor nieuwe teamleden |
| Alles naar `src/` verplaatsen | Scripts zijn geen library-code — ze orkestreren; verplaatsing lost niets op |

### Consequenties

- Nieuwe CLI-functionaliteit → altijd eerst library-code in `src/csat/`, dan wrapper in `scripts/`
- 100% testbaarheid gegarandeerd: tests importeren direct vanuit `src/csat/` — geen `argparse`-overhead
- `scripts/README.md` documenteert alle entrypoints met rol en manual-verwijzing

### Betrokken bestanden

| Bestand | Rol |
| --- | --- |
| `scripts/README.md` | Overzicht van alle CLI-entrypoints (nieuw aangemaakt) |
| `docs/02-tactisch/implementatie-gids.md` | Sectie "Mapstructuur: scripts / src / tools" toegevoegd |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------------------------------------------- | -------------------- |
| 1.0 | 18/03/2026 | Initiële versie — 5 ADRs op basis van MCQ-sessie | Danny Depecker + GHC |
| 1.1 | 20/03/2026 | ADR-006 toegevoegd: reactiegraad niet meetbaar via V_CSAT_1 | Danny Depecker |
| 1.2 | 20/03/2026 | ADR-007 toegevoegd: analyseperiode en ONBEKEND hospital | Danny Depecker + GHC |
| 1.3 | 22/03/2026 | ADR-008 toegevoegd: mapstructuur en mapfilosofie | Danny Depecker + GHC |
| 1.4 | 22/03/2026 | ADR-009 toegevoegd: AVG_SCORE_MIN drempelwaarde = 4,00 | Danny Depecker + GHC |
| 1.5 | 23/03/2026 | ADR-010 toegevoegd: ZORGI Design System integratie en kleurbeleid | Danny Depecker + Claude |
| 1.6 | 25/03/2026 | ADR-011 toegevoegd: satisfaction_date als CSAT-periodegroepering | Danny Depecker + GHC |
| 1.7 | 25/03/2026 | ADR-012 toegevoegd: nieuwe instappers uitsluiten uit delta-ranking subplot 4 | Danny Depecker + GHC |
| 1.8 | 25/03/2026 | ADR-012 uitgebreid: ZORGI_BORDEAUX kleurverantwoording + zorgi_theme.py als betrokken bestand | Danny Depecker + GHC |
| 1.9 | 31/03/2026 | ADR-013 toegevoegd: runner/library-structuur scripts vs src vs tools | Danny Depecker + GHC |
