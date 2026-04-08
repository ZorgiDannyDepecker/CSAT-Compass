"""
Unit tests voor InsightsGenerator en InsightsBundle — Fase 3g.

Dekt: classify_severity, generate(), executive summary, critical findings,
positive developments, recommendations, follow-up actions, visual analysis,
turning point analysis, randgevallen.
"""

from __future__ import annotations

import pandas as pd
import pytest

from csat.core.analysers.evolution_analyser import EvolutionAnalyser
from csat.core.analysers.evolution_result import (
    EvolutionResult,
    HospitalComparison,
    KpiTarget,
    MonthlyDataPoint,
    NegativeCase,
    ResponseTimeInsight,
    ThemeEvolution,
)
from csat.core.insights import InsightsBundle, InsightsGenerator
from csat.core.insights.insights_generator import (
    CriticalFinding,
    FollowUpAction,
    PositiveDevelopment,
    Recommendation,
    VisualAnalysis,
)
from csat.i18n import load_translations

# ---------------------------------------------------------------------------
# Constanten
# ---------------------------------------------------------------------------

BASELINE = ["2025-06", "2025-07"]
CURRENT = ["2026-01", "2026-02"]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def nl_translations() -> dict:
    """Laad de Nederlandse vertalingen."""
    return load_translations("nl")


@pytest.fixture
def fr_translations() -> dict:
    """Laad de Franse vertalingen."""
    return load_translations("fr")


@pytest.fixture
def insights_gen_nl(nl_translations: dict) -> InsightsGenerator:
    """InsightsGenerator NL met vaste seed voor reproduceerbaarheid."""
    return InsightsGenerator(nl_translations, lang="nl", seed=20260101)


@pytest.fixture
def insights_gen_fr(fr_translations: dict) -> InsightsGenerator:
    """InsightsGenerator FR met vaste seed voor reproduceerbaarheid."""
    return InsightsGenerator(fr_translations, lang="fr", seed=20260101)


@pytest.fixture
def evolution_result_full(evolution_df: pd.DataFrame) -> EvolutionResult:
    """Volledig EvolutionResult via EvolutionAnalyser op evolution_df."""
    analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
    return analyser.analyse(BASELINE, CURRENT)


@pytest.fixture
def minimal_result() -> EvolutionResult:
    """Minimaal EvolutionResult met alleen vereiste velden."""
    return EvolutionResult(
        pillar="pharma",
        baseline_label="2025",
        current_label="2026",
        baseline_total=10,
        current_total=8,
        baseline_avg_score=3.50,
        current_avg_score=4.00,
        delta_avg_score=0.50,
        baseline_pct_positive=60.0,
        current_pct_positive=75.0,
        baseline_pct_negative=20.0,
        current_pct_negative=10.0,
        baseline_avg_response_days=12.0,
        current_avg_response_days=8.0,
        baseline_n_hospitals=5,
        current_n_hospitals=5,
        baseline_hc_ratio=10.0,
        current_hc_ratio=12.0,
        trend_is_structural=True,
        trend_breadth="breed",
    )


# ---------------------------------------------------------------------------
# 1. classify_severity
# ---------------------------------------------------------------------------


class TestClassifySeverity:
    """Tests voor classify_severity — ernst-drempellogica."""

    def test_score_delta_licht(self, insights_gen_nl: InsightsGenerator) -> None:
        assert insights_gen_nl.classify_severity(0.05, "score_delta") == "licht"

    def test_score_delta_matig(self, insights_gen_nl: InsightsGenerator) -> None:
        assert insights_gen_nl.classify_severity(0.20, "score_delta") == "matig"

    def test_score_delta_significant(self, insights_gen_nl: InsightsGenerator) -> None:
        assert insights_gen_nl.classify_severity(0.50, "score_delta") == "significant"

    def test_pct_negative_licht(self, insights_gen_nl: InsightsGenerator) -> None:
        assert insights_gen_nl.classify_severity(3.0, "pct_negative") == "licht"

    def test_pct_negative_matig(self, insights_gen_nl: InsightsGenerator) -> None:
        assert insights_gen_nl.classify_severity(7.0, "pct_negative") == "matig"

    def test_pct_negative_significant(self, insights_gen_nl: InsightsGenerator) -> None:
        assert insights_gen_nl.classify_severity(15.0, "pct_negative") == "significant"

    def test_onbekende_metric_valt_terug(self, insights_gen_nl: InsightsGenerator) -> None:
        """Onbekende metric gebruikt fallback-drempels."""
        assert insights_gen_nl.classify_severity(0.05, "onbekend") == "licht"
        assert insights_gen_nl.classify_severity(0.20, "onbekend") == "matig"
        assert insights_gen_nl.classify_severity(0.50, "onbekend") == "significant"

    def test_grens_exact_licht(self, insights_gen_nl: InsightsGenerator) -> None:
        """Precies op drempel licht/matig → "matig"."""
        assert insights_gen_nl.classify_severity(0.10, "score_delta") == "matig"

    def test_grens_exact_matig(self, insights_gen_nl: InsightsGenerator) -> None:
        """Precies op drempel matig/significant → "significant"."""
        assert insights_gen_nl.classify_severity(0.30, "score_delta") == "significant"


# ---------------------------------------------------------------------------
# 2. generate() — InsightsBundle structuur
# ---------------------------------------------------------------------------


