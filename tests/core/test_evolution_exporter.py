"""
Unit tests voor EvolutionExporter en _fmt_delta.

Dekt: render(), export(), _build_context(), _fmt_delta(),
tweetaligheid NL/FR, conditionele executive summary, randgevallen.
"""

from pathlib import Path

import pandas as pd
import pytest

from csat.core.analysers.evolution_analyser import EvolutionAnalyser
from csat.core.analysers.evolution_result import EvolutionResult
from csat.core.exporters.evolution_exporter import EvolutionExporter, _fmt_delta

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BASELINE = ["2025-06", "2025-07"]
CURRENT = ["2026-01", "2026-02"]


@pytest.fixture
def evolution_result(evolution_df: pd.DataFrame) -> EvolutionResult:
    """EvolutionResult via EvolutionAnalyser op de evolution_df fixture."""
    analyser = EvolutionAnalyser(evolution_df, pillar_key="pharma")
    return analyser.analyse(BASELINE, CURRENT)


@pytest.fixture
def exporter_nl(tmp_path: Path) -> EvolutionExporter:
    """EvolutionExporter NL met tijdelijke outputmap en echte templates."""
    from csat.config.settings import TEMPLATES_PATH

    return EvolutionExporter(lang="nl", templates_path=TEMPLATES_PATH, output_path=tmp_path)


@pytest.fixture
def exporter_fr(tmp_path: Path) -> EvolutionExporter:
    """EvolutionExporter FR met tijdelijke outputmap en echte templates."""
    from csat.config.settings import TEMPLATES_PATH

    return EvolutionExporter(lang="fr", templates_path=TEMPLATES_PATH, output_path=tmp_path)


# ---------------------------------------------------------------------------
# 1. _fmt_delta hulpfunctie
# ---------------------------------------------------------------------------


class TestFmtDelta:
    """Tests voor de _fmt_delta hulpfunctie."""

    def test_positieve_waarde(self) -> None:
        assert _fmt_delta(1.70, 2) == "+1,70"

    def test_negatieve_waarde(self) -> None:
        assert _fmt_delta(-0.5, 1) == "-0,5"

    def test_nul(self) -> None:
        assert _fmt_delta(0.0, 1) == "+0,0"

    def test_grote_waarde(self) -> None:
        assert _fmt_delta(1234.5, 1) == "+1.234,5"

    def test_default_decimalen(self) -> None:
        result = _fmt_delta(0.92)
        assert result.startswith("+")
        assert "," in result


# ---------------------------------------------------------------------------
# 2. Initialisatie
# ---------------------------------------------------------------------------


class TestEvolutionExporterInit:
    """Tests voor __init__ — taalvalidatie."""

    def test_init_nl(self, tmp_path: Path) -> None:
        from csat.config.settings import TEMPLATES_PATH

        e = EvolutionExporter(lang="nl", templates_path=TEMPLATES_PATH, output_path=tmp_path)
        assert e._lang == "nl"

    def test_init_fr(self, tmp_path: Path) -> None:
        from csat.config.settings import TEMPLATES_PATH

        e = EvolutionExporter(lang="fr", templates_path=TEMPLATES_PATH, output_path=tmp_path)
        assert e._lang == "fr"

    def test_init_ongeldige_taal(self, tmp_path: Path) -> None:
        from csat.config.settings import TEMPLATES_PATH

        with pytest.raises(ValueError, match="Niet-ondersteunde taal"):
            EvolutionExporter(lang="de", templates_path=TEMPLATES_PATH, output_path=tmp_path)


# ---------------------------------------------------------------------------
# 3. Render — basisinhoud
# ---------------------------------------------------------------------------


