"""
Unit tests voor BaseAnalyser en KpiResult.
BaseAnalyser is abstract — tests via minimale ConcreteAnalyser subklasse.
Gedekte methoden:
    _calc_reactiegraad, _calc_avg_score, _calc_high_critical,
    _calc_comment_ratio, _calc_mom_trend, _group_by_hospital,
    KpiResult.to_dict(), abstracte eigenschappen
"""

import pandas as pd
import pytest

from csat.core.analysers.base_analyser import BaseAnalyser, KpiResult


class ConcreteAnalyser(BaseAnalyser):
    def analyse(self, period: str) -> KpiResult:
        return KpiResult(period=period, pillar="test")


@pytest.fixture
def df5():
    return pd.DataFrame(
        [
            {"score": 4.0, "priority": "Minor", "comment": "goed", "hospital": "AZ Test"},
            {"score": 5.0, "priority": "Blocker", "comment": "uitstekend", "hospital": "AZ Test"},
            {"score": 2.0, "priority": "Critical", "comment": "", "hospital": "UZ Brussel"},
            {"score": 3.0, "priority": "Trivial", "comment": "matig", "hospital": "UZ Brussel"},
            {"score": None, "priority": "Minor", "comment": None, "hospital": "OLV Aalst"},
        ]
    )


@pytest.fixture
def df_leeg():
    return pd.DataFrame(columns=["score", "priority", "comment", "hospital"]).astype(
        {"score": float}
    )


@pytest.fixture
def analyser(df5):
    return ConcreteAnalyser(df5)


# ---------------------------------------------------------------------------
# KpiResult
# ---------------------------------------------------------------------------
class TestKpiResultDataclass:
    def test_defaults(self):
        r = KpiResult(period="2026-01", pillar="pharma")
        assert r.total_tickets == 0
        assert r.hospitals == []
        assert r.per_hospital == {}

    def test_to_dict_keys(self):
        d = KpiResult(period="2026-01", pillar="pharma").to_dict()
        assert {
            "period",
            "pillar",
            "total_tickets",
            "scored_tickets",
            "reactiegraad",
            "avg_score",
            "high_critical_count",
            "high_critical_ratio",
            "comment_ratio",
            "hospitals",
        }.issubset(d)

    def test_to_dict_hospitals_is_count(self):
        r = KpiResult(period="2026-01", pillar="pharma", hospitals=["A", "B"])
        assert r.to_dict()["hospitals"] == 2

    def test_to_dict_no_per_hospital(self):
        r = KpiResult(period="2026-01", pillar="pharma", per_hospital={"X": {}})
        assert "per_hospital" not in r.to_dict()

    def test_to_dict_values(self):
        r = KpiResult(
            period="2026-02", pillar="care", total_tickets=20, reactiegraad=75.0, avg_score=4.2
        )
        d = r.to_dict()
        assert d["total_tickets"] == 20
        assert d["reactiegraad"] == 75.0


# ---------------------------------------------------------------------------
# _calc_reactiegraad
# ---------------------------------------------------------------------------
class TestCalcReactiegraad:
    def test_normaal(self, analyser, df5):
        total, scored, rate = analyser._calc_reactiegraad(df5)
        assert total == 5
        assert scored == 4
        assert rate == pytest.approx(80.0)

    def test_alle_gescoord(self, analyser):
        df = pd.DataFrame([{"score": 4.0}, {"score": 5.0}])
        _, _, rate = analyser._calc_reactiegraad(df)
        assert rate == pytest.approx(100.0)

    def test_geen_scores(self, analyser):
        df = pd.DataFrame([{"score": None}, {"score": None}])
        _total, scored, rate = analyser._calc_reactiegraad(df)
        assert scored == 0 and rate == 0.0

    def test_leeg(self, analyser, df_leeg):
        total, _scored, rate = analyser._calc_reactiegraad(df_leeg)
        assert total == 0 and rate == 0.0

    def test_retourtype(self, analyser, df5):
        r = analyser._calc_reactiegraad(df5)
        assert isinstance(r[0], int) and isinstance(r[1], int) and isinstance(r[2], float)


