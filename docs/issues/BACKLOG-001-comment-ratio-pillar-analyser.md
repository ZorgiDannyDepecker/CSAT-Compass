# BACKLOG-001 — comment_ratio toevoegen aan PillarAnalyser

**Status:** Gesloten — geïmplementeerd 13/04/2026
**Prioriteit:** Laag — geen impact op dashboard
**Aangemaakt:** 13/04/2026
**Context:** Sessie "CSAT fase 5a kerncijfers" — besloten na tokenlimiet

## Achtergrond

Tijdens de implementatie van `% Tickets met Comment` als volwaardige KPI werd vastgesteld dat:

- `PCT_WITH_COMMENT_MIN` al volledig doorgetrokken is in de **EvolutionAnalyser**-pipeline (dashboard + rapporten fase 3g)
- De **PillarAnalyser** (`pillar_analyser.py`) berekent `comment_ratio` nog **niet** in `analyse()` en `analyse_ytd()`
- `KpiResult` heeft nog geen `comment_ratio`-veld
- `BaseAnalyser` heeft nog geen `_calc_comment_ratio()`-methode

## Scope

Enkel relevant voor de **maandrapport-pipeline** — geen impact op het dashboard.

### Prompt 2 — `base_analyser.py`

In `src/csat/core/analysers/base_analyser.py`:

1. In `KpiResult`, na `high_critical_ratio`, toevoegen:

   ```python
   comment_ratio: float = 0.0  # % tickets met een niet-lege comment
   ```

2. In `to_dict()`, na `"high_critical_ratio"`, toevoegen:

   ```python
   "comment_ratio": self.comment_ratio,
   ```

3. In `BaseAnalyser`, na `_calc_high_critical()`, nieuwe methode:

   ```python
   def _calc_comment_ratio(self, df: pd.DataFrame) -> float:
       """Bereken het percentage tickets met een niet-lege comment."""
       total = len(df)
       if total == 0:
           return 0.0
       with_comment = int(
           (df["comment"].notna() & (df["comment"].str.strip() != "")).sum()
       ) if "comment" in df.columns else 0
       return round(with_comment / total * 100, 1)
   ```

### Prompt 3 — `pillar_analyser.py`

In `src/csat/core/analysers/pillar_analyser.py`, in **beide** methoden `analyse()` en `analyse_ytd()`:

1. Na `_calc_high_critical()`-aanroep toevoegen:

   ```python
   comment_ratio = self._calc_comment_ratio(current_df)  # of ytd_df
   ```

2. In `KpiResult(...)`-constructor, na `high_critical_ratio=hc_ratio,`:

   ```python
   comment_ratio=comment_ratio,
   ```

3. In `logger.info` van `analyse()`, aan het einde toevoegen:

   ```text
   | comment {comment_ratio}%
   ```

## Wanneer oppakken

Bij de eerste sessie waarin `pillar_analyser.py` of de maandrapport-pipeline toch al wordt aangepast.
