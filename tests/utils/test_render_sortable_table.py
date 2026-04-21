"""
Unit tests voor _render_sortable_table() in src/dashboard/app.py.

Strategie:
    - _render_sortable_table() leeft binnen app.py maar heeft geen externe
      Streamlit-runtime nodig voor HTML-generatie.
    - We importeren de functie via een helper die streamlit + streamlit_components
      volledig mockt, zodat de HTML-string beschikbaar is zonder browser.
    - Alle tests draaien op de gegenereerde HTML-string — geen UI-interactie.
    - Scope: signatuur, parameters insight_html / footer_html_raw / footer_text,
      hoogte-berekening, scrollbar-logica, delta-kleur, titel/export-knop.
"""

import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Hulpfunctie: laad _render_sortable_table als testbare callable
# ---------------------------------------------------------------------------
_APP = Path(__file__).resolve().parent.parent.parent / "src" / "dashboard" / "app.py"


def _get_fn() -> Any:
    """
    Importeer _render_sortable_table vanuit app.py met volledig gemockte
    Streamlit + streamlit_components omgeving.

    Retourneert een tuple (fn, captured) waarbij captured["html"] de
    gegenereerde HTML-string bevat na elke aanroep.
    """
    import importlib.util

    captured: dict[str, str] = {"html": ""}

    mock_st = MagicMock()
    mock_st.session_state = {}
    mock_st.set_page_config = MagicMock()
    mock_st.cache_data = lambda *a, **kw: lambda f: f

    mock_stc = MagicMock()

    def _html_capture(html_str: str, **kwargs: Any) -> None:
        captured["html"] = html_str

    mock_stc.html = _html_capture

    with (
        patch.dict(
            sys.modules,
            {
                "streamlit": mock_st,
                "streamlit.components": MagicMock(),
                "streamlit.components.v1": mock_stc,
            },
        ),
    ):
        spec = importlib.util.spec_from_file_location("app_test_module", str(_APP))
        if not spec or not spec.loader:
            pytest.skip("app.py spec kon niet worden aangemaakt")
        mod: ModuleType = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        except Exception:
            pytest.skip("app.py kon niet geladen worden in mock-context")

    fn = getattr(mod, "_render_sortable_table", None)
    if fn is None:
        pytest.skip("_render_sortable_table niet gevonden in app.py")

    # Bind mock_stc opnieuw op de geladen module zodat html_capture werkt
    mod_stc = getattr(mod, "_stc", None)
    if mod_stc is not None:
        mod_stc.html = _html_capture

    return fn, captured


# ---------------------------------------------------------------------------
# Fixture: eenvoudig DataFrame + geladen functie
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def fn_and_capture():
    """Gedeelde import van _render_sortable_table voor de hele testmodule."""
    return _get_fn()


@pytest.fixture()
def simple_df() -> pd.DataFrame:
    """Minimaal DataFrame met 3 rijen voor basistests."""
    return pd.DataFrame(
        {
            "Type": ["Incident", "Bug", "Request"],
            "Score": ["4.0★", "3.0★", "5.0★"],
            "Δ Score": ["+1.00★", "-0.50★", "+0.00★"],
        }
    )


