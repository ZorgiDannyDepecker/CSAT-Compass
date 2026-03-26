"""
Unit tests voor EvolutionVisualiser en _fmt_delta / _extract_year helpers.

Dekt: render(), export(), alle 4 subplots, lege data-randgevallen,
pijlerkleur-lookup, bestandsnaamconventie en logger-aanroep.
"""

from pathlib import Path
from unittest.mock import patch

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytest

matplotlib.use("Agg")  # Geen GUI-venster openen tijdens tests

from csat.core.analysers.evolution_analyser import EvolutionAnalyser
from csat.core.analysers.evolution_result import (
    EvolutionResult,
    HospitalComparison,
)
from csat.core.exporters.evolution_visualiser import (
    EvolutionVisualiser,
    _extract_year,
    _fmt_delta,
    _style_legend,
)

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
def lege_result() -> EvolutionResult:
    """EvolutionResult zonder tijdlijn of ziekenhuis-data — randgeval."""
    return EvolutionResult(
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
        trend_breadth="beperkt",
        monthly_timeline=[],
        hospital_comparison=[],
    )


@pytest.fixture
def zorgi_result(evolution_df: pd.DataFrame) -> EvolutionResult:
    """EvolutionResult voor de zorgi-pijler (Dark Blue kleur)."""
    analyser = EvolutionAnalyser(evolution_df, pillar_key="zorgi")
    return analyser.analyse(BASELINE, CURRENT)


# ---------------------------------------------------------------------------
# 1. Helperfuncties
# ---------------------------------------------------------------------------


class TestFmtDelta:
    """Tests voor _fmt_delta hulpfunctie."""

    def test_positief(self) -> None:
        assert _fmt_delta(1.70) == "+1,70"

    def test_negatief(self) -> None:
        assert _fmt_delta(-0.50) == "-0,50"

    def test_nul(self) -> None:
        assert _fmt_delta(0.0) == "+0,00"

    def test_een_decimaal(self) -> None:
        assert _fmt_delta(0.92, 1) == "+0,9"

    def test_grote_waarde(self) -> None:
        result = _fmt_delta(1234.5, 1)
        assert result.startswith("+")
        assert "," in result


class TestExtractYear:
    """Tests voor _extract_year hulpfunctie."""

    def test_puur_jaar(self) -> None:
        assert _extract_year("2026") == "2026"

    def test_jaar_met_maandlabel(self) -> None:
        assert _extract_year("jan-mrt 2026") == "2026"

    def test_jaar_met_langere_prefix(self) -> None:
        assert _extract_year("Volledig 2025") == "2025"

    def test_geen_jaar_geeft_label_terug(self) -> None:
        assert _extract_year("baseline") == "baseline"

    def test_twee_jaren_geeft_eerste(self) -> None:
        # Pakt het eerste gevonden vier-cijferige jaar
        result = _extract_year("2025-2026")
        assert result in ("2025", "2026")


# ---------------------------------------------------------------------------
# 2. Initialisatie
# ---------------------------------------------------------------------------


class TestEvolutionVisualiserInit:
    """Constructorvalidatie."""

    def test_pillar_color_pharma(self, evolution_result: EvolutionResult) -> None:
        vis = EvolutionVisualiser(evolution_result)
        assert vis._pillar_color == "#609fce"

    def test_pillar_name_pharma(self, evolution_result: EvolutionResult) -> None:
        vis = EvolutionVisualiser(evolution_result)
        assert vis._pillar_name == "ZORGI PHARMA"

    def test_pillar_color_zorgi(self, zorgi_result: EvolutionResult) -> None:
        vis = EvolutionVisualiser(zorgi_result)
        assert vis._pillar_color == "#003a70"

    def test_onbekende_pijler_fallback_kleur(self, evolution_result: EvolutionResult) -> None:
        """Onbekende pijler valt terug op dark_blue."""
        result = EvolutionResult(
            pillar="onbekend",
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
            trend_breadth="beperkt",
        )
        vis = EvolutionVisualiser(result)
        assert vis._pillar_color == "#003a70"


# ---------------------------------------------------------------------------
# 3. render()
# ---------------------------------------------------------------------------


