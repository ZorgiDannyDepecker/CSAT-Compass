"""
Unit tests voor DashboardExporter — Fase 5a.

Dekt alle publieke methoden en randgevallen van DashboardExporter en DashboardData.
Gebruikt de bestaande evolution_df fixture uit conftest.py.
"""

from __future__ import annotations

import pytest

from csat.core.analysers.evolution_analyser import EvolutionAnalyser
from csat.core.analysers.evolution_result import (
    EvolutionResult,
    HospitalComparison,
    KpiTarget,
    MonthlyDataPoint,
    NegativeCase,
    PriorityComparison,
)
from csat.core.exporters.dashboard_exporter import (
    DashboardData,
    DashboardExporter,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def pharma_result(evolution_df) -> EvolutionResult:
    """
    Volledig EvolutionResult voor de PHARMA-pijler op basis van evolution_df.

    baseline=["2025-06","2025-07"]  current=["2026-01","2026-02"]
    """
    analyser = EvolutionAnalyser(evolution_df, "pharma")
    return analyser.analyse(
        baseline_periods=["2025-06", "2025-07"],
        current_periods=["2026-01", "2026-02"],
    )


@pytest.fixture
def minimal_result() -> EvolutionResult:
    """Minimaal EvolutionResult voor randgeval-tests (leeg)."""
    return EvolutionResult(
        pillar="pharma",
        baseline_label="2025",
        current_label="2026",
        baseline_total=0,
        current_total=0,
        baseline_avg_score=0.0,
        current_avg_score=0.0,
        delta_avg_score=0.0,
        baseline_pct_positive=0.0,
        current_pct_positive=0.0,
        baseline_pct_negative=0.0,
        current_pct_negative=0.0,
        baseline_avg_response_days=0.0,
        current_avg_response_days=0.0,
        baseline_n_hospitals=0,
        current_n_hospitals=0,
        baseline_hc_ratio=0.0,
        current_hc_ratio=0.0,
        trend_is_structural=False,
        trend_breadth="gemengd",
    )


# ---------------------------------------------------------------------------
# Tests — DashboardExporter.prepare() globaal
# ---------------------------------------------------------------------------


class TestPrepareGlobal:
    """Tests voor DashboardExporter.prepare() — basisgedrag."""

    def test_prepare_returns_dashboard_data(self, pharma_result):
        """prepare() retourneert een DashboardData instance."""
        data = DashboardExporter.prepare(pharma_result)
        assert isinstance(data, DashboardData)

    def test_prepare_full_mode(self, pharma_result):
        """Zonder window_start is mode == 'full'."""
        data = DashboardExporter.prepare(pharma_result, window_start=None)
        assert data.mode == "full"
        assert data.window_start is None

    def test_prepare_trend_mode(self, pharma_result):
        """Met window_start is mode == 'trend'."""
        data = DashboardExporter.prepare(pharma_result, window_start="2025-07-01")
        assert data.mode == "trend"
        assert data.window_start == "2025-07-01"

    def test_prepare_pillar_info(self, pharma_result):
        """Pillar-metadata correct ingevuld."""
        data = DashboardExporter.prepare(pharma_result)
        assert data.pillar == "pharma"
        assert data.pillar_name == "ZORGI PHARMA"
        assert data.pillar_color == "#609fce"

    def test_prepare_labels(self, pharma_result):
        """Baseline- en current-labels worden doorgegeven."""
        data = DashboardExporter.prepare(pharma_result)
        assert data.baseline_label == pharma_result.baseline_label
        assert data.current_label == pharma_result.current_label

    def test_prepare_raw_result(self, pharma_result):
        """raw bevat het originele EvolutionResult."""
        data = DashboardExporter.prepare(pharma_result)
        assert data.raw is pharma_result

    def test_prepare_minimal_result(self, minimal_result):
        """prepare() faalt niet op een leeg result."""
        data = DashboardExporter.prepare(minimal_result)
        assert isinstance(data, DashboardData)
        assert data.kpi_avg_score == 0.0
        assert data.kpi_responses_total == 0


# ---------------------------------------------------------------------------
# Tests — KPI-kaarten
# ---------------------------------------------------------------------------


class TestKpiCards:
    """Tests voor de 8 KPI-kaarten in de DashboardData."""

    def test_kpi_avg_score(self, pharma_result):
        """kpi_avg_score == current_avg_score uit het result."""
        data = DashboardExporter.prepare(pharma_result)
        assert data.kpi_avg_score == pharma_result.current_avg_score

    def test_kpi_delta_full_mode(self, pharma_result):
        """Volledig venster: delta t.o.v. baseline_avg_score."""
        data = DashboardExporter.prepare(pharma_result)
        expected = round(pharma_result.current_avg_score - pharma_result.baseline_avg_score, 2)
        assert data.kpi_avg_score_delta == expected

    def test_kpi_delta_trend_mode_uses_benchmark_h2(self, pharma_result):
        """Tendensvenster: delta t.o.v. benchmark_h2 (als aanwezig)."""
        if pharma_result.benchmark_h2 is None:
            pytest.skip("Geen benchmark_h2 beschikbaar in testdata")
        data = DashboardExporter.prepare(pharma_result, "2025-07-01")
        bh2 = pharma_result.benchmark_h2
        expected = round(pharma_result.current_avg_score - bh2.avg_score, 2)
        assert data.kpi_avg_score_delta == expected

    def test_kpi_delta_trend_fallback_to_baseline(self, minimal_result):
        """Tendensvenster zonder benchmark_h2 → fallback naar baseline."""
        assert minimal_result.benchmark_h2 is None
        data = DashboardExporter.prepare(minimal_result, "2025-07-01")
        expected = round(minimal_result.current_avg_score - minimal_result.baseline_avg_score, 2)
        assert data.kpi_avg_score_delta == expected

    def test_kpi_pct_positive(self, pharma_result):
        """kpi_pct_positive == current_pct_positive."""
        data = DashboardExporter.prepare(pharma_result)
        assert data.kpi_pct_positive == pharma_result.current_pct_positive

    def test_kpi_pct_negative(self, pharma_result):
        """kpi_pct_negative == current_pct_negative."""
        data = DashboardExporter.prepare(pharma_result)
        assert data.kpi_pct_negative == pharma_result.current_pct_negative

    def test_kpi_responses_total(self, pharma_result):
        """kpi_responses_total == current_total."""
        data = DashboardExporter.prepare(pharma_result)
        assert data.kpi_responses_total == pharma_result.current_total

    def test_kpi_critical_accounts_nonnegative(self, pharma_result):
        """kpi_critical_accounts >= 0."""
        data = DashboardExporter.prepare(pharma_result)
        assert data.kpi_critical_accounts >= 0

    def test_kpi_targets_met_tuple(self, pharma_result):
        """kpi_targets_met <= kpi_targets_total."""
        data = DashboardExporter.prepare(pharma_result)
        assert 0 <= data.kpi_targets_met <= data.kpi_targets_total


# ---------------------------------------------------------------------------
# Tests — _filter_timeline
# ---------------------------------------------------------------------------


class TestFilterTimeline:
    """Tests voor tijdlijnfiltering op window_start."""

    def _make_pts(self, periods: list[str]) -> list[MonthlyDataPoint]:
        return [
            MonthlyDataPoint(
                period=p, avg_score=4.0, total_tickets=10, pct_negative=5.0, fase="S2 2025"
            )
            for p in periods
        ]

    def test_no_filter_returns_all_sorted(self):
        """Zonder window_start worden alle punten gesorteerd teruggegeven."""
        pts = self._make_pts(["2026-01", "2025-03", "2025-11"])
        result = DashboardExporter._filter_timeline(pts, None)
        assert [p.period for p in result] == ["2025-03", "2025-11", "2026-01"]

    def test_filter_cuts_before_window(self):
        """Punten vóór window_start worden uitgefilterd."""
        pts = self._make_pts(["2025-06", "2025-07", "2025-08", "2026-01"])
        result = DashboardExporter._filter_timeline(pts, "2025-07-01")
        periods = [p.period for p in result]
        assert "2025-06" not in periods
        assert "2025-07" in periods
        assert "2026-01" in periods

    def test_filter_result_sorted(self):
        """Gefilterd resultaat is gesorteerd op periode."""
        pts = self._make_pts(["2026-01", "2025-09", "2025-07", "2025-06"])
        result = DashboardExporter._filter_timeline(pts, "2025-07-01")
        assert result == sorted(result, key=lambda p: p.period)

    def test_empty_timeline(self):
        """Lege tijdlijn geeft lege lijst terug."""
        assert DashboardExporter._filter_timeline([], None) == []
        assert DashboardExporter._filter_timeline([], "2025-07-01") == []


# ---------------------------------------------------------------------------
# Tests — _best_month
# ---------------------------------------------------------------------------


class TestBestMonth:
    def _make_pt(self, period: str, score: float, tickets: int = 10) -> MonthlyDataPoint:
        return MonthlyDataPoint(
            period=period, avg_score=score, total_tickets=tickets, pct_negative=5.0, fase="S2 2025"
        )

    def test_returns_best_score(self):
        """Geeft de periode met de hoogste score terug."""
        pts = [
            self._make_pt("2026-01", 4.0),
            self._make_pt("2026-02", 4.8),
            self._make_pt("2025-12", 3.5),
        ]
        label, _score = DashboardExporter._best_month(pts)
        assert label == "2026-02"
        assert _score == 4.8

    def test_ignores_zero_tickets(self):
        """Maanden zonder tickets worden genegeerd."""
        pts = [self._make_pt("2026-01", 5.0, tickets=0), self._make_pt("2026-02", 4.0, tickets=5)]
        label, _score = DashboardExporter._best_month(pts)
        assert label == "2026-02"

    def test_empty_returns_dash(self):
        """Lege lijst geeft ('—', 0.0) terug."""
        assert DashboardExporter._best_month([]) == ("—", 0.0)


# ---------------------------------------------------------------------------
# Tests — _calc_streak
# ---------------------------------------------------------------------------


class TestCalcStreak:
    def _make_pt(self, period: str, score: float, tickets: int = 10) -> MonthlyDataPoint:
        return MonthlyDataPoint(
            period=period, avg_score=score, total_tickets=tickets, pct_negative=5.0, fase="S2 2025"
        )

    def test_streak_all_above_threshold(self):
        """Alle maanden >= 4.0 → streak == aantal maanden."""
        pts = [self._make_pt(f"2026-0{i}", 4.5) for i in range(1, 4)]
        assert DashboardExporter._calc_streak(pts) == 3

    def test_streak_broken_in_middle(self):
        """Onderbreking in het midden geeft alleen de recente reeks."""
        pts = [
            self._make_pt("2025-10", 4.5),
            self._make_pt("2025-11", 3.0),  # Onderbreking
            self._make_pt("2025-12", 4.2),
            self._make_pt("2026-01", 4.5),
        ]
        # Meest recent (2026-01, 2025-12) >= 4.0 → streak=2 (2025-11 breekt de keten)
        assert DashboardExporter._calc_streak(pts) == 2

    def test_streak_zero_if_latest_below_threshold(self):
        """Recentste maand < 4.0 → streak 0."""
        pts = [self._make_pt("2026-01", 3.8), self._make_pt("2026-02", 3.5)]
        assert DashboardExporter._calc_streak(pts) == 0

    def test_empty_tickets_skipped(self):
        """Maanden zonder tickets worden overgeslagen."""
        pts = [
            self._make_pt("2025-12", 4.5),
            self._make_pt("2026-01", 4.0, tickets=0),  # Overgeslagen
            self._make_pt("2026-02", 4.3),
        ]
        # Meest recent: 2026-02 (4.3 >=4) → check, 2026-01 (0 tickets) skip, 2025-12 (4.5>=4) → streak=2
        assert DashboardExporter._calc_streak(pts) == 2

    def test_empty_timeline(self):
        """Lege tijdlijn geeft streak 0."""
        assert DashboardExporter._calc_streak([]) == 0


# ---------------------------------------------------------------------------
# Tests — _count_critical_accounts
# ---------------------------------------------------------------------------


class TestCountCriticalAccounts:
    def _make_hc(self, name: str, score: float | None, total: int) -> HospitalComparison:
        return HospitalComparison(
            hospital=name,
            baseline_score=3.0,
            baseline_total=5,
            current_score=score,
            current_total=total,
        )

    def test_counts_below_threshold(self):
        """Telt ziekenhuizen met score < 3.0 en tickets > 0."""
        comps = [
            self._make_hc("A", 2.0, 5),  # Kritiek
            self._make_hc("B", 2.4, 3),  # Kritiek
            self._make_hc("C", 3.0, 4),  # Net niet kritiek (grens exclusief)
            self._make_hc("D", 4.0, 10),  # OK
        ]
        assert DashboardExporter._count_critical_accounts(comps) == 2

    def test_ignores_none_score(self):
        """Ziekenhuizen zonder current_score worden genegeerd."""
        comps = [self._make_hc("A", None, 5), self._make_hc("B", 1.0, 3)]
        assert DashboardExporter._count_critical_accounts(comps) == 1

    def test_ignores_zero_tickets(self):
        """Ziekenhuizen met 0 tickets worden genegeerd."""
        comps = [self._make_hc("A", 2.0, 0), self._make_hc("B", 2.0, 5)]
        assert DashboardExporter._count_critical_accounts(comps) == 1

    def test_empty_list(self):
        """Lege lijst geeft 0."""
        assert DashboardExporter._count_critical_accounts([]) == 0


# ---------------------------------------------------------------------------
# Tests — _count_targets_met
# ---------------------------------------------------------------------------


class TestCountTargetsMet:
    def _make_target(self, name: str, on_track: bool) -> KpiTarget:
        return KpiTarget(
            name=name,
            baseline=3.0,
            target=4.0,
            current=4.5 if on_track else 3.5,
            status="op_schema" if on_track else "kritiek",
            on_track=on_track,
        )

    def test_all_met(self):
        """Alle 3 score-targets bereikt."""
        targets = [
            self._make_target("avg_score_min", True),
            self._make_target("pct_positive_min", True),
            self._make_target("pct_negative_max", True),
            self._make_target("avg_response_days_max", False),  # Niet in telling
        ]
        met, total = DashboardExporter._count_targets_met(targets)
        assert met == 3
        assert total == 3

    def test_none_met(self):
        """Geen score-targets bereikt."""
        targets = [
            self._make_target("avg_score_min", False),
            self._make_target("pct_positive_min", False),
            self._make_target("pct_negative_max", False),
        ]
        met, total = DashboardExporter._count_targets_met(targets)
        assert met == 0
        assert total == 3

    def test_non_score_targets_excluded(self):
        """Targets buiten de set van 3 score-targets worden niet meegeteld."""
        targets = [self._make_target("avg_response_days_max", True)]
        met, total = DashboardExporter._count_targets_met(targets)
        assert total == 0
        assert met == 0

    def test_empty_list(self):
        """Lege lijst geeft (0, 0)."""
        assert DashboardExporter._count_targets_met([]) == (0, 0)


# ---------------------------------------------------------------------------
# Tests — _build_top3 / _build_bottom3
# ---------------------------------------------------------------------------


class TestBuildSignalCards:
    def _make_hc(self, name: str, score: float, total: int) -> HospitalComparison:
        return HospitalComparison(
            hospital=name,
            baseline_score=3.0,
            baseline_total=5,
            current_score=score,
            current_total=total,
        )

    def test_top3_max_three_entries(self):
        """Top-3 bevat maximaal 3 items."""
        comps = [self._make_hc(f"ZH{i}", 4.5 - i * 0.1, 10) for i in range(6)]
        result = DashboardExporter._build_top3(comps)
        assert len(result) <= 3

    def test_top3_excludes_none_score(self):
        """Ziekenhuizen zonder score worden uitgesloten."""
        comps = [
            HospitalComparison("A", 3.0, 5, None, 0),
            self._make_hc("B", 4.8, 10),
        ]
        result = DashboardExporter._build_top3(comps)
        hospitals = [e.hospital for e in result]
        assert "A" not in hospitals
        assert "B" in hospitals

    def test_bottom3_disengagement_flag(self):
        """Disengagement-flag wordt correct gezet (score < 2.5 EN tickets < 6)."""
        comps = [
            self._make_hc("LIEGE", 2.0, 2),  # disengagement_risk=True
            self._make_hc("GENT", 2.4, 10),  # score < 2.5 maar > 6 tickets → False
            self._make_hc("BELOEIL", 2.5, 3),  # score == 2.5 → False (grens exclusief)
        ]
        result = DashboardExporter._build_bottom3(comps)
        liege = next((e for e in result if e.hospital == "LIEGE"), None)
        gent = next((e for e in result if e.hospital == "GENT"), None)
        assert liege is not None and liege.disengagement_risk is True
        assert gent is not None and gent.disengagement_risk is False

    def test_bottom3_empty(self):
        """Lege lijst geeft lege resultaten."""
        assert DashboardExporter._build_top3([]) == []
        assert DashboardExporter._build_bottom3([]) == []


# ---------------------------------------------------------------------------
# Tests — _build_comparison_rows
# ---------------------------------------------------------------------------


class TestBuildComparisonRows:
    def test_returns_five_rows(self, pharma_result):
        """Vergelijkingstabel bevat 5 rijen."""
        rows = DashboardExporter._build_comparison_rows(pharma_result)
        assert len(rows) == 5

    def test_row_metrics(self, pharma_result):
        """De 5 verwachte metriek-sleutels zijn aanwezig."""
        rows = DashboardExporter._build_comparison_rows(pharma_result)
        metrics = {r.metric for r in rows}
        expected = {"avg_score", "pct_positive", "pct_negative", "n_hospitals", "total_tickets"}
        assert metrics == expected

    def test_delta_format_with_sign(self, pharma_result):
        """Delta-strings beginnen altijd met '+' of '-'."""
        rows = DashboardExporter._build_comparison_rows(pharma_result)
        for row in rows:
            assert row.delta_value[0] in ("+", "-") or row.delta_value == "+0"


# ---------------------------------------------------------------------------
# Tests — _build_period_groups
# ---------------------------------------------------------------------------


class TestBuildPeriodGroups:
    def _make_pts(self, mapping: dict[str, tuple[float, int]]) -> list[MonthlyDataPoint]:
        """mapping = {period: (avg_score, total_tickets)}"""
        return [
            MonthlyDataPoint(
                period=p,
                avg_score=s,
                total_tickets=t,
                pct_negative=5.0,
                fase="S1 2025" if int(p.split("-")[1]) <= 6 else "S2 2025",
            )
            for p, (s, t) in mapping.items()
        ]

    def test_groups_h1_h2_q1(self):
        """Periodes worden correct ingedeeld in H1/H2/Q-groepen."""
        pts = self._make_pts(
            {
                "2025-01": (3.0, 10),
                "2025-06": (3.2, 8),
                "2025-07": (4.0, 12),
                "2025-12": (4.5, 15),
                "2026-01": (4.8, 20),
                "2026-03": (4.6, 18),
            }
        )
        groups = DashboardExporter._build_period_groups(pts, None)
        labels = [g.label for g in groups]
        assert "S1 2025" in labels
        assert "S2 2025" in labels
        assert "Q1 2026" in labels

    def test_trend_filter_applied(self):
        """Tendensvenster filtert periodes voor window_start eruit."""
        pts = self._make_pts(
            {
                "2025-04": (3.0, 10),  # < window_start → weggefilterd
                "2025-07": (4.0, 12),  # >= window_start → behouden
                "2026-01": (4.8, 20),
            }
        )
        groups = DashboardExporter._build_period_groups(pts, "2025-07-01")
        labels = [g.label for g in groups]
        assert "S1 2025" not in labels
        assert "S2 2025" in labels

    def test_avg_score_weighted_by_tickets(self):
        """Gemiddelde score wordt gewogen naar ticketvolume."""
        pts = self._make_pts(
            {
                "2025-07": (4.0, 10),
                "2025-08": (5.0, 10),
            }
        )
        groups = DashboardExporter._build_period_groups(pts, None)
        h2_group = next(g for g in groups if g.label == "S2 2025")
        # Gelijkmatig gewogen: (4.0*10 + 5.0*10) / 20 = 4.5
        assert h2_group.avg_score == pytest.approx(4.5, abs=0.01)

    def test_empty_timeline(self):
        """Lege tijdlijn geeft lege periode-groepen."""
        assert DashboardExporter._build_period_groups([], None) == []


# ---------------------------------------------------------------------------
# Tests — _trivial_stats
# ---------------------------------------------------------------------------


class TestTrivialStats:
    def test_returns_trivial_data(self):
        """Geeft correct avg_score en pct_neg voor Trivial terug."""
        priorities = [
            PriorityComparison("Blocker", 2.0, 30.0, 4.0, 5.0),
            PriorityComparison("Trivial", 3.5, 20.0, 4.2, 14.7),
        ]
        avg, neg = DashboardExporter._trivial_stats(priorities)
        assert avg == 4.2
        assert neg == 14.7

    def test_returns_zero_if_no_trivial(self):
        """Geeft (0.0, 0.0) als Trivial niet aanwezig is."""
        priorities = [PriorityComparison("Blocker", 2.0, 30.0, 3.5, 20.0)]
        assert DashboardExporter._trivial_stats(priorities) == (0.0, 0.0)

    def test_empty_list(self):
        """Lege lijst geeft (0.0, 0.0)."""
        assert DashboardExporter._trivial_stats([]) == (0.0, 0.0)


# ---------------------------------------------------------------------------
# Tests — _build_hospital_bottom5
# ---------------------------------------------------------------------------


class TestBuildHospitalBottom5:
    def _make_hc(self, name: str, score: float, total: int) -> HospitalComparison:
        return HospitalComparison(
            hospital=name,
            baseline_score=3.0,
            baseline_total=5,
            current_score=score,
            current_total=total,
        )

    def _make_case(self, hospital: str, category: str) -> NegativeCase:
        return NegativeCase(
            ticket_id="SD-001",
            hospital=hospital,
            issue_type="Bug",
            score=2,
            response_days=5.0,
            category=category,
            comment="Test",
        )

    def test_dominant_cause_derived_from_cases(self):
        """Oorzaak = meest voorkomende categorie per ziekenhuis."""
        bottom = [self._make_hc("LIEGE", 2.0, 3)]
        cases = [
            self._make_case("LIEGE", "responstijd"),
            self._make_case("LIEGE", "responstijd"),
            self._make_case("LIEGE", "communicatie"),
        ]
        result = DashboardExporter._build_hospital_bottom5(bottom, cases)
        assert len(result) == 1
        assert result[0].cause == "responstijd"

    def test_disengagement_risk_flag(self):
        """Disengagement = score < 2.5 EN tickets < 6."""
        bottom = [
            self._make_hc("A", 2.0, 2),  # risk=True
            self._make_hc("B", 2.0, 10),  # risk=False (>= 6 tickets)
            self._make_hc("C", 2.5, 3),  # risk=False (score >= 2.5)
        ]
        result = DashboardExporter._build_hospital_bottom5(bottom, [])
        a = next(r for r in result if r.hospital == "A")
        b = next(r for r in result if r.hospital == "B")
        c = next(r for r in result if r.hospital == "C")
        assert a.disengagement_risk is True
        assert b.disengagement_risk is False
        assert c.disengagement_risk is False

    def test_skips_none_score(self):
        """Ziekenhuizen zonder current_score worden overgeslagen."""
        bottom = [
            HospitalComparison("A", 3.0, 5, None, 0),
            self._make_hc("B", 2.0, 5),
        ]
        result = DashboardExporter._build_hospital_bottom5(bottom, [])
        assert all(r.hospital != "A" for r in result)

    def test_no_cases_empty_cause(self):
        """Zonder negative_cases is de oorzaak een lege string."""
        bottom = [self._make_hc("GENT", 2.5, 8)]
        result = DashboardExporter._build_hospital_bottom5(bottom, [])
        assert result[0].cause == ""

    def test_empty_inputs(self):
        """Lege bottom-lijst geeft lege output."""
        assert DashboardExporter._build_hospital_bottom5([], []) == []


# ---------------------------------------------------------------------------
# Tests — _build_period_groups volledig via prepare()
# ---------------------------------------------------------------------------


class TestPreparePeriodGroups:
    def test_full_mode_has_h1_h2_groups(self, pharma_result):
        """Volledig venster bevat H1 en H2 groepen."""
        data = DashboardExporter.prepare(pharma_result)
        labels = {g.label for g in data.period_groups}
        # evolution_df heeft 2025-06 en 2025-07 → S1 2025 en S2 2025
        assert "S1 2025" in labels
        assert "S2 2025" in labels

    def test_trend_mode_no_h1(self, pharma_result):
        """Tendensvenster (jul 2025 →) bevat geen S1 2025."""
        data = DashboardExporter.prepare(pharma_result, "2025-07-01")
        labels = {g.label for g in data.period_groups}
        assert "S1 2025" not in labels

    def test_period_groups_avg_score_positive(self, pharma_result):
        """Alle periode-groepen hebben een avg_score >= 0."""
        data = DashboardExporter.prepare(pharma_result)
        for g in data.period_groups:
            assert g.avg_score >= 0.0
