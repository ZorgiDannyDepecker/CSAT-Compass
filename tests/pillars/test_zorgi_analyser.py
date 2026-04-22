"""
Unit tests voor ZorgiAnalyser en ZorgiResult.

Fase 6a: test aggregatie, gewogen gemiddelden, best/worst pijler,
trendclassificatie en randgevallen (lege input, 1 pijler).
"""

from __future__ import annotations

import pytest

from csat.core.analysers.evolution_result import EvolutionResult
from csat.pillars.zorgi.analyser import ZorgiAnalyser
from csat.pillars.zorgi.result import PillarSummary, ZorgiResult

# ------------------------------------------------------------------
# Helpers / fixtures
# ------------------------------------------------------------------


def _make_evolution_result(
    pillar: str,
    current_total: int,
    current_avg_score: float,
    baseline_avg_score: float,
    current_pct_positive: float = 70.0,
    current_pct_negative: float = 10.0,
    current_hc_ratio: float = 5.0,
    current_n_hospitals: int = 3,
) -> EvolutionResult:
    """Maak een minimale EvolutionResult aan voor testdoeleinden."""
    delta = round(current_avg_score - baseline_avg_score, 2)
    return EvolutionResult(
        pillar=pillar,
        baseline_label="2025",
        current_label="2026",
        baseline_total=current_total,
        current_total=current_total,
        baseline_avg_score=baseline_avg_score,
        current_avg_score=current_avg_score,
        delta_avg_score=delta,
        baseline_pct_positive=65.0,
        current_pct_positive=current_pct_positive,
        baseline_pct_negative=15.0,
        current_pct_negative=current_pct_negative,
        baseline_avg_response_days=2.0,
        current_avg_response_days=2.0,
        baseline_n_hospitals=current_n_hospitals,
        current_n_hospitals=current_n_hospitals,
        baseline_hc_ratio=5.0,
        current_hc_ratio=current_hc_ratio,
        trend_is_structural=False,
        trend_breadth="beperkt",
    )


@pytest.fixture
def vier_pijler_results() -> dict[str, EvolutionResult]:
    """4 realistische pijler-resultaten voor aggregatietests."""
    return {
        "pharma": _make_evolution_result("pharma", 100, 4.55, 4.30, 85.0, 5.0, 4.0, 5),
        "care": _make_evolution_result("care", 80, 4.20, 4.10, 75.0, 10.0, 6.0, 4),
        "care_admin": _make_evolution_result("care_admin", 60, 4.10, 4.25, 70.0, 12.0, 7.0, 3),
        "erp4hc": _make_evolution_result("erp4hc", 40, 3.95, 4.00, 65.0, 15.0, 10.0, 2),
    }


# ------------------------------------------------------------------
# TestZorgiResultDatastructuur
# ------------------------------------------------------------------


class TestZorgiResultDatastructuur:
    """Basiscontroles op de ZorgiResult-dataklasse."""

    def test_default_instantiatie(self) -> None:
        """ZorgiResult kan zonder argumenten worden aangemaakt."""
        result = ZorgiResult()
        assert result.pillar == "zorgi"
        assert result.org_avg_score == 0.0
        assert result.org_total_tickets == 0
        assert result.pillar_summaries == {}

    def test_pillar_summary_instantiatie(self) -> None:
        """PillarSummary kan direct worden aangemaakt."""
        ps = PillarSummary(
            pillar="pharma",
            current_avg_score=4.55,
            baseline_avg_score=4.30,
            delta_avg_score=0.25,
            current_pct_positive=85.0,
            current_pct_negative=5.0,
            current_hc_ratio=4.0,
            current_total=100,
            trend="improving",
        )
        assert ps.pillar == "pharma"
        assert ps.trend == "improving"


# ------------------------------------------------------------------
# TestZorgiAnalyserLegeInput
# ------------------------------------------------------------------


class TestZorgiAnalyserLegeInput:
    """Randgeval: geen pijlers beschikbaar."""

    def test_lege_dict_geeft_default_zorgi_result(self) -> None:
        """Lege input → ZorgiResult met standaardwaarden."""
        analyser = ZorgiAnalyser({})
        result = analyser.aggregate()
        assert isinstance(result, ZorgiResult)
        assert result.org_avg_score == 0.0
        assert result.org_total_tickets == 0
        assert result.best_pillar == ""
        assert result.worst_pillar == ""

    def test_alle_none_pijlers(self) -> None:
        """Alle pijlers None → ZorgiResult met standaardwaarden."""
        analyser = ZorgiAnalyser(
            {
                "pharma": None,
                "care": None,
                "care_admin": None,
                "erp4hc": None,
            }
        )
        result = analyser.aggregate()
        assert result.org_avg_score == 0.0
        assert result.org_total_tickets == 0


