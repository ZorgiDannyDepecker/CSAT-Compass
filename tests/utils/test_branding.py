"""
Unit tests voor src/csat/utils/branding.py.
Test constanten, apply_plotly_theme(), inject_css() en render_topbar() via mocks.
"""

from unittest.mock import MagicMock, patch

from csat.config.pillars import PILLAR_REGISTRY
from csat.utils.branding import (
    COLORS,
    GRADIENT_CSS,
    LOGO_ASSETS,
    PILLAR_COLORS,
    PILLAR_COLORWAY,
    PLOTLY_LAYOUT,
    STREAMLIT_CSS,
    add_watermark,
    apply_plotly_theme,
    inject_css,
    inject_tab_font_css,
    inject_tab_scroll_reset,
    render_topbar,
)

# ------------------------------------------------------------------
# Constanten
# ------------------------------------------------------------------


class TestBrandingConstanten:
    """Controleer dat brandkleuren correct gedefinieerd zijn."""

    def test_dark_blue_aanwezig(self) -> None:
        assert COLORS["dark_blue"] == "#003a70"

    def test_red_aanwezig(self) -> None:
        assert COLORS["red"] == "#dc2b26"

    def test_purple_aanwezig(self) -> None:
        assert COLORS["purple"] == "#7f4267"

    def test_alle_pijlers_in_pillar_colors(self) -> None:
        verwacht = {"zorgi", "pharma", "care", "care_admin", "erp4hc"}
        assert set(PILLAR_COLORS.keys()) == verwacht

    def test_gradient_bevat_alle_drie_kleuren(self) -> None:
        assert "#003a70" in GRADIENT_CSS
        assert "#7f4267" in GRADIENT_CSS
        assert "#dc2b26" in GRADIENT_CSS

    def test_pillar_colorway_is_lijst(self) -> None:
        assert isinstance(PILLAR_COLORWAY, list)
        assert len(PILLAR_COLORWAY) == 5

    def test_plotly_layout_heeft_font(self) -> None:
        assert "font" in PLOTLY_LAYOUT

    def test_streamlit_css_bevat_style_tag(self) -> None:
        assert "<style>" in STREAMLIT_CSS


# ------------------------------------------------------------------
# apply_plotly_theme()
# ------------------------------------------------------------------


class TestApplyPlotlyTheme:
    """Test Plotly-thema toepassing via mock figure."""

    def test_retourneert_zelfde_figuur(self) -> None:
        mock_fig = MagicMock()
        result = apply_plotly_theme(mock_fig)
        assert result is mock_fig

    def test_update_layout_aangeroepen(self) -> None:
        mock_fig = MagicMock()
        apply_plotly_theme(mock_fig)
        mock_fig.update_layout.assert_called_once()

    def test_layout_bevat_font_argument(self) -> None:
        mock_fig = MagicMock()
        apply_plotly_theme(mock_fig)
        _, kwargs = mock_fig.update_layout.call_args
        assert "font" in kwargs


# ------------------------------------------------------------------
# inject_css()
# ------------------------------------------------------------------


class TestInjectCss:
    """Test Streamlit CSS-injectie via mock st-module."""

    def test_markdown_aangeroepen(self) -> None:
        mock_st = MagicMock()
        inject_css(mock_st)
        mock_st.markdown.assert_called_once()

    def test_unsafe_allow_html_true(self) -> None:
        mock_st = MagicMock()
        inject_css(mock_st)
        _, kwargs = mock_st.markdown.call_args
        assert kwargs.get("unsafe_allow_html") is True

    def test_css_bevat_poppins(self) -> None:
        mock_st = MagicMock()
        inject_css(mock_st)
        css_arg = mock_st.markdown.call_args[0][0]
        assert "Poppins" in css_arg

    def test_prod_mode_roept_markdown_twee_keer_aan(self) -> None:
        """inject_css() met prod_mode=True moet st.markdown() tweemaal aanroepen."""
        mock_st = MagicMock()
        inject_css(mock_st, prod_mode=True)
        assert mock_st.markdown.call_count == 2

    def test_prod_mode_tweede_call_bevat_deploy_knop_selector(self) -> None:
        """Tweede markdown-call verbergt de deploy-knop (prod-CSS)."""
        mock_st = MagicMock()
        inject_css(mock_st, prod_mode=True)
        tweede_call_css = mock_st.markdown.call_args_list[1][0][0]
        assert "stAppDeployButton" in tweede_call_css

    def test_prod_mode_false_roept_markdown_een_keer_aan(self) -> None:
        """inject_css() zonder prod_mode mag st.markdown() slechts eenmaal aanroepen."""
        mock_st = MagicMock()
        inject_css(mock_st, prod_mode=False)
        assert mock_st.markdown.call_count == 1


