"""
ZORGI brand-constanten voor CSAT-Compass.

Kleuren en typografie komen uit csat.utils.zorgi_theme (single source of truth).
Dit bestand voegt framework-specifieke theming toe voor Streamlit, Plotly en matplotlib.

Golden source: PHARMA-Conventions/zorgi/zorgi_design_system.md
"""

import base64
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

_ASSETS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "assets"
_IMG_DIR = _ASSETS_DIR / "img"
_FONTS_DIR = _ASSETS_DIR / "fonts"

# =============================================================================
# Logo-assets — conform Design System sectie 4
# =============================================================================

LOGO_ASSETS: dict[str, Path] = {
    # Sleutelnamen behouden voor backward-compatibiliteit (gebruikt in add_watermark, render_topbar, tests)
    # Bestandsnamen bijgewerkt naar de hernoemde ZORGI-assets (heartbeat_* → Logo-icoon *)
    "heartbeat_144_wit": _IMG_DIR / "Logo-icoon 144 x 144 px wit.png",
    "heartbeat_144_kleur": _IMG_DIR / "Logo-icoon 144 x 144 px.png",
    "heartbeat_512_wit": _IMG_DIR / "Logo-icoon 512 x 512 px wit.png",
    "heartbeat_512_kleur": _IMG_DIR / "Logo-icoon 512 x 512 px.png",
    "heartbeat_hires_transparant": _IMG_DIR / "Logo-icoon cirkel 512 x 512 px.png",
    "heartbeat_klein_kleur": _IMG_DIR / "Logo-icoon 144 x 144 px.png",
    "logo_icoon_144_wit": _IMG_DIR / "Logo-icoon 144 x 144 px wit.png",
    "zorgi_wit_full": _IMG_DIR / "Zorgi_wit.png",
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
            "family": f"{ZORGI_FONT_PRIMARY}, {ZORGI_FONT_FALLBACK}, sans-serif",
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
# Sidebar breedte — Streamlit standaard: min ~244px, max ~736px
# Danny: minimale breedte +10%, maximale breedte -35%
# =============================================================================

_SIDEBAR_MIN_WIDTH: int = 220  # Vaste breedte — sidebar niet meer resizable
_SIDEBAR_MAX_WIDTH: int = 220  # Gelijk aan min → resize uitgeschakeld
_SIDEBAR_DEFAULT_WIDTH: int = 220  # Idem

# Positie van expand/collapse knoppen — één constante per modus.
# visibility:hidden (ipv display:none) voor toolbar-items zorgt ervoor dat
# de layout-footprint zo identiek mogelijk blijft, maar Streamlit berekent
# intern nog ~10px verschil. _BTN_TOP_PX_PROD compenseert dit.
_BTN_TOP_PX: int = 123  # expand/collapse — identiek in demo én prod

# Publieke exports — te gebruiken in app.py (bijv. debug display)
SIDEBAR_MIN_WIDTH: int = _SIDEBAR_MIN_WIDTH
SIDEBAR_MAX_WIDTH: int = _SIDEBAR_MAX_WIDTH
SIDEBAR_DEFAULT_WIDTH: int = _SIDEBAR_DEFAULT_WIDTH
SIDEBAR_DEFAULT_MIN: int = 244  # Streamlit ingebouwd default min
SIDEBAR_DEFAULT_MAX: int = 736  # Streamlit ingebouwd default max


# =============================================================================
# Streamlit CSS-injectie
# =============================================================================

STREAMLIT_CSS: str = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;800&display=swap');

    html, body, [class*="css"] {{
        font-family: '{ZORGI_FONT_PRIMARY}', '{ZORGI_FONT_FALLBACK}', sans-serif;
    }}

    /* Voorkom dat browser scroll-positie "herstelt" na tab-wissel (DOM-anchoring) */
    html, body {{
        scroll-behavior: auto !important;
        overflow-anchor: none !important;
    }}
    [data-baseweb="tab-panel"],
    [data-testid="stAppViewMain"],
    [data-testid="stMainBlockContainer"] {{
        overflow-anchor: none !important;
    }}

    /* Headers conform Design System sectie 3 */
    h1 {{ color: {ZORGI_DARK_BLUE}; font-weight: 800; }}
    h2 {{ color: {ZORGI_GREY_BLUE}; font-weight: 800; }}
    h3 {{ color: {ZORGI_LIGHT_BLUE}; font-weight: 800; }}

    .zorgi-header {{
        background: {ZORGI_GRADIENT_CSS};
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }}

    .zorgi-card {{
        background: {ZORGI_ULTRA_LIGHT};
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }}

    .zorgi-kpi {{
        background: {ZORGI_WHITE};
        border-left: 4px solid {ZORGI_DARK_BLUE};
        border-radius: 8px;
        padding: 1rem;
    }}

    [data-testid="stMetric"] {{
        background:
            linear-gradient(to bottom, #003a70, #609fce 60%, transparent) left no-repeat,
            {ZORGI_ULTRA_LIGHT};
        background-size: 4px 100%, 100% 100%;
        border-radius: 12px;
        border: 2px solid rgba(0,58,112,0.20) !important;
        padding: 0.75rem 0.9rem 0.75rem 1.2rem;
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    /* ── GELIJKE TEGELHOOGTE: kolommen stretchen ── */
    [data-testid="stHorizontalBlock"] {{
        align-items: stretch !important;
    }}
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
        display: flex !important;
        flex-direction: column !important;
    }}
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div {{
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }}
    /* stMetric: vult volledige kolomhoogte */
    [data-testid="stMetric"] {{
        flex: 1 !important;
    }}
    /* stMarkdown-wrapper voor T8: ook stretchen zodat .zorgi-tile de hoogte erft */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div > [data-testid="stMarkdown"] {{
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }}
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div > [data-testid="stMarkdown"] > div {{
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }}

    /* ── T8 zorgi-tile: exacte kopie van stMetric-stijl + Poppins font ── */
    .zorgi-tile {{
        font-family: '{ZORGI_FONT_PRIMARY}', '{ZORGI_FONT_FALLBACK}', sans-serif !important;
        flex: 1 !important;
        background:
            linear-gradient(to bottom, #003a70, #609fce 60%, transparent) left no-repeat,
            {ZORGI_ULTRA_LIGHT};
        background-size: 4px 100%, 100% 100%;
        border-radius: 12px !important;
        border: 2px solid rgba(0,58,112,0.20) !important;
        padding: 0.75rem 0.9rem 0.75rem 1.2rem !important;
        min-height: 110px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-sizing: border-box !important;
    }}

    /* ZORGI kritiek-woord in T8 label */
    .zorgi-crit {{
        color: #dc2b26 !important;
        font-weight: 800 !important;
    }}
    /* Metric delta-tekst: geen afbreking */
    [data-testid="stMetricDelta"] > div {{
        white-space: normal !important;
        line-height: 1.3 !important;
        font-size: 0.78rem !important;
    }}
    /* Metric label: vaste grootte */
    [data-testid="stMetricLabel"] {{
        font-size: 0.78rem !important;
        line-height: 1.35 !important;
    }}

    .trend-up     {{ color: #00aa44; font-weight: 800; }}
    .trend-down   {{ color: {ZORGI_RED}; font-weight: 800; }}
    .trend-stable {{ color: {ZORGI_GREY_BLUE}; font-weight: 800; }}

    /* Sidebar — vaste breedte (min = max = 220px), resize uitgeschakeld.
       height: calc(100vh - 110px) → sidebar stopt exact aan onderkant scherm.
       overflow-y: auto → scroll mogelijk wanneer inhoud groter is dan venster. */
    [data-testid="stSidebar"] {{
        background: {ZORGI_ULTRA_LIGHT};
        top: 110px !important;
        height: calc(100vh - 110px) !important;
        overflow-y: auto !important;
        min-width: {_SIDEBAR_MIN_WIDTH}px !important;
        max-width: {_SIDEBAR_MAX_WIDTH}px !important;
        width: {_SIDEBAR_MIN_WIDTH}px !important;
    }}
    /* Sidebar-divider: compacte lijn — beheerd via widget-sectie CSS hieronder */
    /* Pijler sub-items naar rechts: radio-group met 5 labels = uniek de pijlerselectie.
       :has(label:nth-child(5)) treft enkel die radio, niet mode (2) of taal (2).
       padding-left schuift zowel het rondje als de tekst naar rechts. */
    [data-testid="stSidebar"] [role="radiogroup"]:has(label:nth-child(5)) label:not(:first-child) {{
        padding-left: 1.2rem !important;
    }}
    /* Resize-handle verbergen — veilige selectors + scoped col-resize binnen sidebar */
    [data-testid="stSidebarUserResizeHandle"],
    [data-testid="stSidebarResizeHandle"],
    [data-testid="stResizeHandle"],
    [data-testid="stSidebar"] div[style*="col-resize"],
    [data-testid="stSidebar"] div[style*="col-resize"] * {{
        display: none !important;
        pointer-events: none !important;
        width: 0 !important;
        min-width: 0 !important;
        overflow: hidden !important;
    }}
    /* stSidebarUserContent: overflow visible → tooltip kan sidebar verlaten.
       padding-top:0.75rem → meer ruimte tov topbalk.
       padding-left:0.6rem → icoon dichter bij linkerrand. */
    [data-testid="stSidebarUserContent"] {{
        width: 100% !important;
        overflow: visible !important;
        padding-top: 0.75rem !important;
        padding-left: 0.6rem !important;
    }}
    /* Sidebar blokken: compactere verticale tussenruimte */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        gap: 0.15rem !important;
    }}
    /* Sidebar markdown titels (Pijler / Weergave-modus / Taal):
       minder ruimte boven de titel, geen extra ruimte onder de laatste keuze */
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p {{
        margin-bottom: 0.1rem !important;
        margin-top: 0 !important;
    }}
    /* Sidebar radio-container: negatieve margin trekt de volgende divider dichter naar
       de laatste radioknop toe (compenseert Streamlit's interne bottom-padding ~4-6px) */
    [data-testid="stSidebar"] [data-testid="stRadio"] {{
        margin-bottom: -0.3rem !important;
        padding-bottom: 0 !important;
    }}
    /* Laatste radio-label: interne padding minimaliseren */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:last-of-type,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:last-child {{
        padding-bottom: 2px !important;
        margin-bottom: 0 !important;
    }}
    /* Ruimte voor/na divider strak houden */
    [data-testid="stSidebar"] [data-testid="stDivider"] {{
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }}
    /* ── VASTE TABBALK (position:fixed) ─────────────────────────────────────
       sticky werkt niet in Streamlit (overflow:hidden op een voorouder-container).
       Originele waarden (voor volledige revert):
         position: sticky; top: 110px; (geen left/right/box-shadow/padding-top/transition)
         background: transparent !important;
         padding-bottom: 6px !important; padding-top: 6px !important;
    ── */
    [data-baseweb="tab-list"] {{
        position: fixed !important;
        top: 110px !important;
        left: {_SIDEBAR_MIN_WIDTH}px !important;
        right: 0 !important;
        z-index: 9990 !important;
        background: {ZORGI_WHITE} !important;
        gap: 6px !important;
        border-bottom: 2px solid {ZORGI_ULTRA_LIGHT} !important;
        padding: 12px 1rem 12px 5rem !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        scrollbar-width: none !important;
        box-shadow: 0 2px 6px rgba(0, 58, 112, 0.08) !important;
        transition: left 0.3s ease, padding-left 0.3s ease !important;
    }}
    /* Verberg scrollbar in WebKit (Chrome/Edge/Safari) */
    [data-baseweb="tab-list"]::-webkit-scrollbar {{
        display: none !important;
    }}
    /* Sidebar ingeklapt — :has() voor robuuste DOM-detectie ongeacht nesting;
       ~ sibling selector als fallback voor browsers zonder :has()-support.
       padding-left: 5rem → uitlijning met content (zelfde als block-container).
       5rem = 80px > 32px (breedte >> expand-knop) → geen overlap. */
    body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-baseweb="tab-list"],
    [data-testid="stSidebar"][aria-expanded="false"]
        ~ [data-testid="stAppViewContainer"] [data-baseweb="tab-list"] {{
        left: 0 !important;
        padding-left: 5rem !important;
    }}
    /* Tab-paneel: compensatie voor de vaste tabbalk (hoogte ≈ 64px) */
    [data-baseweb="tab-panel"] {{
        padding-top: 68px !important;
    }}
    /* Tabs - meerdere selectors voor Streamlit 1.28-1.55 compatibiliteit.
       font-size ook op alle kindelementen (*) gezet: Streamlit plaatst de tekst
       in een binnenste <p> of <span> met font-size:inherit die anders de
       button-font-size negeert (inherit-chain gaat voorbij onze regel). */
    [data-baseweb="tab"],
    [role="tab"],
    button[role="tab"],
    [data-baseweb="tab-list"] button {{
        background-color: {ZORGI_DARK_BLUE} !important;
        color: {ZORGI_WHITE} !important;
        border-radius: 50px !important;
        padding: 0.45rem 1.2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        border: none !important;
        min-height: 2.5rem !important;
        white-space: nowrap !important;
        flex-shrink: 0 !important;
        transition: background 0.2s ease, transform 0.15s ease !important;
        margin: 2px 0 !important;
    }}
    /* Kindelementen: enkel font-size + color forceren, geen eigen box-model */
    [data-baseweb="tab"] *,
    [role="tab"] *,
    button[role="tab"] *,
    [data-baseweb="tab-list"] button * {{
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: {ZORGI_WHITE} !important;
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 0 !important;
        min-height: unset !important;
    }}
    [data-baseweb="tab"]:hover,
    [role="tab"]:hover,
    button[role="tab"]:hover {{
        background-color: {ZORGI_GREY_BLUE} !important;
        color: white !important;
        transform: translateY(-1px) !important;
    }}
    [data-baseweb="tab"][aria-selected="true"],
    [role="tab"][aria-selected="true"],
    button[role="tab"][aria-selected="true"] {{
        background: {ZORGI_GRADIENT_CSS} !important;
        color: white !important;
        box-shadow: 0 3px 10px rgba(0, 58, 112, 0.3) !important;
    }}
    [data-baseweb="tab-highlight"],
    [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* stHeader — transparant, boven topbalk zodat toggle-knoppen zichtbaar blijven */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        z-index: 100001 !important;
    }}

    /* Collapse/Expand knoppen — FOUC-preventie via animation-delay.
       Knoppen starten onzichtbaar en verschijnen pas nadat CSS volledig is
       toegepast (na ~150ms). Zo is de "spring" naar top:130px nooit zichtbaar. */
    @keyframes zorgi-btn-appear {{
        from {{ opacity: 0; }}
        to   {{ opacity: 1; }}
    }}
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"] {{
        animation: zorgi-btn-appear 0.15s ease 0.35s both;
    }}

    /* stSidebarHeader — minimale hoogte: content start zo hoog mogelijk.
       De << knop is position:fixed en staat buiten de DOM-flow → hoogte heeft
       geen invloed op de knoppositie. */
    [data-testid="stSidebarHeader"] {{
        height: 4px !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: visible !important;
        box-sizing: border-box !important;
    }}
    /* Streamlit-navigatieknop in sidebar-header verbergen (single-page app).
       In Streamlit 1.37+ rendert Streamlit automatisch een klikbaar paginapictogram
       (stSidebarNavLink / stLogoLink / stPageLink) in de sidebar-header.
       Klikken op dit icoon triggert een navigatie-event en breekt de sidebar-layout.
       Oplossing: alle sidebar-navigatie-elementen verbergen én onklikbaar maken.
       selector :not([data-testid="stSidebarCollapseButton"]) behoudt de << knop. */
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavSeparator"],
    [data-testid="stSidebarNavLink"],
    [data-testid="stLogoLink"],
    [data-testid="stLogo"],
    [data-testid="stPageLink"],
    section[data-testid="stSidebar"] nav,
    [data-testid="stSidebarHeader"] > *:not([data-testid="stSidebarCollapseButton"]) {{
        display: none !important;
        pointer-events: none !important;
    }}
    /* << collapse-knop: left 179px, top _BTN_TOP_PX */
    [data-testid="stSidebarCollapseButton"] {{
        position: fixed !important;
        left: 179px !important;
        top: {_BTN_TOP_PX}px !important;
        z-index: 999998 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    /* Knop verbergen als sidebar ingeklapt is (expand-knop >> neemt het over) */
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] {{
        display: none !important;
    }}

    /* Native sidebar-knoppen — ZORGI-stijl zonder JS.
       >> expand : links-vast, position:fixed (buiten sidebar DOM → altijd zichtbaar).
       << collapse: rechts in sidebar-header via flex (IN flow → auto-resize werkt). */

    /* Expand-knop >> — position:fixed vrij van sidebar stacking context */
    [data-testid="stExpandSidebarButton"] {{
        position: fixed !important;
        top: {_BTN_TOP_PX}px !important;
        left: 0 !important;
        z-index: 999999 !important;
        background: {ZORGI_DARK_BLUE} !important;
        border: none !important;
        border-radius: 0 8px 8px 0 !important;
        width: 32px !important;
        height: 40px !important;
        box-shadow: 3px 2px 10px rgba(0, 0, 0, 0.30) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        font-size: 0 !important;
        color: transparent !important;
    }}
    [data-testid="stExpandSidebarButton"] > *,
    [data-testid="stExpandSidebarButton"] button > * {{
        display: none !important;
    }}
    [data-testid="stExpandSidebarButton"]::after,
    [data-testid="stExpandSidebarButton"] button::after {{
        content: ">>" !important;
        color: {ZORGI_WHITE} !important;
        font-size: 18px !important;
        font-weight: 400 !important;
        letter-spacing: 0 !important;
        line-height: 1 !important;
        display: block !important;
    }}
    [data-testid="stExpandSidebarButton"]:hover,
    [data-testid="stExpandSidebarButton"] button:hover {{
        background: {ZORGI_LIGHT_BLUE} !important;
    }}

    /* Collapse-knop << — rechts in sidebar-header (flex), IN flow, << wit */
    [data-testid="stSidebarCollapseButton"] button {{
        background: {ZORGI_DARK_BLUE} !important;
        color: transparent !important;
        font-size: 0 !important;
        border: none !important;
        border-radius: 8px 0 0 8px !important;
        width: 32px !important;
        height: 40px !important;
        min-height: 40px !important;
        box-shadow: -3px 2px 8px rgba(0, 0, 0, 0.25) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
    }}
    [data-testid="stSidebarCollapseButton"] button > * {{
        display: none !important;
    }}
    [data-testid="stSidebarCollapseButton"] button::after {{
        content: "<<" !important;
        color: {ZORGI_WHITE} !important;
        font-size: 18px !important;
        font-weight: 400 !important;
        letter-spacing: 0 !important;
        line-height: 1 !important;
        display: block !important;
    }}
    [data-testid="stSidebarCollapseButton"] button:hover {{
        background: {ZORGI_LIGHT_BLUE} !important;
    }}
    [data-testid="stSidebarCollapseButton"] svg {{
        display: none !important;
    }}

    /* Deploy-knop + drie-puntjes worden alleen in prod_mode verborgen (zie inject_css) */

    /* Actieknoppen in het hoofdpaneel — zelfde hoogte als sidebar collapse-knop (40px) */
    [data-testid="stButton"] > button {{
        height: 40px !important;
        min-height: 40px !important;
    }}
    [data-testid="stToolbar"]    {{ z-index: 100 !important; }}
    [data-testid="stDecoration"] {{ z-index: 100 !important; }}

    /* ZORGI-stijl voor help-tooltips (? icoontje).
       Meerdere selectors voor maximale compatibiliteit:
       - [role="tooltip"]          → ARIA-standaard BaseWeb popup
       - [data-baseweb="popover"]  → BaseWeb portal-container
       - kind-elementen krijgen transparant bg zodat de kleur niet dubbel valt */
    [role="tooltip"],
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-testid="stTooltipContent"] {{
        background-color: {ZORGI_DARK_BLUE} !important;
        color: {ZORGI_WHITE} !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 58, 112, 0.35) !important;
    }}
    [role="tooltip"] *,
    [data-baseweb="popover"] *,
    [data-testid="stTooltipContent"] * {{
        color: {ZORGI_WHITE} !important;
        background-color: transparent !important;
    }}

    /* Widget-label consistent met st.markdown("**...**") — Weergave-modus/Mode d'affichage
       moet dezelfde visuele stijl (font-weight, grootte) én dezelfde afspatiëring hebben
       als Pijler/Pijler, Periode/Période en Taal/Langue.
       Streamlit rendert de label als <label> of <p> ngl versie — beide targeten. */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {{
        font-weight: 700 !important;
        font-size: 1rem !important;
        color: {ZORGI_BODY_TEXT} !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.6 !important;
    }}
    /* De widget-label container: compactere bottom-margin */
    [data-testid="stWidgetLabel"] {{
        margin-bottom: 0.2rem !important;
        padding-bottom: 0 !important;
    }}
    /* Radio-opties: geen extra top-margin zodat afstand overal gelijk is */
    [data-testid="stRadio"] > div + div {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    /* Radio optietekst: uniforme letterhoogte in alle secties (Pijler/Modus/Taal) */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        font-size: 0.9375rem !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label span {{
        font-size: 0.9375rem !important;
    }}

    /* ── Pure CSS tooltip voor Weergave-modus / Mode d'affichage ─────────────
       Vervangt Streamlit help-parameter: zelfde ZORGI-stijl, gegarandeerd bold
       label via <strong> (HTML-gebaseerd, niet afhankelijk van emotion-CSS). */
    p.zorgi-section-label {{
        position: relative !important;   /* Anker: tooltip positioneert t.o.v. deze <p> */
        margin-top: 0 !important;
        margin-bottom: 1rem !important;  /* Zelfde als Streamlit default <p> → zelfde spatiëring als Pijler/Taal */
        font-size: 1rem !important;
        color: {ZORGI_BODY_TEXT} !important;
        line-height: 1.6 !important;
    }}
    /* Help-badge: ronde knop identiek aan Streamlit native ? icoon */
    .zorgi-help-tip {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 16px;
        height: 16px;
        background: {ZORGI_GREY_BLUE};
        color: {ZORGI_WHITE};
        border-radius: 50%;
        font-size: 0.65rem;
        font-weight: 800;
        cursor: help;
        vertical-align: middle;
        margin-left: 3px;
        flex-shrink: 0;
        overflow: visible;
        outline: none;
        /* position: static (default) → tooltip positioneert t.o.v. de <p> */
    }}
    /* Tooltip popup — standaard verborgen.
       Bij hover/focus: position:fixed om overflow clipping te omzeilen.
       left:165px → rechts van het ?-icoon (icoon staat op ~155px viewport-x).
       top:390px → zelfde hoogte als het ?-icoon (Weergave-modus ~390px viewport-y).
       width:190px → past exact voor de twee modusnamen op één lijn elk. */
    .zorgi-help-tip-content {{
        display: none;
        position: absolute;
        z-index: 99999;
        background: {ZORGI_DARK_BLUE};
        color: {ZORGI_WHITE} !important;
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        font-size: 0.875rem;
        font-weight: 400 !important;
        white-space: normal;
        width: 190px;
        left: 0;
        top: calc(100% + 2px);
        line-height: 1.5;
        box-shadow: 0 4px 12px rgba(0, 58, 112, 0.35);
    }}
    .zorgi-help-tip:hover .zorgi-help-tip-content,
    .zorgi-help-tip:focus .zorgi-help-tip-content,
    .zorgi-help-tip:focus-within .zorgi-help-tip-content {{
        display: block !important;
        position: fixed !important;
        left: 165px !important;
        top: 390px !important;
        width: 310px !important;
        max-width: 310px !important;
        white-space: nowrap !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 0.8rem !important;
        line-height: 1.6 !important;
        border-radius: 6px !important;
        box-shadow: 0 4px 16px rgba(0, 58, 112, 0.45) !important;
        z-index: 999999 !important;
    }}
    .zorgi-help-tip-content strong {{
        color: {ZORGI_WHITE} !important;
        font-weight: 400 !important;
    }}
    /* Maandnamen (januari/juli, janvier/juillet): bold */
    .zorgi-help-tip-content .zorgi-tip-month {{
        font-weight: 700 !important;
        color: {ZORGI_WHITE} !important;
    }}

    /* Ankerlink-icoon (⛓) naast headings verbergen.
       Streamlit genereert automatisch [data-testid="stHeaderAnchor"] naast elke heading.
       Klikken op dit icoon verandert de URL-hash en triggert een browser-scroll,
       waardoor de position:fixed topbalk tijdelijk wegspringt.
       Oplossing: volledig verbergen + niet-klikbaar. */
    [data-testid="stHeaderAnchor"],
    .stMarkdown a[href^="#"],
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {{
        display: none !important;
        pointer-events: none !important;
    }}

    /* Inhoudspaneel: normale padding-top */
    .main .block-container {{
        padding-top: 55px !important;
    }}


    /* AUTO-RESIZE INHOUDSPANEEL — kern van het probleem:
       Zolang stSidebar min-width:Xpx !important heeft, blijft het een kolom innemen in de
       CSS layout, ook wanneer visueel ingeklapt via transform:translateX(-100%).
       Fix: forceer min-width/max-width → 0 bij aria-expanded="false", zodat het CSS Grid
       de vrijgekomen breedte overdraagt aan het inhoudspaneel. */
    [data-testid="stSidebar"][aria-expanded="false"] {{
        min-width: 0 !important;
        max-width: 0 !important;
        overflow: hidden !important;
    }}
    [data-testid="stSidebar"][aria-expanded="false"]
        ~ [data-testid="stAppViewContainer"] .block-container,
    [data-testid="stSidebar"][aria-expanded="false"]
        ~ [data-testid="stAppViewContainer"] [data-testid="stMainBlockContainer"] {{
        padding-left: 1rem !important;
        max-width: 100% !important;
    }}

    /* ── ZH MINI-SIGNAALKAART KAARTJES ────────────────────────────────────────
       .zh-signal-card     : kaartje met kleurgecodeerde linker border
       .zh-score-bar-wrap  : container progress bar + drempelmarkeringen
       .zh-score-bar       : gekleurde invulbalk (breedte en kleur via inline style)
       .zh-threshold-marker: verticale lijn op drempelposities (3,0★ en 4,0★)
       REVERT: verwijder deze sectie + _zh_signal_card() helper in app.py
    ── */
    .zh-signal-card {{
        background: {ZORGI_WHITE};
        border-radius: 10px;
        padding: 0.55rem 0.8rem 0.6rem 1rem;
        margin-bottom: 0.45rem;
        border-top: 4px solid {ZORGI_ULTRA_LIGHT};
        border-right: 4px solid {ZORGI_ULTRA_LIGHT};
        border-bottom: 4px solid {ZORGI_ULTRA_LIGHT};
        border-left: 3px solid transparent;
        box-shadow: 0 1px 3px rgba(0, 58, 112, 0.08);
    }}
    .zh-score-bar-wrap {{
        position: relative;
        background: {ZORGI_ULTRA_LIGHT};
        border-radius: 3px;
        height: 5px;
        margin-top: 5px;
    }}
    .zh-score-bar {{
        height: 5px;
        border-radius: 3px;
    }}
    .zh-threshold-marker {{
        position: absolute;
        top: -2px;
        width: 1px;
        height: 9px;
        background: rgba(0, 0, 0, 0.22);
    }}

    /* ── ZH SIGNAALKAART — navigatieknop naar tab Ziekenhuizen ─────────────
       Inline HTML-knop (st.markdown unsafe_allow_html) — géén nested iframe,
       onclick werkt direct in de Streamlit-app context.
       REVERT: verwijder deze sectie en de .zorgi-tab-nav-btn in _tab_summary().
    ── */
    .zorgi-tab-nav-btn {{
        background: none;
        border: 1px solid {ZORGI_ULTRA_LIGHT};
        border-radius: 6px;
        color: {ZORGI_GREY_BLUE};
        font-size: 0.82rem;
        cursor: pointer;
        padding: 0.25rem 0.7rem;
        font-family: '{ZORGI_FONT_PRIMARY}', '{ZORGI_FONT_FALLBACK}', sans-serif;
        margin-top: 0.35rem;
        transition: background 0.15s ease, color 0.15s ease;
    }}
    /* ── stIFrame auto-resize — live getest 15/04/2026 ─────────────────────
       inject_iframe_resize() JS bepaalt de exacte hoogte via getBoundingClientRect
       (topRow + scroll-wrap + footers). Deze CSS-regels stellen de basis in.
       De spacer-verberging elimineert de 3x16px=48px gap die Streamlit produceert
       via lege placeholder-children na elke iframe-container. */
    [data-testid="stElementContainer"]:has(> .stIFrame) {{
        flex: 0 0 auto !important;
        min-height: 0 !important;
    }}
    /* Verberg lege spacer-containers na iframes (h=0px met alleen een lege div erin) */
    [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(> div:empty):not(:has(iframe)):not(:has([data-testid])) {{
        display: none !important;
    }}
    .zorgi-tab-nav-btn:hover {{
        background: {ZORGI_ULTRA_LIGHT};
        color: {ZORGI_DARK_BLUE};
    }}
</style>
"""

# =============================================================================
# JavaScript — eigen ZORGI sidebar-toggle knop
#
# BELANGRIJK: st.markdown() filtert <script> tags — JavaScript wordt NIET
# uitgevoerd. Daarom gebruiken we st.components.v1.html() die een iframe
# aanmaakt waarin JavaScript WEL draait. Vanuit die iframe bereiken we de
# Streamlit parent-DOM via window.parent.document.
#
# inject_sidebar_toggle() moet NA alle pagina-content worden aangeroepen
# (einde van main()), anders blokkeert de iframe-component de rendering.
# =============================================================================

# _SIDEBAR_TOGGLE_JS: str = f"""
# <script>
# (function() {{
#     var doc = window.parent.document;
#     if (doc.getElementById('zorgi-sidebar-toggle')) return;

#     var btn = doc.createElement('button');
#     btn.id = 'zorgi-sidebar-toggle';
#     btn.setAttribute('aria-label', 'Toggle sidebar');
#     btn.title = 'Sidebar in/uitklappen';
#     doc.body.appendChild(btn);

#     function isSidebarOpen() {{
#         var sb = doc.querySelector('[data-testid="stSidebar"]');
#         if (sb) {{
#             var exp = sb.getAttribute('aria-expanded');
#             if (exp === 'true') return true;
#             if (exp === 'false') return false;
#         }}
#         if (doc.querySelector('[data-testid="stExpandSidebarButton"]')) return false;
#         if (doc.querySelector('[data-testid="stSidebarCollapseButton"]')) return true;
#         return true;
#     }}

#     function updateIcon() {{
#         btn.textContent = isSidebarOpen() ? '\\u00AB' : '\\u00BB';
#     }}

#     btn.addEventListener('click', function(e) {{
#         e.preventDefault();
#         e.stopPropagation();
#         if (isSidebarOpen()) {{
#             var c = doc.querySelector('[data-testid="stSidebarCollapseButton"] button');
#             if (c) c.click();
#         }} else {{
#             var x = doc.querySelector('[data-testid="stExpandSidebarButton"] button');
#             if (x) x.click();
#         }}
#         setTimeout(updateIcon, 150);
#     }});

#     var obs = new MutationObserver(function() {{ updateIcon(); }});
#     obs.observe(doc.body, {{
#         childList: true, subtree: true,
#         attributes: true, attributeFilter: ['aria-expanded', 'data-collapsed']
#     }});
#     updateIcon();
# }})();
# </script>
# """


def inject_css(st, prod_mode: bool = False) -> None:
    """
    Injecteer ZORGI CSS in een Streamlit-app (alleen styles, geen JS).

    De sidebar-toggle knop wordt apart geïnjecteerd via inject_sidebar_toggle()
    aan het EINDE van main() — zodat de iframe-component de paginrendering
    niet blokkeert.

    Args:
        st:        Streamlit module (doorgegeven om circulaire imports te vermijden)
        prod_mode: True → verbergt Deploy-knop en drie-puntjes-menu (productie-modus)
    """
    st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)
    if prod_mode:
        st.markdown(
            """
            <style>
            /* Prod-modus: layout-items ONZICHTBAAR maar in layout-flow behouden.
               visibility:hidden + pointer-events:none ipv display:none →
               Streamlit's JS meet dezelfde header-hoogte als in demo →
               content-positie identiek → geen positie-shift van tabbladen.
               Portals/dropdowns (stMainMenu, stMainMenuPopover) wél display:none
               want die zitten buiten de layout-flow. */
            [data-testid="stAppDeployButton"]     { visibility: hidden !important; pointer-events: none !important; }
            [data-testid="stMainMenuButton"]      { visibility: hidden !important; pointer-events: none !important; }
            [data-testid="stToolbarActions"]      { visibility: hidden !important; pointer-events: none !important; }
            [data-testid="stToolbarActionButton"] { visibility: hidden !important; pointer-events: none !important; }
            [data-testid="stDecoration"]          { visibility: hidden !important; opacity: 0 !important; }
            /* Portals: display:none is veilig (zitten niet in layout-flow) */
            [data-testid="stMainMenu"]            { display: none !important; }
            [data-testid="stMainMenuPopover"]     { display: none !important; }
            /* Tabs zitten ~10px hoger in prod dan demo → padding verhogen om tabs naar beneden te duwen.
               Demo-basis = 55px. Huidige waarde: 65px. Aanpasbaar. */
            .main .block-container,
            [data-testid="stMainBlockContainer"]  { padding-top: 80px !important; }
            </style>
            """.replace("PROD_BTN_TOP", f"{_BTN_TOP_PX}px"),
            unsafe_allow_html=True,
        )


