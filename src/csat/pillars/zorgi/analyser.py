"""
ZorgiAnalyser — organisatiebrede CSAT-aggregator.

Fase 6a: combineert EvolutionResult-objecten van PHARMA, CARE, CARE ADMIN en ERP4HC
tot één ZorgiResult via gewogen gemiddelden op ticketvolume.

Geen ruwe datalaadlogica — ontvangt uitsluitend al verwerkte EvolutionResult-objecten.
"""

from __future__ import annotations

from csat.core.analysers.evolution_result import EvolutionResult
from csat.pillars.zorgi.result import PillarSummary, ZorgiResult

# Drempelwaarden voor trendclassificatie
_TREND_THRESHOLD_IMPROVE = 0.05  # delta >= +0,05 → improving
_TREND_THRESHOLD_DECLINE = -0.05  # delta <= -0,05 → declining


class ZorgiAnalyser:
    """
    Aggregeert EvolutionResults van alle 4 pillar-analysers.

    Gebruik:
        results = {
            "pharma": evolution_result_pharma,
            "care": evolution_result_care,
            ...
        }
        analyser = ZorgiAnalyser(results)
        zorgi_result = analyser.aggregate()
    """

    def __init__(self, pillar_results: dict[str, EvolutionResult | None]) -> None:
        """
        Initialiseer met een dict van pijlersleutel → EvolutionResult (of None).

        Args:
            pillar_results: Dict met maximaal 4 pijlers
                (pharma, care, care_admin, erp4hc). None voor ontbrekende pijlers.
        """
        self._pillar_results = pillar_results

    # ------------------------------------------------------------------
    # Publieke interface
    # ------------------------------------------------------------------

    def aggregate(self) -> ZorgiResult:
        """
        Combineert 4 pijlers tot 1 ZorgiResult.

        Gewogen gemiddelden op basis van current_total (ticketvolume).
        """
        valid: dict[str, EvolutionResult] = {
            k: v for k, v in self._pillar_results.items() if v is not None
        }

        if not valid:
            return ZorgiResult()

        # Labels afleiden van de eerste geldige pijler
        first = next(iter(valid.values()))
        baseline_label = first.baseline_label
        current_label = first.current_label

        # Per-pijler samenvattingen bouwen
        pillar_summaries: dict[str, PillarSummary | None] = {}
        for key, res in self._pillar_results.items():
            if res is None:
                pillar_summaries[key] = None
            else:
                pillar_summaries[key] = self._build_pillar_summary(key, res)

        valid_summaries = [s for s in pillar_summaries.values() if s is not None]

        # Organisatie-brede gewogen gemiddelden
        org_avg = self._weighted_avg_from_results(valid, "current_avg_score")
        org_baseline_avg = self._weighted_avg_from_results(valid, "baseline_avg_score")
        org_delta = round(org_avg - org_baseline_avg, 2)
        org_pct_pos = self._weighted_avg_from_results(valid, "current_pct_positive")
        org_pct_neg = self._weighted_avg_from_results(valid, "current_pct_negative")
        org_hc = self._weighted_avg_from_results(valid, "current_hc_ratio")
        org_total = sum(r.current_total for r in valid.values())
        org_hospitals = sum(r.current_n_hospitals for r in valid.values())

        # Best/worst pijler
        sorted_summaries = sorted(valid_summaries, key=lambda s: s.current_avg_score, reverse=True)
        best = sorted_summaries[0].pillar if sorted_summaries else ""
        worst = sorted_summaries[-1].pillar if sorted_summaries else ""

        # Trendtelling
        improving = sum(1 for s in valid_summaries if s.trend == "improving")
        stable = sum(1 for s in valid_summaries if s.trend == "stable")
        declining = sum(1 for s in valid_summaries if s.trend == "declining")

        # Aandachtspunten
        most_declining = (
            min(valid_summaries, key=lambda s: s.delta_avg_score).pillar if valid_summaries else ""
        )
        highest_hc = (
            max(valid_summaries, key=lambda s: s.current_hc_ratio).pillar if valid_summaries else ""
        )

        return ZorgiResult(
            pillar="zorgi",
            baseline_label=baseline_label,
            current_label=current_label,
            pillar_summaries=pillar_summaries,
            org_avg_score=round(org_avg, 2),
            org_baseline_avg_score=round(org_baseline_avg, 2),
            org_delta_avg_score=org_delta,
            org_pct_positive=round(org_pct_pos, 1),
            org_pct_negative=round(org_pct_neg, 1),
            org_hc_ratio=round(org_hc, 1),
            org_total_tickets=org_total,
            org_n_hospitals=org_hospitals,
            best_pillar=best,
            worst_pillar=worst,
            pillars_improving=improving,
            pillars_stable=stable,
            pillars_declining=declining,
            pillar_most_declining=most_declining,
            pillar_highest_hc=highest_hc,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_pillar_summary(self, key: str, res: EvolutionResult) -> PillarSummary:
        """Zet een EvolutionResult om naar een compacte PillarSummary."""
        trend = self._classify_trend(res.delta_avg_score)
        return PillarSummary(
            pillar=key,
            current_avg_score=res.current_avg_score,
            baseline_avg_score=res.baseline_avg_score,
            delta_avg_score=res.delta_avg_score,
            current_pct_positive=res.current_pct_positive,
            current_pct_negative=res.current_pct_negative,
            current_hc_ratio=res.current_hc_ratio,
            current_total=res.current_total,
            trend=trend,
        )

    @staticmethod
    def _classify_trend(delta: float) -> str:
        """Classificeer de trend op basis van delta_avg_score."""
        if delta >= _TREND_THRESHOLD_IMPROVE:
            return "improving"
        if delta <= _TREND_THRESHOLD_DECLINE:
            return "declining"
        return "stable"

    @staticmethod
    def _weighted_avg_from_results(results: dict[str, EvolutionResult], attr: str) -> float:
        """
        Gewogen gemiddelde van een attribuut over meerdere EvolutionResults.

        Gewicht = current_total (ticketvolume per pijler).
        Geeft 0.0 terug als er geen resultaten zijn of totaal = 0.
        """
        total_weight = sum(r.current_total for r in results.values())
        if total_weight == 0:
            return 0.0
        weighted_sum: float = sum(getattr(r, attr) * r.current_total for r in results.values())
        return float(weighted_sum / total_weight)