# ------------------------------------------------------------------
# C1 — render_topbar()
# ------------------------------------------------------------------


class TestRenderTopbar:
    """Test render_topbar() — vaste ZORGI branded topbalk."""

    def _make_st(self) -> MagicMock:
        mock_st = MagicMock()
        mock_st.markdown = MagicMock()
        return mock_st

    def test_markdown_aangeroepen(self) -> None:
        """render_topbar() roept st_container.markdown() aan."""
        mock_st = self._make_st()
        render_topbar(mock_st, today_str="06/04/2026")
        mock_st.markdown.assert_called_once()

    def test_unsafe_allow_html_true(self) -> None:
        """render_topbar() geeft unsafe_allow_html=True mee."""
        mock_st = self._make_st()
        render_topbar(mock_st, today_str="06/04/2026")
        _, kwargs = mock_st.markdown.call_args
        assert kwargs.get("unsafe_allow_html") is True

    def test_today_str_in_html(self) -> None:
        """De datum-string verschijnt in de gegenereerde HTML."""
        mock_st = self._make_st()
        render_topbar(mock_st, today_str="06/04/2026")
        html = mock_st.markdown.call_args[0][0]
        assert "06/04/2026" in html

    def test_pillar_name_in_html(self) -> None:
        """pillar_name wordt opgenomen in de topbalk-HTML."""
        mock_st = self._make_st()
        render_topbar(mock_st, today_str="06/04/2026", pillar_name="ZORGI PHARMA")
        html = mock_st.markdown.call_args[0][0]
        assert "ZORGI PHARMA" in html

    def test_zonder_pillar_name_csat_compass_in_html(self) -> None:
        """Zonder pillar_name verschijnt 'CSAT-Compass' als fallback-label."""
        mock_st = self._make_st()
        render_topbar(mock_st, today_str="06/04/2026")
        html = mock_st.markdown.call_args[0][0]
        assert "CSAT-Compass" in html

    def test_mode_label_in_html_als_pillar_opgegeven(self) -> None:
        """full_window_label verschijnt in de HTML als pillar_name opgegeven is."""
        mock_st = self._make_st()
        render_topbar(
            mock_st,
            today_str="06/04/2026",
            pillar_name="ZORGI PHARMA",
            full_window_label="📊 Volledig venster · 2025 → mrt 2026",
        )
        html = mock_st.markdown.call_args[0][0]
        assert "Volledig venster" in html
        assert "2025" in html

    def test_zonder_mode_label_geen_sub_lijn(self) -> None:
        """Zonder mode_label mag geen <span class="zorgi-topbar-pillar-sub"> in de HTML-body zitten."""
        mock_st = self._make_st()
        render_topbar(mock_st, today_str="06/04/2026", pillar_name="ZORGI PHARMA")
        html = mock_st.markdown.call_args[0][0]
        # De CSS-definitie mag aanwezig zijn, maar de concrete <span>-tag niet
        assert '<span class="zorgi-topbar-pillar-sub">' not in html

    def test_logo_html_aanwezig_als_logo_bestaat(self) -> None:
        """Als het logo-bestand bestaat, verschijnt een <img>-tag in de HTML."""
        mock_st = self._make_st()
        logo_path = LOGO_ASSETS["logo_icoon_144_wit"]
        assert logo_path.exists(), "Voorwaarde: logo moet op schijf bestaan"
        render_topbar(mock_st, today_str="06/04/2026")
        html = mock_st.markdown.call_args[0][0]
        assert "<img" in html

    def test_geen_logo_html_als_logo_ontbreekt(self) -> None:
        """Als het logo-bestand niet bestaat, mag er geen <img>-tag zijn."""
        from pathlib import Path

        mock_st = self._make_st()
        with patch(
            "csat.utils.branding.LOGO_ASSETS",
            {"logo_icoon_144_wit": Path("/nonexistent/logo.png")},
        ):
            render_topbar(mock_st, today_str="06/04/2026")
        html = mock_st.markdown.call_args[0][0]
        assert "<img" not in html

    def test_zorgi_topbar_class_aanwezig(self) -> None:
        """De topbalk-container heeft altijd de klasse 'zorgi-topbar'."""
        mock_st = self._make_st()
        render_topbar(mock_st, today_str="06/04/2026")
        html = mock_st.markdown.call_args[0][0]
        assert "zorgi-topbar" in html