def inject_tab_font_css(st) -> None:
    """
    Injecteer tab-font-size CSS NA het renderen van de tabs.

    Moet ná st.tabs() worden aangeroepen zodat deze <style>-tag in de DOM
    verschijnt na de emotion-CSS van Streamlit en de cascade wint.
    Font-size ook op kindelementen (*) gezet: Streamlit plaatst de tab-tekst
    in een binnenste <p>/<span> met font-size:inherit.

    Args:
        st: Streamlit module
    """
    st.markdown(
        "<style>"
        "html body [data-baseweb='tab'],"
        "html body [role='tab'],"
        "html body button[role='tab'] {"
        "    font-size: 1rem !important;"
        "}"
        "html body [data-baseweb='tab'] *,"
        "html body [role='tab'] *,"
        "html body button[role='tab'] * {"
        "    font-size: 1rem !important;"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )


# =============================================================================
# JavaScript — ZORGI sidebar toggle-knop
#
# inject_sidebar_toggle() voegt #zorgi-sidebar-toggle toe aan document.body
# (BUITEN de sidebar DOM) via st.components.v1.html().
# De iframe krijgt pointer-events:none via STREAMLIT_CSS zodat hij geen focus
# of klik-events onderschept.
# =============================================================================

_SIDEBAR_TOGGLE_JS: str = """
<script>
(function() {
    var doc = window.parent.document;
    if (doc.getElementById('zorgi-sidebar-toggle')) return;

    var btn = doc.createElement('button');
    btn.id = 'zorgi-sidebar-toggle';
    btn.setAttribute('aria-label', 'Toggle sidebar');
    btn.title = 'Sidebar in/uitklappen';
    doc.body.appendChild(btn);

    function isSidebarOpen() {
        var sb = doc.querySelector('[data-testid="stSidebar"]');
        if (!sb) return false;
        var exp = sb.getAttribute('aria-expanded');
        if (exp === 'true')  return true;
        if (exp === 'false') return false;
        return !!doc.querySelector('[data-testid="stSidebarCollapseButton"]');
    }

    function updateIcon() {
        btn.textContent = isSidebarOpen() ? '<<' : '>>';
    }

    btn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (isSidebarOpen()) {
            var c = doc.querySelector('[data-testid="stSidebarCollapseButton"] button')
                 || doc.querySelector('[data-testid="stSidebarCollapseButton"]');
            if (c) c.click();
        } else {
            var x = doc.querySelector('[data-testid="stExpandSidebarButton"] button')
                 || doc.querySelector('[data-testid="stExpandSidebarButton"]');
            if (x) x.click();
        }
        setTimeout(updateIcon, 200);
    });

    var obs = new MutationObserver(function() { updateIcon(); });
    obs.observe(doc.body, {
        childList: true, subtree: true,
        attributes: true,
        attributeFilter: ['aria-expanded', 'data-collapsed', 'style', 'class']
    });
    updateIcon();
})();
</script>
"""


