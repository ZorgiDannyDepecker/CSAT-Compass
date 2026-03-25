"""
ZORGI brand-constanten voor CSAT-Compass.

Kleuren en typografie komen uit csat.utils.zorgi_theme (single source of truth).
Dit bestand voegt framework-specifieke theming toe voor Streamlit, Plotly en matplotlib.

Golden source: PHARMA-Conventions/zorgi/zorgi_design_system.md
"""

from pathlib import Path

from csat.utils.zorgi_theme import (
    ZORGI_BODY_TEXT,
    ZORGI_DARK_BLUE,
    ZORGI_FONT_FALLBACK,
    ZORGI_FONT_PRIMARY,
    ZORGI_GRADIENT_CSS,
    ZORGI_GREY_BLUE,
    ZORGI_LIGHT_BLUE,
    ZORGI_PILLAR_COLORS,
    ZORGI_PURPLE,
    ZORGI_RED,
    ZORGI_ULTRA_LIGHT,
    ZORGI_WHITE,
)

# =============================================================================
# Backward-compatible aliases
# Bestaande code die COLORS["dark_blue"] of PILLAR_COLORS gebruikt blijft werken.
# =============================================================================

COLORS: dict[str, str] = {
    "dark_blue": ZORGI_DARK_BLUE,
    "red": ZORGI_RED,
    "purple": ZORGI_PURPLE,
    "grey_blue": ZORGI_GREY_BLUE,
    "light_blue": ZORGI_LIGHT_BLUE,
    "ultra_light_blue": ZORGI_ULTRA_LIGHT,
    "white": ZORGI_WHITE,
    "text": ZORGI_BODY_TEXT,
}

GRADIENT_CSS = ZORGI_GRADIENT_CSS

# =============================================================================
# Paden — statische assets
# =============================================================================

_STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"
_IMG_DIR = _STATIC_DIR / "img"
_FONTS_DIR = _STATIC_DIR / "fonts"

# =============================================================================
# Logo-assets — conform Design System sectie 4
# =============================================================================

LOGO_ASSETS: dict[str, Path] = {
    "heartbeat_144_wit": _IMG_DIR / "heartbeat_144_wit.png",
    "heartbeat_144_kleur": _IMG_DIR / "heartbeat_144_kleur.png",
    "heartbeat_512_wit": _IMG_DIR / "heartbeat_512_wit.png",
    "heartbeat_512_kleur": _IMG_DIR / "heartbeat_512_kleur.png",
    "heartbeat_hires_transparant": _IMG_DIR / "heartbeat_hires_transparant.png",
    "heartbeat_klein_kleur": _IMG_DIR / "heartbeat_klein_kleur.png",
}

# =============================================================================
# Pijlerkleuren — re-export vanuit zorgi_theme (backward-compatible)
# =============================================================================

PILLAR_COLORS: dict[str, str] = ZORGI_PILLAR_COLORS

# =============================================================================
# Plotly theme
# =============================================================================

PLOTLY_LAYOUT: dict = {
    "font": {
        "family": f"{ZORGI_FONT_PRIMARY}, {ZORGI_FONT_FALLBACK}, sans-serif",
        "color": ZORGI_BODY_TEXT,
    },
    "paper_bgcolor": ZORGI_WHITE,
    "plot_bgcolor": ZORGI_ULTRA_LIGHT,
    "colorway": [
        ZORGI_DARK_BLUE,
        ZORGI_LIGHT_BLUE,
        ZORGI_GREY_BLUE,
        "#a06b8a",  # Light Purple — OAZIS
        ZORGI_PURPLE,
    ],
    "title": {
        "font": {
            "color": ZORGI_DARK_BLUE,
            "size": 16,
        }
    },
    "legend": {
        "bgcolor": ZORGI_ULTRA_LIGHT,
        "bordercolor": ZORGI_LIGHT_BLUE,
        "borderwidth": 1,
    },
}

# Kleurenreeks voor multi-pijler charts (volgorde = kompas: centrum → N → O → W → Z)
PILLAR_COLORWAY: list[str] = list(PILLAR_COLORS.values())


def apply_plotly_theme(fig):
    """
    Pas het ZORGI brand-theme toe op een Plotly figuur.

    Args:
        fig: Plotly figure object

    Returns:
        Figuur met ZORGI-stijl toegepast
    """
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# =============================================================================
# Streamlit CSS-injectie
# =============================================================================