# ------------------------------------------------------------------
# inject_tab_font_css()
# ------------------------------------------------------------------


class TestInjectTabFontCss:
    """Test inject_tab_font_css() — injecteert tab font-size CSS via Streamlit."""

    def test_markdown_aangeroepen(self) -> None:
        mock_st = MagicMock()
        inject_tab_font_css(mock_st)
        mock_st.markdown.assert_called_once()

    def test_unsafe_allow_html_true(self) -> None:
        mock_st = MagicMock()
        inject_tab_font_css(mock_st)
        _, kwargs = mock_st.markdown.call_args
        assert kwargs.get("unsafe_allow_html") is True

    def test_css_bevat_tab_selector(self) -> None:
        mock_st = MagicMock()
        inject_tab_font_css(mock_st)
        css_arg = mock_st.markdown.call_args[0][0]
        assert "tab" in css_arg.lower()

    def test_css_bevat_font_size(self) -> None:
        mock_st = MagicMock()
        inject_tab_font_css(mock_st)
        css_arg = mock_st.markdown.call_args[0][0]
        assert "font-size" in css_arg


# ------------------------------------------------------------------
# inject_tab_scroll_reset()
# ------------------------------------------------------------------


class TestInjectTabScrollReset:
    """Test inject_tab_scroll_reset() — injecteert scroll-naar-boven JS via stc.html()."""

    def _call_with_mock(self):
        """Voer inject_tab_scroll_reset() uit met gemockte streamlit.components.v1."""
        from unittest.mock import MagicMock, patch

        mock_stc = MagicMock()
        with patch.dict("sys.modules", {"streamlit.components.v1": mock_stc}):
            inject_tab_scroll_reset()
        return mock_stc

    def test_html_aangeroepen(self) -> None:
        """stc.html() wordt exact één keer aangeroepen."""
        mock_stc = self._call_with_mock()
        mock_stc.html.assert_called_once()

    def test_html_height_is_1(self) -> None:
        """height-parameter is 1 (onzichtbare iframe)."""
        mock_stc = self._call_with_mock()
        _, kwargs = mock_stc.html.call_args
        assert kwargs.get("height") == 1

    def test_html_scrolling_false(self) -> None:
        """scrolling=False zodat de iframe geen eigen scrollbalk krijgt."""
        mock_stc = self._call_with_mock()
        _, kwargs = mock_stc.html.call_args
        assert kwargs.get("scrolling") is False

    def test_html_bevat_zorgi_scroll_functie(self) -> None:
        """De gegenereerde HTML bevat de _zorgiTop JavaScript-functie."""
        mock_stc = self._call_with_mock()
        html_arg = mock_stc.html.call_args[0][0]
        assert "_zorgiTop" in html_arg

    def test_html_bevat_tab_listener(self) -> None:
        """De gegenereerde HTML bevat een click-listener op tab-elementen."""
        mock_stc = self._call_with_mock()
        html_arg = mock_stc.html.call_args[0][0]
        assert "data-baseweb" in html_arg


# ------------------------------------------------------------------
# A7 — Validatietests pijlerkleuren
# ------------------------------------------------------------------

# Toegestaan kleurenpalet: ZORGI Design System + afgeleide (ADR-010)
ALLOWED_COLORS = {
    "#003a70",  # Dark Blue
    "#dc2b26",  # Red
    "#7f4267",  # Purple
    "#5f8495",  # Grey Blue
    "#609fce",  # Light Blue
    "#d7e7f3",  # Ultra Light Blue
    "#a06b8a",  # Light Purple (afgeleide — ADR-010)
}


class TestPijlerkleuren:
    """Validatie: alle pijlerkleuren zijn on-brand conform ZORGI Design System."""

    def test_alle_pijlerkleuren_in_toegestaan_palet(self) -> None:
        for key, config in PILLAR_REGISTRY.items():
            kleur = config["color"].lower()
            assert kleur in ALLOWED_COLORS, (
                f"Pijler '{key}' heeft off-brand kleur {kleur} — toegestaan: {ALLOWED_COLORS}"
            )

    def test_pillar_colors_consistent_met_registry(self) -> None:
        """PILLAR_COLORS in branding.py moet exact overeenkomen met pillars.py."""
        for key in PILLAR_COLORS:
            assert key in PILLAR_REGISTRY, f"'{key}' in PILLAR_COLORS maar niet in PILLAR_REGISTRY"
            assert PILLAR_COLORS[key].lower() == PILLAR_REGISTRY[key]["color"].lower(), (
                f"Pijler '{key}': branding.py={PILLAR_COLORS[key]}, "
                f"pillars.py={PILLAR_REGISTRY[key]['color']}"
            )


