# 🧭 CSAT-Compass — maandelijkse rapportage

> Gesplitste opzet: **Windows Taakplanner** genereert de rapporten + PDF's,
> **Claude Cowork** leest die en maakt een samenvatting + onepager + tendens-rapport.

---

## 🧩 Waarom gesplitst?

Cowork voert taken uit binnen een **Linux-VM** (de Claude Code-engine). Daarin
kunnen je Windows-`.venv` en `md_to_pdf.py` (pywin32 — Windows-only) **niet**
draaien. Daarom splitsen we het werk naar wat elke omgeving aankan:

| Deel | Wat | Waar | Waarom |
| --- | --- | --- | --- |
| A | Analyse + PDF-conversie | **Windows Taakplanner** | Windows-venv + pywin32 draaien native |
| B | Samenvatting + onepager + tendens-rapport | **Claude Cowork** | leest/schrijft enkel tekst → werkt in de sandbox |

**Status (24/08/2026):** Deel A is gebouwd (`_run_maandelijks.bat`) en handmatig
succesvol getest. Deel B moet nog geactiveerd worden. De Taakplanner-trigger
zelf staat nog uit — dat wordt later ingepland (zie `fase7-maandelijkse-distributie.md`).

---

## 🪟 Deel A — Windows: generatie + PDF (Taakplanner)

### A.1 — Het batch-bestand

Staat al klaar op:
`C:\Users\danndepe\Documents\AI\CSAT-Compass\_run_maandelijks.bat`

```bat
@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================== >> _run_log.txt
echo [Deel A] Maandelijkse run gestart: %date% %time% >> _run_log.txt
echo ============================================== >> _run_log.txt

REM --- Stap 1: matrix + evolutie genereren (alle pijlers, NL+FR) ---
echo Starten CSAT-Compass maandelijkse run...
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe scripts\run_monthly.py >> _run_log.txt 2>&1
IF ERRORLEVEL 1 (
    echo SQL-fout of andere fout gedetecteerd, opnieuw proberen met --force-csv... >> _run_log.txt
    set PYTHONIOENCODING=utf-8
    .venv\Scripts\python.exe scripts\run_monthly.py --force-csv >> _run_log.txt 2>&1
    IF ERRORLEVEL 1 (
        echo [FOUT] run_monthly.py definitief mislukt - Deel A afgebroken, geen PDF-conversie. >> _run_log.txt
        exit /b 1
    )
)

REM --- Stap 2: datum van vandaag bepalen, locale-onafhankelijk via PowerShell ---
for /f %%d in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "VANDAAG=%%d"

REM --- Stap 3: PDF-conversie van alle .md + .png in de datummap van vandaag ---
echo PDF-conversie starten voor output\%VANDAAG%... >> _run_log.txt
.venv\Scripts\python.exe "C:\Users\danndepe\Documents\AI\Q&A-Lab\code\md_to_pdf.py" -r "output\%VANDAAG%" >> _run_log.txt 2>&1
IF ERRORLEVEL 1 (
    echo [FOUT] PDF-conversie mislukt voor output\%VANDAAG% >> _run_log.txt
    exit /b 1
)

echo [Deel A] Klaar. Resultaat in output\%VANDAAG%\ en _run_log.txt >> _run_log.txt
echo Klaar. Resultaat in output\%VANDAAG%\ en _run_log.txt
```

> ✅ **Al geverifieerd:** `.venv\Scripts\python.exe` bevat zowel `weasyprint`
> als `pywin32` — dezelfde omgeving als je handmatige conversie. Geen apart
> python-pad nodig.

> ✅ **Handmatig getest op 25/08/2026 door Danny** — geslaagd, geen fouten in
> `_run_log.txt`, PDF's correct naast de bestaande .md/.png-bestanden.

### A.2 — Taakplanner (Nederlandse UI)

> ⏸️ **Nog niet ingesteld — bewust uitgesteld tot na afronding van Deel B.**
> Onderstaande stappen blijven staan als naslag voor wanneer dit wordt opgepakt.

1. Open **Taakplanner** → rechts **"Basistaak maken…"**.
2. **Naam:** `CSAT-Compass maandelijks`.
3. **Trigger:** *Maandelijks* → **dag 2** (niet dag 1 — geeft ticketdata van de
   laatste dag van de vorige maand een dag marge), tijd bv. **07:00**.