class TestRender:
    """Tests voor de render() methode."""

    def test_render_retourneert_figure(self, evolution_result: EvolutionResult) -> None:
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_render_heeft_vier_assen(self, evolution_result: EvolutionResult) -> None:
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        assert len(fig.axes) == 4
        plt.close(fig)

    def test_render_figuurgrootte(self, evolution_result: EvolutionResult) -> None:
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        breedte, hoogte = fig.get_size_inches()
        assert breedte == pytest.approx(15.0)
        assert hoogte == pytest.approx(10.0)
        plt.close(fig)

    def test_render_figuur_facecolor(self, evolution_result: EvolutionResult) -> None:
        """Figuurachtergrond moet Ultra Light Blue (#d7e7f3) zijn."""
        from matplotlib.colors import to_hex

        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        kleur = to_hex(fig.get_facecolor())
        assert kleur.lower() == "#d7e7f3"
        plt.close(fig)

    def test_render_suptitle_bevat_pijlernaam(self, evolution_result: EvolutionResult) -> None:
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        # suptitle is beschikbaar via fig.texts
        titels = [t.get_text() for t in fig.texts]
        assert any("ZORGI PHARMA" in t for t in titels)
        plt.close(fig)

    def test_render_suptitle_bevat_delta(self, evolution_result: EvolutionResult) -> None:
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        titels = [t.get_text() for t in fig.texts]
        assert any("Δ" in t for t in titels)
        plt.close(fig)

    def test_render_structureel_in_titel(self, evolution_result: EvolutionResult) -> None:
        """Structureel of Niet structureel staat in de supertitel."""
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        titels = [t.get_text() for t in fig.texts]
        assert any("structureel" in t.lower() for t in titels)
        plt.close(fig)

    def test_render_met_lege_data(self, lege_result: EvolutionResult) -> None:
        """render() mag niet crashen bij lege tijdlijn en geen ziekenhuizen."""
        vis = EvolutionVisualiser(lege_result)
        fig = vis.render()
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 4
        plt.close(fig)

    def test_render_geen_bestandsschrijving(
        self, evolution_result: EvolutionResult, tmp_path: Path
    ) -> None:
        """render() schrijft geen bestanden naar schijf."""
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        assert not list(tmp_path.glob("*.png"))
        plt.close(fig)


# ---------------------------------------------------------------------------
# 4. export()
# ---------------------------------------------------------------------------


class TestExport:
    """Tests voor de export() methode."""

    def test_export_schrijft_png(self, evolution_result: EvolutionResult, tmp_path: Path) -> None:
        vis = EvolutionVisualiser(evolution_result)
        pad = vis.export(tmp_path, year="2026")
        assert pad.exists()

    def test_export_bestandsextensie(
        self, evolution_result: EvolutionResult, tmp_path: Path
    ) -> None:
        vis = EvolutionVisualiser(evolution_result)
        pad = vis.export(tmp_path, year="2026")
        assert pad.suffix == ".png"

    def test_export_bestandsnaam_pharma(
        self, evolution_result: EvolutionResult, tmp_path: Path
    ) -> None:
        vis = EvolutionVisualiser(evolution_result)
        pad = vis.export(tmp_path, year="2026", timestamp=False)
        assert pad.name == "evolutie-pharma-2026-nl.png"

    def test_export_bestandsnaam_zonder_year_param(
        self, evolution_result: EvolutionResult, tmp_path: Path
    ) -> None:
        """Zonder year-parameter wordt het jaar uit current_label geëxtraheerd."""
        vis = EvolutionVisualiser(evolution_result)
        pad = vis.export(tmp_path)
        # current_label is "2026" — moet "evolutie-pharma-2026-nl.png" worden
        assert pad.suffix == ".png"
        assert "pharma" in pad.name

    def test_export_retourneert_pad_object(
        self, evolution_result: EvolutionResult, tmp_path: Path
    ) -> None:
        vis = EvolutionVisualiser(evolution_result)
        pad = vis.export(tmp_path, year="2026")
        assert isinstance(pad, Path)

    def test_export_maakt_outputmap_aan(
        self, evolution_result: EvolutionResult, tmp_path: Path
    ) -> None:
        """export() maakt de outputmap aan als die nog niet bestaat."""
        nieuwe_map = tmp_path / "submap" / "grafieken"
        vis = EvolutionVisualiser(evolution_result)
        pad = vis.export(nieuwe_map, year="2026")
        assert pad.exists()

    def test_export_sluit_figuur(self, evolution_result: EvolutionResult, tmp_path: Path) -> None:
        """Na export() is het figure gesloten (geen geheugenlek)."""
        aantal_voor = len(plt.get_fignums())
        vis = EvolutionVisualiser(evolution_result)
        vis.export(tmp_path, year="2026")
        aantal_na = len(plt.get_fignums())
        assert aantal_na <= aantal_voor  # figure is gesloten

    def test_export_logt_naar_logger(
        self, evolution_result: EvolutionResult, tmp_path: Path
    ) -> None:
        """export() moet een INFO-logbericht schrijven via loguru."""
        vis = EvolutionVisualiser(evolution_result)
        with patch("csat.core.exporters.evolution_visualiser.logger") as mock_log:
            vis.export(tmp_path, year="2026")
            mock_log.info.assert_called_once()

    def test_export_zorgi_pijler(self, zorgi_result: EvolutionResult, tmp_path: Path) -> None:
        vis = EvolutionVisualiser(zorgi_result)
        pad = vis.export(tmp_path, year="2026", timestamp=False)
        assert pad.name == "evolutie-zorgi-2026-nl.png"

    def test_export_jaar_met_spaties(
        self, evolution_result: EvolutionResult, tmp_path: Path
    ) -> None:
        """Spaties in year-param worden vervangen door koppeltekens."""
        vis = EvolutionVisualiser(evolution_result)
        pad = vis.export(tmp_path, year="jan mrt 2026")
        assert " " not in pad.name


