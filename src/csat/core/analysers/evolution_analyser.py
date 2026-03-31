"""
EvolutionAnalyser voor CSAT-Compass.

Vergelijkt twee periodegroepen (baseline vs huidig) en berekent alle metrics
voor de EvolutionResult dataclass.

Spelregels:
- ADR-006: reactiegraad N/A — niet berekenen
- ADR-007: baseline start 01/01/2025 (ANALYSE_START_DATE)
- ADR-009: KPI OK = avg_score >= AVG_SCORE_MIN (4,00)
- Fase 3g: uitgebreid met SummaryStats, ScoreDistribution, ResponseTimeInsight,
           NegativeCase, KpiTarget, BenchmarkComparison
"""

from __future__ import annotations

import re

import pandas as pd
from loguru import logger

from csat.config.pillars import FILTER_COLUMN, HIGH_CRITICAL_PRIORITIES, PILLAR_REGISTRY
from csat.config.settings import (
    ANALYSE_START_DATE,
    AVG_RESPONSE_DAYS_MAX,
    AVG_SCORE_MIN,
    HIGH_CRITICAL_MAX,
    HOSPITAL_RETENTION_MIN,
    PCT_NEGATIVE_MAX,
    PCT_POSITIVE_MIN,
    PCT_WITH_COMMENT_MIN,
)
from csat.utils.date_utils import filter_period, parse_period