4. **Actie:** *Een programma starten* → blader naar `_run_maandelijks.bat`.
5. **Voltooien**. (Eventueel: eigenschappen → *Uitvoeren ongeacht of gebruiker
   is aangemeld* als het ook zonder sessie moet draaien.)

Deze stap draait native, verbruikt geen credits en werkt los van Claude Desktop.

---

## 🤖 Deel B — Cowork: lezen + samenvatten + onepager + tendens-rapport

> De oude **uitvoer-taak** ("Csat compass maandelijks") kan je verwijderen of op
> Manual/uit zetten — die blijft anders falen. We maken een **nieuwe** taak.

### B.1 — Projectinstructies (Instructions ✏️) — vervang de oude

```text
Context: dit project leest de CSAT-Compass-rapportage in de gekoppelde map
C:\Users\danndepe\Documents\AI\CSAT-Compass en maakt samenvattingen,
onepagers en tendens-rapporten.

Belangrijk — Cowork voert hier GEEN scripts uit:
- run_monthly.py en md_to_pdf.py zijn Windows-specifiek (Windows-venv + pywin32)
  en draaien native via Windows Taakplanner, niet in Cowork.
- Jouw taak is uitsluitend: bestaande output lezen en nieuwe tekstbestanden
  (samenvatting, onepager, tendens-rapport) schrijven. Niets uitvoeren, geen
  code wijzigen.

Conventies:
- Pijlers: zorgi (totaal), pharma, care, care_admin, erp4hc.
- Onderpresteerders dynamisch bepalen uit de data van deze maand (sites met een
  gemiddelde onder 3,0 ster; toon in elk geval de drie laagste). Geen vaste lijst.
- ZORGI-stijl: header-div bovenaan, emoji als visuele ankers, tweetalig NL/FR.
- De evolutie-.md-bestanden bevatten al kant-en-klare narratieve secties
  (executive_summary, critical_findings, positive_developments, recommendations,
  follow_up_actions, turning_point_analysis, type_analysis_narrative,
  priority_analysis_narrative, response_time_narrative) — gegenereerd door
  insights_generator.py. Hergebruik en herstructureer deze inhoud voor de
  onepager en het tendens-rapport in plaats van zelf opnieuw te analyseren.
- Schrijf outputbestanden in de nieuwste output\YYYY-MM-DD\ map.
```

### B.2 — Nieuwe taak aanmaken

- **New task** → **Name:** `csat-onepager-maandelijks`
- **Description:** `CSAT-Compass lezen, samenvatten, onepager + tendens-rapport maken`
- **Context:** map `…\AI\CSAT-Compass` (*from project*)
- **Mode:** *Ask* voor de eerste run; daarna mag automatisch
- **Frequency:** eerst **Manual** (testen), daarna **Daily**, 09:00 — niet Monthly:
  Cowork's scheduler ondersteunt geen Monthly-optie (enkel Manual/Hourly/Daily/Weekdays/
  Weekly). Weekly is bewust afgewezen: een vaste weekdag valt niet gegarandeerd ná dag 2
  van de Taakplanner-run (dag 1 van de maand kan toevallig die weekdag zijn, waardoor de
  taak vóór Deel A zou draaien op oude data). Daily lost dit op: dag 2 valt altijd binnen
  elke 7-dagen-cyclus, en de taak zelf bevat een datumcontrole (§B.3, stap 0) die enkel op
  dag 2 effectief iets doet en de overige 29 dagen meteen stopt. Zie
  `docs/project-journal.md`, entry "2026-08-26 (3)" voor de volledige afweging.

### B.3 — De taak-prompt (in het instructievak van de taak)

> **Herzien op 26/08/2026** (tweemaal), na de eerste dry-run op 25/08/2026 (periode 2026-08)
> en na de ontdekking dat Cowork's scheduler geen Monthly-optie heeft (stap 0 toegevoegd
> voor Daily + datumcontrole). Aanleiding en herkomst van elke wijziging staan in
> `docs/project-journal.md`, entry "2026-08-26 — Fase 7: kwaliteitsfixes na eerste Cowork
> dry-run" en entry "2026-08-26 (3)".