class TestRenderBasis:
    """Tests voor render() — basisinhoud en structuur."""

    def test_render_retourneert_string(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_render_bevat_pillar_naam(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "ZORGI PHARMA" in result

    def test_render_bevat_baseline_label(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "2025" in result

    def test_render_bevat_current_label(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "2026" in result

    def test_render_bevat_delta_positief(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """Delta +1,70 moet in het rapport staan."""
        result = exporter_nl.render(evolution_result)
        assert "+1,70" in result

    def test_render_bevat_avg_score_current(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "4,50" in result

    def test_render_bevat_pct_negatief(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """Baseline pct_negatief = 40,0%."""
        result = exporter_nl.render(evolution_result)
        assert "40,0%" in result

    def test_render_bevat_maandelijkse_tijdlijn(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "2025-06" in result
        assert "2026-01" in result

    def test_render_bevat_fase_labels(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "H1 2025" in result
        assert "H2 2025" in result

    def test_render_bevat_ziekenhuizen(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "AZ Groeninge" in result
        assert "UZ Brussel" in result

    def test_render_bevat_verdwenen_ziekenhuizen(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "OLV Aalst" in result

    def test_render_bevat_kpi_status_ok(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "✅ OK" in result

    def test_render_bevat_kpi_status_risico(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "🔴 Risico" in result

    def test_render_bevat_adr006_noot(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "ADR-006" in result


# ---------------------------------------------------------------------------
# 4. Render — tweetaligheid
# ---------------------------------------------------------------------------


class TestRenderTweetaligheid:
    """Tests voor NL vs FR taalverschillen in render()."""

    def test_nl_sectietitel_kerncijfers(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "Kerncijfers" in result

    def test_fr_sectietitel_kerncijfers(
        self, exporter_fr: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_fr.render(evolution_result)
        assert "Chiffres clés" in result

    def test_nl_responstijd_eenheid_d(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """NL gebruikt 'd' als eenheid voor dagen."""
        result = exporter_nl.render(evolution_result)
        assert " d |" in result or " d\n" in result

    def test_fr_responstijd_eenheid_j(
        self, exporter_fr: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """FR gebruikt 'j' als eenheid voor jours."""
        result = exporter_fr.render(evolution_result)
        assert " j |" in result or " j\n" in result

    def test_fr_bevat_pillar_naam(
        self, exporter_fr: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_fr.render(evolution_result)
        assert "ZORGI PHARMA" in result

    def test_nl_bevat_ziekenhuizen_label(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "Ziekenhuisvergelijking" in result

    def test_fr_bevat_hospitals_label(
        self, exporter_fr: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_fr.render(evolution_result)
        assert "Comparaison par" in result


# ---------------------------------------------------------------------------
# 5. Render — thema's
# ---------------------------------------------------------------------------


class TestRenderThemas:
    """Tests voor thema-sectie in het rapport."""

    def test_opgelost_thema_aanwezig(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """responstijd en onvolledig zijn OPGELOST → moeten in het rapport staan."""
        result = exporter_nl.render(evolution_result)
        assert "Opgelost" in result or "OPGELOST" in result or "✅ Opgelost" in result

    def test_geen_themas_toon_placeholder(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """Als er geen thema's zijn, toon placeholder tekst."""
        # Maak result zonder thema's
        import dataclasses

        result_no_themes = dataclasses.replace(evolution_result, negative_themes=[])
        rendered = exporter_nl.render(result_no_themes)
        assert "Geen negatieve feedbackthema" in rendered


# ---------------------------------------------------------------------------
# 6. Render — executive summary (conditionele logica)
# ---------------------------------------------------------------------------


class TestRenderConclusion:
    """Tests voor de conditionele executive summary (sectie 8)."""

    def test_structurele_verbetering_breed(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """delta=+1,70 en breadth='breed' → 'Structurele verbetering'."""
        import dataclasses

        result = dataclasses.replace(
            evolution_result,
            delta_avg_score=1.70,
            trend_is_structural=True,
            trend_breadth="breed",
        )
        rendered = exporter_nl.render(result)
        assert "Structurele verbetering" in rendered

    def test_selectieve_verbetering_beperkt(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        import dataclasses

        result = dataclasses.replace(
            evolution_result,
            delta_avg_score=0.80,
            trend_is_structural=True,
            trend_breadth="beperkt",
        )
        rendered = exporter_nl.render(result)
        assert "Selectieve verbetering" in rendered

    def test_verbetering_gemengd(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        import dataclasses

        result = dataclasses.replace(
            evolution_result,
            delta_avg_score=0.60,
            trend_is_structural=True,
            trend_breadth="gemengd",
        )
        rendered = exporter_nl.render(result)
        assert "Verbetering in evolutie" in rendered

    def test_stabiele_situatie(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        import dataclasses

        result = dataclasses.replace(
            evolution_result, delta_avg_score=0.10, trend_is_structural=False
        )
        rendered = exporter_nl.render(result)
        assert "Stabiele situatie" in rendered

    def test_achteruitgang(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        import dataclasses

        result = dataclasses.replace(
            evolution_result, delta_avg_score=-0.80, trend_is_structural=False
        )
        rendered = exporter_nl.render(result)
        assert "Achteruitgang" in rendered

    def test_hc_ratio_at_risk_melding(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """HC > 25% → AT_RISK melding in conclusie."""
        import dataclasses

        result = dataclasses.replace(evolution_result, current_hc_ratio=50.0)
        rendered = exporter_nl.render(result)
        assert "HC-ratio aandacht" in rendered

    def test_hc_ratio_warning_melding(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """HC tussen 15% en 25% → WARNING melding."""
        import dataclasses

        result = dataclasses.replace(evolution_result, current_hc_ratio=20.0)
        rendered = exporter_nl.render(result)
        assert "boven drempel" in rendered

    def test_verdwenen_ziekenhuizen_melding(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """hospitals_disappeared → melding in conclusie."""
        rendered = exporter_nl.render(evolution_result)
        assert "Ontbrekende ziekenhuizen" in rendered

    def test_geen_verdwenen_ziekenhuizen_geen_melding(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        import dataclasses

        result = dataclasses.replace(evolution_result, hospitals_disappeared=[])
        rendered = exporter_nl.render(result)
        assert "Ontbrekende ziekenhuizen" not in rendered

    def test_opgeloste_themas_in_conclusie(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        rendered = exporter_nl.render(evolution_result)
        assert "Opgeloste aandachtspunten" in rendered

    def test_fr_structurele_verbetering(
        self, exporter_fr: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        import dataclasses

        result = dataclasses.replace(
            evolution_result,
            delta_avg_score=1.70,
            trend_is_structural=True,
            trend_breadth="breed",
        )
        rendered = exporter_fr.render(result)
        assert "Amélioration structurelle" in rendered


# ---------------------------------------------------------------------------
# 7. Export — bestandsschrijving
# ---------------------------------------------------------------------------


class TestExport:
    """Tests voor export() — bestandsschrijving en naamgeving."""

    def test_export_schrijft_bestand(
        self,
        exporter_nl: EvolutionExporter,
        evolution_result: EvolutionResult,
        tmp_path: Path,
    ) -> None:
        pad = exporter_nl.export(evolution_result)
        assert pad.exists()
        assert pad.stat().st_size > 0

    def test_export_bestandsnaam_nl(
        self,
        exporter_nl: EvolutionExporter,
        evolution_result: EvolutionResult,
    ) -> None:
        pad = exporter_nl.export(evolution_result, year="2026")
        assert pad.name == "evolutie-pharma-2026-nl.md"

    def test_export_bestandsnaam_fr(
        self,
        exporter_fr: EvolutionExporter,
        evolution_result: EvolutionResult,
    ) -> None:
        pad = exporter_fr.export(evolution_result, year="2026")
        assert pad.name == "evolutie-pharma-2026-fr.md"

    def test_export_bestandsnaam_zonder_year(
        self,
        exporter_nl: EvolutionExporter,
        evolution_result: EvolutionResult,
    ) -> None:
        """Zonder year-argument: pillar + current_label worden gebruikt."""
        pad = exporter_nl.export(evolution_result)
        assert "evolutie-pharma-" in pad.name
        assert "-nl.md" in pad.name

    def test_export_bestandsnaam_spaties_gesaniteerd(
        self,
        exporter_nl: EvolutionExporter,
        evolution_result: EvolutionResult,
    ) -> None:
        """Spaties in year → koppeltekens in bestandsnaam."""
        pad = exporter_nl.export(evolution_result, year="jan mrt 2026")
        assert " " not in pad.name

    def test_export_inhoud_utf8(
        self,
        exporter_nl: EvolutionExporter,
        evolution_result: EvolutionResult,
    ) -> None:
        pad = exporter_nl.export(evolution_result, year="2026")
        inhoud = pad.read_text(encoding="utf-8")
        assert "ZORGI PHARMA" in inhoud

    def test_export_maakt_map_aan(
        self,
        evolution_result: EvolutionResult,
        tmp_path: Path,
    ) -> None:
        """Output-map wordt aangemaakt als die nog niet bestaat."""
        from csat.config.settings import TEMPLATES_PATH

        nieuwe_map = tmp_path / "submap" / "output"
        e = EvolutionExporter(lang="nl", templates_path=TEMPLATES_PATH, output_path=nieuwe_map)
        pad = e.export(evolution_result, year="2026")
        assert pad.exists()

    def test_export_retourneert_pad(
        self,
        exporter_nl: EvolutionExporter,
        evolution_result: EvolutionResult,
    ) -> None:
        pad = exporter_nl.export(evolution_result, year="2026")
        assert isinstance(pad, Path)

    def test_export_fr(
        self,
        exporter_fr: EvolutionExporter,
        evolution_result: EvolutionResult,
    ) -> None:
        pad = exporter_fr.export(evolution_result, year="2026")
        inhoud = pad.read_text(encoding="utf-8")
        assert "Chiffres clés" in inhoud


# ---------------------------------------------------------------------------
# 8. Getalnotatie
# ---------------------------------------------------------------------------


class TestGetalnotatie:
    """Tests voor ZORGI getalnotatie in het gegenereerde rapport."""

    def test_komma_als_decimaalteken(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        # ZORGI notatie: 4,50 niet 4.50
        assert "4,50" in result

    def test_punt_als_duizendtalscheider(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """Test bij grote aantallen — met > 1000 tickets."""
        import dataclasses

        result_groot = dataclasses.replace(evolution_result, baseline_total=1247)
        rendered = exporter_nl.render(result_groot)
        assert "1.247" in rendered

    def test_delta_plus_prefix(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        result = exporter_nl.render(evolution_result)
        assert "+1,70" in result


# ---------------------------------------------------------------------------
# 9. Recurring themes — voorbeeld + actiehint (fase 3g scope)
# ---------------------------------------------------------------------------


class TestRenderRecurringThemes:
    """Tests voor recurring themes sectie met voorbeeld en actiehint."""

    def test_nog_aanwezig_thema_toont_voorbeeld(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """NOG_AANWEZIG thema met example → voorbeeld verschijnt in rapport."""
        import dataclasses

        from csat.core.analysers.evolution_result import ThemeEvolution

        result = dataclasses.replace(
            evolution_result,
            negative_themes=[
                ThemeEvolution(
                    theme_key="responstijd",
                    pct_baseline=30.0,
                    pct_current=20.0,
                    status="NOG_AANWEZIG",
                    example="te lang gewacht op een reactie",
                    action_hint="Controleer SLA-naleving.",
                )
            ],
        )
        rendered = exporter_nl.render(result)
        assert "te lang gewacht op een reactie" in rendered

    def test_nog_aanwezig_thema_toont_actiehint(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """NOG_AANWEZIG thema met action_hint → actiehint verschijnt in rapport."""
        import dataclasses

        from csat.core.analysers.evolution_result import ThemeEvolution

        result = dataclasses.replace(
            evolution_result,
            negative_themes=[
                ThemeEvolution(
                    theme_key="communicatie",
                    pct_baseline=15.0,
                    pct_current=25.0,
                    status="NOG_AANWEZIG",
                    example="geen update gekregen",
                    action_hint="Activeer proactieve statusupdates.",
                )
            ],
        )
        rendered = exporter_nl.render(result)
        assert "Activeer proactieve statusupdates." in rendered

    def test_opgelost_thema_toont_geen_voorbeeld_sectie(
        self, exporter_nl: EvolutionExporter, evolution_result: EvolutionResult
    ) -> None:
        """OPGELOST thema → geen voorbeeld/actiehint weergegeven in uitgebreide sectie."""
        import dataclasses

        from csat.core.analysers.evolution_result import ThemeEvolution

        result = dataclasses.replace(
            evolution_result,
            negative_themes=[
                ThemeEvolution(
                    theme_key="responstijd",
                    pct_baseline=30.0,
                    pct_current=0.0,
                    status="OPGELOST",
                    example="te lang gewacht",
                    action_hint="Controleer SLA.",
                )
            ],
        )
        rendered = exporter_nl.render(result)
        # Het thema staat in de tabel maar het voorbeeld-blok wordt niet getoond
        assert "✅ Opgelost" in rendered
        assert "te lang gewacht" not in rendered  # voorbeeld niet zichtbaar voor opgeloste
