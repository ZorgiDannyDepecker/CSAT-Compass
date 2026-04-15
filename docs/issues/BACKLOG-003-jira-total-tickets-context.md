# BACKLOG-003 — Totaal aantal Jira-tickets weergeven naast CSAT-sterren

**Status:** Open
**Prioriteit:** Hoog
**Aangemaakt:** 14/04/2026
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

## Functionele vereisten

1. **Databron:** totaal aantal tickets per ziekenhuis/periode rechtstreeks vanuit de SD30-export (CSV/Excel)
2. **Weergave in dashboard:** naast (of onder) de sterren een kolom/cel met `Jira-tickets: N`
3. **Ratio-berekening:** automatisch `negatieve CSAT-tickets / totaal Jira-tickets` als nieuwe KPI
   - Werknaam: `csat_jira_ratio` of `relevantie_ratio`
   - Drempelwaarden (voorstel): < 5% = groen, 5–15% = oranje, > 15% = rood
4. **Tweetaligheid:**
   - NL: `Jira-tickets`, `Relevantieratio`
   - FR: `Tickets Jira`, `Ratio de pertinence`

## Technische aandachtspunten

- **Koppeling CSAT ↔ Jira:** de SD30-export bevat beide databronnen of vereist een join op periode + ziekenhuis
- **Nieuwe KPI in `KpiResult`:** veld `total_jira_tickets: int = 0` + `csat_jira_ratio: float = 0.0`
- **`BaseAnalyser`:** nieuwe methode `_calc_csat_jira_ratio(csat_count, jira_total)`
- **Dashboard HTML:** nieuwe kolom of badge zichtbaar in alle drie vensters (volledig, tendensvenster, maandvenster)
- **Rapporten:** ook in NL/FR markdown-rapporten opnemen (tabel uitbreiden)

## Afhankelijkheden

- Vereist dat het totale Jira-ticketvolume beschikbaar is in de SD30-export of via een aparte kolom
- Eventueel afstemmen met BACKLOG-002 (maandvenster) voor consistente weergave

## Wanneer oppakken

Zodra bevestigd is welke kolom in de SD30-export het totale Jira-volume bevat (of hoe dit apart
aangeleverd wordt). Technische implementatie kan daarna in één fase.
