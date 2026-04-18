"""Unit tests voor PillarAnalyser — initialisatie, analyse(), analyse_ytd(), comment_ratio."""

import pandas as pd
import pytest

from csat.config.pillars import PILLAR_REGISTRY
from csat.core.analysers.base_analyser import KpiResult
from csat.core.analysers.pillar_analyser import PillarAnalyser


@pytest.fixture
def analyser_pharma(sample_df):
    return PillarAnalyser(sample_df, pillar_key="pharma")


@pytest.fixture
def analyser_care(sample_df):
    return PillarAnalyser(sample_df, pillar_key="care")


# ---------------------------------------------------------------------------
# Init & validatie
# ---------------------------------------------------------------------------
class TestPillarAnalyserInit:
    def test_geldige_pharma(self, sample_df):
        assert PillarAnalyser(sample_df, "pharma")._pillar_key == "pharma"

    def test_geldige_care(self, sample_df):
        assert PillarAnalyser(sample_df, "care")._pillar_key == "care"

    def test_alle_pijlers(self, sample_df):
        for key in PILLAR_REGISTRY:
            assert PillarAnalyser(sample_df, key)._pillar_key == key

    def test_ongeldig_gooit_valueerror(self, sample_df):
        with pytest.raises(ValueError, match="Onbekende pijler"):
            PillarAnalyser(sample_df, "niet_bestaand")

    def test_filter_pharma(self, analyser_pharma):
        assert (analyser_pharma._pillar_df["product_domain"] == "PHARMA").all()

    def test_filter_care(self, analyser_care):
        assert (analyser_care._pillar_df["product_domain"] == "CARE").all()

    def test_startdatum_filter(self, sample_df):
        oud = pd.DataFrame(
            [
                {
                    "key": "OLD-001",
                    "issue_type": "Bug",
                    "priority": "Minor",
                    "summary": "Oud",
                    "score": 3.0,
                    "comment": "",
                    "satisfaction_date": pd.Timestamp("2024-06-20"),
                    "created": pd.Timestamp("2024-06-01"),
                    "hospital": "AZ Oud",
                    "product": "Apotheek",
                    "product_domain": "PHARMA",
                    "project_key": "SD30",
                }
            ]
        )
        combined = pd.concat([sample_df, oud], ignore_index=True)
        a = PillarAnalyser(combined, "pharma")
        assert (pd.to_datetime(a._pillar_df["created"]) >= pd.Timestamp("2025-01-01")).all()

    def test_origineel_ongewijzigd(self, sample_df):
        n = len(sample_df)
        PillarAnalyser(sample_df, "pharma")
        assert len(sample_df) == n


# ---------------------------------------------------------------------------
# analyse()
# ---------------------------------------------------------------------------
class TestPillarAnalyserAnalyse:
    def test_retourtype(self, analyser_pharma):
        assert isinstance(analyser_pharma.analyse("2026-01"), KpiResult)

    def test_period_label(self, analyser_pharma):
        assert analyser_pharma.analyse("2026-01").period == "2026-01"

    def test_pillar_label(self, analyser_pharma):
        assert analyser_pharma.analyse("2026-01").pillar == "pharma"

    def test_total_pharma_jan(self, analyser_pharma):
        assert analyser_pharma.analyse("2026-01").total_tickets == 6

    def test_scored_pharma_jan(self, analyser_pharma):
        assert analyser_pharma.analyse("2026-01").scored_tickets == 5

    def test_reactiegraad_pharma_jan(self, analyser_pharma):
        assert analyser_pharma.analyse("2026-01").reactiegraad == pytest.approx(83.3, abs=0.1)

    def test_avg_score_pharma_jan(self, analyser_pharma):
        # (4+3+5+2+5)/5 = 3.80
        assert analyser_pharma.analyse("2026-01").avg_score == pytest.approx(3.80)

    def test_hc_count_pharma_jan(self, analyser_pharma):
        # Blocker + Critical = 2
        assert analyser_pharma.analyse("2026-01").high_critical_count == 2

    def test_hc_ratio_pharma_jan(self, analyser_pharma):
        assert analyser_pharma.analyse("2026-01").high_critical_ratio == pytest.approx(
            33.3, abs=0.1
        )

    def test_comment_ratio_geldig_bereik(self, analyser_pharma):
        r = analyser_pharma.analyse("2026-01").comment_ratio
        assert 0.0 <= r <= 100.0

    def test_hospitals_gesorteerd(self, analyser_pharma):
        h = analyser_pharma.analyse("2026-01").hospitals
        assert h == sorted(h)

    def test_per_hospital_sleutels(self, analyser_pharma):
        assert set(analyser_pharma.analyse("2026-01").per_hospital.keys()) == {
            "AZ Groeninge",
            "UZ Brussel",
        }

    def test_mom_score_aanwezig(self, analyser_pharma):
        r = analyser_pharma.analyse("2026-01")
        assert hasattr(r, "mom_score") and isinstance(r.mom_score, float)

    def test_mom_reactiegraad_aanwezig(self, analyser_pharma):
        r = analyser_pharma.analyse("2026-01")
        assert hasattr(r, "mom_reactiegraad") and isinstance(r.mom_reactiegraad, float)

    def test_mom_nul_zonder_vorige_maand(self, analyser_pharma):
        assert analyser_pharma.analyse("2026-01").mom_score == pytest.approx(0.0)

    def test_mom_negatief_bij_dalende_score(self, sample_df):
        a = PillarAnalyser(sample_df, "pharma")
        # feb avg (3.5) < jan avg (3.8) => mom_score negatief
        assert a.analyse("2026-02").mom_score < 0

    def test_lege_periode_nulwaarden(self, analyser_pharma):
        r = analyser_pharma.analyse("2025-06")
        assert r.total_tickets == 0 and r.avg_score == 0.0 and r.hospitals == []

    def test_care_jan_totaal(self, analyser_care):
        assert analyser_care.analyse("2026-01").total_tickets == 4

    def test_care_jan_avg(self, analyser_care):
        # (4+5+3)/3 = 4.0
        assert analyser_care.analyse("2026-01").avg_score == pytest.approx(4.0)

    def test_care_jan_hospital(self, analyser_care):
        assert analyser_care.analyse("2026-01").hospitals == ["OLV Aalst"]


