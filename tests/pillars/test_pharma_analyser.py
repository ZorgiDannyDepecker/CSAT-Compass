"""
Unit tests voor PharmaAnalyser.

Test KPI-berekeningen, drempelwaardeevaluatie en kpi_status()
op basis van de conftest.py sample_df fixture.
"""

import pandas as pd
import pytest

from csat.pillars.pharma import config as pharma_config
from csat.pillars.pharma.analyser import PharmaAnalyser

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def analyser(sample_df: pd.DataFrame) -> PharmaAnalyser:
    """PharmaAnalyser geladen met de gedeelde testdataset."""
    return PharmaAnalyser(sample_df)


@pytest.fixture
def analyser_leeg(empty_df: pd.DataFrame) -> PharmaAnalyser:
    """PharmaAnalyser op lege dataset — test randgevallen."""
    return PharmaAnalyser(empty_df)


# ------------------------------------------------------------------
# Pijlerfilter
# ------------------------------------------------------------------


class TestPharmaFilter:
    """Controleer dat de PHARMA-filter correct werkt."""

    def test_alleen_pharma_tickets_geladen(self, analyser: PharmaAnalyser) -> None:
        """Na filter moet het interne DataFrame enkel PHARMA-rijen bevatten."""
        assert all(analyser._pillar_df["product"].str.upper() == "PHARMA")

    def test_aantal_pharma_tickets(self, analyser: PharmaAnalyser) -> None:
        """Sample bevat 8 PHARMA-tickets (6 jan + 2 feb)."""
        assert len(analyser._pillar_df) == 8

    def test_care_tickets_gefilterd(self, analyser: PharmaAnalyser) -> None:
        """CARE-tickets mogen niet in de PHARMA-analyser zitten."""
        assert "CARE" not in analyser._pillar_df["product"].values


# ------------------------------------------------------------------
# KPI-berekeningen — jan 2026
# ------------------------------------------------------------------


class TestKpiJan2026:
    """
    Tests op bekende waarden uit de sample fixture voor jan 2026:
    - 6 tickets: SD-001 t/m SD-006
    - SD-006 heeft geen score → 5 gescoord
    - Reactiegraad = 5/6 = 83,3%
    - Scores: 4, 3, 5, 2, 5 → gem = 3.8
    - High/Critical: SD-001 (High) + SD-002 (Critical) = 2/6 = 33,3%
    """

    def test_totaal_tickets(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.total_tickets == 6

    def test_scored_tickets(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.scored_tickets == 5

    def test_reactiegraad(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.reactiegraad == pytest.approx(83.3, abs=0.1)

    def test_avg_score(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.avg_score == pytest.approx(3.8, abs=0.01)

    def test_high_critical_count(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.high_critical_count == 2

    def test_high_critical_ratio(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.high_critical_ratio == pytest.approx(33.3, abs=0.1)

    def test_pillar_label(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.pillar == "pharma"

    def test_period_label(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.period == "2026-01"

    def test_ziekenhuizen_aanwezig(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert "AZ Groeninge" in result.hospitals
        assert "UZ Brussel" in result.hospitals

    def test_per_hospital_structuur(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        for _hospital, kpis in result.per_hospital.items():
            assert "total_tickets" in kpis
            assert "reactiegraad" in kpis
            assert "avg_score" in kpis
            assert "high_critical_ratio" in kpis


# ------------------------------------------------------------------
# KPI-berekeningen — randgevallen
# ------------------------------------------------------------------


class TestKpiRandgevallen:
    """Tests op lege dataset en onbekende periode."""

    def test_lege_dataset_geeft_nullen(self, analyser_leeg: PharmaAnalyser) -> None:
        result = analyser_leeg.analyse("2026-01")
        assert result.total_tickets == 0
        assert result.reactiegraad == 0.0
        assert result.avg_score == 0.0
        assert result.high_critical_ratio == 0.0
        assert result.hospitals == []

    def test_onbekende_periode_geeft_nullen(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2020-06")
        assert result.total_tickets == 0
        assert result.reactiegraad == 0.0


# ------------------------------------------------------------------
# Drempelwaardeevaluatie
# ------------------------------------------------------------------


class TestDrempelwaardeEvaluatie:
    """Controleer dat kpi_status() correct True/False retourneert."""

    def test_reactiegraad_te_laag(self, analyser: PharmaAnalyser) -> None:
        """Jan 2026: reactiegraad 83,3% < drempel 85% → False."""
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert status["reactiegraad_ok"] is False

    def test_high_critical_te_hoog(self, analyser: PharmaAnalyser) -> None:
        """Jan 2026: H/C 33,3% > drempel 15% → False."""
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert status["high_critical_ok"] is False

    def test_kpi_status_bevat_verplichte_sleutels(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "reactiegraad_ok" in status
        assert "high_critical_ok" in status

    def test_avg_score_niet_in_status_als_tbd(self, analyser: PharmaAnalyser) -> None:
        """Zolang AVG_SCORE_MIN = None is de sleutel afwezig in kpi_status."""
        assert pharma_config.AVG_SCORE_MIN is None
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "avg_score_ok" not in status

    def test_reactiegraad_ok_bij_voldoende_respons(self, analyser: PharmaAnalyser) -> None:
        """Feb 2026: 2/2 scores = 100% reactiegraad → True."""
        result = analyser.analyse("2026-02")
        status = analyser.kpi_status(result)
        assert status["reactiegraad_ok"] is True

    def test_high_critical_ok_bij_laag_aandeel(self, analyser: PharmaAnalyser) -> None:
        """Feb 2026: 1 High op 2 tickets = 50% — nog steeds boven drempel."""
        result = analyser.analyse("2026-02")
        status = analyser.kpi_status(result)
        # SD-007 is High → 1/2 = 50% > 15% → False
        assert status["high_critical_ok"] is False


# ------------------------------------------------------------------
# to_dict
# ------------------------------------------------------------------


class TestKpiResultToDict:
    """Controleer de serialisatie van KpiResult."""

    def test_to_dict_bevat_alle_sleutels(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse("2026-01")
        d = result.to_dict()
        verplicht = [
            "period",
            "pillar",
            "total_tickets",
            "scored_tickets",
            "reactiegraad",
            "avg_score",
            "high_critical_count",
            "high_critical_ratio",
            "hospitals",
        ]
        for sleutel in verplicht:
            assert sleutel in d, f"Sleutel ontbreekt in to_dict(): {sleutel}"

    def test_to_dict_hospitals_is_getal(self, analyser: PharmaAnalyser) -> None:
        """to_dict() slaat het AANTAL ziekenhuizen op, niet de lijst."""
        result = analyser.analyse("2026-01")
        d = result.to_dict()
        assert isinstance(d["hospitals"], int)
        assert d["hospitals"] == 2


# ------------------------------------------------------------------
# YTD
# ------------------------------------------------------------------


class TestYtd:
    """Tests voor de YTD-aggregatie."""

    def test_ytd_jan_feb(self, analyser: PharmaAnalyser) -> None:
        """YTD jan-feb 2026: alle 8 PHARMA-tickets."""
        result = analyser.analyse_ytd(year=2026, up_to_month=2)
        assert result.total_tickets == 8

    def test_ytd_jan_only(self, analyser: PharmaAnalyser) -> None:
        """YTD t/m jan 2026: 6 PHARMA-tickets."""
        result = analyser.analyse_ytd(year=2026, up_to_month=1)
        assert result.total_tickets == 6

    def test_ytd_period_label(self, analyser: PharmaAnalyser) -> None:
        result = analyser.analyse_ytd(year=2026, up_to_month=2)
        assert result.period == "2026-YTD-02"
