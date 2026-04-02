"""
DashboardExporter voor CSAT-Compass — Fase 5a.

Bereidt EvolutionResult-data voor voor het Streamlit-dashboard.
Geen Streamlit-afhankelijkheden — pure data-transformatie, volledig testbaar.

Gebruik:
    data = DashboardExporter.prepare(result)                    # Volledig venster
    data = DashboardExporter.prepare(result, "2025-07-01")      # Tendensvenster
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from csat.config.pillars import PILLAR_REGISTRY
from csat.core.analysers.evolution_result import (
    EvolutionResult,
    HospitalComparison,
    IssueTypeComparison,
    KpiTarget,
    MonthlyDataPoint,
    NegativeCase,
    PriorityComparison,
    ResponseTimeInsight,
    ResponseTimeRow,
    ThemeEvolution,
)
from csat.utils.date_utils import parse_period

# ---------------------------------------------------------------------------
# Output-dataklassen
# ---------------------------------------------------------------------------


@dataclass
class ZhSignalEntry:
    """Compact ziekenhuissignaal voor de mini-signaalkaart (Tab 1) en Tab 5."""

    hospital: str
    score: float
    tickets: int
    disengagement_risk: bool = False  # score < 2,5★ EN < 6 kwartaaltickets


@dataclass
class HospitalWithCause:
    """Ziekenhuisrij voor de bottom-5-tabel inclusief oorzaakkolom (Tab 5)."""

    hospital: str
    score: float
    baseline_score: float
    tickets: int
    cause: str  # Dominante negatieve thema (uit negative_cases)
    disengagement_risk: bool = False


@dataclass
class PeriodGroup:
    """Geaggregeerd datapunt voor de vergelijkingsbalk (Tab 2)."""

    label: str  # "S1 2025", "S2 2025", "Q1 2026" …
    avg_score: float
    pct_negative: float
    total: int


@dataclass
class ComparisonRow:
    """Rij in de kerncijfers-vergelijkingstabel (Tab 1)."""

    metric: str  # i18n-sleutel
    baseline_value: str
    current_value: str
    delta_value: str


@dataclass
class DashboardData:
    """
    Container voor alle voorbereide Streamlit-dashboard-data (Fase 5a).

    Aangemaakt door DashboardExporter.prepare() — bevat géén DataFrames
    zodat Streamlit's @st.cache_data de waarde zonder problemen kan serialiseren.
    """

    # --- Modus & identificatie ---
    mode: str  # "full" | "trend"
    window_start: str | None  # "2025-07-01" voor Tendensvenster, None voor Volledig
    pillar: str
    pillar_name: str
    pillar_color: str
    baseline_label: str
    current_label: str

    # --- KPI-kaarten (8 st.metric()-blokken) ---
    kpi_avg_score: float = 0.0
    kpi_avg_score_delta: float = 0.0
    kpi_avg_score_ref_label: str = ""
    kpi_pct_positive: float = 0.0
    kpi_pct_positive_delta: float = 0.0
    kpi_pct_negative: float = 0.0
    kpi_pct_negative_delta: float = 0.0
    kpi_best_month_label: str = ""
    kpi_best_month_score: float = 0.0
    kpi_responses_total: int = 0
    kpi_streak_months: int = 0
    kpi_critical_accounts: int = 0
    kpi_targets_met: int = 0
    kpi_targets_total: int = 3  # avg_score · pct_positive · pct_negative

    # --- Mini-signaalkaart (Tab 1) ---
    zh_top3: list[ZhSignalEntry] = field(default_factory=list)
    zh_bottom3: list[ZhSignalEntry] = field(default_factory=list)

    # --- Kerncijfers vergelijkingstabel (Tab 1) ---
    comparison_rows: list[ComparisonRow] = field(default_factory=list)

    # --- Tijdlijn (Tab 2, gefilterd op window_start) ---
    timeline: list[MonthlyDataPoint] = field(default_factory=list)
    period_groups: list[PeriodGroup] = field(default_factory=list)

    # --- Tickets & Prioriteit (Tab 3) ---
    by_issue_type: list[IssueTypeComparison] = field(default_factory=list)
    by_priority: list[PriorityComparison] = field(default_factory=list)
    negative_themes: list[ThemeEvolution] = field(default_factory=list)
    trivial_avg_score: float = 0.0
    trivial_pct_negative: float = 0.0

    # --- Responstijd (Tab 4) ---
    response_time_by_score: dict[int, ResponseTimeRow] = field(default_factory=dict)
    response_time_insight: ResponseTimeInsight | None = None
    baseline_correlation: float | None = None
    current_correlation: float | None = None

    # --- Ziekenhuizen (Tab 5) ---
    hospital_top5: list[ZhSignalEntry] = field(default_factory=list)
    hospital_bottom5: list[HospitalWithCause] = field(default_factory=list)

    # --- KPI Targets (Tab 6) ---
    kpi_targets: list[KpiTarget] = field(default_factory=list)

    # --- Ruwe resultaten (voor geavanceerd gebruik in app.py) ---
    raw: EvolutionResult | None = None


# ---------------------------------------------------------------------------
# DashboardExporter
# ---------------------------------------------------------------------------


class DashboardExporter:
    """
    Bereidt een EvolutionResult voor het Streamlit-dashboard.

    Gebruik altijd de statische methode prepare() — geen instantiatie nodig.
    """

    _DISENGAGEMENT_SCORE_THRESHOLD: float = 2.5
    _DISENGAGEMENT_TICKET_THRESHOLD: int = 6
    _STREAK_THRESHOLD: float = 4.0
    _CRITICAL_SCORE_THRESHOLD: float = 2.5
    _SCORE_TARGET_KEYS: frozenset[str] = frozenset(
        {"avg_score_min", "pct_positive_min", "pct_negative_max"}
    )

    @classmethod
    def prepare(
        cls,
        result: EvolutionResult,
        window_start: str | None = None,
    ) -> DashboardData:
        """
        Bereid alle dashboard-data voor op basis van een EvolutionResult.

        Args:
            result:       Volledig geanalyseerd EvolutionResult
            window_start: ISO-datum (YYYY-MM-DD) als startpunt voor Tendensvenster.
                          None → Volledig venster (jan 2025 → nu).
                          "2025-07-01" → Tendensvenster (jul 2025 → nu).

        Returns:
            DashboardData met alle voorbereide data voor de 6 tabs.
        """
        mode = "trend" if window_start else "full"
        pillar_cfg = PILLAR_REGISTRY.get(result.pillar, {})

        # Tijdlijn filteren op window_start
        timeline = cls._filter_timeline(result.monthly_timeline, window_start)

        # Referentiewaarden voor delta-berekening
        ref_avg, ref_pos, ref_neg, ref_label = cls._get_reference(result, mode)

        # KPI-kaarten
        kpi_best_month_label, kpi_best_month_score = cls._best_month(timeline)
        kpi_streak = cls._calc_streak(result.monthly_timeline)
        kpi_critical = cls._count_critical_accounts(result.hospital_comparison)
        kpi_targets_met, kpi_targets_total = cls._count_targets_met(result.kpi_targets)

        # Mini-signaalkaart
        zh_top3 = cls._build_top3(result.hospital_top5)
        zh_bottom3 = cls._build_bottom3(result.hospital_bottom5)

        # Kerncijfers vergelijkingstabel
        comparison_rows = cls._build_comparison_rows(result)

        # Periode-groepen voor vergelijkingsbalk
        period_groups = cls._build_period_groups(result.monthly_timeline, window_start)

        # Trivial-alert data
        trivial_avg, trivial_neg = cls._trivial_stats(result.by_priority)

        # Correlatie-waarden
        baseline_corr = None
        current_corr = None
        if result.response_time_insight:
            baseline_corr = result.response_time_insight.baseline_correlation_score
            current_corr = result.response_time_insight.correlation_score

        # Hospital bottom-5 met oorzaakkolom en disengagement-flag
        hospital_bottom5 = cls._build_hospital_bottom5(
            result.hospital_bottom5,
            result.negative_cases,
        )

        # Hospital top-5 voor Tab 5
        hospital_top5_full = cls._build_hospital_top5_full(result.hospital_top5)

        return DashboardData(
            mode=mode,
            window_start=window_start,
            pillar=result.pillar,
            pillar_name=pillar_cfg.get("report_name", result.pillar.upper()),
            pillar_color=pillar_cfg.get("color", "#609fce"),
            baseline_label=result.baseline_label,
            current_label=result.current_label,
            # KPI-kaarten
            kpi_avg_score=result.current_avg_score,
            kpi_avg_score_delta=round(result.current_avg_score - ref_avg, 2),
            kpi_avg_score_ref_label=ref_label,
            kpi_pct_positive=result.current_pct_positive,
            kpi_pct_positive_delta=round(result.current_pct_positive - ref_pos, 1),
            kpi_pct_negative=result.current_pct_negative,
            kpi_pct_negative_delta=round(result.current_pct_negative - ref_neg, 1),
            kpi_best_month_label=kpi_best_month_label,
            kpi_best_month_score=kpi_best_month_score,
            kpi_responses_total=result.current_total,
            kpi_streak_months=kpi_streak,
            kpi_critical_accounts=kpi_critical,
            kpi_targets_met=kpi_targets_met,
            kpi_targets_total=kpi_targets_total,
            # Mini-signaalkaart
            zh_top3=zh_top3,
            zh_bottom3=zh_bottom3,
            # Vergelijkingstabel
            comparison_rows=comparison_rows,
            # Tijdlijn
            timeline=timeline,
            period_groups=period_groups,
            # Tickets & Prioriteit
            by_issue_type=result.by_issue_type,
            by_priority=result.by_priority,
            negative_themes=result.negative_themes,
            trivial_avg_score=trivial_avg,
            trivial_pct_negative=trivial_neg,
            # Responstijd
            response_time_by_score=result.response_time_by_score,
            response_time_insight=result.response_time_insight,
            baseline_correlation=baseline_corr,
            current_correlation=current_corr,
            # Ziekenhuizen
            hospital_top5=hospital_top5_full,
            hospital_bottom5=hospital_bottom5,
            # KPI Targets
            kpi_targets=result.kpi_targets,
            # Raw
            raw=result,
        )

    # ------------------------------------------------------------------
    # Intern — tijdlijn
    # ------------------------------------------------------------------

    @staticmethod
    def _filter_timeline(
        timeline: list[MonthlyDataPoint],
        window_start: str | None,
    ) -> list[MonthlyDataPoint]:
        """Filter de tijdlijn op window_start (YYYY-MM-DD → YYYY-MM vergelijking)."""
        if not window_start:
            return sorted(timeline, key=lambda p: p.period)
        ws_period = window_start[:7]  # "2025-07-01" → "2025-07"
        return sorted(
            [p for p in timeline if p.period >= ws_period],
            key=lambda p: p.period,
        )

    @staticmethod
    def _best_month(timeline: list[MonthlyDataPoint]) -> tuple[str, float]:
        """Geef de beste maand (hoogste avg_score, min. 1 ticket) terug."""
        candidates = [p for p in timeline if p.total_tickets > 0 and p.avg_score > 0]
        if not candidates:
            return "—", 0.0
        best = max(candidates, key=lambda p: p.avg_score)
        return best.period, round(best.avg_score, 2)

    @staticmethod
    def _calc_streak(
        timeline: list[MonthlyDataPoint],
        threshold: float = 4.0,
    ) -> int:
        """
        Bereken aaneengesloten maanden >= threshold van meest recent naar oud.

        Maanden zonder tickets worden overgeslagen (niet als onderbreking geteld).
        """
        sorted_pts = sorted(timeline, key=lambda p: p.period, reverse=True)
        streak = 0
        for pt in sorted_pts:
            if pt.total_tickets == 0:
                continue  # Lege maand overslaan
            if pt.avg_score >= threshold:
                streak += 1
            else:
                break
        return streak

    # ------------------------------------------------------------------
    # Intern — referentiewaarden voor delta-berekening
    # ------------------------------------------------------------------

    @staticmethod
    def _get_reference(
        result: EvolutionResult,
        mode: str,
    ) -> tuple[float, float, float, str]:
        """
        Geef de referentiewaarden terug voor delta-berekening.

        Volledig venster → baseline-totaal (result.baseline_*)
        Tendensvenster  → H2-benchmark (result.benchmark_h2)

        Returns:
            Tuple (ref_avg, ref_pos, ref_neg, ref_label)
        """
        if mode == "trend" and result.benchmark_h2 is not None:
            bh2 = result.benchmark_h2
            return bh2.avg_score, bh2.pct_positive, bh2.pct_negative, bh2.label
        return (
            result.baseline_avg_score,
            result.baseline_pct_positive,
            result.baseline_pct_negative,
            result.baseline_label,
        )

    # ------------------------------------------------------------------
    # Intern — KPI helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _count_critical_accounts(hospital_comparison: list[HospitalComparison]) -> int:
        """Tel ziekenhuizen met current_score < 2,5★ en min. 1 ticket in huidige periode."""
        return sum(
            1
            for h in hospital_comparison
            if h.current_score is not None
            and h.current_total > 0
            and h.current_score < DashboardExporter._CRITICAL_SCORE_THRESHOLD
        )

    @staticmethod
    def _count_targets_met(kpi_targets: list[KpiTarget]) -> tuple[int, int]:
        """Tel de 3 score-targets die bereikt zijn (avg_score / pct_positive / pct_negative)."""
        score_targets = [t for t in kpi_targets if t.name in DashboardExporter._SCORE_TARGET_KEYS]
        met = sum(1 for t in score_targets if t.on_track)
        return met, len(score_targets)

    # ------------------------------------------------------------------
    # Intern — mini-signaalkaart
    # ------------------------------------------------------------------

    @staticmethod
    def _build_top3(hospital_top5: list[HospitalComparison]) -> list[ZhSignalEntry]:
        """Bouw top-3 signaallijst (groen) voor de mini-signaalkaart."""
        return [
            ZhSignalEntry(
                hospital=h.hospital,
                score=h.current_score if h.current_score is not None else 0.0,
                tickets=h.current_total,
            )
            for h in hospital_top5[:3]
            if h.current_score is not None
        ]

    @staticmethod
    def _build_bottom3(hospital_bottom5: list[HospitalComparison]) -> list[ZhSignalEntry]:
        """Bouw bottom-3 signaallijst (rood) met disengagement-flag."""
        return [
            ZhSignalEntry(
                hospital=h.hospital,
                score=h.current_score if h.current_score is not None else 0.0,
                tickets=h.current_total,
                disengagement_risk=(
                    h.current_score is not None
                    and h.current_score < DashboardExporter._DISENGAGEMENT_SCORE_THRESHOLD
                    and h.current_total < DashboardExporter._DISENGAGEMENT_TICKET_THRESHOLD
                ),
            )
            for h in hospital_bottom5[:3]
            if h.current_score is not None
        ]

    # ------------------------------------------------------------------
    # Intern — vergelijkingstabel
    # ------------------------------------------------------------------

    @staticmethod
    def _build_comparison_rows(result: EvolutionResult) -> list[ComparisonRow]:
        """Bouw de kerncijfers-vergelijkingstabel (Tab 1)."""

        def _delta_str(cur: float, ref: float, decimals: int = 2, suffix: str = "") -> str:
            d = cur - ref
            sign = "+" if d >= 0 else ""
            return f"{sign}{d:.{decimals}f}{suffix}"

        return [
            ComparisonRow(
                metric="avg_score",
                baseline_value=f"{result.baseline_avg_score:.2f}★",
                current_value=f"{result.current_avg_score:.2f}★",
                delta_value=_delta_str(
                    result.current_avg_score, result.baseline_avg_score, suffix="★"
                ),
            ),
            ComparisonRow(
                metric="pct_positive",
                baseline_value=f"{result.baseline_pct_positive:.1f}%",
                current_value=f"{result.current_pct_positive:.1f}%",
                delta_value=_delta_str(
                    result.current_pct_positive, result.baseline_pct_positive, 1, " ppt"
                ),
            ),
            ComparisonRow(
                metric="pct_negative",
                baseline_value=f"{result.baseline_pct_negative:.1f}%",
                current_value=f"{result.current_pct_negative:.1f}%",
                delta_value=_delta_str(
                    result.current_pct_negative, result.baseline_pct_negative, 1, " ppt"
                ),
            ),
            ComparisonRow(
                metric="n_hospitals",
                baseline_value=str(result.baseline_n_hospitals),
                current_value=str(result.current_n_hospitals),
                delta_value=_delta_str(
                    float(result.current_n_hospitals),
                    float(result.baseline_n_hospitals),
                    0,
                ),
            ),
            ComparisonRow(
                metric="total_tickets",
                baseline_value=str(result.baseline_total),
                current_value=str(result.current_total),
                delta_value=_delta_str(
                    float(result.current_total),
                    float(result.baseline_total),
                    0,
                ),
            ),
        ]

    # ------------------------------------------------------------------
    # Intern — periode-groepen voor vergelijkingsbalk
    # ------------------------------------------------------------------

    @staticmethod
    def _build_period_groups(
        timeline: list[MonthlyDataPoint],
        window_start: str | None,
    ) -> list[PeriodGroup]:
        """
        Groepeer maandelijkse datapunten per halfjaar (baseline) of kwartaal (huidig jaar).

        Volledig:       S1 2025 / S2 2025 / Q1 2026 / Q2 2026 …
        Tendensvenster: S2 2025 / Q1 2026 / Q2 2026 …
        """
        ws_period = window_start[:7] if window_start else None

        groups: dict[str, dict] = defaultdict(
            lambda: {
                "total": 0,
                "score_weighted": 0.0,
                "score_tickets": 0,
                "neg_sum": 0.0,
                "neg_count": 0,
            }
        )
        order: list[str] = []

        for dp in sorted(timeline, key=lambda p: p.period):
            if ws_period and dp.period < ws_period:
                continue
            year, month = parse_period(dp.period)
            # Baseline-jaar (2025 en ouder) → semester; huidig jaar → kwartaal
            if year <= 2025:
                label = f"S1 {year}" if month <= 6 else f"S2 {year}"
            else:
                q = (month - 1) // 3 + 1
                label = f"Q{q} {year}"

            g = groups[label]
            g["total"] += dp.total_tickets
            if dp.total_tickets > 0 and dp.avg_score > 0:
                g["score_weighted"] += dp.avg_score * dp.total_tickets
                g["score_tickets"] += dp.total_tickets
                g["neg_sum"] += dp.pct_negative
                g["neg_count"] += 1
            if label not in order:
                order.append(label)

        result = []
        for label in order:
            g = groups[label]
            avg = (
                round(g["score_weighted"] / g["score_tickets"], 2)
                if g["score_tickets"] > 0
                else 0.0
            )
            avg_neg = round(g["neg_sum"] / g["neg_count"], 1) if g["neg_count"] > 0 else 0.0
            result.append(
                PeriodGroup(label=label, avg_score=avg, pct_negative=avg_neg, total=g["total"])
            )
        return result

    # ------------------------------------------------------------------
    # Intern — tickets & prioriteit
    # ------------------------------------------------------------------

    @staticmethod
    def _trivial_stats(by_priority: list[PriorityComparison]) -> tuple[float, float]:
        """Geef de huidige score en % negatief voor Trivial-tickets terug."""
        for p in by_priority:
            if p.priority == "Trivial":
                return p.current_score, p.current_pct_neg
        return 0.0, 0.0

    # ------------------------------------------------------------------
    # Intern — ziekenhuizen
    # ------------------------------------------------------------------

    @staticmethod
    def _build_hospital_top5_full(
        hospital_top5: list[HospitalComparison],
    ) -> list[ZhSignalEntry]:
        """Bouw de volledige top-5-lijst voor Tab 5."""
        return [
            ZhSignalEntry(
                hospital=h.hospital,
                score=h.current_score if h.current_score is not None else 0.0,
                tickets=h.current_total,
            )
            for h in hospital_top5
            if h.current_score is not None
        ]

    @staticmethod
    def _build_hospital_bottom5(
        hospital_bottom5: list[HospitalComparison],
        negative_cases: list[NegativeCase],
    ) -> list[HospitalWithCause]:
        """
        Bouw de bottom-5-tabel met oorzaakkolom en disengagement-flag (§9.8-C).

        Oorzaak = dominant negatief thema per ziekenhuis (uit negative_cases).
        Disengagement-risico = score < 2,5★ EN < 6 tickets.
        """
        cause_counter: dict[str, Counter] = defaultdict(Counter)
        for case in negative_cases:
            if case.category and case.category != "—":
                cause_counter[case.hospital][case.category] += 1

        result = []
        for h in hospital_bottom5:
            if h.current_score is None:
                continue
            cause = ""
            if cause_counter.get(h.hospital):
                cause = cause_counter[h.hospital].most_common(1)[0][0]

            disengagement = (
                h.current_score < DashboardExporter._DISENGAGEMENT_SCORE_THRESHOLD
                and h.current_total < DashboardExporter._DISENGAGEMENT_TICKET_THRESHOLD
            )

            result.append(
                HospitalWithCause(
                    hospital=h.hospital,
                    score=h.current_score,
                    baseline_score=h.baseline_score,
                    tickets=h.current_total,
                    cause=cause,
                    disengagement_risk=disengagement,
                )
            )
        return result