```text
Controleer EERST de datum van vandaag voor je iets anders doet.

0. Voer de volledige taak (stap 1 t.e.m. 7 hieronder) enkel uit als vandaag dag 2 van
   de kalendermaand is. Is dat niet het geval, meld dan enkel in de chat: "Vandaag is
   dag {dag} van de maand, geen actie nodig (enkel dag 2 triggert de volledige taak)."
   en stop onmiddellijk — voer geen van de volgende stappen uit, lees geen bestanden,
   schrijf niets weg. Dit voorkomt dat de taak op een verkeerde dag draait, vóór Deel A
   (Taakplanner, dag 2, 07:00) de dagverse data heeft klaargezet.

Lees de nieuwste CSAT-Compass-rapportage en maak een samenvatting, een
onepager en een tendens-rapport. Voer GEEN scripts uit en wijzig geen code —
enkel tekst lezen en schrijven.

1. Bepaal de nieuwste gedateerde map onder output\ (formaat YYYY-MM-DD).

2. Lees de NL-evolutierapporten van ZORGI (totaal) en PHARMA, inclusief de
   narratieve secties die insights_generator.py al genereerde (executive
   summary, kritieke bevindingen, aanbevelingen, turning-point-analyse,
   type- en priority-narratieven, responstijd-narratief).

3. Geef me in de chat een beknopte management-samenvatting (max. 10 regels):
   globale trend, opvallende bewegingen, en de onderpresteerders van deze maand
   — dynamisch uit de data (sites onder 3,0 ster; toon minstens de drie laagste),
   met per site de score, het ticketvolume en de evolutie t.o.v. vorige maand.

4. Schrijf een onepager naar diezelfde outputmap:
   onepager-<periode>-nl.md
   waarbij <periode> = JJJJ-MM van de rapportagemaand (bv. 2026-08 voor augustus 2026).
   Eén pagina, ZORGI-stijl (header-div + emoji-ankers). Enkel NL — geen FR-versie.
   Inhoud:
   - kop met overzicht ZORGI (totaal) + PHARMA: gem. score + delta t.o.v. baseline
   - 3 tot 5 kern-KPI's
   - top 3 positieve bewegingen en top 3 onderpresteerders van deze maand
   - 2 tot 3 concrete actiepunten

5. Schrijf een tendens-rapport naar diezelfde outputmap:
   tendens-<periode>-nl.md
   waarbij <periode> hetzelfde JJJJ-MM-formaat volgt als bij de onepager (punt 4) —
   gebruik in beide bestandsnamen exact dezelfde periode-waarde.
   Langere, doorlopende verhalende stijl (in tegenstelling tot de compacte
   onepager) met deze structuur:
   - Executive Summary
   - 🔴 Kritieke Bevindingen
   - 📊 Structurele Patronen (per Issue Type, per Priority, per Hospital)
   - 📈 Tijdstrend Analyse
   - ⏱️ Responstijd Analyse
   - ⚠️ Analyse van Negatieve Feedback
   - 🎯 Strategische Aanbevelingen
   - 📊 KPI Dashboard
   - 🔄 Follow-up Acties
   - 📝 Conclusie
   Bouw dit op vanuit de al aanwezige narratieve secties in de evolutie-.md's
   (zie projectinstructies) — herstructureer en verrijk deze tot doorlopende
   prose per sectie, herschrijf niet vanaf nul en verzin geen nieuwe cijfers.

6. KWALITEITSREGELS — verplicht toe te passen in zowel de onepager als het
   tendens-rapport, EN expliciet zichtbaar te vermelden in de output zelf
   (niet enkel stilzwijgend toepassen):

   a) Minimum-steekproefgrootte ziekenhuizen: neem een ziekenhuis enkel op in
      een top/bottom-ranking, sterkste-stijger/-daler-lijst, of vergelijkbare
      lijst als het minstens 5 tickets heeft in de periode waarover die
      ranking gaat. Ziekenhuizen met minder dan 5 tickets mag je wel losstaand
      vermelden (bv. als kanttekening), maar niet meetellen in een ranking.
      Vermeld ONDERAAN elke tabel/lijst waar dit relevant is een korte regel:
      "Ziekenhuizen met minder dan 5 tickets zijn uitgesloten van deze ranking."
      Als je er toch een vermeldt met een lager aantal (bv. als kanttekening
      bij een pijler-specifieke uitschieter), zet het aantal tickets er altijd
      expliciet bij.

   b) Correlatie-richting verifiëren: voor élke uitspraak over een verband
      tussen twee variabelen (bv. responstijd en score) waar je een
      correlatiecoëfficiënt (r) citeert: controleer eerst het teken van r
      voordat je de richting van het verband in woorden omschrijft.
      Een NEGATIEVE r betekent dat de twee variabelen tegengesteld bewegen
      (de ene stijgt terwijl de andere daalt). Een POSITIEVE r betekent dat ze
      samen bewegen (beide stijgen of beide dalen). Toets je eigen formulering
      aan de concrete cijfers waarop je je baseert (bv. gemiddelde responstijd
      bij positieve vs. negatieve scores) voor je de zin schrijft — bij een
      tegenspraak tussen de r-waarde en de concrete cijfers, ga uit van de
      concrete cijfers en meld dat expliciet in de tekst in plaats van de
      tegenspraak stilzwijgend op te lossen.

7. Meld welke bestanden je hebt aangemaakt.
```

