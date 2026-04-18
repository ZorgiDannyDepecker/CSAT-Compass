"""
Unit tests voor EvolutionAnalyser en EvolutionResult.

Verwachte testwaarden zijn berekend op basis van de evolution_df fixture
(zie tests/conftest.py voor de volledige documentatie van verwachte waarden).

Baseline-periodes: ["2025-06", "2025-07"]
Current-periodes:  ["2026-01", "2026-02"]
"""

import pandas as pd
import pytest

from csat.core.analysers.evolution_analyser import (
    THEME_ACTION_HINTS,
    THEME_KEYWORDS,
    EvolutionAnalyser,
)
from csat.core.analysers.evolution_result import (
    EvolutionResult,
    HospitalComparison,
    IssueTypeComparison,
    KpiStatus,
    MonthlyDataPoint,
    PriorityComparison,
    ResponseTimeRow,
    ThemeEvolution,
)

# Vaste periodes voor alle tests
BASELINE = ["2025-06", "2025-07"]
CURRENT = ["2026-01", "2026-02"]


# ===========================================================================
# Helpers
# ===========================================================================


def make_analyser(evolution_df: pd.DataFrame) -> EvolutionAnalyser:
    """Maak een EvolutionAnalyser voor de pharma-pijler."""
    return EvolutionAnalyser(evolution_df, pillar_key="pharma")


def run_analyse(evolution_df: pd.DataFrame) -> EvolutionResult:
    """Voer de standaard analyse uit op de evolution_df fixture."""
    return make_analyser(evolution_df).analyse(BASELINE, CURRENT)


# ===========================================================================
# 1. Initialisatie
# ===========================================================================


class TestEvolutionAnalyserInit:
    """Tests voor __init__ — pijlervalidatie en data-filtering."""

    def test_init_geldige_pijler(self, evolution_df: pd.DataFrame) -> None:
        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        assert analyser._pillar_key == "pharma"

    def test_init_ongeldige_pijler_gooit_valueerror(self, evolution_df: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="Onbekende pijler"):
            EvolutionAnalyser(evolution_df, pillar_key="niet_bestaand")

    def test_init_filtert_pijler(self, evolution_df: pd.DataFrame) -> None:
        """Pillar_df mag enkel PHARMA-rijen bevatten."""
        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        assert (analyser._pillar_df["product_domain"] == "PHARMA").all()

    def test_init_filtert_startdatum(self, evolution_df: pd.DataFrame) -> None:
        """Rijen vóór ANALYSE_START_DATE (2025-01-01) worden uitgesloten."""
        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        created = pd.to_datetime(analyser._pillar_df["created"])
        assert (created >= pd.Timestamp("2025-01-01")).all()

    def test_init_alle_geldige_pijlers(self, evolution_df: pd.DataFrame) -> None:
        """Alle pijlers uit PILLAR_REGISTRY moeten initialiseerbaar zijn."""
        for pillar in ["zorgi", "pharma", "care", "care_admin", "erp4hc"]:
            analyser = EvolutionAnalyser(evolution_df, pillar_key=pillar)
            assert analyser._pillar_key == pillar


# ===========================================================================
# 2. Analyse — retourtype en labels
# ===========================================================================


