"""
Unit tests voor ReportExporter en i18n-hulpfuncties.

Dekt: render(), export(), _build_context(), hulpfuncties formattering,
load_translations(), tweetaligheid NL/FR, randgevallen.
"""

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from csat.core.analysers.base_analyser import KpiResult
from csat.core.exporters.report_exporter import (
    ReportExporter,
    _format_date,
    _format_mom,
    _format_number,
    _format_period_label,
)
from csat.i18n import load_translations

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def pharma_result() -> KpiResult:
    """KpiResult voor PHARMA januari 2026 — standaard testgeval."""
    result = KpiResult(
        period="2026-01",
        pillar="pharma",
        total_tickets=6,
        scored_tickets=5,
        reactiegraad=100.0,
        avg_score=3.80,
        high_critical_count=2,
        high_critical_ratio=33.3,
        hospitals=["AZ Groeninge", "UZ Brussel"],
        per_hospital={
            "AZ Groeninge": {
                "total_tickets": 3,
                "scored_tickets": 3,
                "reactiegraad": 100.0,
                "avg_score": 4.0,
                "high_critical_count": 2,
                "high_critical_ratio": 66.7,
            },
            "UZ Brussel": {
                "total_tickets": 3,
                "scored_tickets": 2,
                "reactiegraad": 66.7,
                "avg_score": 3.5,
                "high_critical_count": 0,
                "high_critical_ratio": 0.0,
            },
        },
    )
    # MoM-trend als extra attribuut (zoals PillarAnalyser dit instelt)
    result.mom_score = 0.2  # type: ignore[attr-defined]
    result.mom_reactiegraad = 0.0  # type: ignore[attr-defined]
    return result


@pytest.fixture
def result_with_unknown(pharma_result: KpiResult) -> KpiResult:
    """KpiResult met een ONBEKEND ziekenhuis."""
    pharma_result.per_hospital["ONBEKEND"] = {
        "total_tickets": 2,
        "scored_tickets": 2,
        "reactiegraad": 100.0,
        "avg_score": 2.5,
        "high_critical_count": 0,
        "high_critical_ratio": 0.0,
    }
    pharma_result.hospitals.append("ONBEKEND")
    return pharma_result


@pytest.fixture
def empty_result() -> KpiResult:
    """KpiResult zonder tickets of ziekenhuizen (randgeval)."""
    return KpiResult(
        period="2026-02",
        pillar="pharma",
        total_tickets=0,
        scored_tickets=0,
        reactiegraad=0.0,
        avg_score=0.0,
        high_critical_count=0,
        high_critical_ratio=0.0,
        hospitals=[],
        per_hospital={},
    )


@pytest.fixture
def templates_path() -> Path:
    """Absoluut pad naar de Jinja2-templates in docs/templates/."""
    # Navigeer vanuit dit testbestand naar de repo-root
    return Path(__file__).resolve().parents[2] / "docs" / "templates"


# ---------------------------------------------------------------------------
# _format_number
# ---------------------------------------------------------------------------


class TestFormatNumber:
    """Formattering van getallen conform ZORGI-standaard (punt/komma)."""

    def test_geheel_getal_zonder_scheider(self) -> None:
        assert _format_number(75.0, 0) == "75"

    def test_duizendtal_scheider(self) -> None:
        assert _format_number(1234.0, 0) == "1.234"

    def test_decimalen_komma(self) -> None:
        assert _format_number(3.8, 2) == "3,80"

    def test_grote_waarde_met_decimalen(self) -> None:
        assert _format_number(1234.5, 1) == "1.234,5"

    def test_nul_waarde(self) -> None:
        assert _format_number(0.0, 1) == "0,0"

    def test_percentage(self) -> None:
        assert _format_number(15.3, 1) == "15,3"

    def test_standaard_decimalen_is_1(self) -> None:
        assert _format_number(3.8) == "3,8"


# ---------------------------------------------------------------------------
# _format_mom
# ---------------------------------------------------------------------------


class TestFormatMom:
    """MoM-trendformattering met prefix."""

    def test_positieve_waarde(self) -> None:
        assert _format_mom(0.2) == "+0,2"

    def test_negatieve_waarde(self) -> None:
        assert _format_mom(-0.5) == "-0,5"

    def test_nul_krijgt_plus(self) -> None:
        assert _format_mom(0.0) == "+0,0"

    def test_grote_positieve_waarde(self) -> None:
        assert _format_mom(1.5) == "+1,5"


