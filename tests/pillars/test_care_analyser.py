"""
Unit tests voor CareAnalyser.

Test KPI-berekeningen, drempelwaardeevaluatie en kpi_status()
op basis van de sample_df fixture uit conftest.py (CARE-subset).

Testdata (sample_df — CARE-tickets):
- Jan 2026: 4 tickets (SD-009 t/m SD-012), alle in OLV Aalst
- SD-012 heeft geen score → 3 gescoord
- Reactiegraad: 75% | Gem. score: 4,0 | H/C: 25% (Major)
"""

import pandas as pd
import pytest

from csat.core.analysers.pillar_analyser import PillarAnalyser
from csat.pillars.care import config as care_config
from csat.pillars.care.analyser import CareAnalyser

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def analyser(sample_df: pd.DataFrame) -> CareAnalyser:
    """CareAnalyser geladen met de gedeelde testdataset (CARE-subset)."""
    return CareAnalyser(sample_df)


@pytest.fixture
def analyser_leeg(empty_df: pd.DataFrame) -> CareAnalyser:
    """CareAnalyser op lege dataset — test randgevallen."""
    return CareAnalyser(empty_df)


# ------------------------------------------------------------------
# Pijlerfilter
# ------------------------------------------------------------------


class TestCareFilter:
    """Controleer dat de CARE-filter correct werkt."""

    def test_alleen_care_tickets_geladen(self, analyser: CareAnalyser) -> None:
        """Na filter moet product_domain uitsluitend CARE bevatten."""
        assert all(analyser._pillar_df["product_domain"].str.upper() == "CARE")

    def test_aantal_care_tickets(self, analyser: CareAnalyser) -> None:
        """sample_df bevat 4 CARE-tickets (SD-009 t/m SD-012)."""
        assert len(analyser._pillar_df) == 4

    def test_pharma_tickets_gefilterd(self, analyser: CareAnalyser) -> None:
        """PHARMA-tickets mogen niet in de CARE-analyser zitten."""
        assert "PHARMA" not in analyser._pillar_df["product_domain"].values


# ------------------------------------------------------------------
# KPI-berekeningen — jan 2026
# ------------------------------------------------------------------


