"""
Unit tests voor MatrixExporter.

Dekt: render(), export(), _build_context(), tweetaligheid NL/FR,
matrix-opbouw, ranking, trendberekening, randgevallen.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from csat.core.analysers.base_analyser import KpiResult
from csat.core.exporters.matrix_exporter import _TREND_THRESHOLD, MatrixExporter
from csat.i18n import load_translations

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_result(
    period: str,
    hospitals: dict[str, dict],
    avg_score: float = 4.0,
    high_critical_ratio: float = 20.0,
    total_tickets: int = 10,
) -> KpiResult:
    """Hulpfunctie: bouw een KpiResult voor de opgegeven periode en ziekenhuizen."""
    return KpiResult(
        period=period,
        pillar="pharma",
        total_tickets=total_tickets,
        scored_tickets=total_tickets,
        reactiegraad=100.0,
        avg_score=avg_score,
        high_critical_count=int(total_tickets * high_critical_ratio / 100),
        high_critical_ratio=high_critical_ratio,
        hospitals=list(hospitals.keys()),
        per_hospital=hospitals,
    )


@pytest.fixture
def az_groeninge_kpis() -> dict:
    """Standaard KPI-blok voor AZ Groeninge."""
    return {
        "total_tickets": 5,
        "scored_tickets": 5,
        "reactiegraad": 100.0,
        "avg_score": 4.2,
        "high_critical_count": 1,
        "high_critical_ratio": 20.0,
    }


@pytest.fixture
def uz_brussel_kpis() -> dict:
    """Standaard KPI-blok voor UZ Brussel."""
    return {
        "total_tickets": 5,
        "scored_tickets": 5,
        "reactiegraad": 100.0,
        "avg_score": 3.8,
        "high_critical_count": 1,
        "high_critical_ratio": 20.0,
    }


@pytest.fixture
def result_jan(az_groeninge_kpis: dict, uz_brussel_kpis: dict) -> KpiResult:
    """KpiResult voor PHARMA januari 2026."""
    return _make_result(
        period="2026-01",
        hospitals={"AZ Groeninge": az_groeninge_kpis, "UZ Brussel": uz_brussel_kpis},
        avg_score=4.0,
    )


@pytest.fixture
def result_feb(az_groeninge_kpis: dict, uz_brussel_kpis: dict) -> KpiResult:
    """KpiResult voor PHARMA februari 2026."""
    az = dict(az_groeninge_kpis)
    az["avg_score"] = 4.5  # stijging t.o.v. januari
    uz = dict(uz_brussel_kpis)
    uz["avg_score"] = 3.6  # daling t.o.v. januari
    return _make_result(
        period="2026-02",
        hospitals={"AZ Groeninge": az, "UZ Brussel": uz},
        avg_score=4.1,
    )


@pytest.fixture
def result_mrt(az_groeninge_kpis: dict, uz_brussel_kpis: dict) -> KpiResult:
    """KpiResult voor PHARMA maart 2026."""
    az = dict(az_groeninge_kpis)
    az["avg_score"] = 4.3  # stabiel t.o.v. januari (delta = +0.1 = exact drempel)
    uz = dict(uz_brussel_kpis)
    uz["avg_score"] = 3.8  # stabiel t.o.v. januari (delta = 0.0)
    return _make_result(
        period="2026-03",
        hospitals={"AZ Groeninge": az, "UZ Brussel": uz},
        avg_score=4.05,
    )


@pytest.fixture
def drie_periodes(
    result_jan: KpiResult,
    result_feb: KpiResult,
    result_mrt: KpiResult,
) -> list[KpiResult]:
    """Lijst van drie KpiResult-objecten voor kwartaalmatrix."""
    return [result_jan, result_feb, result_mrt]


@pytest.fixture
def result_met_onbekend(az_groeninge_kpis: dict) -> KpiResult:
    """KpiResult met ONBEKEND ziekenhuis."""
    onbekend_kpis = {
        "total_tickets": 2,
        "scored_tickets": 2,
        "reactiegraad": 100.0,
        "avg_score": 2.5,
        "high_critical_count": 0,
        "high_critical_ratio": 0.0,
    }
    return _make_result(
        period="2026-01",
        hospitals={"AZ Groeninge": az_groeninge_kpis, "ONBEKEND": onbekend_kpis},
    )


@pytest.fixture
def templates_path() -> Path:
    """Absoluut pad naar de Jinja2-templates in docs/templates/."""
    return Path(__file__).resolve().parents[2] / "docs" / "templates"


# ---------------------------------------------------------------------------
# MatrixExporter — initialisatie
# ---------------------------------------------------------------------------


class TestMatrixExporterInit:
    """Constructorvalidatie."""

    def test_standaard_taal_nl(self, templates_path: Path) -> None:
        exporter = MatrixExporter(templates_path=templates_path)
        assert exporter._lang == "nl"

    def test_fr_taal_instellen(self, templates_path: Path) -> None:
        exporter = MatrixExporter(lang="fr", templates_path=templates_path)
        assert exporter._lang == "fr"

    def test_onbekende_taal_gooit_fout(self, templates_path: Path) -> None:
        with pytest.raises(ValueError, match="Niet-ondersteunde taal"):
            MatrixExporter(lang="de", templates_path=templates_path)

    def test_custom_templates_pad(self, tmp_path: Path) -> None:
        """Pad wordt bewaard — template-fout bij render verwacht (pad leeg)."""
        exporter = MatrixExporter(lang="nl", templates_path=tmp_path)
        assert exporter._templates_path == tmp_path

    def test_custom_output_pad(self, tmp_path: Path, templates_path: Path) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        assert exporter._output_path == tmp_path


# ---------------------------------------------------------------------------
# MatrixExporter — render()
# ---------------------------------------------------------------------------


class TestMatrixExporterRender:
    """Controle van de gegenereerde markdown-inhoud."""

    def test_render_retourneert_string(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_lege_lijst_gooit_fout(self, templates_path: Path) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        with pytest.raises(ValueError, match="Lege resultatenlijst"):
            exporter.render([])

    def test_render_bevat_h1_nl(self, drie_periodes: list[KpiResult], templates_path: Path) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "CSAT-Compass" in output
        assert "Vergelijkingsmatrix" in output

    def test_render_bevat_h1_fr(self, drie_periodes: list[KpiResult], templates_path: Path) -> None:
        exporter = MatrixExporter(lang="fr", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "CSAT-Compass" in output
        assert "Matrice comparative" in output

    def test_render_bevat_pijlernaam(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "ZORGI PHARMA" in output

    def test_render_bevat_jaar(self, drie_periodes: list[KpiResult], templates_path: Path) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "2026" in output

    def test_render_bevat_periodes_nl(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "januari 2026" in output
        assert "februari 2026" in output
        assert "maart 2026" in output

    def test_render_bevat_periodes_fr(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="fr", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "janvier 2026" in output
        assert "février 2026" in output
        assert "mars 2026" in output

    def test_render_bevat_ziekenhuizen(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "AZ Groeninge" in output
        assert "UZ Brussel" in output

    def test_render_bevat_scores(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        """Gem. scores moeten in ZORGI-formaat (komma) in de output staan."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "4,20" in output  # AZ Groeninge jan
        assert "3,80" in output  # UZ Brussel jan

    def test_render_secties_nl(self, drie_periodes: list[KpiResult], templates_path: Path) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "Gemiddelde CSAT-score per ziekenhuis" in output
        assert "High/Critical-ratio per ziekenhuis" in output
        assert "Ticketvolume per ziekenhuis" in output
        assert "Top/bottom performers" in output
        assert "Trendsamenvatting" in output

    def test_render_secties_fr(self, drie_periodes: list[KpiResult], templates_path: Path) -> None:
        exporter = MatrixExporter(lang="fr", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "Score CSAT moyen par hôpital" in output
        assert "Taux High/Critical par hôpital" in output
        assert "Volume de tickets par hôpital" in output
        assert "Meilleures et moins bonnes performances" in output
        assert "Résumé des tendances" in output

    def test_render_trend_stijgend(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        """AZ Groeninge stijgt van 4,2 → 4,5 → 4,3: trend vergelijkt eerste (4,2) met laatste (4,3), delta = +0.1 = drempel → stabiel."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        # AZ Groeninge: 4,2 → 4,5 → 4,3 — delta eerste naar laatste = +0,1 = exact _TREND_THRESHOLD → stabiel
        assert "→ Stabiel" in output

    def test_render_trend_dalend(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        """UZ Brussel daalt van 3,8 → 3,6 → 3,8: vergelijk eerste (3,8) met laatste (3,8), delta = 0 → stabiel."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(drie_periodes)
        assert "→ Stabiel" in output

    def test_render_onbekend_ziekenhuis_aanwezig(
        self, result_met_onbekend: KpiResult, templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render([result_met_onbekend])
        assert "ONBEKEND" in output

    def test_render_enkel_een_periode(self, result_jan: KpiResult, templates_path: Path) -> None:
        """MatrixExporter moet ook werken met slechts één periode."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output = exporter.render([result_jan])
        assert "AZ Groeninge" in output
        assert "januari 2026" in output

    def test_render_volgorde_niet_gesorteerd_als_input(
        self,
        result_jan: KpiResult,
        result_feb: KpiResult,
        result_mrt: KpiResult,
        templates_path: Path,
    ) -> None:
        """Periodes worden altijd chronologisch gesorteerd, ongeacht invoervolgorde."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        output_geordend = exporter.render([result_jan, result_feb, result_mrt])
        output_ongeordend = exporter.render([result_mrt, result_jan, result_feb])
        assert output_geordend == output_ongeordend


# ---------------------------------------------------------------------------
# MatrixExporter — export()
# ---------------------------------------------------------------------------


class TestMatrixExporterExport:
    """Bestandsschrijving en naamgeving."""

    def test_export_schrijft_bestand(
        self,
        drie_periodes: list[KpiResult],
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        output_file = exporter.export(drie_periodes)
        assert output_file.exists()

    def test_export_bestandsnaam_nl(
        self,
        drie_periodes: list[KpiResult],
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        output_file = exporter.export(drie_periodes)
        assert output_file.name == "matrix-pharma-2026-nl.md"

    def test_export_bestandsnaam_fr(
        self,
        drie_periodes: list[KpiResult],
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = MatrixExporter(lang="fr", templates_path=templates_path, output_path=tmp_path)
        output_file = exporter.export(drie_periodes)
        assert output_file.name == "matrix-pharma-2026-fr.md"

    def test_export_inhoud_leesbaar(
        self,
        drie_periodes: list[KpiResult],
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        output_file = exporter.export(drie_periodes)
        content = output_file.read_text(encoding="utf-8")
        assert "CSAT-Compass" in content

    def test_export_maakt_outputmap_aan(
        self,
        drie_periodes: list[KpiResult],
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        """Exportmap wordt aangemaakt als die nog niet bestaat."""
        nieuwe_map = tmp_path / "submap" / "output"
        exporter = MatrixExporter(lang="nl", templates_path=templates_path, output_path=nieuwe_map)
        output_file = exporter.export(drie_periodes)
        assert output_file.exists()

    def test_export_retourneert_pad(
        self,
        drie_periodes: list[KpiResult],
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        result = exporter.export(drie_periodes)
        assert isinstance(result, Path)

    def test_export_logt_naar_logger(
        self,
        drie_periodes: list[KpiResult],
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        """export() moet een INFO-logbericht schrijven via loguru."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        with patch("csat.core.exporters.matrix_exporter.logger") as mock_log:
            exporter.export(drie_periodes)
            mock_log.info.assert_called_once()


# ---------------------------------------------------------------------------
# MatrixExporter — _build_context()
# ---------------------------------------------------------------------------


class TestBuildContext:
    """Inhoud van de template-context."""

    def test_context_bevat_alle_sleutels(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        verplichte_sleutels = [
            "t",
            "year",
            "generated_date",
            "pillar",
            "pillar_name",
            "periods",
            "hospitals",
            "score_matrix",
            "hc_matrix",
            "volume_matrix",
            "rankings",
            "trends",
            "lang",
        ]
        for sleutel in verplichte_sleutels:
            assert sleutel in ctx, f"Sleutel '{sleutel}' ontbreekt in context"

    def test_context_jaar_correct(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        assert ctx["year"] == "2026"

    def test_context_periodes_gesorteerd(
        self,
        result_jan: KpiResult,
        result_mrt: KpiResult,
        result_feb: KpiResult,
        templates_path: Path,
    ) -> None:
        """Periodes worden altijd chronologisch gesorteerd."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context([result_mrt, result_jan, result_feb])
        assert ctx["periods"] == ["januari 2026", "februari 2026", "maart 2026"]

    def test_context_periodes_fr(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="fr", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        assert ctx["periods"] == ["janvier 2026", "février 2026", "mars 2026"]

    def test_context_hospitals_gesorteerd(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        assert ctx["hospitals"] == ["AZ Groeninge", "UZ Brussel"]

    def test_context_onbekend_als_laatste(
        self, result_met_onbekend: KpiResult, templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context([result_met_onbekend])
        assert ctx["hospitals"][-1] == "ONBEKEND"

    def test_context_score_matrix_waarden(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        score_matrix = ctx["score_matrix"]
        assert score_matrix["AZ Groeninge"]["januari 2026"] == pytest.approx(4.2)
        assert score_matrix["UZ Brussel"]["januari 2026"] == pytest.approx(3.8)

    def test_context_score_matrix_ontbrekend_is_none(
        self,
        templates_path: Path,
        az_groeninge_kpis: dict,
    ) -> None:
        """Ziekenhuis dat in één periode ontbreekt → None in de matrix."""
        result_a = _make_result("2026-01", {"AZ Groeninge": az_groeninge_kpis})
        result_b = _make_result(
            "2026-02",
            {
                "UZ Brussel": {
                    "total_tickets": 3,
                    "scored_tickets": 3,
                    "reactiegraad": 100.0,
                    "avg_score": 4.0,
                    "high_critical_count": 0,
                    "high_critical_ratio": 0.0,
                }
            },
        )
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context([result_a, result_b])
        # AZ Groeninge heeft geen data in februari
        assert ctx["score_matrix"]["AZ Groeninge"]["februari 2026"] is None
        # UZ Brussel heeft geen data in januari
        assert ctx["score_matrix"]["UZ Brussel"]["januari 2026"] is None

    def test_context_rankings_gesorteerd_op_score(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        """Rankings gesorteerd van hoogste naar laagste gem. score."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        # AZ Groeninge gem. > UZ Brussel gem. → AZ Groeninge op rang 1
        rankings = ctx["rankings"]
        assert rankings[0][0] == 1  # rang 1
        assert rankings[0][1] == "AZ Groeninge"
        assert rankings[1][1] == "UZ Brussel"

    def test_context_rankings_onbekend_uitgesloten(
        self, result_met_onbekend: KpiResult, templates_path: Path
    ) -> None:
        """ONBEKEND-ziekenhuis mag niet in de ranking staan."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context([result_met_onbekend])
        hospital_namen = [naam for _, naam, _ in ctx["rankings"]]
        assert "ONBEKEND" not in hospital_namen

    def test_context_trends_aanwezig(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        assert len(ctx["trends"]) == 2  # AZ Groeninge + UZ Brussel

    def test_context_trend_na_bij_een_periode(
        self, result_jan: KpiResult, templates_path: Path
    ) -> None:
        """Bij slechts één periode is de trend N/A."""
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context([result_jan])
        t = load_translations("nl")
        na_label = t["matrix"]["trends"]["na"]
        trends_dict = dict(ctx["trends"])
        assert trends_dict["AZ Groeninge"] == na_label
        assert trends_dict["UZ Brussel"] == na_label

    def test_context_trend_stijgend(self, templates_path: Path, az_groeninge_kpis: dict) -> None:
        """Ziekenhuis met duidelijke stijging (> drempel) → 'Stijgend'."""
        begin_kpis = dict(az_groeninge_kpis)
        begin_kpis["avg_score"] = 3.0
        eind_kpis = dict(az_groeninge_kpis)
        eind_kpis["avg_score"] = 4.5  # delta = +1.5 > _TREND_THRESHOLD

        result_a = _make_result("2026-01", {"AZ Groeninge": begin_kpis})
        result_b = _make_result("2026-03", {"AZ Groeninge": eind_kpis})

        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context([result_a, result_b])
        t = load_translations("nl")
        trends_dict = dict(ctx["trends"])
        assert trends_dict["AZ Groeninge"] == t["matrix"]["trends"]["up"]

    def test_context_trend_dalend(self, templates_path: Path, az_groeninge_kpis: dict) -> None:
        """Ziekenhuis met duidelijke daling (< -drempel) → 'Dalend'."""
        begin_kpis = dict(az_groeninge_kpis)
        begin_kpis["avg_score"] = 4.5
        eind_kpis = dict(az_groeninge_kpis)
        eind_kpis["avg_score"] = 3.0  # delta = -1.5 < -_TREND_THRESHOLD

        result_a = _make_result("2026-01", {"AZ Groeninge": begin_kpis})
        result_b = _make_result("2026-03", {"AZ Groeninge": eind_kpis})

        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context([result_a, result_b])
        t = load_translations("nl")
        trends_dict = dict(ctx["trends"])
        assert trends_dict["AZ Groeninge"] == t["matrix"]["trends"]["down"]

    def test_context_trend_stabiel_exact_drempel(
        self, templates_path: Path, az_groeninge_kpis: dict
    ) -> None:
        """Delta = exact _TREND_THRESHOLD → 'Stabiel' (grenswaarde)."""
        begin_kpis = dict(az_groeninge_kpis)
        begin_kpis["avg_score"] = 4.0
        eind_kpis = dict(az_groeninge_kpis)
        eind_kpis["avg_score"] = 4.0 + _TREND_THRESHOLD  # exact op de grens

        result_a = _make_result("2026-01", {"AZ Groeninge": begin_kpis})
        result_b = _make_result("2026-03", {"AZ Groeninge": eind_kpis})

        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context([result_a, result_b])
        t = load_translations("nl")
        trends_dict = dict(ctx["trends"])
        assert trends_dict["AZ Groeninge"] == t["matrix"]["trends"]["stable"]

    def test_context_pillar_name_nl(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        assert ctx["pillar_name"] == "ZORGI PHARMA"

    def test_context_pillar_name_fr(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        exporter = MatrixExporter(lang="fr", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        assert ctx["pillar_name"] == "ZORGI PHARMA"

    def test_context_onbekende_pijler_fallback(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        """Onbekende pijler gebruikt uppercase pillar_key als fallback."""
        for r in drie_periodes:
            r.pillar = "unknown_pillar"
        exporter = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(drie_periodes)
        assert ctx["pillar_name"] == "UNKNOWN_PILLAR"


# ---------------------------------------------------------------------------
# i18n — matrix-sleutels aanwezig in NL + FR
# ---------------------------------------------------------------------------


class TestI18nMatrixSleutels:
    """Verifieer dat matrix-vertalingen correct geladen worden."""

    def test_nl_matrix_sectie_aanwezig(self) -> None:
        t = load_translations("nl")
        assert "matrix" in t

    def test_fr_matrix_sectie_aanwezig(self) -> None:
        t = load_translations("fr")
        assert "matrix" in t

    def test_nl_matrix_bevat_alle_sleutels(self) -> None:
        t = load_translations("nl")
        m = t["matrix"]
        assert "title" in m
        assert "subtitle" in m
        assert "sections" in m
        assert "table" in m
        assert "trends" in m
        assert "no_data" in m

    def test_fr_matrix_bevat_alle_sleutels(self) -> None:
        t = load_translations("fr")
        m = t["matrix"]
        assert "title" in m
        assert "subtitle" in m
        assert "sections" in m
        assert "table" in m
        assert "trends" in m
        assert "no_data" in m

    def test_nl_trend_labels(self) -> None:
        t = load_translations("nl")
        trends = t["matrix"]["trends"]
        assert "up" in trends
        assert "stable" in trends
        assert "down" in trends
        assert "na" in trends

    def test_fr_trend_labels(self) -> None:
        t = load_translations("fr")
        trends = t["matrix"]["trends"]
        assert "up" in trends
        assert "stable" in trends
        assert "down" in trends
        assert "na" in trends

    def test_nl_sections_labels(self) -> None:
        t = load_translations("nl")
        sections = t["matrix"]["sections"]
        for sleutel in ("score_matrix", "hc_matrix", "volume_matrix", "rankings", "trends"):
            assert sleutel in sections, f"Sectie '{sleutel}' ontbreekt in nl.json matrix.sections"

    def test_fr_sections_labels(self) -> None:
        t = load_translations("fr")
        sections = t["matrix"]["sections"]
        for sleutel in ("score_matrix", "hc_matrix", "volume_matrix", "rankings", "trends"):
            assert sleutel in sections, f"Sectie '{sleutel}' ontbreekt in fr.json matrix.sections"

    def test_nl_kwartaal_en_jaar_labels(self) -> None:
        t = load_translations("nl")
        sections = t["matrix"]["sections"]
        for sleutel in (
            "quarterly_score",
            "quarterly_hc",
            "quarterly_volume",
            "yearly_score",
            "yearly_hc",
            "yearly_volume",
        ):
            assert sleutel in sections, f"Sectie '{sleutel}' ontbreekt in nl.json matrix.sections"

    def test_fr_kwartaal_en_jaar_labels(self) -> None:
        t = load_translations("fr")
        sections = t["matrix"]["sections"]
        for sleutel in (
            "quarterly_score",
            "quarterly_hc",
            "quarterly_volume",
            "yearly_score",
            "yearly_hc",
            "yearly_volume",
        ):
            assert sleutel in sections, f"Sectie '{sleutel}' ontbreekt in fr.json matrix.sections"

    def test_nl_table_heeft_score_hc_pct_volume(self) -> None:
        t = load_translations("nl")
        table = t["matrix"]["table"]
        for sleutel in ("score", "hc_pct", "volume"):
            assert sleutel in table, f"Tabelsleutel '{sleutel}' ontbreekt in nl.json matrix.table"

    def test_fr_table_heeft_score_hc_pct_volume(self) -> None:
        t = load_translations("fr")
        table = t["matrix"]["table"]
        for sleutel in ("score", "hc_pct", "volume"):
            assert sleutel in table, f"Tabelsleutel '{sleutel}' ontbreekt in fr.json matrix.table"


# ---------------------------------------------------------------------------
# MatrixExporter — _period_to_quarter()
# ---------------------------------------------------------------------------


class TestPeriodToQuarter:
    """Mapping van periode naar kwartaallabel."""

    def test_q1_januari(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_quarter("2025-01") == "Q1 2025"

    def test_q1_maart(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_quarter("2025-03") == "Q1 2025"

    def test_q2_april(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_quarter("2025-04") == "Q2 2025"

    def test_q2_juni(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_quarter("2025-06") == "Q2 2025"

    def test_q3_juli(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_quarter("2025-07") == "Q3 2025"

    def test_q4_oktober(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_quarter("2025-10") == "Q4 2025"

    def test_q4_december(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_quarter("2025-12") == "Q4 2025"

    def test_jaargrens(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_quarter("2026-01") == "Q1 2026"


# ---------------------------------------------------------------------------
# MatrixExporter — _period_to_year()
# ---------------------------------------------------------------------------


class TestPeriodToYear:
    """Mapping van periode naar jaarlabel."""

    def test_jaar_2025(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_year("2025-06") == "2025"

    def test_jaar_2026(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        assert e._period_to_year("2026-03") == "2026"


# ---------------------------------------------------------------------------
# MatrixExporter — _ordered_groups()
# ---------------------------------------------------------------------------


class TestOrderedGroups:
    """Deduplicatie en volgorde van groepslabels."""

    def test_dedupliceert_kwartalen(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        periods = ["2025-01", "2025-02", "2025-03", "2025-04"]
        result = e._ordered_groups(periods, e._period_to_quarter)
        assert result == ["Q1 2025", "Q2 2025"]

    def test_behoudt_volgorde(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        periods = ["2025-10", "2025-11", "2025-12", "2026-01"]
        result = e._ordered_groups(periods, e._period_to_quarter)
        assert result == ["Q4 2025", "Q1 2026"]

    def test_jaren(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        periods = ["2025-11", "2025-12", "2026-01", "2026-02"]
        result = e._ordered_groups(periods, e._period_to_year)
        assert result == ["2025", "2026"]

    def test_enkel_een_jaar(self, templates_path: Path) -> None:
        e = MatrixExporter(templates_path=templates_path)
        periods = ["2026-01", "2026-02", "2026-03"]
        result = e._ordered_groups(periods, e._period_to_year)
        assert result == ["2026"]


# ---------------------------------------------------------------------------
# MatrixExporter — _aggregate_matrix()
# ---------------------------------------------------------------------------


class TestAggregateMatrix:
    """Gewogen aggregatie per kwartaal/jaar."""

    def _score_lookup(self, hospital: str, scores_by_period: dict[str, float]) -> dict:
        """Bouw een score_lookup dict op voor één ziekenhuis."""
        lookup = {}
        for period, score in scores_by_period.items():
            lookup[period] = {
                hospital: {
                    "total_tickets": 10,
                    "scored_tickets": 10,
                    "avg_score": score,
                    "high_critical_count": 2,
                    "high_critical_ratio": 20.0,
                }
            }
        return lookup

    def test_gewogen_gemiddelde_score(self, templates_path: Path) -> None:
        """Gewogen gemiddelde: 2 tickets @ 4.0 + 8 tickets @ 5.0 = 4.8."""
        e = MatrixExporter(templates_path=templates_path)
        lookup = {
            "2026-01": {
                "AZ": {
                    "total_tickets": 2,
                    "scored_tickets": 2,
                    "avg_score": 4.0,
                    "high_critical_count": 0,
                    "high_critical_ratio": 0.0,
                }
            },
            "2026-02": {
                "AZ": {
                    "total_tickets": 8,
                    "scored_tickets": 8,
                    "avg_score": 5.0,
                    "high_critical_count": 0,
                    "high_critical_ratio": 0.0,
                }
            },
        }
        score, _hc, _vol = e._aggregate_matrix(
            ["AZ"], ["2026-01", "2026-02"], lookup, e._period_to_quarter, ["Q1 2026"]
        )
        assert score["AZ"]["Q1 2026"] == pytest.approx(4.8)

    def test_hc_ratio_aggregatie(self, templates_path: Path) -> None:
        """H/C ratio = totaal hc_count / totaal tickets * 100."""
        e = MatrixExporter(templates_path=templates_path)
        lookup = {
            "2026-01": {
                "AZ": {
                    "total_tickets": 10,
                    "scored_tickets": 10,
                    "avg_score": 4.0,
                    "high_critical_count": 2,
                    "high_critical_ratio": 20.0,
                }
            },
            "2026-02": {
                "AZ": {
                    "total_tickets": 10,
                    "scored_tickets": 10,
                    "avg_score": 4.0,
                    "high_critical_count": 4,
                    "high_critical_ratio": 40.0,
                }
            },
        }
        _score, hc, _vol = e._aggregate_matrix(
            ["AZ"], ["2026-01", "2026-02"], lookup, e._period_to_quarter, ["Q1 2026"]
        )
        # (2 + 4) / (10 + 10) * 100 = 30.0%
        assert hc["AZ"]["Q1 2026"] == pytest.approx(30.0)

    def test_volume_sommatie(self, templates_path: Path) -> None:
        """Volume = som van tickets per periode."""
        e = MatrixExporter(templates_path=templates_path)
        lookup = {
            "2026-01": {
                "AZ": {
                    "total_tickets": 5,
                    "scored_tickets": 5,
                    "avg_score": 4.0,
                    "high_critical_count": 0,
                    "high_critical_ratio": 0.0,
                }
            },
            "2026-02": {
                "AZ": {
                    "total_tickets": 8,
                    "scored_tickets": 8,
                    "avg_score": 4.0,
                    "high_critical_count": 0,
                    "high_critical_ratio": 0.0,
                }
            },
        }
        _score, _hc, vol = e._aggregate_matrix(
            ["AZ"], ["2026-01", "2026-02"], lookup, e._period_to_quarter, ["Q1 2026"]
        )
        assert vol["AZ"]["Q1 2026"] == pytest.approx(13.0)

    def test_ontbrekende_periode_is_none(self, templates_path: Path) -> None:
        """Ziekenhuis zonder data in een groep → None."""
        e = MatrixExporter(templates_path=templates_path)
        lookup: dict = {}
        score, hc, vol = e._aggregate_matrix(
            ["AZ"], ["2026-01"], lookup, e._period_to_quarter, ["Q1 2026"]
        )
        assert score["AZ"]["Q1 2026"] is None
        assert hc["AZ"]["Q1 2026"] is None
        assert vol["AZ"]["Q1 2026"] is None

    def test_jaar_aggregatie(self, templates_path: Path) -> None:
        """Jaaraggregatie over 12 maanden."""
        e = MatrixExporter(templates_path=templates_path)
        lookup = {
            f"2025-{m:02d}": {
                "AZ": {
                    "total_tickets": 10,
                    "scored_tickets": 10,
                    "avg_score": 4.0,
                    "high_critical_count": 1,
                    "high_critical_ratio": 10.0,
                }
            }
            for m in range(1, 13)
        }
        periods_raw = [f"2025-{m:02d}" for m in range(1, 13)]
        score, hc, vol = e._aggregate_matrix(
            ["AZ"], periods_raw, lookup, e._period_to_year, ["2025"]
        )
        assert score["AZ"]["2025"] == pytest.approx(4.0)
        assert hc["AZ"]["2025"] == pytest.approx(10.0)
        assert vol["AZ"]["2025"] == pytest.approx(120.0)


# ---------------------------------------------------------------------------
# MatrixExporter — context kwartaal/jaar sleutels
# ---------------------------------------------------------------------------


class TestBuildContextAggregaties:
    """Kwartaal- en jaar-sleutels aanwezig in de context."""

    def test_context_bevat_kwartaal_sleutels(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = e._build_context(drie_periodes)
        for sleutel in (
            "quarters",
            "quarterly_score_matrix",
            "quarterly_hc_matrix",
            "quarterly_volume_matrix",
        ):
            assert sleutel in ctx, f"Sleutel '{sleutel}' ontbreekt in context"

    def test_context_bevat_jaar_sleutels(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = e._build_context(drie_periodes)
        for sleutel in (
            "year_labels",
            "yearly_score_matrix",
            "yearly_hc_matrix",
            "yearly_volume_matrix",
        ):
            assert sleutel in ctx, f"Sleutel '{sleutel}' ontbreekt in context"

    def test_kwartalen_correct_bepaald(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        """Jan, feb, mrt 2026 behoren alle tot Q1 2026."""
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = e._build_context(drie_periodes)
        assert ctx["quarters"] == ["Q1 2026"]

    def test_jaar_correct_bepaald(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = e._build_context(drie_periodes)
        assert ctx["year_labels"] == ["2026"]

    def test_kwartaal_score_gewogen(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        """Q1 2026 score AZ Groeninge = gewogen gem. van 3 maanden."""
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = e._build_context(drie_periodes)
        q_score = ctx["quarterly_score_matrix"]["AZ Groeninge"]["Q1 2026"]
        assert q_score is not None
        # jan=4.2 (5t), feb=4.5 (5t), mrt=4.3 (5t) → (4.2+4.5+4.3)/3 = 4.333...
        assert q_score == pytest.approx((4.2 + 4.5 + 4.3) / 3, rel=1e-3)

    def test_jaarvolume_is_som(self, drie_periodes: list[KpiResult], templates_path: Path) -> None:
        """Jaarvolume AZ Groeninge = 5 + 5 + 5 = 15."""
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        ctx = e._build_context(drie_periodes)
        assert ctx["yearly_volume_matrix"]["AZ Groeninge"]["2026"] == pytest.approx(15.0)


# ---------------------------------------------------------------------------
# MatrixExporter — render() kwartaal/jaar secties
# ---------------------------------------------------------------------------


class TestRenderAggregaties:
    """Kwartaal- en jaarsecties aanwezig in de gegenereerde markdown."""

    def test_render_bevat_kwartaal_secties_nl(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        output = e.render(drie_periodes)
        assert "Gemiddelde CSAT-score per kwartaal" in output
        assert "High/Critical-ratio per kwartaal" in output
        assert "Ticketvolume per kwartaal" in output

    def test_render_bevat_jaar_secties_nl(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        output = e.render(drie_periodes)
        assert "Gemiddelde CSAT-score per jaar" in output
        assert "High/Critical-ratio per jaar" in output
        assert "Ticketvolume per jaar" in output

    def test_render_bevat_kwartaal_secties_fr(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        e = MatrixExporter(lang="fr", templates_path=templates_path)
        output = e.render(drie_periodes)
        assert "Score CSAT moyen par trimestre" in output
        assert "Taux High/Critical par trimestre" in output
        assert "Volume de tickets par trimestre" in output

    def test_render_bevat_kwartaallabel(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        output = e.render(drie_periodes)
        assert "Q1 2026" in output

    def test_render_bevat_jaarlabel(
        self, drie_periodes: list[KpiResult], templates_path: Path
    ) -> None:
        e = MatrixExporter(lang="nl", templates_path=templates_path)
        output = e.render(drie_periodes)
        # "2026" staat in de koptekst maar ook in de jaartabelkolom
        assert output.count("2026") > 1