def inject_tab_scroll_reset() -> None:
    """
    Injecteer scroll-naar-boven bij tabbladwissel.

    Strategie (3 lagen):
    1. CSS: overflow-anchor:none + scroll-behavior:auto in STREAMLIT_CSS
       → voorkomt dat browser scroll-positie "herstelt" na DOM-wijziging
    2. JavaScript _zorgiTop():
       - blur() van actief element (voorkomt scroll-into-view na React-focus)
       - scrollTo({top:0, behavior:'instant'}) op window
       - scrollTop=0 op alle bekende Streamlit-containers
       - ancestor-walk vanuit [data-baseweb="tab-panel"] omhoog
       - rAF-keten (8 frames, ~133ms) + timeouts (100/300/600/1000ms)
    3. Remove/re-add handler bij elke Streamlit-rerun (iframe vernietigd/hergemaakt)
    """
    import streamlit.components.v1 as _stc_inner

    _js = """<style>html,body{margin:0;padding:0;height:1px;overflow:hidden}</style>
<script>
(function() {
    var w = window.parent, d = w.document;

    /* ── Scroll-functie: raakt alle mogelijke scroll-containers ── */
    function _zorgiTop() {
        /* Blur actief element - React focust na tabklik op de knop,
           browser scrollt dan naar het gefocuste element (scroll-into-view).
           Blur() annuleert dit. */
        try { if (d.activeElement && d.activeElement !== d.body) d.activeElement.blur(); } catch(_) {}

        /* Window + document root */
        try { w.scrollTo({top:0, left:0, behavior:'instant'}); } catch(_) {
            try { w.scrollTo(0, 0); } catch(_) {}
        }
        try { d.documentElement.scrollTop = 0; } catch(_) {}
        try { d.body.scrollTop = 0; } catch(_) {}

        /* Expliciete Streamlit-containers */
        ['#root','[data-testid="stApp"]','[data-testid="stAppViewContainer"]',
         '[data-testid="stAppViewMain"]','[data-testid="stMainBlockContainer"]','.main']
        .forEach(function(q) {
            try { var e = d.querySelector(q); if (e) e.scrollTop = 0; } catch(_) {}
        });

        /* Ancestor-walk vanuit het tab-panel omhoog (vangt alle versies op) */
        try {
            var tp = d.querySelector('[data-baseweb="tab-panel"]');
            var el = tp ? tp.parentElement : null, n = 0;
            while (el && el !== d.documentElement && n++ < 12) {
                el.scrollTop = 0;
                el = el.parentElement;
            }
        } catch(_) {}
    }

    /* ── Registreer handler (remove/re-add voor rerun-veiligheid) ── */
    if (typeof d.__zorgiScrollHandler === 'function') {
        d.removeEventListener('click', d.__zorgiScrollHandler, true);
    }
    d.__zorgiScrollHandler = function(e) {
        var el = e.target;
        while (el && el !== d.documentElement) {
            if (el.getAttribute && el.getAttribute('data-baseweb') === 'tab') {
                /* Direct + rAF-keten (8 frames) + timeouts */
                _zorgiTop();
                (function raf(n) {
                    if (n <= 0) return;
                    try { w.requestAnimationFrame(function() { _zorgiTop(); raf(n-1); }); } catch(_) {}
                })(8);
                setTimeout(_zorgiTop, 100);
                setTimeout(_zorgiTop, 300);
                setTimeout(_zorgiTop, 600);
                setTimeout(_zorgiTop, 1000);
                break;
            }
            el = el.parentElement;
        }
    };
    d.addEventListener('click', d.__zorgiScrollHandler, true);
})();
</script>"""
    _stc_inner.html(_js, height=1, scrolling=False)