# ---------------------------------------------------------------------------
# _calc_avg_score
# ---------------------------------------------------------------------------
class TestCalcAvgScore:
    def test_normaal(self, analyser, df5):
        assert analyser._calc_avg_score(df5) == pytest.approx(3.50)

    def test_leeg(self, analyser, df_leeg):
        assert analyser._calc_avg_score(df_leeg) == 0.0

    def test_alle_nan(self, analyser):
        df = pd.DataFrame([{"score": None}])
        assert analyser._calc_avg_score(df) == 0.0

    def test_afgerond_2dec(self, analyser):
        df = pd.DataFrame([{"score": 1.0}, {"score": 2.0}, {"score": 3.0}])
        v = analyser._calc_avg_score(df)
        assert v == round(v, 2)

    def test_enkele_rij(self, analyser):
        df = pd.DataFrame([{"score": 4.5}])
        assert analyser._calc_avg_score(df) == pytest.approx(4.5)


# ---------------------------------------------------------------------------
# _calc_high_critical
# ---------------------------------------------------------------------------
class TestCalcHighCritical:
    def test_blocker_critical(self, analyser, df5):
        hc, ratio = analyser._calc_high_critical(df5)
        assert hc == 2 and ratio == pytest.approx(40.0)

    def test_major_telt_mee(self, analyser):
        df = pd.DataFrame([{"priority": "Major"}, {"priority": "Minor"}, {"priority": "Trivial"}])
        hc, ratio = analyser._calc_high_critical(df)
        assert hc == 1 and ratio == pytest.approx(33.3, abs=0.1)

    def test_geen_hc(self, analyser):
        df = pd.DataFrame([{"priority": "Minor"}, {"priority": "Trivial"}])
        hc, ratio = analyser._calc_high_critical(df)
        assert hc == 0 and ratio == 0.0

    def test_alle_hc(self, analyser):
        df = pd.DataFrame(
            [{"priority": "Blocker"}, {"priority": "Critical"}, {"priority": "Major"}]
        )
        hc, ratio = analyser._calc_high_critical(df)
        assert hc == 3 and ratio == pytest.approx(100.0)

    def test_leeg(self, analyser, df_leeg):
        hc, ratio = analyser._calc_high_critical(df_leeg)
        assert hc == 0 and ratio == 0.0

    def test_retourtype(self, analyser, df5):
        r = analyser._calc_high_critical(df5)
        assert isinstance(r[0], int) and isinstance(r[1], float)


# ---------------------------------------------------------------------------
# _calc_comment_ratio
# ---------------------------------------------------------------------------
class TestCalcCommentRatio:
    def test_normaal(self, analyser, df5):
        # 'goed', 'uitstekend', 'matig' = 3/5 = 60%
        assert analyser._calc_comment_ratio(df5) == pytest.approx(60.0)

    def test_alle_leeg(self, analyser):
        df = pd.DataFrame([{"comment": ""}, {"comment": ""}, {"comment": "   "}])
        assert analyser._calc_comment_ratio(df) == 0.0

    def test_alle_gevuld(self, analyser):
        df = pd.DataFrame([{"comment": "a"}, {"comment": "b"}])
        assert analyser._calc_comment_ratio(df) == pytest.approx(100.0)

    def test_kolom_ontbreekt(self, analyser):
        df = pd.DataFrame([{"score": 4.0}])
        assert analyser._calc_comment_ratio(df) == 0.0

    def test_leeg_df(self, analyser):
        df = pd.DataFrame(columns=["comment"])
        assert analyser._calc_comment_ratio(df) == 0.0

    def test_whitespace(self, analyser):
        df = pd.DataFrame([{"comment": "   "}, {"comment": "opmerking"}])
        assert analyser._calc_comment_ratio(df) == pytest.approx(50.0)

    def test_none(self, analyser):
        df = pd.DataFrame([{"comment": None}, {"comment": "opmerking"}])
        assert analyser._calc_comment_ratio(df) == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# _calc_mom_trend