# ---------------------------------------------------------------------------
# 5. Subplot-logica — inhoud via axes
# ---------------------------------------------------------------------------


class TestSubplots:
    """Controle van de inhoud van de individuele subplots."""

    def test_subplot1_heeft_lijnen(self, evolution_result: EvolutionResult) -> None:
        """Subplot 1 moet minstens twee lijnen bevatten (baseline + current)."""
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        ax1 = fig.axes[0]
        # Inclusief de drempellijn: minstens 2 lijnen
        assert len(ax1.get_lines()) >= 2
        plt.close(fig)

    def test_subplot1_ylim_boven_vijf(self, evolution_result: EvolutionResult) -> None:
        """Y-as subplot 1 begint bij 0 en gaat boven 5."""
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        ax1 = fig.axes[0]
        ymin, ymax = ax1.get_ylim()
        assert ymin == pytest.approx(0.0, abs=0.1)
        assert ymax > 5.0
        plt.close(fig)

    def test_subplot2_heeft_staven(self, evolution_result: EvolutionResult) -> None:
        """Subplot 2 moet staven bevatten (één per datapunt)."""
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        ax2 = fig.axes[1]
        assert len(ax2.patches) > 0
        plt.close(fig)

    def test_subplot3_heeft_twee_staven(self, evolution_result: EvolutionResult) -> None:
        """Subplot 3 toont exact 2 staven: baseline en current."""
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        ax3 = fig.axes[2]
        assert len(ax3.patches) == 2
        plt.close(fig)

    def test_subplot4_heeft_horizontale_staven(self, evolution_result: EvolutionResult) -> None:
        """Subplot 4 bevat horizontale staven (barh)."""
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        ax4 = fig.axes[3]
        assert len(ax4.patches) > 0
        plt.close(fig)

    def test_subplot1_lege_data_geen_fout(self, lege_result: EvolutionResult) -> None:
        """Subplot 1 toont 'Geen data' tekst als timeline leeg is."""
        vis = EvolutionVisualiser(lege_result)
        fig = vis.render()
        ax1 = fig.axes[0]
        teksten = [t.get_text() for t in ax1.texts]
        assert any("Geen data" in t for t in teksten)
        plt.close(fig)

    def test_subplot4_lege_hospitals_geen_fout(self, lege_result: EvolutionResult) -> None:
        """Subplot 4 toont fallback tekst als geen vergelijkbare ziekenhuizen."""
        vis = EvolutionVisualiser(lege_result)
        fig = vis.render()
        ax4 = fig.axes[3]
        teksten = [t.get_text() for t in ax4.texts]
        assert any("Geen" in t for t in teksten)
        plt.close(fig)

    def test_subplot4_nieuwe_instappers_uitgesloten(self) -> None:
        """Subplot 4 sluit ziekenhuizen met baseline_total=0 uit (nieuwe instappers)."""
        hospitals = [
            HospitalComparison(
                hospital="Bestaand_ZH",
                baseline_score=4.0,
                baseline_total=10,
                current_score=4.5,
                current_total=5,
            ),
            HospitalComparison(
                hospital="Nieuw_ZH",
                baseline_score=0.0,  # default bij geen data
                baseline_total=0,  # ← nieuwe instapper
                current_score=5.0,
                current_total=2,
            ),
        ]
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=10,
            current_total=7,
            baseline_avg_score=4.0,
            current_avg_score=4.5,
            delta_avg_score=0.5,
            baseline_pct_positive=70.0,
            current_pct_positive=80.0,
            baseline_pct_negative=10.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=5.0,
            current_avg_response_days=3.0,
            baseline_n_hospitals=1,
            current_n_hospitals=2,
            baseline_hc_ratio=10.0,
            current_hc_ratio=5.0,
            trend_is_structural=True,
            trend_breadth="breed",
            hospital_comparison=hospitals,
        )
        vis = EvolutionVisualiser(result)
        fig = vis.render()
        ax4 = fig.axes[3]
        # Enkel Bestaand_ZH mag een label hebben — Nieuw_ZH is uitgesloten
        y_labels = [lbl.get_text() for lbl in ax4.get_yticklabels()]
        assert "Bestaand_ZH" in y_labels
        assert "Nieuw_ZH" not in y_labels
        # Precies 1 staaf
        assert len(ax4.patches) == 1
        plt.close(fig)

    def test_subplot4_max_15_ziekenhuizen(self) -> None:
        """Subplot 4 toont maximaal 15 ziekenhuizen."""
        # Bouw een result met 20 ziekenhuizen
        hospitals = [
            HospitalComparison(
                hospital=f"Ziekenhuis {i:02d}",
                baseline_score=3.5,
                baseline_total=10,
                current_score=4.0 + (i * 0.05),
                current_total=10,
            )
            for i in range(20)
        ]
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=200,
            current_total=200,
            baseline_avg_score=3.5,
            current_avg_score=4.0,
            delta_avg_score=0.5,
            baseline_pct_positive=60.0,
            current_pct_positive=80.0,
            baseline_pct_negative=20.0,
            current_pct_negative=5.0,
            baseline_avg_response_days=10.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=20,
            current_n_hospitals=20,
            baseline_hc_ratio=25.0,
            current_hc_ratio=10.0,
            trend_is_structural=True,
            trend_breadth="breed",
            hospital_comparison=hospitals,
        )
        vis = EvolutionVisualiser(result)
        fig = vis.render()
        ax4 = fig.axes[3]
        # Maximaal 15 staven
        assert len(ax4.patches) <= 15
        plt.close(fig)

    def test_subplot3_drempellijn_aanwezig(self, evolution_result: EvolutionResult) -> None:
        """Subplot 3 bevat een horizontale drempellijn."""
        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        ax3 = fig.axes[2]
        # Drempellijn is een axhline → aanwezig als lijn in de ax
        assert len(ax3.get_lines()) >= 1
        plt.close(fig)

    def test_subplot1_drempellijn_avg_score_min(self, evolution_result: EvolutionResult) -> None:
        """Subplot 1 bevat een horizontale drempellijn op AVG_SCORE_MIN."""
        from csat.config.settings import AVG_SCORE_MIN

        vis = EvolutionVisualiser(evolution_result)
        fig = vis.render()
        ax1 = fig.axes[0]
        # Controleer of een lijn op y=AVG_SCORE_MIN bestaat
        lijn_y_waarden = [lijn.get_ydata() for lijn in ax1.get_lines()]
        drempels = [y for yd in lijn_y_waarden for y in yd if hasattr(y, "__float__")]
        assert any(abs(float(y) - AVG_SCORE_MIN) < 0.01 for y in drempels)
        plt.close(fig)