# ---------------------------------------------------------------------------
# _format_date
# ---------------------------------------------------------------------------


class TestFormatDate:
    """Datumformattering DD/MM/YYYY."""

    def test_standaard_datum(self) -> None:
        assert _format_date(date(2026, 3, 20)) == "20/03/2026"

    def test_eerste_dag_maand(self) -> None:
        assert _format_date(date(2026, 1, 1)) == "01/01/2026"

    def test_december(self) -> None:
        assert _format_date(date(2025, 12, 31)) == "31/12/2025"


# ---------------------------------------------------------------------------
# _format_period_label
# ---------------------------------------------------------------------------


class TestFormatPeriodLabel:
    """Periodestring omzetten naar leesbare maand-jaar string."""

    def test_nl_maart(self) -> None:
        nl_months = load_translations("nl")["months"]
        assert _format_period_label("2026-03", nl_months) == "maart 2026"

    def test_fr_mars(self) -> None:
        fr_months = load_translations("fr")["months"]
        assert _format_period_label("2026-03", fr_months) == "mars 2026"

    def test_nl_januari(self) -> None:
        nl_months = load_translations("nl")["months"]
        assert _format_period_label("2026-01", nl_months) == "januari 2026"

    def test_fr_decembre(self) -> None:
        fr_months = load_translations("fr")["months"]
        assert _format_period_label("2025-12", fr_months) == "décembre 2025"

    def test_ongeldig_formaat_gooit_fout(self) -> None:
        with pytest.raises(ValueError):
            _format_period_label("202603", ["jan"] * 12)


# ---------------------------------------------------------------------------
# load_translations
# ---------------------------------------------------------------------------


class TestLoadTranslations:
    """i18n JSON-loader."""

    def test_nl_laadt_correct(self) -> None:
        t = load_translations("nl")
        assert "months" in t
        assert len(t["months"]) == 12
        assert t["months"][0] == "januari"

    def test_fr_laadt_correct(self) -> None:
        t = load_translations("fr")
        assert "months" in t
        assert t["months"][0] == "janvier"

    def test_nl_heeft_alle_secties(self) -> None:
        t = load_translations("nl")
        for sectie in (
            "report",
            "sections",
            "kpi",
            "status",
            "thresholds",
            "table",
            "notes",
            "history",
        ):
            assert sectie in t, f"Sectie '{sectie}' ontbreekt in nl.json"

    def test_fr_heeft_alle_secties(self) -> None:
        t = load_translations("fr")
        for sectie in (
            "report",
            "sections",
            "kpi",
            "status",
            "thresholds",
            "table",
            "notes",
            "history",
        ):
            assert sectie in t, f"Sectie '{sectie}' ontbreekt in fr.json"

    def test_onbekende_taal_gooit_fout(self) -> None:
        with pytest.raises(ValueError, match="Niet-ondersteunde taal"):
            load_translations("de")


# ---------------------------------------------------------------------------
# ReportExporter — initialisatie
# ---------------------------------------------------------------------------


class TestReportExporterInit:
    """Constructorvalidatie."""

    def test_standaard_taal_nl(self, templates_path: Path) -> None:
        exporter = ReportExporter(templates_path=templates_path)
        assert exporter._lang == "nl"

    def test_fr_taal_instellen(self, templates_path: Path) -> None:
        exporter = ReportExporter(lang="fr", templates_path=templates_path)
        assert exporter._lang == "fr"

    def test_onbekende_taal_gooit_fout(self, templates_path: Path) -> None:
        with pytest.raises(ValueError, match="Niet-ondersteunde taal"):
            ReportExporter(lang="de", templates_path=templates_path)

    def test_custom_templates_pad(self, tmp_path: Path) -> None:
        """Pad wordt bewaard — template-fout bij render verwacht (pad leeg)."""
        exporter = ReportExporter(lang="nl", templates_path=tmp_path)
        assert exporter._templates_path == tmp_path

    def test_custom_output_pad(self, tmp_path: Path, templates_path: Path) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        assert exporter._output_path == tmp_path


# ---------------------------------------------------------------------------
# ReportExporter — render()
# ---------------------------------------------------------------------------