> 💡 Een onepager of tendens-rapport als **PDF** voor collega's? Laat
> `md_to_pdf.py` die MD-bestanden gewoon mee converteren in Deel A (ze staan
> al in de outputmap), of converteer ze los wanneer nodig.

---

## ⚠️ Aandachtspunten

- **Cowork = enkel lezen/schrijven van tekst.** Geen Windows-scripts in Cowork.
- **Volgorde:** Cowork-taak ná de Taakplanner-run plannen (anders is er nog
  geen verse output om te lezen).
- **App open + pc wakker** geldt enkel voor de Cowork-taak (Deel B). Deel A
  draait sowieso via Taakplanner.
- **Onepager-taal:** enkel NL (FR geschrapt op 26/08/2026 — geen aangetoonde
  FR-behoefte bij Tom/Thomas/Erwin, consistent gemaakt met de tendens).
- **Tendens-rapport:** enkel NL (conform Erwin's feedback op de proefmail —
  geen FR-vraag geweest).
- **Trigger-dag:** bewust dag 2, niet dag 1 — zie `fase7-maandelijkse-distributie.md` §5.1.

---

## 📋 Checklist

- [x] Deel A: `_run_maandelijks.bat` opgeslagen + python-pad gecontroleerd
- [x] Deel A: handmatige testrun geslaagd
- [x] Deel A: Taakplanner-basistaak (maandelijks, dag 2, 07:00) ingesteld en via geforceerde Uitvoeren-test bevestigd (25/08/2026)
- [x] Oude Cowork-taak hernoemd naar "Csat onepager maandelijks_old version" (Repeats: Manual only — geen risico op automatische conflicterende run, dus behouden i.p.v. verwijderd)
- [x] Projectinstructies vervangen door de read-only versie (met tendens-vermelding)
- [x] Nieuwe taak `csat-onepager-maandelijks` aangemaakt
- [x] Eerste **Manual**-test in **Ask**-modus (25/08/2026, periode 2026-08) —
      3 bestanden correct aangemaakt, proces werkt end-to-end
- [x] Inhoudelijke review van de eerste dry-run — 2 kwaliteitsproblemen gevonden
      (zie §B.3-herziening + `project-journal.md` 2026-08-26): ontbrekende
      minimum-n bij hospital-rankings, tegenstrijdige correlatie-interpretatie
      in Executive Summary vs. Responstijd Analyse
- [x] Taakprompt (§B.3) herzien: kwaliteitsregels 6a/6b toegevoegd, FR-onepager geschrapt
- [x] Oude 3 testbestanden (`onepager-2026-08-nl.md`, `onepager-2026-08-fr.md`,
      `tendens-2026-08-nl.md`) verwijderd, herziene taak meermaals opnieuw gedraaid
      (25/08 18:44-run en 26/08 08:08-run)
- [x] Herziene run gecontroleerd: minimum-n zichtbaar vermeld en correlatie-richting
      consistent bevestigd in zowel ZORGI als PHARMA (18:44-run, en herbevestigd in de
      08:08-run van 26/08 na de bronfix in `insights_generator.py`)
- [x] Daarna Frequency op **Daily, 09:00** (ná de Taakplanner-run) — niet Monthly (bestaat niet in Cowork's scheduler)
