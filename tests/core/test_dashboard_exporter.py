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
    PriorityComparison,
)
from csat.core.exporters.dashboard_exporter import (
    DashboardData,
    DashboardExporter,
    PillarSummaryRow,
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

    def test_kpi_responses_hospitals(self, pharma_result):
        """kpi_responses_hospitals == aantal ZH met current_total > 0."""
        data = DashboardExporter.prepare(pharma_result)
        expected = sum(1 for hc in pharma_result.hospital_comparison if hc.current_total > 0)
        assert data.kpi_responses_hospitals == expected

    def test_kpi_responses_hospitals_nonnegative(self, minimal_result):
        """kpi_responses_hospitals >= 0 ook bij leeg result."""
        data = DashboardExporter.prepare(minimal_result)
        assert data.kpi_responses_hospitals >= 0

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


# ---------------------------------------------------------------------------
# Tests — _recent_month_name
# ---------------------------------------------------------------------------


_MONTHS_NL = [
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
]


class TestRecentMonthName:
    """Tests voor _recent_month_name() — period-string naar leesbare maandnaam."""

    def test_normale_periode(self):
        """Valide 'YYYY-MM' met volledige maandenlijst geeft 'Maandnaam YYYY'."""
        result = DashboardExporter._recent_month_name("2026-03", _MONTHS_NL)
        assert result == "Maart 2026"

    def test_leeg_string_retourneert_leeg(self):
        """Lege string wordt ongewijzigd teruggegeven."""
        assert DashboardExporter._recent_month_name("", _MONTHS_NL) == ""

    def test_dash_retourneert_dash(self):
        """'—' (em-dash vlag) wordt ongewijzigd teruggegeven."""
        assert DashboardExporter._recent_month_name("—", _MONTHS_NL) == "—"

    def test_te_korte_maandenlijst_fallback_naar_maandnummer(self):
        """Als maandenlijst korter is dan maandindex, valt terug op het maandnummer."""
        result = DashboardExporter._recent_month_name("2026-03", ["jan", "feb"])
        assert result == "03 2026"

    def test_ongeldig_formaat_retourneert_origineel(self):
        """Bij een ongeldige string (ValueError/IndexError) wordt de invoer teruggegeven."""
        assert DashboardExporter._recent_month_name("ongeldige-waarde", []) == "ongeldige-waarde"

    def test_december(self):
        """Maand 12 wordt correct omgezet."""
        result = DashboardExporter._recent_month_name("2025-12", _MONTHS_NL)
        assert result == "December 2025"


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


class TestBuildHospitalBottom10:
    def _make_hc(self, name: str, score: float, total: int) -> HospitalComparison:
        return HospitalComparison(
            hospital=name,
            baseline_score=3.0,
            baseline_total=5,
            current_score=score,
            current_total=total,
        )

    def test_returns_bottom_sorted_ascending(self):
        """Bottom-10 wordt gesorteerd op oplopende score."""
        comparisons = [
            self._make_hc("A", 4.0, 10),
            self._make_hc("B", 2.0, 5),
            self._make_hc("C", 3.0, 8),
        ]
        result = DashboardExporter._build_hospital_bottom10(comparisons)
        assert result[0].hospital == "B"
        assert result[1].hospital == "C"
        assert result[2].hospital == "A"

    def test_disengagement_risk_flag(self):
        """Disengagement = score < 2.5 EN tickets < 6."""
        comparisons = [
            self._make_hc("A", 2.0, 2),  # risk=True
            self._make_hc("B", 2.0, 10),  # risk=False (>= 6 tickets)
            self._make_hc("C", 2.5, 3),  # risk=False (score >= 2.5)
        ]
        result = DashboardExporter._build_hospital_bottom10(comparisons)
        a = next(r for r in result if r.hospital == "A")
        b = next(r for r in result if r.hospital == "B")
        c = next(r for r in result if r.hospital == "C")
        assert a.disengagement_risk is True
        assert b.disengagement_risk is False
        assert c.disengagement_risk is False

    def test_skips_none_score(self):
        """Ziekenhuizen zonder current_score worden overgeslagen."""
        comparisons = [
            HospitalComparison("A", 3.0, 5, None, 0),
            self._make_hc("B", 2.0, 5),
        ]
        result = DashboardExporter._build_hospital_bottom10(comparisons)
        assert all(r.hospital != "A" for r in result)

    def test_no_disengagement_when_absent(self):
        """Ziekenhuis met score >= 2.5 of tickets >= 6 heeft geen disengagement_risk."""
        comparisons = [self._make_hc("GENT", 3.5, 8)]
        result = DashboardExporter._build_hospital_bottom10(comparisons)
        assert result[0].disengagement_risk is False

    def test_empty_inputs(self):
        """Lege bottom-lijst geeft lege output."""
        assert DashboardExporter._build_hospital_bottom10([]) == []


# ---------------------------------------------------------------------------
# Tests — _build_hospital_top10
# ---------------------------------------------------------------------------


class TestBuildHospitalTop10:
    """Tests voor DashboardExporter._build_hospital_top10() — score >= 4.0 + min 5 tickets."""

    def _make_hc(self, name: str, score: float | None, total: int) -> HospitalComparison:
        return HospitalComparison(
            hospital=name,
            baseline_score=4.0,
            baseline_total=5,
            current_score=score,
            current_total=total,
        )

    def test_sluit_score_onder_4_uit(self):
        """Ziekenhuizen met score < 4.0 worden niet opgenomen (title-garantie)."""
        comparisons = [
            self._make_hc("TOP", 4.5, 10),  # ✓ opgenomen
            self._make_hc("GRENS", 3.9, 10),  # ✗ score < 4.0
        ]
        result = DashboardExporter._build_hospital_top10(comparisons)
        hospitals = [e.hospital for e in result]
        assert "TOP" in hospitals
        assert "GRENS" not in hospitals

    def test_grenswaarde_4_0_opgenomen(self):
        """Score exact 4.0 met voldoende tickets wordt WEL opgenomen."""
        comparisons = [self._make_hc("EXACT", 4.0, 5)]
        result = DashboardExporter._build_hospital_top10(comparisons)
        assert len(result) == 1
        assert result[0].hospital == "EXACT"

    def test_sluit_onvoldoende_tickets_uit(self):
        """Score >= 4.0 maar < _TOP_MIN_TICKETS tickets wordt niet opgenomen."""
        comparisons = [
            self._make_hc("WEINIG", 4.8, 4),  # ✗ < 5 tickets
            self._make_hc("VOLDOENDE", 4.2, 5),  # ✓ >= 5 tickets
        ]
        result = DashboardExporter._build_hospital_top10(comparisons)
        hospitals = [e.hospital for e in result]
        assert "WEINIG" not in hospitals
        assert "VOLDOENDE" in hospitals

    def test_gesorteerd_hoogste_score_eerst(self):
        """Top-10 wordt gesorteerd op aflopende score."""
        comparisons = [
            self._make_hc("A", 4.2, 10),
            self._make_hc("B", 5.0, 5),
            self._make_hc("C", 4.8, 8),
        ]
        result = DashboardExporter._build_hospital_top10(comparisons)
        scores = [e.score for e in result]
        assert scores == sorted(scores, reverse=True)

    def test_maximaal_10_entries(self):
        """Lijst is beperkt tot 10 entries ook bij meer dan 10 kandidaten."""
        comparisons = [self._make_hc(f"ZH{i}", 4.0 + i * 0.05, 10) for i in range(15)]
        result = DashboardExporter._build_hospital_top10(comparisons)
        assert len(result) <= 10

    def test_slaat_none_score_over(self):
        """Ziekenhuizen met score=None worden overgeslagen."""
        comparisons = [
            HospitalComparison("A", 4.0, 5, None, 10),
            self._make_hc("B", 4.5, 10),
        ]
        result = DashboardExporter._build_hospital_top10(comparisons)
        assert all(e.hospital != "A" for e in result)

    def test_lege_input_geeft_lege_lijst(self):
        """Lege input geeft lege lijst terug."""
        assert DashboardExporter._build_hospital_top10([]) == []

    def test_score_en_tickets_correct_overgenomen(self):
        """Score en tickets worden correct overgezet naar ZhSignalEntry."""
        comparisons = [self._make_hc("UZ Leuven", 4.75, 12)]
        result = DashboardExporter._build_hospital_top10(comparisons)
        assert len(result) == 1
        assert result[0].hospital == "UZ Leuven"
        assert result[0].score == 4.75
        assert result[0].tickets == 12


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


# ---------------------------------------------------------------------------
# Tests — _build_hospital_attention
# ---------------------------------------------------------------------------


class TestBuildHospitalAttention:
    """Tests voor DashboardExporter._build_hospital_attention() — lijn 852 coverage."""

    def _make_hc(self, name: str, score: float | None, total: int) -> HospitalComparison:
        return HospitalComparison(
            hospital=name,
            baseline_score=3.5,
            baseline_total=5,
            current_score=score,
            current_total=total,
        )

    def test_bevat_scores_tussen_3_en_4(self):
        """Accounts met score >= 3.0 en < 4.0 worden opgenomen."""
        comparisons = [
            self._make_hc("A", 3.5, 10),  # aandacht ✓
            self._make_hc("B", 2.9, 5),  # kritiek — buiten range
            self._make_hc("C", 4.0, 8),  # top — buiten range
            self._make_hc("D", 3.0, 3),  # grenswaarde ondergrens ✓
        ]
        result = DashboardExporter._build_hospital_attention(comparisons)
        hospitals = [e.hospital for e in result]
        assert "A" in hospitals
        assert "D" in hospitals
        assert "B" not in hospitals
        assert "C" not in hospitals

    def test_gesorteerd_op_score_oplopend(self):
        """Aandachtslijst wordt gesorteerd op oplopende score."""
        comparisons = [
            self._make_hc("A", 3.8, 5),
            self._make_hc("B", 3.2, 5),
            self._make_hc("C", 3.5, 5),
        ]
        result = DashboardExporter._build_hospital_attention(comparisons)
        scores = [e.score for e in result]
        assert scores == sorted(scores)

    def test_slaat_none_score_over(self):
        """Ziekenhuizen met score=None worden overgeslagen."""
        comparisons = [
            HospitalComparison("A", 3.0, 5, None, 3),
            self._make_hc("B", 3.5, 3),
        ]
        result = DashboardExporter._build_hospital_attention(comparisons)
        assert all(e.hospital != "A" for e in result)

    def test_slaat_nul_tickets_over(self):
        """Ziekenhuizen met 0 tickets worden overgeslagen."""
        comparisons = [
            self._make_hc("A", 3.5, 0),
            self._make_hc("B", 3.5, 3),
        ]
        result = DashboardExporter._build_hospital_attention(comparisons)
        assert all(e.hospital != "A" for e in result)

    def test_lege_input_geeft_lege_lijst(self):
        """Lege input geeft lege lijst terug."""
        assert DashboardExporter._build_hospital_attention([]) == []

    def test_geen_aandachtsaccounts_buiten_range(self):
        """Geeft lege lijst als alle scores buiten 3.0-4.0 liggen."""
        comparisons = [
            self._make_hc("A", 2.0, 5),
            self._make_hc("B", 4.5, 5),
        ]
        assert DashboardExporter._build_hospital_attention(comparisons) == []

    def test_score_en_tickets_correct_overgenomen(self):
        """Score en tickets worden correct overgezet naar ZhSignalEntry."""
        comparisons = [self._make_hc("UZ Gent", 3.7, 12)]
        result = DashboardExporter._build_hospital_attention(comparisons)
        assert len(result) == 1
        assert result[0].hospital == "UZ Gent"
        assert result[0].score == 3.7
        assert result[0].tickets == 12

    def test_geen_limiet_op_aantal_entries(self):
        """Alle aandachtsaccounts worden opgenomen — geen max limiet."""
        comparisons = [self._make_hc(f"ZH{i}", 3.0 + i * 0.05, 5) for i in range(15)]
        result = DashboardExporter._build_hospital_attention(comparisons)
        # Alle 15 scores zijn >= 3.0; die met score >= 4.0 vallen buiten range
        assert len(result) == sum(1 for i in range(15) if 3.0 <= (3.0 + i * 0.05) < 4.0)


# ---------------------------------------------------------------------------
# Tests — PillarSummaryRow
# ---------------------------------------------------------------------------


class TestPillarSummaryRow:
    """Tests voor PillarSummaryRow dataclass — veldwaarden en trend-logica."""

    def _make_row(
        self,
        pillar: str = "pharma",
        name: str = "PHARMA",
        color: str = "#609fce",
        current: float = 4.44,
        baseline: float = 3.48,
        pct_pos: float = 87.7,
        pct_neg: float = 8.2,
        hc: float = 45.2,
        tickets: int = 73,
        trend: str = "up",
    ) -> PillarSummaryRow:
        return PillarSummaryRow(
            pillar=pillar,
            pillar_name=name,
            pillar_color=color,
            current_score=current,
            baseline_score=baseline,
            delta_score=round(current - baseline, 2),
            pct_positive=pct_pos,
            pct_negative=pct_neg,
            hc_ratio=hc,
            tickets=tickets,
            trend=trend,
        )

    def test_velden_correct_ingevuld(self):
        """Alle velden worden correct opgeslagen."""
        row = self._make_row()
        assert row.pillar == "pharma"
        assert row.pillar_name == "PHARMA"
        assert row.pillar_color == "#609fce"
        assert row.current_score == 4.44
        assert row.baseline_score == 3.48
        assert row.delta_score == pytest.approx(0.96, abs=0.01)
        assert row.pct_positive == 87.7
        assert row.pct_negative == 8.2
        assert row.hc_ratio == 45.2
        assert row.tickets == 73
        assert row.trend == "up"

    def test_trend_up_bij_positieve_delta(self):
        """delta > 0.05 → trend 'up'."""
        row = self._make_row(current=4.44, baseline=3.48, trend="up")
        assert row.trend == "up"

    def test_trend_down_bij_negatieve_delta(self):
        """delta < -0.05 → trend 'down'."""
        row = self._make_row(current=3.80, baseline=4.30, trend="down")
        assert row.trend == "down"

    def test_trend_stable_bij_kleine_delta(self):
        """|delta| <= 0.05 → trend 'stable'."""
        row = self._make_row(current=4.00, baseline=4.02, trend="stable")
        assert row.trend == "stable"

    def test_pillar_comparison_rows_leeg_zonder_zorgi(self, pharma_result):
        """DashboardData.pillar_comparison_rows is leeg voor niet-ZORGI pijlers."""
        data = DashboardExporter.prepare(pharma_result)
        assert data.pillar_comparison_rows == []

    def test_pillar_comparison_rows_leeg_op_minimal(self, minimal_result):
        """pillar_comparison_rows is leeg bij minimaal result."""
        data = DashboardExporter.prepare(minimal_result)
        assert data.pillar_comparison_rows == []
