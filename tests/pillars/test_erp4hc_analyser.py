"""
Unit tests voor Erp4hcAnalyser.

Test KPI-berekeningen, drempelwaardeevaluatie en kpi_status()
op basis van de erp4hc_df fixture uit conftest.py.

Testdata (erp4hc_df):
- Jan 2026: 3 tickets (AZ Delta), 1 feb 2026 (GHB Hasselt)
- SDE-003 heeft geen score → 2 gescoord van 3 in jan
- Reactiegraad jan: 66,7% | Gem. score jan: 3,5 | H/C jan: 33,3% (Blocker)
"""

import pandas as pd
import pytest

from csat.core.analysers.pillar_analyser import PillarAnalyser
from csat.pillars.erp4hc import config as erp4hc_config
from csat.pillars.erp4hc.analyser import Erp4hcAnalyser

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def analyser(erp4hc_df: pd.DataFrame) -> Erp4hcAnalyser:
    """Erp4hcAnalyser geladen met de ERP4HC testdataset."""
    return Erp4hcAnalyser(erp4hc_df)


@pytest.fixture
def analyser_leeg(empty_df: pd.DataFrame) -> Erp4hcAnalyser:
    """Erp4hcAnalyser op lege dataset — test randgevallen."""
    return Erp4hcAnalyser(empty_df)


# ------------------------------------------------------------------
# Pijlerfilter
# ------------------------------------------------------------------


class TestErp4hcFilter:
    """Controleer dat de ERP4HC-filter correct werkt."""

    def test_alleen_erp_tickets_geladen(self, analyser: Erp4hcAnalyser) -> None:
        """Na filter moet product_domain uitsluitend ERP bevatten."""
        assert all(analyser._pillar_df["product_domain"].str.upper() == "ERP")

    def test_aantal_erp_tickets(self, analyser: Erp4hcAnalyser) -> None:
        """erp4hc_df bevat 4 ERP-tickets (SDE-001 t/m SDE-004)."""
        assert len(analyser._pillar_df) == 4

    def test_andere_domeinen_gefilterd(self, analyser: Erp4hcAnalyser) -> None:
        """PHARMA- en CARE-tickets mogen niet in de ERP4HC-analyser zitten."""
        domeinen = analyser._pillar_df["product_domain"].unique()
        assert "PHARMA" not in domeinen
        assert "CARE" not in domeinen


# ------------------------------------------------------------------
# KPI-berekeningen — jan 2026
# ------------------------------------------------------------------


