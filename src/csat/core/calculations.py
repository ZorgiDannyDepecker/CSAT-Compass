"""
CSAT-Compass -- Berekeningsfuncties voor dashboard-tabbladen.
Fase 5a: Hero-metrics en vergelijkingstabellen voor Tickets & Prioriteit.
Venstermodi (mode-parameter):
  "full"   -- volledig baseline-jaar vs huidig jaar YTD t/m current_month
  "trend"  -- S2 baseline-jaar (>=trend_start_month) vs huidig jaar YTD t/m current_month
  Toekomstige modussen kunnen hier worden toegevoegd als extra elif-takken.
"""

from __future__ import annotations

import math
from datetime import UTC
from datetime import datetime as _dt

import pandas as pd

from csat.config.pillars import HIGH_CRITICAL_PRIORITIES
from csat.config.settings import HIGH_CRITICAL_MAX

# Standaard startmaand voor de tendens-modus (S2 = juli)
_TREND_DEFAULT_START_MONTH: int = 7


def _build_window_frames(
    df: pd.DataFrame,
    mode: str,
    baseline_year: int,
    current_year: int,
    current_month: int,
    trend_start_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bouw df_prev en df_curr op basis van de venstermodus.
    Args:
        df:                 Volledig CSAT DataFrame met satisfaction_date-kolom.
        mode:               "full" of "trend" (uitbreidbaar).
        baseline_year:      Referentiejaar (bv. 2025).
        current_year:       Huidig jaar (bv. 2026).
        current_month:      Laatste afgeronde maand van current_year (1-12).
        trend_start_month:  Startmaand voor tendens-modus (standaard 7 = S2).
    Returns:
        (df_prev, df_curr) -- beide gefilterd op de juiste periode.
    """
    sat_dt = pd.to_datetime(df["satisfaction_date"])
    # df_curr: altijd jan t/m current_month van current_year
    mask_curr = (sat_dt.dt.year == current_year) & (sat_dt.dt.month <= current_month)
    df_curr = df[mask_curr].copy()
    # df_prev: afhankelijk van modus
    if mode == "trend":
        # S2 van baseline_year: trend_start_month t/m december
        mask_prev = (sat_dt.dt.year == baseline_year) & (sat_dt.dt.month >= trend_start_month)
    else:
        # "full" (en toekomstige onbekende modi): volledig baseline_year
        mask_prev = sat_dt.dt.year == baseline_year
    df_prev = df[mask_prev].copy()
    return df_prev, df_curr


def calc_hero_metrics_tickets(
    df: pd.DataFrame,
    mode: str = "full",
    baseline_year: int | None = None,
    current_year: int | None = None,
    current_month: int | None = None,
    trend_start_month: int = _TREND_DEFAULT_START_MONTH,
) -> dict:
    """Berekent de 4 hero-metrics voor het tabblad Tickets & Prioriteit.
    Hero-metrics zijn altijd gebaseerd op het lopende jaar YTD (df_curr).
    df_prev wordt meegegeven voor toekomstige delta-berekeningen.
    Args:
        df:                 Volledige CSAT DataFrame (satisfaction_date, issue_type,
                            priority, key, score).
        mode:               Venstermodus -- "full" of "trend".
        baseline_year:      Referentiejaar. Standaard: huidig jaar - 1.
        current_year:       Huidig jaar. Standaard: huidig jaar.
        current_month:      Laatste afgeronde maand. Standaard: vorige maand.
        trend_start_month:  Startmaand tendens-modus. Standaard: 7 (S2 = juli).
    Returns:
        dict met 10 sleutels: most_common_type, most_common_type_pct,
          lowest_score_type, lowest_score_type_value,
          largest_priority_group, largest_priority_pct, largest_priority_neg_pct,
          high_critical_pct, high_critical_ok, high_critical_margin.
    """
    today = _dt.now(tz=UTC).date()
    _current_year = current_year or today.year
    _baseline_year = baseline_year or (_current_year - 1)
    _current_month = current_month or (today.month - 1 or 12)
    _df_prev, df_curr = _build_window_frames(
        df, mode, _baseline_year, _current_year, _current_month, trend_start_month
    )
    # Fallback bij lege data
    if df_curr.empty:
        return {
            "most_common_type": "\u2014",
            "most_common_type_pct": 0.0,
            "lowest_score_type": "\u2014",
            "lowest_score_type_value": 0.0,
            "largest_priority_group": "\u2014",
            "largest_priority_pct": 0.0,
            "largest_priority_neg_pct": 0.0,
            "high_critical_pct": 0.0,
            "high_critical_ok": True,
            "high_critical_margin": round(HIGH_CRITICAL_MAX, 1),
        }
    total = len(df_curr)
    # T-A: meest voorkomend issue type
    type_counts = df_curr.groupby("issue_type")["key"].count()
    most_common_type = type_counts.idxmax()
    most_common_type_pct = round(type_counts.max() / total * 100, 1)
    # T-B: laagst scorend issue type
    scored = df_curr[df_curr["score"].notna()]
    if not scored.empty:
        type_scores = scored.groupby("issue_type")["score"].mean()
        lowest_score_type = type_scores.idxmin()
        lowest_score_type_value = round(float(type_scores.min()), 2)
    else:
        lowest_score_type = "\u2014"
        lowest_score_type_value = 0.0
    # T-C: grootste prioritaire groep
    prio_counts = df_curr.groupby("priority")["key"].count()
    largest_priority_group = prio_counts.idxmax()
    largest_priority_pct = round(prio_counts.max() / total * 100, 1)
    df_largest_prio = df_curr[df_curr["priority"] == largest_priority_group]
    largest_priority_neg_pct = round(
        len(df_largest_prio[df_largest_prio["score"] <= 2]) / len(df_largest_prio) * 100,
        1,
    )
    # T-D: % High/Critical (KPI)
    hc_df = df_curr[df_curr["priority"].isin(HIGH_CRITICAL_PRIORITIES)]
    high_critical_pct = round(len(hc_df) / total * 100, 1)
    high_critical_ok = high_critical_pct <= HIGH_CRITICAL_MAX
    high_critical_margin = round(HIGH_CRITICAL_MAX - high_critical_pct, 1)
    return {
        "most_common_type": most_common_type,
        "most_common_type_pct": most_common_type_pct,
        "lowest_score_type": lowest_score_type,
        "lowest_score_type_value": lowest_score_type_value,
        "largest_priority_group": largest_priority_group,
        "largest_priority_pct": largest_priority_pct,
        "largest_priority_neg_pct": largest_priority_neg_pct,
        "high_critical_pct": high_critical_pct,
        "high_critical_ok": high_critical_ok,
        "high_critical_margin": high_critical_margin,
    }


def calc_issue_type_comparison(
    df: pd.DataFrame,
    mode: str = "full",
    baseline_year: int | None = None,
    current_year: int | None = None,
    current_month: int | None = None,
    trend_start_month: int = _TREND_DEFAULT_START_MONTH,
) -> pd.DataFrame:
    """Berekent vergelijkingstabel per issue type: baseline-venster vs huidig jaar YTD.
    Kolommen: issue_type, score_prev, score_curr, pct_neg_curr,
               delta_score, delta_neg, count_prev, count_curr.
    Gesorteerd op score_curr oplopend (laagst scorend type bovenaan).
    Args:
        df:                 Volledige CSAT DataFrame.
        mode:               "full" of "trend" -- zie module-docstring.
        baseline_year:      Referentiejaar. Standaard: huidig jaar - 1.
        current_year:       Huidig jaar. Standaard: huidig jaar.
        current_month:      Laatste afgeronde maand. Standaard: vorige maand.
        trend_start_month:  Startmaand tendens-modus. Standaard: 7 (S2 = juli).
    """
    today = _dt.now(tz=UTC).date()
    _current_year = current_year or today.year
    _baseline_year = baseline_year or (_current_year - 1)
    _current_month = current_month or (today.month - 1 or 12)
    df_prev, df_curr = _build_window_frames(
        df, mode, _baseline_year, _current_year, _current_month, trend_start_month
    )
    if df_curr.empty and df_prev.empty:
        return pd.DataFrame(
            columns=[
                "issue_type",
                "score_prev",
                "score_curr",
                "pct_neg_curr",
                "delta_score",
                "delta_neg",
            ]
        )
    all_types = sorted(
        set(
            list(df_curr["issue_type"].dropna().unique())
            + list(df_prev["issue_type"].dropna().unique())
        )
    )
    rows = []
    for t in all_types:
        dc = df_curr[df_curr["issue_type"] == t]
        dp = df_prev[df_prev["issue_type"] == t]
        dc_scored = dc[dc["score"].notna()]
        dp_scored = dp[dp["score"].notna()]
        score_curr = (
            round(float(dc_scored["score"].mean()), 2) if not dc_scored.empty else float("nan")
        )
        score_prev = (
            round(float(dp_scored["score"].mean()), 2) if not dp_scored.empty else float("nan")
        )
        pct_neg_curr = (
            round(len(dc_scored[dc_scored["score"] <= 2]) / len(dc_scored) * 100, 1)
            if not dc_scored.empty
            else float("nan")
        )
        pct_neg_prev = (
            round(len(dp_scored[dp_scored["score"] <= 2]) / len(dp_scored) * 100, 1)
            if not dp_scored.empty
            else float("nan")
        )
        delta_score = (
            round(score_curr - score_prev, 2)
            if not math.isnan(score_curr) and not math.isnan(score_prev)
            else float("nan")
        )
        delta_neg = (
            round(pct_neg_curr - pct_neg_prev, 1)
            if not math.isnan(pct_neg_curr) and not math.isnan(pct_neg_prev)
            else float("nan")
        )
        rows.append(
            {
                "issue_type": t,
                "score_prev": score_prev,
                "score_curr": score_curr,
                "pct_neg_curr": pct_neg_curr,
                "delta_score": delta_score,
                "delta_neg": delta_neg,
                "count_prev": len(dp),
                "count_curr": len(dc),
            }
        )
    result = pd.DataFrame(rows)
    result = result[(result["count_prev"] > 0) | (result["count_curr"] > 0)]
    result = result.sort_values("score_curr", ascending=True, na_position="last")
    return result.reset_index(drop=True)


def calc_priority_comparison(
    df: pd.DataFrame,
    mode: str = "full",
    baseline_year: int | None = None,
    current_year: int | None = None,
    current_month: int | None = None,
    trend_start_month: int = _TREND_DEFAULT_START_MONTH,
) -> pd.DataFrame:
    """Berekent vergelijkingstabel per prioriteit: baseline-venster vs huidig jaar YTD.

    Vaste rij-volgorde: Blocker → Critical → Major → Minor → Trivial.
    Alle 5 rijen altijd aanwezig — NaN voor ontbrekende data.
    Kolommen: priority, score_prev, score_curr, pct_neg_curr,
               delta_score, delta_neg, count_prev, count_curr
    Args:
        df:                 Volledige CSAT DataFrame.
        mode:               "full" of "trend" -- zie module-docstring.
        baseline_year:      Referentiejaar. Standaard: huidig jaar - 1.
        current_year:       Huidig jaar. Standaard: huidig jaar.
        current_month:      Laatste afgeronde maand. Standaard: vorige maand.
        trend_start_month:  Startmaand tendens-modus. Standaard: 7 (S2 = juli).
    """
    priority_order = ["Blocker", "Critical", "Major", "Minor", "Trivial"]

    today = _dt.now(tz=UTC).date()
    _current_year = current_year or today.year
    _baseline_year = baseline_year or (_current_year - 1)
    _current_month = current_month or (today.month - 1 or 12)

    df_prev, df_curr = _build_window_frames(
        df, mode, _baseline_year, _current_year, _current_month, trend_start_month
    )

    rows = []
    for p in priority_order:
        dc = df_curr[df_curr["priority"] == p]
        dp = df_prev[df_prev["priority"] == p]
        dc_scored = dc[dc["score"].notna()]
        dp_scored = dp[dp["score"].notna()]

        score_curr = (
            round(float(dc_scored["score"].mean()), 2) if not dc_scored.empty else float("nan")
        )
        score_prev = (
            round(float(dp_scored["score"].mean()), 2) if not dp_scored.empty else float("nan")
        )
        pct_neg_curr = (
            round(len(dc_scored[dc_scored["score"] <= 2]) / len(dc_scored) * 100, 1)
            if not dc_scored.empty
            else float("nan")
        )
        pct_neg_prev = (
            round(len(dp_scored[dp_scored["score"] <= 2]) / len(dp_scored) * 100, 1)
            if not dp_scored.empty
            else float("nan")
        )
        delta_score = (
            round(score_curr - score_prev, 2)
            if not math.isnan(score_curr) and not math.isnan(score_prev)
            else float("nan")
        )
        delta_neg = (
            round(pct_neg_curr - pct_neg_prev, 1)
            if not math.isnan(pct_neg_curr) and not math.isnan(pct_neg_prev)
            else float("nan")
        )
        rows.append(
            {
                "priority": p,
                "score_prev": score_prev,
                "score_curr": score_curr,
                "pct_neg_curr": pct_neg_curr,
                "delta_score": delta_score,
                "delta_neg": delta_neg,
                "count_prev": len(dp),
                "count_curr": len(dc),
            }
        )

    return pd.DataFrame(rows)
