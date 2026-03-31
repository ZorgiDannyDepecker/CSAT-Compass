"""
Dataklassen voor de evolutie-analyse in CSAT-Compass.

Bevat EvolutionResult en alle helper-dataklassen die de vergelijking
tussen baseline en huidige periode beschrijven.

Fase 3g: uitgebreid met SummaryStats, ScoreDistribution, ResponseTimeInsight,
NegativeCase, KpiTarget en BenchmarkComparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class KpiStatus(StrEnum):
    """Status van een KPI-meting t.o.v. de drempelwaarden (ADR-009)."""

    OK = "ok"
    WARNING = "warning"
    AT_RISK = "at_risk"
    UNKNOWN = "unknown"


@dataclass
class MonthlyDataPoint:
    """Datapunt voor één maand in de evolutie-tijdlijn."""

    period: str  # "YYYY-MM"
    avg_score: float  # Gemiddelde CSAT-score (alleen gescoorde tickets)
    total_tickets: int  # Totaal tickets (inclusief ongescoorde)
    pct_negative: float  # % scores <= 2 t.o.v. gescoorde tickets
    fase: str  # "H1 YYYY" of "H2 YYYY"
    priority_counts: dict[str, int] = field(default_factory=dict)
    # Tickettelling per Jira-prioriteit (Blocker/Critical/Major/Minor/Trivial)
    # Gebruikt door EvolutionVisualiser subplot 3 (prioriteitscompositie).


@dataclass
class IssueTypeComparison:
    """Vergelijking per issue type — baseline vs huidig."""

    issue_type: str
    baseline_score: float
    baseline_pct_neg: float
    current_score: float
    current_pct_neg: float


@dataclass
class PriorityComparison:
    """Vergelijking per prioriteit — baseline vs huidig."""

    priority: str
    baseline_score: float
    baseline_pct_neg: float
    current_score: float
    current_pct_neg: float


@dataclass
class HospitalComparison:
    """Vergelijking per ziekenhuis — baseline vs huidig."""

    hospital: str
    baseline_score: float
    baseline_total: int
    current_score: float | None  # None als ziekenhuis niet aanwezig in huidig
    current_total: int


@dataclass
class ThemeEvolution:
    """Evolutie van een negatief feedbackthema (keyword matching op comment-veld)."""

    theme_key: str  # "responstijd" / "onvolledig" / "communicatie" / ...
    pct_baseline: float  # % van negatieve comments in baseline (score <= 2)
    pct_current: float  # % van negatieve comments in huidige periode
    status: str  # "OPGELOST" / "NOG_AANWEZIG" / "NIEUW"
    # Fase 3g — recurring themes (voorbeeld + actiehint — scope release 1)
    example: str = field(default="")  # Voorbeeldcomment uit huidig/baseline
    action_hint: str = field(default="")  # Regelgebaseerde actiehint per thematype


@dataclass
class ResponseTimeRow:
    """Gemiddelde responstijd per score-niveau (satisfaction_date - created)."""

    score_level: int  # 1-5
    baseline_days: float | None  # None als geen data beschikbaar
    current_days: float | None  # None als geen data beschikbaar


# ---------------------------------------------------------------------------
# Nieuwe dataklassen — Fase 3g (beslissingen 2, 3, 5, 8, 9, 12)
# ---------------------------------------------------------------------------


@dataclass
class SummaryStats:
    """Samenvattingsstatistieken voor één analyseperiode (baseline of huidig)."""

    total_responses: int
    avg_score: float
    median_score: float
    std_dev_score: float
    pct_positive: float
    pct_neutral: float
    pct_negative: float
    period_start: str | None = None  # "YYYY-MM"
    period_end: str | None = None  # "YYYY-MM"
    pct_with_comment: float = 0.0  # % tickets met een niet-lege comment


@dataclass
class ScoreDistribution:
    """Verdeling per scoreniveau 1-5 (beslissing 12)."""

    counts: dict[int, int] = field(default_factory=dict)
    percentages: dict[int, float] = field(default_factory=dict)
    compact_label: str = ""  # "5★:30 (62,5%) | 4★:10 (20,8%) | ..."
    narrative: str = ""  # "Van de 48 responses scoort 62,5% een volle 5★"


@dataclass
class ResponseTimeInsight:
    """Uitgebreide responstijdanalyse met correlatie en pos/neg-vergelijking."""

    avg_days: float = 0.0
    median_days: float = 0.0
    min_days: float = 0.0
    max_days: float = 0.0
    correlation_score: float | None = None  # Pearson r (responstijd ↔ score)
    baseline_correlation_score: float | None = None
    # Pearson r voor de baseline-periode — nodig voor correlatie-omslag detectie in InsightsGenerator
    avg_positive_days: float | None = None  # Gem. responstijd bij score >= 4
    avg_negative_days: float | None = None  # Gem. responstijd bij score <= 2


@dataclass
class NegativeCase:
    """Eén negatief ticket met volledige context (beslissingen 2 + 3)."""

    ticket_id: str  # "SD30-36770" — zichtbaar in rapport
    hospital: str  # Volledige naam — geen anonimisering
    issue_type: str
    score: int
    response_days: float | None  # None als geen satisfaction_date
    category: str  # Primaire probleemclassificatie via THEME_KEYWORDS
    comment: str  # Volledige tekst uit V_CSAT_1 (gesaniteerd)


@dataclass
class KpiTarget:
    """KPI target tracking: baseline → target → huidig → status (beslissing 5)."""

    name: str  # Sleutel, bv. "avg_score_min"
    baseline: float
    target: float
    current: float
    status: str  # "op_schema" | "aandacht" | "kritiek"
    on_track: bool


@dataclass
class BenchmarkComparison:
    """Vergelijkingspunt voor dubbele benchmark (volledig 2025 + H2 2025)."""

    label: str  # "H2 2025" of "2025"
    avg_score: float = 0.0
    pct_positive: float = 0.0
    pct_negative: float = 0.0
    avg_response_days: float = 0.0
    hc_ratio: float = 0.0
    total: int = 0


@dataclass
class EvolutionResult:
    """
    Container voor alle vergelijkingsdata baseline vs huidige periode.

    Dit is de pure data-laag voor de evolutie-analyse.
    Fase 3c (EvolutionExporter) gebruikt dit object als input voor template-rendering.
    Fase 3g voegt rijkere analyse-objecten toe (SummaryStats, ScoreDistribution, etc.).

    ADR-verwijzingen:
    - ADR-006: reactiegraad N/A — niet opgenomen
    - ADR-007: baseline start 01/01/2025
    - ADR-009: KPI OK = avg_score >= 4,00
    """

    # --- Identificatie ---
    pillar: str
    baseline_label: str  # bv. "2025"
    current_label: str  # bv. "2026"

    # --- Kerncijfers (sectie 1 + 3) ---
    baseline_total: int
    current_total: int
    baseline_avg_score: float
    current_avg_score: float
    delta_avg_score: float  # current - baseline, afgerond op 2 decimalen
    baseline_pct_positive: float  # % score >= 4 (t.o.v. gescoorde tickets)
    current_pct_positive: float
    baseline_pct_negative: float  # % score <= 2 (t.o.v. gescoorde tickets)
    current_pct_negative: float
    baseline_avg_response_days: float
    current_avg_response_days: float
    baseline_n_hospitals: int
    current_n_hospitals: int
    baseline_hc_ratio: float  # % High/Critical-tickets
    current_hc_ratio: float

    # --- Trend classificatie ---
    trend_is_structural: bool  # True = delta >= 0,5 (significante verbetering)
    trend_breadth: str  # "breed" / "beperkt" / "gemengd"

    # --- Tijdlijn (sectie 2) ---
    monthly_timeline: list[MonthlyDataPoint] = field(default_factory=list)

    # --- Breakdowns (secties 4-5) ---
    by_issue_type: list[IssueTypeComparison] = field(default_factory=list)
    by_priority: list[PriorityComparison] = field(default_factory=list)

    # --- Responstijd per score-niveau (sectie 5) ---
    response_time_by_score: dict[int, ResponseTimeRow] = field(default_factory=dict)

    # --- Ziekenhuizen (sectie 7) ---
    hospital_comparison: list[HospitalComparison] = field(default_factory=list)
    hospitals_disappeared: list[str] = field(default_factory=list)  # baseline → verdwenen
    hospitals_new: list[str] = field(default_factory=list)  # nieuw in huidig

    # --- Thema's (sectie 8) ---
    negative_themes: list[ThemeEvolution] = field(default_factory=list)

    # --- KPI status (sectie 9) ---
    kpi_status: dict[str, KpiStatus] = field(default_factory=dict)

    # -----------------------------------------------------------------------
    # Fase 3g — nieuwe velden (backward-compatible via field(default=...))
    # -----------------------------------------------------------------------

    # Samenvattingsstatistieken per periode (mediaan, std dev, neutraal %)
    baseline_summary: SummaryStats | None = field(default=None)
    current_summary: SummaryStats | None = field(default=None)

    # Scoreverdeling per niveau (beslissing 12)
    score_distribution_baseline: ScoreDistribution | None = field(default=None)
    score_distribution_current: ScoreDistribution | None = field(default=None)

    # Uitgebreide responstijdanalyse met correlatie (KRITIEK gap)
    response_time_insight: ResponseTimeInsight | None = field(default=None)

    # Negatieve ticket-cases met volledige context (beslissingen 2 + 3)
    negative_cases: list[NegativeCase] = field(default_factory=list)

    # KPI target tracking — 7 targets (beslissing 5)
    kpi_targets: list[KpiTarget] = field(default_factory=list)

    # Dubbele benchmark: H2 van het baselinejaar
    benchmark_h2: BenchmarkComparison | None = field(default=None)

    # Shortlist ziekenhuizen (top/bottom movers) — boven de volledige tabel
    hospital_shortlist: list[HospitalComparison] = field(default_factory=list)

    # Ziekenhuisretentie % (hoeveel baseline-ziekenhuizen nog aanwezig)
    hospital_retention_pct: float = field(default=100.0)