def inject_tab_persistence() -> None:
    """
    Injecteer tab-persistentie bij Streamlit-rerun (bv. taalwissel, pijlerwijziging).

    Strategie — MutationObserver + localStorage (geen Python-afhankelijkheid):
    - JS tracker: bij elke tabklik → localStorage['zorgi_tab_idx'] bijwerken
    - JS restore: MutationObserver bewaakt de tabbalk; zodra de DOM 200ms stabiel is
      (= Streamlit klaar met renderen), wordt de juiste tab EENMALIG geklikt
    - Geen race condition: we klikken pas NADAT React klaar is, nooit ertijdens
    - Absolute fallback: na 3s alsnog proberen (veiligheidsnetz voor trage renders)
    """
    import streamlit.components.v1 as _stc_inner

    _js = """<style>html,body{margin:0;padding:0;height:1px;overflow:hidden}</style>
<script>
(function() {
    var w = window.parent, d = w.document;
    var TAB_SEL = '[data-baseweb="tab-list"] [data-baseweb="tab"]';
    var STORAGE_KEY = 'zorgi_tab_idx';
    var _restored = false;

    /* ── Klik de juiste tab ── */
    function doRestore(idx) {
        if (_restored) return;
        var tabs = d.querySelectorAll(TAB_SEL);
        if (!tabs || !tabs[idx]) return;
        _restored = true;
        tabs[idx].click();
    }

    /* ── Herstel NADAT DOM stabiel is (Streamlit klaar met renderen) ── */
    function restoreWhenStable() {
        var idx;
        try { idx = parseInt(w.localStorage.getItem(STORAGE_KEY) || '0', 10); } catch(e) { return; }
        if (!idx || idx <= 0) { _restored = true; return; }

        /* Zoek de tabbalk; wacht als die er nog niet is */
        var tabList = d.querySelector('[data-baseweb="tab-list"]');
        if (!tabList) { setTimeout(restoreWhenStable, 150); return; }

        /* Bewaar tijdstip laatste DOM-wijziging in de tabbalk */
        var lastChange = Date.now();
        var obs = new MutationObserver(function() { lastChange = Date.now(); });
        obs.observe(tabList, { childList: true, subtree: true, attributes: true });

        /* Poll elke 100ms: als 200ms geen wijziging → Streamlit klaar → klikken */
        (function poll() {
            if (_restored) { obs.disconnect(); return; }
            if (Date.now() - lastChange >= 200) {
                obs.disconnect();
                doRestore(idx);
            } else {
                setTimeout(poll, 100);
            }
        })();

        /* Absolute fallback na 3s (trage renders) */
        setTimeout(function() { obs.disconnect(); doRestore(idx); }, 3000);
    }

    /* ── Koppel tracker aan elk tabblad ── */
    function attachTrackers() {
        d.querySelectorAll(TAB_SEL).forEach(function(tab, idx) {
            if (tab.__zorgiPersistTracked) return;
            tab.__zorgiPersistTracked = true;
            tab.addEventListener('click', function() {
                try { w.localStorage.setItem(STORAGE_KEY, idx.toString()); } catch(e) {}
            });
        });
    }

    /* ── Start: tabbalk zoeken + restore triggeren + trackers koppelen ── */
    setTimeout(function() { restoreWhenStable(); attachTrackers(); }, 100);
})();
</script>"""
    _stc_inner.html(_js, height=1, scrolling=False)