# ---------------------------------------------------------------------------
class TestCalcMomTrend:
    def test_positief(self, analyser):
        c = pd.DataFrame([{"score": 4.5}])
        p = pd.DataFrame([{"score": 3.5}])
        assert analyser._calc_mom_trend(c, p, metric="avg_score") == pytest.approx(1.0)

    def test_negatief(self, analyser):
        c = pd.DataFrame([{"score": 3.0}])
        p = pd.DataFrame([{"score": 4.0}])
        assert analyser._calc_mom_trend(c, p, metric="avg_score") == pytest.approx(-1.0)

    def test_nul(self, analyser):
        c = pd.DataFrame([{"score": 4.0}])
        p = pd.DataFrame([{"score": 4.0}])
        assert analyser._calc_mom_trend(c, p, metric="avg_score") == pytest.approx(0.0)

    def test_lege_vorige(self, analyser):
        c = pd.DataFrame([{"score": 4.0}])
        p = pd.DataFrame(columns=["score"])
        assert analyser._calc_mom_trend(c, p, metric="avg_score") == 0.0

    def test_reactiegraad(self, analyser):
        c = pd.DataFrame([{"score": 4.0}, {"score": 5.0}])
        p = pd.DataFrame([{"score": 4.0}, {"score": None}])
        assert analyser._calc_mom_trend(c, p, metric="reactiegraad") == pytest.approx(50.0)

    def test_onbekend_gooit_valueerror(self, analyser):
        with pytest.raises(ValueError, match="Onbekende metric"):
            analyser._calc_mom_trend(
                pd.DataFrame([{"score": 4.0}]), pd.DataFrame([{"score": 3.0}]), metric="fout"
            )

    def test_afgerond_1dec(self, analyser):
        c = pd.DataFrame([{"score": 4.333}])
        p = pd.DataFrame([{"score": 3.0}])
        delta = analyser._calc_mom_trend(c, p, metric="avg_score")
        assert delta == round(delta, 1)


# ---------------------------------------------------------------------------
# _group_by_hospital
# ---------------------------------------------------------------------------
class TestGroupByHospital:
    def test_leeg(self, analyser, df_leeg):
        assert analyser._group_by_hospital(df_leeg) == {}

    def test_sleutels(self, analyser, df5):
        assert set(analyser._group_by_hospital(df5).keys()) == {
            "AZ Test",
            "UZ Brussel",
            "OLV Aalst",
        }

    def test_az_kpi(self, analyser, df5):
        az = analyser._group_by_hospital(df5)["AZ Test"]
        assert az["total_tickets"] == 2
        assert az["avg_score"] == pytest.approx(4.5)
        assert az["high_critical_count"] == 1

    def test_uz_kpi(self, analyser, df5):
        uz = analyser._group_by_hospital(df5)["UZ Brussel"]
        assert uz["avg_score"] == pytest.approx(2.5)

    def test_onbekend(self, analyser):
        df = pd.DataFrame([{"score": 4.0, "priority": "Minor", "comment": "", "hospital": None}])
        result = analyser._group_by_hospital(df)
        assert "ONBEKEND" in result

    def test_alle_velden(self, analyser, df5):
        verplicht = {
            "total_tickets",
            "scored_tickets",
            "reactiegraad",
            "avg_score",
            "high_critical_count",
            "high_critical_ratio",
        }
        for d in analyser._group_by_hospital(df5).values():
            assert verplicht.issubset(d)

    def test_olv_geen_score(self, analyser, df5):
        olv = analyser._group_by_hospital(df5)["OLV Aalst"]
        assert olv["scored_tickets"] == 0
        assert olv["avg_score"] == 0.0

    def test_kopie_origineel_ongewijzigd(self, analyser):
        df = pd.DataFrame([{"score": 4.0, "priority": "Minor", "comment": "", "hospital": None}])
        original = df["hospital"].iloc[0]
        analyser._group_by_hospital(df)
        assert df["hospital"].iloc[0] == original


# ---------------------------------------------------------------------------
# Abstract + init
# ---------------------------------------------------------------------------
class TestBaseAnalyserAbstract:
    def test_directe_instantiatie_verboden(self):
        with pytest.raises(TypeError):
            BaseAnalyser(pd.DataFrame([{"score": 4.0}]))  # type: ignore[abstract]

    def test_concrete_instantieerbaar(self, df5):
        assert ConcreteAnalyser(df5) is not None

    def test_kopie_bij_init(self):
        df = pd.DataFrame([{"score": 4.0, "priority": "Minor", "comment": "", "hospital": "H"}])
        a = ConcreteAnalyser(df)
        df["score"] = 99.0
        assert a._df["score"].iloc[0] == 4.0

    def test_analyse_retourneert_kpiresult(self, df5):
        assert isinstance(ConcreteAnalyser(df5).analyse("2026-01"), KpiResult)
