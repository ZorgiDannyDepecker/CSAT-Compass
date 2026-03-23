"""
ZORGI brand-constanten voor CSAT-Compass.

Gebaseerd op docs/01-strategisch/ZORGI_Design_System.md — single source of truth.
Gebruik deze module in Streamlit (dashboard), Plotly (grafieken) en
weasyprint (PDF-rapporten) om brandconsistentie te garanderen.
"""

from pathlib import Path

# =============================================================================
# Kleuren
# =============================================================================

COLORS: dict[str, str] = {
    # Primaire kleuren
    "dark_blue": "#003a70",
    "red": "#dc2b26",
    "purple": "#7f4267",
    # Secundaire kleuren
    "grey_blue": "#5f8495",
    "light_blue": "#609fce",
    "ultra_light_blue": "#d7e7f3",
    # Basiskleuren
    "white": "#ffffff",
    "text": "#1a1a1a",
}


# Gradient
GRADIENT_CSS = "linear-gradient(to right, #003a70, #7f4267, #dc2b26)"

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
# Pijlerkleuren
# =============================================================================

# Kleur per pijler (conform kompasmetafoor en Design System §3.1)
PILLAR_COLORS: dict[str, str] = {
    "zorgi": "#003a70",  # Dark Blue — centrum
    "pharma": "#609fce",  # Light Blue — noord
    "care": "#5f8495",  # Grey Blue — oost
    "care_admin": "#a06b8a",  # Light Purple — west (afgeleide gradient)
    "erp4hc": "#7f4267",  # Purple — zuid
}

# =============================================================================
# Plotly theme
# =============================================================================

PLOTLY_LAYOUT: dict = {
    "font": {
        "family": "Poppins, Verdana, sans-serif",
        "color": COLORS["text"],
    },
    "paper_bgcolor": COLORS["white"],
    "plot_bgcolor": COLORS["ultra_light_blue"],
    "colorway": [
        COLORS["dark_blue"],
        COLORS["light_blue"],
        COLORS["grey_blue"],
        "#a06b8a",  # Light Purple — OAZIS
        COLORS["purple"],
    ],
    "title": {
        "font": {
            "color": COLORS["dark_blue"],
            "size": 16,
        }
    },
    "legend": {
        "bgcolor": COLORS["ultra_light_blue"],
        "bordercolor": COLORS["light_blue"],
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
        font-family: 'Poppins', 'Verdana', sans-serif;
    }}

    /* Headers conform Design System sectie 3 */
    h1 {{ color: {COLORS["dark_blue"]}; font-weight: 800; }}
    h2 {{ color: {COLORS["grey_blue"]}; font-weight: 800; }}
    h3 {{ color: {COLORS["light_blue"]}; font-weight: 800; }}

    /* Gradient header-blok */
    .zorgi-header {{
        background: {GRADIENT_CSS};
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }}

    /* Kaartcomponent */
    .zorgi-card {{
        background: {COLORS["ultra_light_blue"]};
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }}

    /* KPI-blok */
    .zorgi-kpi {{
        background: {COLORS["white"]};
        border-left: 4px solid {COLORS["dark_blue"]};
        border-radius: 8px;
        padding: 1rem;
    }}

    /* Streamlit metric-widget */
    [data-testid="stMetric"] {{
        background: {COLORS["ultra_light_blue"]};
        border-radius: 12px;
        padding: 0.75rem;
    }}

    /* Trend-indicatoren */
    .trend-up     {{ color: #00aa44; font-weight: 800; }}
    .trend-down   {{ color: {COLORS["red"]}; font-weight: 800; }}
    .trend-stable {{ color: {COLORS["grey_blue"]}; font-weight: 800; }}

    /* Sidebar branding */
    [data-testid="stSidebar"] {{
        background: {COLORS["ultra_light_blue"]};
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
            "font.family": [font_name, "Verdana", "sans-serif"],
            "font.weight": "light",
            "axes.titleweight": "800",
            "axes.prop_cycle": plt.cycler(color=list(PILLAR_COLORS.values())),
            "axes.facecolor": COLORS["ultra_light_blue"],
            "figure.facecolor": COLORS["white"],
            "axes.edgecolor": COLORS["grey_blue"],
            "axes.labelcolor": COLORS["dark_blue"],
            "text.color": COLORS["text"],
            "xtick.color": COLORS["grey_blue"],
            "ytick.color": COLORS["grey_blue"],
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
