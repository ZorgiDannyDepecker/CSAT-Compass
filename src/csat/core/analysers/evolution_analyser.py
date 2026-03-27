"""
EvolutionAnalyser voor CSAT-Compass.

Vergelijkt twee periodegroepen (baseline vs huidig) en berekent alle metrics
voor de EvolutionResult dataclass.

Spelregels:
- ADR-006: reactiegraad N/A — niet berekenen
- ADR-007: baseline start 01/01/2025 (ANALYSE_START_DATE)
- ADR-009: KPI OK = avg_score >= AVG_SCORE_MIN (4,00)
"""

from __future__ import annotations

import re

import pandas as pd
from loguru import logger

from csat.config.pillars import FILTER_COLUMN, HIGH_CRITICAL_PRIORITIES, PILLAR_REGISTRY
from csat.config.settings import ANALYSE_START_DATE, AVG_SCORE_MIN, HIGH_CRITICAL_MAX
from csat.utils.date_utils import filter_period, parse_period

from .evolution_result import (
    EvolutionResult,
    HospitalComparison,
    IssueTypeComparison,
    KpiStatus,
    MonthlyDataPoint,
    PriorityComparison,
    ResponseTimeRow,
    ThemeEvolution,
)

# ---------------------------------------------------------------------------
# Keyword-configuratie voor negatieve feedbackthema's (sectie 8)
# ---------------------------------------------------------------------------

THEME_KEYWORDS: dict[str, list[str]] = {
    "responstijd": [
        "wachttijd",
        "te lang",
        "traag",
        "wacht",
        "dagen",
        "attente",
        "lent",
        "tardif",
        "délai",
    ],
    "onvolledig": [
        "niet opgelost",
        "deels",
        "onvolledig",
        "nog steeds",
        "non résolu",
        "incomplet",
        "partiellement",
    ],
    "communicatie": [
        "geen update",
        "niet gecontacteerd",
        "onduidelijk",
        "pas de nouvelles",
        "pas contacté",
        "flou",
    ],
    "urgentie": [
        "dringend",
        "prioriteit",
        "spoed",
        "urgent",
        "priorité",
    ],
    "automatisering": [
        "automatisch",
        "script",
        "automatiseer",
        "automatique",
    ],
}


