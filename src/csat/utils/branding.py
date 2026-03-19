"""
ZORGI brand-constanten voor CSAT-Compass.

Gebaseerd op .github/docs/zorgi-design-system.md — single source of truth.
Gebruik deze module in Streamlit (dashboard), Plotly (grafieken) en
weasyprint (PDF-rapporten) om brandconsistentie te garanderen.
"""

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

# Kleur per pijler (conform kompasmetafoor)
PILLAR_COLORS: dict[str, str] = {
    "zorgi": "#003a70",  # Dark Blue — centrum
    "pharma": "#003a70",  # Noord
    "care": "#609fce",  # Oost
    "care_admin": "#5f8495",  # West
    "erp4hc": "#7f4267",  # Zuid
}

# Gradient
GRADIENT_CSS = "linear-gradient(to right, #003a70, #7f4267, #dc2b26)"

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
        COLORS["purple"],
        COLORS["red"],
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