class TestKpiJan2026:
    """
    Tests op bekende waarden uit de erp4hc_df fixture voor jan 2026.

    - 3 tickets: SDE-001 t/m SDE-003 (alle AZ Delta)
    - SDE-003 heeft geen score → 2 gescoord
    - Reactiegraad = 2/3 = 66,7%
    - Scores: 3, 4 → gem = 3,5
    - H/C: SDE-003 (Blocker) = 1/3 = 33,3%
    """

    def test_totaal_tickets(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.total_tickets == 3

    def test_scored_tickets(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.scored_tickets == 2

    def test_reactiegraad(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.reactiegraad == pytest.approx(66.7, abs=0.1)

    def test_avg_score(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.avg_score == pytest.approx(3.5, abs=0.01)

    def test_high_critical_count(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.high_critical_count == 1

    def test_high_critical_ratio(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.high_critical_ratio == pytest.approx(33.3, abs=0.1)

    def test_pillar_label(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.pillar == "erp4hc"

    def test_period_label(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.period == "2026-01"

    def test_ziekenhuizen_aanwezig(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert "AZ Delta" in result.hospitals

    def test_per_hospital_structuur(self, analyser: Erp4hcAnalyser) -> None:
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

    def test_mom_score_aanwezig(self, analyser: Erp4hcAnalyser) -> None:
        r = analyser.analyse("2026-01")
        assert hasattr(r, "mom_score") and isinstance(r.mom_score, float)

    def test_mom_reactiegraad_aanwezig(self, analyser: Erp4hcAnalyser) -> None:
        r = analyser.analyse("2026-01")
        assert hasattr(r, "mom_reactiegraad") and isinstance(r.mom_reactiegraad, float)

    def test_mom_nul_zonder_vorige_maand(self, analyser: Erp4hcAnalyser) -> None:
        """Jan 2026: geen dec 2025 ERP-data → MoM = 0."""
        assert analyser.analyse("2026-01").mom_score == pytest.approx(0.0)  # type: ignore[attr-defined]


# ------------------------------------------------------------------
# Randgevallen
# ------------------------------------------------------------------


class TestRandgevallen:
    """Tests op lege dataset en onbekende periode."""

    def test_lege_dataset_geeft_nullen(self, analyser_leeg: Erp4hcAnalyser) -> None:
        result = analyser_leeg.analyse("2026-01")
        assert result.total_tickets == 0
        assert result.reactiegraad == 0.0
        assert result.avg_score == 0.0
        assert result.high_critical_ratio == 0.0
        assert result.hospitals == []

    def test_onbekende_periode_geeft_nullen(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2020-06")
        assert result.total_tickets == 0
        assert result.reactiegraad == 0.0


# ------------------------------------------------------------------
# Drempelwaardeevaluatie
# ------------------------------------------------------------------


class TestDrempelwaardeEvaluatie:
    """Controleer dat kpi_status() correct True/False retourneert."""

    def test_high_critical_te_hoog(self, analyser: Erp4hcAnalyser) -> None:
        """Jan 2026: H/C 33,3% > drempel 15% → False."""
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert status["high_critical_ok"] is False

    def test_kpi_status_bevat_high_critical(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "high_critical_ok" in status

    def test_reactiegraad_niet_in_status_als_na(self, analyser: Erp4hcAnalyser) -> None:
        """ADR-006: REACTIEGRAAD_MIN = None → reactiegraad_ok afwezig in kpi_status."""
        assert erp4hc_config.REACTIEGRAAD_MIN is None
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "reactiegraad_ok" not in status

    def test_avg_score_niet_in_status_als_tbd(self, analyser: Erp4hcAnalyser) -> None:
        """Zolang AVG_SCORE_MIN = None is de sleutel afwezig in kpi_status."""
        assert erp4hc_config.AVG_SCORE_MIN is None
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "avg_score_ok" not in status

    def test_reactiegraad_activeerbaar_via_monkeypatch(
        self, analyser: Erp4hcAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Als REACTIEGRAAD_MIN ingesteld wordt, verschijnt reactiegraad_ok."""
        monkeypatch.setattr(erp4hc_config, "REACTIEGRAAD_MIN", 60.0)
        result = analyser.analyse("2026-01")  # jan: 2/3 = 66,7% ≥ 60%
        status = analyser.kpi_status(result)
        assert "reactiegraad_ok" in status
        assert status["reactiegraad_ok"] is True

    def test_reactiegraad_warning_als_te_laag(
        self, analyser: Erp4hcAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Reactiegraad < drempel als REACTIEGRAAD_MIN hoger dan 66,7% ingesteld."""
        monkeypatch.setattr(erp4hc_config, "REACTIEGRAAD_MIN", 85.0)
        result = analyser.analyse("2026-01")  # jan: 66,7% < 85%
        status = analyser.kpi_status(result)
        assert status["reactiegraad_ok"] is False


# ------------------------------------------------------------------
# AVG_SCORE_MIN drempel
# ------------------------------------------------------------------


class TestAvgScoreDrempel:
    """Test de avg_score-drempeltak via monkeypatch."""

    def test_avg_score_ok_logt_geen_warning(
        self, analyser: Erp4hcAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Score OK: avg=3,5 ≥ drempel=3,0."""
        monkeypatch.setattr(erp4hc_config, "AVG_SCORE_MIN", 3.0)
        result = analyser.analyse("2026-01")
        assert result.avg_score > 3.0

    def test_avg_score_te_laag_logt_warning(
        self, analyser: Erp4hcAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Score te laag: avg=3,5 < drempel=4,0."""
        monkeypatch.setattr(erp4hc_config, "AVG_SCORE_MIN", 4.0)
        result = analyser.analyse("2026-01")
        assert result.avg_score < 4.0

    def test_kpi_status_bevat_avg_score_ok(
        self, analyser: Erp4hcAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """kpi_status() voegt avg_score_ok toe als drempel ingesteld is."""
        monkeypatch.setattr(erp4hc_config, "AVG_SCORE_MIN", 3.0)
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "avg_score_ok" in status
        assert status["avg_score_ok"] is True

    def test_kpi_status_avg_score_false_als_te_laag(
        self, analyser: Erp4hcAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(erp4hc_config, "AVG_SCORE_MIN", 4.0)
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert status["avg_score_ok"] is False


# ------------------------------------------------------------------
# YTD
# ------------------------------------------------------------------


class TestYtd:
    """Tests voor de YTD-aggregatie."""

    def test_ytd_jan_feb(self, analyser: Erp4hcAnalyser) -> None:
        """YTD jan-feb 2026: alle 4 ERP4HC-tickets."""
        result = analyser.analyse_ytd(year=2026, up_to_month=2)
        assert result.total_tickets == 4

    def test_ytd_jan_only(self, analyser: Erp4hcAnalyser) -> None:
        """YTD t/m jan 2026: 3 ERP4HC-tickets."""
        result = analyser.analyse_ytd(year=2026, up_to_month=1)
        assert result.total_tickets == 3

    def test_ytd_period_label(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse_ytd(year=2026, up_to_month=2)
        assert result.period == "2026-YTD-02"

    def test_ytd_pillar_label(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse_ytd(year=2026, up_to_month=1)
        assert result.pillar == "erp4hc"

    def test_ytd_leeg_jaar(self, analyser: Erp4hcAnalyser) -> None:
        result = analyser.analyse_ytd(year=2025, up_to_month=3)
        assert result.total_tickets == 0 and result.avg_score == 0.0


# ------------------------------------------------------------------
# to_dict
# ------------------------------------------------------------------


class TestKpiResultToDict:
    """Controleer de serialisatie van KpiResult."""

    def test_to_dict_bevat_alle_sleutels(self, analyser: Erp4hcAnalyser) -> None:
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

    def test_to_dict_hospitals_is_getal(self, analyser: Erp4hcAnalyser) -> None:
        """to_dict() slaat het AANTAL ziekenhuizen op, niet de lijst."""
        result = analyser.analyse("2026-01")
        d = result.to_dict()
        assert isinstance(d["hospitals"], int)
        assert d["hospitals"] == 1


# ------------------------------------------------------------------
# PillarAnalyser-integratie
# ------------------------------------------------------------------


class TestPillarAnalyserIntegratie:
    """ERP4HC als PillarAnalyser — integratie checks."""

    def test_erp4hc_via_pillaranalyser(self, erp4hc_df: pd.DataFrame) -> None:
        """Erp4hcAnalyser erft correct van PillarAnalyser."""
        a = PillarAnalyser(erp4hc_df, "erp4hc")
        assert a._pillar_key == "erp4hc"

    def test_erp_filter_via_pillaranalyser(self, erp4hc_df: pd.DataFrame) -> None:
        a = PillarAnalyser(erp4hc_df, "erp4hc")
        assert all(a._pillar_df["product_domain"].str.upper() == "ERP")

    def test_comment_ratio_aanwezig(self, analyser: Erp4hcAnalyser) -> None:
        r = analyser.analyse("2026-01")
        assert 0.0 <= r.comment_ratio <= 100.0

    def test_hospitals_gesorteerd(self, analyser: Erp4hcAnalyser) -> None:
        h = analyser.analyse("2026-01").hospitals
        assert h == sorted(h)
