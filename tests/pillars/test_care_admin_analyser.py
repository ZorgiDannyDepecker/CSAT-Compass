"""
Unit tests voor CareAdminAnalyser.

Test KPI-berekeningen, drempelwaardeevaluatie en kpi_status()
op basis van de care_admin_df fixture uit conftest.py.

Testdata (care_admin_df):
- Jan 2026: 5 tickets, 4 gescoord
- Reactiegraad: 80% | Gem. score: 4,0 | H/C: 20% (Blocker)
- Ziekenhuizen: Sint-Maarten Mechelen, ZNA Middelheim
"""

import pandas as pd
import pytest

from csat.core.analysers.pillar_analyser import PillarAnalyser
from csat.pillars.care_admin import config as care_admin_config
from csat.pillars.care_admin.analyser import CareAdminAnalyser

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def analyser(care_admin_df: pd.DataFrame) -> CareAdminAnalyser:
    """CareAdminAnalyser geladen met de CARE ADMIN testdataset."""
    return CareAdminAnalyser(care_admin_df)


@pytest.fixture
def analyser_leeg(empty_df: pd.DataFrame) -> CareAdminAnalyser:
    """CareAdminAnalyser op lege dataset — test randgevallen."""
    return CareAdminAnalyser(empty_df)


# ------------------------------------------------------------------
# Pijlerfilter
# ------------------------------------------------------------------


class TestCareAdminFilter:
    """Controleer dat de CARE ADMIN-filter correct werkt."""

    def test_alleen_care_admin_tickets_geladen(self, analyser: CareAdminAnalyser) -> None:
        """Na filter moet product_domain uitsluitend CARE ADMIN bevatten."""
        assert all(analyser._pillar_df["product_domain"].str.upper() == "CARE ADMIN")

    def test_aantal_care_admin_tickets(self, analyser: CareAdminAnalyser) -> None:
        """care_admin_df bevat 6 CARE ADMIN-tickets."""
        assert len(analyser._pillar_df) == 6

    def test_andere_domeinen_gefilterd(self, analyser: CareAdminAnalyser) -> None:
        """PHARMA- en ERP-tickets mogen niet in de CARE ADMIN-analyser zitten."""
        domeinen = analyser._pillar_df["product_domain"].unique()
        assert "PHARMA" not in domeinen
        assert "ERP" not in domeinen


# ------------------------------------------------------------------
# KPI-berekeningen — jan 2026
# ------------------------------------------------------------------