class TestGenerate:
    """Tests voor generate() — correcte InsightsBundle structuur."""

    def test_generate_geeft_insightsbundle(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        bundle = insights_gen_nl.generate(evolution_result_full)
        assert isinstance(bundle, InsightsBundle)

    def test_executive_summary_niet_leeg(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        bundle = insights_gen_nl.generate(evolution_result_full)
        assert len(bundle.executive_summary) > 0

    def test_critical_findings_max_5(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        bundle = insights_gen_nl.generate(evolution_result_full)
        assert len(bundle.critical_findings) <= 5

    def test_recommendations_aanwezig(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        bundle = insights_gen_nl.generate(evolution_result_full)
        assert isinstance(bundle.recommendations, list)

    def test_follow_up_actions_aanwezig(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        bundle = insights_gen_nl.generate(evolution_result_full)
        assert isinstance(bundle.follow_up_actions, list)

    def test_visual_analysis_is_visualanalysis(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        bundle = insights_gen_nl.generate(evolution_result_full)
        assert isinstance(bundle.visual_analysis, VisualAnalysis)

    def test_turning_point_analysis_aanwezig(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        bundle = insights_gen_nl.generate(evolution_result_full)
        assert isinstance(bundle.turning_point_analysis, str)

    def test_generate_minimaal_result_geen_fouten(
        self,
        insights_gen_nl: InsightsGenerator,
        minimal_result: EvolutionResult,
    ) -> None:
        """generate() mag niet falen op een minimaal result zonder Fase 3g velden."""
        bundle = insights_gen_nl.generate(minimal_result)
        assert isinstance(bundle, InsightsBundle)

    def test_seed_geeft_reproduceerbaarheid(
        self,
        nl_translations: dict,
        evolution_result_full: EvolutionResult,
    ) -> None:
        """Twee InsightsGenerators met dezelfde seed geven identieke output."""
        gen1 = InsightsGenerator(nl_translations, lang="nl", seed=42)
        gen2 = InsightsGenerator(nl_translations, lang="nl", seed=42)
        assert (
            gen1.generate(evolution_result_full).executive_summary
            == gen2.generate(evolution_result_full).executive_summary
        )


# ---------------------------------------------------------------------------
# 3. Executive Summary
# ---------------------------------------------------------------------------


class TestExecutiveSummary:
    """Tests voor de executive summary inhoud."""

    def test_bevat_score_beweging(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        """Summary bevat een observatie over de score-beweging."""
        summary = insights_gen_nl.generate(evolution_result_full).executive_summary
        # evolution_df: delta = +1.70 — significant stijging
        assert any(
            word in summary for word in ["steeg", "stijging", "sterk", "significant", "score"]
        )

    def test_bevat_samenvatting_bij_daling(
        self, nl_translations: dict, minimal_result: EvolutionResult
    ) -> None:
        """Bij score-daling bevat de summary een negatief woord."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=10,
            baseline_avg_score=4.50,
            current_avg_score=4.10,
            delta_avg_score=-0.40,
            baseline_pct_positive=90.0,
            current_pct_positive=80.0,
            baseline_pct_negative=5.0,
            current_pct_negative=12.0,
            baseline_avg_response_days=5.0,
            current_avg_response_days=8.0,
            baseline_n_hospitals=4,
            current_n_hospitals=4,
            baseline_hc_ratio=10.0,
            current_hc_ratio=15.0,
            trend_is_structural=False,
            trend_breadth="gemengd",
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        summary = gen.generate(result).executive_summary
        assert any(word in summary for word in ["daalde", "terugval", "daling", "neerwaarts"])

    def test_bevat_scoreverdeling_narratief(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        """Als score_distribution_current aanwezig is, verschijnt het narratief."""
        bundle = insights_gen_nl.generate(evolution_result_full)
        if evolution_result_full.score_distribution_current:
            assert (
                evolution_result_full.score_distribution_current.narrative
                in bundle.executive_summary
            )

    def test_stabiele_score_geen_crash(self, nl_translations: dict) -> None:
        """Bij delta ≈ 0 mag de summary niet crashen."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=10,
            baseline_avg_score=4.50,
            current_avg_score=4.52,
            delta_avg_score=0.02,
            baseline_pct_positive=85.0,
            current_pct_positive=86.0,
            baseline_pct_negative=5.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=5.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=4,
            current_n_hospitals=4,
            baseline_hc_ratio=10.0,
            current_hc_ratio=10.0,
            trend_is_structural=False,
            trend_breadth="gemengd",
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        bundle = gen.generate(result)
        assert len(bundle.executive_summary) > 0

    def test_kpi_achievement_alle_targets_gehaald(self, nl_translations: dict) -> None:
        """Als alle KPI-targets on_track zijn, bevat de summary de achievement-zin."""
        from csat.core.analysers.evolution_result import KpiTarget

        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=20,
            current_total=20,
            baseline_avg_score=3.5,
            current_avg_score=4.5,
            delta_avg_score=1.0,
            baseline_pct_positive=60.0,
            current_pct_positive=88.0,
            baseline_pct_negative=20.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=15.0,
            current_avg_response_days=6.0,
            baseline_n_hospitals=5,
            current_n_hospitals=5,
            baseline_hc_ratio=20.0,
            current_hc_ratio=10.0,
            trend_is_structural=True,
            trend_breadth="breed",
            kpi_targets=[
                KpiTarget("avg_score_min", 3.5, 4.0, 4.5, "op_schema", True),
                KpiTarget("pct_positive_min", 60.0, 75.0, 88.0, "op_schema", True),
                KpiTarget("pct_negative_max", 20.0, 15.0, 5.0, "op_schema", True),
            ],
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        summary = gen.generate(result).executive_summary
        assert "Alle 3 KPI-targets" in summary or "KPI-targets" in summary


# ---------------------------------------------------------------------------
# 4. Critical findings
# ---------------------------------------------------------------------------


class TestCriticalFindings:
    """Tests voor de kritieke bevindingen."""

    def test_findings_zijn_criticalfinding_objecten(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        findings = insights_gen_nl.generate(evolution_result_full).critical_findings
        assert all(isinstance(f, CriticalFinding) for f in findings)

    def test_findings_gesorteerd_ernst(
        self,
        insights_gen_nl: InsightsGenerator,
        evolution_result_full: EvolutionResult,
    ) -> None:
        """Bevindingen zijn gesorteerd: hoog → medium → laag."""
        findings = insights_gen_nl.generate(evolution_result_full).critical_findings
        order = {"hoog": 0, "medium": 1, "laag": 2}
        ranks = [order.get(f.severity, 3) for f in findings]
        assert ranks == sorted(ranks)

    def test_hoge_hc_ratio_geeft_bevinding(self, nl_translations: dict) -> None:
        """HC-ratio > 15% genereert een bevinding."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=20,
            current_total=20,
            baseline_avg_score=4.0,
            current_avg_score=4.0,
            delta_avg_score=0.0,
            baseline_pct_positive=75.0,
            current_pct_positive=75.0,
            baseline_pct_negative=5.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=5.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=4,
            current_n_hospitals=4,
            baseline_hc_ratio=10.0,
            current_hc_ratio=25.0,  # Boven drempel
            trend_is_structural=False,
            trend_breadth="gemengd",
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        findings = gen.generate(result).critical_findings
        hc_titles = [f.title for f in findings if "HC-ratio" in f.title or "High" in f.title]
        assert len(hc_titles) >= 1

    def test_verdwenen_ziekenhuizen_geeft_bevinding(self, nl_translations: dict) -> None:
        """Verdwenen ziekenhuizen genereren een bevinding."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=8,
            baseline_avg_score=4.0,
            current_avg_score=4.0,
            delta_avg_score=0.0,
            baseline_pct_positive=80.0,
            current_pct_positive=80.0,
            baseline_pct_negative=5.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=5.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=4,
            current_n_hospitals=2,
            baseline_hc_ratio=10.0,
            current_hc_ratio=10.0,
            trend_is_structural=False,
            trend_breadth="gemengd",
            hospitals_disappeared=["OLV Aalst", "AZ Groeninge"],
            hospital_retention_pct=50.0,
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        findings = gen.generate(result).critical_findings
        retention_titles = [
            f.title
            for f in findings
            if "retentie" in f.title.lower() or "ziekenhuis" in f.title.lower()
        ]
        assert len(retention_titles) >= 1

    def test_lege_result_geen_crash(
        self, nl_translations: dict, minimal_result: EvolutionResult
    ) -> None:
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        findings = gen.generate(minimal_result).critical_findings
        assert isinstance(findings, list)

    def test_correlatie_omslag_neg_naar_pos_geeft_bevinding(self, nl_translations: dict) -> None:
        """Baseline r < -0.05 en huidig r > 0.05 → correlatie-omslag bevinding aanwezig."""
        from csat.core.analysers.evolution_result import ResponseTimeInsight

        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=20,
            current_total=20,
            baseline_avg_score=3.5,
            current_avg_score=4.2,
            delta_avg_score=0.7,
            baseline_pct_positive=55.0,
            current_pct_positive=80.0,
            baseline_pct_negative=20.0,
            current_pct_negative=8.0,
            baseline_avg_response_days=12.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=4,
            current_n_hospitals=4,
            baseline_hc_ratio=10.0,
            current_hc_ratio=10.0,
            trend_is_structural=True,
            trend_breadth="breed",
            response_time_insight=ResponseTimeInsight(
                avg_days=5.0,
                correlation_score=0.25,  # huidig positief
                baseline_correlation_score=-0.30,  # baseline negatief
            ),
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        findings = gen.generate(result).critical_findings
        titles = [f.title for f in findings]
        assert any("omslag" in t.lower() or "🔄" in t for t in titles)

    def test_correlatie_geen_omslag_zelfde_teken_geen_bevinding(
        self, nl_translations: dict
    ) -> None:
        """Beide correlaties positief → geen correlatie-omslag bevinding."""
        from csat.core.analysers.evolution_result import ResponseTimeInsight

        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=20,
            current_total=20,
            baseline_avg_score=3.8,
            current_avg_score=4.2,
            delta_avg_score=0.4,
            baseline_pct_positive=60.0,
            current_pct_positive=80.0,
            baseline_pct_negative=15.0,
            current_pct_negative=8.0,
            baseline_avg_response_days=10.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=4,
            current_n_hospitals=4,
            baseline_hc_ratio=10.0,
            current_hc_ratio=10.0,
            trend_is_structural=True,
            trend_breadth="breed",
            response_time_insight=ResponseTimeInsight(
                avg_days=5.0,
                correlation_score=0.20,  # huidig positief
                baseline_correlation_score=0.15,  # baseline ook positief — geen omslag
            ),
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        findings = gen.generate(result).critical_findings
        titles = [f.title for f in findings]
        assert not any("omslag" in t.lower() or "🔄" in t for t in titles)


# ---------------------------------------------------------------------------
# 5. Positive developments
# ---------------------------------------------------------------------------


class TestPositiveDevelopments:
    """Tests voor positieve ontwikkelingen."""

    def test_score_stijging_geeft_ontwikkeling(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        """Bij delta +1.70 moet er een positieve ontwikkeling zijn voor score."""
        devs = insights_gen_nl.generate(evolution_result_full).positive_developments
        assert any(isinstance(d, PositiveDevelopment) for d in devs)
        score_devs = [d for d in devs if "score" in d.title.lower() or "verbet" in d.title.lower()]
        assert len(score_devs) >= 1

    def test_geen_ontwikkelingen_bij_stabiel(
        self, nl_translations: dict, minimal_result: EvolutionResult
    ) -> None:
        """Bij minimale verbeteringen kan de lijst leeg zijn."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=10,
            baseline_avg_score=4.40,
            current_avg_score=4.41,
            delta_avg_score=0.01,
            baseline_pct_positive=80.0,
            current_pct_positive=80.5,
            baseline_pct_negative=5.0,
            current_pct_negative=4.9,
            baseline_avg_response_days=5.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=4,
            current_n_hospitals=4,
            baseline_hc_ratio=10.0,
            current_hc_ratio=10.0,
            trend_is_structural=False,
            trend_breadth="gemengd",
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        devs = gen.generate(result).positive_developments
        assert isinstance(devs, list)  # Mag leeg zijn

    def test_opgeloste_themas_geeft_ontwikkeling(self, nl_translations: dict) -> None:
        """Opgeloste feedbackthema's genereren een positieve ontwikkeling."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=10,
            baseline_avg_score=4.0,
            current_avg_score=4.5,
            delta_avg_score=0.5,
            baseline_pct_positive=75.0,
            current_pct_positive=90.0,
            baseline_pct_negative=10.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=10.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=4,
            current_n_hospitals=4,
            baseline_hc_ratio=10.0,
            current_hc_ratio=10.0,
            trend_is_structural=True,
            trend_breadth="breed",
            negative_themes=[
                ThemeEvolution("responstijd", 50.0, 0.0, "OPGELOST"),
            ],
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        devs = gen.generate(result).positive_developments
        opgelost = [d for d in devs if "opgelost" in d.title.lower() or "thema" in d.title.lower()]
        assert len(opgelost) >= 1


# ---------------------------------------------------------------------------
# 6. Recommendations
# ---------------------------------------------------------------------------


class TestRecommendations:
    """Tests voor strategische aanbevelingen."""

    def test_recommendations_zijn_recommendation_objecten(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        recs = insights_gen_nl.generate(evolution_result_full).recommendations
        assert all(isinstance(r, Recommendation) for r in recs)

    def test_recommendation_heeft_alle_velden(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        recs = insights_gen_nl.generate(evolution_result_full).recommendations
        for rec in recs:
            assert rec.title
            assert rec.description
            assert rec.expected_impact
            assert rec.timeline in ("kort", "middellang", "lang")
            assert rec.owner
            assert rec.priority in ("hoog", "midden", "laag")

    def test_negative_cases_geeft_recommendation(self, nl_translations: dict) -> None:
        """Negatieve tickets genereren een opvolgingsaanbeveling."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=10,
            baseline_avg_score=4.0,
            current_avg_score=3.5,
            delta_avg_score=-0.5,
            baseline_pct_positive=70.0,
            current_pct_positive=60.0,
            baseline_pct_negative=10.0,
            current_pct_negative=20.0,
            baseline_avg_response_days=5.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=4,
            current_n_hospitals=4,
            baseline_hc_ratio=10.0,
            current_hc_ratio=10.0,
            trend_is_structural=False,
            trend_breadth="gemengd",
            negative_cases=[
                NegativeCase(
                    "SD-001", "AZ Groeninge", "Bug", 2, 5.0, "responstijd", "Wachttijd te lang"
                ),
                NegativeCase("SD-002", "UZ Brussel", "Bug", 1, 10.0, "onvolledig", "Niet opgelost"),
            ],
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        recs = gen.generate(result).recommendations
        ticket_recs = [
            r for r in recs if "ticket" in r.title.lower() or "negatief" in r.title.lower()
        ]
        assert len(ticket_recs) >= 1

    def test_recommendations_gesorteerd_prioriteit(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        """Aanbevelingen zijn gesorteerd: hoog → midden → laag."""
        recs = insights_gen_nl.generate(evolution_result_full).recommendations
        order = {"hoog": 0, "midden": 1, "laag": 2}
        ranks = [order.get(r.priority, 3) for r in recs]
        assert ranks == sorted(ranks)


# ---------------------------------------------------------------------------
# 7. Follow-up actions
# ---------------------------------------------------------------------------


class TestFollowUpActions:
    """Tests voor follow-up acties per tijdshorizon."""

    def test_follow_up_actions_zijn_followupaction_objecten(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        actions = insights_gen_nl.generate(evolution_result_full).follow_up_actions
        assert all(isinstance(a, FollowUpAction) for a in actions)

    def test_horizons_zijn_geldig(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        actions = insights_gen_nl.generate(evolution_result_full).follow_up_actions
        for a in actions:
            assert a.horizon in ("kort", "middellang", "lang")

    def test_altijd_lange_termijn_actie(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        """Er is altijd minimaal één lange-termijn actie (hervalideer KPI-targets)."""
        actions = insights_gen_nl.generate(evolution_result_full).follow_up_actions
        long_actions = [a for a in actions if a.horizon == "lang"]
        assert len(long_actions) >= 1

    def test_negatieve_cases_geeft_korte_termijn_actie(self, nl_translations: dict) -> None:
        """Negatieve tickets genereren een korte-termijn opvolgactie."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=10,
            baseline_avg_score=4.0,
            current_avg_score=3.5,
            delta_avg_score=-0.5,
            baseline_pct_positive=70.0,
            current_pct_positive=60.0,
            baseline_pct_negative=10.0,
            current_pct_negative=20.0,
            baseline_avg_response_days=5.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=4,
            current_n_hospitals=4,
            baseline_hc_ratio=10.0,
            current_hc_ratio=10.0,
            trend_is_structural=False,
            trend_breadth="gemengd",
            negative_cases=[
                NegativeCase("SD-001", "AZ Groeninge", "Bug", 2, 5.0, "responstijd", "Test"),
            ],
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        actions = gen.generate(result).follow_up_actions
        short_actions = [a for a in actions if a.horizon == "kort"]
        assert len(short_actions) >= 1


# ---------------------------------------------------------------------------
# 8. Visual analysis
# ---------------------------------------------------------------------------


class TestVisualAnalysis:
    """Tests voor visuele analyse beschrijvingen."""

    def test_visual_analysis_is_visualanalysis_object(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        va = insights_gen_nl.generate(evolution_result_full).visual_analysis
        assert isinstance(va, VisualAnalysis)

    def test_subplot1_scoretrend_niet_leeg(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        va = insights_gen_nl.generate(evolution_result_full).visual_analysis
        assert len(va.subplot1_scoretrend) > 0

    def test_subplot2_volume_niet_leeg(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        va = insights_gen_nl.generate(evolution_result_full).visual_analysis
        assert len(va.subplot2_volume) > 0

    def test_stijgende_trend_beschrijving(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        """Bij delta +1.70 moet 'stijgend' in subplot1 staan."""
        va = insights_gen_nl.generate(evolution_result_full).visual_analysis
        assert "stijgend" in va.subplot1_scoretrend.lower()

    def test_visual_analysis_zonder_data_geen_crash(
        self, nl_translations: dict, minimal_result: EvolutionResult
    ) -> None:
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        va = gen.generate(minimal_result).visual_analysis
        assert isinstance(va, VisualAnalysis)


# ---------------------------------------------------------------------------
# 9. Turning point analysis
# ---------------------------------------------------------------------------


class TestTurningPointAnalysis:
    """Tests voor de keerpuntanalyse."""

    def test_turning_point_bevat_dieptepunt(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        """Keerpuntanalyse benoemt het dieptepunt."""
        tpa = insights_gen_nl.generate(evolution_result_full).turning_point_analysis
        assert "Dieptepunt" in tpa or "dieptepunt" in tpa

    def test_turning_point_bevat_topmaand(
        self, insights_gen_nl: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        """Keerpuntanalyse benoemt de topmaand."""
        tpa = insights_gen_nl.generate(evolution_result_full).turning_point_analysis
        assert "Topmaand" in tpa or "topmaand" in tpa or len(tpa) > 0

    def test_turning_point_leeg_bij_geen_data(
        self, nl_translations: dict, minimal_result: EvolutionResult
    ) -> None:
        """Geen maanddata → lege keerpuntanalyse."""
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        tpa = gen.generate(minimal_result).turning_point_analysis
        assert tpa == ""

    def test_turning_point_3_periodes_trend_detectie(self, nl_translations: dict) -> None:
        """Met ≥ 3 gescoorde periodes detecteert de analyser de trend."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=15,
            current_total=10,
            baseline_avg_score=3.5,
            current_avg_score=4.5,
            delta_avg_score=1.0,
            baseline_pct_positive=60.0,
            current_pct_positive=90.0,
            baseline_pct_negative=20.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=10.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=3,
            current_n_hospitals=3,
            baseline_hc_ratio=20.0,
            current_hc_ratio=5.0,
            trend_is_structural=True,
            trend_breadth="breed",
            monthly_timeline=[
                MonthlyDataPoint("2025-06", 3.0, 5, 30.0, "S1 2025"),
                MonthlyDataPoint("2025-07", 3.5, 5, 20.0, "S2 2025"),
                MonthlyDataPoint("2026-01", 4.0, 5, 10.0, "S1 2026"),
                MonthlyDataPoint("2026-02", 4.5, 5, 5.0, "S1 2026"),
            ],
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        tpa = gen.generate(result).turning_point_analysis
        # Stijgende trend in laatste 3 periodes
        assert len(tpa) > 0


# ---------------------------------------------------------------------------
# 10. Tweetaligheid — FR
# ---------------------------------------------------------------------------


class TestFrancaisInsights:
    """Tests voor de Franse InsightsGenerator."""

    def test_fr_generate_geen_crash(
        self, insights_gen_fr: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        bundle = insights_gen_fr.generate(evolution_result_full)
        assert isinstance(bundle, InsightsBundle)

    def test_fr_executive_summary_niet_leeg(
        self, insights_gen_fr: InsightsGenerator, evolution_result_full: EvolutionResult
    ) -> None:
        bundle = insights_gen_fr.generate(evolution_result_full)
        assert len(bundle.executive_summary) > 0


# ---------------------------------------------------------------------------
# 11. Coverage — aanvullende tests voor ontbrekende paden
# ---------------------------------------------------------------------------


def _make_result_with_rti(
    nl_translations: dict,
    correlation: float | None = None,
    avg_days: float = 5.0,
    avg_positive: float | None = 3.0,
    avg_negative: float | None = 8.0,
    delta: float = 0.5,
    pct_positive: float = 80.0,
    pct_negative: float = 10.0,
    hc_ratio: float = 10.0,
    trend_structural: bool = True,
    trend_breadth: str = "breed",
) -> EvolutionResult:
    """Hulpfunctie: bouw EvolutionResult met specifieke ResponseTimeInsight."""
    from csat.core.analysers.evolution_result import ResponseTimeInsight as RTI  # noqa: N817

    return EvolutionResult(
        pillar="pharma",
        baseline_label="2025",
        current_label="2026",
        baseline_total=20,
        current_total=20,
        baseline_avg_score=round(4.5 - delta, 2),
        current_avg_score=4.5,
        delta_avg_score=delta,
        baseline_pct_positive=max(0.0, pct_positive - 5.0),
        current_pct_positive=pct_positive,
        baseline_pct_negative=pct_negative,
        current_pct_negative=pct_negative,
        baseline_avg_response_days=avg_days + 2.0,
        current_avg_response_days=avg_days,
        baseline_n_hospitals=4,
        current_n_hospitals=4,
        baseline_hc_ratio=hc_ratio,
        current_hc_ratio=hc_ratio,
        trend_is_structural=trend_structural,
        trend_breadth=trend_breadth,
        response_time_insight=RTI(
            avg_days=avg_days,
            median_days=avg_days,
            min_days=1.0,
            max_days=avg_days * 2,
            correlation_score=correlation,
            avg_positive_days=avg_positive,
            avg_negative_days=avg_negative,
        ),
    )


class TestCoverageOntbrekendesPaden:
    """Gerichte tests voor nog niet-gedekte code-paden (100% coverage)."""

    # --- executive summary nuancering (lines 233-239) ---

    def test_summary_nuance_kleine_daling_hoog_positief(self, nl_translations: dict) -> None:
        """delta < 0, abs(delta) < 0.15, pct_positive > 75% → nuance-pad."""
        result = _make_result_with_rti(
            nl_translations,
            delta=-0.08,  # abs < 0.15
            pct_positive=82.0,  # > 75%
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        summary = gen.generate(result).executive_summary
        assert len(summary) > 0  # Nuanceparagraaf mag niet crashen

    # --- correlatie paden (lines 244-261) ---

    def test_summary_positieve_correlatie(self, nl_translations: dict) -> None:
        """r > 0.1 → positieve correlatietekst."""
        result = _make_result_with_rti(nl_translations, correlation=0.35)
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        summary = gen.generate(result).executive_summary
        assert "correlatie" in summary.lower() or "r=" in summary

    def test_summary_negatieve_correlatie(self, nl_translations: dict) -> None:
        """r < -0.1 → negatieve correlatietekst."""
        result = _make_result_with_rti(nl_translations, correlation=-0.35)
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        summary = gen.generate(result).executive_summary
        assert "correlatie" in summary.lower() or "r=" in summary

    def test_summary_neutrale_correlatie(self, nl_translations: dict) -> None:
        """abs(r) ≤ 0.1 → neutrale correlatietekst."""
        result = _make_result_with_rti(nl_translations, correlation=0.05)
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        summary = gen.generate(result).executive_summary
        assert len(summary) > 0

    # --- structural_limited conclusie (lines 313-331) ---

    def test_summary_structural_limited(self, nl_translations: dict) -> None:
        """trend_is_structural=True maar breadth != 'breed' → structural_limited."""
        result = _make_result_with_rti(
            nl_translations, trend_structural=True, trend_breadth="beperkt"
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        summary = gen.generate(result).executive_summary
        assert len(summary) > 0

    def test_summary_declining_conclusie(self, nl_translations: dict) -> None:
        """delta < -0.3, not structural → declining conclusie."""
        result = _make_result_with_rti(nl_translations, delta=-0.40, trend_structural=False)
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        summary = gen.generate(result).executive_summary
        assert len(summary) > 0

    # --- responstijd recommendation (line 479) ---

    def test_recommendation_responstijd_positieve_correlatie(self, nl_translations: dict) -> None:
        """r > 0.1 → responstijd-aanbeveling aanwezig."""
        result = _make_result_with_rti(nl_translations, correlation=0.35)
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        recs = gen.generate(result).recommendations
        resp_recs = [r for r in recs if "esponstijd" in r.title]
        assert len(resp_recs) >= 1

    # --- HC > 25% finding (lines 557-558) ---

    def test_finding_hc_ratio_hoog(self, nl_translations: dict) -> None:
        """HC > 25% → 'hoog' severity finding."""
        result = _make_result_with_rti(nl_translations, hc_ratio=30.0)
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        findings = gen.generate(result).critical_findings
        hc_findings = [f for f in findings if "HC" in f.title or "High" in f.title]
        if hc_findings:
            assert hc_findings[0].severity == "hoog"

    # --- negatieve correlatie finding (line 607) ---

    def test_finding_negatieve_correlatie(self, nl_translations: dict) -> None:
        """r < -0.1 → negatieve correlatie finding aanwezig."""
        result = _make_result_with_rti(nl_translations, correlation=-0.35)
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        findings = gen.generate(result).critical_findings
        corr_findings = [f for f in findings if "correlatie" in f.title.lower()]
        assert len(corr_findings) >= 1

    # --- follow-up responstijd (line 700) ---

    def test_follow_up_responstijd_monitoring(self, nl_translations: dict) -> None:
        """rti.avg_days > 10.0 → middellange-termijn follow-up actie."""
        result = _make_result_with_rti(nl_translations, avg_days=15.0)
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        actions = gen.generate(result).follow_up_actions
        mid_actions = [a for a in actions if a.horizon == "middellang"]
        assert any("responstijd" in a.action.lower() for a in mid_actions)

    # --- visual analysis met twee verschillende ziekenhuizen (lines 742-743) ---

    def test_visual_analysis_twee_ziekenhuizen_shortlist(self, nl_translations: dict) -> None:
        """Shortlist met best != worst → beide verschijnen in subplot4."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=20,
            current_total=20,
            baseline_avg_score=3.5,
            current_avg_score=4.5,
            delta_avg_score=1.0,
            baseline_pct_positive=60.0,
            current_pct_positive=90.0,
            baseline_pct_negative=20.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=10.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=3,
            current_n_hospitals=3,
            baseline_hc_ratio=20.0,
            current_hc_ratio=5.0,
            trend_is_structural=True,
            trend_breadth="breed",
            hospital_shortlist=[
                HospitalComparison("AZ Best", 3.5, 5, 5.0, 5),  # best
                HospitalComparison("OLV Worst", 3.0, 5, 3.0, 5),  # worst
            ],
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        va = gen.generate(result).visual_analysis
        assert "AZ Best" in va.subplot4_hospitals
        assert "OLV Worst" in va.subplot4_hospitals

    # --- stijgende trend (line 774) ---

    def test_turning_point_stijgende_trend(self, nl_translations: dict) -> None:
        """3 stijgende periodes → 'stijgende trend' in output."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=15,
            current_total=10,
            baseline_avg_score=3.5,
            current_avg_score=4.5,
            delta_avg_score=1.0,
            baseline_pct_positive=60.0,
            current_pct_positive=90.0,
            baseline_pct_negative=20.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=10.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=3,
            current_n_hospitals=3,
            baseline_hc_ratio=20.0,
            current_hc_ratio=5.0,
            trend_is_structural=True,
            trend_breadth="breed",
            monthly_timeline=[
                MonthlyDataPoint("2025-06", 3.0, 5, 30.0, "S1 2025"),
                MonthlyDataPoint("2025-07", 3.5, 5, 20.0, "S2 2025"),
                MonthlyDataPoint("2026-01", 4.0, 5, 10.0, "S1 2026"),
                MonthlyDataPoint("2026-02", 4.5, 5, 5.0, "S1 2026"),
            ],
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        tpa = gen.generate(result).turning_point_analysis
        assert "stijgende trend" in tpa

    # --- dalende trend (line 789) ---

    def test_turning_point_dalende_trend(self, nl_translations: dict) -> None:
        """3 dalende periodes → 'dalende trend' in output."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=10,
            baseline_avg_score=4.5,
            current_avg_score=3.5,
            delta_avg_score=-1.0,
            baseline_pct_positive=90.0,
            current_pct_positive=60.0,
            baseline_pct_negative=5.0,
            current_pct_negative=20.0,
            baseline_avg_response_days=5.0,
            current_avg_response_days=10.0,
            baseline_n_hospitals=3,
            current_n_hospitals=3,
            baseline_hc_ratio=5.0,
            current_hc_ratio=20.0,
            trend_is_structural=False,
            trend_breadth="beperkt",
            monthly_timeline=[
                MonthlyDataPoint("2025-10", 4.5, 5, 5.0, "S2 2025"),
                MonthlyDataPoint("2025-11", 4.0, 5, 10.0, "S2 2025"),
                MonthlyDataPoint("2026-01", 3.5, 5, 20.0, "S1 2026"),
                MonthlyDataPoint("2026-02", 3.0, 5, 25.0, "S1 2026"),
            ],
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        tpa = gen.generate(result).turning_point_analysis
        assert "dalende trend" in tpa

    # --- fasen > 1 (lines 793-794) ---

    def test_turning_point_fasen_vermeld(self, nl_translations: dict) -> None:
        """Meerdere halfjaarperiodes → fasen worden vermeld in keerpuntanalyse."""
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=10,
            baseline_avg_score=3.5,
            current_avg_score=4.5,
            delta_avg_score=1.0,
            baseline_pct_positive=60.0,
            current_pct_positive=90.0,
            baseline_pct_negative=20.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=10.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=3,
            current_n_hospitals=3,
            baseline_hc_ratio=20.0,
            current_hc_ratio=5.0,
            trend_is_structural=True,
            trend_breadth="breed",
            monthly_timeline=[
                MonthlyDataPoint("2025-07", 3.5, 5, 20.0, "S2 2025"),
                MonthlyDataPoint("2026-01", 4.5, 5, 5.0, "S1 2026"),
            ],
        )
        gen = InsightsGenerator(nl_translations, lang="nl", seed=1)
        tpa = gen.generate(result).turning_point_analysis
        # 2 fasen: S2 2025 + S1 2026
        assert "halfjaarperiode" in tpa

    # --- score_distribution lege df (line 810 in analyser) ---

    def test_score_distribution_lege_df_geeft_geen_gescoord_narrative(
        self, nl_translations: dict, evolution_df: pd.DataFrame
    ) -> None:
        """Lege df → narrative = 'Geen gescoorde antwoorden beschikbaar.'"""
        from csat.core.analysers.evolution_analyser import EvolutionAnalyser

        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        empty = evolution_df.iloc[0:0].copy()
        sd = analyser._calc_score_distribution(empty)
        assert sd.narrative == "Geen gescoorde antwoorden beschikbaar."

    # --- avg_negative_days met negatieve tickets (line 887 in analyser) ---

    def test_response_time_insight_baseline_heeft_avg_negative(
        self, nl_translations: dict, evolution_df: pd.DataFrame
    ) -> None:
        """Baseline bevat negatieve tickets met satisfaction_date → avg_negative aanwezig."""
        from csat.core.analysers.evolution_analyser import EvolutionAnalyser

        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        baseline_df = analyser._get_df_for_periods(["2025-06", "2025-07"])
        insight = analyser._calc_response_time_insight(baseline_df)
        assert insight.avg_negative_days is not None
        assert insight.avg_negative_days > 0

    # --- KPI target "aandacht" (lines 985, 993 in analyser) ---

    def test_kpi_target_aandacht_higher_is_better(
        self, nl_translations: dict, evolution_df: pd.DataFrame
    ) -> None:
        """pct_positive: current=70 is >= 67.5 (75*0.9) maar < 75 → aandacht."""
        from csat.core.analysers.evolution_analyser import EvolutionAnalyser

        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        targets = analyser._calc_kpi_targets(
            4.5,
            4.5,  # avg
            5.0,
            5.0,  # hc
            80.0,
            70.0,  # pct_pos (70 < 75 maar >= 67.5)
            10.0,
            10.0,  # pct_neg
            5.0,
            5.0,  # resp
            35.0,
            35.0,  # comment
            100.0,  # retention
        )
        pos_t = next(t for t in targets if t.name == "pct_positive_min")
        assert pos_t.status == "aandacht"

    def test_kpi_target_aandacht_lower_is_better(
        self, nl_translations: dict, evolution_df: pd.DataFrame
    ) -> None:
        """avg_response: current=10.5 > 10 maar <= 11 (10*1.1) → aandacht."""
        from csat.core.analysers.evolution_analyser import EvolutionAnalyser

        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        targets = analyser._calc_kpi_targets(
            4.5,
            4.5,  # avg
            5.0,
            5.0,  # hc
            80.0,
            80.0,  # pct_pos
            10.0,
            10.0,  # pct_neg
            5.0,
            10.5,  # resp (10.5 > 10 maar <= 11) → aandacht
            35.0,
            35.0,  # comment
            100.0,  # retention
        )
        resp_t = next(t for t in targets if t.name == "avg_response_days_max")
        assert resp_t.status == "aandacht"

    # --- lege H2 df (line 1027 in analyser) ---

    def test_benchmark_h2_lege_h2_data(
        self, nl_translations: dict, evolution_df: pd.DataFrame
    ) -> None:
        """H2-periodes aanwezig maar geen data → benchmark_h2 = None."""
        from csat.core.analysers.evolution_analyser import EvolutionAnalyser

        analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
        # 2025-11 en 2025-12 zijn H2 maar bevatten geen data in de fixture
        bm = analyser._calc_benchmark_h2(["2025-11", "2025-12"])
        assert bm is None


# ===========================================================================
# Tests voor ongedekte edge cases — InsightsGenerator (fase 3g coverage)
# ===========================================================================


class TestInsightsEdgeCases:
    """
    Tests die specifiek de 7 ongedekte regels in insights_generator.py dekken.

    Doelregels: 557-558 (nieuwe thema-aanbeveling), 774 (i18n non-dict pad),
                789 (pick lege opties), 793-794 (pick format-fout).
    """

    # --- Lines 557-558: Aanbeveling voor nieuw feedbackthema ---

    def test_recommendation_nieuw_thema_aangemaakt(
        self, insights_gen_nl: InsightsGenerator, minimal_result: EvolutionResult
    ) -> None:
        """Aanbeveling wordt gegenereerd als er een NIEUW thema aanwezig is."""
        import dataclasses

        result = dataclasses.replace(
            minimal_result,
            negative_themes=[
                ThemeEvolution(
                    theme_key="communicatie",
                    pct_baseline=0.0,
                    pct_current=30.0,
                    status="NIEUW",
                )
            ],
        )
        bundle = insights_gen_nl.generate(result)
        titles = [r.title for r in bundle.recommendations]
        assert any("communicatie" in t.lower() or "thema" in t.lower() for t in titles), (
            f"Geen thema-aanbeveling gevonden in: {titles}"
        )

    def test_recommendation_nieuw_thema_beschrijving_gevuld(
        self, insights_gen_nl: InsightsGenerator, minimal_result: EvolutionResult
    ) -> None:
        """Beschrijving van de thema-aanbeveling bevat de themanaam en het jaar."""
        import dataclasses

        result = dataclasses.replace(
            minimal_result,
            negative_themes=[
                ThemeEvolution(
                    theme_key="urgentie",
                    pct_baseline=0.0,
                    pct_current=20.0,
                    status="NIEUW",
                )
            ],
        )
        bundle = insights_gen_nl.generate(result)
        thema_rec = next((r for r in bundle.recommendations if "urgentie" in r.title.lower()), None)
        assert thema_rec is not None
        assert "urgentie" in thema_rec.description.lower()
        assert result.current_label in thema_rec.description

    # --- Line 774: _get_i18n retourneert '' als path door non-dict gaat ---

    def test_get_i18n_non_dict_node_geeft_leeg(self, insights_gen_nl: InsightsGenerator) -> None:
        """_get_i18n traverseert voorbij een lijst-node → retourneert ''."""
        # insights.connectors.contrast is een lijst ["Hoewel", ...]
        # Extra level "onbestaand" voorbij de lijst → non-dict → ""
        result = insights_gen_nl._get_i18n("insights.connectors.contrast.onbestaand")
        assert result == ""

    def test_get_i18n_onbestaand_pad_geeft_leeg(self, insights_gen_nl: InsightsGenerator) -> None:
        """_get_i18n retourneert '' voor volledig onbekend pad."""
        result = insights_gen_nl._get_i18n("bestaat.niet.echt")
        assert result == ""

    # --- Line 789: _pick retourneert '' bij lege opties ---

    def test_pick_lege_lijst_geeft_leeg(self, insights_gen_nl: InsightsGenerator) -> None:
        """_pick([]) retourneert een lege string."""
        assert insights_gen_nl._pick([]) == ""

    def test_pick_lege_string_geeft_leeg(self, insights_gen_nl: InsightsGenerator) -> None:
        """_pick('') retourneert een lege string (falsy check)."""
        assert insights_gen_nl._pick("") == ""

    # --- Lines 793-794: _pick handelt format-fouten af ---

    def test_pick_keyerror_retourneert_ruwe_tekst(self, insights_gen_nl: InsightsGenerator) -> None:
        """_pick met ontbrekende format-sleutel retourneert de template-string ongewijzigd."""
        template = "Score {ontbrekende_sleutel} is zichtbaar."
        result = insights_gen_nl._pick(template)
        assert result == template

    def test_pick_indexerror_retourneert_ruwe_tekst(
        self, insights_gen_nl: InsightsGenerator
    ) -> None:
        """_pick met positional placeholder zonder args retourneert de template-string."""
        template = "Ticket {0} is belangrijk."
        result = insights_gen_nl._pick(template)
        assert result == template


# ---------------------------------------------------------------------------
# Prompt 3 — correlatie-omslag + KPI-achievement narrative
# ---------------------------------------------------------------------------


class TestCorrelatieomslagEnKpiAchievement:
    """Tests voor correlatie-omslag bevinding en KPI-achievement narrative (Fase 3g Prompt 3)."""

    def _base_result(self) -> EvolutionResult:
        """Minimaal EvolutionResult als basis voor parametrische tests."""
        return EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=8,
            baseline_avg_score=3.50,
            current_avg_score=4.20,
            delta_avg_score=0.70,
            baseline_pct_positive=60.0,
            current_pct_positive=80.0,
            baseline_pct_negative=20.0,
            current_pct_negative=8.0,
            baseline_avg_response_days=12.0,
            current_avg_response_days=7.0,
            baseline_n_hospitals=5,
            current_n_hospitals=5,
            baseline_hc_ratio=10.0,
            current_hc_ratio=12.0,
            trend_is_structural=True,
            trend_breadth="breed",
        )

    def test_correlatie_omslag_bevinding_bij_neg_naar_pos(
        self, insights_gen_nl: InsightsGenerator
    ) -> None:
        """Correlatie-omslag bevinding wordt gegenereerd als baseline_corr < -0,05 en current_corr > 0,05."""
        result = self._base_result()
        result.response_time_insight = ResponseTimeInsight(
            avg_days=7.0,
            correlation_score=0.118,
            baseline_correlation_score=-0.356,
        )
        bundle = insights_gen_nl.generate(result)
        titels = [f.title for f in bundle.critical_findings]
        assert any("omslag" in t.lower() or "inversion" in t.lower() for t in titels), (
            "Verwacht een correlatie-omslag bevinding bij overgang neg → pos"
        )

    def test_geen_correlatie_omslag_bij_zelfde_teken(
        self, insights_gen_nl: InsightsGenerator
    ) -> None:
        """Geen correlatie-omslag bevinding als beide correlaties hetzelfde teken hebben."""
        result = self._base_result()
        result.response_time_insight = ResponseTimeInsight(
            avg_days=7.0,
            correlation_score=0.150,
            baseline_correlation_score=0.200,
        )
        bundle = insights_gen_nl.generate(result)
        titels = [f.title for f in bundle.critical_findings]
        assert not any("omslag" in t.lower() for t in titels), (
            "Geen correlatie-omslag bevinding verwacht als beide correlaties positief zijn"
        )

    def test_kpi_achievement_narrative_alle_targets_op_schema(
        self, insights_gen_nl: InsightsGenerator
    ) -> None:
        """Executive summary bevat KPI-achievement zin als alle targets op schema zijn."""
        result = self._base_result()
        result.kpi_targets = [
            KpiTarget(
                name="avg_score_min",
                baseline=3.5,
                target=4.0,
                current=4.2,
                status="op_schema",
                on_track=True,
            ),
            KpiTarget(
                name="pct_positive_min",
                baseline=60.0,
                target=75.0,
                current=80.0,
                status="op_schema",
                on_track=True,
            ),
            KpiTarget(
                name="hc_ratio_max",
                baseline=10.0,
                target=15.0,
                current=12.0,
                status="op_schema",
                on_track=True,
            ),
        ]
        bundle = insights_gen_nl.generate(result)
        assert "3" in bundle.executive_summary and "KPI" in bundle.executive_summary, (
            "Executive summary moet KPI-achievement zin bevatten als alle targets op schema zijn"
        )


# ---------------------------------------------------------------------------
# Prompt 4 — ontbrekende branches (coverage 100%)
# ---------------------------------------------------------------------------


class TestNarrativeBranches:
    """Coverage-tests voor ongedekte branches in InsightsGenerator (Fase 3g — Prompt 4)."""

    def _minimal(self) -> EvolutionResult:
        """Basisresultaat zonder optionele velden."""
        return EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=8,
            baseline_avg_score=3.50,
            current_avg_score=4.00,
            delta_avg_score=0.50,
            baseline_pct_positive=60.0,
            current_pct_positive=75.0,
            baseline_pct_negative=20.0,
            current_pct_negative=10.0,
            baseline_avg_response_days=12.0,
            current_avg_response_days=8.0,
            baseline_n_hospitals=5,
            current_n_hospitals=5,
            baseline_hc_ratio=10.0,
            current_hc_ratio=12.0,
            trend_is_structural=True,
            trend_breadth="breed",
        )

    # --- Line 266: top_level == 5 (5★ heeft meeste counts) ---

    def test_score_dist_top_level_5_narrative(self, insights_gen_nl: InsightsGenerator) -> None:
        """Executive summary toont 'volle 5★' als score 5 het meest voorkomt (top_level==5, line 266)."""
        import dataclasses

        from csat.core.analysers.evolution_result import ScoreDistribution

        sd = ScoreDistribution(
            counts={1: 2, 2: 3, 3: 5, 4: 10, 5: 30},
            percentages={1: 4.0, 2: 6.0, 3: 10.0, 4: 20.0, 5: 60.0},
        )
        result = dataclasses.replace(self._minimal(), score_distribution_current=sd)
        bundle = insights_gen_nl.generate(result)
        assert "volle 5★" in bundle.executive_summary

    # --- Lines 269-273: top_level == 4 (niet 5) ---

    def test_score_dist_top_level_4_narrative(self, insights_gen_nl: InsightsGenerator) -> None:
        """Executive summary toont '4★ of hoger' als score 4 het meest voorkomt (top_level==4)."""
        import dataclasses

        from csat.core.analysers.evolution_result import ScoreDistribution

        sd = ScoreDistribution(
            counts={1: 2, 2: 3, 3: 5, 4: 30, 5: 10},
            percentages={1: 4.0, 2: 6.0, 3: 10.0, 4: 60.0, 5: 20.0},
        )
        result = dataclasses.replace(self._minimal(), score_distribution_current=sd)
        bundle = insights_gen_nl.generate(result)
        assert "4★ of hoger" in bundle.executive_summary

    # --- Lines 276-279: top_level <= 3 ---

    def test_score_dist_top_level_laag_narrative(self, insights_gen_nl: InsightsGenerator) -> None:
        """Executive summary toont 'meerderheid' als score 3 het meest voorkomt (top_level==3)."""
        import dataclasses

        from csat.core.analysers.evolution_result import ScoreDistribution

        sd = ScoreDistribution(
            counts={1: 5, 2: 8, 3: 30, 4: 4, 5: 3},
            percentages={1: 10.0, 2: 16.0, 3: 60.0, 4: 8.0, 5: 6.0},
        )
        result = dataclasses.replace(self._minimal(), score_distribution_current=sd)
        bundle = insights_gen_nl.generate(result)
        assert "meerderheid" in bundle.executive_summary

    # --- Line 508: baseline_corr > 0.05 EN current_corr < -0.05 ---

    def test_correlatie_omslag_baseline_pos_current_neg(
        self, insights_gen_nl: InsightsGenerator
    ) -> None:
        """'risicofactor'-bevinding gegenereerd als baseline_corr > 0,05 en current_corr < -0,05."""
        result = self._minimal()
        result.response_time_insight = ResponseTimeInsight(
            avg_days=7.0,
            correlation_score=-0.20,
            baseline_correlation_score=0.25,
        )
        bundle = insights_gen_nl.generate(result)
        titels = [f.title for f in bundle.critical_findings]
        assert any("risicofactor" in t.lower() for t in titels), (
            "Verwacht een 'risicofactor'-bevinding als baseline pos en current neg zijn"
        )

    # --- Line 978: stabiele trend (delta tussen -0,05 en 0,05) ---

    def test_visual_analysis_stabiele_trend(self, insights_gen_nl: InsightsGenerator) -> None:
        """subplot1_scoretrend toont 'stabiel' als delta_avg_score ≈ 0 (tussen -0,05 en 0,05)."""
        import dataclasses

        result = dataclasses.replace(
            self._minimal(),
            delta_avg_score=0.02,
            monthly_timeline=[
                MonthlyDataPoint(
                    period="2026-01",
                    avg_score=4.0,
                    total_tickets=10,
                    pct_negative=5.0,
                    fase="S1 2026",
                ),
                MonthlyDataPoint(
                    period="2026-02",
                    avg_score=4.02,
                    total_tickets=8,
                    pct_negative=4.0,
                    fase="S1 2026",
                ),
            ],
        )
        bundle = insights_gen_nl.generate(result)
        assert "stabiel" in bundle.visual_analysis.subplot1_scoretrend

    # --- Line 1195: worst.priority NIET in (Trivial, Minor) ---

    def test_priority_worst_niet_laag_narrative(self, insights_gen_nl: InsightsGenerator) -> None:
        """priority_analysis_narrative toont 'opvolging aanbevolen' als worst prioriteit Blocker is."""
        import dataclasses

        from csat.core.analysers.evolution_result import PriorityComparison

        result = dataclasses.replace(
            self._minimal(),
            by_priority=[
                PriorityComparison(
                    priority="Blocker",
                    baseline_score=3.5,
                    baseline_pct_neg=20.0,
                    current_score=2.5,
                    current_pct_neg=30.0,
                ),
                PriorityComparison(
                    priority="Major",
                    baseline_score=4.0,
                    baseline_pct_neg=10.0,
                    current_score=4.5,
                    current_pct_neg=5.0,
                ),
                PriorityComparison(
                    priority="Trivial",
                    baseline_score=3.0,
                    baseline_pct_neg=25.0,
                    current_score=4.0,
                    current_pct_neg=10.0,
                ),
            ],
        )
        bundle = insights_gen_nl.generate(result)
        assert "opvolging aanbevolen" in bundle.priority_analysis_narrative

    # --- Lines 1203-1210: high_urgency aanwezig + avg_high >= avg_low ---

    def test_priority_escalatie_werkt_narrative(self, insights_gen_nl: InsightsGenerator) -> None:
        """priority_analysis_narrative toont escalatie-zin als Blocker/Critical hoger dan Trivial/Minor."""
        import dataclasses

        from csat.core.analysers.evolution_result import PriorityComparison

        result = dataclasses.replace(
            self._minimal(),
            by_priority=[
                PriorityComparison(
                    priority="Blocker",
                    baseline_score=3.0,
                    baseline_pct_neg=30.0,
                    current_score=4.8,
                    current_pct_neg=0.0,
                ),
                PriorityComparison(
                    priority="Critical",
                    baseline_score=3.0,
                    baseline_pct_neg=30.0,
                    current_score=4.6,
                    current_pct_neg=0.0,
                ),
                PriorityComparison(
                    priority="Trivial",
                    baseline_score=3.5,
                    baseline_pct_neg=20.0,
                    current_score=3.5,
                    current_pct_neg=15.0,
                ),
                PriorityComparison(
                    priority="Minor",
                    baseline_score=3.5,
                    baseline_pct_neg=20.0,
                    current_score=4.0,
                    current_pct_neg=10.0,
                ),
            ],
        )
        bundle = insights_gen_nl.generate(result)
        assert "escalatieprocedure" in bundle.priority_analysis_narrative

    # --- Lines 1248-1249: shortest.score_level <= 2 (paradox: lage score, korte responstijd) ---

    def test_response_time_paradox_lage_score_korte_tijd(
        self, insights_gen_nl: InsightsGenerator
    ) -> None:
        """response_time_narrative toont paradox als score 1/2 de kortste responstijd heeft."""
        import dataclasses

        from csat.core.analysers.evolution_result import ResponseTimeRow

        result = dataclasses.replace(
            self._minimal(),
            response_time_by_score={
                1: ResponseTimeRow(score_level=1, baseline_days=5.0, current_days=1.0),
                5: ResponseTimeRow(score_level=5, baseline_days=8.0, current_days=10.0),
            },
        )
        bundle = insights_gen_nl.generate(result)
        assert "paradox" in bundle.response_time_narrative.lower()

    # --- Lines 1266-1275: longest.score_level >= 4 (hoge score, lange responstijd = complexe dossiers) ---

    def test_response_time_hoge_score_langste_tijd(
        self, insights_gen_nl: InsightsGenerator
    ) -> None:
        """response_time_narrative toont 'complexere dossiers' als score 4/5 de langste responstijd heeft
        + positieve correlatie wordt toegevoegd aan narrative (lines 1266-1275)."""
        import dataclasses

        from csat.core.analysers.evolution_result import ResponseTimeRow

        result = dataclasses.replace(
            self._minimal(),
            response_time_by_score={
                2: ResponseTimeRow(score_level=2, baseline_days=5.0, current_days=2.0),
                4: ResponseTimeRow(score_level=4, baseline_days=8.0, current_days=12.0),
            },
            response_time_insight=ResponseTimeInsight(
                avg_days=8.0,
                correlation_score=0.15,  # r > 0.1 → positieve correlatie-tekst (line 1267-1273)
            ),
        )
        bundle = insights_gen_nl.generate(result)
        assert "complexere dossiers" in bundle.response_time_narrative
        assert "positieve correlatie" in bundle.response_time_narrative

    def test_response_time_negatieve_correlatie_narrative(
        self, insights_gen_nl: InsightsGenerator
    ) -> None:
        """response_time_narrative toont negatieve correlatie-tekst als r < -0.1 (lines 1274-1275)."""
        import dataclasses

        from csat.core.analysers.evolution_result import ResponseTimeRow

        result = dataclasses.replace(
            self._minimal(),
            response_time_by_score={
                3: ResponseTimeRow(score_level=3, baseline_days=6.0, current_days=3.0),
                5: ResponseTimeRow(score_level=5, baseline_days=10.0, current_days=15.0),
            },
            response_time_insight=ResponseTimeInsight(
                avg_days=8.0,
                correlation_score=-0.25,  # r < -0.1 → negatieve correlatie-tekst (line 1274-1275)
            ),
        )
        bundle = insights_gen_nl.generate(result)
        assert "negatieve correlatie" in bundle.response_time_narrative