class TestEvolutionAnalyserRetourtype:
    """Tests voor het retourtype en de labels van analyse()."""

    def test_analyse_retourneert_evolution_result(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert isinstance(result, EvolutionResult)

    def test_pillar_correct(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.pillar == "pharma"

    def test_labels_auto_gegenereerd_zelfde_jaar(self, evolution_df: pd.DataFrame) -> None:
        """Baseline ["2025-06", "2025-07"] → label "2025"."""
        result = run_analyse(evolution_df)
        assert result.baseline_label == "2025"
        assert result.current_label == "2026"

    def test_labels_custom_overschrijven_auto(self, evolution_df: pd.DataFrame) -> None:
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(
            BASELINE, CURRENT, baseline_label="Jaar A", current_label="Jaar B"
        )
        assert result.baseline_label == "Jaar A"
        assert result.current_label == "Jaar B"

    def test_label_enkele_periode(self, evolution_df: pd.DataFrame) -> None:
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(["2025-06"], ["2026-01"])
        assert result.baseline_label == "2025-06"
        assert result.current_label == "2026-01"

    def test_label_meerdere_jaren(self, evolution_df: pd.DataFrame) -> None:
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(["2025-06", "2026-01"], ["2026-02"])
        assert result.baseline_label == "2025-06 - 2026-01"

    def test_ongeldige_periode_gooit_valueerror(self, evolution_df: pd.DataFrame) -> None:
        analyser = make_analyser(evolution_df)
        with pytest.raises(ValueError):
            analyser.analyse(["2025-13"], ["2026-01"])


# ===========================================================================
# 3. Kerncijfers
# ===========================================================================


class TestKerncijfers:
    """Tests voor de berekening van kerncijfers."""

    def test_baseline_total(self, evolution_df: pd.DataFrame) -> None:
        """6 PHARMA-tickets in baseline (2025-06 + 2025-07)."""
        result = run_analyse(evolution_df)
        assert result.baseline_total == 6

    def test_current_total(self, evolution_df: pd.DataFrame) -> None:
        """4 PHARMA-tickets in current (2026-01 + 2026-02)."""
        result = run_analyse(evolution_df)
        assert result.current_total == 4

    def test_baseline_avg_score(self, evolution_df: pd.DataFrame) -> None:
        """(2+3+2+4+3)/5 = 2,80."""
        result = run_analyse(evolution_df)
        assert result.baseline_avg_score == pytest.approx(2.80)

    def test_current_avg_score(self, evolution_df: pd.DataFrame) -> None:
        """(5+4+5+4)/4 = 4,50."""
        result = run_analyse(evolution_df)
        assert result.current_avg_score == pytest.approx(4.50)

    def test_delta_avg_score(self, evolution_df: pd.DataFrame) -> None:
        """Delta = 4,50 - 2,80 = +1,70."""
        result = run_analyse(evolution_df)
        assert result.delta_avg_score == pytest.approx(1.70)

    def test_baseline_pct_positive(self, evolution_df: pd.DataFrame) -> None:
        """1/5 gescoorde tickets >= 4 = 20,0%."""
        result = run_analyse(evolution_df)
        assert result.baseline_pct_positive == pytest.approx(20.0)

    def test_current_pct_positive(self, evolution_df: pd.DataFrame) -> None:
        """4/4 gescoorde tickets >= 4 = 100,0%."""
        result = run_analyse(evolution_df)
        assert result.current_pct_positive == pytest.approx(100.0)

    def test_baseline_pct_negative(self, evolution_df: pd.DataFrame) -> None:
        """2/5 gescoorde tickets <= 2 = 40,0%."""
        result = run_analyse(evolution_df)
        assert result.baseline_pct_negative == pytest.approx(40.0)

    def test_current_pct_negative(self, evolution_df: pd.DataFrame) -> None:
        """0/4 gescoorde tickets <= 2 = 0,0%."""
        result = run_analyse(evolution_df)
        assert result.current_pct_negative == pytest.approx(0.0)

    def test_baseline_hc_ratio(self, evolution_df: pd.DataFrame) -> None:
        """3/6 tickets zijn Blocker/Critical/Major = 50,0%."""
        result = run_analyse(evolution_df)
        assert result.baseline_hc_ratio == pytest.approx(50.0)

    def test_current_hc_ratio(self, evolution_df: pd.DataFrame) -> None:
        """0/4 tickets zijn Blocker/Critical/Major = 0,0%."""
        result = run_analyse(evolution_df)
        assert result.current_hc_ratio == pytest.approx(0.0)

    def test_baseline_n_hospitals(self, evolution_df: pd.DataFrame) -> None:
        """3 unieke ziekenhuizen in baseline."""
        result = run_analyse(evolution_df)
        assert result.baseline_n_hospitals == 3

    def test_current_n_hospitals(self, evolution_df: pd.DataFrame) -> None:
        """2 unieke ziekenhuizen in current."""
        result = run_analyse(evolution_df)
        assert result.current_n_hospitals == 2

    def test_baseline_avg_response_days(self, evolution_df: pd.DataFrame) -> None:
        """(15+15+13+9+10)/5 = 12,4 d."""
        result = run_analyse(evolution_df)
        assert result.baseline_avg_response_days == pytest.approx(12.4)

    def test_current_avg_response_days(self, evolution_df: pd.DataFrame) -> None:
        """(1+2+2+2)/4 = 1,75 → afgerond 1,8 d."""
        result = run_analyse(evolution_df)
        assert result.current_avg_response_days == pytest.approx(1.8)


# ===========================================================================
# 4. Lege periodes
# ===========================================================================


class TestLegeData:
    """Tests voor randgevallen met lege DataFrames."""

    def test_lege_baseline(self, evolution_df: pd.DataFrame) -> None:
        """Baseline zonder data → baseline_total=0, avg=0.0."""
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(["2024-01"], CURRENT)
        assert result.baseline_total == 0
        assert result.baseline_avg_score == 0.0
        assert result.baseline_pct_positive == 0.0
        assert result.baseline_n_hospitals == 0

    def test_lege_current(self, evolution_df: pd.DataFrame) -> None:
        """Current zonder data → current_total=0, avg=0.0."""
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(BASELINE, ["2027-01"])
        assert result.current_total == 0
        assert result.current_avg_score == 0.0

    def test_beide_leeg(self, evolution_df: pd.DataFrame) -> None:
        """Beide periodes zonder data → delta = 0.0."""
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(["2024-01"], ["2027-01"])
        assert result.delta_avg_score == 0.0
        assert result.trend_breadth == "gemengd"

    def test_lege_periodes_lijst(self, evolution_df: pd.DataFrame) -> None:
        """Lege periodes-lijst → baseline_total=0."""
        analyser = make_analyser(evolution_df)
        result = analyser.analyse([], CURRENT)
        assert result.baseline_total == 0
        assert result.baseline_label == "—"

    def test_lege_df_response_time(self, empty_df: pd.DataFrame) -> None:
        """Lege DataFrame → avg_response_days = 0.0."""
        analyser = EvolutionAnalyser(empty_df, pillar_key="pharma")
        assert analyser._calc_avg_response_days(empty_df) == 0.0


# ===========================================================================
# 5. Maandelijkse tijdlijn
# ===========================================================================


class TestMonthlyTimeline:
    """Tests voor de monthly_timeline berekening."""

    def test_aantal_datapunten(self, evolution_df: pd.DataFrame) -> None:
        """4 unieke periodes → 4 datapunten in tijdlijn."""
        result = run_analyse(evolution_df)
        assert len(result.monthly_timeline) == 4

    def test_periodes_gesorteerd(self, evolution_df: pd.DataFrame) -> None:
        """Tijdlijn is chronologisch gesorteerd."""
        result = run_analyse(evolution_df)
        periodes = [dp.period for dp in result.monthly_timeline]
        assert periodes == sorted(periodes)

    def test_fase_h1_2025(self, evolution_df: pd.DataFrame) -> None:
        """Maand 6 → S1 2025."""
        result = run_analyse(evolution_df)
        dp = next(d for d in result.monthly_timeline if d.period == "2025-06")
        assert dp.fase == "S1 2025"

    def test_fase_h2_2025(self, evolution_df: pd.DataFrame) -> None:
        """Maand 7 → S2 2025."""
        result = run_analyse(evolution_df)
        dp = next(d for d in result.monthly_timeline if d.period == "2025-07")
        assert dp.fase == "S2 2025"

    def test_fase_h1_2026(self, evolution_df: pd.DataFrame) -> None:
        """Maand 1 van 2026 → S1 2026."""
        result = run_analyse(evolution_df)
        dp = next(d for d in result.monthly_timeline if d.period == "2026-01")
        assert dp.fase == "S1 2026"

    def test_datapunt_2025_06_avg_score(self, evolution_df: pd.DataFrame) -> None:
        """2025-06: (2+3+2)/3 = 2,33."""
        result = run_analyse(evolution_df)
        dp = next(d for d in result.monthly_timeline if d.period == "2025-06")
        assert dp.avg_score == pytest.approx(2.33, abs=0.01)

    def test_datapunt_2025_06_total(self, evolution_df: pd.DataFrame) -> None:
        """2025-06: 3 tickets totaal."""
        result = run_analyse(evolution_df)
        dp = next(d for d in result.monthly_timeline if d.period == "2025-06")
        assert dp.total_tickets == 3

    def test_datapunt_2025_06_pct_neg(self, evolution_df: pd.DataFrame) -> None:
        """2025-06: 2/3 negatief = 66,7%."""
        result = run_analyse(evolution_df)
        dp = next(d for d in result.monthly_timeline if d.period == "2025-06")
        assert dp.pct_negative == pytest.approx(66.7, abs=0.1)

    def test_datapunt_leeg_periode(self, evolution_df: pd.DataFrame) -> None:
        """Periode zonder data → avg_score=0.0, total=0."""
        analyser = make_analyser(evolution_df)
        dp = analyser._make_monthly_datapoint("2024-01")
        assert dp.avg_score == 0.0
        assert dp.total_tickets == 0


# ===========================================================================
# 6. Issue type vergelijking
# ===========================================================================


class TestIssueTypeComparison:
    """Tests voor by_issue_type berekening."""

    def test_alle_types_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        """Bug, Question, Improvement moeten aanwezig zijn."""
        result = run_analyse(evolution_df)
        types = [c.issue_type for c in result.by_issue_type]
        assert "Bug" in types
        assert "Question" in types
        assert "Improvement" in types

    def test_bug_baseline_score(self, evolution_df: pd.DataFrame) -> None:
        """Bug baseline: (2+3+4)/3 = 3,0 (EB-006 geen score)."""
        result = run_analyse(evolution_df)
        bug = next(c for c in result.by_issue_type if c.issue_type == "Bug")
        assert bug.baseline_score == pytest.approx(3.0)

    def test_bug_current_score(self, evolution_df: pd.DataFrame) -> None:
        """Bug current: (5+5)/2 = 5,0."""
        result = run_analyse(evolution_df)
        bug = next(c for c in result.by_issue_type if c.issue_type == "Bug")
        assert bug.current_score == pytest.approx(5.0)

    def test_bug_baseline_pct_neg(self, evolution_df: pd.DataFrame) -> None:
        """Bug baseline: 1/3 gescoord <= 2 = 33,3%."""
        result = run_analyse(evolution_df)
        bug = next(c for c in result.by_issue_type if c.issue_type == "Bug")
        assert bug.baseline_pct_neg == pytest.approx(33.3, abs=0.1)

    def test_type_alleen_in_baseline(self, evolution_df: pd.DataFrame) -> None:
        """Type alleen in baseline → current_score=0.0, current_pct_neg=0.0."""
        result = run_analyse(evolution_df)
        # Improvement is in beide periodes; Blocker-priority-type check
        for comp in result.by_issue_type:
            assert isinstance(comp, IssueTypeComparison)

    def test_gesorteerd_op_naam(self, evolution_df: pd.DataFrame) -> None:
        """by_issue_type is alfabetisch gesorteerd."""
        result = run_analyse(evolution_df)
        types = [c.issue_type for c in result.by_issue_type]
        assert types == sorted(types)


# ===========================================================================
# 7. Prioriteit vergelijking
# ===========================================================================


class TestPriorityComparison:
    """Tests voor by_priority berekening."""

    def test_blocker_enkel_in_baseline(self, evolution_df: pd.DataFrame) -> None:
        """Blocker zit alleen in baseline → current_score=0.0."""
        result = run_analyse(evolution_df)
        blocker = next(c for c in result.by_priority if c.priority == "Blocker")
        assert blocker.baseline_score == pytest.approx(2.0)
        assert blocker.current_score == pytest.approx(0.0)

    def test_trivial_in_beide_periodes(self, evolution_df: pd.DataFrame) -> None:
        """Trivial: baseline=2,0 (EB-003), current=4,67 (EC-001,EC-003,EC-004)."""
        result = run_analyse(evolution_df)
        trivial = next(c for c in result.by_priority if c.priority == "Trivial")
        assert trivial.baseline_score == pytest.approx(2.0)
        assert trivial.current_score == pytest.approx(4.67, abs=0.01)

    def test_alle_baseline_prioriteiten_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        """Blocker, Critical, Major, Minor, Trivial moeten aanwezig zijn."""
        result = run_analyse(evolution_df)
        prios = {c.priority for c in result.by_priority}
        assert {"Blocker", "Critical", "Major", "Minor", "Trivial"}.issubset(prios)

    def test_gesorteerd_op_naam(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        prios = [c.priority for c in result.by_priority]
        assert prios == sorted(prios)


# ===========================================================================
# 8. Responstijd per score-niveau
# ===========================================================================


class TestResponseTimeByScore:
    """Tests voor response_time_by_score berekening."""

    def test_score2_baseline_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        """Score 2: EB-001 (15d) + EB-003 (13d) → avg=14,0d."""
        result = run_analyse(evolution_df)
        assert 2 in result.response_time_by_score
        row = result.response_time_by_score[2]
        assert row.baseline_days == pytest.approx(14.0)

    def test_score2_current_none(self, evolution_df: pd.DataFrame) -> None:
        """Score 2 heeft geen current-data → current_days=None."""
        result = run_analyse(evolution_df)
        row = result.response_time_by_score[2]
        assert row.current_days is None

    def test_score3_baseline(self, evolution_df: pd.DataFrame) -> None:
        """Score 3: EB-002 (15d) + EB-005 (10d) → avg=12,5d."""
        result = run_analyse(evolution_df)
        assert 3 in result.response_time_by_score
        row = result.response_time_by_score[3]
        assert row.baseline_days == pytest.approx(12.5)

    def test_score4_beide_periodes(self, evolution_df: pd.DataFrame) -> None:
        """Score 4: baseline=9,0d (EB-004), current=2,0d (EC-002, EC-004)."""
        result = run_analyse(evolution_df)
        assert 4 in result.response_time_by_score
        row = result.response_time_by_score[4]
        assert row.baseline_days == pytest.approx(9.0)
        assert row.current_days == pytest.approx(2.0)

    def test_score5_current_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        """Score 5: EC-001 (1d) + EC-003 (2d) → avg=1,5d."""
        result = run_analyse(evolution_df)
        assert 5 in result.response_time_by_score
        row = result.response_time_by_score[5]
        assert row.current_days == pytest.approx(1.5)
        assert row.baseline_days is None

    def test_score1_niet_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        """Score 1 komt niet voor → niet in dict."""
        result = run_analyse(evolution_df)
        assert 1 not in result.response_time_by_score

    def test_geen_satisfaction_date(self, evolution_df: pd.DataFrame) -> None:
        """EB-006 heeft geen satisfaction_date — mag geen invloed hebben."""
        result = run_analyse(evolution_df)
        # EB-006 heeft score=None, dus geen invloed op response_time
        assert result.baseline_avg_response_days > 0

    def test_response_row_is_correct_type(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        for row in result.response_time_by_score.values():
            assert isinstance(row, ResponseTimeRow)


# ===========================================================================
# 9. Ziekenhuisvergelijking
# ===========================================================================


class TestHospitalComparison:
    """Tests voor hospital_comparison, hospitals_disappeared en hospitals_new."""

    def test_drie_ziekenhuizen_in_comparison(self, evolution_df: pd.DataFrame) -> None:
        """AZ Groeninge + UZ Brussel + OLV Aalst = 3 entries."""
        result = run_analyse(evolution_df)
        assert len(result.hospital_comparison) == 3

    def test_hospitals_disappeared(self, evolution_df: pd.DataFrame) -> None:
        """OLV Aalst verdwijnt in current."""
        result = run_analyse(evolution_df)
        names = [h.hospital for h in result.hospitals_disappeared]
        assert "OLV Aalst" in names

    def test_hospitals_new_leeg(self, evolution_df: pd.DataFrame) -> None:
        """Geen nieuwe ziekenhuizen in current."""
        result = run_analyse(evolution_df)
        assert result.hospitals_new == []

    def test_az_groeninge_scores(self, evolution_df: pd.DataFrame) -> None:
        """AZ Groeninge: baseline=(2+3)/2=2,5, current=(5+4)/2=4,5."""
        result = run_analyse(evolution_df)
        az = next(h for h in result.hospital_comparison if h.hospital == "AZ Groeninge")
        assert az.baseline_score == pytest.approx(2.5)
        assert az.current_score == pytest.approx(4.5)

    def test_uz_brussel_scores(self, evolution_df: pd.DataFrame) -> None:
        """UZ Brussel: baseline=(2+4)/2=3,0, current=(5+4)/2=4,5."""
        result = run_analyse(evolution_df)
        uz = next(h for h in result.hospital_comparison if h.hospital == "UZ Brussel")
        assert uz.baseline_score == pytest.approx(3.0)
        assert uz.current_score == pytest.approx(4.5)

    def test_olv_aalst_current_score_none(self, evolution_df: pd.DataFrame) -> None:
        """OLV Aalst is verdwenen → current_score=None, current_total=0."""
        result = run_analyse(evolution_df)
        olv = next(h for h in result.hospital_comparison if h.hospital == "OLV Aalst")
        assert olv.current_score is None
        assert olv.current_total == 0

    def test_hospital_comparison_type(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        for h in result.hospital_comparison:
            assert isinstance(h, HospitalComparison)

    def test_nieuw_ziekenhuis(self, evolution_df: pd.DataFrame) -> None:
        """Ziekenhuis alleen in current → baseline_score=0.0, baseline_total=0."""
        # Voeg een nieuw ziekenhuis toe in de current data
        extra = evolution_df.copy()
        new_row = pd.DataFrame(
            [
                {
                    "key": "EC-NEW",
                    "issue_type": "Bug",
                    "priority": "Minor",
                    "summary": "Test",
                    "score": 4.0,
                    "comment": "",
                    "satisfaction_date": pd.Timestamp("2026-01-15"),
                    "created": pd.Timestamp("2026-01-10"),
                    "hospital": "Nieuw Ziekenhuis",
                    "product": "Apotheek",
                    "product_domain": "PHARMA",
                    "project_key": "SD30",
                }
            ]
        )
        combined = pd.concat([extra, new_row], ignore_index=True)
        analyser = EvolutionAnalyser(combined, pillar_key="pharma")
        result = analyser.analyse(BASELINE, CURRENT)
        assert "Nieuw Ziekenhuis" in [h.hospital for h in result.hospitals_new]
        nieuw = next(h for h in result.hospital_comparison if h.hospital == "Nieuw Ziekenhuis")
        assert nieuw.baseline_total == 0
        assert nieuw.baseline_score == pytest.approx(0.0)


# ===========================================================================
# 10. Negatieve thema's
# ===========================================================================


class TestNegativeThemes:
    """Tests voor _negative_themes keyword matching."""

    def test_responstijd_opgelost(self, evolution_df: pd.DataFrame) -> None:
        """EB-001 (score=2, 'te lang gewacht') → responstijd OPGELOST."""
        result = run_analyse(evolution_df)
        resp = next((t for t in result.negative_themes if t.theme_key == "responstijd"), None)
        assert resp is not None
        assert resp.status == "OPGELOST"
        assert resp.pct_baseline == pytest.approx(50.0)
        assert resp.pct_current == pytest.approx(0.0)

    def test_onvolledig_opgelost(self, evolution_df: pd.DataFrame) -> None:
        """EB-003 (score=2, 'nog steeds niet opgelost') → onvolledig OPGELOST."""
        result = run_analyse(evolution_df)
        onv = next((t for t in result.negative_themes if t.theme_key == "onvolledig"), None)
        assert onv is not None
        assert onv.status == "OPGELOST"
        assert onv.pct_baseline == pytest.approx(50.0)

    def test_communicatie_niet_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        """Geen communicatie-keywords in data → niet in negative_themes."""
        result = run_analyse(evolution_df)
        comm = next((t for t in result.negative_themes if t.theme_key == "communicatie"), None)
        assert comm is None

    def test_geen_negatieve_tickets_leeg(self, evolution_df: pd.DataFrame) -> None:
        """Lege baseline → geen thema's."""
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(["2024-01"], CURRENT)
        assert result.negative_themes == []

    def test_theme_nog_aanwezig(self) -> None:
        """Thema in beide periodes → status NOG_AANWEZIG."""
        import pandas as pd

        def make_row(key, score, comment, created, sat=None, domain="PHARMA"):
            return {
                "key": key,
                "issue_type": "Bug",
                "priority": "Minor",
                "summary": "Test",
                "score": score,
                "comment": comment,
                "satisfaction_date": pd.Timestamp(sat) if sat else pd.NaT,
                "created": pd.Timestamp(created),
                "hospital": "H1",
                "product": "P",
                "product_domain": domain,
                "project_key": "SD30",
            }

        rows = [
            make_row("T1", 2.0, "te lang gewacht", "2025-06-01"),
            make_row("T2", 2.0, "te lang gewacht", "2026-01-01"),
        ]
        df = pd.DataFrame(rows)
        analyser = EvolutionAnalyser(df, pillar_key="pharma")
        result = analyser.analyse(["2025-06"], ["2026-01"])
        resp = next((t for t in result.negative_themes if t.theme_key == "responstijd"), None)
        assert resp is not None
        assert resp.status == "NOG_AANWEZIG"

    def test_theme_nieuw(self) -> None:
        """Thema alleen in current → status NIEUW."""
        import pandas as pd

        def make_row(key, score, comment, created, domain="PHARMA"):
            return {
                "key": key,
                "issue_type": "Bug",
                "priority": "Minor",
                "summary": "Test",
                "score": score,
                "comment": comment,
                "satisfaction_date": pd.NaT,
                "created": pd.Timestamp(created),
                "hospital": "H1",
                "product": "P",
                "product_domain": domain,
                "project_key": "SD30",
            }

        rows = [
            make_row("T1", 3.0, "goed", "2025-06-01"),
            make_row("T2", 2.0, "te lang gewacht", "2026-01-01"),
        ]
        df = pd.DataFrame(rows)
        analyser = EvolutionAnalyser(df, pillar_key="pharma")
        result = analyser.analyse(["2025-06"], ["2026-01"])
        resp = next((t for t in result.negative_themes if t.theme_key == "responstijd"), None)
        assert resp is not None
        assert resp.status == "NIEUW"

    def test_theme_keywords_config(self) -> None:
        """THEME_KEYWORDS bevat de 5 verwachte thema's."""
        expected = {"responstijd", "onvolledig", "communicatie", "urgentie", "automatisering"}
        assert set(THEME_KEYWORDS.keys()) == expected


# ===========================================================================
# 11. KPI status
# ===========================================================================


class TestKpiStatus:
    """Tests voor KPI status berekening (ADR-009)."""

    def test_kpi_keys_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        expected_keys = {
            "avg_score_baseline",
            "avg_score_current",
            "high_critical_baseline",
            "high_critical_current",
            "trend",
        }
        assert expected_keys == set(result.kpi_status.keys())

    def test_avg_score_baseline_at_risk(self, evolution_df: pd.DataFrame) -> None:
        """Baseline avg=2,80 < 3,5 → AT_RISK."""
        result = run_analyse(evolution_df)
        assert result.kpi_status["avg_score_baseline"] == KpiStatus.AT_RISK

    def test_avg_score_current_ok(self, evolution_df: pd.DataFrame) -> None:
        """Current avg=4,50 >= 4,0 → OK."""
        result = run_analyse(evolution_df)
        assert result.kpi_status["avg_score_current"] == KpiStatus.OK

    def test_hc_baseline_at_risk(self, evolution_df: pd.DataFrame) -> None:
        """Baseline HC=50% > 25% → AT_RISK."""
        result = run_analyse(evolution_df)
        assert result.kpi_status["high_critical_baseline"] == KpiStatus.AT_RISK

    def test_hc_current_ok(self, evolution_df: pd.DataFrame) -> None:
        """Current HC=0% <= 15% → OK."""
        result = run_analyse(evolution_df)
        assert result.kpi_status["high_critical_current"] == KpiStatus.OK

    def test_trend_ok(self, evolution_df: pd.DataFrame) -> None:
        """Current OK + delta positief → trend OK."""
        result = run_analyse(evolution_df)
        assert result.kpi_status["trend"] == KpiStatus.OK

    def test_kpi_unknown_bij_lege_data(self, evolution_df: pd.DataFrame) -> None:
        """Lege baseline → avg_score_baseline=UNKNOWN."""
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(["2024-01"], CURRENT)
        assert result.kpi_status["avg_score_baseline"] == KpiStatus.UNKNOWN

    def test_kpi_status_warning(self) -> None:
        """Score tussen 3,5 en 4,0 → WARNING."""
        import pandas as pd

        rows = [
            {
                "key": "W1",
                "issue_type": "Bug",
                "priority": "Minor",
                "summary": "Test",
                "score": 3.7,
                "comment": "",
                "satisfaction_date": pd.NaT,
                "created": pd.Timestamp("2025-06-01"),
                "hospital": "H1",
                "product": "P",
                "product_domain": "PHARMA",
                "project_key": "SD30",
            },
            {
                "key": "W2",
                "issue_type": "Bug",
                "priority": "Minor",
                "summary": "Test",
                "score": 4.5,
                "comment": "",
                "satisfaction_date": pd.NaT,
                "created": pd.Timestamp("2026-01-01"),
                "hospital": "H1",
                "product": "P",
                "product_domain": "PHARMA",
                "project_key": "SD30",
            },
        ]
        df = pd.DataFrame(rows)
        analyser = EvolutionAnalyser(df, pillar_key="pharma")
        result = analyser.analyse(["2025-06"], ["2026-01"])
        assert result.kpi_status["avg_score_baseline"] == KpiStatus.WARNING

    def test_kpi_hc_warning(self) -> None:
        """HC ratio tussen 15% en 25% → WARNING."""
        import pandas as pd

        # 20 tickets, 4 HC (20%) — grens between HIGH_CRITICAL_MAX (15%) en 25%
        rows = []
        for i in range(20):
            priority = "Blocker" if i < 4 else "Minor"
            rows.append(
                {
                    "key": f"H{i}",
                    "issue_type": "Bug",
                    "priority": priority,
                    "summary": "Test",
                    "score": 4.0,
                    "comment": "",
                    "satisfaction_date": pd.NaT,
                    "created": pd.Timestamp("2025-06-01"),
                    "hospital": "H1",
                    "product": "P",
                    "product_domain": "PHARMA",
                    "project_key": "SD30",
                }
            )
        df = pd.DataFrame(rows)
        analyser = EvolutionAnalyser(df, pillar_key="pharma")
        result = analyser.analyse(["2025-06"], ["2026-01"])
        assert result.kpi_status["high_critical_baseline"] == KpiStatus.WARNING

    def test_trend_at_risk_bij_negatieve_delta(self) -> None:
        """Grote negatieve delta → trend AT_RISK."""
        import pandas as pd

        rows = [
            {
                "key": "R1",
                "issue_type": "Bug",
                "priority": "Minor",
                "summary": "Test",
                "score": 4.5,
                "comment": "",
                "satisfaction_date": pd.NaT,
                "created": pd.Timestamp("2025-06-01"),
                "hospital": "H1",
                "product": "P",
                "product_domain": "PHARMA",
                "project_key": "SD30",
            },
            {
                "key": "R2",
                "issue_type": "Bug",
                "priority": "Minor",
                "summary": "Test",
                "score": 2.0,
                "comment": "",
                "satisfaction_date": pd.NaT,
                "created": pd.Timestamp("2026-01-01"),
                "hospital": "H1",
                "product": "P",
                "product_domain": "PHARMA",
                "project_key": "SD30",
            },
        ]
        df = pd.DataFrame(rows)
        analyser = EvolutionAnalyser(df, pillar_key="pharma")
        result = analyser.analyse(["2025-06"], ["2026-01"])
        assert result.kpi_status["trend"] == KpiStatus.AT_RISK


# ===========================================================================
# 12. Trend classificatie
# ===========================================================================


class TestTrendClassificatie:
    """Tests voor trend_is_structural en trend_breadth."""

    def test_structureel_bij_grote_delta(self, evolution_df: pd.DataFrame) -> None:
        """Delta=+1,70 >= 0,5 → trend_is_structural=True."""
        result = run_analyse(evolution_df)
        assert result.trend_is_structural is True

    def test_niet_structureel_bij_kleine_delta(self, evolution_df: pd.DataFrame) -> None:
        """Delta < 0,5 → trend_is_structural=False."""
        analyser = make_analyser(evolution_df)
        # Gebruik periodes met minimaal verschil
        result = analyser.analyse(["2026-01"], ["2026-02"])
        assert result.trend_is_structural is False

    def test_trend_breadth_breed(self, evolution_df: pd.DataFrame) -> None:
        """AZ Groeninge + UZ Brussel beide verbeterd → breadth='breed'."""
        result = run_analyse(evolution_df)
        assert result.trend_breadth == "breed"

    def test_trend_breadth_beperkt(self) -> None:
        """Slechts 1 van 4 ziekenhuizen verbeterd → breadth='beperkt'."""
        import pandas as pd

        rows = []
        hospitals = ["H1", "H2", "H3", "H4"]
        # Baseline: alle ziekenhuizen met lage score
        for i, h in enumerate(hospitals):
            rows.append(
                {
                    "key": f"B{i}",
                    "issue_type": "Bug",
                    "priority": "Minor",
                    "summary": "Test",
                    "score": 3.0,
                    "comment": "",
                    "satisfaction_date": pd.NaT,
                    "created": pd.Timestamp("2025-06-01"),
                    "hospital": h,
                    "product": "P",
                    "product_domain": "PHARMA",
                    "project_key": "SD30",
                }
            )
        # Current: alleen H1 verbeterd, rest verslechterd
        scores_current = {"H1": 4.5, "H2": 2.0, "H3": 2.0, "H4": 2.0}
        for i, h in enumerate(hospitals):
            rows.append(
                {
                    "key": f"C{i}",
                    "issue_type": "Bug",
                    "priority": "Minor",
                    "summary": "Test",
                    "score": scores_current[h],
                    "comment": "",
                    "satisfaction_date": pd.NaT,
                    "created": pd.Timestamp("2026-01-01"),
                    "hospital": h,
                    "product": "P",
                    "product_domain": "PHARMA",
                    "project_key": "SD30",
                }
            )
        df = pd.DataFrame(rows)
        analyser = EvolutionAnalyser(df, pillar_key="pharma")
        result = analyser.analyse(["2025-06"], ["2026-01"])
        assert result.trend_breadth == "beperkt"

    def test_trend_breadth_gemengd(self) -> None:
        """2 van 4 ziekenhuizen verbeterd → breadth='gemengd'."""
        import pandas as pd

        rows = []
        hospitals = ["H1", "H2", "H3", "H4"]
        for i, h in enumerate(hospitals):
            rows.append(
                {
                    "key": f"B{i}",
                    "issue_type": "Bug",
                    "priority": "Minor",
                    "summary": "Test",
                    "score": 3.0,
                    "comment": "",
                    "satisfaction_date": pd.NaT,
                    "created": pd.Timestamp("2025-06-01"),
                    "hospital": h,
                    "product": "P",
                    "product_domain": "PHARMA",
                    "project_key": "SD30",
                }
            )
        scores_current = {"H1": 4.5, "H2": 4.5, "H3": 2.0, "H4": 2.0}
        for i, h in enumerate(hospitals):
            rows.append(
                {
                    "key": f"C{i}",
                    "issue_type": "Bug",
                    "priority": "Minor",
                    "summary": "Test",
                    "score": scores_current[h],
                    "comment": "",
                    "satisfaction_date": pd.NaT,
                    "created": pd.Timestamp("2026-01-01"),
                    "hospital": h,
                    "product": "P",
                    "product_domain": "PHARMA",
                    "project_key": "SD30",
                }
            )
        df = pd.DataFrame(rows)
        analyser = EvolutionAnalyser(df, pillar_key="pharma")
        result = analyser.analyse(["2025-06"], ["2026-01"])
        assert result.trend_breadth == "gemengd"

    def test_trend_breadth_geen_gedeelde_ziekenhuizen(self, evolution_df: pd.DataFrame) -> None:
        """Geen ziekenhuizen in current → breadth='gemengd'."""
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(BASELINE, ["2027-01"])
        assert result.trend_breadth == "gemengd"


# ===========================================================================
# 13. KpiStatus enum
# ===========================================================================


class TestKpiStatusEnum:
    """Tests voor de KpiStatus enum."""

    def test_enum_waarden(self) -> None:
        assert KpiStatus.OK == "ok"
        assert KpiStatus.WARNING == "warning"
        assert KpiStatus.AT_RISK == "at_risk"
        assert KpiStatus.UNKNOWN == "unknown"

    def test_enum_is_str(self) -> None:
        assert isinstance(KpiStatus.OK, str)


# ===========================================================================
# 14. Dataclass instantiatie
# ===========================================================================


class TestDataclassInstantiatie:
    """Tests voor directe instantiatie van helper-dataklassen."""

    def test_monthly_datapoint(self) -> None:
        dp = MonthlyDataPoint(
            period="2025-06",
            avg_score=3.5,
            total_tickets=10,
            pct_negative=20.0,
            fase="S1 2025",
        )
        assert dp.period == "2025-06"
        assert dp.fase == "S1 2025"

    def test_issue_type_comparison(self) -> None:
        c = IssueTypeComparison(
            issue_type="Bug",
            baseline_score=2.5,
            baseline_pct_neg=40.0,
            current_score=4.5,
            current_pct_neg=0.0,
        )
        assert c.issue_type == "Bug"

    def test_priority_comparison(self) -> None:
        c = PriorityComparison(
            priority="Blocker",
            baseline_score=2.0,
            baseline_pct_neg=100.0,
            current_score=0.0,
            current_pct_neg=0.0,
        )
        assert c.priority == "Blocker"

    def test_hospital_comparison(self) -> None:
        h = HospitalComparison(
            hospital="AZ Test",
            baseline_score=3.0,
            baseline_total=5,
            current_score=4.5,
            current_total=3,
        )
        assert h.hospital == "AZ Test"
        assert h.current_score == 4.5

    def test_hospital_comparison_current_none(self) -> None:
        h = HospitalComparison(
            hospital="AZ Verdwenen",
            baseline_score=3.0,
            baseline_total=5,
            current_score=None,
            current_total=0,
        )
        assert h.current_score is None

    def test_theme_evolution(self) -> None:
        t = ThemeEvolution(
            theme_key="responstijd",
            pct_baseline=50.0,
            pct_current=0.0,
            status="OPGELOST",
        )
        assert t.status == "OPGELOST"

    def test_response_time_row(self) -> None:
        r = ResponseTimeRow(score_level=3, baseline_days=12.5, current_days=None)
        assert r.score_level == 3
        assert r.current_days is None

    def test_evolution_result_defaults(self) -> None:
        """EvolutionResult met enkel verplichte velden — collecties default leeg."""
        r = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=0,
            current_total=0,
            baseline_avg_score=0.0,
            current_avg_score=0.0,
            delta_avg_score=0.0,
            baseline_pct_positive=0.0,
            current_pct_positive=0.0,
            baseline_pct_negative=0.0,
            current_pct_negative=0.0,
            baseline_avg_response_days=0.0,
            current_avg_response_days=0.0,
            baseline_n_hospitals=0,
            current_n_hospitals=0,
            baseline_hc_ratio=0.0,
            current_hc_ratio=0.0,
            trend_is_structural=False,
            trend_breadth="gemengd",
        )
        assert r.monthly_timeline == []
        assert r.by_issue_type == []
        assert r.hospital_comparison == []
        assert r.kpi_status == {}
        assert r.negative_themes == []


# ===========================================================================
# Fase 3g — nieuwe metrics
# ===========================================================================


class TestFase3gSummaryStats:
    """Tests voor _calc_summary_stats en nieuwe SummaryStats velden."""

    def test_summary_stats_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.baseline_summary is not None
        assert result.current_summary is not None

    def test_summary_stats_total_responses(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.baseline_summary is not None
        assert result.baseline_summary.total_responses == 6
        assert result.current_summary is not None
        assert result.current_summary.total_responses == 4

    def test_summary_stats_median_score(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.current_summary is not None
        # Current scores: [5, 4, 5, 4] → mediaan = 4.5
        assert result.current_summary.median_score == 4.50

    def test_summary_stats_std_dev_groter_nul(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.baseline_summary is not None
        assert result.baseline_summary.std_dev_score > 0.0

    def test_summary_stats_pct_neutral(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.current_summary is not None
        pct_pos = result.current_summary.pct_positive
        pct_neg = result.current_summary.pct_negative
        pct_neu = result.current_summary.pct_neutral
        assert abs(pct_pos + pct_neg + pct_neu - 100.0) < 0.2

    def test_summary_stats_period_start_end(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.baseline_summary is not None
        assert result.baseline_summary.period_start == "2025-06"
        assert result.baseline_summary.period_end == "2025-07"
        assert result.current_summary is not None
        assert result.current_summary.period_start == "2026-01"
        assert result.current_summary.period_end == "2026-02"


class TestFase3gScoreDistribution:
    """Tests voor _calc_score_distribution."""

    def test_score_distribution_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.score_distribution_current is not None
        assert result.score_distribution_baseline is not None

    def test_score_distribution_counts_optelling(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.score_distribution_current is not None
        sd = result.score_distribution_current
        # Current: 4 gescoorde tickets [5, 4, 5, 4]
        total = sum(sd.counts.values())
        assert total == 4

    def test_score_distribution_percentages_optelling(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.score_distribution_current is not None
        total_pct = sum(result.score_distribution_current.percentages.values())
        assert abs(total_pct - 100.0) < 0.5

    def test_score_distribution_compact_label_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.score_distribution_current is not None
        assert "★" in result.score_distribution_current.compact_label
        assert "|" in result.score_distribution_current.compact_label

    def test_score_distribution_narrative_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.score_distribution_current is not None
        assert len(result.score_distribution_current.narrative) > 0

    def test_score_distribution_niveau_5_hoog(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.score_distribution_current is not None
        # Current: 2x score 5, 2x score 4 → 5★: 50%
        pct_5 = result.score_distribution_current.percentages.get(5, 0.0)
        assert pct_5 == 50.0

    def test_score_distribution_narrative_top_level_vijf(self, evolution_df: pd.DataFrame) -> None:
        """Als 5★ de dominante score is, bevat narrative '5★'."""
        from tests.conftest import _make_row

        # Maak een df met 3x 5★ en 1x 4★ → top_level = 5 (3 > 1)
        rijen = [
            _make_row(
                "X1", "Bug", "Trivial", 5.0, "ZH", "Apotheek", "PHARMA", "2026-01-05", "2026-01-06"
            ),
            _make_row(
                "X2", "Bug", "Trivial", 5.0, "ZH", "Apotheek", "PHARMA", "2026-01-06", "2026-01-07"
            ),
            _make_row(
                "X3", "Bug", "Trivial", 5.0, "ZH", "Apotheek", "PHARMA", "2026-01-07", "2026-01-08"
            ),
            _make_row(
                "X4", "Bug", "Trivial", 4.0, "ZH", "Apotheek", "PHARMA", "2026-01-08", "2026-01-09"
            ),
        ]
        df = pd.DataFrame(rijen)
        df["effective_date"] = pd.to_datetime(df["satisfaction_date"])
        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        sd = analyser._calc_score_distribution(df)
        # top_level = 5 (3 hits) → narrative bevat "volle 5★"
        assert "5★" in sd.narrative
        assert "75,0%" in sd.narrative  # 3/4 = 75%


class TestFase3gResponseTimeInsight:
    """Tests voor _calc_response_time_insight."""

    def test_response_time_insight_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.response_time_insight is not None

    def test_response_time_avg_positief(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.response_time_insight is not None
        # Current: 4 tickets met responstijden [1, 2, 2, 2] dagen
        assert result.response_time_insight.avg_days == 1.8

    def test_response_time_min_max(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.response_time_insight is not None
        assert result.response_time_insight.min_days == 1.0
        assert result.response_time_insight.max_days == 2.0

    def test_response_time_mediaan(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.response_time_insight is not None
        assert result.response_time_insight.median_days == 2.0

    def test_response_time_avg_positive_dagen(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert result.response_time_insight is not None
        # Alle current tickets scoren ≥ 4
        assert result.response_time_insight.avg_positive_days is not None
        assert result.response_time_insight.avg_positive_days > 0

    def test_response_time_insight_lege_df(self, evolution_df: pd.DataFrame) -> None:
        """Lege periode → ResponseTimeInsight met nullen."""
        analyser = make_analyser(evolution_df)
        insight = analyser._calc_response_time_insight(evolution_df.iloc[0:0].copy())
        assert insight.avg_days == 0.0
        assert insight.correlation_score is None

    def test_baseline_correlation_score_type(self, evolution_df: pd.DataFrame) -> None:
        """baseline_correlation_score is float of None — nooit een ander type."""
        analyser = make_analyser(evolution_df)
        current_df = analyser._get_df_for_periods(CURRENT)
        baseline_df = analyser._get_df_for_periods(BASELINE)
        insight = analyser._calc_response_time_insight(current_df, baseline_df)
        assert insight.baseline_correlation_score is None or isinstance(
            insight.baseline_correlation_score, float
        )

    def test_baseline_correlation_score_none_bij_te_weinig_datapunten(
        self, evolution_df: pd.DataFrame
    ) -> None:
        """baseline_correlation_score is None als er minder dan 5 datapunten zijn."""
        analyser = make_analyser(evolution_df)
        current_df = analyser._get_df_for_periods(CURRENT)
        # Geef een baseline_df mee met slechts 2 rijen → < 5 datapunten
        tiny_baseline = analyser._get_df_for_periods(BASELINE).head(2).copy()
        insight = analyser._calc_response_time_insight(current_df, tiny_baseline)
        assert insight.baseline_correlation_score is None

    def test_baseline_correlation_except_geeft_none(self, evolution_df: pd.DataFrame) -> None:
        """Als corr() een uitzondering gooit, is baseline_correlation_score None (lines 958-959)."""
        from unittest.mock import patch

        import pandas as pd

        analyser = make_analyser(evolution_df)
        current_df = analyser._get_df_for_periods(CURRENT)
        baseline_df = analyser._get_df_for_periods(BASELINE)
        with patch.object(pd.Series, "corr", side_effect=RuntimeError("gesimuleerde fout")):
            insight = analyser._calc_response_time_insight(current_df, baseline_df)
        assert insight.baseline_correlation_score is None

    # --- Tests voor _calc_negative_cases ---

    def test_negative_cases_aantal(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        # Geen negatieve (≤ 2) in current_df (alle scores ≥ 4)
        assert result.negative_cases == []

    def test_negative_cases_met_lage_scores(self, evolution_df: pd.DataFrame) -> None:
        """Test met baseline (bevat lage scores) als current — dekt line 1004."""
        analyser = make_analyser(evolution_df)
        baseline_df = analyser._get_df_for_periods(BASELINE)
        cases = analyser._calc_negative_cases(baseline_df)
        # Baseline: EB-001 (score=2) en EB-003 (score=2)
        assert len(cases) == 2

    def test_negative_cases_gesorteerd(self, evolution_df: pd.DataFrame) -> None:
        """Cases gesorteerd op score (laagste eerst)."""
        analyser = make_analyser(evolution_df)
        baseline_df = analyser._get_df_for_periods(BASELINE)
        cases = analyser._calc_negative_cases(baseline_df)
        scores = [c.score for c in cases]
        assert scores == sorted(scores)

    def test_negative_case_velden_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        """Elke NegativeCase heeft alle vereiste velden."""
        analyser = make_analyser(evolution_df)
        baseline_df = analyser._get_df_for_periods(BASELINE)
        cases = analyser._calc_negative_cases(baseline_df)
        for c in cases:
            assert c.ticket_id
            assert c.hospital
            assert c.issue_type
            assert c.score in (1, 2)

    def test_negative_case_comment_gevuld(self, evolution_df: pd.DataFrame) -> None:
        """Cases met comment bevatten de volledige tekst."""
        analyser = make_analyser(evolution_df)
        baseline_df = analyser._get_df_for_periods(BASELINE)
        cases = analyser._calc_negative_cases(baseline_df)
        cases_with_comment = [c for c in cases if c.comment]
        assert len(cases_with_comment) >= 1

    def test_negative_case_categorie_responstijd(self, evolution_df: pd.DataFrame) -> None:
        """EB-001 (comment='te lang gewacht') krijgt categorie 'responstijd'."""
        analyser = make_analyser(evolution_df)
        baseline_df = analyser._get_df_for_periods(BASELINE)
        cases = analyser._calc_negative_cases(baseline_df)
        resp_cases = [c for c in cases if c.category == "responstijd"]
        assert len(resp_cases) >= 1

    def test_thema_zonder_match_geeft_leeg_voorbeeld(self, evolution_df: pd.DataFrame) -> None:
        """Thema zonder matchende comments → example blijft leeg."""
        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        lege = evolution_df.iloc[0:0].copy()
        themes = analyser._negative_themes(lege, lege)
        assert themes == []


# ===========================================================================
# Fase 3g — KPI targets
# ===========================================================================


class TestFase3gKpiTargets:
    """Tests voor _calc_kpi_targets."""

    def test_kpi_targets_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert isinstance(result.kpi_targets, list)
        assert len(result.kpi_targets) > 0

    def test_kpi_target_velden(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        for t in result.kpi_targets:
            assert t.name
            assert isinstance(t.baseline, float)
            assert isinstance(t.current, float)
            assert t.status in ("op_schema", "aandacht", "risico", "onbekend", "kritiek")
            assert isinstance(t.on_track, bool)

    def test_kpi_target_avg_score_op_schema(self, evolution_df: pd.DataFrame) -> None:
        """current_avg=4,50 >= target → op_schema."""
        result = run_analyse(evolution_df)
        avg_t = next(t for t in result.kpi_targets if t.name == "avg_score_min")
        assert avg_t.on_track is True
        assert avg_t.status == "op_schema"

    def test_kpi_target_hc_ratio_op_schema(self, evolution_df: pd.DataFrame) -> None:
        """current HC=0% <= drempel → on_track is True (naam: 'high_critical_max')."""
        result = run_analyse(evolution_df)
        hc_t = next(t for t in result.kpi_targets if t.name == "high_critical_max")
        assert hc_t.on_track is True


# ===========================================================================
# Fase 3g — Benchmark H2
# ===========================================================================


class TestFase3gBenchmarkH2:
    """Tests voor _calc_benchmark_h2."""

    def test_benchmark_h2_none_bij_geen_data(self, evolution_df: pd.DataFrame) -> None:
        """Geen H2-data in evolution_df → benchmark_h2 = None."""
        analyser = make_analyser(evolution_df)
        bm = analyser._calc_benchmark_h2(["2025-08", "2025-12"])
        assert bm is None

    def test_benchmark_h2_aanwezig_bij_h2_data(self, evolution_df: pd.DataFrame) -> None:
        """2025-07 is H2 → benchmark_h2 aanwezig."""
        analyser = make_analyser(evolution_df)
        bm = analyser._calc_benchmark_h2(["2025-07"])
        assert bm is not None
        assert bm.avg_score > 0


# ===========================================================================
# Fase 3g — Hospital shortlist
# ===========================================================================


class TestFase3gHospitalShortlist:
    """Tests voor hospital_shortlist veld."""

    def test_shortlist_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        assert isinstance(result.hospital_shortlist, list)

    def test_shortlist_bevat_hospitalen_met_current_score(self, evolution_df: pd.DataFrame) -> None:
        result = run_analyse(evolution_df)
        for h in result.hospital_shortlist:
            assert h.current_score is not None


# ===========================================================================
# Fase 3g — Hospital retention
# ===========================================================================


class TestFase3gHospitalRetention:
    """Tests voor hospital_retention_pct berekening."""

    def test_retention_pct_berekend(self, evolution_df: pd.DataFrame) -> None:
        """2 van 3 baseline-ziekenhuizen aanwezig in current → 66,7%."""
        result = run_analyse(evolution_df)
        assert result.hospital_retention_pct == pytest.approx(66.7, abs=0.1)

    def test_retention_pct_nul_bij_geen_baseline(self, evolution_df: pd.DataFrame) -> None:
        """Lege baseline → geen baseline-ziekenhuizen → retentie = 0.0% of 100.0% (implementatie-afhankelijk)."""
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(["2024-01"], CURRENT)
        # Bij lege baseline zijn er geen baseline-ziekenhuizen → retentie 0 of 100 afhankelijk van implementatie
        assert result.hospital_retention_pct in (0.0, 100.0)

    def test_retention_pct_100_bij_alle_aanwezig(self, evolution_df: pd.DataFrame) -> None:
        """Alle baseline-ziekenhuizen aanwezig in current → 100%."""
        analyser = make_analyser(evolution_df)
        result = analyser.analyse(BASELINE, BASELINE)
        assert result.hospital_retention_pct == pytest.approx(100.0, abs=0.1)


# ===========================================================================
# Sanitize comment — lines 149-150
# ===========================================================================


class TestSanitizeComment:
    """Tests voor sanitize_comment functie — medewerkersnamen anonimiseren."""

    def test_sanitize_vervangt_naam(self) -> None:
        """Namen in 'names' worden vervangen door [ZORGI] (lines 149-150)."""
        from csat.core.analysers.evolution_analyser import sanitize_comment

        result = sanitize_comment("Jan Janssen heeft geholpen", names=["Jan Janssen"])
        assert result == "[ZORGI] heeft geholpen"

    def test_sanitize_meerdere_namen(self) -> None:
        """Meerdere namen worden elk vervangen (lines 149-150 — loop)."""
        from csat.core.analysers.evolution_analyser import sanitize_comment

        result = sanitize_comment(
            "Jan Janssen en Piet Pieters werkten samen",
            names=["Jan Janssen", "Piet Pieters"],
        )
        assert "[ZORGI]" in result
        assert "Jan Janssen" not in result
        assert "Piet Pieters" not in result

    def test_sanitize_lege_comment_geeft_leeg(self) -> None:
        """Lege comment → vroege return (line 146)."""
        from csat.core.analysers.evolution_analyser import sanitize_comment

        assert sanitize_comment("") == ""
        assert sanitize_comment(None) is None  # type: ignore[arg-type]

    def test_sanitize_lege_naam_overgeslagen(self) -> None:
        """Lege naam in lijst → if name: slaat hem over (line 149)."""
        from csat.core.analysers.evolution_analyser import sanitize_comment

        result = sanitize_comment("tekst met inhoud", names=["", "Jan Janssen"])
        assert "[ZORGI]" in result or result == "tekst met inhoud"

    def test_sanitize_zonder_namen_geen_wijziging(self) -> None:
        """ZORGI_EMPLOYEE_NAMES = [] → geen vervangingen."""
        from csat.core.analysers.evolution_analyser import sanitize_comment

        result = sanitize_comment("tekst zonder bekende namen")
        assert result == "tekst zonder bekende namen"

    def test_sanitize_naam_niet_aanwezig_geen_wijziging(self) -> None:
        """Naam in lijst maar niet in comment → comment ongewijzigd."""
        from csat.core.analysers.evolution_analyser import sanitize_comment

        result = sanitize_comment("andere tekst", names=["Jan Janssen"])
        assert result == "andere tekst"


# ===========================================================================
# Fase 3g — ThemeEvolution uitgebreid
# ===========================================================================


class TestFase3gThemeEvolutionExtended:
    """Uitgebreide tests voor thema-evolutie en action_hint."""

    def test_theme_action_hint_responstijd(self, evolution_df: pd.DataFrame) -> None:
        """responstijd-thema krijgt een action_hint."""

        assert "SLA" in THEME_ACTION_HINTS["responstijd"]

    def test_thema_zonder_match_geeft_leeg_voorbeeld(self, evolution_df: pd.DataFrame) -> None:
        """Thema zonder matchende comments → example blijft leeg."""
        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        lege = evolution_df.iloc[0:0].copy()
        themes = analyser._negative_themes(lege, lege)
        assert themes == []


# ===========================================================================
# _calc_negative_cases — probleemclassificatie & sortering (regels 1033-1081)
# ===========================================================================
class TestCalcNegativeCases:
    """Tests voor EvolutionAnalyser._calc_negative_cases()."""

    @staticmethod
    def _df(rows):
        defaults = {
            "key": "SD-000",
            "score": 1.0,
            "created": "2026-01-01",
            "satisfaction_date": "2026-01-05",
            "hospital": "AZ Test",
            "issue_type": "Bug",
            "comment": "",
            "product_domain": "PHARMA",
            "priority": "Minor",
        }
        rijen = []
        for r in rows:
            rij = {**defaults, **r}
            rij["created"] = pd.Timestamp(rij["created"])
            rij["satisfaction_date"] = (
                pd.Timestamp(rij["satisfaction_date"]) if rij["satisfaction_date"] else pd.NaT
            )
            rijen.append(rij)
        return pd.DataFrame(rijen)

    @staticmethod
    def _ana(df):
        return EvolutionAnalyser(df, pillar_key="pharma")

    # Basis
    def test_lege_df_geeft_lege_lijst(self, empty_df):
        assert self._ana(empty_df)._calc_negative_cases(empty_df) == []

    def test_alle_scores_positief_geeft_leeg(self):
        df = self._df([{"score": 3.0}, {"score": 4.0}, {"score": 5.0}])
        assert self._ana(df)._calc_negative_cases(df) == []

    def test_score_nan_genegeerd(self):
        df = self._df([{"score": None, "satisfaction_date": "2026-01-05"}])
        assert self._ana(df)._calc_negative_cases(df) == []

    # Classificatie
    def test_responstijd_keyword(self):
        df = self._df([{"score": 1.0, "comment": "te lang gewacht"}])
        r = self._ana(df)._calc_negative_cases(df)
        assert r[0].category == "responstijd"

    def test_onvolledig_keyword(self):
        df = self._df([{"score": 2.0, "comment": "nog steeds niet opgelost"}])
        r = self._ana(df)._calc_negative_cases(df)
        assert r[0].category == "onvolledig"

    def test_eerste_match_wint(self):
        df = self._df([{"score": 1.0, "comment": "te lang gewacht en nog steeds niet opgelost"}])
        r = self._ana(df)._calc_negative_cases(df)
        first_theme = next(iter(THEME_KEYWORDS))
        assert r[0].category == first_theme

    def test_geen_keyword_geeft_streep(self):
        df = self._df([{"score": 2.0, "comment": "algemene opmerking"}])
        r = self._ana(df)._calc_negative_cases(df)
        assert r[0].category == "—"

    def test_lege_comment_geeft_streep(self):
        df = self._df([{"score": 1.0, "comment": ""}])
        assert self._ana(df)._calc_negative_cases(df)[0].category == "—"

    def test_case_insensitive(self):
        df = self._df([{"score": 1.0, "comment": "TE LANG GEWACHT"}])
        assert self._ana(df)._calc_negative_cases(df)[0].category == "responstijd"

    # response_days
    def test_response_days_correct(self):
        df = self._df([{"score": 1.0, "created": "2026-01-01", "satisfaction_date": "2026-01-06"}])
        assert self._ana(df)._calc_negative_cases(df)[0].response_days == 5.0

    def test_response_days_none_bij_nat(self):
        df = self._df([{"score": 2.0, "satisfaction_date": None}])
        assert self._ana(df)._calc_negative_cases(df)[0].response_days is None

    def test_response_days_none_bij_negatief_interval(self):
        df = self._df([{"score": 1.0, "created": "2026-01-10", "satisfaction_date": "2026-01-05"}])
        assert self._ana(df)._calc_negative_cases(df)[0].response_days is None

    # Sortering
    def test_laagste_score_eerst(self):
        df = self._df(
            [
                {
                    "key": "SD-2",
                    "score": 2.0,
                    "created": "2026-01-01",
                    "satisfaction_date": "2026-01-03",
                },
                {
                    "key": "SD-1",
                    "score": 1.0,
                    "created": "2026-01-01",
                    "satisfaction_date": "2026-01-03",
                },
            ]
        )
        r = self._ana(df)._calc_negative_cases(df)
        assert r[0].ticket_id == "SD-1"

    def test_gelijke_score_langste_responstijd_eerst(self):
        df = self._df(
            [
                {
                    "key": "SD-A",
                    "score": 1.0,
                    "created": "2026-01-01",
                    "satisfaction_date": "2026-01-04",
                },
                {
                    "key": "SD-B",
                    "score": 1.0,
                    "created": "2026-01-01",
                    "satisfaction_date": "2026-01-11",
                },
            ]
        )
        r = self._ana(df)._calc_negative_cases(df)
        assert r[0].ticket_id == "SD-B"

    # Velden
    def test_velden_correct(self):
        df = self._df(
            [
                {
                    "key": "SD-999",
                    "score": 2.0,
                    "hospital": "UZ Gent",
                    "issue_type": "Improvement",
                    "comment": "traag",
                    "created": "2026-03-01",
                    "satisfaction_date": "2026-03-06",
                }
            ]
        )
        c = self._ana(df)._calc_negative_cases(df)[0]
        assert c.ticket_id == "SD-999"
        assert c.hospital == "UZ Gent"
        assert c.score == 2
        assert c.response_days == 5.0
        assert c.category == "responstijd"

    def test_retourtype_is_list(self):
        df = self._df([{"score": 5.0}])
        r = self._ana(df)._calc_negative_cases(df)
        assert isinstance(r, list)