# ------------------------------------------------------------------
# A8 — Validatietest logo-paden
# ------------------------------------------------------------------


class TestLogoAssets:
    """Validatie: alle logo-assets bestaan op schijf."""

    def test_alle_logo_paden_bestaan(self) -> None:
        for naam, pad in LOGO_ASSETS.items():
            assert pad.exists(), f"Logo-asset '{naam}' niet gevonden: {pad}"

    def test_minstens_6_assets(self) -> None:
        assert len(LOGO_ASSETS) >= 6


# ------------------------------------------------------------------
# add_watermark()
# ------------------------------------------------------------------


class TestAddWatermark:
    """Test add_watermark() — logo bestaat of niet."""

    def test_watermark_zonder_logo(self) -> None:
        """fig.figimage() wordt NIET aangeroepen als logo niet bestaat."""
        mock_fig = MagicMock()
        from pathlib import Path

        with patch(
            "csat.utils.branding.LOGO_ASSETS",
            {"heartbeat_hires_transparant": Path("/nonexistent/logo.png")},
        ):
            add_watermark(mock_fig)
        mock_fig.figimage.assert_not_called()

    def test_watermark_met_logo(self) -> None:
        """fig.figimage() wordt aangeroepen als logo op schijf bestaat."""
        mock_fig = MagicMock()
        mock_fig.bbox.xmax = 800
        logo_path = LOGO_ASSETS["heartbeat_hires_transparant"]
        assert logo_path.exists(), "Voorwaarde: logo-asset moet bestaan voor deze test"
        with patch("matplotlib.image.imread", return_value=MagicMock()):
            add_watermark(mock_fig)
        mock_fig.figimage.assert_called_once()


# ------------------------------------------------------------------
# B5 — Matplotlib-thema tests
# ------------------------------------------------------------------


class TestMatplotlibTheme:
    """Test ZORGI matplotlib-thema en Poppins-registratie."""

    def test_register_poppins_geeft_string_terug(self) -> None:
        """_register_poppins() retourneert altijd 'Poppins' of 'Verdana'."""
        from csat.utils.branding import _register_poppins

        result = _register_poppins()
        assert result in ("Poppins", "Verdana")

    def test_apply_matplotlib_theme_wijzigt_rcparams(self) -> None:
        """apply_matplotlib_theme() past ZORGI-kleuren toe op rcParams."""
        import matplotlib.pyplot as plt

        from csat.utils.branding import apply_matplotlib_theme

        apply_matplotlib_theme()
        assert plt.rcParams["axes.facecolor"] == COLORS["ultra_light_blue"]
        assert plt.rcParams["figure.facecolor"] == COLORS["white"]
        assert plt.rcParams["text.color"] == COLORS["text"]

    def test_colorway_bevat_geen_rood(self) -> None:
        """Rood mag niet in de matplotlib colorway — gereserveerd voor alarmen."""
        import matplotlib.pyplot as plt

        from csat.utils.branding import apply_matplotlib_theme

        apply_matplotlib_theme()
        cycle_colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
        assert COLORS["red"] not in cycle_colors, (
            "Rood mag niet in de matplotlib colorway — gereserveerd voor alarmen"
        )


# ------------------------------------------------------------------
# B6 — Brand guard: CSS ↔ COLORS consistentie
# ------------------------------------------------------------------


class TestBrandGuard:
    """Validatie: CSS-constanten bevatten uitsluitend kleuren uit COLORS dict."""

    def test_streamlit_css_kleuren_komen_uit_colors(self) -> None:
        """Elke hex-kleur in STREAMLIT_CSS moet voorkomen in COLORS of als
        bekende afgeleide/externe kleur."""
        import re

        toegestaan = set(COLORS.values()) | {"#a06b8a", "#00aa44"}
        hex_kleuren = set(re.findall(r"#[0-9a-fA-F]{6}", STREAMLIT_CSS))
        off_brand = hex_kleuren - toegestaan
        assert not off_brand, f"Off-brand kleuren gevonden in STREAMLIT_CSS: {off_brand}"

    def test_plotly_colorway_bevat_geen_rood(self) -> None:
        """Rood is gereserveerd voor alarmen — mag niet in grafiek-colorway."""
        assert COLORS["red"] not in PLOTLY_LAYOUT["colorway"], (
            "PLOTLY_LAYOUT.colorway bevat rood — in strijd met kleurreservering"
        )