class EvolutionAnalyser:
    """
    Analyser voor evolutievergelijking tussen baseline en huidige periode.

    Filtert data op pijler en start-datum (cf. PillarAnalyser-logica),
    en berekent alle metrics voor EvolutionResult.

    Periodegroepering (maand/jaar) gebeurt op basis van effective_date:
    satisfaction_date indien beschikbaar (CSAT-relevante tijdstempel), anders
    fallback naar created. Tickets aangemaakt in december maar gescoord in januari
    tellen mee in de januaricijfers. Ongescoorde tickets (satisfaction_date=NaT)
    worden ingedeeld op basis van created. Start-datumfilter blijft op 'created' (ADR-007).

    Args:
        df:          Volledig geladen DataFrame (alle pijlers)
        pillar_key:  Pijlersleutel uit PILLAR_REGISTRY (bv. 'pharma')
    """

    # Datumkolom voor periodegroepering — effective_date: satisfaction_date indien beschikbaar,
    # anders fallback naar created (voor ongescoorde tickets zonder satisfaction_date)
    _PERIOD_DATE_COL: str = "effective_date"

    def __init__(self, df: pd.DataFrame, pillar_key: str) -> None:
        if pillar_key not in PILLAR_REGISTRY:
            raise ValueError(
                f"Onbekende pijler: '{pillar_key}' — kies uit {sorted(PILLAR_REGISTRY)}"
            )

        self._pillar_key = pillar_key
        self._pillar_config = PILLAR_REGISTRY[pillar_key]
        self._pillar_df = self._filter_pillar(df)
        self._pillar_df = self._filter_start_date(self._pillar_df)
        # effective_date: satisfaction_date waar beschikbaar, anders fallback naar created
        self._pillar_df = self._pillar_df.copy()
        self._pillar_df["effective_date"] = self._pillar_df["satisfaction_date"].where(
            self._pillar_df["satisfaction_date"].notna(),
            other=pd.to_datetime(self._pillar_df["created"]),
        )

    # ------------------------------------------------------------------
    # Publieke interface
    # ------------------------------------------------------------------

    def analyse(
        self,
        baseline_periods: list[str],
        current_periods: list[str],
        baseline_label: str | None = None,
        current_label: str | None = None,
    ) -> EvolutionResult:
        """
        Voer de volledige evolutie-analyse uit.

        Args:
            baseline_periods: Periodes voor de baseline (bv. ["2025-01", ..., "2025-12"])
            current_periods:  Periodes voor huidig jaar (bv. ["2026-01", "2026-02"])
            baseline_label:   Label baseline (auto: jaar van eerste periode)
            current_label:    Label huidig (auto: jaar van eerste periode)

        Returns:
            EvolutionResult met alle vergelijkingsdata.

        Raises:
            ValueError: Als een periodestring ongeldig is.
        """
        # Valideer alle periodestrings
        for p in baseline_periods + current_periods:
            parse_period(p)

        baseline_df = self._get_df_for_periods(baseline_periods)
        current_df = self._get_df_for_periods(current_periods)

        bl = baseline_label or self._make_label(baseline_periods)
        cl = current_label or self._make_label(current_periods)

        # --- Kerncijfers ---
        b_total = len(baseline_df)
        c_total = len(current_df)
        b_avg = self._calc_avg_score(baseline_df)
        c_avg = self._calc_avg_score(current_df)
        delta = round(c_avg - b_avg, 2)

        b_pct_pos = self._calc_pct_scored(baseline_df, lambda s: s >= 4.0)
        c_pct_pos = self._calc_pct_scored(current_df, lambda s: s >= 4.0)
        b_pct_neg = self._calc_pct_scored(baseline_df, lambda s: s <= 2.0)
        c_pct_neg = self._calc_pct_scored(current_df, lambda s: s <= 2.0)

        b_resp = self._calc_avg_response_days(baseline_df)
        c_resp = self._calc_avg_response_days(current_df)

        b_hosp = int(baseline_df["hospital"].dropna().nunique()) if not baseline_df.empty else 0
        c_hosp = int(current_df["hospital"].dropna().nunique()) if not current_df.empty else 0

        _, b_hc_ratio = self._calc_high_critical(baseline_df)
        _, c_hc_ratio = self._calc_high_critical(current_df)

        # --- Tijdlijn ---
        all_periods = sorted(set(baseline_periods + current_periods))
        monthly_timeline = [self._make_monthly_datapoint(p) for p in all_periods]

        # --- Breakdowns ---
        by_issue_type = self._issue_type_comparison(baseline_df, current_df)
        by_priority = self._priority_comparison(baseline_df, current_df)

        # --- Responstijd per score-niveau ---
        response_time_by_score = self._response_time_by_score(baseline_df, current_df)

        # --- Ziekenhuizen ---
        hospital_comparison, hospitals_disappeared, hospitals_new = self._hospital_comparison(
            baseline_df, current_df
        )

        # --- Thema's ---
        negative_themes = self._negative_themes(baseline_df, current_df)

        # --- Trend classificatie ---
        trend_is_structural, trend_breadth = self._classify_trend(delta, hospital_comparison)

        # --- KPI status ---
        kpi_status = self._calc_kpi_status(b_avg, c_avg, b_hc_ratio, c_hc_ratio, b_total, c_total)

        result = EvolutionResult(
            pillar=self._pillar_key,
            baseline_label=bl,
            current_label=cl,
            baseline_total=b_total,
            current_total=c_total,
            baseline_avg_score=b_avg,
            current_avg_score=c_avg,
            delta_avg_score=delta,
            baseline_pct_positive=b_pct_pos,
            current_pct_positive=c_pct_pos,
            baseline_pct_negative=b_pct_neg,
            current_pct_negative=c_pct_neg,
            baseline_avg_response_days=b_resp,
            current_avg_response_days=c_resp,
            baseline_n_hospitals=b_hosp,
            current_n_hospitals=c_hosp,
            baseline_hc_ratio=b_hc_ratio,
            current_hc_ratio=c_hc_ratio,
            trend_is_structural=trend_is_structural,
            trend_breadth=trend_breadth,
            monthly_timeline=monthly_timeline,
            by_issue_type=by_issue_type,
            by_priority=by_priority,
            response_time_by_score=response_time_by_score,
            hospital_comparison=hospital_comparison,
            hospitals_disappeared=hospitals_disappeared,
            hospitals_new=hospitals_new,
            negative_themes=negative_themes,
            kpi_status=kpi_status,
        )

        logger.info(
            f"[EvolutionAnalyser:{self._pillar_key}] Analyse voltooid — "
            f"baseline={bl} ({b_total:,} tickets, avg={b_avg}) | "
            f"current={cl} ({c_total:,} tickets, avg={c_avg}) | "
            f"delta={delta:+.2f} | {'structureel' if trend_is_structural else 'onduidelijk'} "
            f"({trend_breadth})"
        )
        return result

    # ------------------------------------------------------------------
    # Intern — data filtering (cf. PillarAnalyser)
    # ------------------------------------------------------------------

    def _filter_pillar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter het DataFrame op de product_domain-waarden van deze pijler."""
        products = self._pillar_config.get("products", [])
        if not products:  # pragma: no cover
            return df.copy()
        products_upper = [p.upper() for p in products]
        mask = df[FILTER_COLUMN].str.strip().str.upper().isin(products_upper)
        filtered = df[mask].copy()
        logger.info(
            f"[EvolutionAnalyser:{self._pillar_key}] {len(filtered):,} rijen na pijlerfilter"
        )
        return filtered

    def _filter_start_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sluit tickets uit die aangemaakt zijn vóór ANALYSE_START_DATE (ADR-007)."""
        if not ANALYSE_START_DATE:  # pragma: no cover
            return df
        start = pd.Timestamp(ANALYSE_START_DATE)
        mask = pd.to_datetime(df["created"]) >= start
        filtered = df.loc[mask].copy()
        logger.info(
            f"[EvolutionAnalyser:{self._pillar_key}] Datumfilter >= {ANALYSE_START_DATE}: "
            f"{len(filtered):,} rijen behouden (was {len(df):,})"
        )
        return filtered

    def _get_df_for_periods(self, periods: list[str]) -> pd.DataFrame:
        """Combineer DataFrames voor een lijst van periodes (gefilterd op satisfaction_date)."""
        if not periods:
            return self._pillar_df.iloc[0:0].copy()
        frames = [
            filter_period(self._pillar_df, p, date_col=self._PERIOD_DATE_COL) for p in periods
        ]
        non_empty = [f for f in frames if not f.empty]
        if not non_empty:
            return self._pillar_df.iloc[0:0].copy()
        return pd.concat(non_empty, ignore_index=True)

    # ------------------------------------------------------------------
    # Intern — KPI-berekeningen (cf. BaseAnalyser)
    # ------------------------------------------------------------------

    def _calc_avg_score(self, df: pd.DataFrame) -> float:
        """Bereken de gemiddelde CSAT-score (alleen gescoorde tickets)."""
        scored = df[df["score"].notna()]
        if scored.empty:
            return 0.0
        return round(float(scored["score"].mean()), 2)

    def _calc_high_critical(self, df: pd.DataFrame) -> tuple[int, float]:
        """Bereken het aantal en percentage High/Critical-tickets."""
        total = len(df)
        hc_count = int(df["priority"].isin(HIGH_CRITICAL_PRIORITIES).sum())
        hc_ratio = round((hc_count / total * 100), 1) if total > 0 else 0.0
        return hc_count, hc_ratio

    def _calc_pct_scored(self, df: pd.DataFrame, condition) -> float:
        """Bereken het % gescoorde tickets dat aan een conditie voldoet."""
        scored = df[df["score"].notna()]
        if scored.empty:
            return 0.0
        count = int(scored[scored["score"].apply(condition)].shape[0])
        return round(count / len(scored) * 100, 1)

    def _calc_avg_response_days(self, df: pd.DataFrame) -> float:
        """
        Bereken de gemiddelde responstijd in dagen (satisfaction_date - created).

        Returns:
            Gemiddelde responstijd in dagen, of 0.0 als geen geldige datums beschikbaar zijn.
        """
        if df.empty:
            return 0.0
        created = pd.to_datetime(df["created"])
        sat = pd.to_datetime(df["satisfaction_date"])
        days = (sat - created).dt.days
        valid = days.dropna()
        valid = valid[valid >= 0]
        if valid.empty:
            return 0.0
        return round(float(valid.mean()), 1)

    # ------------------------------------------------------------------
    # Intern — tijdlijn
    # ------------------------------------------------------------------

    def _make_monthly_datapoint(self, period: str) -> MonthlyDataPoint:
        """Maak een MonthlyDataPoint voor één periode op basis van satisfaction_date."""
        df = filter_period(self._pillar_df, period, date_col=self._PERIOD_DATE_COL)
        year, month = parse_period(period)
        fase = f"H1 {year}" if month <= 6 else f"H2 {year}"

        # Prioriteitstellingen — voor subplot 3 (prioriteitscompositie per maand)
        priority_counts: dict[str, int] = {}
        if "priority" in df.columns and not df.empty:
            counts = df["priority"].dropna().value_counts()
            priority_counts = {str(k): int(v) for k, v in counts.items()}

        return MonthlyDataPoint(
            period=period,
            avg_score=self._calc_avg_score(df),
            total_tickets=len(df),
            pct_negative=self._calc_pct_scored(df, lambda s: s <= 2.0),
            fase=fase,
            priority_counts=priority_counts,
        )

    # ------------------------------------------------------------------
    # Intern — breakdowns
    # ------------------------------------------------------------------

    def _issue_type_comparison(
        self, baseline_df: pd.DataFrame, current_df: pd.DataFrame
    ) -> list[IssueTypeComparison]:
        """Vergelijk issue types tussen baseline en huidige periode."""
        all_types = sorted(
            set(
                baseline_df["issue_type"].dropna().unique().tolist()
                + current_df["issue_type"].dropna().unique().tolist()
            )
        )
        result = []
        for issue_type in all_types:
            b_sub = baseline_df[baseline_df["issue_type"] == issue_type]
            c_sub = current_df[current_df["issue_type"] == issue_type]
            result.append(
                IssueTypeComparison(
                    issue_type=issue_type,
                    baseline_score=self._calc_avg_score(b_sub),
                    baseline_pct_neg=self._calc_pct_scored(b_sub, lambda s: s <= 2.0),
                    current_score=self._calc_avg_score(c_sub),
                    current_pct_neg=self._calc_pct_scored(c_sub, lambda s: s <= 2.0),
                )
            )
        return result

    def _priority_comparison(
        self, baseline_df: pd.DataFrame, current_df: pd.DataFrame
    ) -> list[PriorityComparison]:
        """Vergelijk prioriteiten tussen baseline en huidige periode."""
        all_prios = sorted(
            set(
                baseline_df["priority"].dropna().unique().tolist()
                + current_df["priority"].dropna().unique().tolist()
            )
        )
        result = []
        for priority in all_prios:
            b_sub = baseline_df[baseline_df["priority"] == priority]
            c_sub = current_df[current_df["priority"] == priority]
            result.append(
                PriorityComparison(
                    priority=priority,
                    baseline_score=self._calc_avg_score(b_sub),
                    baseline_pct_neg=self._calc_pct_scored(b_sub, lambda s: s <= 2.0),
                    current_score=self._calc_avg_score(c_sub),
                    current_pct_neg=self._calc_pct_scored(c_sub, lambda s: s <= 2.0),
                )
            )
        return result

    # ------------------------------------------------------------------
    # Intern — responstijd per score
    # ------------------------------------------------------------------

    def _response_time_by_score(
        self, baseline_df: pd.DataFrame, current_df: pd.DataFrame
    ) -> dict[int, ResponseTimeRow]:
        """Bereken gemiddelde responstijd per score-niveau (1-5)."""
        result: dict[int, ResponseTimeRow] = {}
        for score_level in range(1, 6):
            b_sub = baseline_df[
                baseline_df["score"].notna() & (baseline_df["score"] == float(score_level))
            ]
            c_sub = current_df[
                current_df["score"].notna() & (current_df["score"] == float(score_level))
            ]

            b_days: float | None = None
            if not b_sub.empty and b_sub["satisfaction_date"].notna().any():
                b_days = self._calc_avg_response_days(b_sub)

            c_days: float | None = None
            if not c_sub.empty and c_sub["satisfaction_date"].notna().any():
                c_days = self._calc_avg_response_days(c_sub)

            if b_days is not None or c_days is not None:
                result[score_level] = ResponseTimeRow(
                    score_level=score_level,
                    baseline_days=b_days,
                    current_days=c_days,
                )
        return result

    # ------------------------------------------------------------------
    # Intern — ziekenhuizen
    # ------------------------------------------------------------------

    def _hospital_comparison(
        self, baseline_df: pd.DataFrame, current_df: pd.DataFrame
    ) -> tuple[list[HospitalComparison], list[str], list[str]]:
        """
        Vergelijk ziekenhuizen tussen baseline en huidige periode.

        Returns:
            Tuple (comparisons, hospitals_disappeared, hospitals_new)
        """
        b_hospitals: set[str] = set(baseline_df["hospital"].dropna().unique())
        c_hospitals: set[str] = set(current_df["hospital"].dropna().unique())

        hospitals_disappeared = sorted(b_hospitals - c_hospitals)
        hospitals_new = sorted(c_hospitals - b_hospitals)
        all_hospitals = sorted(b_hospitals | c_hospitals)

        comparisons: list[HospitalComparison] = []
        for hospital in all_hospitals:
            b_sub = baseline_df[baseline_df["hospital"] == hospital]
            c_sub = current_df[current_df["hospital"] == hospital]

            b_score = self._calc_avg_score(b_sub) if not b_sub.empty else 0.0
            b_total = len(b_sub)

            c_score: float | None = None
            c_total = len(c_sub)
            if c_total > 0:
                c_score = self._calc_avg_score(c_sub)

            comparisons.append(
                HospitalComparison(
                    hospital=hospital,
                    baseline_score=b_score,
                    baseline_total=b_total,
                    current_score=c_score,
                    current_total=c_total,
                )
            )

        return comparisons, hospitals_disappeared, hospitals_new

    # ------------------------------------------------------------------
    # Intern — thema's
    # ------------------------------------------------------------------

    def _negative_themes(
        self, baseline_df: pd.DataFrame, current_df: pd.DataFrame
    ) -> list[ThemeEvolution]:
        """
        Detecteer negatieve feedbackthema's via keyword matching op het comment-veld.

        Enkel negatieve tickets (score <= 2) worden geanalyseerd.
        """
        baseline_neg = baseline_df[baseline_df["score"].notna() & (baseline_df["score"] <= 2)]
        current_neg = current_df[current_df["score"].notna() & (current_df["score"] <= 2)]

        n_baseline = len(baseline_neg)
        n_current = len(current_neg)

        results: list[ThemeEvolution] = []
        for theme_key, keywords in THEME_KEYWORDS.items():
            pattern = "|".join(re.escape(kw) for kw in keywords)

            pct_baseline = 0.0
            if n_baseline > 0:
                hits = (
                    baseline_neg["comment"].fillna("").str.lower().str.contains(pattern, regex=True)
                )
                pct_baseline = round(hits.sum() / n_baseline * 100, 1)

            pct_current = 0.0
            if n_current > 0:
                hits = (
                    current_neg["comment"].fillna("").str.lower().str.contains(pattern, regex=True)
                )
                pct_current = round(hits.sum() / n_current * 100, 1)

            if pct_baseline > 0 or pct_current > 0:
                if pct_baseline > 0 and pct_current > 0:
                    status = "NOG_AANWEZIG"
                elif pct_baseline > 0:
                    status = "OPGELOST"
                else:
                    status = "NIEUW"

                results.append(
                    ThemeEvolution(
                        theme_key=theme_key,
                        pct_baseline=pct_baseline,
                        pct_current=pct_current,
                        status=status,
                    )
                )

        return results

    # ------------------------------------------------------------------
    # Intern — trend classificatie
    # ------------------------------------------------------------------

    def _classify_trend(
        self,
        delta_avg_score: float,
        hospital_comparison: list[HospitalComparison],
    ) -> tuple[bool, str]:
        """
        Classificeer de trend als structureel of tijdelijk, en bepaal de breedte.

        Returns:
            Tuple (trend_is_structural, trend_breadth)
            - trend_is_structural: True als delta >= 0,5 (significante verbetering)
            - trend_breadth: "breed" (>= 60% verbeterd) / "beperkt" (<= 30%) / "gemengd"
        """
        trend_is_structural = delta_avg_score >= 0.5

        # Alleen ziekenhuizen aanwezig in beide periodes
        shared = [h for h in hospital_comparison if h.current_score is not None]

        if not shared:
            return trend_is_structural, "gemengd"

        improved = sum(
            1 for h in shared if h.current_score is not None and h.current_score > h.baseline_score
        )
        pct_improved = improved / len(shared) * 100

        if pct_improved >= 60:
            breadth = "breed"
        elif pct_improved <= 30:
            breadth = "beperkt"
        else:
            breadth = "gemengd"

        return trend_is_structural, breadth

    # ------------------------------------------------------------------
    # Intern — KPI status
    # ------------------------------------------------------------------

    def _calc_kpi_status(
        self,
        baseline_avg_score: float,
        current_avg_score: float,
        baseline_hc_ratio: float,
        current_hc_ratio: float,
        baseline_total: int,
        current_total: int,
    ) -> dict[str, KpiStatus]:
        """
        Bepaal KPI-status voor alle metrics (ADR-009).

        Keys: avg_score_baseline, avg_score_current,
              high_critical_baseline, high_critical_current, trend
        """
        cur_score_status = self._score_kpi_status(current_avg_score, current_total)
        delta = round(current_avg_score - baseline_avg_score, 2)

        if cur_score_status == KpiStatus.OK and delta >= 0.0:
            trend = KpiStatus.OK
        elif cur_score_status == KpiStatus.AT_RISK or delta <= -0.5:
            trend = KpiStatus.AT_RISK
        else:
            trend = KpiStatus.WARNING

        return {
            "avg_score_baseline": self._score_kpi_status(baseline_avg_score, baseline_total),
            "avg_score_current": cur_score_status,
            "high_critical_baseline": self._hc_kpi_status(baseline_hc_ratio, baseline_total),
            "high_critical_current": self._hc_kpi_status(current_hc_ratio, current_total),
            "trend": trend,
        }

    def _score_kpi_status(self, avg: float, total: int) -> KpiStatus:
        """Bepaal KPI-status voor een gemiddelde CSAT-score (ADR-009)."""
        if total == 0 or avg == 0.0:
            return KpiStatus.UNKNOWN
        if avg >= AVG_SCORE_MIN:
            return KpiStatus.OK
        if avg >= 3.5:
            return KpiStatus.WARNING
        return KpiStatus.AT_RISK

    def _hc_kpi_status(self, ratio: float, total: int) -> KpiStatus:
        """Bepaal KPI-status voor de High/Critical-ratio."""
        if total == 0:
            return KpiStatus.UNKNOWN
        if ratio <= HIGH_CRITICAL_MAX:
            return KpiStatus.OK
        if ratio <= 25.0:
            return KpiStatus.WARNING
        return KpiStatus.AT_RISK

    # ------------------------------------------------------------------
    # Intern — hulpfuncties
    # ------------------------------------------------------------------

    def _make_label(self, periods: list[str]) -> str:
        """Genereer automatisch een label voor een periodegroep."""
        if not periods:
            return "—"
        if len(periods) == 1:
            return periods[0]
        first_year, _ = parse_period(periods[0])
        last_year, _ = parse_period(periods[-1])
        if first_year == last_year:
            return str(first_year)
        return f"{periods[0]} - {periods[-1]}"