# ------------------------------------------------------------------
# TestZorgiAnalyserEénPijler
# ------------------------------------------------------------------


class TestZorgiAnalyserEénPijler:
    """Aggregatie met slechts 1 geldige pijler (rest None)."""

    def test_een_pijler_geeft_correct_resultaat(self) -> None:
        """Met 1 pijler moet org_avg_score gelijk zijn aan die pijler."""
        er = _make_evolution_result("pharma", 50, 4.50, 4.20)
        analyser = ZorgiAnalyser(
            {
                "pharma": er,
                "care": None,
                "care_admin": None,
                "erp4hc": None,
            }
        )
        result = analyser.aggregate()
        assert result.org_avg_score == pytest.approx(4.50, abs=0.01)
        assert result.org_total_tickets == 50
        assert result.best_pillar == "pharma"
        assert result.worst_pillar == "pharma"

    def test_een_pijler_labels_overgenomen(self) -> None:
        """Labels (baseline/current) worden overgenomen van de actieve pijler."""
        er = _make_evolution_result("pharma", 50, 4.50, 4.20)
        analyser = ZorgiAnalyser({"pharma": er})
        result = analyser.aggregate()
        assert result.baseline_label == "2025"
        assert result.current_label == "2026"


# ------------------------------------------------------------------
# TestZorgiAnalyserGewogenGemiddelde
# ------------------------------------------------------------------


class TestZorgiAnalyserGewogenGemiddelde:
    """Correctheid van gewogen gemiddelden op ticketvolume."""

    def test_gewogen_gemiddelde_score(self) -> None:
        """
        Twee pijlers: pharma 100 tickets @ 4,0 en care 100 tickets @ 3,0.
        Verwacht gemiddelde = 3,50.
        """
        results = {
            "pharma": _make_evolution_result("pharma", 100, 4.0, 4.0),
            "care": _make_evolution_result("care", 100, 3.0, 3.0),
        }
        analyser = ZorgiAnalyser(results)  # type: ignore[arg-type]
        result = analyser.aggregate()
        assert result.org_avg_score == pytest.approx(3.50, abs=0.01)

    def test_gewogen_gemiddelde_ongelijk_volume(self) -> None:
        """
        pharma 200 tickets @ 4,0 en care 100 tickets @ 3,0.
        Verwacht: (200*4 + 100*3) / 300 = 3,667.
        """
        results = {
            "pharma": _make_evolution_result("pharma", 200, 4.0, 4.0),
            "care": _make_evolution_result("care", 100, 3.0, 3.0),
        }
        analyser = ZorgiAnalyser(results)  # type: ignore[arg-type]
        result = analyser.aggregate()
        expected = (200 * 4.0 + 100 * 3.0) / 300
        assert result.org_avg_score == pytest.approx(expected, abs=0.01)

    def test_total_tickets_is_som(self, vier_pijler_results: dict) -> None:
        """org_total_tickets = som van alle pijlers."""
        analyser = ZorgiAnalyser(vier_pijler_results)
        result = analyser.aggregate()
        assert result.org_total_tickets == 100 + 80 + 60 + 40

    def test_org_delta_klopt(self, vier_pijler_results: dict) -> None:
        """org_delta = org_current_avg - org_baseline_avg."""
        analyser = ZorgiAnalyser(vier_pijler_results)
        result = analyser.aggregate()
        assert result.org_delta_avg_score == pytest.approx(
            result.org_avg_score - result.org_baseline_avg_score, abs=0.01
        )


# ------------------------------------------------------------------
# TestZorgiAnalyserBestWorst
# ------------------------------------------------------------------


class TestZorgiAnalyserBestWorst:
    """Detectie van best/worst pijler op huidige gemiddelde score."""

    def test_best_pijler_is_hoogste_score(self, vier_pijler_results: dict) -> None:
        """pharma (4,55) is de best scorende pijler."""
        analyser = ZorgiAnalyser(vier_pijler_results)
        result = analyser.aggregate()
        assert result.best_pillar == "pharma"

    def test_worst_pijler_is_laagste_score(self, vier_pijler_results: dict) -> None:
        """erp4hc (3,95) is de slechtst scorende pijler."""
        analyser = ZorgiAnalyser(vier_pijler_results)
        result = analyser.aggregate()
        assert result.worst_pillar == "erp4hc"