class TestReportExporterRender:
    """Controle van de gegenereerde markdown-inhoud."""

    def test_render_retourneert_string(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_bevat_h1_titel_nl(self, pharma_result: KpiResult, templates_path: Path) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "# CSAT-Compass" in output
        assert "januari 2026" in output

    def test_render_bevat_h1_titel_fr(self, pharma_result: KpiResult, templates_path: Path) -> None:
        exporter = ReportExporter(lang="fr", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "# CSAT-Compass" in output
        assert "janvier 2026" in output

    def test_render_bevat_pijlernaam_nl(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "ZORGI PHARMA" in output

    def test_render_bevat_periode(self, pharma_result: KpiResult, templates_path: Path) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "2026-01" in output

    def test_render_nl_kpi_labels(self, pharma_result: KpiResult, templates_path: Path) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "Totaal tickets" in output
        assert "Gemiddelde CSAT-score" in output
        assert "High/Critical-ratio" in output

    def test_render_fr_kpi_labels(self, pharma_result: KpiResult, templates_path: Path) -> None:
        exporter = ReportExporter(lang="fr", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "Total tickets" in output
        assert "Score CSAT moyen" in output
        assert "Taux High/Critical" in output

    def test_render_kpi_waarden_aanwezig(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        """KPI-waarden moeten in Dutch number format in de output staan."""
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "3,80" in output  # avg_score
        assert "33,3" in output  # high_critical_ratio
        assert "+0,2" in output  # mom_score MoM trend

    def test_render_hc_status_warning_boven_drempel(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        """33,3% > 15% → status moet ⚠️ Aandacht tonen."""
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "⚠️ Aandacht" in output

    def test_render_hc_status_ok_onder_drempel(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        """Zet ratio naar 10% → status moet ✅ OK tonen."""
        pharma_result.high_critical_ratio = 10.0
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "✅ OK" in output

    def test_render_bevat_ziekenhuizen_tabel(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "AZ Groeninge" in output
        assert "UZ Brussel" in output

    def test_render_onbekend_ziekenhuis_aanwezig(
        self, result_with_unknown: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(result_with_unknown)
        assert "ONBEKEND" in output
        assert "data-kwaliteit" in output  # opmerking in notes sectie

    def test_render_geen_onbekend_ziekenhuis(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        """Zonder ONBEKEND-ziekenhuis mag de datakwaliteitsopmerking niet verschijnen."""
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "data-kwaliteit" not in output

    def test_render_bevat_versiehistorie(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "## Versiehistorie" in output
        assert "GHC" in output

    def test_render_bevat_adr006_waarschuwing(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "ADR-006" in output

    def test_render_fr_bevat_fr_labels(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="fr", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "Résumé" in output
        assert "Hôpital" in output

    def test_render_zonder_mom_attribuut(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        """KpiResult zonder mom_score attribuut mag geen fout geven (fallback 0.0)."""
        del pharma_result.mom_score  # type: ignore[attr-defined]
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "+0,0" in output  # fallback waarde geformatteerd

    def test_render_leeg_result(self, empty_result: KpiResult, templates_path: Path) -> None:
        """Leeg KpiResult (0 tickets) mag geen fout geven."""
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(empty_result)
        assert "# CSAT-Compass" in output
        assert "0" in output

    def test_render_bestandsnaam_in_header_nl(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "rapport-2026-01-nl.md" in output

    def test_render_bestandsnaam_in_header_fr(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="fr", templates_path=templates_path)
        output = exporter.render(pharma_result)
        assert "rapport-2026-01-fr.md" in output


# ---------------------------------------------------------------------------
# ReportExporter — export()
# ---------------------------------------------------------------------------


class TestReportExporterExport:
    """Bestandsschrijving en naamgeving."""

    def test_export_schrijft_bestand(
        self,
        pharma_result: KpiResult,
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        output_file = exporter.export(pharma_result)
        assert output_file.exists()

    def test_export_bestandsnaam_nl(
        self,
        pharma_result: KpiResult,
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        output_file = exporter.export(pharma_result)
        assert output_file.name == "rapport-2026-01-nl.md"

    def test_export_bestandsnaam_fr(
        self,
        pharma_result: KpiResult,
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = ReportExporter(lang="fr", templates_path=templates_path, output_path=tmp_path)
        output_file = exporter.export(pharma_result)
        assert output_file.name == "rapport-2026-01-fr.md"

    def test_export_inhoud_leesbaar(
        self,
        pharma_result: KpiResult,
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        output_file = exporter.export(pharma_result)
        content = output_file.read_text(encoding="utf-8")
        assert "# CSAT-Compass" in content

    def test_export_maakt_outputmap_aan(
        self,
        pharma_result: KpiResult,
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        """Exportmap wordt aangemaakt als die nog niet bestaat."""
        nieuwe_map = tmp_path / "submap" / "output"
        exporter = ReportExporter(lang="nl", templates_path=templates_path, output_path=nieuwe_map)
        output_file = exporter.export(pharma_result)
        assert output_file.exists()

    def test_export_retourneert_pad(
        self,
        pharma_result: KpiResult,
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        result = exporter.export(pharma_result)
        assert isinstance(result, Path)

    def test_export_logt_naar_logger(
        self,
        pharma_result: KpiResult,
        templates_path: Path,
        tmp_path: Path,
    ) -> None:
        """export() moet een INFO-logbericht schrijven via loguru."""
        exporter = ReportExporter(lang="nl", templates_path=templates_path, output_path=tmp_path)
        with patch("csat.core.exporters.report_exporter.logger") as mock_log:
            exporter.export(pharma_result)
            mock_log.info.assert_called_once()


# ---------------------------------------------------------------------------
# ReportExporter — _build_context()
# ---------------------------------------------------------------------------


class TestBuildContext:
    """Inhoud van de template-context."""

    def test_context_bevat_alle_sleutels(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        verplichte_sleutels = [
            "t",
            "period",
            "period_label",
            "generated_date",
            "pillar",
            "pillar_name",
            "total_tickets",
            "scored_tickets",
            "avg_score",
            "high_critical_ratio",
            "high_critical_count",
            "n_hospitals",
            "mom_score",
            "hc_ok",
            "per_hospital",
            "has_unknown",
            "lang",
        ]
        for sleutel in verplichte_sleutels:
            assert sleutel in ctx, f"Sleutel '{sleutel}' ontbreekt in context"

    def test_context_hc_ok_false_boven_drempel(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        """33,3% > 15% → hc_ok moet False zijn."""
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["hc_ok"] is False

    def test_context_hc_ok_true_onder_drempel(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        pharma_result.high_critical_ratio = 14.9
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["hc_ok"] is True

    def test_context_onbekend_gesorteerd_als_laatste(
        self, result_with_unknown: KpiResult, templates_path: Path
    ) -> None:
        """ONBEKEND moet als laatste ziekenhuis in de gesorteerde lijst staan."""
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(result_with_unknown)
        ziekenhuizen = [naam for naam, _ in ctx["per_hospital"]]
        assert ziekenhuizen[-1] == "ONBEKEND"

    def test_context_has_unknown_true(
        self, result_with_unknown: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(result_with_unknown)
        assert ctx["has_unknown"] is True

    def test_context_has_unknown_false(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["has_unknown"] is False

    def test_context_period_label_nl(self, pharma_result: KpiResult, templates_path: Path) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["period_label"] == "januari 2026"

    def test_context_period_label_fr(self, pharma_result: KpiResult, templates_path: Path) -> None:
        exporter = ReportExporter(lang="fr", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["period_label"] == "janvier 2026"

    def test_context_mom_fallback_nul(self, pharma_result: KpiResult, templates_path: Path) -> None:
        """Zonder mom_score attribuut moet de fallback 0.0 zijn."""
        del pharma_result.mom_score  # type: ignore[attr-defined]
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["mom_score"] == 0.0

    def test_context_n_hospitals(self, pharma_result: KpiResult, templates_path: Path) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["n_hospitals"] == 2

    def test_context_pillar_name_nl_pharma(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["pillar_name"] == "ZORGI PHARMA"

    def test_context_pillar_name_fr_pharma(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        exporter = ReportExporter(lang="fr", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["pillar_name"] == "ZORGI PHARMA"

    def test_context_onbekende_pijler_fallback(
        self, pharma_result: KpiResult, templates_path: Path
    ) -> None:
        """Onbekende pijler gebruikt uppercase pillar_key als fallback."""
        pharma_result.pillar = "unknown_pillar"
        exporter = ReportExporter(lang="nl", templates_path=templates_path)
        ctx = exporter._build_context(pharma_result)
        assert ctx["pillar_name"] == "UNKNOWN_PILLAR"
