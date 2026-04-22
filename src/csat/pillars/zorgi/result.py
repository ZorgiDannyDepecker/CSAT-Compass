"""
ZorgiResult — organisatiebrede CSAT-aggregatie van alle 4 pijlers.

Fase 6a: ZORGI Overall Aggregatie.
Ontvangen als output van ZorgiAnalyser.aggregate() na combinatie
van EvolutionResult-objecten van PHARMA, CARE, CARE ADMIN en ERP4HC.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PillarSummary:
    """Compacte samenvatting per pijler voor de ZORGI-aggregatietabel."""

    pillar: str  # "pharma" / "care" / "care_admin" / "erp4hc"
    current_avg_score: float
    baseline_avg_score: float
    delta_avg_score: float
    current_pct_positive: float
    current_pct_negative: float
    current_hc_ratio: float
    current_total: int
    trend: str  # "improving" / "stable" / "declining"


@dataclass
class ZorgiResult:
    """
    Organisatiebrede CSAT-aggregatie van alle 4 pijlers.

    Ontvangen als output van ZorgiAnalyser.aggregate().
    Bevat gewogen gemiddelden + per-pijler overzicht.
    Bedoeld voor executive-niveau rapportage (CEO, COO).
    """

    # --- Identificatie ---
    pillar: str = "zorgi"
    baseline_label: str = ""
    current_label: str = ""

    # --- Per-pijler samenvattingen (None als pijler geen data heeft) ---
    pillar_summaries: dict[str, PillarSummary | None] = field(default_factory=dict)

    # --- Gewogen gemiddelden organisatie-breed ---
    org_avg_score: float = 0.0
    org_baseline_avg_score: float = 0.0
    org_delta_avg_score: float = 0.0
    org_pct_positive: float = 0.0
    org_pct_negative: float = 0.0
    org_hc_ratio: float = 0.0
    org_total_tickets: int = 0
    org_n_hospitals: int = 0

    # --- Top/Bottom pijler (op huidige gemiddelde score) ---
    best_pillar: str = ""
    worst_pillar: str = ""

    # --- Trend per pijler ---
    pillars_improving: int = 0
    pillars_stable: int = 0
    pillars_declining: int = 0

    # --- Aandachtspunten ---
    pillar_most_declining: str = ""  # pijler met sterkste daling (delta)
    pillar_highest_hc: str = ""  # pijler met hoogste High/Critical ratio