from .evolution_result import (
    BenchmarkComparison,
    EvolutionResult,
    HospitalComparison,
    IssueTypeComparison,
    KpiStatus,
    KpiTarget,
    MonthlyDataPoint,
    NegativeCase,
    PriorityComparison,
    ResponseTimeInsight,
    ResponseTimeRow,
    ScoreDistribution,
    SummaryStats,
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

# ---------------------------------------------------------------------------
# Actiehints per thematype (fase 3g — recurring themes scope release 1)
# ---------------------------------------------------------------------------

THEME_ACTION_HINTS: dict[str, str] = {
    "responstijd": (
        "Controleer SLA-naleving en overweeg responstijd-alerts voor tickets "
        "met een openstaande tijd > 5 werkdagen."
    ),
    "onvolledig": (
        "Implementeer een oplossingsbevestiging bij ticket-afhandeling: "
        "klantaccord vereist vóór sluiting."
    ),
    "communicatie": (
        "Activeer proactieve statusupdates bij langlopende tickets (> 5 werkdagen): "
        "automatische melding bij statuswijziging."
    ),
    "urgentie": (
        "Review escalatiebeleid: zorg voor direct klantcontact bij "
        "hoge-urgentie tickets binnen 1 werkdag."
    ),
    "automatisering": (
        "Evalueer automatiseringsopportuniteiten in de ticketworkflow "
        "om repetitieve manuele stappen te elimineren."
    ),
}
# Hulpfunctie: commentaarsanitisering (beslissing 3 — privacy ZORGI-medewerkers)
# ---------------------------------------------------------------------------

#: Pas deze lijst aan met echte medewerkersnamen — bewust leeg in repo (privacy).
ZORGI_EMPLOYEE_NAMES: list[str] = []


def sanitize_comment(comment: str, names: list[str] | None = None) -> str:
    """
    Verwijder ZORGI-medewerkersnamen uit een klantcomment.

    Args:
        comment: Originele commentaartekst uit V_CSAT_1.
        names:   Optionele override van de te verwijderen namen.
                 Standaard: ZORGI_EMPLOYEE_NAMES (zie module-niveau).

    Returns:
        Gesaniteerde commentaartekst — namen vervangen door "[ZORGI]".
    """
    if not comment:
        return comment
    result = str(comment)
    for name in names if names is not None else ZORGI_EMPLOYEE_NAMES:
        if name:
            result = result.replace(name, "[ZORGI]")
    return result


def _fmt_nl(value: float, decimals: int = 1) -> str:
    """Formatteer een getal in ZORGI-notatie (punt als duizendtal, komma als decimaal)."""
    formatted = f"{value:,.{decimals}f}"
    # Python gebruikt "," als duizendtalsscheiding en "." als decimaal — omwisselen
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


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

    # Datumkolom voor periodegroepering
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

        # -------------------------------------------------------------------
        # Fase 3g — nieuwe metrics
        # -------------------------------------------------------------------

        # Samenvattingsstatistieken per periode
        b_pct_comment = self._calc_pct_with_comment(baseline_df)
        c_pct_comment = self._calc_pct_with_comment(current_df)

        baseline_summary = self._calc_summary_stats(baseline_df, baseline_periods, b_pct_comment)
        current_summary = self._calc_summary_stats(current_df, current_periods, c_pct_comment)

        # Scoreverdeling
        score_dist_baseline = self._calc_score_distribution(baseline_df)
        score_dist_current = self._calc_score_distribution(current_df)

        # Responstijdanalyse met correlatie
        response_time_insight = self._calc_response_time_insight(current_df, baseline_df)

        # Negatieve cases met volledige context (huidige periode)
        negative_cases = self._calc_negative_cases(current_df)

        # Ziekenhuisretentie
        if b_hosp > 0:
            hospital_retention_pct = round((b_hosp - len(hospitals_disappeared)) / b_hosp * 100, 1)
        else:
            hospital_retention_pct = 100.0

        # KPI target tracking (7 targets)
        kpi_targets = self._calc_kpi_targets(
            b_avg,
            c_avg,
            b_hc_ratio,
            c_hc_ratio,
            b_pct_pos,
            c_pct_pos,
            b_pct_neg,
            c_pct_neg,
            b_resp,
            c_resp,
            b_pct_comment,
            c_pct_comment,
            hospital_retention_pct,
        )

        # Dubbele benchmark: H2 van baselinejaar
        benchmark_h2 = self._calc_benchmark_h2(baseline_periods)

        # Shortlist ziekenhuizen (top/bottom movers)
        hospital_shortlist = self._calc_hospital_shortlist(hospital_comparison)

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
            # Fase 3g
            baseline_summary=baseline_summary,
            current_summary=current_summary,
            score_distribution_baseline=score_dist_baseline,
            score_distribution_current=score_dist_current,
            response_time_insight=response_time_insight,
            negative_cases=negative_cases,
            kpi_targets=kpi_targets,
            benchmark_h2=benchmark_h2,
            hospital_shortlist=hospital_shortlist,
            hospital_retention_pct=hospital_retention_pct,
        )

        logger.info(
            f"[EvolutionAnalyser:{self._pillar_key}] Analyse voltooid — "
            f"baseline={bl} ({b_total:,} tickets, avg={b_avg}) | "
            f"current={cl} ({c_total:,} tickets, avg={c_avg}) | "
            f"delta={delta:+.2f} | {'structureel' if trend_is_structural else 'onduidelijk'} "
            f"({trend_breadth}) | retentie={hospital_retention_pct}%"
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

    def _calc_pct_with_comment(self, df: pd.DataFrame) -> float:
        """Bereken het % tickets met een niet-lege klantcomment."""
        if df.empty:
            return 0.0
        has_comment = df["comment"].fillna("").str.strip().str.len() > 0
        return round(has_comment.sum() / len(df) * 100, 1)

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
        Fase 3g: voegt example (voorbeeldcomment) en action_hint toe per thema.
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

                # Voorbeeldcomment: uit huidig (bij NIEUW/NOG_AANWEZIG) of baseline (bij OPGELOST)
                example = ""
                source_neg = current_neg if status in ("NIEUW", "NOG_AANWEZIG") else baseline_neg
                if not source_neg.empty:
                    matched = source_neg[
                        source_neg["comment"]
                        .fillna("")
                        .str.lower()
                        .str.contains(pattern, regex=True)
                    ]
                    if not matched.empty:
                        raw = str(matched.iloc[0].get("comment", "") or "")
                        example = sanitize_comment(raw)

                # Regelgebaseerde actiehint per thematype
                action_hint = THEME_ACTION_HINTS.get(theme_key, "")

                results.append(
                    ThemeEvolution(
                        theme_key=theme_key,
                        pct_baseline=pct_baseline,
                        pct_current=pct_current,
                        status=status,
                        example=example,
                        action_hint=action_hint,
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
        """Bepaal KPI-status voor alle metrics (ADR-009)."""
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
    # Intern — Fase 3g: nieuwe metric-methoden
    # ------------------------------------------------------------------

    def _calc_summary_stats(
        self, df: pd.DataFrame, periods: list[str], pct_with_comment: float
    ) -> SummaryStats:
        """Bereken samenvattingsstatistieken voor één analyseperiode."""
        scored = df[df["score"].notna()]
        total = len(df)
        avg_score = self._calc_avg_score(df)

        median_score = round(float(scored["score"].median()), 2) if not scored.empty else 0.0
        std_dev = round(float(scored["score"].std(ddof=1)), 2) if len(scored) > 1 else 0.0

        pct_positive = self._calc_pct_scored(df, lambda s: s >= 4.0)
        pct_negative = self._calc_pct_scored(df, lambda s: s <= 2.0)
        pct_neutral = round(max(0.0, 100.0 - pct_positive - pct_negative), 1)

        period_start = min(periods) if periods else None
        period_end = max(periods) if periods else None

        return SummaryStats(
            total_responses=total,
            avg_score=avg_score,
            median_score=median_score,
            std_dev_score=std_dev,
            pct_positive=pct_positive,
            pct_neutral=pct_neutral,
            pct_negative=pct_negative,
            period_start=period_start,
            period_end=period_end,
            pct_with_comment=pct_with_comment,
        )

    def _calc_score_distribution(self, df: pd.DataFrame) -> ScoreDistribution:
        """
        Bereken de scoreverdeling per niveau 1-5 (beslissing 12).

        Returns:
            ScoreDistribution met counts, percentages, compact_label en narrative.
        """
        scored = df[df["score"].notna()]
        n = len(scored)

        counts: dict[int, int] = {}
        percentages: dict[int, float] = {}
        for level in range(1, 6):
            cnt = int((scored["score"] == float(level)).sum())
            counts[level] = cnt
            percentages[level] = round(cnt / n * 100, 1) if n > 0 else 0.0

        # Compact label (5★ → 1★)
        parts = []
        for level in range(5, 0, -1):
            pct = percentages.get(level, 0.0)
            parts.append(f"{level}★:{counts.get(level, 0)} ({_fmt_nl(pct, 1)}%)")
        compact_label = " | ".join(parts)

        # Narratief
        if n > 0:
            top_level = max(range(1, 6), key=lambda k: counts.get(k, 0))
            top_pct = percentages.get(top_level, 0.0)
            if top_level == 5:
                narrative = f"Van de {n} responses scoort {_fmt_nl(top_pct, 1)}% een volle 5★."
            elif top_level >= 4:
                narrative = (
                    f"Van de {n} responses beoordeelt {_fmt_nl(top_pct, 1)}% het ticket "
                    f"positief ({top_level}★ of hoger)."
                )
            else:
                narrative = (
                    f"Van de {n} responses is de meerderheid ({_fmt_nl(top_pct, 1)}%) "
                    f"geconcentreerd rond {top_level}★."
                )
        else:
            narrative = "Geen gescoorde responses beschikbaar."

        return ScoreDistribution(
            counts=counts,
            percentages=percentages,
            compact_label=compact_label,
            narrative=narrative,
        )

    def _calc_response_time_insight(  # noqa: C901
        self, df: pd.DataFrame, baseline_df: pd.DataFrame | None = None
    ) -> ResponseTimeInsight:
        """
        Bereken uitgebreide responstijdstatistieken incl. correlatie (KRITIEK gap).

        Correlatie: Pearson r tussen response_days en score (minimaal 5 datapunten).
        """
        if df.empty:
            return ResponseTimeInsight()

        created = pd.to_datetime(df["created"])
        sat = pd.to_datetime(df["satisfaction_date"])
        all_days = (sat - created).dt.days

        valid_mask = all_days.notna() & (all_days >= 0)
        valid_days = all_days[valid_mask]

        if valid_days.empty:
            return ResponseTimeInsight()

        avg_d = round(float(valid_days.mean()), 1)
        median_d = round(float(valid_days.median()), 1)
        min_d = round(float(valid_days.min()), 1)
        max_d = round(float(valid_days.max()), 1)

        # Correlatie responstijd ↔ score (minimaal 5 datapunten)
        correlation: float | None = None
        df2 = df.copy()
        df2["_days"] = all_days
        scored_with_days = df2[df2["score"].notna() & df2["_days"].notna() & (df2["_days"] >= 0)]
        if len(scored_with_days) >= 5:
            try:
                corr_val = scored_with_days["score"].corr(scored_with_days["_days"])
                if pd.notna(corr_val):
                    correlation = round(float(corr_val), 3)
            except Exception as exc:  # pragma: no cover
                logger.debug(f"Correlatie-berekening mislukt: {exc}")

        # Gem. responstijd positieve vs negatieve scores
        avg_positive: float | None = None
        avg_negative: float | None = None
        if "score" in df2.columns:
            pos = df2[
                df2["score"].notna()
                & (df2["score"] >= 4.0)
                & df2["_days"].notna()
                & (df2["_days"] >= 0)
            ]
            neg = df2[
                df2["score"].notna()
                & (df2["score"] <= 2.0)
                & df2["_days"].notna()
                & (df2["_days"] >= 0)
            ]
            if not pos.empty:
                avg_positive = round(float(pos["_days"].mean()), 1)
            if not neg.empty:
                avg_negative = round(float(neg["_days"].mean()), 1)

        # Baseline-correlatie (voor correlatie-omslag detectie)
        baseline_correlation: float | None = None
        if baseline_df is not None and not baseline_df.empty:
            b_created = pd.to_datetime(baseline_df["created"])
            b_sat = pd.to_datetime(baseline_df["satisfaction_date"])
            b_days = (b_sat - b_created).dt.days
            b_df2 = baseline_df.copy()
            b_df2["_days"] = b_days
            b_scored = b_df2[
                b_df2["score"].notna() & b_df2["_days"].notna() & (b_df2["_days"] >= 0)
            ]
            if len(b_scored) >= 5:
                try:
                    b_corr = b_scored["score"].corr(b_scored["_days"])
                    if pd.notna(b_corr):
                        baseline_correlation = round(float(b_corr), 3)
                except Exception as exc:
                    logger.debug(f"Baseline correlatie-berekening mislukt: {exc}")

        return ResponseTimeInsight(
            avg_days=avg_d,
            median_days=median_d,
            min_days=min_d,
            max_days=max_d,
            correlation_score=correlation,
            avg_positive_days=avg_positive,
            avg_negative_days=avg_negative,
            baseline_correlation_score=baseline_correlation,
        )

    def _calc_negative_cases(self, df: pd.DataFrame) -> list[NegativeCase]:
        """
        Extraheer negatieve ticket-cases met volledige context (beslissingen 2 + 3).

        Geen limiet op quotelengte. Ziekenhuisnamen worden niet geanonimiseerd.
        Enige sanitizing: eventuele ZORGI-medewerkersnamen via sanitize_comment().
        """
        neg = df[df["score"].notna() & (df["score"] <= 2.0)].copy()
        if neg.empty:
            return []

        created = pd.to_datetime(neg["created"])
        sat = pd.to_datetime(neg["satisfaction_date"])
        neg = neg.copy()
        neg["_days"] = (sat - created).dt.days

        cases: list[NegativeCase] = []
        for _, row in neg.iterrows():
            comment_raw = str(row.get("comment", "") or "")
            comment_lower = comment_raw.lower()

            # Primaire probleemclassificatie o.b.v. THEME_KEYWORDS
            category = "—"
            for theme_key, keywords in THEME_KEYWORDS.items():
                pattern = "|".join(re.escape(kw) for kw in keywords)
                if re.search(pattern, comment_lower):
                    category = theme_key
                    break

            response_days: float | None = None
            days_val = row.get("_days")
            if pd.notna(days_val) and days_val >= 0:
                response_days = round(float(days_val), 1)

            cases.append(
                NegativeCase(
                    ticket_id=str(row.get("key", "—")),
                    hospital=str(row.get("hospital", "—")),
                    issue_type=str(row.get("issue_type", "—")),
                    score=int(row["score"]),
                    response_days=response_days,
                    category=category,
                    comment=sanitize_comment(comment_raw),
                )
            )

        # Sorteer: laagste score eerst, daarna langste responstijd
        cases.sort(key=lambda c: (c.score, -(c.response_days or 0)))
        return cases

    def _calc_kpi_targets(
        self,
        b_avg: float,
        c_avg: float,
        b_hc_ratio: float,
        c_hc_ratio: float,
        b_pct_pos: float,
        c_pct_pos: float,
        b_pct_neg: float,
        c_pct_neg: float,
        b_resp: float,
        c_resp: float,
        b_pct_comment: float,
        c_pct_comment: float,
        hospital_retention_pct: float,
    ) -> list[KpiTarget]:
        """
        Bereken KPI target tracking voor alle 7 targets (beslissing 5).

        Status-logica:
        - higher_is_better=True:  op_schema ≥ target | aandacht ≥ target*0,9 | kritiek anders
        - higher_is_better=False: op_schema ≤ target | aandacht ≤ target*1,1 | kritiek anders
        """

        def _make(
            name: str,
            baseline: float,
            target: float,
            current: float,
            higher: bool = True,
        ) -> KpiTarget:
            if higher:
                on_track = bool(current >= target)
                if on_track:
                    status = "op_schema"
                elif current >= target * 0.9:
                    status = "aandacht"
                else:
                    status = "kritiek"
            else:
                on_track = bool(current <= target)
                if on_track:
                    status = "op_schema"
                elif current <= target * 1.1:
                    status = "aandacht"
                else:
                    status = "kritiek"
            return KpiTarget(
                name=name,
                baseline=float(round(baseline, 2)),
                target=float(round(target, 2)),
                current=float(round(current, 2)),
                status=status,
                on_track=on_track,
            )

        return [
            _make("avg_score_min", b_avg, AVG_SCORE_MIN, c_avg, higher=True),
            _make("high_critical_max", b_hc_ratio, HIGH_CRITICAL_MAX, c_hc_ratio, higher=False),
            _make("pct_positive_min", b_pct_pos, PCT_POSITIVE_MIN, c_pct_pos, higher=True),
            _make("pct_negative_max", b_pct_neg, PCT_NEGATIVE_MAX, c_pct_neg, higher=False),
            _make("avg_response_days_max", b_resp, AVG_RESPONSE_DAYS_MAX, c_resp, higher=False),
            _make(
                "pct_with_comment_min",
                b_pct_comment,
                PCT_WITH_COMMENT_MIN,
                c_pct_comment,
                higher=True,
            ),
            _make(
                "hospital_retention_min",
                100.0,
                HOSPITAL_RETENTION_MIN,
                hospital_retention_pct,
                higher=True,
            ),
        ]

    def _calc_benchmark_h2(self, baseline_periods: list[str]) -> BenchmarkComparison | None:
        """
        Bereken de H2-benchmark (maanden 7-12) uit de baseline-periodes.

        Returns None als er geen H2-periodes aanwezig zijn.
        """
        h2_periods = [p for p in baseline_periods if parse_period(p)[1] >= 7]
        if not h2_periods:
            return None

        h2_df = self._get_df_for_periods(h2_periods)
        if h2_df.empty:
            return None

        _, hc_ratio = self._calc_high_critical(h2_df)
        baseline_year = parse_period(h2_periods[0])[0]

        return BenchmarkComparison(
            label=f"H2 {baseline_year}",
            avg_score=self._calc_avg_score(h2_df),
            pct_positive=self._calc_pct_scored(h2_df, lambda s: s >= 4.0),
            pct_negative=self._calc_pct_scored(h2_df, lambda s: s <= 2.0),
            avg_response_days=self._calc_avg_response_days(h2_df),
            hc_ratio=hc_ratio,
            total=len(h2_df),
        )

    def _calc_hospital_shortlist(
        self, comparison: list[HospitalComparison]
    ) -> list[HospitalComparison]:
        """
        Geef de top/bottom movers — ziekenhuizen met de grootste score-delta.

        Top 3 verbeteraars + top 3 dalers (of minder als niet beschikbaar).
        Alleen ziekenhuizen aanwezig in beide periodes.
        """
        shared = [h for h in comparison if h.current_score is not None and h.baseline_score > 0]
        if not shared:
            return []

        with_delta = sorted(shared, key=lambda h: (h.current_score or 0) - h.baseline_score)

        n = min(3, len(with_delta))
        bottom = with_delta[:n]  # Meeste daling
        top = with_delta[-(n):]  # Meeste verbetering

        # Dedupliceer en bewaar volgorde (slechtste eerst)
        seen: set[str] = set()
        shortlist: list[HospitalComparison] = []
        for h in bottom + list(reversed(top)):
            if h.hospital not in seen:
                seen.add(h.hospital)
                shortlist.append(h)
        return shortlist

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