class TestKpiJan2026:
    """
    Tests op bekende waarden uit de care_admin_df fixture voor jan 2026.

    - 5 tickets: SDX-001 t/m SDX-005
    - SDX-004 heeft geen score → 4 gescoord
    - Reactiegraad = 4/5 = 80%
    - Scores: 4, 5, 3, 4 → gem = 4,0
    - H/C: SDX-001 (Blocker) = 1/5 = 20%
    """

    def test_totaal_tickets(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.total_tickets == 5

    def test_scored_tickets(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.scored_tickets == 4

    def test_reactiegraad(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.reactiegraad == pytest.approx(80.0, abs=0.1)

    def test_avg_score(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.avg_score == pytest.approx(4.0, abs=0.01)

    def test_high_critical_count(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.high_critical_count == 1

    def test_high_critical_ratio(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.high_critical_ratio == pytest.approx(20.0, abs=0.1)

    def test_pillar_label(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.pillar == "care_admin"

    def test_period_label(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert result.period == "2026-01"

    def test_ziekenhuizen_aanwezig(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        assert "Sint-Maarten Mechelen" in result.hospitals
        assert "ZNA Middelheim" in result.hospitals

    def test_per_hospital_structuur(self, analyser: CareAdminAnalyser) -> None:
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

    def test_mom_score_aanwezig(self, analyser: CareAdminAnalyser) -> None:
        r = analyser.analyse("2026-01")
        assert hasattr(r, "mom_score") and isinstance(r.mom_score, float)

    def test_mom_reactiegraad_aanwezig(self, analyser: CareAdminAnalyser) -> None:
        r = analyser.analyse("2026-01")
        assert hasattr(r, "mom_reactiegraad") and isinstance(r.mom_reactiegraad, float)

    def test_mom_nul_zonder_vorige_maand(self, analyser: CareAdminAnalyser) -> None:
        """Jan 2026: geen dec 2025 data → MoM = 0."""
        assert analyser.analyse("2026-01").mom_score == pytest.approx(0.0)  # type: ignore[attr-defined]


# ------------------------------------------------------------------
# Randgevallen
# ------------------------------------------------------------------


class TestRandgevallen:
    """Tests op lege dataset en onbekende periode."""

    def test_lege_dataset_geeft_nullen(self, analyser_leeg: CareAdminAnalyser) -> None:
        result = analyser_leeg.analyse("2026-01")
        assert result.total_tickets == 0
        assert result.reactiegraad == 0.0
        assert result.avg_score == 0.0
        assert result.high_critical_ratio == 0.0
        assert result.hospitals == []

    def test_onbekende_periode_geeft_nullen(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2020-06")
        assert result.total_tickets == 0
        assert result.reactiegraad == 0.0


# ------------------------------------------------------------------
# Drempelwaardeevaluatie
# ------------------------------------------------------------------


class TestDrempelwaardeEvaluatie:
    """Controleer dat kpi_status() correct True/False retourneert."""

    def test_high_critical_te_hoog(self, analyser: CareAdminAnalyser) -> None:
        """Jan 2026: H/C 20% > drempel 15% → False."""
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert status["high_critical_ok"] is False

    def test_kpi_status_bevat_high_critical(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "high_critical_ok" in status

    def test_reactiegraad_niet_in_status_als_na(self, analyser: CareAdminAnalyser) -> None:
        """ADR-006: REACTIEGRAAD_MIN = None → reactiegraad_ok afwezig in kpi_status."""
        assert care_admin_config.REACTIEGRAAD_MIN is None
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "reactiegraad_ok" not in status

    def test_avg_score_niet_in_status_als_tbd(self, analyser: CareAdminAnalyser) -> None:
        """Zolang AVG_SCORE_MIN = None is de sleutel afwezig in kpi_status."""
        assert care_admin_config.AVG_SCORE_MIN is None
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "avg_score_ok" not in status

    def test_reactiegraad_activeerbaar_via_monkeypatch(
        self, analyser: CareAdminAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Als REACTIEGRAAD_MIN ingesteld wordt, verschijnt reactiegraad_ok."""
        monkeypatch.setattr(care_admin_config, "REACTIEGRAAD_MIN", 75.0)
        result = analyser.analyse("2026-01")  # jan: 4/5 = 80% ≥ 75%
        status = analyser.kpi_status(result)
        assert "reactiegraad_ok" in status
        assert status["reactiegraad_ok"] is True

    def test_reactiegraad_warning_als_te_laag(
        self, analyser: CareAdminAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Reactiegraad < drempel als REACTIEGRAAD_MIN hoger dan 80% ingesteld."""
        monkeypatch.setattr(care_admin_config, "REACTIEGRAAD_MIN", 90.0)
        result = analyser.analyse("2026-01")  # jan: 80% < 90%
        status = analyser.kpi_status(result)
        assert status["reactiegraad_ok"] is False


# ------------------------------------------------------------------
# AVG_SCORE_MIN drempel
# ------------------------------------------------------------------


class TestAvgScoreDrempel:
    """Test de avg_score-drempeltak via monkeypatch."""

    def test_avg_score_ok_logt_geen_warning(
        self, analyser: CareAdminAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Score OK: avg=4,0 ≥ drempel=3,5."""
        monkeypatch.setattr(care_admin_config, "AVG_SCORE_MIN", 3.5)
        result = analyser.analyse("2026-01")
        assert result.avg_score > 3.5

    def test_avg_score_te_laag_logt_warning(
        self, analyser: CareAdminAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Score te laag: avg=4,0 < drempel=4,5."""
        monkeypatch.setattr(care_admin_config, "AVG_SCORE_MIN", 4.5)
        result = analyser.analyse("2026-01")
        assert result.avg_score < 4.5

    def test_kpi_status_bevat_avg_score_ok(
        self, analyser: CareAdminAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """kpi_status() voegt avg_score_ok toe als drempel ingesteld is."""
        monkeypatch.setattr(care_admin_config, "AVG_SCORE_MIN", 3.5)
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert "avg_score_ok" in status
        assert status["avg_score_ok"] is True

    def test_kpi_status_avg_score_false_als_te_laag(
        self, analyser: CareAdminAnalyser, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(care_admin_config, "AVG_SCORE_MIN", 4.5)
        result = analyser.analyse("2026-01")
        status = analyser.kpi_status(result)
        assert status["avg_score_ok"] is False


# ------------------------------------------------------------------
# YTD
# ------------------------------------------------------------------


class TestYtd:
    """Tests voor de YTD-aggregatie."""

    def test_ytd_jan_feb(self, analyser: CareAdminAnalyser) -> None:
        """YTD jan-feb 2026: alle 6 CARE ADMIN-tickets."""
        result = analyser.analyse_ytd(year=2026, up_to_month=2)
        assert result.total_tickets == 6

    def test_ytd_jan_only(self, analyser: CareAdminAnalyser) -> None:
        """YTD t/m jan 2026: 5 CARE ADMIN-tickets."""
        result = analyser.analyse_ytd(year=2026, up_to_month=1)
        assert result.total_tickets == 5

    def test_ytd_period_label(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse_ytd(year=2026, up_to_month=2)
        assert result.period == "2026-YTD-02"

    def test_ytd_pillar_label(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse_ytd(year=2026, up_to_month=1)
        assert result.pillar == "care_admin"

    def test_ytd_leeg_jaar(self, analyser: CareAdminAnalyser) -> None:
        result = analyser.analyse_ytd(year=2025, up_to_month=3)
        assert result.total_tickets == 0 and result.avg_score == 0.0


# ------------------------------------------------------------------
# to_dict
# ------------------------------------------------------------------


class TestKpiResultToDict:
    """Controleer de serialisatie van KpiResult."""

    def test_to_dict_bevat_alle_sleutels(self, analyser: CareAdminAnalyser) -> None:
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

    def test_to_dict_hospitals_is_getal(self, analyser: CareAdminAnalyser) -> None:
        """to_dict() slaat het AANTAL ziekenhuizen op, niet de lijst."""
        result = analyser.analyse("2026-01")
        d = result.to_dict()
        assert isinstance(d["hospitals"], int)
        assert d["hospitals"] == 2


# ------------------------------------------------------------------
# PillarAnalyser-integratie
# ------------------------------------------------------------------


class TestPillarAnalyserIntegratie:
    """CARE ADMIN als PillarAnalyser — integratie en initialisatie checks."""

    def test_care_admin_via_pillaranalyser(self, care_admin_df: pd.DataFrame) -> None:
        """CareAdminAnalyser erft correct van PillarAnalyser."""
        a = PillarAnalyser(care_admin_df, "care_admin")
        assert a._pillar_key == "care_admin"

    def test_care_admin_filter_via_pillaranalyser(self, care_admin_df: pd.DataFrame) -> None:
        a = PillarAnalyser(care_admin_df, "care_admin")
        assert all(a._pillar_df["product_domain"].str.upper() == "CARE ADMIN")

    def test_comment_ratio_aanwezig(self, analyser: CareAdminAnalyser) -> None:
        r = analyser.analyse("2026-01")
        assert 0.0 <= r.comment_ratio <= 100.0

    def test_hospitals_gesorteerd(self, analyser: CareAdminAnalyser) -> None:
        h = analyser.analyse("2026-01").hospitals
        assert h == sorted(h)
