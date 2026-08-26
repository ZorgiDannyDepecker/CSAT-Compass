# CSAT-Compass - Fase 7: Maandelijkse Distributie-Automatisering (PHARMA)  

**Versie:** 1.3
**Laatst bijgewerkt:** 26/08/2026

**Doel:** Plan van aanpak voor de geautomatiseerde maandelijkse generatie en distributie van CSAT-rapporten aan de PHARMA-collega's
**Type:** Planning
**Auteur:** Danny Depecker + Claude
**Status:** Volledig afgerond — Deel A, B en C allemaal ingesteld en getest, wacht enkel nog op de eerste live cyclus (02/09/2026)
**Bestandsnaam:** fase7-maandelijkse-distributie.md
**Path:** docs/02-tactisch/fasen/

> **Vervolgt op:** `docs/03-operationeel/cowork-onepager.md` (Deel A + B, ontworpen maar nog niet live)

---

## Inhoudsopgave  

1. [Uitgangssituatie](#1-uitgangssituatie-gecontroleerd-op-24082026)
2. [Scope en fasering](#2-scope-en-fasering)
3. [Architectuur](#3-architectuur)
4. [Gap-analyse](#4-gap-analyse)
5. [Stappenplan Fase 7A (A+B)](#5-stappenplan-fase-7a-deel-ab---doel-02092026)
6. [Rolverdeling](#6-rolverdeling)
7. [Risico's en mitigatie](#7-risicos-en-mitigatie)
8. [Fase 7B — Deel C (later, apart te bekijken)](#8-fase-7b--deel-c-later-apart-te-bekijken)

---

## 1. Uitgangssituatie (gecontroleerd op 24/08/2026)  

Voor dit plan is het project rechtstreeks geïnspecteerd via de Filesystem-koppeling.  
Bevindingen:  

| Onderdeel | Status | Bewijs |
| --- | --- | --- |
| `run_monthly.py` (matrix + evolutie, alle 5 pijlers, NL+FR) | ✅ Werkt, productierijp | `_run_log.txt`: succesvolle run 15/06/2026, 30 bestanden, 60,1s |
| `insights_generator.py` (regelgebaseerde narratieve laag) | ✅ Bestaat al, rijk uitgewerkt | Executive summary, kritieke bevindingen, aanbevelingen — volledig regelgebaseerd, geen LLM nodig |
| PDF-conversie (`md_to_pdf.py`, WeasyPrint + pywin32) | ✅ Werkt, gedeeld met Q&A-Lab | Gebruikt door `generate_and_print.py`, ook los inzetbaar via `--batch` |
| Cowork-ontwerp voor onepager (Deel A/B-split) | 🟡 Ontworpen, niet geactiveerd | Checklist in `cowork-onepager.md` volledig onaangevinkt |
| Laatste automatische run | 🔴 Loopt niet | Laatste outputmap: `output\2026-07-01\` — sindsdien niets, dus geen augustus-run |
| E-mail distributie (Deel C) | 🔴 Bestaat niet | Geen "mail"-gerelateerde bestanden gevonden in het volledige project |
| "Tendens"-stijl narratief rapport (zoals Erwin waardeert) | 🔴 Niet geautomatiseerd | De 4 AI-rapporten in de juli-mail zijn handmatig via Claude-chat gemaakt, geen scriptpad |
| Akkoord Tom De Laere | ✅ Binnen | Tom is akkoord met wat zijn teamleden (Thomas, Erwin) gemeld hebben |

**Belangrijkste implicatie:** de zwaarste bouwstenen (data, narratieve regelengine, PDF) staan al.  
Wat ontbreekt is precies wat nu gevraagd wordt: het activeren en afwerken van Deel A+B, met Deel C (distributie) als apart vervolgtraject.  

---

## 2. Scope en fasering  

Op vraag van Danny (24/08/2026) wordt dit traject in twee fasen geknipt:  

| Fase | Inhoud | Wanneer bekeken |
| --- | --- | --- |
| **Fase 7A** | Deel A (Windows Taakplanner: generatie + PDF) + Deel B (Cowork: onepager + tendens-samenvatting) volledig op punt zetten en live | Nu — doel 02/09/2026 |
| **Fase 7B** | Deel C (e-mail distributie naar Tom, Thomas, Erwin) | Pas nadat Fase 7A volledig afgerond en stabiel is |

> ⚠️ **Belangrijk:** de deadline van 02/09/2026 geldt voor Fase 7A.  
> Deel C wordt bewust niet mee op deze deadline gepland — dat voorkomt dat een nog niet beproefd mail-onderdeel het geheel vertraagt of onbetrouwbaar maakt.  

---

## 3. Architectuur  

Fase 7A bouwt volledig voort op het bestaande, ontworpen maar nog niet geactiveerde ontwerp uit `cowork-onepager.md`.  

```text
DEEL A — Windows Taakplanner (native, geen Claude-credits)
  _run_maandelijks.bat
  1. run_monthly.py       -> matrix + evolutie, alle pijlers, NL+FR
  2. md_to_pdf.py --batch -> alle nieuwe .md + .png naar PDF

DEEL B — Claude Cowork (sandbox, leest/schrijft enkel tekst)
  Taak: csat-onepager-maandelijks (UITGEBREID - zie 5.3)
  1. Lees nieuwste output\YYYY-MM-DD\ (ZORGI + PHARMA)
  2. Schrijf onepager-<periode>-nl.md   (Thomas' voorkeur)
  3. Schrijf tendens-<periode>-nl.md    (Erwin's voorkeur - NIEUW)

DEEL C — later, Fase 7B (zie hoofdstuk 8)
```

**Waarom dit de juiste architectuur is:**  

- Deel A is pure Windows-Python en draait via Taakplanner zonder dat een Claude-sessie open hoeft te staan.  
- Deel B (Cowork) is de enige stap die een levende Claude-instantie nodig heeft — precies waar dat waarde toevoegt (narratieve duiding).  
- Door Deel C bewust apart te houden, kan Fase 7A op zichzelf getest en stabiel gemaakt worden vóór er een distributierisico bijkomt.  

---

## 4. Gap-analyse  

Enkel de onderdelen relevant voor Fase 7A (Deel A+B):  

| # | Onderdeel | Bestaat al? | Actie |
| --- | --- | --- | --- |
| 1 | Data + matrix + evolutie genereren | ✅ Ja | Geen — hergebruiken |
| 2 | Narratieve regelengine (executive summary, bevindingen) | ✅ Ja (`insights_generator.py`) | Geen — hergebruiken |
| 3 | PDF-conversie | ✅ Ja (`md_to_pdf.py`) | Geen — hergebruiken |
| 4 | Cowork-taak: onepager genereren | 🟡 Ontworpen, niet actief | Activeren (checklist afwerken) |
| 5 | Cowork-taak: tendens-stijl rapport genereren | 🔴 Ontbreekt | Nieuw — prompt uitbreiden (zie 5.3) |
| 6 | Taakplanner-trigger Deel A | 🟡 Ontworpen, niet actief | Activeren |
| 7 | Testcyclus vóór go-live | 🔴 Nog niet gedaan | Verplicht vóór 02/09 |

*Deel C (mail-samenstelling, ontvangerslijst, Taakplanner-trigger Deel C) verschuift naar Fase 7B — zie hoofdstuk 8.*  

---

## 5. Stappenplan Fase 7A (Deel A+B) - doel 02/09/2026  

Vandaag is maandag 24/08/2026.  
Beschikbare werkdagen: 25, 26, 27, 28, 31/08 en 01/09.  

### 5.1 Dag 1 — ma 25/08: Beslissingen bevestigen  

- [x] Akkoord Tom De Laere binnen — geen verdere blokkade op teamniveau.
- [x] Trigger-moment bevestigd: dag 2 van de maand in plaats van dag 1 zoals oorspronkelijk in `cowork-onepager.md` ontworpen.  
  Dit geeft ticketdata van de laatste dag van de vorige maand een dag marge, en laat de eerste live run samenvallen met 02/09.  
  Verwerkt in `cowork-onepager.md` §A.2 en §B.2.  

### 5.2 Dag 2 — di 26/08: Deel A activeren (bestaand ontwerp)  

- [x] `_run_maandelijks.bat` aangemaakt conform `cowork-onepager.md` §A.1, python-pad geverifieerd (`.venv\Scripts\python.exe`, bevat zowel weasyprint als pywin32).
- [x] Handmatige testrun uitgevoerd door Danny — geslaagd, geen fouten in `_run_log.txt`, PDF's correct aangemaakt naast de bestaande .md/.png-bestanden.
- [x] Taakplanner-basistaak aangemaakt: maandelijks, dag 2, 07:00, met "zo snel mogelijk na gemiste activering" en "computer uit slaapstand halen" aangevinkt, netstroom-vereiste uitgevinkt (laptop, nooit aan de lader 's nachts). Via geforceerde Uitvoeren-test bevestigd (25/08/2026): alle 5 pijlers NL+FR gegenereerd, 20/20 bestanden succesvol naar PDF.

### 5.3 Dag 3 — wo 27/08: Deel B activeren + uitbreiden met tendens-formaat  

- [x] Cowork-taak `csat-onepager-maandelijks` aangemaakt en in Ask-modus getest (25/08/2026, dry-run op output\2026-08-25\ — nieuwste map op het testmoment, niet 2026-07-01).
- [x] Projectinstructies (§B.1) overgenomen.
- [x] **Kwaliteitsreview van de eerste dry-run (26/08/2026):** 2 problemen gevonden en gefixt — zie `cowork-onepager.md` §B.3 en `project-journal.md` entry 2026-08-26 voor volledige details en herkomst. Kort samengevat: ontbrekende minimum-n=5 bij hospital-rankings, en een tegenstrijdige interpretatie van de responstijd-correlatie in Executive Summary vs. Responstijd Analyse. Bijkomend: FR-onepager geschrapt, consistent gemaakt met de NL-only tendens.
- [x] **Nieuw:** taak-prompt (§B.3, bijgewerkt) uitgebreid met een derde output naast de twee onepagers: `tendens-<periode>-nl.md`, in de leesbare, verhalende stijl die Erwin waardeerde.
  Structuur: Executive Summary, Kritieke Bevindingen, Structurele Patronen, Tijdstrend, Responstijd, Negatieve Feedback, Aanbevelingen, KPI Dashboard, Follow-up, Conclusie — conform de bestaande handmatige `tendens.md`-prompts.  
- [x] Bron voor de tendens-inhoud vastgelegd: de al aanwezige narratieve secties uit `insights_generator.py`'s output (executive_summary, critical_findings, positive_developments, recommendations, follow_up_actions, turning_point_analysis, type_analysis_narrative, priority_analysis_narrative, response_time_narrative staan al in de gegenereerde evolutie-.md's).  
  Cowork herstructureert en verrijkt deze tot een leesbaar doorlopend rapport, in plaats van from scratch te heranalyseren.  
  Dat houdt het betrouwbaar en snel.  
- [x] Uitbreiding getest in Ask-modus (25/08/2026, op de dan-nieuwste augustus-data i.p.v. juli — zie toelichting hierboven) en herzien na inhoudelijke review (26/08/2026). Herziene run nog te bevestigen.

### 5.4 Dag 4 — vervroegd afgerond op 26/08/2026 (i.p.v. gepland do 28/08): Eerste ketentest Deel A + B  

- [x] Deel A → Deel B meermaals na elkaar gedraaid (25/08 en 26/08, meerdere cycli
  inclusief kwaliteitsfixes) — substantieel vervroegd t.o.v. de oorspronkelijke planning
  van do 28/08, dankzij een efficiënte testronde op 25-26/08.

#### ▶️ Oorspronkelijke ochtendchecklist (niet meer nodig — werk al gedaan, zie hieronder)

<details>
<summary>Details van de oorspronkelijk voorbereide checklist (achterhaald, opengeklapt ter referentie)</summary>

1. **Deel A draaien:** Taakplanner → rechtsklik "CSAT-Compass maandelijks" → Uitvoeren.
2. **Deel A verifiëren:** `_run_log.txt` — nieuw blok, geen `[FOUT]`.
3. **Deel B draaien, meteen na Deel A:** Cowork-taak "CSAT Onepager maandelijks" → Run now.
4. **Deel B verifiëren:** onepager + tendens correct aangemaakt, periode-formaat JJJJ-MM.

</details>

- [x] Opmaak van beide rapporten, PDF-kwaliteit en ZORGI-huisstijl gecontroleerd (18:44-run,
  25/08) — geen dubbele of ontbrekende bestanden.
- [x] Gevonden problemen gecorrigeerd: zie de volledige kwaliteitsronde in
  `project-journal.md`, entries 2026-08-26 t/m 2026-08-26 (3) (minimum-n, correlatie-
  richting, periode-naamgeving, Cowork-scheduling).

### 5.5 Dag 5 — vervroegd afgerond op 26/08/2026 (i.p.v. gepland vr 29/08 of ma 31/08): Generale repetitie  

- [x] Volledige keten meermaals herhaald via de Taakplanner- en Cowork-triggers zelf
  (handmatig gestart, niet gewacht op de klok) — inclusief een expliciete niet-dag-2-test
  van Deel B (26/08, 11:15) die correct gedrag bevestigde.
- [x] Onepager + tendens bevestigd correct aanwezig in de nieuwste `output\YYYY-MM-DD\`-map,
  meermaals over verschillende dagen (2026-08-25 en 2026-08-26).

### 5.6 Dag 6 — vervroegd afgerond op 26/08/2026 (i.p.v. gepland ma 31/08 of di 01/09): Laatste controle  

- [x] Volledige checklist van `cowork-onepager.md` (Deel A + B) aangevinkt.
- [x] Taakplanner-trigger op dag 2, 07:00 bevestigd correct ingesteld (screenshot-verificatie
  25/08/2026, incl. voorwaarden afgestemd op laptop/slaapstand-situatie).

### 5.7 02/09 — Go-live Fase 7A  

- [ ] Taakplanner draait automatisch (dag 2, 07:00 gevolgd door de Cowork-taak).
- [ ] Danny controleert de output in de nieuwste outputmap.
- [x] ~~Distributie... gebeurt voorlopig nog handmatig~~ — **ingehaald:** Deel C (Fase 7B) is
  op 26/08/2026 al gebouwd en getest, dus de eerste live cyclus op 02/09 omvat meteen ook
  de automatische mail-distributie (zie §8).

---

## 6. Rolverdeling  

| Rol | Verantwoordelijkheid | Waarom |
| --- | --- | --- |
| Claude Desktop (dit gesprek) | Architectuur, dit plan, review van tussentijdse outputs | Advisory-first, geen implementatie hier conform de vaste werkwijze |
| Claude Cowork | Maandelijkse narratieve samenvatting: onepager + tendens | Enige stap die levende Claude-redenering nodig heeft; sandbox, leest/schrijft enkel tekst |
| Windows Taakplanner | Orchestratie van Deel A, zonder Claude-afhankelijkheid | Betrouwbaarheid op de deadline zelf — geen afhankelijkheid van sessie-beschikbaarheid |
| Danny | Activeren van Taakplanner-taken, review van eerste runs, handmatige distributie tot Fase 7B live is | Human-in-the-loop tijdens de opstartperiode |

---

## 7. Risico's en mitigatie  

| Risico | Mitigatie |
| --- | --- |
| Tendens-formaat (nieuw) haalt kwaliteit van de handmatige chat-versie niet | Dag 3 expliciet als aparte stap met eigen dry-run; hergebruik bestaande `insights_generator.py`-output in plaats van from-scratch generatie |
| Taakplanner-timing dag 1 versus dag 2 | Bewust gekozen voor dag 2 — lost tegelijk de deadline-datum op en geeft data een dag marge |
| Cowork-sandbox kan geen Windows-scripts draaien | Al opgelost in het bestaande ontwerp (Deel A/B-split) — overgenomen |
| Geen enkele testcyclus vóór go-live | Dag 4 en 5 zijn expliciet dry-runs op bestaande juli-data |
| Handmatige distributie na 02/09 wordt vergeten of vertraagd | Danny blijft tot Fase 7B live is de expliciete eigenaar van de laatste stap (versturen) |

---

## 8. Fase 7B — Deel C (opgestart 26/08/2026)  

Deel C (e-mail distributie) wordt opgestart nadat Fase 7A volledig afgerond en stabiel gebleken is — bevestigd op 26/08/2026 na meerdere geslaagde Deel A→B-cycli en de opgeloste kwaliteits- en scheduling-problemen (zie `project-journal.md`, entries 2026-08-26 t/m 2026-08-26 (3)).  

**Definitieve beslissingen (26/08/2026):**

- **Bijlagen:** enkel `onepager-<periode>-nl.pdf` + `tendens-<periode>-nl.pdf`. Geen data-driven
  PDF's (matrix/evolutie ZORGI+PHARMA) als bijlage — die blijven beschikbaar in de outputmap
  voor wie dieper wil kijken, maar worden niet meegestuurd.
- **Taal van de mail:** enkel NL (de rapporten zelf blijven zoals ingesteld — onepager en
  tendens zijn sowieso al NL-only sinds §6a/26/08).
- **Verzendmodus:** volautomatisch `.Send()` vanaf de eerste live cyclus (02/09) — geen
  `.Display()`-tussenstap. Bewuste afwijking van het oorspronkelijke voorzichtige voorstel;
  mitigatie: Danny staat in **CC** op elke verstuurde mail voor vroege detectie van problemen.
- **PDF-conversie van onepager/tendens:** gebeurt binnen Deel C zelf, vóór de mail wordt
  samengesteld (zie beslissing van eerder op 26/08/2026, hierboven in dit document).
- **BACKLOG-007 (26/08/2026):** bewust **niet** aangemaakt als formeel backlog-bestand.
  De drie potentiële vervolgpunten (uitbreiding naar CARE/CARE ADMIN/ERP4HC, data-driven
  PDF's alsnog als bijlage, meldingsmechanisme bij mislukte run door niet-aangemelde sessie)
  blijven als informele notitie in dit document en in `project-journal.md` staan — geen van
  de drie is dringend of risicovol genoeg om nu een apart bestand voor te openen.

**Architectuur (definitief):**  

- Nieuw script `scripts/mail_maandelijks.py`, zelfde runner/library-patroon als de rest van `scripts/`.
- Converteert eerst `onepager-<periode>-nl.md` en `tendens-<periode>-nl.md` naar PDF (via
  `md_to_pdf.py`, zelfde aanpak als Deel A), daarna verzamelt het enkel die 2 PDF's als bijlage.
- Stelt een Outlook-mail samen via `win32com.client.Dispatch("Outlook.Application")` — zelfde
  pywin32-stack als `md_to_pdf.py`, geen nieuwe dependency.
- Ontvangers: Tom De Laere, Thomas Wyckstandt, Erwin Casier. Danny in **CC**.
- Verstuurt volautomatisch via `.Send()` — geen `.Display()`-tussenstap.

**Openstaande beslissingen voor bij opstart Fase 7B:**  

- ~~Definitieve ontvangerslijst en formaat-mix bevestigen~~ — **bevestigd 26/08/2026, zie boven**
- ~~Taal van de distributiemail~~ — **bevestigd 26/08/2026, zie boven**
- ~~Moment van overschakelen van `.Display()` naar volautomatisch `.Send()`~~ —
  **bevestigd 26/08/2026: meteen volautomatisch, met CC-mitigatie, zie boven**
- ~~Eventueel `BACKLOG-007-maandelijkse-mail-distributie.md` aanmaken~~ —
  **beslist 26/08/2026: niet aanmaken, zie boven**

### 8.1 Bijkomend, niet-blokkerend aandachtspunt (later)  

Bij de Taakplanner-test van 25/08/2026 gaf `_run_log.txt` bij één van de 20 conversies
(`evolution-zorgi-2026-fr`) `????` in plaats van het 🚧-emoji in de logregel.  
De conversie zelf verliep normaal (`🟢 Succesvol geconverteerd` op de volgende regel) —
zuiver cosmetisch, intermitterend codepage-issue in `logger.info()` binnen
`C:\Users\danndepe\Documents\AI\Q&A-Lab\code\md_to_pdf.py`, ondanks `PYTHONIOENCODING=utf-8`.  

Bewust niet aangepakt vóór 02/09: `md_to_pdf.py` is een gedeeld, werkend productiebestand
(ook gebruikt door Q&A-Lab), en dit is geen functioneel probleem.  
Op te pakken na 02/09, met voldoende ruimte om een fix (bv. expliciete UTF-8-encoding op
de logging file-handler) rustig te testen op beide projecten.

**Definitief besluit (26/08/2026):** geen nadelen vastgesteld bij dit gewoon nooit actief
op te lossen — treft uitsluitend één decoratieve emoji in een intern logbestand dat enkel
Danny inkijkt, nooit de output naar Tom/Thomas/Erwin. Enkel oppakken bij toevallige
gelegenheid (als `md_to_pdf.py` om een andere reden alsnog bewerkt wordt) of als het aandeel
vaker dan dit ene geval zou beginnen voorkomen. Geen actieve opvolging gepland.

---

## Versiehistorie  

| Versie | Datum | Wijzigingen | Auteur |
| --- | --- | --- | --- |
| 1.0 | 24/08/2026 | Initieel plan van aanpak, gebaseerd op inspectie van bestaande projectstructuur | Danny Depecker + Claude |
| 1.1 | 24/08/2026 | Herschreven conform md-style-guide.md (header, kopstructuur, alinea- en zinsscheiding); scope gesplitst in Fase 7A (Deel A+B, doel 02/09) en Fase 7B (Deel C, later apart te bekijken); akkoord Tom De Laere verwerkt | Danny Depecker + Claude |
| 1.2 | 26/08/2026 | Fase 7A (Deel A+B) volledig afgerond en gedocumenteerd als voltooid (Dag 4-6 vervroegd, met bewijs); Fase 7B (Deel C) opgestart, gebouwd en getest — zie `project-journal.md` entries 2026-08-26 t/m (4) en `CHANGELOG.md` [0.9.4]-[0.9.8] voor volledige details | Danny Depecker + Claude |
| 1.3 | 26/08/2026 | Sessie-afsluiting: beide restpunten (md_to_pdf.py-encoding, BACKLOG-007) definitief besloten als niet-actief op te volgen; Fase 7 (A+B+C) volledig live en getest, wacht op eerste automatische cyclus 02/09/2026 | Danny Depecker + Claude |