def inject_iframe_resize() -> None:
    """
    Resize alle sorteerbare-tabel iframes naar hun exacte content-hoogte.

    Probleem: Streamlit's emotion-cache hardcodeert height op stElementContainer.
    scrollHeight klopt niet (bevat lege scroll-wrap ruimte via max-height).

    Oplossing: meet topRow + scroll-wrap + footers direct via getBoundingClientRect.
    Dit is de enige betrouwbare maat — live getest 14/04/2026.
    Wordt ook herhaald bij tabbladwissel via click-listener.
    """
    import streamlit.components.v1 as _stc_inner

    _js = """<style>html,body{margin:0;padding:0;height:1px;overflow:hidden}</style>
<script>
(function() {
    var d = window.parent.document;

    function resizeAll() {
        var containers = d.querySelectorAll(
            '[data-testid="stElementContainer"]:has(> .stIFrame)'
        );
        containers.forEach(function(c) {
            var iframe = c.querySelector('iframe');
            if (!iframe) return;
            try {
                var doc = iframe.contentDocument;
                if (!doc) return;
                var topRow = doc.querySelector('.top-row');
                var wrap   = doc.querySelector('.scroll-wrap');
                if (!wrap) return;  /* geen sorteerbare tabel — overslaan */
                var footers = doc.querySelectorAll('p.footer');
                var topH    = topRow ? Math.round(topRow.getBoundingClientRect().height) : 0;
                var wrapH   = Math.round(wrap.getBoundingClientRect().height);
                var footerH = 0;
                footers.forEach(function(p) {
                    footerH += Math.round(p.getBoundingClientRect().height) + 4;
                });
                /* 4px gap topRow→wrap, 8px onderste padding */
                var realH = topH + 4 + wrapH + (footerH ? footerH + 8 : 0) + 8;
                if (realH > 50) {
                    c.style.setProperty('height', realH + 'px', 'important');
                    c.style.setProperty('flex', '0 0 ' + realH + 'px', 'important');
                    iframe.style.setProperty('height', realH + 'px', 'important');
                }
            } catch(e) {}
        });
    }

    /* Initiële resize — iframes laden asynchroon */
    setTimeout(resizeAll, 250);
    setTimeout(resizeAll, 700);
    setTimeout(resizeAll, 1400);

    /* Herhaal bij elke tabbladwissel */
    if (!d.__zorgiIframeResizeAttached) {
        d.__zorgiIframeResizeAttached = true;
        d.addEventListener('click', function(e) {
            var el = e.target;
            while (el && el !== d.documentElement) {
                if (el.getAttribute && el.getAttribute('data-baseweb') === 'tab') {
                    setTimeout(resizeAll, 350);
                    setTimeout(resizeAll, 900);
                    setTimeout(resizeAll, 1800);
                    break;
                }
                el = el.parentElement;
            }
        }, true);
    }
})();
</script>"""
    _stc_inner.html(_js, height=1, scrolling=False)