STREAMLIT_CSS: str = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;800&display=swap');

    html, body, [class*="css"] {{
        font-family: '{ZORGI_FONT_PRIMARY}', '{ZORGI_FONT_FALLBACK}', sans-serif;
    }}

    /* Headers conform Design System sectie 3 */
    h1 {{ color: {ZORGI_DARK_BLUE}; font-weight: 800; }}
    h2 {{ color: {ZORGI_GREY_BLUE}; font-weight: 800; }}
    h3 {{ color: {ZORGI_LIGHT_BLUE}; font-weight: 800; }}

    /* Gradient header-blok */
    .zorgi-header {{
        background: {ZORGI_GRADIENT_CSS};
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }}

    /* Kaartcomponent */
    .zorgi-card {{
        background: {ZORGI_ULTRA_LIGHT};
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }}

    /* KPI-blok */
    .zorgi-kpi {{
        background: {ZORGI_WHITE};
        border-left: 4px solid {ZORGI_DARK_BLUE};
        border-radius: 8px;
        padding: 1rem;
    }}

    /* Streamlit metric-widget */
    [data-testid="stMetric"] {{
        background: {ZORGI_ULTRA_LIGHT};
        border-radius: 12px;
        padding: 0.75rem;
    }}

    /* Trend-indicatoren */
    .trend-up     {{ color: #00aa44; font-weight: 800; }}
    .trend-down   {{ color: {ZORGI_RED}; font-weight: 800; }}
    .trend-stable {{ color: {ZORGI_GREY_BLUE}; font-weight: 800; }}

    /* Sidebar branding */
    [data-testid="stSidebar"] {{
        background: {ZORGI_ULTRA_LIGHT};
    }}
</style>
"""


def inject_css(st) -> None:
    """
    Injecteer ZORGI CSS in een Streamlit-app.

    Args:
        st: Streamlit module (doorgegeven om circulaire imports te vermijden)

    Gebruik in app.py:
        from csat.utils.branding import inject_css
        import streamlit as st
        inject_css(st)
    """
    st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)


# =============================================================================
# Matplotlib theme — Fase B2
# =============================================================================


def _register_poppins() -> str:
    """
    Registreer lokale Poppins TTF-bestanden bij matplotlib.

    Zoekt in src/static/fonts/ naar Poppins-*.ttf bestanden en registreert
    ze via matplotlib.font_manager. Valt terug op Verdana als er geen
    TTF-bestanden gevonden worden.

    Returns:
        Fontnaam 'Poppins' indien beschikbaar, anders 'Verdana'.
    """
    from matplotlib import font_manager

    registered = False
    for ttf in _FONTS_DIR.glob("Poppins-*.ttf"):
        font_manager.fontManager.addfont(str(ttf))
        registered = True
    return "Poppins" if registered else "Verdana"


def apply_matplotlib_theme() -> None:
    """
    Pas ZORGI brand-kleuren en -fonts toe als matplotlib rcParams.

    Registreert lokale Poppins-fonts (indien aanwezig in src/static/fonts/)
    en configureert kleuren, achtergronden en typografie conform het
    ZORGI Design System.

    Gebruik:
        from csat.utils.branding import apply_matplotlib_theme
        apply_matplotlib_theme()
        # Alle volgende plots gebruiken nu ZORGI-stijl
    """
    import matplotlib.pyplot as plt

    font_name = _register_poppins()

    plt.rcParams.update(
        {
            "font.family": [font_name, ZORGI_FONT_FALLBACK, "sans-serif"],
            "font.weight": "light",
            "axes.titleweight": "800",
            "axes.prop_cycle": plt.cycler(color=list(ZORGI_PILLAR_COLORS.values())),
            "axes.facecolor": ZORGI_ULTRA_LIGHT,
            "figure.facecolor": ZORGI_WHITE,
            "axes.edgecolor": ZORGI_GREY_BLUE,
            "axes.labelcolor": ZORGI_DARK_BLUE,
            "text.color": ZORGI_BODY_TEXT,
            "xtick.color": ZORGI_GREY_BLUE,
            "ytick.color": ZORGI_GREY_BLUE,
        }
    )


def add_watermark(fig, alpha: float = 0.08) -> None:
    """
    Voeg het ZORGI heartbeat-icoon toe als subtiel watermark
    in de rechteronderhoek van een matplotlib-figuur.

    Args:
        fig:   Matplotlib figure object
        alpha: Transparantie (standaard 0.08 — nauwelijks zichtbaar)
    """
    logo_path = LOGO_ASSETS.get("heartbeat_hires_transparant")
    if logo_path and logo_path.exists():
        from matplotlib.image import imread

        logo = imread(str(logo_path))
        fig.figimage(logo, xo=fig.bbox.xmax - 80, yo=10, alpha=alpha, zorder=1)
