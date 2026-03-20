"""
Unit tests voor src/csat/utils/branding.py.
Test constanten, apply_plotly_theme() en inject_css() via mocks.
"""

from unittest.mock import MagicMock

from csat.utils.branding import (
    COLORS,
    GRADIENT_CSS,
    PILLAR_COLORS,
    PILLAR_COLORWAY,
    PLOTLY_LAYOUT,
    STREAMLIT_CSS,
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