# ------------------------------------------------------------------
# TestZorgiAnalyserTrend
# ------------------------------------------------------------------


class TestZorgiAnalyserTrend:
    """Trendclassificatie en -telling."""

    def test_trendtelling_vier_pijlers(self, vier_pijler_results: dict) -> None:
        """
        pharma: +0,25 → improving
        care:   +0,10 → improving
        care_admin: -0,15 → declining
        erp4hc: -0,05 → declining (net op grens)
        """
        analyser = ZorgiAnalyser(vier_pijler_results)
        result = analyser.aggregate()
        assert result.pillars_improving == 2
        assert result.pillars_declining == 2
        assert result.pillars_stable == 0

    def test_trend_improving_drempel(self) -> None:
        """Delta van +0,05 → precies op grens: moet improving zijn."""
        er = _make_evolution_result("pharma", 50, 4.25, 4.20)  # delta = +0,05
        analyser = ZorgiAnalyser({"pharma": er})
        result = analyser.aggregate()
        assert result.pillars_improving == 1

    def test_trend_stable_tussen_drempels(self) -> None:
        """Delta van 0,00 → stable."""
        er = _make_evolution_result("pharma", 50, 4.20, 4.20)  # delta = 0,00
        analyser = ZorgiAnalyser({"pharma": er})
        result = analyser.aggregate()
        assert result.pillars_stable == 1

    def test_trend_declining_drempel(self) -> None:
        """Delta van -0,05 → precies op grens: declining."""
        er = _make_evolution_result("pharma", 50, 4.15, 4.20)  # delta = -0,05
        analyser = ZorgiAnalyser({"pharma": er})
        result = analyser.aggregate()
        assert result.pillars_declining == 1


# ------------------------------------------------------------------
# TestZorgiAnalyserAandachtspunten
# ------------------------------------------------------------------


class TestZorgiAnalyserAandachtspunten:
    """Detectie van pillar_most_declining en pillar_highest_hc."""

    def test_meest_dalende_pijler(self, vier_pijler_results: dict) -> None:
        """care_admin heeft delta -0,15 — meest dalend."""
        analyser = ZorgiAnalyser(vier_pijler_results)
        result = analyser.aggregate()
        assert result.pillar_most_declining == "care_admin"

    def test_hoogste_hc_ratio(self, vier_pijler_results: dict) -> None:
        """erp4hc heeft hc_ratio 10,0 — hoogste."""
        analyser = ZorgiAnalyser(vier_pijler_results)
        result = analyser.aggregate()
        assert result.pillar_highest_hc == "erp4hc"


# ------------------------------------------------------------------
# TestZorgiAnalyserPillarSummaries
# ------------------------------------------------------------------


class TestZorgiAnalyserPillarSummaries:
    """Controle op de pillar_summaries dict in ZorgiResult."""

    def test_summaries_aanwezig_voor_geldige_pijlers(self, vier_pijler_results: dict) -> None:
        """Alle 4 pijlers moeten een PillarSummary hebben."""
        analyser = ZorgiAnalyser(vier_pijler_results)
        result = analyser.aggregate()
        for key in ("pharma", "care", "care_admin", "erp4hc"):
            assert key in result.pillar_summaries
            assert isinstance(result.pillar_summaries[key], PillarSummary)

    def test_none_pijler_in_summaries(self) -> None:
        """None-pijlers worden als None opgenomen in pillar_summaries."""
        analyser = ZorgiAnalyser(
            {
                "pharma": _make_evolution_result("pharma", 50, 4.5, 4.2),
                "care": None,
            }
        )
        result = analyser.aggregate()
        assert result.pillar_summaries["care"] is None
        assert isinstance(result.pillar_summaries["pharma"], PillarSummary)

    def test_summary_data_klopt(self, vier_pijler_results: dict) -> None:
        """PillarSummary voor pharma bevat correcte waarden."""
        analyser = ZorgiAnalyser(vier_pijler_results)
        result = analyser.aggregate()
        pharma_summary = result.pillar_summaries["pharma"]
        assert pharma_summary is not None
        assert pharma_summary.current_avg_score == pytest.approx(4.55, abs=0.01)
        assert pharma_summary.current_total == 100
        assert pharma_summary.trend == "improving"
