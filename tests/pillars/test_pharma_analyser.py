"""
Unit tests voor PharmaAnalyser.

Test KPI-berekeningen, drempelwaardeevaluatie en kpi_status()
op basis van de conftest.py sample_df fixture.
"""

import pandas as pd
import pytest

from csat.core.analysers.pillar_analyser import PillarAnalyser
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


# ------------------------------------------------------------------
# PillarAnalyser — aanvullende paden (regels 33, 55-58)
# ------------------------------------------------------------------


class TestPillarAnalyserExtra:
    """Dekt ValueError voor ongeldige pijler + zorgi-aggregatiepad."""

    def test_ongeldige_pijler_raises(self, sample_df: pd.DataFrame) -> None:
        """Regel 33 — ValueError bij onbekende pillar_key."""
        with pytest.raises(ValueError, match="Onbekende pijler"):
            PillarAnalyser(sample_df, "onbekend")

    def test_zorgi_geen_productfilter(self, sample_df: pd.DataFrame) -> None:
        """Regels 55-58 — zorgi-pijler bevat alle rijen (geen product-filter)."""
        analyser = PillarAnalyser(sample_df, "zorgi")
        assert len(analyser._pillar_df) == 12  # alle rijen in sample

    def test_zorgi_analyse_telt_alle_tickets(self, sample_df: pd.DataFrame) -> None:
        analyser = PillarAnalyser(sample_df, "zorgi")
        result = analyser.analyse("2026-01")
        assert result.total_tickets == 10  # jan 2026: 6 PHARMA + 4 CARE


# ------------------------------------------------------------------
# BaseAnalyser — ongeldige metric in _calc_mom_trend (regel 156)
# ------------------------------------------------------------------


class TestMomTrendInvalidMetric:
    """Dekt de ValueError-branch bij onbekende metric-parameter."""

    def test_ongeldige_metric_raises(self, analyser: PharmaAnalyser) -> None:
        """Regel 156 — ValueError bij metric != avg_score/reactiegraad.
        Beide DataFrames moeten niet-leeg zijn zodat de vroege empty-return niet triggert.
        """
        from csat.utils.date_utils import filter_period

        current = filter_period(analyser._pillar_df, "2026-01")
        previous = filter_period(analyser._pillar_df, "2026-02")  # feb heeft ook data
        with pytest.raises(ValueError, match="Onbekende metric"):
            analyser._calc_mom_trend(current, previous, metric="onbekend")


# ------------------------------------------------------------------
# PharmaAnalyser — AVG_SCORE_MIN branches (regels 81-87, 108)
# ------------------------------------------------------------------


class TestAvgScoreDrempel:
    """Test de avg_score-drempeltak die alleen actief is als AVG_SCORE_MIN niet None is."""

    def test_avg_score_ok_logt_geen_warning(
        self, analyser: PharmaAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regels 84-87 — score OK: avg=3,8 ≥ drempel=3,0."""
        monkeypatch.setattr(pharma_config, "AVG_SCORE_MIN", 3.0)
        result = analyser.analyse("2026-01")
        assert result.avg_score > 3.0  # sanity check

    def test_avg_score_te_laag_logt_warning(
        self, analyser: PharmaAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regels 81-83 — score te laag: avg=3,8 < drempel=4,5."""
        monkeypatch.setattr(pharma_config, "AVG_SCORE_MIN", 4.5)
        result = analyser.analyse("2026-01")
        assert result.avg_score < 4.5  # sanity check

    def test_kpi_status_bevat_avg_score_ok(
        self, analyser: PharmaAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regel 108 — kpi_status() voegt avg_score_ok toe als drempel ingesteld is."""
        monkeypatch.setattr(pharma_config, "AVG_SCORE_MIN", 3.0)
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "avg_score_ok" in status
        assert status["avg_score_ok"] is True

    def test_kpi_status_avg_score_false_als_te_laag(
        self, analyser: PharmaAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(pharma_config, "AVG_SCORE_MIN", 4.5)
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert status["avg_score_ok"] is False
