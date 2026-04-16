"""
Tests voor src/csat/core/calculations.py

Dekt:
- _build_window_frames(): "full" en "trend" venstermodus, current_month-afkap
- calc_hero_metrics_tickets(): hero-metrics per modus + fallback lege data
- calc_issue_type_comparison(): vergelijkingstabel per modus + randgevallen

Fixture: evolution_df (conftest.py) — bevat 2025 (jun+jul) en 2026 (jan+feb) data.
"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from csat.core.calculations import (
    _build_window_frames,
    calc_hero_metrics_tickets,
    calc_issue_type_comparison,
)

# ===========================================================================
# Hulpfuncties
# ===========================================================================


def _isnan(v) -> bool:
    """True als v float NaN is."""
    try:
        return math.isnan(v)
    except TypeError:
        return False


# ===========================================================================
# _build_window_frames
# ===========================================================================


class TestBuildWindowFrames:
    """Venstermodus-filtering: juiste rijen in df_prev en df_curr."""

    def test_full_prev_bevat_volledig_baseline_jaar(self, evolution_df):
        """mode='full': df_prev bevat 2025-tickets met satisfaction_date (5 rijen).

        EB-006 heeft satisfaction_date=NaT → valt buiten de filter → 5 van de 6 rijen.
        """
        df_prev, _ = _build_window_frames(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=12,
            trend_start_month=7,
        )
        assert len(df_prev) == 5
        jaren = pd.to_datetime(df_prev["satisfaction_date"].dropna()).dt.year.unique()
        assert list(jaren) == [2025]

    def test_trend_prev_bevat_alleen_s2_baseline(self, evolution_df):
        """mode='trend': df_prev bevat jul 2025-tickets met satisfaction_date (2 rijen).

        EB-006 heeft satisfaction_date=NaT → valt buiten de filter → 2 van de 3 jul-rijen.
        """
        df_prev, _ = _build_window_frames(
            evolution_df,
            mode="trend",
            baseline_year=2025,
            current_year=2026,
            current_month=12,
            trend_start_month=7,
        )
        assert len(df_prev) == 2
        mnd = pd.to_datetime(df_prev["satisfaction_date"].dropna()).dt.month.unique()
        assert all(m >= 7 for m in mnd)

    def test_curr_altijd_jan_tm_current_month(self, evolution_df):
        """df_curr bevat altijd alleen rijen t/m current_month van current_year."""
        _, df_curr = _build_window_frames(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=1,
            trend_start_month=7,
        )
        # Alleen jan 2026: EC-001 en EC-002
        assert len(df_curr) == 2
        mnd = pd.to_datetime(df_curr["satisfaction_date"]).dt.month.unique()
        assert list(mnd) == [1]

    def test_curr_met_two_maanden(self, evolution_df):
        """current_month=2 → jan + feb 2026 (4 rijen)."""
        _, df_curr = _build_window_frames(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
            trend_start_month=7,
        )
        assert len(df_curr) == 4

    def test_onbekende_mode_valt_terug_op_full(self, evolution_df):
        """Onbekende mode ('xyz') gebruikt 'full'-logica: volledig baseline-jaar."""
        df_prev_full, _ = _build_window_frames(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=12,
            trend_start_month=7,
        )
        df_prev_xyz, _ = _build_window_frames(
            evolution_df,
            mode="xyz",
            baseline_year=2025,
            current_year=2026,
            current_month=12,
            trend_start_month=7,
        )
        assert len(df_prev_full) == len(df_prev_xyz)


# ===========================================================================
# calc_hero_metrics_tickets
# ===========================================================================


class TestCalcHeroMetricsTickets:
    """Hero-metrics op basis van df_curr (YTD current year)."""

    def test_most_common_type_is_bug(self, evolution_df):
        """Bug komt het vaakst voor in 2026 YTD (EC-001 + EC-003 = 2 van 4)."""
        result = calc_hero_metrics_tickets(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        assert result["most_common_type"] == "Bug"
        assert result["most_common_type_pct"] == 50.0  # 2/4

    def test_lowest_score_type_niet_bug(self, evolution_df):
        """Bug heeft gem. 5.0★ in 2026 — laagst scorend is Question of Improvement (4.0★)."""
        result = calc_hero_metrics_tickets(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        assert result["lowest_score_type_value"] == pytest.approx(4.0)
        assert result["lowest_score_type"] != "Bug"

    def test_high_critical_pct_nul_in_2026(self, evolution_df):
        """Geen Blocker/Critical/Major tickets in 2026-data → high_critical_pct = 0."""
        result = calc_hero_metrics_tickets(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        assert result["high_critical_pct"] == 0.0
        assert result["high_critical_ok"] is True

    def test_current_month_filter_werkt(self, evolution_df):
        """current_month=1 vs current_month=2 → ander largest_priority_pct.

        Jan 2026 (2 tickets): Minor en Trivial elk 50%.
        Feb 2026 (4 tickets): Trivial = 3/4 = 75% → groter.
        """
        result_jan = calc_hero_metrics_tickets(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=1,
        )
        result_feb = calc_hero_metrics_tickets(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        assert result_jan["largest_priority_pct"] != result_feb["largest_priority_pct"]
        assert result_feb["largest_priority_pct"] == pytest.approx(75.0)  # Trivial: 3/4

    def test_mode_heeft_geen_effect_op_hero_metrics(self, evolution_df):
        """Hero-metrics gebruiken altijd df_curr — mode beïnvloedt enkel df_prev."""
        result_full = calc_hero_metrics_tickets(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        result_trend = calc_hero_metrics_tickets(
            evolution_df,
            mode="trend",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        assert result_full["most_common_type"] == result_trend["most_common_type"]
        assert result_full["high_critical_pct"] == result_trend["high_critical_pct"]

    def test_fallback_bij_lege_data(self, empty_df):
        """Lege data → fallback dict met standaardwaarden."""
        result = calc_hero_metrics_tickets(empty_df)
        assert result["most_common_type"] == "—"
        assert result["most_common_type_pct"] == 0.0
        assert result["high_critical_ok"] is True

    def test_retourneert_alle_verwachte_sleutels(self, evolution_df):
        """Dict bevat alle 10 verwachte sleutels."""
        verwacht = {
            "most_common_type",
            "most_common_type_pct",
            "lowest_score_type",
            "lowest_score_type_value",
            "largest_priority_group",
            "largest_priority_pct",
            "largest_priority_neg_pct",
            "high_critical_pct",
            "high_critical_ok",
            "high_critical_margin",
        }
        result = calc_hero_metrics_tickets(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        assert set(result.keys()) == verwacht


# ===========================================================================
# calc_issue_type_comparison
# ===========================================================================


class TestCalcIssueTypeComparison:
    """Vergelijkingstabel per issue type — baseline vs YTD."""

    def test_full_prev_bevat_alle_2025_types(self, evolution_df):
        """mode='full': score_prev gebaseerd op volledig 2025 → Bug gem. (2+3+4)/3=3.0."""
        result = calc_issue_type_comparison(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        bug_row = result[result["issue_type"] == "Bug"].iloc[0]
        assert bug_row["score_prev"] == pytest.approx(3.0)  # (2+3+4)/3

    def test_trend_prev_bevat_alleen_s2_2025(self, evolution_df):
        """mode='trend': score_prev Bug gebaseerd op jul 2025 → alleen EB-004 (4.0★)."""
        result = calc_issue_type_comparison(
            evolution_df,
            mode="trend",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
            trend_start_month=7,
        )
        bug_row = result[result["issue_type"] == "Bug"].iloc[0]
        assert bug_row["score_prev"] == pytest.approx(4.0)

    def test_question_nan_in_trend_mode(self, evolution_df):
        """mode='trend': Question heeft geen jul 2025-data → score_prev = NaN."""
        result = calc_issue_type_comparison(
            evolution_df,
            mode="trend",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
            trend_start_month=7,
        )
        q_row = result[result["issue_type"] == "Question"].iloc[0]
        assert _isnan(q_row["score_prev"])

    def test_score_curr_correct(self, evolution_df):
        """score_curr Bug in 2026 jan+feb: (5+5)/2 = 5.0."""
        result = calc_issue_type_comparison(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        bug_row = result[result["issue_type"] == "Bug"].iloc[0]
        assert bug_row["score_curr"] == pytest.approx(5.0)

    def test_delta_score_correct(self, evolution_df):
        """delta_score Bug full: 5.0 - 3.0 = +2.0."""
        result = calc_issue_type_comparison(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        bug_row = result[result["issue_type"] == "Bug"].iloc[0]
        assert bug_row["delta_score"] == pytest.approx(2.0)

    def test_delta_nan_als_een_score_nan_is(self, evolution_df):
        """delta_score = NaN als score_prev of score_curr NaN is."""
        result = calc_issue_type_comparison(
            evolution_df,
            mode="trend",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
            trend_start_month=7,
        )
        q_row = result[result["issue_type"] == "Question"].iloc[0]
        assert _isnan(q_row["delta_score"])

    def test_kolommen_aanwezig(self, evolution_df):
        """Resultaat bevat alle verwachte kolommen."""
        result = calc_issue_type_comparison(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        verwacht = {
            "issue_type",
            "score_prev",
            "score_curr",
            "pct_neg_curr",
            "delta_score",
            "delta_neg",
            "count_prev",
            "count_curr",
        }
        assert verwacht.issubset(set(result.columns))

    def test_gesorteerd_op_score_curr_oplopend(self, evolution_df):
        """Resultaat is gesorteerd op score_curr oplopend (laagste bovenaan)."""
        result = calc_issue_type_comparison(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        scores = result["score_curr"].dropna().tolist()
        assert scores == sorted(scores)

    def test_lege_data_geeft_leeg_dataframe(self, empty_df):
        """Lege invoer → leeg DataFrame met juiste kolommen."""
        result = calc_issue_type_comparison(empty_df)
        assert result.empty
        assert "issue_type" in result.columns

    def test_count_prev_en_curr_correct(self, evolution_df):
        """count_prev telt alleen tickets met satisfaction_date in 2025.

        2025 Bug met satisfaction_date: EB-001, EB-002, EB-004 = 3 tickets.
        EB-006 (Bug/jul 2025) heeft satisfaction_date=NaT → telt NIET mee.
        2026 Bug met satisfaction_date: EC-001, EC-003 = 2 tickets.
        """
        result = calc_issue_type_comparison(
            evolution_df,
            mode="full",
            baseline_year=2025,
            current_year=2026,
            current_month=2,
        )
        bug_row = result[result["issue_type"] == "Bug"].iloc[0]
        assert bug_row["count_prev"] == 3
        assert bug_row["count_curr"] == 2
