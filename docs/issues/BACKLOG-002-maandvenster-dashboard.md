# BACKLOG-002 — Maandvenster toevoegen aan dashboard

**Status:** Open
**Prioriteit:** Medium
**Aangemaakt:** 14/04/2026
**Context:** Sessie "dashboard uitbreiding vensters"

## Achtergrond

Het dashboard biedt momenteel twee tijdsvensters:

- **Volledig venster** — alle beschikbare historische data
- **Tendensvenster** — recente trendperiode (rolling window)

Een derde venster werd gevraagd:

- **Maandvenster** — gefocust op één kalendermaand (selecteerbaar of meest recente maand)

Dit sluit aan bij de maandelijkse rapportagecyclus (SD30) en laat toe om de maandresultaten
rechtstreeks in het dashboard te bekijken zonder te moeten schakelen naar de maandrapport-pipeline.

## Scope

- Dashboard-pipeline (`dashboard_exporter.py` en/of `evolution_exporter.py`)
- Mogelijke aanpassingen aan `EvolutionAnalyser` voor maandfiltering
- UI-aanpassing in de gegenereerde HTML (extra tabblad of toggle naast Volledig/Tendensvenster)

## Functionele vereisten

1. **Maandselectie:** standaard = meest recente beschikbare maand; optioneel selecteerbaar via parameter
2. **Weergave:** zelfde KPI-structuur als de bestaande vensters (sterren, ratios, comment_ratio, enz.)
3. **Naamgeving:** consistent met bestaande vensterterminologie (bv. `maandvenster`, `month_window`)
4. **Tweetaligheid:** label zowel in NL (`Maandoverzicht`) als FR (`Aperçu mensuel`) voorzien

## Technische aandachtspunten

- Filterlogica: `df[df["maand"] == geselecteerde_maand]` of equivalent op datumkolom
- Geen impact op bestaande vensters — addief, niet vervangend
- Parameters via `config.py` of inline bij `DashboardExporter`-aanroep

## Wanneer oppakken

Bij de volgende uitbreiding van de dashboard-exportpipeline of bij start van fase 5b/5c.
