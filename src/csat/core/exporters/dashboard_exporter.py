"""
DashboardExporter voor CSAT-Compass — Fase 5a.

Bereidt EvolutionResult-data voor voor het Streamlit-dashboard.
Geen Streamlit-afhankelijkheden — pure data-transformatie, volledig testbaar.

Gebruik:
    data = DashboardExporter.prepare(result)                    # Volledig venster
    data = DashboardExporter.prepare(result, "2025-07-01")      # Tendensvenster
"""

from __future__ import annotations

from collections import defaultdict
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
    pillar: str = ""  # Optioneel: pijler-badge (bv. "PHARMA") — ingevuld voor ZORGI cross-pijler
    pillar_tickets: dict = field(default_factory=dict)  # {badge: ticket_count} — ZORGI cross-pijler


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

    # --- KPI-kaarten (8 st.metric()-blokken — Rij A: KPI-targets, Rij B: Context & Risico) ---
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
    kpi_attention_accounts: int = 0
    kpi_critical_account_names: list[str] = field(default_factory=list)
    zh_attention_list: list[ZhSignalEntry] = field(default_factory=list)
    kpi_targets_met: int = 0
    kpi_targets_total: int = 3  # avg_score · pct_positive · pct_negative
    kpi_high_critical_ratio: float = 0.0
    kpi_recent_month_label: str = ""
    kpi_recent_month_score: float = 0.0
    current_year: int = 0
    kpi_recent_month_name: str = ""
    kpi_recent_month_target_delta: float = 0.0
    kpi_responses_baseline_monthly_avg: float = 0.0
    kpi_responses_current_period_months: int = 0
    kpi_streak_current_year: int = 0
    kpi_streak_baseline_pct: float = 0.0
    kpi_responses_h2_monthly_avg: float = 0.0  # S2 baseline gem. responses/mnd (Tendensvenster)
    kpi_streak_h2_pct: float = 0.0  # % maanden >= 4,0★ in S2 baseline (Tendensvenster)

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
    negative_cases: list[NegativeCase] = field(default_factory=list)

    # --- Ziekenhuizen (Tab 5) ---
    hospital_top10: list[ZhSignalEntry] = field(default_factory=list)
    hospital_bottom10: list[ZhSignalEntry] = field(default_factory=list)
    hospital_attention: list[ZhSignalEntry] = field(default_factory=list)

    # --- KPI Targets (Tab 6) ---
    kpi_targets: list[KpiTarget] = field(default_factory=list)

    # --- ZORGI cross-pijler: ticket-breakdown per score-niveau (Tab 4 chips) ---
    # Structuur: {score_level: {"PHARMA": 8, "CARE": 4, ...}}
    score_pillar_breakdown: dict[int, dict[str, int]] = field(default_factory=dict)

    # --- ZORGI cross-pijler: per-ZH per-pijler (score, tickets) matrix (Tab 5 tabel) ---
    # Structuur: {hospital: {"PHARMA": (4.55, 10), "CARE": (3.80, 5), ...}}
    hospital_pillar_matrix: dict[str, dict[str, tuple[float, int]]] = field(default_factory=dict)

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
    _CRITICAL_SCORE_THRESHOLD: float = 3.0  # was: 2.5
    _ATTENTION_SCORE_THRESHOLD: float = 4.0  # nieuw: 3.0 ≤ score < 4.0
    _TOP_MIN_TICKETS: int = 5  # minimum tickets voor top-10 (statistisch relevant)
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
        kpi_attention = cls._count_attention_accounts(result.hospital_comparison)
        kpi_critical_names = cls._get_critical_account_names(result.hospital_comparison)
        zh_attention = cls._build_attention_list(result.hospital_comparison)
        kpi_targets_met, kpi_targets_total = cls._count_targets_met(result.kpi_targets)
        kpi_hc_ratio = cls._get_hc_ratio(result.kpi_targets)
        kpi_recent_label, kpi_recent_score = cls._recent_month(timeline)

        _current_year = int(window_start[:4]) if window_start else 0
        # Bepaal het huidige jaar op basis van de meest recente periode in timeline
        if timeline:
            _current_year = int(sorted(timeline, key=lambda p: p.period)[-1].period[:4])

        _baseline_year = _current_year - 1

        kpi_streak_cy = cls._calc_streak_current_year(result.monthly_timeline, _current_year)
        kpi_streak_bl_pct = cls._calc_streak_baseline_pct(result.monthly_timeline, _baseline_year)
        kpi_resp_monthly_avg = cls._calc_responses_baseline_monthly_avg(result.baseline_total)
        kpi_resp_months = len([p for p in timeline if p.total_tickets > 0])

        # S2-specifieke baseline (voor Tendensvenster-vergelijking)
        if result.benchmark_h2 is not None:
            kpi_resp_h2_avg = round(result.benchmark_h2.total / 6, 1)
            kpi_streak_h2_pct_val = cls._calc_streak_h2_pct(result.monthly_timeline, _baseline_year)
        else:
            kpi_resp_h2_avg = kpi_resp_monthly_avg
            kpi_streak_h2_pct_val = kpi_streak_bl_pct

        _avg_tgt_val = next(
            (kt.target for kt in result.kpi_targets if kt.name == "avg_score_min"), 4.0
        )
        kpi_recent_target_delta = round(kpi_recent_score - _avg_tgt_val, 2)

        # Mini-signaalkaart
        zh_top3 = cls._build_top3(result.hospital_top5)
        zh_bottom3 = cls._build_bottom3(result.hospital_comparison)

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

        # Hospital bottom-10 als ZhSignalEntry (≥ 1 ticket, slechtste score eerst)
        hospital_bottom10 = cls._build_hospital_bottom10(result.hospital_comparison)

        # Hospital top-10 voor Tab 5 (min. _TOP_MIN_TICKETS tickets)
        hospital_top10 = cls._build_hospital_top10(result.hospital_comparison)

        # Hospital aandachtslijst (3,0★ ≤ score < 4,0★) voor Tab 5
        hospital_attention = cls._build_hospital_attention(result.hospital_comparison)

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
            kpi_attention_accounts=kpi_attention,
            kpi_critical_account_names=kpi_critical_names,
            zh_attention_list=zh_attention,
            kpi_targets_met=kpi_targets_met,
            kpi_targets_total=kpi_targets_total,
            kpi_high_critical_ratio=kpi_hc_ratio,
            kpi_recent_month_label=kpi_recent_label,
            kpi_recent_month_score=kpi_recent_score,
            current_year=_current_year,
            kpi_recent_month_name=kpi_recent_label,
            kpi_recent_month_target_delta=kpi_recent_target_delta,
            kpi_responses_baseline_monthly_avg=kpi_resp_monthly_avg,
            kpi_responses_current_period_months=kpi_resp_months,
            kpi_streak_current_year=kpi_streak_cy,
            kpi_streak_baseline_pct=kpi_streak_bl_pct,
            kpi_responses_h2_monthly_avg=kpi_resp_h2_avg,
            kpi_streak_h2_pct=kpi_streak_h2_pct_val,
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
            hospital_top10=hospital_top10,
            hospital_bottom10=hospital_bottom10,
            hospital_attention=hospital_attention,
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
        """Tel ziekenhuizen met current_score < 3,0★ en min. 1 ticket in huidige periode."""
        return sum(
            1
            for h in hospital_comparison
            if h.current_score is not None
            and h.current_total > 0
            and h.current_score < DashboardExporter._CRITICAL_SCORE_THRESHOLD
        )

    @staticmethod
    def _count_attention_accounts(
        hospital_comparison: list[HospitalComparison],
    ) -> int:
        """Tel ziekenhuizen met score >= 3.0 en < 4.0 (min. 1 ticket huidig)."""
        return sum(
            1
            for h in hospital_comparison
            if h.current_score is not None
            and h.current_total > 0
            and DashboardExporter._CRITICAL_SCORE_THRESHOLD
            <= h.current_score
            < DashboardExporter._ATTENTION_SCORE_THRESHOLD
        )

    @staticmethod
    def _get_critical_account_names(
        hospital_comparison: list[HospitalComparison],
    ) -> list[str]:
        """Geef namen van kritieke ziekenhuizen (score < 3.0, min. 1 ticket)."""
        return [
            h.hospital
            for h in sorted(hospital_comparison, key=lambda h: h.current_score or 0.0)
            if h.current_score is not None
            and h.current_total > 0
            and h.current_score < DashboardExporter._CRITICAL_SCORE_THRESHOLD
        ]

    @staticmethod
    def _build_attention_list(
        hospital_comparison: list[HospitalComparison],
    ) -> list[ZhSignalEntry]:
        """Bouw de aandachtslijst (score >= 3.0 en < 4.0) gesorteerd op score.

        Sortering: laagste score eerst; bij gelijke score meer tickets eerst.
        """
        return [
            ZhSignalEntry(
                hospital=h.hospital,
                score=h.current_score,  # type: ignore[arg-type]
                tickets=h.current_total,
            )
            for h in sorted(
                hospital_comparison,
                key=lambda h: (h.current_score or 0.0, -h.current_total, h.hospital),
            )
            if h.current_score is not None
            and h.current_total > 0
            and DashboardExporter._CRITICAL_SCORE_THRESHOLD
            <= h.current_score
            < DashboardExporter._ATTENTION_SCORE_THRESHOLD
        ]

    @staticmethod
    def _count_targets_met(kpi_targets: list[KpiTarget]) -> tuple[int, int]:
        """Tel de 3 score-targets die bereikt zijn (avg_score / pct_positive / pct_negative)."""
        score_targets = [t for t in kpi_targets if t.name in DashboardExporter._SCORE_TARGET_KEYS]
        met = sum(1 for t in score_targets if t.on_track)
        return met, len(score_targets)

    @staticmethod
    def _get_hc_ratio(kpi_targets: list[KpiTarget]) -> float:
        """Geef de huidige High/Critical-ratio terug uit kpi_targets."""
        for kp in kpi_targets:
            if kp.name == "high_critical_max":
                return round(kp.current, 1)
        return 0.0

    @staticmethod
    def _recent_month(timeline: list[MonthlyDataPoint]) -> tuple[str, float]:
        """Geef de meest recente maand met tickets terug (niet de beste)."""
        candidates = [p for p in timeline if p.total_tickets > 0]
        if not candidates:
            return "—", 0.0
        latest = max(candidates, key=lambda p: p.period)
        return latest.period, round(latest.avg_score, 2)

    @staticmethod
    def _calc_streak_current_year(
        timeline: list[MonthlyDataPoint],
        current_year: int,
        threshold: float = 4.0,
    ) -> int:
        """Tel maanden >= threshold in het huidige kalenderjaar."""
        return sum(
            1
            for p in timeline
            if p.total_tickets > 0
            and p.avg_score >= threshold
            and p.period.startswith(str(current_year))
        )

    @staticmethod
    def _calc_streak_baseline_pct(
        timeline: list[MonthlyDataPoint],
        baseline_year: int,
        threshold: float = 4.0,
    ) -> float:
        """Bereken het % maanden >= threshold in het baseline kalenderjaar (/ 12)."""
        count = sum(
            1
            for p in timeline
            if p.total_tickets > 0
            and p.avg_score >= threshold
            and p.period.startswith(str(baseline_year))
        )
        return round(count / 12 * 100, 0)

    @staticmethod
    def _calc_responses_baseline_monthly_avg(
        baseline_total: int,
    ) -> float:
        """Gemiddeld aantal responses per maand in het baseline jaar (/ 12)."""
        return round(baseline_total / 12, 1)

    @staticmethod
    def _recent_month_name(
        period_label: str,
        months_i18n: list[str],
    ) -> str:
        """Zet een period-string 'YYYY-MM' om naar een leesbare maandnaam."""
        if not period_label or period_label == "—":
            return period_label
        try:
            parts = period_label.split("-")
            year, month = int(parts[0]), int(parts[1])
            month_name = months_i18n[month - 1] if len(months_i18n) >= month else parts[1]
            return f"{month_name.capitalize()} {year}"
        except (IndexError, ValueError):
            return period_label

    @staticmethod
    def _calc_streak_h2_pct(
        timeline: list[MonthlyDataPoint],
        baseline_year: int,
        threshold: float = 4.0,
    ) -> float:
        """Bereken het % maanden >= threshold in S2 (jul-dec) van het baseline jaar (/ 6)."""
        count = sum(
            1
            for p in timeline
            if p.total_tickets > 0
            and p.avg_score >= threshold
            and p.period.startswith(str(baseline_year))
            and int(p.period[5:7]) >= 7
        )
        return round(count / 6 * 100, 0)

    # ------------------------------------------------------------------
    # Intern — mini-signaalkaart
    # ------------------------------------------------------------------

    @staticmethod
    def _build_top3(hospital_top5: list[HospitalComparison]) -> list[ZhSignalEntry]:
        """Bouw top-3 signaallijst (groen) voor de mini-signaalkaart.

        Sortering: hoogste score eerst; bij gelijke score meer tickets eerst.
        """
        sorted_top = sorted(
            hospital_top5,
            key=lambda h: (-(h.current_score or 0.0), -h.current_total, h.hospital),
        )
        return [
            ZhSignalEntry(
                hospital=h.hospital,
                score=h.current_score if h.current_score is not None else 0.0,
                tickets=h.current_total,
            )
            for h in sorted_top[:3]
            if h.current_score is not None
        ]

    @staticmethod
    def _build_bottom3(
        hospital_comparison: list[HospitalComparison],
    ) -> list[ZhSignalEntry]:
        """Bouw kritieke signaallijst (score < 3,0★) voor de mini-signaalkaart.

        Enkel ziekenhuizen met current_score < _CRITICAL_SCORE_THRESHOLD (3,0).
        Sortering: laagste score eerst; bij gelijke score meer tickets eerst.
        Max. 3 entries — leeg als geen enkel ZH de kritieke grens overschrijdt.
        """
        critical = [
            h
            for h in hospital_comparison
            if h.current_score is not None
            and h.current_total > 0
            and h.current_score < DashboardExporter._CRITICAL_SCORE_THRESHOLD
        ]
        critical.sort(key=lambda h: (h.current_score or 0.0, -h.current_total, h.hospital))
        return [
            ZhSignalEntry(
                hospital=h.hospital,
                score=h.current_score,  # type: ignore[arg-type]
                tickets=h.current_total,
                disengagement_risk=(
                    (h.current_score or 0.0) < DashboardExporter._DISENGAGEMENT_SCORE_THRESHOLD
                    and h.current_total < DashboardExporter._DISENGAGEMENT_TICKET_THRESHOLD
                ),
            )
            for h in critical[:3]
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
    @classmethod
    def _build_hospital_top10(
        cls,
        hospital_comparison: list[HospitalComparison],
    ) -> list[ZhSignalEntry]:
        """Bouw de top-10-lijst voor Tab 5 (score ≥ 4,0★ + min. _TOP_MIN_TICKETS tickets).

        Score-filter ≥ 4,0 garandeert dat de titel '≥ 4,0★' altijd klopt.
        Ticket-filter (min. 5) zorgt voor statistisch relevante resultaten.
        Sortering: hoogste score eerst; bij gelijke score meer tickets eerst.
        """
        filtered = [
            h
            for h in hospital_comparison
            if h.current_score is not None
            and h.current_score >= cls._ATTENTION_SCORE_THRESHOLD
            and h.current_total >= cls._TOP_MIN_TICKETS
        ]
        sorted_top = sorted(
            filtered,
            key=lambda h: (-(h.current_score or 0.0), -h.current_total, h.hospital),
        )
        return [
            ZhSignalEntry(
                hospital=h.hospital,
                score=h.current_score,  # type: ignore[arg-type]
                tickets=h.current_total,
            )
            for h in sorted_top[:10]
        ]

    @classmethod
    def _build_hospital_bottom10(
        cls,
        hospital_comparisons: list[HospitalComparison],
    ) -> list[ZhSignalEntry]:
        """
        Bouw de bottom-10-lijst (slechtste score) als ZhSignalEntry.

        Filter: ziekenhuizen met ≥ 1 ticket in de huidige periode.
        Sortering: oplopend current_score.
        Disengagement-risico = score < 2,5★ EN < 6 tickets.
        """
        filtered = [
            h for h in hospital_comparisons if h.current_score is not None and h.current_total >= 1
        ]
        sorted_bottom = sorted(
            filtered,
            key=lambda h: (h.current_score or 0.0, -h.current_total, h.hospital),
        )
        return [
            ZhSignalEntry(
                hospital=hc.hospital,
                score=hc.current_score,  # type: ignore[arg-type]
                tickets=hc.current_total,
                disengagement_risk=(
                    hc.current_score is not None
                    and hc.current_score < cls._DISENGAGEMENT_SCORE_THRESHOLD
                    and hc.current_total < cls._DISENGAGEMENT_TICKET_THRESHOLD
                ),
            )
            for hc in sorted_bottom[:10]
        ]

    @classmethod
    def _build_hospital_attention(
        cls,
        hospital_comparisons: list[HospitalComparison],
    ) -> list[ZhSignalEntry]:
        """Aandachtsaccounts: score ≥ 3,0★ en < 4,0★ (≥1 ticket huidig).

        Sortering: oplopend score.
        Geen limiet — alle aandachtsaccounts worden opgenomen.
        Kan overlappen met bottom-10 (correct gedrag).
        """
        result = []
        for hc in hospital_comparisons:
            if hc.current_score is None or hc.current_total < 1:
                continue
            if cls._CRITICAL_SCORE_THRESHOLD <= hc.current_score < cls._ATTENTION_SCORE_THRESHOLD:
                result.append(
                    ZhSignalEntry(
                        hospital=hc.hospital,
                        score=hc.current_score,  # type: ignore[arg-type]
                        tickets=hc.current_total,
                    )
                )
        return sorted(result, key=lambda e: e.score)
