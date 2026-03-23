"""
Unit tests voor src/csat/utils/branding.py.
Test constanten, apply_plotly_theme() en inject_css() via mocks.
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