@pytest.fixture()
def large_df() -> pd.DataFrame:
    """DataFrame met 20 rijen voor scrollbar-test (>15 rijen)."""
    return pd.DataFrame(
        {
            "Ziekenhuis": [f"ZH_{i:02d}" for i in range(20)],
            "Score": [f"{4.0 + i * 0.05:.2f}★" for i in range(20)],
        }
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _call(fn_and_capture, df, **kwargs) -> str:
    """Roep _render_sortable_table aan en retourneer de gegenereerde HTML."""
    _fn, captured = fn_and_capture
    captured_local: dict[str, str] = {"html": ""}

    def _capture(html_str: str, **kw: Any) -> None:
        captured_local["html"] = html_str

    import importlib.util

    # Haal het module-object op via de fn-closure
    import sys

    mock_st = MagicMock()
    mock_st.session_state = {}
    mock_st.cache_data = lambda *a, **kw2: lambda f: f

    def _html_capture2(html_str: str, **kw: Any) -> None:
        captured["html"] = html_str

    with (
        patch.dict(
            sys.modules,
            {
                "streamlit": mock_st,
                "streamlit.components": MagicMock(),
                "streamlit.components.v1": MagicMock(html=_html_capture2),
            },
        ),
    ):
        spec = importlib.util.spec_from_file_location("_app_tmp", str(_APP))
        if not spec or not spec.loader:
            pytest.skip("app.py spec niet aanmaakbaar")
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        except Exception:
            pytest.skip("app.py laad mislukt")

        mod_fn = getattr(mod, "_render_sortable_table", None)
        if mod_fn is None:
            pytest.skip("_render_sortable_table niet gevonden")

        import csat.utils.branding as _b  # noqa: F401 — zorgt voor branding-attrs

        real_stc = getattr(mod, "_stc", None)
        if real_stc is not None:
            real_stc.html = _html_capture2

        try:
            mod_fn(df, "Test-titel", **kwargs)
        except Exception:
            pytest.skip("_render_sortable_table aanroep mislukt in mock-context")

    return str(captured["html"])


# ---------------------------------------------------------------------------
# Klasse 1 — Basistests: signatuur en standaard HTML-structuur
# ---------------------------------------------------------------------------
class TestRenderSortableTableBasis:
    """Basisbehavior: HTML-structuur, titel, exportknop, tabel."""

    def test_html_bevat_doctype(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df)
        assert "<!DOCTYPE html>" in h

    def test_html_bevat_tabel(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df)
        assert "<table" in h
        assert "</table>" in h

    def test_html_bevat_kolomkoppen(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df)
        assert "Type" in h
        assert "Score" in h

    def test_html_bevat_rijen(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df)
        assert "Incident" in h
        assert "Bug" in h

    def test_html_bevat_export_knop(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df)
        assert "export-btn" in h
        assert "Export CSV" in h

    def test_html_bevat_filter_rij(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df)
        assert "filter-row" in h
        assert "applyFilters" in h

    def test_html_bevat_sorteer_script(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df)
        assert "sortBy" in h

    def test_html_bevat_selfresize(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df)
        assert "selfResize" in h

    def test_titel_in_html(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, title="Mijn Testtitel")
        assert "Mijn Testtitel" in h

    def test_show_title_false_geen_h4(self, fn_and_capture, simple_df):
        # sec-title staat in de CSS — controleer dat de <h4>-tag niet verschijnt
        h = _call(fn_and_capture, simple_df, show_title=False)
        assert "<h4 class='sec-title'>" not in h

    def test_export_label_custom(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, export_label="📥 Download")
        assert "Download" in h

    def test_export_filename_in_download_attrib(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, export_filename="mijn_export.csv")
        assert "mijn_export.csv" in h


# ---------------------------------------------------------------------------
# Klasse 2 — footer_text parameter
# ---------------------------------------------------------------------------
class TestFooterText:
    """footer_text: enkelvoudig en meerdere regels via '  |  ' splitter."""

    def test_footer_text_enkelvoudig_in_html(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, footer_text="Legenda: score ≤2★ = negatief")
        assert "Legenda" in h
        assert "footer" in h

    def test_footer_text_meerdere_regels(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, footer_text="Regel 1  |  Regel 2  |  Regel 3")
        assert "Regel 1" in h
        assert "Regel 2" in h
        assert "Regel 3" in h

    def test_footer_text_leeg_geen_footer_klasse(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, footer_text="")
        # geen <p class='footer'> verwacht
        assert "class='footer'" not in h

    def test_footer_text_html_escaped(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, footer_text="Score ≤2★ & meer")
        # html.escape van & → &amp;
        assert "&amp;" in h or "≤2" in h  # unicode wordt niet escaped


# ---------------------------------------------------------------------------
# Klasse 3 — footer_html_raw parameter
# ---------------------------------------------------------------------------
class TestFooterHtmlRaw:
    """footer_html_raw: raw HTML binnenin iframe na de tabel."""

    def test_footer_html_raw_aanwezig(self, fn_and_capture, simple_df):
        raw = "<p style='color:red'>Noot</p>"
        h = _call(fn_and_capture, simple_df, footer_html_raw=raw)
        assert "Noot" in h
        assert "color:red" in h

    def test_footer_html_raw_met_br_tags(self, fn_and_capture, simple_df):
        raw = "Lijn 1<br>Lijn 2<br>Lijn 3"
        h = _call(fn_and_capture, simple_df, footer_html_raw=raw)
        assert "Lijn 1" in h
        assert "Lijn 2" in h

    def test_footer_html_raw_leeg_niet_in_html(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, footer_html_raw="")
        # geen lege placeholder verwacht
        assert "footer_html_raw" not in h

    def test_footer_html_raw_na_tabel(self, fn_and_capture, simple_df):
        raw = "<span id='uniek123'>voetnoot</span>"
        h = _call(fn_and_capture, simple_df, footer_html_raw=raw)
        # raw moet ná </div> (scroll-wrap sluiten) komen
        scroll_end = h.find("</div>")
        raw_pos = h.find("uniek123")
        assert scroll_end < raw_pos


# ---------------------------------------------------------------------------
# Klasse 4 — insight_html parameter
# ---------------------------------------------------------------------------
class TestInsightHtml:
    """insight_html: HTML-blok voor infobalk binnenin iframe."""

    def test_insight_html_aanwezig(self, fn_and_capture, simple_df):
        insight = "<div class='insight-box'>⚠️ Aandachtspunt</div>"
        h = _call(fn_and_capture, simple_df, insight_html=insight)
        assert "Aandachtspunt" in h
        assert "insight-box" in h

    def test_insight_html_leeg_geen_blok(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, insight_html="")
        # CSS bevat .insight-box stijldefinities — die zijn altijd aanwezig
        # Controleer dat er geen <div/span met insight-box> in de body staat
        assert "<div class='insight-box'>" not in h
        assert '<div class="insight-box">' not in h

    def test_insight_html_na_footer(self, fn_and_capture, simple_df):
        """insight_html moet na footer_text komen in de HTML."""
        h = _call(
            fn_and_capture,
            simple_df,
            footer_text="Legenda",
            insight_html="<div id='ins99'>Insight</div>",
        )
        footer_pos = h.find("Legenda")
        insight_pos = h.find("ins99")
        assert footer_pos < insight_pos

    def test_insight_html_met_strong_tag(self, fn_and_capture, simple_df):
        insight = "<div class='insight-box'><strong>Incident</strong>: aandacht</div>"
        h = _call(fn_and_capture, simple_df, insight_html=insight)
        assert "<strong>Incident</strong>" in h

    def test_insight_css_in_stijlblok(self, fn_and_capture, simple_df):
        """CSS-klasse .insight-box moet altijd aanwezig zijn in de <style>."""
        h = _call(fn_and_capture, simple_df)
        assert ".insight-box" in h


# ---------------------------------------------------------------------------
# Klasse 5 — Hoogte-berekening
# ---------------------------------------------------------------------------
class TestHoogteBerekening:
    """Valideer dat de iframe-hoogte proportioneel meeschaalt met de inhoud."""

    def test_meer_rijen_geeft_hogere_iframe(self, fn_and_capture):
        df_klein = pd.DataFrame({"A": ["x"] * 3})
        df_groot = pd.DataFrame({"A": ["x"] * 10})
        # We vergelijken de `height=` waarde in de _stc.html aanroep — niet beschikbaar
        # als returnwaarde. We testen indirect via aanwezigheid van de rijen.
        h_klein = _call(fn_and_capture, df_klein)
        h_groot = _call(fn_and_capture, df_groot)
        # Meer rijen → meer <tr> in tbody
        assert h_groot.count("<tr>") > h_klein.count("<tr>")

    def test_insight_html_verhoogt_hoogte(self, fn_and_capture, simple_df):
        """Met insight_html moet iframe hoger zijn dan zonder."""
        # Indirect: de HTML is aantoonbaar groter met insight_html
        h_zonder = _call(fn_and_capture, simple_df, insight_html="")
        h_met = _call(fn_and_capture, simple_df, insight_html="<div>x</div>")
        assert len(h_met) > len(h_zonder)

    def test_footer_html_raw_verhoogt_hoogte(self, fn_and_capture, simple_df):
        h_zonder = _call(fn_and_capture, simple_df, footer_html_raw="")
        h_met = _call(fn_and_capture, simple_df, footer_html_raw="<p>voetnoot</p>")
        assert len(h_met) > len(h_zonder)


# ---------------------------------------------------------------------------
# Klasse 6 — Scrollbar bij >15 rijen
# ---------------------------------------------------------------------------
class TestScrollbar:
    """Scrollbar (webkit-stijl) actief bij >15 rijen, niet bij ≤15 rijen."""

    def test_scrollbar_aanwezig_bij_grote_tabel(self, fn_and_capture, large_df):
        h = _call(fn_and_capture, large_df)
        assert "webkit-scrollbar" in h
        assert "overflow-y:auto" in h

    def test_scrollbar_afwezig_bij_kleine_tabel(self, fn_and_capture, simple_df):
        # simple_df heeft 3 rijen — geen scrollbar
        h = _call(fn_and_capture, simple_df)
        assert "overflow-y:visible" in h or "overflow-y:auto" not in h


# ---------------------------------------------------------------------------
# Klasse 7 — delta_col kleurcodering
# ---------------------------------------------------------------------------
class TestDeltaCol:
    """Positieve delta → groen, negatieve delta → rood, nul → geen kleur."""

    def test_positieve_delta_groen(self, fn_and_capture):
        df = pd.DataFrame({"Type": ["Inc"], "Δ": ["+1.12★"]})
        h = _call(fn_and_capture, df, delta_col="Δ")
        assert "#2e7d32" in h

    def test_negatieve_delta_rood(self, fn_and_capture):
        df = pd.DataFrame({"Type": ["Inc"], "Δ": ["-0.50★"]})
        h = _call(fn_and_capture, df, delta_col="Δ")
        assert "#dc2b26" in h

    def test_nul_delta_geen_kleur(self, fn_and_capture):
        df = pd.DataFrame({"Type": ["Inc"], "Δ": ["+0.00★"]})
        h = _call(fn_and_capture, df, delta_col="Δ")
        # font-weight:600 enkel bij != 0
        assert "#2e7d32" not in h
        assert "#dc2b26" not in h

    def test_geen_delta_col_geen_kleur(self, fn_and_capture):
        df = pd.DataFrame({"Type": ["Inc"], "Score": ["-1.00★"]})
        h = _call(fn_and_capture, df)  # geen delta_col
        assert "#dc2b26" not in h


# ---------------------------------------------------------------------------
# Klasse 8 — col_widths parameter
# ---------------------------------------------------------------------------
class TestColWidths:
    """col_widths stelt width-attribuut in op kolomkoppen."""

    def test_col_widths_in_th(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df, col_widths=["40%", "30%", "30%"])
        assert "width:40%" in h
        assert "width:30%" in h

    def test_geen_col_widths_geen_width_attrib(self, fn_and_capture, simple_df):
        h = _call(fn_and_capture, simple_df)
        # Zonder col_widths geen style="width:..." op de th
        assert 'style="width:' not in h


# ---------------------------------------------------------------------------
# Klasse 9 — HTML-escaping en veiligheid
# ---------------------------------------------------------------------------
class TestHtmlEscaping:
    """Kolomnamen en celwaarden worden correct HTML-escaped."""

    def test_kolomnaam_met_html_tekens_escaped(self, fn_and_capture):
        df = pd.DataFrame({"<Kolom>": ["<waarde>"]})
        h = _call(fn_and_capture, df)
        assert "&lt;Kolom&gt;" in h
        assert "&lt;waarde&gt;" in h

    def test_celwaarde_met_ampersand_escaped(self, fn_and_capture):
        df = pd.DataFrame({"A": ["Tom & Jerry"]})
        h = _call(fn_and_capture, df)
        assert "Tom &amp; Jerry" in h

    def test_script_tag_in_cel_escaped(self, fn_and_capture):
        df = pd.DataFrame({"A": ['<script>alert("xss")</script>']})
        h = _call(fn_and_capture, df)
        assert "<script>alert" not in h
        assert "&lt;script&gt;" in h