# ---------------------------------------------------------------------------
# analyse_ytd()
# ---------------------------------------------------------------------------
class TestPillarAnalyserAnalyseYtd:
    def test_retourtype(self, analyser_pharma):
        assert isinstance(analyser_pharma.analyse_ytd(2026, 2), KpiResult)

    def test_period_label(self, analyser_pharma):
        assert analyser_pharma.analyse_ytd(2026, 2).period == "2026-YTD-02"

    def test_pillar_label(self, analyser_pharma):
        assert analyser_pharma.analyse_ytd(2026, 2).pillar == "pharma"

    def test_jan_feb_totaal(self, analyser_pharma):
        assert analyser_pharma.analyse_ytd(2026, 2).total_tickets == 8

    def test_jan_feb_avg(self, analyser_pharma):
        # (4+3+5+2+5+4+3)/7 = 3.71
        assert analyser_pharma.analyse_ytd(2026, 2).avg_score == pytest.approx(3.71, abs=0.01)

    def test_jan_only(self, analyser_pharma):
        assert analyser_pharma.analyse_ytd(2026, 1).total_tickets == 6

    def test_leeg_jaar(self, analyser_pharma):
        r = analyser_pharma.analyse_ytd(2025, 3)
        assert r.total_tickets == 0 and r.avg_score == 0.0

    def test_comment_ratio_aanwezig(self, analyser_pharma):
        r = analyser_pharma.analyse_ytd(2026, 2)
        assert 0.0 <= r.comment_ratio <= 100.0

    def test_hospitals_gesorteerd(self, analyser_pharma):
        h = analyser_pharma.analyse_ytd(2026, 2).hospitals
        assert h == sorted(h)

    def test_geen_mom_attributen(self, analyser_pharma):
        r = analyser_pharma.analyse_ytd(2026, 2)
        assert not hasattr(r, "mom_score")
        assert not hasattr(r, "mom_reactiegraad")


# ---------------------------------------------------------------------------
# comment_ratio specifiek
# ---------------------------------------------------------------------------
class TestCommentRatioPillar:
    def test_nul_zonder_comments(self, sample_df):
        df = sample_df.copy()
        df["comment"] = ""
        r = PillarAnalyser(df, "pharma").analyse("2026-01")
        assert r.comment_ratio == 0.0

    def test_honderd_met_comments(self, sample_df):
        df = sample_df.copy()
        df["comment"] = "opmerking"
        r = PillarAnalyser(df, "pharma").analyse("2026-01")
        assert r.comment_ratio == pytest.approx(100.0)

    def test_aanwezig_in_ytd(self, analyser_pharma):
        r = analyser_pharma.analyse_ytd(2026, 1)
        assert isinstance(r.comment_ratio, float)