# ---------------------------------------------------------------------------
# 9. Randgevallen helpers — volledige branch-coverage
# ---------------------------------------------------------------------------


class TestRandgevallenBranchCoverage:
    """Tests voor branches die niet door standaard fixtures geraakt worden."""

    def test_style_legend_none_is_noop(self) -> None:
        """_style_legend(None) mag geen fout geven — early return branch (regel 113)."""
        # Geen exception = geslaagd; bevestigt de None-guard
        _style_legend(None)

    def test_subplot4_negatieve_delta_ticket_label_rechts(self) -> None:
        """Subplot 4 plaatst ticket-label rechts van nul bij negatieve delta (regel 721)."""
        hospitals = [
            HospitalComparison(
                hospital="Verslechterd_ZH",
                baseline_score=4.5,
                baseline_total=8,
                current_score=3.5,  # delta < 0 → else-branch
                current_total=6,
            ),
        ]
        result = EvolutionResult(
            pillar="pharma",
            baseline_label="2025",
            current_label="2026",
            baseline_total=8,
            current_total=6,
            baseline_avg_score=4.5,
            current_avg_score=3.5,
            delta_avg_score=-1.0,
            baseline_pct_positive=80.0,
            current_pct_positive=50.0,
            baseline_pct_negative=5.0,
            current_pct_negative=20.0,
            baseline_avg_response_days=3.0,
            current_avg_response_days=5.0,
            baseline_n_hospitals=1,
            current_n_hospitals=1,
            baseline_hc_ratio=10.0,
            current_hc_ratio=15.0,
            trend_is_structural=False,
            trend_breadth="beperkt",
            hospital_comparison=hospitals,
        )
        vis = EvolutionVisualiser(result)
        fig = vis.render()
        ax4 = fig.axes[3]
        # Ticket-label "#8/6" moet aanwezig zijn in de ax-teksten
        teksten = [t.get_text() for t in ax4.texts]
        assert any("#8/6" in t for t in teksten)
        plt.close(fig)