def inject_sidebar_toggle() -> None:
    """
    No-op — streamlit_js_eval en components.html() bevriezen beide de browser
    (iframe focus-capture). Piste 1 mislukt — zie handover voor alternatieve pistes.

    De >> expand-knop staat links-vast via pure CSS (position:fixed).
    De << collapse-knop zit in de sidebar header (ZORGI-gestyled).
    """


def render_topbar(
    st_container,
    today_str: str,
    prod_mode: bool = False,
    pillar_name: str = "",
    version: str = "",
    full_window_label: str = "",
    trend_window_label: str = "",
) -> None:
    """
    Render de vaste ZORGI branded topbalk bovenaan het dashboard.

    Args:
        st_container:        st module of st.empty() container
        today_str:           Datum (PROD: DD/MM/YYYY) of datum+tijd (DEMO: DD/MM/YYYY · HH:MM)
        prod_mode:           True → stToolbar/stDecoration verborgen (via inject_css)
        pillar_name:         Naam van de actieve pijler (bijv. "ZORGI PHARMA")
        version:             Versienummer (bijv. "v0.4")
        full_window_label:   Label volledig venster incl. maanden (bijv. "📊 Volledig venster · jan 2025 → mrt 2026")
        trend_window_label:  Label tendensvenster incl. maanden (bijv. "📈 Tendensvenster · jul 2025 → mrt 2026")
    """
    # Logo laden: volledig ZORGI wit logo (icoon + woordmerk + tagline)
    logo_path = LOGO_ASSETS.get("zorgi_wit_full")
    logo_html = ""
    if logo_path and logo_path.exists():
        b64 = base64.b64encode(logo_path.read_bytes()).decode()
        logo_html = (
            f'<img src="data:image/png;base64,{b64}" '
            f'height="40" style="display:block;opacity:1;margin-left:16px" alt="ZORGI">'
        )

    # DEMO-badge — enkel zichtbaar wanneer niet in productie-modus
    demo_badge = "" if prod_mode else '<span class="zorgi-topbar-demo-badge">DEMO</span>'

    # Linker sectie — kompas icoon (huidig app-icoon 🧭) + CSAT-Compass label + pijlernaam + vensters
    _compass_svg = '<span style="font-size:13px;line-height:1;flex-shrink:0">🧭</span>'

    # Venster-label — enkel de actieve modus tonen (full_window_label bevat de geselecteerde)
    _active_label = full_window_label or trend_window_label
    windows_html = (
        (
            f'<div class="zorgi-topbar-windows">'
            f'<span class="zorgi-topbar-win">{_active_label}</span>'
            f"</div>"
        )
        if _active_label
        else ""
    )

    if pillar_name:
        left_html = (
            f'<div class="zorgi-topbar-pillar">'
            f'<div class="zorgi-topbar-app-label-row">'
            f"{_compass_svg}"
            f'<span class="zorgi-topbar-app-label">CSAT-Compass</span>'
            f"{demo_badge}"
            f"</div>"
            f'<span class="zorgi-topbar-pillar-name">{pillar_name}</span>'
            f"{windows_html}"
            f"</div>"
        )
    else:
        left_html = (
            f'<div class="zorgi-topbar-pillar">'
            f'<div class="zorgi-topbar-app-label-row">'
            f"{_compass_svg}"
            f'<span class="zorgi-topbar-app-label">CSAT-Compass</span>'
            f"{demo_badge}"
            f"</div>"
            f'<span class="zorgi-topbar-pillar-name">ZORGI</span>'
            f"</div>"
        )

    markup = f"""
<style>
.zorgi-topbar {{
    position: fixed; top: 0; left: 0; right: 0;
    height: 110px; z-index: 100000;
    background: {ZORGI_GRADIENT_CSS};
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 28px;
    box-shadow: 0 3px 14px rgba(0, 0, 0, 0.32);
    font-family: 'Poppins', Verdana, sans-serif;
}}
.zorgi-topbar-left {{
    display: flex; align-items: center; gap: 1rem; padding-left: 28px;
}}
.zorgi-topbar-pillar {{
    display: flex; flex-direction: column; gap: 0.15rem;
}}
.zorgi-topbar-app-label-row {{
    display: flex; align-items: center; gap: 6px;
}}
.zorgi-topbar-app-label {{
    color: rgba(255,255,255,0.62); font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.14em;
}}
.zorgi-topbar-demo-badge {{
    font-size: 9px; font-weight: 800; letter-spacing: 1.5px;
    padding: 2px 7px; border-radius: 4px;
    background: #dc2b26; color: #fff;
    border: 1px solid rgba(255,255,255,0.3);
    margin-left: 4px;
}}
.zorgi-topbar-pillar-name {{
    color: white; font-weight: 800; font-size: 1.8rem;
    line-height: 1.1; letter-spacing: 0.01em;
}}
.zorgi-topbar-windows {{
    display: flex; align-items: center; gap: 8px; margin-top: 2px;
}}
.zorgi-topbar-win {{
    color: rgba(255,255,255,0.72); font-size: 0.89rem; font-weight: 300;
}}
.zorgi-topbar-win-sep {{
    width: 1px; height: 10px; background: rgba(255,255,255,0.25);
    display: inline-block; vertical-align: middle;
}}
.zorgi-topbar-right {{
    display: flex; align-items: center; gap: 14px;
}}
.zorgi-topbar-meta-block {{
    display: flex; align-items: center; gap: 2px;
}}
.zorgi-topbar-meta-text {{
    display: flex; flex-direction: column; align-items: flex-start;
}}
.zorgi-topbar-version {{
    font-size: 12px; font-weight: 300; color: #ffffff; line-height: 1.4;
}}
.zorgi-topbar-date {{
    font-size: 12px; font-weight: 300; color: #ffffff; line-height: 1.4;
}}
.zorgi-topbar-copy {{
    font-size: 10px; font-weight: 300; color: #ffffff; line-height: 1.4;
}}
.zorgi-topbar-dvline {{
    width: 1px; height: 40px; background: rgba(255,255,255,0.18);
    display: inline-block;
}}
</style>
<div class="zorgi-topbar">
    <div class="zorgi-topbar-left">{left_html}</div>
    <div class="zorgi-topbar-right">
        <div class="zorgi-topbar-meta-block">
            <span style="font-size:40px;line-height:1;flex-shrink:0">🧭</span>
            <div class="zorgi-topbar-meta-text">
                <span class="zorgi-topbar-version">{version}</span>
                <span class="zorgi-topbar-date">{today_str}</span>
                <span class="zorgi-topbar-copy">&copy; ZORGI by Danny Depecker</span>
            </div>
        </div>
        {logo_html}
    </div>
</div>
"""
    st_container.markdown(markup, unsafe_allow_html=True)


# =============================================================================
# Matplotlib theme — Fase B2
# =============================================================================


def _register_poppins() -> str:
    """Registreer lokale Poppins TTF-bestanden bij matplotlib."""
    from matplotlib import font_manager

    registered = False
    for ttf in _FONTS_DIR.glob("Poppins-*.ttf"):
        font_manager.fontManager.addfont(str(ttf))
        registered = True
    return "Poppins" if registered else "Verdana"


def apply_matplotlib_theme() -> None:
    """Pas ZORGI brand-kleuren en -fonts toe als matplotlib rcParams."""
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
    """Voeg het ZORGI heartbeat-icoon toe als subtiel watermark."""
    logo_path = LOGO_ASSETS.get("heartbeat_hires_transparant")
    if logo_path and logo_path.exists():
        from matplotlib.image import imread

        logo = imread(str(logo_path))
        fig.figimage(logo, xo=fig.bbox.xmax - 80, yo=10, alpha=alpha, zorder=1)
