# BACKLOG-003 — Totaal aantal Jira-tickets weergeven naast CSAT-sterren

**Status:** Open
**Prioriteit:** Hoog
**Aangemaakt:** 14/04/2026
**Laatst bijgewerkt:** 20/04/2026
**Context:** Sessie "contextualisering CSAT-scores"

## Achtergrond

Momenteel toont het dashboard CSAT-scores (sterren + negatieve/positieve ratio's) zonder de
absolute context van het totale ticketvolume vanuit Jira (project SD30).

Dit leidt tot potentieel misleidende interpretaties:

| Negatieve tickets | Totaal Jira-tickets | Interpretatie |
|---|---|---|
| 1 | 50 | ✅ Niet relevant — 2% negatief |
| 10 | 50 | ❌ Problematisch — 20% negatief |
| 1 | 5 | ⚠️ Aandacht — 20% negatief |

Zonder het totale Jira-volume is het onmogelijk om de CSAT-scores correct te wegen.

## Databron: V_CSAT_2

**Update 20/04/2026:** Er is een nieuwe databaseview `V_CSAT_2` beschikbaar die het volledige
Jira-ticketvolume bevat (alle tickets, niet enkel de CSAT-beoordeelde). Dit is de beoogde
databron voor deze feature en voor meerdere toekomstige grafieken.

**Belangrijke beperking:** `V_CSAT_2` mag **geen DEV-tickets** bevatten in de analyses.
DEV-tickets dienen uitgefilterd te worden bij elke query op `V_CSAT_2`.

> **Filterregel:** `WHERE project_type != 'DEV'` (of equivalent, afhankelijk van de exacte
> kolomnaam in `V_CSAT_2` — te bevestigen bij implementatie).

De bestaande `V_CSAT_1` blijft de primaire databron voor CSAT-scores (ongewijzigd).
`V_CSAT_2` wordt enkel gebruikt als aanvullende databron voor het totale ticketvolume.

## Functionele vereisten

1. **Databron:** `V_CSAT_2` — totaal aantal tickets per ziekenhuis/periode (excl. DEV)
2. **Weergave in dashboard:** naast (of onder) de sterren een kolom/cel met `Jira-tickets: N`
3. **Ratio-berekening:** automatisch `negatieve CSAT-tickets / totaal Jira-tickets` als nieuwe KPI
   - Werknaam: `csat_jira_ratio` of `relevantie_ratio`
   - Drempelwaarden (voorstel): < 5% = groen, 5–15% = oranje, > 15% = rood
4. **Tweetaligheid:**
   - NL: `Jira-tickets`, `Relevantieratio`
   - FR: `Tickets Jira`, `Ratio de pertinence`

## Technische aandachtspunten

- **Nieuwe view in `settings.py`:** `DB_VIEW_2 = os.getenv("CSAT_DB_VIEW_2", "V_CSAT_2")`
- **DEV-filter verplicht:** elke query op `V_CSAT_2` filtert DEV-tickets uit — te encapsuleren
  in een aparte data-accessmethode zodat de filterregel niet verspreid raakt over de codebase
- **Koppeling CSAT ↔ Jira:** join op periode + ziekenhuis tussen `V_CSAT_1` en `V_CSAT_2`
- **Nieuwe KPI in `KpiResult`:** veld `total_jira_tickets: int = 0` + `csat_jira_ratio: float = 0.0`
- **`BaseAnalyser`:** nieuwe methode `_calc_csat_jira_ratio(csat_count, jira_total)`
- **Dashboard:** nieuwe kolom of badge zichtbaar in alle drie vensters (volledig, tendensvenster, maandvenster)
- **Rapporten:** ook in NL/FR markdown-rapporten opnemen (tabel uitbreiden)

## Afhankelijkheden

- `V_CSAT_2` beschikbaar en toegankelijk via `ZRG0014WI/Lerni_DB` ✅ (bevestigd 20/04/2026)
- Exacte kolomnaam voor DEV-filter in `V_CSAT_2` te bevestigen bij implementatie
- Afstemmen met BACKLOG-002 (maandvenster) voor consistente weergave in alle vensters

## Wanneer oppakken

Databron is beschikbaar. Blocker is nog de bevestiging van de exacte kolomnaam voor de
DEV-filter in `V_CSAT_2`. Technische implementatie kan daarna in één fase.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
|---|---|---|---|
| 0.1 | 14/04/2026 | Initieel document | Danny Depecker |
| 0.2 | 20/04/2026 | Databron bijgewerkt naar `V_CSAT_2` + DEV-filterregel toegevoegd | Danny Depecker + CD |