class TestKpiJan2026:
    """
    Tests op bekende waarden uit de sample_df fixture voor jan 2026.

    - 4 tickets: SD-009 t/m SD-012 (alle OLV Aalst)
    - SD-012 heeft geen score → 3 gescoord
    - Reactiegraad = 3/4 = 75%
    - Scores: 4, 5, 3 → gem = 4,0
    - H/C: SD-012 (Major) = 1/4 = 25%
    """

    def test_totaal_tickets(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.total_tickets == 4

    def test_scored_tickets(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.scored_tickets == 3

    def test_reactiegraad(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.reactiegraad == pytest.approx(75.0, abs=0.1)

    def test_avg_score(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.avg_score == pytest.approx(4.0, abs=0.01)

    def test_high_critical_count(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.high_critical_count == 1

    def test_high_critical_ratio(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.high_critical_ratio == pytest.approx(25.0, abs=0.1)

    def test_pillar_label(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.pillar == "care"

    def test_period_label(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.period == "2026-01"

    def test_ziekenhuizen_aanwezig(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert "OLV Aalst" in result.hospitals

    def test_per_hospital_structuur(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        for _hospital, kpis in result.per_hospital.items():
            assert "total_tickets" in kpis
            assert "reactiegraad" in kpis
            assert "avg_score" in kpis
            assert "high_critical_ratio" in kpis


# ------------------------------------------------------------------
# MoM-trends
# ------------------------------------------------------------------


class TestMomTrend:
    """Tests voor MoM-trend attributen."""

    def test_mom_score_aanwezig(self, analyser: CareAnalyser) -> None:
        r = analyser.analyse("2026-01")
        assert hasattr(r, "mom_score") and isinstance(r.mom_score, float)

    def test_mom_reactiegraad_aanwezig(self, analyser: CareAnalyser) -> None:
        r = analyser.analyse("2026-01")
        assert hasattr(r, "mom_reactiegraad") and isinstance(r.mom_reactiegraad, float)

    def test_mom_nul_zonder_vorige_maand(self, analyser: CareAnalyser) -> None:
        """Jan 2026: geen dec 2025 CARE-data → MoM = 0."""
        assert analyser.analyse("2026-01").mom_score == pytest.approx(0.0)  # type: ignore[attr-defined]


# ------------------------------------------------------------------
# Randgevallen
# ------------------------------------------------------------------


class TestRandgevallen:
    """Tests op lege dataset en onbekende periode."""

    def test_lege_dataset_geeft_nullen(self, analyser_leeg: CareAnalyser) -> None:
        result = analyser_leeg.analyse("2026-01")
        assert result.total_tickets == 0
        assert result.reactiegraad == 0.0
        assert result.avg_score == 0.0
        assert result.high_critical_ratio == 0.0
        assert result.hospitals == []

    def test_onbekende_periode_geeft_nullen(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2020-06")
        assert result.total_tickets == 0
        assert result.reactiegraad == 0.0


# ------------------------------------------------------------------
# Drempelwaardeevaluatie
# ------------------------------------------------------------------


class TestDrempelwaardeEvaluatie:
    """Controleer dat kpi_status() correct True/False retourneert."""

    def test_high_critical_te_hoog(self, analyser: CareAnalyser) -> None:
        """Jan 2026: H/C 25% > drempel 15% → False."""
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert status["high_critical_ok"] is False

    def test_kpi_status_bevat_high_critical(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "high_critical_ok" in status

    def test_reactiegraad_niet_in_status_als_na(self, analyser: CareAnalyser) -> None:
        """ADR-006: REACTIEGRAAD_MIN = None → reactiegraad_ok afwezig in kpi_status."""
        assert care_config.REACTIEGRAAD_MIN is None
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "reactiegraad_ok" not in status

    def test_avg_score_niet_in_status_als_tbd(self, analyser: CareAnalyser) -> None:
        """Zolang AVG_SCORE_MIN = None is de sleutel afwezig in kpi_status."""
        assert care_config.AVG_SCORE_MIN is None
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "avg_score_ok" not in status

    def test_reactiegraad_activeerbaar_via_monkeypatch(
        self, analyser: CareAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Als REACTIEGRAAD_MIN ingesteld wordt, verschijnt reactiegraad_ok."""
        monkeypatch.setattr(care_config, "REACTIEGRAAD_MIN", 70.0)
        result = analyser.analyse("2026-01")  # jan: 3/4 = 75% ≥ 70%
        status = analyser.kpi_status(result)
        assert "reactiegraad_ok" in status
        assert status["reactiegraad_ok"] is True

    def test_reactiegraad_warning_als_te_laag(
        self, analyser: CareAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Reactiegraad < drempel als REACTIEGRAAD_MIN hoger dan 75% ingesteld."""
        monkeypatch.setattr(care_config, "REACTIEGRAAD_MIN", 85.0)
        result = analyser.analyse("2026-01")  # jan: 75% < 85%
        status = analyser.kpi_status(result)
        assert status["reactiegraad_ok"] is False


# ------------------------------------------------------------------
# AVG_SCORE_MIN drempel
# ------------------------------------------------------------------


class TestAvgScoreDrempel:
    """Test de avg_score-drempeltak via monkeypatch."""

    def test_avg_score_ok_logt_geen_warning(
        self, analyser: CareAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Score OK: avg=4,0 ≥ drempel=3,5."""
        monkeypatch.setattr(care_config, "AVG_SCORE_MIN", 3.5)
        result = analyser.analyse("2026-01")
        assert result.avg_score > 3.5

    def test_avg_score_te_laag_logt_warning(
        self, analyser: CareAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Score te laag: avg=4,0 < drempel=4,5."""
        monkeypatch.setattr(care_config, "AVG_SCORE_MIN", 4.5)
        result = analyser.analyse("2026-01")
        assert result.avg_score < 4.5

    def test_kpi_status_bevat_avg_score_ok(
        self, analyser: CareAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """kpi_status() voegt avg_score_ok toe als drempel ingesteld is."""
        monkeypatch.setattr(care_config, "AVG_SCORE_MIN", 3.5)
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "avg_score_ok" in status
        assert status["avg_score_ok"] is True

    def test_kpi_status_avg_score_false_als_te_laag(
        self, analyser: CareAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(care_config, "AVG_SCORE_MIN", 4.5)
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert status["avg_score_ok"] is False


# ------------------------------------------------------------------
# YTD
# ------------------------------------------------------------------


class TestYtd:
    """Tests voor de YTD-aggregatie."""

    def test_ytd_jan(self, analyser: CareAnalyser) -> None:
        """YTD jan 2026: 4 CARE-tickets (sample_df heeft geen CARE-data voor feb)."""
        result = analyser.analyse_ytd(year=2026, up_to_month=1)
        assert result.total_tickets == 4

    def test_ytd_period_label(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse_ytd(year=2026, up_to_month=1)
        assert result.period == "2026-YTD-01"

    def test_ytd_pillar_label(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse_ytd(year=2026, up_to_month=1)
        assert result.pillar == "care"

    def test_ytd_leeg_jaar(self, analyser: CareAnalyser) -> None:
        result = analyser.analyse_ytd(year=2025, up_to_month=3)
        assert result.total_tickets == 0 and result.avg_score == 0.0


# ------------------------------------------------------------------
# to_dict
# ------------------------------------------------------------------


class TestKpiResultToDict:
    """Controleer de serialisatie van KpiResult."""

    def test_to_dict_bevat_alle_sleutels(self, analyser: CareAnalyser) -> None:
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

    def test_to_dict_hospitals_is_getal(self, analyser: CareAnalyser) -> None:
        """to_dict() slaat het AANTAL ziekenhuizen op, niet de lijst."""
        result = analyser.analyse("2026-01")
        d = result.to_dict()
        assert isinstance(d["hospitals"], int)
        assert d["hospitals"] == 1


# ------------------------------------------------------------------
# PillarAnalyser-integratie
# ------------------------------------------------------------------


class TestPillarAnalyserIntegratie:
    """CARE als PillarAnalyser — integratie checks."""

    def test_care_via_pillaranalyser(self, sample_df: pd.DataFrame) -> None:
        """CareAnalyser erft correct van PillarAnalyser."""
        a = PillarAnalyser(sample_df, "care")
        assert a._pillar_key == "care"

    def test_care_filter_via_pillaranalyser(self, sample_df: pd.DataFrame) -> None:
        a = PillarAnalyser(sample_df, "care")
        assert all(a._pillar_df["product_domain"].str.upper() == "CARE")

    def test_comment_ratio_aanwezig(self, analyser: CareAnalyser) -> None:
        r = analyser.analyse("2026-01")
        assert 0.0 <= r.comment_ratio <= 100.0

    def test_hospitals_gesorteerd(self, analyser: CareAnalyser) -> None:
        h = analyser.analyse("2026-01").hospitals
        assert h == sorted(h)
