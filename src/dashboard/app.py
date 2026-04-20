"""
CSAT-Compass Streamlit Dashboard — Fase 5a.

Streamlit entry point voor het PHARMA-pijler dashboard.
Start met: streamlit run src/dashboard/app.py

Architectuur:
- Data laden: @st.cache_data → get_loader() + EvolutionAnalyser (gecached 1u)
- Data voorbereiden: DashboardExporter.prepare() — pure transformatie, niet gecached
- UI: sidebar (pijler, modus, periode, taal) + 6 tabs + Plotly grafieken
- Alle UI-strings via nl.json / fr.json — geen hardcoded labels in dit bestand
"""

from __future__ import annotations

import base64
import contextlib
import csv
import html
import io
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as _stc

# Zorg dat src/ op het Python-pad staat bij directe streamlit-run
_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from csat import __version__  # noqa: E402
from csat.config.pillars import (  # noqa: E402
    FILTER_COLUMN,
    HIGH_CRITICAL_PRIORITIES,
    PILLAR_REGISTRY,
)
from csat.config.settings import (  # noqa: E402
    ANALYSE_START_DATE,
    AVG_RESPONSE_DAYS_MAX,
    AVG_SCORE_MIN,
    CSV_FALLBACK_PATH,
    DASHBOARD_PROD_MODE,
    DB_CONN,
    HIGH_CRITICAL_MAX,
    HOSPITAL_RETENTION_MIN,
    PCT_NEGATIVE_MAX,
    PCT_POSITIVE_MIN,
    PCT_WITH_COMMENT_MIN,
    db_available,
)
from csat.core.analysers.evolution_analyser import EvolutionAnalyser  # noqa: E402
from csat.core.analysers.evolution_result import EvolutionResult, HospitalComparison  # noqa: E402
from csat.core.exporters.dashboard_exporter import (  # noqa: E402
    DashboardData,
    DashboardExporter,
    ZhSignalEntry,
)
from csat.core.loaders import get_loader  # noqa: E402
from csat.i18n import load_translations  # noqa: E402
from csat.utils.branding import (  # noqa: E402
    apply_plotly_theme,
    inject_css,
    inject_iframe_resize,
    inject_sidebar_toggle,
    inject_tab_scroll_reset,
    render_topbar,
)
from csat.utils.date_utils import parse_period, period_label  # noqa: E402
from csat.utils.zorgi_theme import (  # noqa: E402
    ZORGI_DARK_BLUE,
    ZORGI_FUNC_POSITIVE,
    ZORGI_GREY_BLUE,
    ZORGI_LIGHT_BLUE,
    ZORGI_PURPLE,
    ZORGI_RED,
    ZORGI_ULTRA_LIGHT,
)

# ---------------------------------------------------------------------------
# Constanten
# ---------------------------------------------------------------------------

_BASELINE_YEAR: int = 2025
_TREND_WINDOW_START: str = "2025-07-01"
_ACTIVE_PILLARS: frozenset[str] = frozenset({"pharma", "care", "care_admin", "erp4hc"})
_APP_VERSION: str = f"v{__version__}"


# Fasegebaseerde puntkleur (tijdlijn combo-grafiek)
_PHASE_POINT_COLOR: dict[str, str] = {
    "S1": ZORGI_RED,  # S1 - crisisperiode (jan-jun)
    "S2": ZORGI_FUNC_POSITIVE,  # S2 - herstelperiode (jul-dec)
    "Q": ZORGI_PURPLE,  # Q1/Q2 2026 - groeiperiode
}

# KPI-namen voor Tab 6 (sleutels uit settings.py / i18n)
_KPI_TARGET_ORDER: list[str] = [
    "avg_score_min",
    "pct_positive_min",
    "pct_negative_max",
    "avg_response_days_max",
    "high_critical_max",
    "pct_with_comment_min",
    "hospital_retention_min",
]

# Hoger = beter per KPI — gebruikt voor semantische kleur realisatie-balk (preview)
_KPI_HIGHER_IS_BETTER: dict[str, bool] = {
    "avg_score_min": True,
    "pct_positive_min": True,
    "pct_negative_max": False,
    "avg_response_days_max": False,
    "high_critical_max": False,
    "pct_with_comment_min": True,
    "hospital_retention_min": True,
}

# Tabel-hoogte constanten — gebruikt in _render_sortable_table() voor D en G
_DF_ROW_PX: int = 34  # pixels per tabelrij (incl. padding + border)
_DF_HEADER_PX: int = 8  # bodem-padding na de rijen
_DF_MIN_ROWS: int = 10  # minimaal te tonen rijen in tabellen D en G

# Consistente Plotly modebar-config — pan, lasso, select en autoScale verwijderd.
# resetScale2d (home-icoon) blijft bewust aanwezig: herstelt zoom na inzoomen.
_CHART_CONFIG: dict = {
    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d", "autoScale2d"],
    "displaylogo": False,
}

# Licht paars (afgeleide ZORGI-kleur) — gebruikt als target-balk in KPI Preview
_ZORGI_LIGHT_PURPLE: str = "#a06b8a"  # OAZIS-kleur uit ZORGI colorway

# Target voor rij 9 — Critical Priority CSAT (≥ 4,50★)
_CRITICAL_PRIORITY_CSAT_TARGET: float = 4.5


# ---------------------------------------------------------------------------
# Hulpfuncties
# ---------------------------------------------------------------------------


def _last_complete_period(today: date) -> tuple[int, int]:
    """Geeft (jaar, maand) van de laatste volledig afgeronde maand.

    Gegevens worden pas opgenomen na de eerste van de volgende maand:
    op 02/04/2026 → (2026, 3) — april is nog niet afgerond.
    Randgeval: op 01/01/2027 → (2026, 12) — december is de laatste volledige maand.
    """
    if today.month == 1:
        return today.year - 1, 12
    return today.year, today.month - 1


def _make_kc_dataframes(
    data: DashboardData,
    venster_modus: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Bereid df_vorig en df_huidig voor tegel 3 (Kerncijfers vergelijking).

    Aanroeper van render_kerncijfers_vergelijking: verantwoordelijk voor correcte
    slicing per venstermodus (spec-contract: slicing hoort in de aanroepende laag).

    - _load_df() is gecached (1u) — geen extra DB-aanroep.
    - Pilaar-filter via PILLAR_REGISTRY[data.pillar]["products"] + FILTER_COLUMN.
    - Start-datum filter: ADR-007 (ANALYSE_START_DATE).
    - effective_date: satisfaction_date waar beschikbaar, anders created.
    - df_huidig beperkt tot afgeronde maanden (via kpi_recent_month_name).
    - "volledig" → df_vorig = volledig baseline-jaar (bv. 2025).
    - "tendens"  → df_vorig = S2 van het baseline-jaar (jul-dec 2025).

    INVARIANT: deze functie wordt door zowel tegel 3 (venster-aware) als
    KPI-Targets (vast 'volledig') aangeroepen. Bij refactoring: zorg dat
    KPI-Targets-aanroepers altijd 'volledig' kunnen blijven gebruiken,
    ongeacht venster-modus-uitbreidingen.
    """
    df = _load_df().copy()

    # Pilaar-filter (product_domain via PILLAR_REGISTRY)
    pillar_cfg = PILLAR_REGISTRY.get(data.pillar, {})
    products_upper = [p.upper() for p in pillar_cfg.get("products", [])]
    if products_upper:
        df = df[df[FILTER_COLUMN].str.strip().str.upper().isin(products_upper)]

    # Start-datum filter (ADR-007)
    if ANALYSE_START_DATE:
        df = df[pd.to_datetime(df["created"]) >= pd.Timestamp(ANALYSE_START_DATE)]

    # effective_date: satisfaction_date waar beschikbaar, anders created
    df["_eff"] = df["satisfaction_date"].where(
        df["satisfaction_date"].notna(),
        other=pd.to_datetime(df["created"]),
    )
    df["_year"] = pd.to_datetime(df["_eff"]).dt.year
    df["_month"] = pd.to_datetime(df["_eff"]).dt.month

    _bl_yr = data.current_year - 1
    _cu_yr = data.current_year

    # Bepaal laatste afgeronde maand uit kpi_recent_month_name (bv. "2026-03" → 3).
    # Voorkomt dat lopende-maand-tickets (bv. april) in df_huidig terechtkomen.
    _max_month = 12  # fallback
    _recent = data.kpi_recent_month_name
    if _recent and _recent not in ("—", ""):
        with contextlib.suppress(IndexError, ValueError):
            _max_month = int(_recent[5:7])

    if venster_modus == "volledig":
        df_vorig = df[df["_year"] == _bl_yr].copy()
    else:  # tendens: S2 van het baseline-jaar (jul-dec)
        df_vorig = df[(df["_year"] == _bl_yr) & (df["_month"] >= 7)].copy()

    # df_huidig: alleen afgeronde maanden (≤ _max_month) — fix voor 81 vs 77 discrepantie
    df_huidig = df[(df["_year"] == _cu_yr) & (df["_month"] <= _max_month)].copy()
    return df_vorig, df_huidig


# ---------------------------------------------------------------------------
# Data-caching
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600, show_spinner=False)
def _load_df() -> pd.DataFrame:
    """Laad de volledige CSAT-data (gecached, 1 uur geldig)."""
    loader = get_loader(DB_CONN, CSV_FALLBACK_PATH, force_csv=not db_available())
    return loader.load()


@st.cache_data(ttl=3600, show_spinner=False)
def _run_analysis(
    baseline_year: int,
    current_year: int,
    current_month: int,
    pillar: str,
) -> EvolutionResult:
    """Voer de evolutie-analyse uit (gecached per unieke parametercombinatie)."""
    df = _load_df()
    baseline_periods = [f"{baseline_year}-{m:02d}" for m in range(1, 13)]
    current_periods = [f"{current_year}-{m:02d}" for m in range(1, current_month + 1)]
    analyser = EvolutionAnalyser(df, pillar)
    return analyser.analyse(baseline_periods, current_periods)


def _run_analysis_on_df(
    df: pd.DataFrame,
    baseline_year: int,
    current_year: int,
    current_month: int,
    pillar: str,
) -> EvolutionResult:
    """Voer analyse uit op een reeds gefilterd DataFrame (niet gecached — voor ziekenhuisfilter)."""
    baseline_periods = [f"{baseline_year}-{m:02d}" for m in range(1, 13)]
    current_periods = [f"{current_year}-{m:02d}" for m in range(1, current_month + 1)]
    analyser = EvolutionAnalyser(df, pillar)
    return analyser.analyse(baseline_periods, current_periods)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------


def _render_sidebar(
    t: dict, today: date, last_year: int, last_month: int, df: pd.DataFrame | None = None
) -> tuple[str, str | None, str, list[str]]:
    """
    Render de sidebar en geef (pillar_key, window_start, lang, selected_hospitals) terug.

    window_start is None voor Volledig venster, "2025-07-01" voor Tendensvenster.
    selected_hospitals is [] wanneer geen filter actief is (= alle ziekenhuizen tonen).
    last_year / last_month: laatste volledig afgeronde maand (nooit de lopende maand).
    """
    d = t["dashboard"]
    lang = st.session_state.get("lang", "nl")

    with st.sidebar:
        # --- Header: links uitgelijnd 🧭 + sectietitel naast elkaar ---
        st.markdown(
            f"<div style='display:flex;align-items:center;justify-content:flex-start;"
            f"gap:2px;padding:0.15rem 0 0.1rem 0;margin-left:-0.15rem'>"
            f"<span style='font-size:1.3rem;line-height:1'>🧭</span>"
            f"<span style='font-size:1.15rem;font-weight:700;color:{ZORGI_DARK_BLUE}'>"
            f"{d['title']}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.divider()

        # --- Pijler ---
        st.markdown(f"**{d['pillar_select']}**")
        st.markdown("<div style='height:2rem;min-height:2rem'></div>", unsafe_allow_html=True)
        sub_pillars = [k for k in PILLAR_REGISTRY if k != "zorgi"]
        pillar_options = ["zorgi", *sub_pillars]
        pillar_labels = {}
        _is_demo = not DASHBOARD_PROD_MODE
        for k in pillar_options:
            label_name = "ZORGI" if k == "zorgi" else PILLAR_REGISTRY[k]["name"]
            pillar_labels[k] = label_name if k in _ACTIVE_PILLARS else f"{label_name} 🚧"
        _demo_default = "pharma" if _is_demo else "zorgi"
        if "selected_pillar" not in st.session_state:
            st.session_state["selected_pillar"] = _demo_default
        _saved_pillar = st.session_state.get("selected_pillar", _demo_default)
        if _is_demo and _saved_pillar not in _ACTIVE_PILLARS:
            _saved_pillar = _demo_default
            st.session_state["selected_pillar"] = _demo_default
        _pillar_idx = pillar_options.index(_saved_pillar) if _saved_pillar in pillar_options else 0
        selected_pillar = st.radio(
            d["pillar_select"],
            options=pillar_options,
            format_func=lambda k: pillar_labels[k],
            index=_pillar_idx,
            label_visibility="collapsed",
        )
        st.session_state["selected_pillar"] = selected_pillar

        st.divider()

        # --- Modus ---
        # Dynamische datumrange-labels: "01/2025 ➡ MM/YYYY" (laatste volledige maand)
        _last_mm = f"{last_month:02d}"
        _last_yy = str(last_year)
        _trend_start_mm = _TREND_WINDOW_START[5:7]
        _trend_start_yyyy = _TREND_WINDOW_START[:4]
        _full_start_yyyy = str(_BASELINE_YEAR)
        mode_full = f"01/{_full_start_yyyy} ➡ {_last_mm}/{_last_yy}"
        mode_trend = f"{_trend_start_mm}/{_trend_start_yyyy} ➡ {_last_mm}/{_last_yy}"
        st.markdown(f"**{d['mode_select']}**")
        st.markdown("<div style='height:2rem;min-height:2rem'></div>", unsafe_allow_html=True)
        _saved_mode_key = st.session_state.get("selected_mode_key", "full")
        _mode_idx = 1 if _saved_mode_key == "trend" else 0
        selected_mode = st.radio(
            d["mode_select"],
            options=[mode_full, mode_trend],
            index=_mode_idx,
            label_visibility="collapsed",
        )
        st.session_state["selected_mode_key"] = "trend" if selected_mode == mode_trend else "full"
        window_start = _TREND_WINDOW_START if selected_mode == mode_trend else None

        st.divider()

        # --- Taal ---
        st.markdown(f"**{d['lang_select']}**")
        st.markdown("<div style='height:2rem;min-height:2rem'></div>", unsafe_allow_html=True)
        lang_options = ["nl", "fr"]
        new_lang = st.radio(
            d["lang_select"],
            options=lang_options,
            format_func=lambda la: "🇳🇱 Nederlands" if la == "nl" else "🇫🇷 Français",
            index=lang_options.index(lang),
            label_visibility="collapsed",
        )
        if new_lang != lang:
            # Vertaal actief tablabel naar nieuwe taal vóór rerun (taalwissel-bestendig)
            _tab_idx = st.session_state.get("_zorgi_tab_idx", 0)
            _new_d = load_translations(new_lang)["dashboard"]
            _new_labels = [
                _new_d["tab_summary"],
                _new_d["tab_timeline"],
                _new_d["tab_tickets"],
                _new_d["tab_response"],
                _new_d["tab_hospitals"],
                _new_d["tab_targets"],
                "DEV Tickets & Prioriteit",
            ]
            if 0 <= _tab_idx < len(_new_labels):
                st.session_state["zorgi_tabs"] = _new_labels[_tab_idx]
            st.session_state["lang"] = new_lang
            st.rerun()
        st.divider()

    return selected_pillar, window_start, lang, []


# ---------------------------------------------------------------------------
# Grafieken (elk max 10 branches — conform McCabe)
# ---------------------------------------------------------------------------


def _chart_timeline(data: DashboardData, t: dict, lang: str) -> go.Figure:
    """
    Combo-grafiek: maandelijkse score (lijn + gekleurde punten) + ticketvolume (bar).

    Visuele elementen (ontwerp "Best of Four" v4 — 15/04/2026):
    ① Kleurgecodeerde bars: ZORGI_LIGHT_BLUE (≥ KPI) / lichtroze (< KPI)
    ② Score-lijn gegarandeerd op voorgrond:
       - Bars op yaxis="y"  (go.Figure hoofdlaag = BOTTOM)
       - Score op yaxis="y2" (go.Figure overplot-laag = TOP — altijd boven hoofdlaag)
       - yaxis  (main,     rechts) = volumeas
       - yaxis2 (overplot, links)  = scoreas
    ③ KPI-drempellijn + gewogen jaar-gemiddelde vorig jaar (via add_shape yref="y2")
    ④ Ticketaantallen als tekstlabel binnenin elke bar (onderkant; auto-fallback = boven de bar)
    ⑤ Jaar-scheidingslijn bij multi-jaar data
    ⑥ Numerieke maandlabels "MM/JJ" (01/25), horizontaal
    ⑦ Score-as 1 decimaal; legenda bovenaan gecentreerd; margin compact

    In Tendensvenster-modus: extra rolvoortschrijdend 3-maands gemiddelde.
    """
    # Lokale kleurconstanten — score-gebaseerde kleurcodering
    green_dot = "#4caf50"  # dot: score ≥ AVG_SCORE_MIN
    pink_bar = "#f5c6c5"  # bar: score < AVG_SCORE_MIN (lichtroze)

    d = t["dashboard"]
    tl = data.timeline
    if not tl:
        return go.Figure()

    periods = [p.period for p in tl]
    scores = [p.avg_score for p in tl]
    volumes = [p.total_tickets for p in tl]

    # ⑥ Numerieke maandlabels: "01/25", "02/25", ..., "01/26"
    x_labels = [f"{parse_period(p)[1]:02d}/{str(parse_period(p)[0])[2:]}" for p in periods]

    # ① Kleurgecodeerde bars op basis van gemiddelde score
    bar_colors = [ZORGI_LIGHT_BLUE if s >= AVG_SCORE_MIN else pink_bar for s in scores]

    # ② Kleurgecodeerde dots op basis van score
    dot_colors = [green_dot if s >= AVG_SCORE_MIN else ZORGI_RED for s in scores]

    fig = go.Figure()

    # ① Volume-bars op yaxis="y" (go.Figure hoofdlaag = BOTTOM → achtergrond)
    # Ticketaantallen als tekstlabel binnenin de bar; auto-fallback = boven de bar
    fig.add_trace(
        go.Bar(
            x=x_labels,
            y=volumes,
            name=d["timeline_volume"],
            marker_color=bar_colors,
            marker_line_color=ZORGI_GREY_BLUE,
            marker_line_width=0.5,
            opacity=0.45,
            yaxis="y",
            text=[str(v) for v in volumes],
            textposition="auto",
            insidetextanchor="start",
            textfont={"size": 10, "color": "#1a1a1a"},
            textangle=0,
            constraintext="none",
        )
    )

    # ② Score-lijn op yaxis2 (overplot-laag → TOP, altijd boven de bars)
    fig.add_trace(
        go.Scatter(
            x=x_labels,
            y=scores,
            mode="lines+markers+text",
            name=d["timeline_score"],
            line={"color": ZORGI_DARK_BLUE, "width": 2.5},
            marker={
                "color": dot_colors,
                "size": 11,
                "line": {"color": "#ffffff", "width": 2},
            },
            text=[f"{s:.2f}".replace(".", ",") for s in scores],
            textposition="top center",
            textfont={"size": 8, "color": ZORGI_DARK_BLUE},
            yaxis="y2",
        )
    )

    # Tendensvenster: rolvoortschrijdend 3-maands gemiddelde (ook op overplot-as)
    if data.mode == "trend":
        rolling = pd.Series(scores).rolling(3, min_periods=1).mean().round(2).tolist()
        fig.add_trace(
            go.Scatter(
                x=x_labels,
                y=rolling,
                mode="lines",
                name=d["rolling_avg"],
                line={"color": ZORGI_PURPLE, "width": 2, "dash": "dot"},
                yaxis="y2",
            )
        )

    # ③ KPI-drempellijn — add_shape met yref="y2" (score-as)
    fig.add_shape(
        type="line",
        x0=0,
        x1=1,
        xref="paper",
        y0=AVG_SCORE_MIN,
        y1=AVG_SCORE_MIN,
        yref="y2",
        line={"dash": "dash", "color": ZORGI_RED, "width": 1.2},
        opacity=0.8,
    )
    fig.add_annotation(
        x=0.99,
        y=AVG_SCORE_MIN,
        xref="paper",
        yref="y2",
        text=f"KPI min. {AVG_SCORE_MIN:.1f}\u2605",
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        font={"size": 10, "color": ZORGI_RED},
    )

    # ③ Gewogen jaar-gemiddelde vorig jaar — ook yref="y2"
    vorig_jaar = data.current_year - 1
    bl_entries = [p for p in tl if parse_period(p.period)[0] == vorig_jaar and p.total_tickets > 0]
    if bl_entries:
        _total_v = sum(p.total_tickets for p in bl_entries)
        gem_vorig = round(sum(p.avg_score * p.total_tickets for p in bl_entries) / _total_v, 2)
        gem_str = str(gem_vorig).replace(".", ",")
        fig.add_shape(
            type="line",
            x0=0,
            x1=1,
            xref="paper",
            y0=gem_vorig,
            y1=gem_vorig,
            yref="y2",
            line={"dash": "dot", "color": ZORGI_GREY_BLUE, "width": 1.0},
            opacity=0.7,
        )
        fig.add_annotation(
            x=0.99,
            y=gem_vorig,
            xref="paper",
            yref="y2",
            text=f"Gem. {vorig_jaar}: {gem_str}\u2605",
            showarrow=False,
            xanchor="right",
            yanchor="top",
            font={"size": 10, "color": ZORGI_GREY_BLUE},
        )

    # ⑤ Jaar-scheidingslijn bij multi-jaar data
    years_in_data = sorted({parse_period(p)[0] for p in periods})
    if len(years_in_data) > 1:
        for yr in years_in_data[1:]:
            jan_lbl = f"01/{str(yr)[2:]}"
            if jan_lbl in x_labels:
                jan_idx = x_labels.index(jan_lbl)
                fig.add_shape(
                    type="line",
                    xref="x",
                    yref="paper",
                    x0=jan_idx - 0.5,
                    x1=jan_idx - 0.5,
                    y0=0,
                    y1=1,
                    line={"color": ZORGI_GREY_BLUE, "width": 1.0, "dash": "dot"},
                    opacity=0.5,
                )

    fig.update_layout(
        title="",
        barmode="overlay",
        xaxis={"tickangle": 0},
        yaxis={
            "title": d["timeline_volume"],
            "side": "right",
            "showgrid": False,
        },
        yaxis2={
            "title": d["timeline_score"],
            "overlaying": "y",
            "side": "left",
            "range": [0, 5.5],
            "tickformat": ".1f",
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
            "itemsizing": "constant",
            "traceorder": "normal",
        },
        margin={"t": 55, "b": 10, "r": 15},
        modebar_remove=["pan2d", "autoScale2d"],
    )
    return apply_plotly_theme(fig)


def _chart_period_comparison(data: DashboardData, t: dict, lang: str = "nl") -> go.Figure:  # noqa: C901
    """
    Verticale bar chart: gewogen gemiddelde score per periode-blok.

    Blokindeling (automatisch op basis van data.timeline):
    - H1 2025: jan-jun 2025  (alleen zichtbaar in Volledig venster)
    - H2 2025: jul-dec 2025  (beide vensters)
    - Q1 2026, Q2 2026, ... : kwartalen lopend jaar (beide vensters)

    Kleuren: H1=ZORGI_RED (crisisperiode), H2='#27ae60' (herstel),
             Q1 2026=ZORGI_PURPLE (groei), overige kwartalen=ZORGI_LIGHT_BLUE.
    Stijl conform _chart_timeline: geen Plotly-titel, KPI-drempellijn,
    legenda boven gecentreerd, apply_plotly_theme.
    """
    tl = data.timeline
    if not tl:
        return go.Figure()

    # Maandafkortingen (tweetalig)
    mr_nl: dict[str, tuple[str, str]] = {
        "H1": ("Jan", "Jun"),
        "H2": ("Jul", "Dec"),
        "Q1": ("Jan", "Mrt"),
        "Q2": ("Apr", "Jun"),
        "Q3": ("Jul", "Sep"),
        "Q4": ("Okt", "Dec"),
    }
    mr_fr: dict[str, tuple[str, str]] = {
        "H1": ("Jan", "Juin"),
        "H2": ("Juil", "D\u00e9c"),
        "Q1": ("Jan", "Mars"),
        "Q2": ("Avr", "Juin"),
        "Q3": ("Juil", "Sep"),
        "Q4": ("Oct", "D\u00e9c"),
    }
    month_range = mr_fr if lang == "fr" else mr_nl

    def _block_key(yr: int, mo: int) -> str:
        if yr == 2025:
            return "H1 2025" if mo <= 6 else "H2 2025"
        return f"Q{(mo - 1) // 3 + 1} {yr}"

    def _block_x_label(bk: str) -> str:
        code = bk.split(" ")[0]
        m_a, m_b = month_range.get(code, ("", ""))
        return f"{bk}<br>({m_a}\u2013{m_b})" if m_a else bk

    def _block_sort_key(bk: str) -> tuple[int, int]:
        code, yr_s = bk.split(" ")
        yr = int(yr_s)
        if code == "H1":
            return (yr, 1)
        if code == "H2":
            return (yr, 7)
        return (yr, (int(code[1]) - 1) * 3 + 1)

    # Gewogen gemiddelde per kwartaalblok
    block_data: dict[str, dict] = {}
    for p in tl:
        yr, mo = parse_period(p.period)
        bk = _block_key(yr, mo)
        if bk not in block_data:
            block_data[bk] = {"sum_s": 0.0, "sum_t": 0}
        block_data[bk]["sum_s"] += p.avg_score * p.total_tickets
        block_data[bk]["sum_t"] += p.total_tickets

    if not block_data:
        return go.Figure()

    sorted_blocks = sorted(block_data, key=_block_sort_key)
    bar_x = [_block_x_label(bk) for bk in sorted_blocks]
    bar_y = [
        round(block_data[bk]["sum_s"] / block_data[bk]["sum_t"], 2)
        if block_data[bk]["sum_t"] > 0
        else 0.0
        for bk in sorted_blocks
    ]
    bar_vols = [block_data[bk]["sum_t"] for bk in sorted_blocks]

    block_color: dict[str, str] = {
        "H1 2025": "#f4a7a3",  # lichtroze  — crisisperiode (baseline)
        "H2 2025": "#9aa5b4",  # lichtgrijs — herstelperiode
        "Q1 2026": ZORGI_DARK_BLUE,  # donkerblauw — groeiperiode (lopend jaar)
    }
    bar_colors = [block_color.get(bk, ZORGI_DARK_BLUE) for bk in sorted_blocks]
    bar_text = [
        f"{s:.2f}\u2605".replace(".", ",") + f"<br>({v} tickets)"
        for s, v in zip(bar_y, bar_vols, strict=False)
    ]

    fig = go.Figure(
        go.Bar(
            x=bar_x,
            y=bar_y,
            marker_color=bar_colors,
            marker_line_width=0,
            opacity=0.78,
            text=bar_text,
            textposition="outside",
            hovertemplate="%{x}: %{y:.2f}\u2605<extra></extra>",
            showlegend=False,
        )
    )

    # KPI-drempellijn
    fig.add_shape(
        type="line",
        x0=0,
        x1=1,
        xref="paper",
        y0=AVG_SCORE_MIN,
        y1=AVG_SCORE_MIN,
        yref="y",
        line={"dash": "dash", "color": ZORGI_RED, "width": 1.2},
        opacity=0.8,
    )
    fig.add_annotation(
        x=0.99,
        y=AVG_SCORE_MIN,
        xref="paper",
        yref="y",
        text=f"KPI min. {AVG_SCORE_MIN:.1f}\u2605",
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        font={"size": 10, "color": ZORGI_RED},
    )

    fig.update_layout(
        title="",
        xaxis={"showgrid": False, "tickangle": 0},
        yaxis={
            "range": [0, 5.5],
            "ticksuffix": "\u2605",
            "tickformat": ".1f",
            "gridcolor": "#edf2f7",
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
            "itemsizing": "constant",
            "traceorder": "normal",
        },
        margin={"t": 45, "b": 10, "r": 15},
    )

    return apply_plotly_theme(fig)


def _chart_rolling_avg(data: DashboardData, t: dict, lang: str = "nl") -> go.Figure:
    """
    Lijn-grafiek: maandelijkse score (gestippeld) + rolvoortschrijdend 3-maands
    gemiddelde (vol, met fill).

    Gebruikt data.timeline (reeds gefilterd op actief venster):
    - Volledig venster: jan 2025 t/m heden
    - Tendensvenster:  jul 2025 t/m heden

    Rolling avg: mean(scores[max(0, i-2):i+1]), min_periods=1.
    Stijl conform _chart_timeline: KPI-drempellijn, legenda boven gecentreerd,
    apply_plotly_theme — ZONDER ingebouwde Plotly-titel.
    """
    d = t["dashboard"]
    tl = data.timeline
    if len(tl) < 2:
        return go.Figure()

    x_labels = [
        f"{parse_period(p.period)[1]:02d}/{str(parse_period(p.period)[0])[-2:]}" for p in tl
    ]
    scores = [p.avg_score for p in tl]
    rolling = pd.Series(scores).rolling(3, min_periods=1).mean().round(2).tolist()

    fig = go.Figure()

    # Dataset 1 — Maandscore (gestippeld, lichtblauw, opacity=0.6)
    fig.add_trace(
        go.Scatter(
            x=x_labels,
            y=scores,
            mode="lines+markers",
            name=d.get("monthly_score", "Maandscore"),
            line={"color": ZORGI_LIGHT_BLUE, "width": 1.5, "dash": "dot"},
            marker={"size": 5, "color": ZORGI_LIGHT_BLUE},
            opacity=0.6,
        )
    )

    # Dataset 2 — 3-maands gemiddelde (vol, donkerblauw, fill naar 0)
    fig.add_trace(
        go.Scatter(
            x=x_labels,
            y=rolling,
            mode="lines+markers+text",
            name=d.get("rolling_avg", "3-maands gemiddelde"),
            line={"color": ZORGI_DARK_BLUE, "width": 2.5},
            marker={"size": 6, "color": ZORGI_DARK_BLUE},
            fill="tozeroy",
            fillcolor="rgba(0,58,112,0.06)",
            text=[f"{v:.2f}".replace(".", ",") for v in rolling],
            textposition="top center",
            textfont={"size": 8, "color": ZORGI_DARK_BLUE},
        )
    )

    # KPI-drempellijn
    fig.add_shape(
        type="line",
        x0=0,
        x1=1,
        xref="paper",
        y0=AVG_SCORE_MIN,
        y1=AVG_SCORE_MIN,
        yref="y",
        line={"dash": "dash", "color": ZORGI_RED, "width": 1.2},
        opacity=0.8,
    )
    fig.add_annotation(
        x=0.99,
        y=AVG_SCORE_MIN,
        xref="paper",
        yref="y",
        text=f"KPI min. {AVG_SCORE_MIN:.1f}\u2605",
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        font={"size": 10, "color": ZORGI_RED},
    )

    # Dynamische y-as range
    _all_vals = [v for v in scores + rolling if v > 0]
    _y_min = max(0.0, min(_all_vals) - 0.3) if _all_vals else 0.0
    _y_max = min(5.5, max(_all_vals) + 0.3) if _all_vals else 5.5

    fig.update_layout(
        title="",
        xaxis={"tickangle": 0, "showgrid": False},
        yaxis={
            "range": [_y_min, _y_max],
            "ticksuffix": "\u2605",
            "tickformat": ".1f",
            "gridcolor": "#edf2f7",
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
            "itemsizing": "constant",
            "traceorder": "normal",
        },
        margin={"t": 45, "b": 10, "r": 15},
    )

    return apply_plotly_theme(fig)


def _chart_grouped_bar(
    items: list,
    x_key: str,
    title: str,
    baseline_label: str,
    current_label: str,
) -> go.Figure:
    """Generieke grouped bar chart voor issue type en prioriteit vergelijking."""
    if not items:
        return go.Figure()
    labels = [getattr(i, x_key) for i in items]
    fig = go.Figure()
    # Baseline-trace (balk)
    fig.add_trace(
        go.Bar(
            name=baseline_label,
            x=labels,
            y=[i.baseline_score for i in items],
            marker_color=ZORGI_GREY_BLUE,
        )
    )
    # Huidig-trace (balk)
    fig.add_trace(
        go.Bar(
            name=current_label,
            x=labels,
            y=[i.current_score for i in items],
            marker_color=ZORGI_LIGHT_BLUE,
        )
    )
    fig.update_layout(
        title=title,
        barmode="group",
        yaxis={"title": "", "range": [0, 5.5]},
        xaxis={"title": ""},
    )
    fig.add_hline(y=4.0, line_dash="dash", line_color=ZORGI_GREY_BLUE)
    return apply_plotly_theme(fig)


def _chart_response_time(data: DashboardData, t: dict, lang: str = "nl") -> go.Figure:
    """Lijn-grafiek: gemiddelde responstijd per score-niveau (baseline gestippeld vs huidig).

    Titel wordt buiten de grafiek als st.markdown h4 geplaatst (conform _tab_timeline stijl).
    As-labels zijn i18n'd via response_yaxis_title / response_xaxis_title.

    Datareeksen:
    - '2025 (baseline)' = gemiddelde responstijd per score-niveau over het volledige
      jaar 2025 (jan-dec), uitsluitend tickets met een satisfaction_date.
    - 'Cumulatief'      = gemiddelde responstijd per score-niveau over de volledige
      analyseperiode (jan 2025 - heden, cumulatief), uitsluitend tickets met een
      satisfaction_date. Dit is de lopende periode in data.response_time_by_score.
    """
    d = t["dashboard"]
    rt = data.response_time_by_score
    if not rt:
        return go.Figure()

    levels = sorted(rt.keys())
    x = [f"{lv}\u2605" for lv in levels]
    baseline_days = [rt[lv].baseline_days for lv in levels]
    current_days = [rt[lv].current_days for lv in levels]
    baseline_counts = [rt[lv].baseline_count for lv in levels]
    current_counts = [rt[lv].current_count for lv in levels]

    # Labelformaat: "7,2d (34 t)"  — lege string bij None
    def _lbl(v: float | None, n: int) -> str:
        if v is None:
            return ""
        days_str = f"{v:.1f}d".replace(".", ",")
        return f"{days_str} ({n} t)" if n > 0 else days_str

    baseline_labels = [_lbl(v, n) for v, n in zip(baseline_days, baseline_counts, strict=False)]
    current_labels = [_lbl(v, n) for v, n in zip(current_days, current_counts, strict=False)]

    _lbl_grey = ZORGI_GREY_BLUE
    _lbl_blue = ZORGI_DARK_BLUE
    _tf = {"size": 10, "family": "Poppins, Verdana, sans-serif"}

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=baseline_days,
            mode="lines+markers+text",
            name=d["response_2025_legend"],
            line={"color": ZORGI_GREY_BLUE, "dash": "dot"},
            marker={"size": 7},
            text=baseline_labels,
            textposition="top center",
            textfont={**_tf, "color": _lbl_grey},
            connectgaps=True,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=current_days,
            mode="lines+markers+text",
            name=d["response_current_legend"],
            line={"color": ZORGI_DARK_BLUE},
            marker={"size": 7},
            text=current_labels,
            textposition="middle right",
            textfont={**_tf, "color": _lbl_blue},
            connectgaps=True,
        )
    )
    fig.update_layout(
        title="",
        yaxis_title=d.get("response_yaxis_title", "Dagen"),
        xaxis_title=d.get("response_xaxis_title", "Score-niveau"),
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
            "itemsizing": "constant",
            "traceorder": "normal",
        },
        margin={"t": 55, "b": 30, "r": 90},
    )
    return apply_plotly_theme(fig)


def _chart_hospitals(data: DashboardData, t: dict) -> go.Figure:
    """Horizontale bar chart: score per ziekenhuis (bottom10 + attention + top10), kleur op score."""
    d = t["dashboard"]

    # Combineer alle drie lijsten, dedupliceer op ziekenhuisnaam
    all_zh: dict[str, float] = {}
    for h in data.hospital_bottom10 or []:
        all_zh[h.hospital] = h.score
    for h in data.hospital_attention or []:
        all_zh[h.hospital] = h.score
    for h in data.hospital_top10 or []:
        all_zh[h.hospital] = h.score

    if not all_zh:
        return go.Figure()

    # Sorteer op score laag → hoog
    sorted_zh = sorted(all_zh.items(), key=lambda x: x[1])
    hospitals = [x[0] for x in sorted_zh]
    scores = [x[1] for x in sorted_zh]

    # Kleur op drempelwaarden
    def _zh_color(s: float) -> str:
        if s >= 4.0:
            return ZORGI_FUNC_POSITIVE
        if s >= 3.0:
            return "#d97706"  # amber — aandacht
        return ZORGI_RED

    colors = [_zh_color(s) for s in scores]

    fig = go.Figure(
        go.Bar(
            y=hospitals,
            x=scores,
            orientation="h",
            marker_color=colors,
            text=[f"{s:.2f}★" for s in scores],
            textposition="outside",
            hovertemplate="%{y}: %{x:.2f}★<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_layout(
        title={"text": ""},  # Leeg — titel staat als st.markdown boven de grafiek
        xaxis={"title": d["timeline_score"]},  # autorange — geen vaste schaal
        yaxis={"autorange": "reversed"},  # lage score bovenaan, hoge score onderaan
        height=max(300, len(hospitals) * 30 + 80),
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        modebar_remove=[
            "pan2d",
            "autoScale2d",
        ],  # resetScale2d (huis-icoon) behouden voor zoom-reset
    )
    fig.add_vline(x=4.0, line_dash="dash", line_color=ZORGI_GREY_BLUE)
    fig.add_vline(
        x=2.5,
        line_dash="dash",
        line_color=ZORGI_RED,
    )
    return apply_plotly_theme(fig)


def _chart_kpi_targets(data: DashboardData, t: dict, lang: str) -> go.Figure:
    """Verticale grouped bar chart (Tab 6 — KPI Targets): baseline / target / realisatie per KPI."""
    d = t["dashboard"]
    kpi_names_i18n = t.get("evolution", {}).get("target_tracking", {}).get("kpi_names", {})
    targets = {kp.name: kp for kp in data.kpi_targets}

    ordered = [k for k in _KPI_TARGET_ORDER if k in targets]
    if not ordered:
        return go.Figure()

    labels = [kpi_names_i18n.get(k, k) for k in ordered]
    baselines = [targets[k].baseline for k in ordered]
    target_vals = [targets[k].target for k in ordered]
    current_vals = [targets[k].current for k in ordered]

    fig = go.Figure()
    # Baseline-trace
    fig.add_trace(
        go.Bar(
            name=d["col_baseline"],
            x=labels,
            y=baselines,
            marker_color=ZORGI_GREY_BLUE,
        )
    )
    # Target-trace (outline balk)
    fig.add_trace(
        go.Bar(
            name=d["col_target"],
            x=labels,
            y=target_vals,
            marker_color=ZORGI_ULTRA_LIGHT,
            marker_line_color=ZORGI_DARK_BLUE,
            marker_line_width=2,
        )
    )
    # Realisatie-trace
    fig.add_trace(
        go.Bar(
            name=d["col_realization"],
            x=labels,
            y=current_vals,
            marker_color=ZORGI_LIGHT_BLUE,
        )
    )
    fig.update_layout(
        title=d.get("kpi_chart_title", ""),
        barmode="group",
        xaxis={"title": ""},
        yaxis={"title": "", "range": [0, 5.5]},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
    )
    return apply_plotly_theme(fig)


def _chart_kpi_targets_h(data: DashboardData, t: dict) -> go.Figure:
    """Horizontale bar chart: drie balken per KPI aansluitend (baseline | target | realisatie).

    Balkbreedtes (y-as eenheden, categorie = 1.0):
      Baseline = 0.24  |  Target = 0.14 (smaller)  |  Realisatie = 0.24
    Totale groepsbreedte = 0.62 — past binnen bargap-beschikbare ruimte (~0.72).
    Implementatie via barmode='overlay' + expliciete offset per trace:
      alle drie balken zijn naadloos aansluitend, geen overlap.
    Realisatie semantisch gekleurd: groen = target gehaald, rood = niet gehaald.
    """
    d = t["dashboard"]
    kpi_names_i18n = t.get("evolution", {}).get("target_tracking", {}).get("kpi_names", {})
    targets = {kp.name: kp for kp in data.kpi_targets}

    ordered = [k for k in _KPI_TARGET_ORDER if k in targets]
    if not ordered:
        return go.Figure()

    labels = [kpi_names_i18n.get(k, k) for k in ordered]
    baselines = [targets[k].baseline for k in ordered]
    target_vals = [targets[k].target for k in ordered]
    current_vals = [targets[k].current for k in ordered]

    # Semantische kleur per KPI: groen = target gehaald, rood = niet gehaald
    real_colors = []
    for k in ordered:
        kp = targets[k]
        higher_is_better = _KPI_HIGHER_IS_BETTER.get(k, True)
        if higher_is_better:
            real_colors.append(ZORGI_FUNC_POSITIVE if kp.current >= kp.target else ZORGI_RED)
        else:
            real_colors.append(ZORGI_FUNC_POSITIVE if kp.current <= kp.target else ZORGI_RED)

    def _fmt(vals: list) -> list[str]:
        return [f"{v:.2f}".replace(".", ",") for v in vals]

    # ── Balkbreedtes en offsets (y-as eenheden) ────────────────────────────
    # Volgorde (boven → onder): Baseline | Target | Realisatie
    # Offset = linker rand van de balk relatief aan het categorie-middelpunt (y=int).
    # Met autorange='reversed' verschijnt de laagste y-offset bovenaan.
    # Breder dan v0.5.0 (0.24/0.14/0.24) — hoogte mee omhoog zodat tussenruimte bewaard blijft.
    _bl_w: float = 0.28  # baseline breedte
    _tg_w: float = 0.16  # target breedte — iets smaller
    _re_w: float = 0.28  # realisatie breedte
    _total: float = _bl_w + _tg_w + _re_w  # = 0.72
    _bl_off: float = -(_total / 2)  # = -0.36 (linker rand baseline)
    _tg_off: float = _bl_off + _bl_w  # = -0.08 (linker rand target)
    _re_off: float = _tg_off + _tg_w  # = +0.08 (linker rand realisatie)

    fig = go.Figure()

    # ── Baseline (boven in groep) ─────────────────────────────────────────
    fig.add_trace(
        go.Bar(
            name=d["col_baseline"],
            y=labels,
            x=baselines,
            orientation="h",
            marker_color=ZORGI_GREY_BLUE,
            text=_fmt(baselines),
            textposition="outside",
            textfont={"size": 11},
            width=_bl_w,
            offset=_bl_off,
        )
    )

    # ── Target (midden in groep, amber, iets smaller) ─────────────────────
    fig.add_trace(
        go.Bar(
            name=d["col_target"],
            y=labels,
            x=target_vals,
            orientation="h",
            marker_color="#f0a500",
            text=_fmt(target_vals),
            textposition="outside",
            textfont={"size": 11, "color": "#f0a500"},
            width=_tg_w,
            offset=_tg_off,
        )
    )

    # ── Realisatie (onder in groep, semantisch gekleurd) ──────────────────
    fig.add_trace(
        go.Bar(
            name=d["col_realization"],
            y=labels,
            x=current_vals,
            orientation="h",
            marker_color=real_colors,
            text=_fmt(current_vals),
            textposition="outside",
            textfont={"size": 11},
            showlegend=False,
            width=_re_w,
            offset=_re_off,
        )
    )

    # ── Legenda-dummy Realisatie: kleurloos open blokje + gecombineerd label ─
    # square-open = enkel omlijning, geen vulling → visueel "kleurloos/neutraal"
    _real_label = d.get("legend_realization_combined", f"{d['col_realization']} (groen/rood)")
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={
                "symbol": "square-open",
                "size": 12,
                "line": {"color": ZORGI_GREY_BLUE, "width": 2},
            },
            name=_real_label,
            showlegend=True,
        )
    )

    fig.update_layout(
        title="",
        barmode="overlay",  # bars handmatig gepositioneerd via offset
        xaxis={"title": "", "gridcolor": "#edf2f7"},
        yaxis={"title": "", "autorange": "reversed"},
        # Hoogte 560px: balken breder (0.72 vs 0.62) + proportioneel groter zodat
        # de tussenruimte tussen KPI-groepen vergelijkbaar blijft (~20-22px).
        height=560,
        legend={
            # Boven gecentreerd — modebar zit rechts, geen overlap met gecentreerde legenda
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
            "itemsizing": "constant",
            "traceorder": "normal",
            "indentation": 10,
        },
        margin={"t": 50, "b": 10, "r": 5},  # t=50: ruimte voor modebar + legenda boven
        modebar_remove=["pan2d", "autoScale2d"],  # analoog aan _chart_hospitals()
    )
    return apply_plotly_theme(fig)


# ---------------------------------------------------------------------------
# Tab-renders
# ---------------------------------------------------------------------------


def _build_kpi_suffixes(
    data: DashboardData,
    avg_abbrev: str,
    hc_baseline: float,
) -> tuple[str, str, str, str]:
    """Bereken contextsuffixen per KPI (avg / pos / neg / hc) als baseline-referentie.

    Returns:
        Tuple (avg_sfx, pos_sfx, neg_sfx, hc_sfx) — lege strings als geen raw-data.
    """
    if data.mode == "trend" and data.raw and data.raw.benchmark_h2:
        bh2 = data.raw.benchmark_h2
        return (
            f"  ({avg_abbrev} {str(round(bh2.avg_score, 2)).replace('.', ',')}★)",
            f"  ({avg_abbrev} {bh2.pct_positive:.1f}%)",
            f"  ({avg_abbrev} {bh2.pct_negative:.1f}%)",
            f"  ({avg_abbrev} {bh2.hc_ratio:.1f}%)",
        )
    if data.raw:
        return (
            f"  ({avg_abbrev} {str(round(data.raw.baseline_avg_score, 2)).replace('.', ',')}★)",
            f"  ({avg_abbrev} {data.raw.baseline_pct_positive:.1f}%)",
            f"  ({avg_abbrev} {data.raw.baseline_pct_negative:.1f}%)",
            f"  ({avg_abbrev} {hc_baseline:.1f}%)",
        )
    return "", "", "", ""


def _zh_signal_card(zh: ZhSignalEntry) -> str:
    """Genereert HTML voor één ZH-signaalkaartje met score-progress bar.

    Kleurcodering op basis van drempelwaarden:
      >= 4,0 -> groen  |  3,0 - 4,0 -> amber  |  < 3,0 -> rood
    Progress bar toont drempelmarkeringen op 60% (3,0★) en 80% (4,0★).
    REVERT: verwijder deze functie + .zh-signal-card CSS-blok in branding.py,
            en herstel de originele 2-kolomcode in _tab_summary().
    """
    if zh.score >= 4.0:
        border_color = "#00aa44"
        bar_color = "#00aa44"
    elif zh.score >= 3.0:
        border_color = "#f0a500"
        bar_color = "#f0a500"
    else:
        border_color = ZORGI_RED
        bar_color = ZORGI_RED
    bar_width = min(zh.score / 5.0 * 100, 100)
    hospital_safe = html.escape(zh.hospital)
    ticket_label = (
        "ticket" if zh.tickets == 1 else "tickets"
    )  # 0 → tickets, 1 → ticket, >1 → tickets
    return (
        f'<div class="zh-signal-card" style="border-left-color:{border_color}">'
        f'<div style="font-weight:700;font-size:0.9rem;color:{ZORGI_DARK_BLUE}">'
        f"{hospital_safe}"
        f"</div>"
        f'<div style="font-size:0.82rem;color:{ZORGI_GREY_BLUE};margin-top:2px">'
        f"{zh.score:.2f}★".replace(".", ",")
        + f" &nbsp;·&nbsp; {zh.tickets} {ticket_label}"
        f"</div>"
        f'<div class="zh-score-bar-wrap">'
        f'<div class="zh-score-bar" style="width:{bar_width:.1f}%;background:{bar_color}"></div>'
        f'<div class="zh-threshold-marker" style="left:60%"></div>'
        f'<div class="zh-threshold-marker" style="left:80%"></div>'
        f"</div>"
        f"</div>"
    )


def _render_zh_signal_section(data: DashboardData, d: dict) -> None:
    """Render de ZH mini-signaalkaart: 3 kolommen (best | kritiek | aandacht) + nav-knop.

    Nav-knop via st.components.v1.html() (height=45, scrolling=False):
    - st.markdown onclick wordt door DOMpurify gesaniteerd → werkt niet
    - components.html() bypast sanitatie en kan window.parent.document bereiken
    - Kleine niet-persistente iframe (45px) → geen browser-freeze (verschil met sidebar-toggle)
    REVERT: verwijder deze functie en vervang de aanroep in _tab_summary() door
    de originele 2-kolomcode met plain markdown en emoji-bullets.
    """
    st.markdown(f"#### {d['signal_section_title']} {data.current_year}")
    col_worst, col_attn, col_best = st.columns(3)
    with col_worst:
        st.markdown(f"**{d['top3_worst']}**")
        if data.zh_bottom3:
            for zh in data.zh_bottom3:
                st.markdown(_zh_signal_card(zh), unsafe_allow_html=True)
        else:
            st.caption(d["kpi_no_critical_accounts"])
    with col_attn:
        st.markdown(f"**{d['kpi_attention_accounts_title']}**")
        if data.zh_attention_list:
            for zh in data.zh_attention_list[:3]:
                st.markdown(_zh_signal_card(zh), unsafe_allow_html=True)
        else:
            st.caption(d["kpi_no_attention_accounts"])
    with col_best:
        st.markdown(f"**{d['top3_best']}**")
        for zh in data.zh_top3:
            st.markdown(_zh_signal_card(zh), unsafe_allow_html=True)


def render_kerncijfers_vergelijking(  # noqa: C901
    df_vorig: pd.DataFrame,
    df_huidig: pd.DataFrame,
    venster_modus: str,
    lang: str,
) -> None:
    """
    Tegel 3 — Samenvatting: Kerncijfers vergelijking (7 rijen, venster-aware kolomlabels).

    Versie x.y · 12/04/2026 — herstructurering conform spec Prompt A:
      uitbreiding 5→7 rijen, venster-aware kolomlabels, Δ-formatting + trend-pijl-semantiek.

    Gedocumenteerde herstructurering (vóór → na):
      VÓÓR: data.comparison_rows (5 ComparisonRow-objecten, pre-berekend door
            DashboardExporter._build_comparison_rows). Vaste 4 kolommen (KPI / Baseline /
            Huidig / Δ), geen mediaan, geen % neutraal, geen venster-bewuste labels,
            geen trend-pijlen. Rendering via st.dataframe().
      NA:   Twee gefilterde DataFrames per venster (df_vorig, df_huidig), 7 rijen live
            berekend, alle labels via i18n, ZORGI HTML-tabelstijl, Δ-kleuren + trend-pijlen.

    Args:
        df_vorig:      Gefilterd DataFrame voor de "vorige" periode.
                       "volledig" → volledig baseline-jaar (bv. 2025).
                       "tendens"  → S2 van het baseline-jaar (jul-dec 2025).
        df_huidig:     Gefilterd DataFrame voor de "huidige" periode (YTD lopend jaar).
        venster_modus: "volledig" → kolomlabels Baseline/Huidig.
                       "tendens"  → kolomlabels Vorige periode/Huidige periode.
        lang:          "nl" of "fr".
    """
    t = load_translations(lang)
    sk = t.get("samenvatting", {}).get("kerncijfers", {})
    gt = t.get("gemeenschappelijk", {}).get("trend", {})

    # --- Kolomlabels (venster-aware, volledig i18n) ---
    col_kpi = sk.get("kolom_kpi", "KPI")
    col_delta = sk.get("kolom_delta", "Δ")
    col_trend = sk.get("kolom_trend", "Trend")
    if venster_modus == "tendens":
        col_vorig = sk.get("kolom_vorig_tendens", "Vorige periode")
        col_huidig = sk.get("kolom_huidig_tendens", "Huidige periode")
    else:  # volledig (fallback)
        col_vorig = sk.get("kolom_vorig_volledig", "Baseline")
        col_huidig = sk.get("kolom_huidig_volledig", "Huidig")

    # --- Trend-symbolen (i18n — toekomstige localisatie mogelijk) ---
    pijl_op = gt.get("pijl_omhoog", "▲")
    pijl_neer = gt.get("pijl_omlaag", "▼")
    pijl_st = gt.get("pijl_stabiel", "►")
    lbl_pos = gt.get("label_positieve_evolutie", "Positieve evolutie")
    lbl_neg = gt.get("label_negatieve_evolutie", "Negatieve evolutie")
    lbl_stabiel = gt.get("label_stabiel", "Stabiel")

    # --- Drempels voor "stabiel" (trend-pijl ►) ---
    _t_score = 0.05  # absolute Δ voor score-rijen
    _t_pct = 2.0  # ppt voor percentagerijen
    _t_n = 2  # absolute Δ voor telrijen

    # --- Belgisch decimaalformaat (komma) — zowel NL als FR ---
    def _fmt_score(v: float) -> str:
        return f"{v:.2f}★".replace(".", ",")

    def _fmt_pct(v: float) -> str:
        return f"{v:.1f}%".replace(".", ",")

    def _delta_score(h: float, v: float) -> str:
        d = h - v
        return f"{'+' if d >= 0 else ''}{d:.2f}★".replace(".", ",")

    def _delta_ppt(h: float, v: float) -> str:
        d = h - v
        return f"{'+' if d >= 0 else ''}{d:.1f} ppt".replace(".", ",")

    def _delta_n(h: int, v: int) -> str:
        d = h - v
        return f"{'+' if d >= 0 else ''}{d}"

    # --- Trend-pijl: (symbool, kleur, tooltip) ---
    def _trend(
        delta: float,
        drempel: float,
        hoger_is_beter: bool,
        neutraal: bool = False,
    ) -> tuple[str, str, str]:
        """► grijs bij stabiel of neutraal; ▲/▼ groen/rood op basis van richting."""
        if neutraal or abs(delta) < drempel:
            return pijl_st, ZORGI_GREY_BLUE, lbl_stabiel
        verbetering = (delta > 0) == hoger_is_beter
        return (
            (pijl_op, ZORGI_FUNC_POSITIVE, lbl_pos)
            if verbetering
            else (pijl_neer, ZORGI_RED, lbl_neg)
        )

    # --- Δ-celkleur (groen/rood/grijs) ---
    def _dclr(delta: float, hoger_is_beter: bool) -> str:
        if abs(delta) < 1e-9:
            return ZORGI_GREY_BLUE
        return ZORGI_FUNC_POSITIVE if (delta > 0) == hoger_is_beter else ZORGI_RED

    # --- Gescoorde rijen (score niet NaN) — conform bestaande analyser-logica ---
    sc_v = df_vorig[df_vorig["score"].notna()] if not df_vorig.empty else df_vorig
    sc_h = df_huidig[df_huidig["score"].notna()] if not df_huidig.empty else df_huidig

    # --- Rijbouw-helper ---
    def _row(
        label: str,
        val_v: str,
        val_h: str,
        delta_str: str,
        delta_val: float,
        drempel: float,
        hoger_is_beter: bool,
        neutraal: bool = False,
    ) -> dict:
        clr_d = ZORGI_GREY_BLUE if neutraal else _dclr(delta_val, hoger_is_beter)
        arr, clr_a, tip = _trend(delta_val, drempel, hoger_is_beter, neutraal)
        return {
            "label": label,
            "vorig": val_v,
            "huidig": val_h,
            "delta": delta_str,
            "delta_color": clr_d,
            "arrow": arr,
            "arrow_color": clr_a,
            "tooltip": tip,
        }

    rows: list[dict] = []

    # --- Periode-normalisatie voor telrijen (R1 en R7) ---
    # R1 (Responses): jaargemiddelde x n_maanden_huidig — consistent met T6-tegel.
    #   T6: kpi_responses_baseline_monthly_avg = baseline_total / 12 → 240/12 = 20/mnd
    #   Tegel 3 baseline = round(20/mnd x 3) = 60  (niet 78 = werkelijk jan-mrt 2025)
    # R7 (Hospitals): dezelfde kalendermaanden van vorig jaar — semantisch correcte vergelijking.
    # R2-R6 (scores/percentages): volledig df_vorig — onafhankelijk van periodelengte.
    _has_month = "_month" in df_huidig.columns and "_month" in df_vorig.columns
    if _has_month and not df_huidig.empty:
        _huidig_months: set[int] = set(int(m) for m in df_huidig["_month"].dropna().unique())
        _n_months_h = len(_huidig_months)
        _n_months_v = (
            len(set(int(m) for m in df_vorig["_month"].dropna().unique()))
            if not df_vorig.empty
            else (6 if venster_modus == "tendens" else 12)
        )
        # R7: zelfde kalendermaanden van baseline-jaar
        if venster_modus == "volledig":
            df_vorig_zh = df_vorig[df_vorig["_month"].isin(_huidig_months)]
        else:
            _s2_first_n = set([7, 8, 9, 10, 11, 12][:_n_months_h])
            df_vorig_zh = df_vorig[df_vorig["_month"].isin(_s2_first_n)]
    else:
        _n_months_h = 1
        _n_months_v = 6 if venster_modus == "tendens" else 12
        df_vorig_zh = df_vorig

    # R1: Totaal responses — baseline = jaargemiddelde x n_maanden_huidig (match T6: 20/mnd x 3 = 60)
    _n_v_full = len(df_vorig)
    n_v_resp = round(_n_v_full / _n_months_v * _n_months_h) if _n_months_v > 0 else _n_v_full
    n_h = len(df_huidig)
    rows.append(
        _row(
            sk.get("rij_totaal_responses", "Totaal responses"),
            str(n_v_resp),
            str(n_h),
            _delta_n(n_h, n_v_resp),
            float(n_h - n_v_resp),
            _t_n,
            True,
        )
    )

    # R2: Gem. score (hoger=beter)
    avg_v = float(sc_v["score"].mean()) if not sc_v.empty else 0.0
    avg_h = float(sc_h["score"].mean()) if not sc_h.empty else 0.0
    rows.append(
        _row(
            sk.get("rij_gem_score", "Gem. score"),
            _fmt_score(avg_v),
            _fmt_score(avg_h),
            _delta_score(avg_h, avg_v),
            avg_h - avg_v,
            _t_score,
            True,
        )
    )

    # R3: Mediaan score (hoger=beter)
    med_v = float(sc_v["score"].median()) if not sc_v.empty else 0.0
    med_h = float(sc_h["score"].median()) if not sc_h.empty else 0.0
    rows.append(
        _row(
            sk.get("rij_mediaan_score", "Mediaan score"),
            _fmt_score(med_v),
            _fmt_score(med_h),
            _delta_score(med_h, med_v),
            med_h - med_v,
            _t_score,
            True,
        )
    )

    # R4: % Positief (≥4★) — drempel staat in het i18n-label; waardecellen tonen enkel het %
    pos_v = float((sc_v["score"] >= 4).mean() * 100) if not sc_v.empty else 0.0
    pos_h = float((sc_h["score"] >= 4).mean() * 100) if not sc_h.empty else 0.0
    rows.append(
        _row(
            sk.get("rij_positief", "% Positief (≥ 4,0★)"),
            _fmt_pct(pos_v),
            _fmt_pct(pos_h),
            _delta_ppt(pos_h, pos_v),
            pos_h - pos_v,
            _t_pct,
            True,
        )
    )

    # R5: % Neutraal (3★) — altijd ► grijs; waardecellen tonen enkel het %
    neu_v = float((sc_v["score"] == 3).mean() * 100) if not sc_v.empty else 0.0
    neu_h = float((sc_h["score"] == 3).mean() * 100) if not sc_h.empty else 0.0
    rows.append(
        _row(
            sk.get("rij_neutraal", "% Neutraal (3,0\u2605 - 4,0\u2605)"),
            _fmt_pct(neu_v),
            _fmt_pct(neu_h),
            _delta_ppt(neu_h, neu_v),
            neu_h - neu_v,
            _t_pct,
            True,
            neutraal=True,
        )
    )

    # R6: % Negatief (≤2★) — lager=beter, geïnverteerd; waardecellen tonen enkel het %
    neg_v = float((sc_v["score"] <= 2).mean() * 100) if not sc_v.empty else 0.0
    neg_h = float((sc_h["score"] <= 2).mean() * 100) if not sc_h.empty else 0.0
    rows.append(
        _row(
            sk.get("rij_negatief", "% Negatief (< 3,0★)"),
            _fmt_pct(neg_v),
            _fmt_pct(neg_h),
            _delta_ppt(neg_h, neg_v),
            neg_h - neg_v,
            _t_pct,
            False,
        )
    )

    # R7: Actieve ziekenhuizen — zelfde kalendermaanden van vorig jaar (semantisch correcte vergelijking)
    zh_v = int(df_vorig_zh["hospital"].dropna().nunique()) if not df_vorig_zh.empty else 0
    zh_h = int(df_huidig["hospital"].dropna().nunique()) if not df_huidig.empty else 0
    rows.append(
        _row(
            sk.get("rij_actieve_ziekenhuizen", "Actieve ziekenhuizen"),
            str(zh_v),
            str(zh_h),
            _delta_n(zh_h, zh_v),
            float(zh_h - zh_v),
            _t_n,
            True,
        )
    )

    # --- Dynamische titel: jaren afleiden uit de DataFrames ---
    _bl_yr = (
        int(df_vorig["_year"].dropna().iloc[0])
        if "_year" in df_vorig.columns and not df_vorig.empty
        else ""
    )
    _cu_yr = (
        int(df_huidig["_year"].dropna().iloc[0])
        if "_year" in df_huidig.columns and not df_huidig.empty
        else ""
    )
    _titel_base = sk.get("titel", "Kerncijfers vergelijking")
    if venster_modus == "tendens":
        title = f"{_titel_base}\u00a0\u2014 S2\u00a0{_bl_yr}\u00a0vs\u00a0{_cu_yr}"
    else:
        title = f"{_titel_base}\u00a0\u2014 {_bl_yr}\u00a0vs\u00a0{_cu_yr}"

    # --- Titel + CSV-downloadknop (HTML — zelfde stijl als _render_sortable_table) ---
    _kc_csv_buf = io.StringIO()
    pd.DataFrame(
        [
            {
                col_kpi: r["label"],
                col_vorig: r["vorig"],
                col_huidig: r["huidig"],
                col_delta: r["delta"],
                col_trend: r["arrow"],
            }
            for r in rows
        ]
    ).to_csv(_kc_csv_buf, index=False)
    _kc_b64 = base64.b64encode(_kc_csv_buf.getvalue().encode()).decode()
    _kc_filename = f"kerncijfers-{_bl_yr}-vs-{_cu_yr}.csv"
    _kc_header_html = (
        f"<div style='display:flex;justify-content:space-between;align-items:center;"
        f"margin-bottom:0'>"
        f"<h4 style='margin:0;font-size:24px;font-weight:600;color:#1A1A1A;"
        f'font-family:"Source Sans",sans-serif;line-height:1.3\'>'
        f"{html.escape(title)}</h4>"
        f"<a href='data:text/csv;base64,{_kc_b64}' download='{_kc_filename}'"
        f" style='background:#003a70;color:#fff;padding:4px 14px;border-radius:4px;"
        f"font-size:0.78rem;font-family:Poppins,Verdana,sans-serif;white-space:nowrap;"
        f"text-decoration:none;display:inline-block'>📤 Export CSV</a>"
        f"</div>"
    )

    _th_base = (
        f"background:{ZORGI_DARK_BLUE};color:#ffffff;"
        f"font-family:Poppins,Verdana,sans-serif;font-weight:800;"
        f"padding:6px 12px;text-align:left;font-size:0.82rem;white-space:nowrap;"
        f"overflow:hidden;text-overflow:ellipsis"
    )
    _td_base = (
        "font-family:Poppins,Verdana,sans-serif;padding:5px 12px;"
        "font-size:0.82rem;border-bottom:1px solid #e0e8f0;overflow:hidden;text-overflow:ellipsis"
    )
    _row_colors = ("#ffffff", ZORGI_ULTRA_LIGHT)

    # Vaste kolombreedtes — identiek in beide venstermodi (Volledig én Tendens)
    _w = {"kpi": "38%", "val": "20%", "delta": "13%", "trend": "9%"}

    parts = [
        _kc_header_html,
        "<table style='width:100%;border-collapse:collapse;margin-top:0;table-layout:fixed'>",
        "<thead><tr>",
        f"<th style='{_th_base};width:{_w['kpi']}'>{html.escape(col_kpi)}</th>",
        f"<th style='{_th_base};width:{_w['val']}'>{html.escape(col_vorig)}</th>",
        f"<th style='{_th_base};width:{_w['val']}'>{html.escape(col_huidig)}</th>",
        f"<th style='{_th_base};width:{_w['delta']}'>{html.escape(col_delta)}</th>",
        f"<th style='{_th_base};width:{_w['trend']}'>{html.escape(col_trend)}</th>",
        "</tr></thead><tbody>",
    ]

    for i, r in enumerate(rows):
        bg = _row_colors[i % 2]
        _td = f"{_td_base};background:{bg}"
        parts += [
            "<tr>",
            f"<td style='{_td}'>{html.escape(r['label'])}</td>",
            f"<td style='{_td}'>{html.escape(r['vorig'])}</td>",
            f"<td style='{_td}'>{html.escape(r['huidig'])}</td>",
            (
                f"<td style='{_td};color:{r['delta_color']};font-weight:600'>"
                f"{html.escape(r['delta'])}</td>"
            ),
            (
                f"<td style='{_td}'>"
                f"<span style='color:{r['arrow_color']};font-weight:700' "
                f"title='{html.escape(r['tooltip'])}'>{r['arrow']}</span>"
                f"</td>"
            ),
            "</tr>",
        ]

    parts.append("</tbody></table>")
    st.markdown("\n".join(parts), unsafe_allow_html=True)

    # --- Mediaan-toelichting (analoog aan ppt-verklaring boven de tabel) ---
    _med_note = sk.get("mediaan_toelichting", "")
    if _med_note:
        _n_sc_h = len(sc_h)
        _n_sc_v = len(sc_v)
        _n_ctx = (
            f" Berekend op <strong>{_n_sc_h}</strong> gescoorde tickets (huidig) "
            f"vs <strong>{_n_sc_v}</strong> (vorig)."
            if lang == "nl"
            else f" Calcul\u00e9 sur <strong>{_n_sc_h}</strong> tickets \u00e9valu\u00e9s (actuel) "
            f"vs <strong>{_n_sc_v}</strong> (r\u00e9f\u00e9rence)."
        )
        st.markdown(
            f"<div style='font-size:0.85rem;color:#5f8495;margin-top:0.5rem;"
            f"line-height:1.55'>{_med_note}{_n_ctx}</div>",
            unsafe_allow_html=True,
        )

    # --- Trend-toelichting (drempelwaarden en pijl-semantiek) ---
    _trend_note = sk.get("trend_toelichting", "")
    if _trend_note:
        st.markdown(
            f"<div style='font-size:0.85rem;color:#5f8495;margin-top:0.3rem;"
            f"line-height:1.55'>{_trend_note}</div>",
            unsafe_allow_html=True,
        )


def _tab_summary(data: DashboardData, t: dict, lang: str) -> None:
    d = t["dashboard"]

    # Referentie-label: verschilt per modus → maakt deltarij mode-gevoelig
    _ref_str = (
        d["vs_h2"] if data.mode == "trend" else d["vs_baseline"].format(label=data.baseline_label)
    )

    # --- Individuele suffixen per KPI (baseline gemiddelde als context) ---
    # Referentie HC-ratio: trend-modus → S2 baseline; full-modus → volledig baseline jaar
    _hc_baseline = (
        data.raw.benchmark_h2.hc_ratio
        if data.mode == "trend" and data.raw and data.raw.benchmark_h2
        else (data.raw.baseline_hc_ratio if data.raw else data.kpi_high_critical_ratio)
    )
    _avg_abbrev = d.get("kpi_avg_abbrev", "gem.")
    _avg_sfx, _pos_sfx, _neg_sfx, _hc_sfx = _build_kpi_suffixes(data, _avg_abbrev, _hc_baseline)

    # --- Rij A: Prestatie-KPIs ---
    row1 = st.columns(4)

    _tgt = {kp.name: kp for kp in data.kpi_targets}
    _avg_tgt = _tgt.get("avg_score_min")
    _pos_tgt = _tgt.get("pct_positive_min")
    _neg_tgt = _tgt.get("pct_negative_max")
    _hc_tgt = _tgt.get("high_critical_max")

    _yr = str(data.current_year)
    _avg_tgt_str = f"{_avg_tgt.target:.2f}★".replace(".", ",") if _avg_tgt else "4,00★"
    _pos_tgt_str = f"{_pos_tgt.target:.0f}%" if _pos_tgt else "75%"
    _neg_tgt_str = f"{_neg_tgt.target:.0f}%" if _neg_tgt else "15%"
    _hc_tgt_str = f"{_hc_tgt.target:.0f}%" if _hc_tgt else "15%"

    _hc_delta_vs_baseline = round(data.kpi_high_critical_ratio - _hc_baseline, 1)

    _dot3 = "\u00b7\u00b7\u00b7"

    row1[0].metric(
        label=f"{d['kpi_avg_score'].format(year=_yr)}  {_dot3} {d['kpi_target_above'].format(t=_avg_tgt_str)}",
        value=f"{data.kpi_avg_score:.2f}★".replace(".", ","),
        delta=f"{data.kpi_avg_score_delta:+.2f}★  {_ref_str}{_avg_sfx}",
    )
    row1[1].metric(
        label=f"{d['kpi_pct_positive'].format(year=_yr)}  {_dot3} {d['kpi_target_above'].format(t=_pos_tgt_str)}",
        value=f"{data.kpi_pct_positive:.1f}%",
        delta=f"{data.kpi_pct_positive_delta:+.1f} ppt  {_ref_str}{_pos_sfx}",
    )
    row1[2].metric(
        label=f"{d['kpi_pct_negative'].format(year=_yr)}  {_dot3} {d['kpi_target_below'].format(t=_neg_tgt_str)}",
        value=f"{data.kpi_pct_negative:.1f}%",
        delta=f"{data.kpi_pct_negative_delta:+.1f} ppt  {_ref_str}{_neg_sfx}",
        delta_color="inverse",
    )
    row1[3].metric(
        label=f"{d['kpi_high_critical'].format(year=_yr)}  {_dot3} {d['kpi_target_below'].format(t=_hc_tgt_str)}",
        value=f"{data.kpi_high_critical_ratio:.1f}%",
        delta=f"{_hc_delta_vs_baseline:+.1f} ppt  {_ref_str}{_hc_sfx}",
        delta_color="inverse",
    )

    # --- Rij B: Context & Risico ---
    row2 = st.columns(4)

    _months_i18n = t.get("months", [])

    # T5: recentste maand — delta = vs huidig jaar + gem. voorafgaande maanden
    _recent_name = ""
    try:
        _parts = data.kpi_recent_month_name.split("-")
        _m_idx = int(_parts[1]) - 1
        _recent_name = f"{_months_i18n[_m_idx].capitalize()} {_parts[0]}"
    except (IndexError, ValueError):
        _recent_name = data.kpi_recent_month_name

    _cy_preceding = [
        p
        for p in data.timeline
        if p.period.startswith(_yr)
        and p.total_tickets > 0
        and p.period < data.kpi_recent_month_name
    ]
    if _cy_preceding:
        _ytd_tickets = sum(p.total_tickets for p in _cy_preceding)
        _ytd_avg = round(
            sum(p.avg_score * p.total_tickets for p in _cy_preceding) / _ytd_tickets, 2
        )
        _ytd_avg_str = str(_ytd_avg).replace(".", ",")
        _t5_delta = (
            f"{data.kpi_recent_month_target_delta:+.2f}★ vs {_yr} ({_avg_abbrev} {_ytd_avg_str}★)"
        )
    else:
        _t5_delta = f"{data.kpi_recent_month_target_delta:+.2f}★ vs {_yr}"

    row2[0].metric(
        label=f"{_recent_name}  {_dot3} {d['kpi_target_above'].format(t=_avg_tgt_str)}",
        value=f"{data.kpi_recent_month_score:.2f}★".replace(".", ","),
        delta=_t5_delta,
    )

    # T6: responses — absolute delta tickets/mnd vs S2 baseline (trend) of volledig baseline jaar
    _yr_bl = str(data.current_year - 1)
    _resp_unit = d.get("kpi_responses_unit_short", "/mnd")
    if data.mode == "trend" and data.raw and data.raw.benchmark_h2:
        _resp_baseline_avg = data.kpi_responses_h2_monthly_avg
        _bl_lbl_t6 = data.raw.benchmark_h2.label  # bijv. "S2 2025"
    else:
        _resp_baseline_avg = data.kpi_responses_baseline_monthly_avg
        _bl_lbl_t6 = _yr_bl
    _resp_baseline_str = str(_resp_baseline_avg).replace(".", ",")
    # Correct: enkel maanden van huidig jaar tellen
    _cy_months_t6 = max(
        len([p for p in data.timeline if p.total_tickets > 0 and p.period.startswith(_yr)]),
        1,
    )
    _resp_rate = data.kpi_responses_total / _cy_months_t6
    _resp_diff = round(_resp_rate - _resp_baseline_avg, 1)
    _resp_diff_str = str(abs(_resp_diff)).replace(".", ",")
    _resp_context = f"vs {_bl_lbl_t6} ({_avg_abbrev} {_resp_baseline_str}{_resp_unit})"
    _resp_delta = (
        f"+{_resp_diff_str} tickets{_resp_unit} {_resp_context}"
        if _resp_diff >= 0
        else f"-{_resp_diff_str} tickets{_resp_unit} {_resp_context}"
    )
    row2[1].metric(
        label=d["kpi_responses"].format(year=_yr),
        value=str(data.kpi_responses_total),
        delta=_resp_delta,
        delta_color="normal",
    )

    # T7: streak — huidig jaar % vs S2 baseline (trend) of volledig baseline jaar
    # Correct: enkel maanden van huidig jaar tellen
    _cy_months_t7 = max(
        len([p for p in data.timeline if p.total_tickets > 0 and p.period.startswith(_yr)]),
        1,
    )
    _cy_streak_pct = round(data.kpi_streak_current_year / _cy_months_t7 * 100, 0)
    if data.mode == "trend" and data.raw and data.raw.benchmark_h2:
        _bl_streak_pct = int(data.kpi_streak_h2_pct)
        _bl_lbl_t7 = data.raw.benchmark_h2.label  # bijv. "S2 2025"
    else:
        _bl_streak_pct = int(data.kpi_streak_baseline_pct)
        _bl_lbl_t7 = _yr_bl
    _streak_diff_pct = int(_cy_streak_pct) - _bl_streak_pct
    _streak_context = f"vs {_bl_lbl_t7} ({_avg_abbrev} {_bl_streak_pct}%)"
    _streak_delta = (
        f"+{_streak_diff_pct}% {_streak_context}"
        if _streak_diff_pct >= 0
        else f"-{abs(_streak_diff_pct)}% {_streak_context}"
    )
    row2[2].metric(
        label=d["kpi_streak"].format(year=_yr),
        value=str(data.kpi_streak_current_year),
        delta=_streak_delta,
        delta_color="normal",
    )

    # T8: ziekenhuizen kritiek · aandacht — standaard st.metric() identiek aan T1-T7
    _crit_count = data.kpi_critical_accounts
    _attn_count = data.kpi_attention_accounts
    _t8_delta = (
        "-" + " \u00b7 ".join(data.kpi_critical_account_names)
        if data.kpi_critical_account_names
        else None
    )
    row2[3].metric(
        label=d["kpi_accounts_label"],
        value=f"{_crit_count} \u00b7 {_attn_count}",
        delta=_t8_delta,
        delta_color="normal",
    )

    # --- ppt-verklaring (markdown met vet) ---
    _ppt_text = d.get("ppt_explanation", "")
    if _ppt_text:
        st.markdown(
            f"<div style='font-size:0.85rem;color:#5f8495;margin-top:0.1rem;"
            f"margin-bottom:0.25rem;line-height:1.55'>{_ppt_text}</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    _render_zh_signal_section(data, d)
    # Slanke scheidingslijn zonder Streamlit-padding (vervangt st.divider() na sectie 2)
    st.markdown(
        "<hr style='margin:1.5rem 0 2rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )

    # --- Tegel 3: Kerncijfers vergelijking (7 rijen, venster-aware kolomlabels) ---
    # Aanroeper _tab_summary bereidt df_vorig en df_huidig via _make_kc_dataframes
    # (spec: slicing verantwoordelijkheid van de aanroepende laag, niet van de renderfunctie).
    venster_modus = "tendens" if data.mode == "trend" else "volledig"
    df_t3_vorig, df_t3_huidig = _make_kc_dataframes(data, venster_modus)
    render_kerncijfers_vergelijking(df_t3_vorig, df_t3_huidig, venster_modus, lang)


def _tab_timeline(data: DashboardData, t: dict, lang: str) -> None:
    """Tab 2 — Tijdlijn: combo-grafiek + blokkenverlijking + rolling avg."""
    d = t["dashboard"]
    if not data.timeline:
        st.info(d["no_data"])
        return

    st.markdown(f"#### {d['timeline_title']}")
    st.plotly_chart(_chart_timeline(data, t, lang), width="stretch", config=_CHART_CONFIG)
    st.divider()
    st.markdown(f"#### {d['period_comparison_title']}")
    st.plotly_chart(_chart_period_comparison(data, t, lang), width="stretch", config=_CHART_CONFIG)
    st.divider()
    st.markdown(f"#### {d.get('rolling_avg_title', 'Voortschrijdend gemiddelde (3 maanden)')}")
    st.plotly_chart(_chart_rolling_avg(data, t, lang), width="stretch", config=_CHART_CONFIG)


def _tab_tickets(data: DashboardData, t: dict, lang: str) -> None:  # noqa: C901
    """Tab 3 — Tickets & Prioriteit: feedbackthema's actiekaarten + bar charts."""
    d = t["dashboard"]
    theme_actions = d.get("theme_action", {})

    # --- Feedbackthema's actiekaarten bovenaan ---
    st.markdown(f"#### {d['feedback_themes_title']}")

    # Sorteer thema's op pct_current (aflopend), neem top-4
    sorted_themes = sorted(
        [th for th in data.negative_themes if th.pct_current > 0],
        key=lambda th: th.pct_current,
        reverse=True,
    )[:4]

    _theme_colors = {
        "responstijd": "#fff3cd",
        "onvolledig": "#d1ecf1",
        "communicatie": "#d4edda",
        "urgentie": "#f8d7da",
    }

    if sorted_themes:
        for theme in sorted_themes:
            cfg = theme_actions.get(theme.theme_key, {})
            title = cfg.get("title", theme.theme_key).format(pct=f"{theme.pct_current:.0f}")
            action = cfg.get("action", theme.action_hint)
            bg = _theme_colors.get(theme.theme_key, ZORGI_ULTRA_LIGHT)
            st.markdown(
                f"<div style='background:{bg};border-radius:8px;padding:0.75rem 1rem;"
                f"margin-bottom:0.5rem;border-left:4px solid {ZORGI_DARK_BLUE}'>"
                f"<b>{title}</b><br><small>→ {action}</small></div>",
                unsafe_allow_html=True,
            )
    else:
        st.info(d["no_data"])

    st.divider()

    # --- Issue type grouped bar + tabel ---
    st.markdown(f"#### {d['issue_type_title']}")
    if data.by_issue_type:
        fig = _chart_grouped_bar(
            data.by_issue_type,
            "issue_type",
            d["issue_type_title"],
            data.baseline_label,
            data.current_label,
        )
        st.plotly_chart(fig, width="stretch")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Type": i.issue_type,
                        f"{data.baseline_label} score": f"{i.baseline_score:.2f}★",
                        f"{data.current_label} score": f"{i.current_score:.2f}★",
                    }
                    for i in data.by_issue_type
                ]
            ),
            hide_index=True,
            width="stretch",
        )

    st.divider()

    # --- Prioriteit grouped bar + tabel + Trivial-alert ---
    st.markdown(f"#### {d['priority_title']}")
    if data.by_priority:
        fig = _chart_grouped_bar(
            data.by_priority,
            "priority",
            d["priority_title"],
            data.baseline_label,
            data.current_label,
        )
        st.plotly_chart(fig, width="stretch", config=_CHART_CONFIG)

        if data.trivial_pct_negative > 10 and data.trivial_avg_score > 0:
            st.warning(
                d["trivial_alert"].format(
                    score=f"{data.trivial_avg_score:.2f}",
                    pct=f"{data.trivial_pct_negative:.1f}",
                )
            )


def _tab_response(data: DashboardData, t: dict, lang: str) -> None:
    """Tab 4 — Responstijd: statistieken + correlatie-panel + lijn-grafiek per score-niveau."""
    d = t["dashboard"]

    # --- Sectie 1: Statistieken responstijd (gem., mediaan, pos. vs neg.) ---
    rt_insight = data.response_time_insight
    if rt_insight and rt_insight.avg_days is not None:
        st.markdown(f"#### {d.get('response_stats_title', 'Statistieken responstijd')}")
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric(
            label=d.get("response_avg_days", "Gem. responstijd"),
            value=f"{rt_insight.avg_days:.1f}d".replace(".", ","),
            delta=None,
        )
        col_b.metric(
            label=d.get("response_median_days", "Mediaan"),
            value=f"{rt_insight.median_days:.1f}d".replace(".", ",")
            if rt_insight.median_days is not None
            else "—",
        )
        col_c.metric(
            label=d.get("response_positive_avg", "Gem. bij positief (\u2265\u00a04\u2605)"),
            value=f"{rt_insight.avg_positive_days:.1f}d".replace(".", ",")
            if rt_insight.avg_positive_days is not None
            else "—",
        )
        col_d.metric(
            label=d.get("response_negative_avg", "Gem. bij negatief (\u2264\u00a02\u2605)"),
            value=f"{rt_insight.avg_negative_days:.1f}d".replace(".", ",")
            if rt_insight.avg_negative_days is not None
            else "—",
            delta_color="inverse",
        )
        st.divider()

    # --- Sectie 2: Correlatie-ommekeer panel ---
    st.markdown(f"#### {d['correlation_panel_title']}")
    col1, col2, col3 = st.columns(3)

    b_corr = data.baseline_correlation
    c_corr = data.current_correlation

    with col1, st.container(border=True):
        st.markdown(f"**{d['corr_2025_title']}**")
        st.markdown(d["corr_2025_body"].format(r=f"{b_corr:.3f}" if b_corr is not None else "N/A"))
    with col2, st.container(border=True):
        st.markdown(f"**{d['corr_q1_title']}**")
        st.markdown(d["corr_q1_body"].format(r=f"{c_corr:.3f}" if c_corr is not None else "N/A"))
    with col3, st.container(border=True):
        st.markdown(f"**{d['corr_conclusion_title']}**")
        st.markdown(d["corr_conclusion_body"])

    st.divider()

    # --- Sectie 3: Lijn-grafiek responstijd per score-niveau ---
    st.markdown(f"#### {d.get('response_chart_title', 'Gem. responstijd per score-niveau')}")
    if data.response_time_by_score:
        st.plotly_chart(_chart_response_time(data, t), width="stretch")
    else:
        st.info(d["no_data"])

    # --- Sectie 4: Negatieve cases met hoge responstijd ---
    neg_cases = [c for c in (data.negative_cases or []) if c.response_days is not None]
    neg_cases_sorted = sorted(neg_cases, key=lambda c: -(c.response_days or 0))[:10]
    if neg_cases_sorted:
        st.divider()
        st.markdown(
            f"#### {d.get('response_negative_cases_title', 'Negatieve cases — hoge responstijd')}"
        )
        _render_sortable_table(
            pd.DataFrame(
                [
                    {
                        d.get("response_col_ticket", "Ticket"): c.ticket_id,
                        d.get("response_col_hospital", "Ziekenhuis"): c.hospital,
                        d.get("response_col_score", "Score"): f"{c.score}\u2605",
                        d.get("response_col_days", "Dagen"): f"{c.response_days:.1f}d".replace(
                            ".", ","
                        ),
                        d.get("response_col_category", "Thema"): c.category,
                    }
                    for c in neg_cases_sorted
                ]
            ),
            title=d.get("response_negative_cases_title", "Negatieve cases — hoge responstijd"),
            export_filename=f"negative-cases-response-{data.current_label}.csv",
            col_widths=["15%", "30%", "10%", "12%", "33%"],
        )


def _render_sortable_table(
    df: pd.DataFrame,
    title: str,
    *,
    delta_col: str | None = None,
    max_body_height: int = 460,
    min_body_height: int = 0,
    export_filename: str = "export.csv",
    export_label: str = "📤 Export CSV",
    footer_text: str = "",
    col_widths: list[str] | None = None,
    show_title: bool = True,  # False = titel weglaten uit iframe (extern via st.markdown)
) -> None:
    """Rendert een sorteerbare HTML-tabel in een iframe met exportknop.

    - Titel matcht visueel met st.markdown('#### ...') — Poppins, ZORGI-stijl.
    - Alle kolomkoppen: ZORGI donkerblauw achtergrond (#003a70), witte tekst.
    - delta_col: waarden krijgen groen/rood kleur op basis van +-teken.
    - Klik op kolomkop → sorteren (toggle asc/desc).
    - footer_text: optionele grijze voetnoot binnen het iframe (geen Streamlit-componentgap).
    """
    cols = list(df.columns)
    n_rows = len(df)

    # CSV-export (base64 data-URI)
    buf = io.StringIO()
    df.to_csv(buf, index=False, quoting=csv.QUOTE_ALL)
    b64 = base64.b64encode(buf.getvalue().encode()).decode()

    # Tabelkop HTML — met sorteer-indicator; optionele col_widths via style="width:..."
    def _th(i: int, c: str) -> str:
        w = f'style="width:{col_widths[i]}"' if col_widths and i < len(col_widths) else ""
        return (
            f'<th onclick="sortBy({i})" data-col="{i}" {w}>'
            f'<span class="th-label">{html.escape(str(c))}</span>'
            f'<span class="sort-icon" id="si{i}"></span></th>'
        )

    th_html = "".join(_th(i, c) for i, c in enumerate(cols))

    # Delta-kleurstijl
    def _delta_style(val: str) -> str:
        stripped = val.replace("\u2605", "").replace("+", "").strip()
        try:
            v = float(stripped.replace(",", "."))
            if v > 0:
                return "color:#2e7d32;font-weight:600;"
            if v < 0:
                return "color:#dc2b26;font-weight:600;"
        except ValueError:
            pass
        return ""

    # Tabelrijen HTML — inline text-align:left op elke cel (voorkomt browser-overschrijving)
    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for c in cols:
            val = html.escape(str(row[c]))
            delta_s = _delta_style(str(row[c])) if (delta_col and c == delta_col) else ""
            style = f"text-align:left;{delta_s}"
            cells += f'<td style="{style}">{val}</td>'
        rows_html += f"<tr>{cells}</tr>"

    # Hoogte-berekening
    # th-rij (32px) + filterrij (30px) zitten BINNEN de scroll-wrap → meeverekenen in scroll_wrap_h
    # 36px per datarij | 8px buffer | top-row: 44px | 4px margin | 16px eindbuffer
    content_h = 32 + 30 + n_rows * 36 + 8
    scroll_wrap_h = min(content_h, max_body_height)
    footer_h = 28 * len(footer_text.split("  |  ")) if footer_text else 0
    top_row_h = 44 if show_title else 0
    iframe_h = top_row_h + 4 + scroll_wrap_h + footer_h + 16

    safe_title = html.escape(title)
    safe_label = html.escape(export_label)
    safe_footer = footer_text if footer_text else ""
    if safe_footer:
        _footer_lines = safe_footer.split("  |  ")
        footer_html = "".join(
            f"<p class='footer'>{html.escape(line)}</p>" for line in _footer_lines
        )
    else:
        footer_html = ""

    html_str = (
        "<!DOCTYPE html><html><head>"
        "<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Source+Sans+3:wght@400;600&display=swap'"
        " rel='stylesheet'>"
        "<style>"
        "body{margin:0;padding:0;background:transparent;"
        "font-family:'Poppins','Verdana',sans-serif;}"
        ".top-row{display:flex;justify-content:space-between;align-items:center;"
        "margin:0 0 4px 0;gap:8px;}"
        "h4.sec-title{margin:0;font-size:24px;font-weight:700;color:#1A1A1A;"
        "font-family:'Source Sans','Source Sans Pro','Source Sans 3',sans-serif;line-height:1.3;}"
        ".export-btn{background:#003a70;color:#fff;border:none;padding:4px 14px;"
        "border-radius:4px;font-size:0.78rem;cursor:pointer;"
        "font-family:'Poppins','Verdana',sans-serif;white-space:nowrap;"
        "text-decoration:none;display:inline-block;}"
        ".export-btn:hover{background:#00509e;}"
        f".scroll-wrap{{max-height:{max_body_height}px;overflow-y:auto;width:100%;"
        "border:1px solid #d0dce8;border-radius:2px;}"
        "table{width:100%;border-collapse:separate;border-spacing:0;"
        "border-bottom:1px solid #d0dce8;border-right:1px solid #d0dce8;}"
        "th{background:#003a70;color:#fff;padding:6px 8px;text-align:left;"
        "font-size:0.82rem;font-family:'Poppins','Verdana',sans-serif;"
        "cursor:pointer;border-right:1px solid #2a5a9c;border-bottom:1px solid #2a5a9c;"
        "white-space:nowrap;user-select:none;position:sticky;top:0;z-index:2;}"
        ".th-label{vertical-align:middle;}"
        ".sort-icon{display:inline-block;margin-left:5px;font-size:0.75rem;"
        "vertical-align:middle;opacity:0.85;min-width:12px;}"
        "th.sorted-asc .sort-icon::after{content:'\\2191';}"
        "th.sorted-desc .sort-icon::after{content:'\\2193';}"
        "th.sorted-asc,th.sorted-desc{background:#1a5faf;}"
        ".filter-row td{background:#e8f0f7;padding:3px 4px;"
        "position:sticky;top:32px;z-index:1;border-bottom:2px solid #b0c8e0;"
        "border-right:1px solid #c8d8e8;}"
        ".filter-row td:last-child{border-right:none;}"
        ".filter-row input{width:100%;box-sizing:border-box;border:1px solid #b0c8e0;"
        "border-radius:3px;padding:2px 5px;font-size:0.75rem;"
        "font-family:'Poppins','Verdana',sans-serif;background:#fff;color:#1a1a1a;}"
        ".filter-row input:focus{outline:none;border-color:#003a70;}"
        "td{padding:5px 8px;font-size:0.82rem;text-align:left;"
        "border-bottom:1px solid #e0e8f0;border-right:1px solid #d0dce8;}"
        "tr:last-child td{border-bottom:none;}"
        "tr:hover td{background:#f0f6ff;}"
        "tr.hidden{display:none;}"
        "p.footer{font-size:0.75rem;color:#5f8495;margin:8px 0 0 0;padding:0;line-height:1.5;}"
        "</style></head><body>"
        + (
            f"<div class='top-row'>"
            f"<h4 class='sec-title'>{safe_title}</h4>"
            f"<a href='data:text/csv;base64,{b64}' download='{export_filename}'"
            f" class='export-btn'>{safe_label}</a>"
            "</div>"
            if show_title
            else f"<div class='top-row' style='justify-content:flex-end;margin-bottom:4px'>"
            f"<a href='data:text/csv;base64,{b64}' download='{export_filename}'"
            f" class='export-btn'>{safe_label}</a>"
            "</div>"
        )
        + "<div class='scroll-wrap'>"
        f"<table id='t'><thead>"
        f"<tr>{th_html}</tr>"
        f"<tr class='filter-row' id='fr'>"
        + "".join(
            f"<td><input type='text' placeholder='🔍' oninput='applyFilters()' "
            f"id='fi{i}' autocomplete='off'/></td>"
            for i in range(len(cols))
        )
        + "</tr>"
        f"</thead>"
        f"<tbody>{rows_html}</tbody></table>"
        f"</div>{footer_html}"
        "<script>"
        "var _sd=-1,_sc=true;"
        "function applyFilters(){"
        "var tb=document.getElementById('t').tBodies[0];"
        "var rows=Array.from(tb.rows);"
        "var filters=[];"
        f"for(var i=0;i<{len(cols)};i++){{"
        "var el=document.getElementById('fi'+i);"
        "filters.push(el?el.value.toLowerCase():'');}"
        "rows.forEach(function(r){"
        "var show=filters.every(function(f,i){"
        "return !f||r.cells[i].textContent.toLowerCase().includes(f);});"
        "r.classList.toggle('hidden',!show);});}"
        "function sortBy(ci){"
        "var t=document.getElementById('t');"
        "var tb=t.tBodies[0];"
        "var rows=Array.from(tb.rows).filter(function(r){return !r.classList.contains('hidden');});"
        "var asc=(_sd===ci)?!_sc:true;"
        "_sd=ci;_sc=asc;"
        "rows.sort(function(a,b){"
        "var av=a.cells[ci].textContent.trim();"
        "var bv=b.cells[ci].textContent.trim();"
        "var an=parseFloat(av.replace(/[\u2605+]/g,''));"
        "var bn=parseFloat(bv.replace(/[\u2605+]/g,''));"
        "if(!isNaN(an)&&!isNaN(bn))return asc?an-bn:bn-an;"
        "return asc?av.localeCompare(bv,undefined,{sensitivity:'base'}):"
        "bv.localeCompare(av,undefined,{sensitivity:'base'});"
        "});"
        "rows.forEach(function(r){tb.appendChild(r);});"
        "var ths=document.getElementById('t').querySelectorAll('th');"
        "ths.forEach(function(th){th.classList.remove('sorted-asc','sorted-desc');});"
        "ths[ci].classList.add(asc?'sorted-asc':'sorted-desc');}"
        "</script></body></html>"
    )

    _stc.html(html_str, height=iframe_h, scrolling=False)
    # Negatieve marge: compenseert het verschil tussen Python-berekende iframe_h
    # en werkelijke content-hoogte + stVerticalBlock gap (16px).
    # inject_iframe_resize() past de exacte hoogte achteraf aan via JS.
    st.markdown(
        "<div style='margin-top:-80px;height:0;overflow:hidden'></div>",
        unsafe_allow_html=True,
    )


def _windowed_hospital_comparison(
    data: DashboardData,
    venster_modus: str,
) -> list[HospitalComparison]:
    """
    Bereken per-ziekenhuis vergelijking op basis van het venster.

    - 'volledig': volledig baseline-jaar (bv. 2025) vs. huidig jaar
    - 'tendens':  S2 baseline-jaar (jul-dec 2025) vs. huidig jaar

    Hergebruikt _make_kc_dataframes() voor consistente pilaar- en datumfiltering.
    Geeft dezelfde interface terug als raw.hospital_comparison.
    """
    df_vorig, df_huidig = _make_kc_dataframes(data, venster_modus)

    b_hospitals: set[str] = (
        set(df_vorig["hospital"].dropna().unique()) if not df_vorig.empty else set()
    )
    c_hospitals: set[str] = (
        set(df_huidig["hospital"].dropna().unique()) if not df_huidig.empty else set()
    )
    all_hospitals = sorted(b_hospitals | c_hospitals)

    comparisons: list[HospitalComparison] = []
    for hospital in all_hospitals:
        b_sub = df_vorig[df_vorig["hospital"] == hospital] if not df_vorig.empty else pd.DataFrame()
        c_sub = (
            df_huidig[df_huidig["hospital"] == hospital] if not df_huidig.empty else pd.DataFrame()
        )

        b_scored = b_sub[b_sub["score"].notna()] if not b_sub.empty else pd.DataFrame()
        c_scored = c_sub[c_sub["score"].notna()] if not c_sub.empty else pd.DataFrame()

        b_score = float(b_scored["score"].mean()) if not b_scored.empty else 0.0
        b_total = len(b_sub)
        c_score: float | None = float(c_scored["score"].mean()) if not c_scored.empty else None
        c_total = len(c_sub)

        comparisons.append(
            HospitalComparison(
                hospital=hospital,
                baseline_score=b_score,
                baseline_total=b_total,
                current_score=c_score,
                current_total=c_total,
            )
        )
    return comparisons


def _render_migration_tables(
    raw: EvolutionResult,
    d: dict,
    col_h: str,
    col_tickets_bl: str,
    col_tickets_cu: str,
    col_date: str,
    compared_to: str,
    bl: str,
    cu: str,
) -> None:
    """Rendert sectie E (verdwenen) en F (nieuwe) ziekenhuistabellen."""
    # --- E: Verdwenen ziekenhuizen ---
    st.markdown(
        "<hr style='margin:0.4rem 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )
    disappeared_title = d.get("hospital_disappeared_title", "Verdwenen ziekenhuizen")
    n_dis = len(raw.hospitals_disappeared)
    if raw.hospitals_disappeared:
        df_e = pd.DataFrame(
            [
                {
                    col_h: hm.hospital,
                    col_tickets_bl: hm.total_tickets,
                    col_date: hm.anchor_date or "\u2014",
                }
                for hm in raw.hospitals_disappeared
            ]
        )
        _render_sortable_table(
            df_e,
            title=f"\U0001f4e4 {disappeared_title} ({n_dis}) {compared_to} {bl}",
            export_filename=f"verdwenen-{cu}.csv",
            col_widths=["55%", "20%", "25%"],
        )
    else:
        st.markdown(f"#### \U0001f4e4 {disappeared_title}")
        st.info(d.get("hospital_no_disappeared", "Geen verdwenen ziekenhuizen."))

    # --- F: Nieuwe ziekenhuizen ---
    st.markdown(
        "<hr style='margin:0.4rem 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )
    new_title = d.get("hospital_new_title", "Nieuwe ziekenhuizen")
    n_new = len(raw.hospitals_new)
    if raw.hospitals_new:
        df_f = pd.DataFrame(
            [
                {
                    col_h: hm.hospital,
                    col_tickets_cu: hm.total_tickets,
                    col_date: hm.anchor_date or "\u2014",
                }
                for hm in raw.hospitals_new
            ]
        )
        _render_sortable_table(
            df_f,
            title=f"\U0001f195 {new_title} ({n_new}) {compared_to} {bl}",
            export_filename=f"nieuwe-{cu}.csv",
            col_widths=["55%", "20%", "25%"],
        )
    else:
        st.markdown(f"#### \U0001f195 {new_title}")
        st.info(d.get("hospital_no_new", "Geen nieuwe ziekenhuizen."))


def _tab_hospitals(data: DashboardData, t: dict, lang: str) -> None:
    """Tab 5 — Ziekenhuizen: bar chart + bottom10/attention/top10 + evolutie/migratie tabellen."""
    d = t["dashboard"]
    bl = data.baseline_label  # bv. "2025"
    cu = data.current_label  # bv. "2026"

    # --- Grafiek ---
    if data.hospital_top10 or data.hospital_bottom10 or data.hospital_attention:
        st.markdown(
            f"<h4 style='font-size:1.3rem;font-weight:700;color:#003a70;"
            f"font-family:Poppins,Verdana,sans-serif;line-height:1.3;margin:0 0 4px 0'>"
            f"{d['hospital_chart_title']}</h4>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_chart_hospitals(data, t), width="stretch")
    st.markdown(
        f"<p style='font-size:0.78rem;color:#5f8495;margin-top:-1.2rem;margin-bottom:2.5rem'>"
        f"<span style='color:{ZORGI_RED};font-weight:700'>- - -</span> "
        f"{d.get('hospital_disengagement_caption', '')}</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<hr style='margin:0 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )

    # --- A: Bottom 10 (< 3,0★) ---
    if data.hospital_bottom10:
        # Disengagement-alerts als footer_text binnen de iframe (geen Streamlit-gap)
        _dis_lines = [
            f"⚠️ {d['disengagement_alert'].format(hospital=h.hospital, score=f'{h.score:.2f}', tickets=h.tickets)}"
            for h in data.hospital_bottom10
            if h.disengagement_risk
        ]
        _dis_footer = "  |  ".join(_dis_lines) if _dis_lines else ""
        _render_sortable_table(
            pd.DataFrame(
                [
                    {
                        d["col_hospital"]: h.hospital,
                        d["col_score"]: f"{h.score:.2f}★",
                        d["col_tickets"]: str(h.tickets),
                    }
                    for h in data.hospital_bottom10
                ]
            ),
            title=f"🔴 {d['hospital_bottom10_title']}",
            export_filename=f"bottom10-{cu}.csv",
            footer_text=_dis_footer,
        )
    else:
        st.info(d["no_data"])

    st.markdown(
        "<hr style='margin:0.4rem 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )

    # --- B: Aandachtsaccounts (3,0★ - 4,0★) ---
    if data.hospital_attention:
        _render_sortable_table(
            pd.DataFrame(
                [
                    {
                        d["col_hospital"]: h.hospital,
                        d["col_score"]: f"{h.score:.2f}★",
                        d["col_tickets"]: str(h.tickets),
                    }
                    for h in data.hospital_attention
                ]
            ),
            title=f"🟡 {d['hospital_attention_title']}",
            export_filename=f"attention-{cu}.csv",
        )
    else:
        st.info(d["hospital_no_attention"])

    st.markdown(
        "<hr style='margin:1.5rem 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )

    # --- C: Top 10 (≥ 4,0★) ---
    if data.hospital_top10:
        _render_sortable_table(
            pd.DataFrame(
                [
                    {
                        d["col_hospital"]: h.hospital,
                        d["col_score"]: f"{h.score:.2f}★",
                        d["col_tickets"]: str(h.tickets),
                    }
                    for h in data.hospital_top10
                ]
            ),
            title=f"🟢 {d['hospital_top10_title']}",
            export_filename=f"top10-{cu}.csv",
            footer_text=d["hospital_top10_footnote"],
        )
    else:
        st.info(d["no_data"])

    # --- Geavanceerde tabellen (vereisen data.raw) ---
    if not data.raw:
        return

    raw = data.raw
    compared_to = d.get("compared_to_full", "t.o.v. volledig")
    col_h = d["col_hospital"]
    col_date = d.get("col_date", "Datum")  # generiek label voor E/F

    # Venster-aware ziekenhuisvergelijking (D + G)
    # Tendensvenster: S2 baseline-jaar als referentie i.p.v. volledig jaar
    _zh_venster = "tendens" if data.mode == "trend" else "volledig"
    _bl_label = f"S2 {data.current_year - 1}" if data.mode == "trend" else bl
    _hosp_comp = _windowed_hospital_comparison(data, _zh_venster)

    # Kolomlabels met jaar (venster-afhankelijk voor D + G)
    col_score_bl = f"Score {_bl_label}"
    col_tickets_bl = f"Tickets {_bl_label}"
    col_score_cu = f"Score {cu}"
    col_tickets_cu = f"Tickets {cu}"
    col_delta = "\u0394"  # Δ

    # --- D: Score-evolutie (grootste verschuivingen) ---
    st.markdown(
        "<hr style='margin:0.4rem 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )
    shifts_title = d.get("hospital_shifts_title", "Score-evolutie: grootste verschuivingen")
    hosp_both = [h for h in _hosp_comp if h.current_score is not None]
    if hosp_both:

        def _d_sort(hc: HospitalComparison) -> tuple:
            delta = (hc.current_score or 0.0) - hc.baseline_score
            return (
                -abs(delta),
                -(hc.current_score or 0.0),
                -hc.current_total,
                -hc.baseline_score,
            )

        hosp_d = sorted(hosp_both, key=_d_sort)
        df_d = pd.DataFrame(
            [
                {
                    col_h: hc.hospital,
                    col_score_bl: f"{hc.baseline_score:.2f}\u2605",
                    col_tickets_bl: hc.baseline_total,
                    col_score_cu: f"{hc.current_score or 0.0:.2f}\u2605",
                    col_tickets_cu: hc.current_total,
                    col_delta: (
                        f"+{(hc.current_score or 0.0) - hc.baseline_score:.2f}"
                        if (hc.current_score or 0.0) - hc.baseline_score >= 0
                        else f"{(hc.current_score or 0.0) - hc.baseline_score:.2f}"
                    ),
                }
                for hc in hosp_d
            ]
        )
        _render_sortable_table(
            df_d,
            title=f"\U0001f4ca {shifts_title}",
            delta_col=col_delta,
            export_filename=f"score-evolutie-{cu}.csv",
        )
    else:
        st.markdown(f"#### \U0001f4ca {shifts_title}")
        st.info(d.get("hospital_no_shifts", "Geen voldoende data voor verschuivingsanalyse."))

    # --- E + F: Verdwenen en nieuwe ziekenhuizen ---
    _render_migration_tables(
        raw, d, col_h, col_tickets_bl, col_tickets_cu, col_date, compared_to, bl, cu
    )

    # --- G: Volledig ziekenhuizenoverzicht ---
    st.markdown(
        "<hr style='margin:0.4rem 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )
    full_title = d.get("hospital_full_title", "Volledig ziekenhuizenoverzicht")
    n_full = len(_hosp_comp)

    def _g_sort(hc: HospitalComparison) -> tuple:
        cs = hc.current_score if hc.current_score is not None else -999.0
        return (
            -cs,
            -hc.current_total,
            -hc.baseline_score,
            -hc.baseline_total,
        )

    hosp_g = sorted(_hosp_comp, key=_g_sort)
    df_g = pd.DataFrame(
        [
            {
                col_h: hc.hospital,
                col_score_bl: f"{hc.baseline_score:.2f}\u2605",
                col_tickets_bl: hc.baseline_total,
                col_score_cu: (
                    f"{hc.current_score:.2f}\u2605" if hc.current_score is not None else "\u2014"
                ),
                col_tickets_cu: hc.current_total,
                col_delta: (
                    f"+{hc.current_score - hc.baseline_score:.2f}"
                    if hc.current_score is not None and hc.current_score - hc.baseline_score >= 0
                    else (
                        f"{hc.current_score - hc.baseline_score:.2f}"
                        if hc.current_score is not None
                        else "\u2014"
                    )
                ),
            }
            for hc in hosp_g
        ]
    )
    _render_sortable_table(
        df_g,
        title=f"\U0001f4cb {full_title} ({n_full})",
        delta_col=col_delta,
        max_body_height=16 * 36 + 62 + 8,
        export_filename=f"ziekenhuizen-volledig-{cu}.csv",
    )


def render_kpi_targets(  # noqa: C901
    df_huidig: pd.DataFrame,
    df_baseline: pd.DataFrame,
    lang: str,
) -> None:
    """
    KPI-Targets tabel (9 rijen) — HTML-rendering met footnote en info-banner.

    Versie x.y · 12/04/2026 — uitgebreid 7→9 rijen:
      Incident CSAT (rij 8), Critical Priority CSAT (rij 9),
      footnote Ziekenhuisretentie (rij 7), info-banner bijgewerkt.

    Venster-aware gedrag is NIET van toepassing: KPI-Targets toont altijd
    de volledige huidige periode vs baseline, ongeacht sidebar-instelling.

    Berekening rijen 1-7 is identiek aan evolution_analyser._calc_kpi_targets
    zodat de regressiewaarden (bv. HC-ratio 46,8% → 🔴 Kritiek) bewaard blijven.

    Args:
        df_huidig:   DataFrame volledig huidig jaar (YTD, niet venster-gefilterd).
        df_baseline: DataFrame volledig baseline jaar.
        lang:        "nl" of "fr".
    """
    t = load_translations(lang)
    d = t["dashboard"]
    kpi_names_i18n = t.get("evolution", {}).get("target_tracking", {}).get("kpi_names", {})
    status_i18n = t.get("evolution", {}).get("target_tracking", {})
    kt = t.get("kpi_targets", {})

    # --- Status-labels (i18n) ---
    status_map: dict[str, str] = {
        "op_schema": status_i18n.get("op_schema", "✅"),
        "aandacht": status_i18n.get("aandacht", "⚠️"),
        "kritiek": status_i18n.get("kritiek", "🔴"),
    }
    status_onbekend: str = kt.get("status_onbekend", "❓")
    status_lage_n: str = kt.get("status_lage_n", "⚠️")

    # --- Actie-teksten per KPI en status (hardcoded NL/FR — geen i18n) ---
    _actie: dict[str, dict[str, str]] = {
        "avg_score_min": {
            "kritiek_nl": "Escaleer naar Service Manager",
            "kritiek_fr": "Escalader au Service Manager",
            "aandacht_nl": "Monitor wekelijks",
            "aandacht_fr": "Suivi hebdomadaire",
        },
        "pct_positive_min": {
            "kritiek_nl": "Analyseer negatieve feedback",
            "kritiek_fr": "Analyser les retours négatifs",
            "aandacht_nl": "Verhoog opvolgingsfrequentie",
            "aandacht_fr": "Augmenter la fréquence de suivi",
        },
        "pct_negative_max": {
            "kritiek_nl": "Analyseer negatieve feedback",
            "kritiek_fr": "Analyser les retours négatifs",
            "aandacht_nl": "Verhoog opvolgingsfrequentie",
            "aandacht_fr": "Augmenter la fréquence de suivi",
        },
        "high_critical_max": {
            "kritiek_nl": "Review open prioritaire tickets",
            "kritiek_fr": "Réviser les tickets prioritaires ouverts",
            "aandacht_nl": "Bewaken via weekrapport",
            "aandacht_fr": "Surveiller via rapport hebdomadaire",
        },
    }

    def _actie_text(kpi_key: str, status_key: str) -> str:
        """Geef actietekst voor de gegeven KPI-sleutel en status. Leeg voor 'op_schema'."""
        if status_key not in ("kritiek", "aandacht"):
            return ""
        return _actie.get(kpi_key, {}).get(f"{status_key}_{lang}", "")

    # --- Status-logica (identiek aan evolution_analyser._calc_kpi_targets) ---
    def _status_key(current: float, target: float, higher: bool) -> str:
        if higher:
            if current >= target:
                return "op_schema"
            if current >= target * 0.9:
                return "aandacht"
            return "kritiek"
        else:
            if current <= target:
                return "op_schema"
            if current <= target * 1.1:
                return "aandacht"
            return "kritiek"

    # --- Berekenings-helpers (identiek aan evolution_analyser-logica) ---
    def _avg_score(df: pd.DataFrame) -> float:
        sc = df[df["score"].notna()]
        return round(float(sc["score"].mean()), 2) if not sc.empty else 0.0

    def _pct_scored(df: pd.DataFrame, *, lower: bool = False) -> float:
        sc = df[df["score"].notna()]
        if sc.empty:
            return 0.0
        condition = sc["score"] <= 2 if lower else sc["score"] >= 4
        return round(float(condition.sum() / len(sc) * 100), 1)

    def _resp_days(df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0
        created = pd.to_datetime(df["created"])
        sat = pd.to_datetime(df["satisfaction_date"])
        days = (sat - created).dt.days
        valid = days.dropna()
        valid = valid[valid >= 0]
        return round(float(valid.mean()), 1) if not valid.empty else 0.0

    def _hc_ratio(df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0
        total = len(df)
        hc = int(df["priority"].isin(HIGH_CRITICAL_PRIORITIES).sum())
        return round(hc / total * 100, 1) if total > 0 else 0.0

    def _pct_comment(df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0
        has_comment = df["comment"].fillna("").str.strip().str.len() > 0
        return round(has_comment.sum() / len(df) * 100, 1)

    def _retention(df_h: pd.DataFrame, df_b: pd.DataFrame) -> float:
        b_hosp = set(df_b["hospital"].dropna().unique()) if not df_b.empty else set()
        if not b_hosp:
            return 100.0
        c_hosp = set(df_h["hospital"].dropna().unique()) if not df_h.empty else set()
        disappeared = b_hosp - c_hosp
        return round((len(b_hosp) - len(disappeared)) / len(b_hosp) * 100, 1)

    # --- Format helpers (Belgisch decimaalformaat) ---
    def _fmt(v: float) -> str:
        return f"{v:.2f}".replace(".", ",")

    def _fmt_star(v: float) -> str:
        return f"{v:.2f}★".replace(".", ",")

    # --- Rijstructuur ---
    rows: list[dict] = []

    def _add_row(
        label: str,
        b_val: float,
        target: float,
        c_val: float,
        higher: bool,
        fmt_fn=_fmt,  # type: ignore[assignment]
        footnote: bool = False,
        kpi_key: str = "",
    ) -> None:
        sk = _status_key(c_val, target, higher)
        rows.append(
            {
                "label": label,
                "baseline": fmt_fn(b_val),
                "target": fmt_fn(target),
                "realisatie": fmt_fn(c_val),
                "status": status_map.get(sk, sk),
                "footnote": footnote,
                "actie": _actie_text(kpi_key, sk),
            }
        )

    # Rij 1 — Gem. CSAT-score (hoger=beter)
    _add_row(
        kpi_names_i18n.get("avg_score_min", "Gem. CSAT-score"),
        _avg_score(df_baseline),
        AVG_SCORE_MIN,
        _avg_score(df_huidig),
        higher=True,
        kpi_key="avg_score_min",
    )
    # Rij 2 — % Positief (hoger=beter)
    _add_row(
        kpi_names_i18n.get("pct_positive_min", "% Positief"),
        _pct_scored(df_baseline),
        PCT_POSITIVE_MIN,
        _pct_scored(df_huidig),
        higher=True,
        kpi_key="pct_positive_min",
    )
    # Rij 3 — % Negatief (lager=beter)
    _add_row(
        kpi_names_i18n.get("pct_negative_max", "% Negatief"),
        _pct_scored(df_baseline, lower=True),
        PCT_NEGATIVE_MAX,
        _pct_scored(df_huidig, lower=True),
        higher=False,
        kpi_key="pct_negative_max",
    )
    # Rij 4 — Gem. responstijd (lager=beter)
    _add_row(
        kpi_names_i18n.get("avg_response_days_max", "Gem. responstijd"),
        _resp_days(df_baseline),
        AVG_RESPONSE_DAYS_MAX,
        _resp_days(df_huidig),
        higher=False,
    )
    # Rij 5 — High/Critical-ratio (lager=beter)
    _add_row(
        kpi_names_i18n.get("high_critical_max", "High/Critical-ratio"),
        _hc_ratio(df_baseline),
        HIGH_CRITICAL_MAX,
        _hc_ratio(df_huidig),
        higher=False,
        kpi_key="high_critical_max",
    )
    # Rij 6 — % Met comment (hoger=beter)
    _add_row(
        kpi_names_i18n.get("pct_with_comment_min", "% Met comment"),
        _pct_comment(df_baseline),
        PCT_WITH_COMMENT_MIN,
        _pct_comment(df_huidig),
        higher=True,
    )
    # Rij 7 — Ziekenhuisretentie (hoger=beter) — footnote ¹
    # Baseline is altijd 100,0 (definitie: baseline behoudt 100% van zichzelf)
    _add_row(
        kpi_names_i18n.get("hospital_retention_min", "Ziekenhuisretentie"),
        100.0,
        HOSPITAL_RETENTION_MIN,
        _retention(df_huidig, df_baseline),
        higher=True,
        footnote=True,
    )

    # --- Rij 8 — Incident CSAT (hoger=beter) — edge case n=0 / n<5 ---
    _inc_target = AVG_SCORE_MIN  # >= 4,00★
    sub_inc_h = df_huidig[df_huidig["issue_type"] == "Incident"]["score"].dropna()
    sub_inc_b = df_baseline[df_baseline["issue_type"] == "Incident"]["score"].dropna()
    n_inc = len(sub_inc_h)
    b_inc = round(float(sub_inc_b.mean()), 2) if not sub_inc_b.empty else 0.0

    if n_inc == 0:
        real_inc = "n.b."
        stat_inc = status_onbekend
    elif n_inc < 5:
        v_inc = round(float(sub_inc_h.mean()), 2)
        real_inc = f"{v_inc:.2f}★ (n={n_inc})".replace(".", ",")
        sk_inc = _status_key(v_inc, _inc_target, higher=True)
        stat_inc = f"{status_lage_n} {status_map.get(sk_inc, sk_inc)}"
    else:
        v_inc = round(float(sub_inc_h.mean()), 2)
        real_inc = _fmt_star(v_inc)
        sk_inc = _status_key(v_inc, _inc_target, higher=True)
        stat_inc = status_map.get(sk_inc, sk_inc)

    rows.append(
        {
            "label": kt.get("rij_incident_csat_label", "Incident CSAT"),
            "baseline": _fmt_star(b_inc),
            "target": _fmt_star(_inc_target),
            "realisatie": real_inc,
            "status": stat_inc,
            "footnote": False,
            "actie": "",
        }
    )

    # --- Rij 9 — Critical Priority CSAT (hoger=beter) — edge case n=0 / n<5 ---
    # Gebruikt HIGH_CRITICAL_PRIORITIES uit pillars.py = ["Blocker","Critical","Major"]
    _cp_target = _CRITICAL_PRIORITY_CSAT_TARGET  # >= 4,50★
    sub_cp_h = df_huidig[df_huidig["priority"].isin(HIGH_CRITICAL_PRIORITIES)]["score"].dropna()
    sub_cp_b = df_baseline[df_baseline["priority"].isin(HIGH_CRITICAL_PRIORITIES)]["score"].dropna()
    n_cp = len(sub_cp_h)
    b_cp = round(float(sub_cp_b.mean()), 2) if not sub_cp_b.empty else 0.0

    if n_cp == 0:
        real_cp = "n.b."
        stat_cp = status_onbekend
    elif n_cp < 5:
        v_cp = round(float(sub_cp_h.mean()), 2)
        real_cp = f"{v_cp:.2f}★ (n={n_cp})".replace(".", ",")
        sk_cp = _status_key(v_cp, _cp_target, higher=True)
        stat_cp = f"{status_lage_n} {status_map.get(sk_cp, sk_cp)}"
    else:
        v_cp = round(float(sub_cp_h.mean()), 2)
        real_cp = _fmt_star(v_cp)
        sk_cp = _status_key(v_cp, _cp_target, higher=True)
        stat_cp = status_map.get(sk_cp, sk_cp)

    rows.append(
        {
            "label": kt.get("rij_critical_priority_csat_label", "Critical Priority CSAT"),
            "baseline": _fmt_star(b_cp),
            "target": _fmt_star(_cp_target),
            "realisatie": real_cp,
            "status": stat_cp,
            "footnote": False,
            "actie": "",
        }
    )

    # --- HTML-tabel ---
    _th_base = (
        f"background:{ZORGI_DARK_BLUE};color:#ffffff;"
        f"font-family:Poppins,Verdana,sans-serif;font-weight:800;"
        f"padding:6px 12px;text-align:left;font-size:0.82rem;white-space:nowrap;"
        f"overflow:hidden;text-overflow:ellipsis"
    )
    _td_base = (
        "font-family:Poppins,Verdana,sans-serif;padding:5px 12px;"
        "font-size:0.82rem;border-bottom:1px solid #e0e8f0;overflow:hidden;text-overflow:ellipsis"
    )
    _row_colors = ("#ffffff", ZORGI_ULTRA_LIGHT)
    _w = {
        "kpi": "28%",
        "val": "12%",
        "target": "12%",
        "real": "14%",
        "status": "14%",
        "actie": "20%",
    }

    col_kpi = d.get("col_kpi", "KPI")
    col_baseline_h = d.get("col_baseline", "Baseline")
    col_target_h = d.get("col_target", "Target")
    col_realization = d.get("col_realization", "Realisatie")
    col_status_h = d.get("col_status", "Status")
    col_actie_h = "Action" if lang == "fr" else "Actie"

    # --- CSV-downloadknop (HTML — zelfde stijl als _render_sortable_table, rechts uitgelijnd) ---
    _kt_csv_buf = io.StringIO()
    pd.DataFrame(
        [
            {
                col_kpi: r["label"],
                col_baseline_h: r["baseline"],
                col_target_h: r["target"],
                col_realization: r["realisatie"],
                col_status_h: r["status"],
                col_actie_h: r.get("actie", ""),
            }
            for r in rows
        ]
    ).to_csv(_kt_csv_buf, index=False)
    _kt_b64 = base64.b64encode(_kt_csv_buf.getvalue().encode()).decode()
    _kt_title = d.get("kpi_targets_table_title", d.get("kpi_targets_title", "KPI Targets"))
    _kt_header_html = (
        f"<div style='display:flex;justify-content:space-between;align-items:center;"
        f"margin-bottom:0'>"
        f"<h4 style='margin:0;font-size:24px;font-weight:600;color:#1A1A1A;"
        f'font-family:"Source Sans",sans-serif;line-height:1.3\'>'
        f"{html.escape(_kt_title)}</h4>"
        f"<a href='data:text/csv;base64,{_kt_b64}' download='kpi-targets-export.csv'"
        f" style='background:#003a70;color:#fff;padding:4px 14px;border-radius:4px;"
        f"font-size:0.78rem;font-family:Poppins,Verdana,sans-serif;white-space:nowrap;"
        f"text-decoration:none;display:inline-block'>📤 Export CSV</a>"
        f"</div>"
    )

    parts = [
        _kt_header_html,
        "<table style='width:100%;border-collapse:collapse;margin-top:0;table-layout:fixed'>",
        "<thead><tr>",
        f"<th style='{_th_base};width:{_w['kpi']}'>{html.escape(col_kpi)}</th>",
        f"<th style='{_th_base};width:{_w['val']}'>{html.escape(col_baseline_h)}</th>",
        f"<th style='{_th_base};width:{_w['target']}'>{html.escape(col_target_h)}</th>",
        f"<th style='{_th_base};width:{_w['real']}'>{html.escape(col_realization)}</th>",
        f"<th style='{_th_base};width:{_w['status']}'>{html.escape(col_status_h)}</th>",
        f"<th style='{_th_base};width:{_w['actie']}'>{html.escape(col_actie_h)}</th>",
        "</tr></thead><tbody>",
    ]

    for i, r in enumerate(rows):
        bg = _row_colors[i % 2]
        _td = f"{_td_base};background:{bg}"
        label_html = html.escape(r["label"])
        if r["footnote"]:
            label_html += "<sup style='color:#5f8495;font-size:0.7em;margin-left:2px'>¹</sup>"
        parts += [
            "<tr>",
            f"<td style='{_td}'>{label_html}</td>",
            f"<td style='{_td}'>{html.escape(r['baseline'])}</td>",
            f"<td style='{_td}'>{html.escape(r['target'])}</td>",
            f"<td style='{_td}'>{html.escape(r['realisatie'])}</td>",
            f"<td style='{_td}'>{html.escape(r['status'])}</td>",
            f"<td style='{_td}'>{html.escape(r.get('actie', ''))}</td>",
            "</tr>",
        ]

    parts.append("</tbody></table>")
    st.markdown("\n".join(parts), unsafe_allow_html=True)

    # --- Footnote ¹ (Ziekenhuisretentie) ---
    _fn_text = kt.get("footnote_ziekenhuisretentie", "")
    if _fn_text:
        st.markdown(
            f"<div style='font-size:0.85em;color:#5f8495;margin-top:0.4rem;line-height:1.5'>"
            f"<sup>¹</sup>&nbsp;{html.escape(_fn_text)}"
            f"</div>",
            unsafe_allow_html=True,
        )

    # --- Info-banner (bijgestelde targets) ---
    _banner_text = kt.get("banner_bijgestelde_targets", "")
    if _banner_text:
        st.markdown(
            f"<div style='background:#d7e7f3;border-radius:6px;padding:0.7rem 1rem;"
            f"margin-top:0.8rem;color:{ZORGI_DARK_BLUE};"
            f"font-family:Poppins,Verdana,sans-serif;font-size:0.85rem;line-height:1.5'>"
            f"💡&nbsp;{html.escape(_banner_text)}"
            f"</div>",
            unsafe_allow_html=True,
        )


def _tab_targets(data: DashboardData, t: dict, lang: str) -> None:
    """Tab 6 — KPI Targets: grouped bar chart + 9-rijen overzichtstabel + info-banner."""
    d = t["dashboard"]

    st.markdown(f"#### {d['kpi_targets_title']}")

    if data.kpi_targets:
        st.plotly_chart(_chart_kpi_targets_h(data, t), width="stretch")

    # KPI-Targets is altijd "volledig" — venster-modus mag deze aanroep NIET beïnvloeden.
    # Toekomstige refactoring van _make_kc_dataframes mag deze invariant niet breken.
    # Zie ook: visuele invariant-test in acceptatiecriteria Prompt B-bis.
    df_kpi_vorig, df_kpi_huidig = _make_kc_dataframes(data, "volledig")
    render_kpi_targets(df_kpi_huidig, df_kpi_vorig, lang)


# ---------------------------------------------------------------------------
# DEV-tabblad — tijdelijk ontwikkeltabblad Tickets & Prioriteit (Fase 5a)
# ---------------------------------------------------------------------------


def _build_issue_type_chart(df_comparison, chart_title: str = "", prev_label: str = "2025"):
    """Horizontale bar chart voor issue type vergelijking — Plotly/ZORGI-stijl."""
    import math

    color_ok = ZORGI_FUNC_POSITIVE
    color_bad = ZORGI_RED
    color_neutral = ZORGI_DARK_BLUE
    color_prev = "#A7B4C1"  # lichtgrijs voor baseline-balk
    df_sorted = df_comparison.sort_values(
        "issue_type", ascending=True, na_position="last"
    ).reset_index(drop=True)
    types = df_sorted["issue_type"].tolist()
    scores_prev = df_sorted["score_prev"].tolist()
    scores_curr = df_sorted["score_curr"].tolist()
    counts_prev = (
        df_sorted["count_prev"].tolist() if "count_prev" in df_sorted.columns else [0] * len(types)
    )
    counts_curr = (
        df_sorted["count_curr"].tolist() if "count_curr" in df_sorted.columns else [0] * len(types)
    )
    n = len(types)
    _bar_w = 0.35  # iets kleiner van 0.40 → 0.35
    ytd_colors = []
    for sp, sc in zip(scores_prev, scores_curr, strict=False):
        if not math.isnan(sc) and not math.isnan(sp):
            ytd_colors.append(color_ok if sc >= sp else color_bad)
        else:
            ytd_colors.append(color_neutral)
    all_sc = [s for s in scores_prev + scores_curr if not math.isnan(s)]
    x_max = round(max(all_sc) + 0.3, 1) if all_sc else 5.5
    x_min = max(0.0, round(min(all_sc) - 0.3, 1)) if all_sc else 0.0

    def _score_text(v):
        return f"\u00a0\u00a0{v:.2f}\u2605" if not math.isnan(v) else ""

    fig = go.Figure()
    # 2025-balk — lichtgrijs, score buiten
    fig.add_trace(
        go.Bar(
            name=prev_label,
            y=types,
            x=scores_prev,
            orientation="h",
            marker_color=color_prev,
            text=[_score_text(v) for v in scores_prev],
            textposition="outside",
            textfont={"size": 9, "color": "#444444"},
            width=_bar_w,
            offset=-_bar_w,
            hovertemplate=f"%{{y}} {prev_label}: %{{x:.2f}}\u2605<extra></extra>",
        )
    )
    # YTD-balk — gekleurde bars, score buiten
    fig.add_trace(
        go.Bar(
            name="YTD",
            y=types,
            x=scores_curr,
            orientation="h",
            marker_color=ytd_colors,
            text=[_score_text(v) for v in scores_curr],
            textposition="outside",
            textfont={"size": 9, "color": "#444444"},
            width=_bar_w,
            offset=0.0,
            showlegend=False,
            hovertemplate="%{y} YTD: %{x:.2f}\u2605<extra></extra>",
        )
    )
    # Legenda-dummies
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={"symbol": "square", "size": 12, "color": color_ok},
            name="YTD (verbetering)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={"symbol": "square", "size": 12, "color": color_bad},
            name="YTD (verslechtering)",
        )
    )
    # 6. Ticketaantallen binnenin via annotaties — wit
    for t_name, vp, cp, vc, cc in zip(
        types, scores_prev, counts_prev, scores_curr, counts_curr, strict=False
    ):
        if not math.isnan(vp) and cp > 0:
            fig.add_annotation(
                x=x_min + 0.03,
                y=t_name,
                text=f"{int(cp)} t",
                showarrow=False,
                xanchor="left",
                font={"size": 10, "color": "#ffffff"},
                yshift=10,
            )
        if not math.isnan(vc) and cc > 0:
            fig.add_annotation(
                x=x_min + 0.03,
                y=t_name,
                text=f"{int(cc)} t",
                showarrow=False,
                xanchor="left",
                font={"size": 10, "color": "#ffffff"},
                yshift=-10,
            )
    # 4+5. Legenda bottom = top datasectie; modebar right = datasectie right
    _title_cfg = (
        {
            "text": f"<b>{chart_title}</b>",
            "font": {
                "size": 24,
                "family": "'Source Sans', 'Source Sans Pro', 'Source Sans 3', sans-serif",
                "color": "#1A1A1A",
            },
            "x": 0,
            "xanchor": "left",
            "xref": "paper",
            "pad": {"l": 0, "b": 4},
        }
        if chart_title
        else ""
    )
    _margin_t = 64 if chart_title else 50
    fig.update_layout(
        title=_title_cfg,
        barmode="overlay",
        xaxis={
            "title": "",
            "range": [x_min, x_max],
            "gridcolor": "#edf2f7",
            "ticksuffix": "\u2605",
            "tickformat": ".1f",
        },
        yaxis={"title": "", "autorange": "reversed"},
        height=max(250, n * 72 + 80),
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.04,
            "xanchor": "center",
            "x": 0.5,
            "itemsizing": "constant",
        },
        margin={"t": _margin_t, "b": 10, "r": 0},
        modebar_remove=["pan2d", "autoScale2d"],
    )
    return apply_plotly_theme(fig)


def _build_priority_chart(df_comparison, prev_label: str = "2025"):
    """Horizontale Plotly grouped bar chart voor prioriteit vergelijking."""
    import math

    priority_order = ["Blocker", "Critical", "Major", "Minor", "Trivial"]
    color_ok = ZORGI_FUNC_POSITIVE
    color_bad = ZORGI_RED
    color_neutral = ZORGI_DARK_BLUE
    color_prev = "#A7B4C1"
    _bar_w = 0.35

    df_sorted = df_comparison.set_index("priority").reindex(priority_order).reset_index()
    df_sorted = df_sorted[::-1].reset_index(drop=True)

    priorities = df_sorted["priority"].tolist()
    scores_prev = df_sorted["score_prev"].tolist()
    scores_curr = df_sorted["score_curr"].tolist()
    counts_prev = (
        df_sorted["count_prev"].tolist()
        if "count_prev" in df_sorted.columns
        else [0] * len(priorities)
    )
    counts_curr = (
        df_sorted["count_curr"].tolist()
        if "count_curr" in df_sorted.columns
        else [0] * len(priorities)
    )
    n = len(priorities)

    ytd_colors = []
    for sp, sc in zip(scores_prev, scores_curr, strict=False):
        if not math.isnan(sc) and not math.isnan(sp):
            ytd_colors.append(color_ok if sc >= sp else color_bad)
        else:
            ytd_colors.append(color_neutral)

    all_sc = [s for s in scores_prev + scores_curr if not math.isnan(s)]
    x_max = round(max(all_sc) + 0.3, 1) if all_sc else 5.5
    x_min = max(0.0, round(min(all_sc) - 0.3, 1)) if all_sc else 0.0

    def _score_text(v):
        return f"\u00a0\u00a0{v:.2f}\u2605" if not math.isnan(v) else ""

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name=prev_label,
            y=priorities,
            x=scores_prev,
            orientation="h",
            marker_color=color_prev,
            text=[_score_text(v) for v in scores_prev],
            textposition="outside",
            textfont={"size": 9, "color": "#444444"},
            width=_bar_w,
            offset=-_bar_w,
            hovertemplate=f"%{{y}} {prev_label}: %{{x:.2f}}\u2605<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="YTD",
            y=priorities,
            x=scores_curr,
            orientation="h",
            marker_color=ytd_colors,
            text=[_score_text(v) for v in scores_curr],
            textposition="outside",
            textfont={"size": 9, "color": "#444444"},
            width=_bar_w,
            offset=0.0,
            showlegend=False,
            hovertemplate="%{y} YTD: %{x:.2f}\u2605<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={"symbol": "square", "size": 12, "color": color_ok},
            name="YTD (verbetering)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={"symbol": "square", "size": 12, "color": color_bad},
            name="YTD (verslechtering)",
        )
    )

    for p_name, vp, cp, vc, cc in zip(
        priorities, scores_prev, counts_prev, scores_curr, counts_curr, strict=False
    ):
        if not math.isnan(vp) and cp > 0:
            fig.add_annotation(
                x=x_min + 0.03,
                y=p_name,
                text=f"{int(cp)} t",
                showarrow=False,
                xanchor="left",
                font={"size": 10, "color": "#ffffff"},
                yshift=-10,
            )
        if not math.isnan(vc) and cc > 0:
            fig.add_annotation(
                x=x_min + 0.03,
                y=p_name,
                text=f"{int(cc)} t",
                showarrow=False,
                xanchor="left",
                font={"size": 10, "color": "#ffffff"},
                yshift=10,
            )

    fig.update_layout(
        title="",
        barmode="overlay",
        xaxis={
            "title": "",
            "range": [x_min, x_max],
            "gridcolor": "#edf2f7",
            "ticksuffix": "\u2605",
            "tickformat": ".1f",
        },
        yaxis={"title": "", "autorange": "reversed"},
        height=max(250, n * 72 + 80),
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.04,
            "xanchor": "center",
            "x": 0.5,
            "itemsizing": "constant",
        },
        margin={"t": 50, "b": 10, "r": 0},
        modebar_remove=["pan2d", "autoScale2d"],
    )
    return apply_plotly_theme(fig)


def _render_feedback_themas(themas: list, lang: str) -> None:
    """Rendert feedbackthema's als lichtblauwe kaartjes, of een caption bij lege lijst."""

    def _ls(nl: str, fr: str) -> str:
        return fr if lang == "fr" else nl

    if themas:
        for thema in themas:
            if isinstance(thema, dict):
                naam = thema.get("naam") or thema.get("name", "\u2014")
                beschrijving = thema.get("beschrijving") or thema.get("description", "")
            elif hasattr(thema, "naam"):
                naam = str(thema.naam)
                beschrijving = str(getattr(thema, "beschrijving", ""))
            elif hasattr(thema, "name"):
                naam = str(thema.name)
                beschrijving = str(getattr(thema, "description", str(thema)))
            else:
                naam = str(thema)
                beschrijving = ""

            st.markdown(
                f'<div style="border-left:3px solid #609FCE;'
                f"background:#E8F4FB;border-radius:0 8px 8px 0;"
                f'padding:8px 14px;margin-bottom:8px;">'
                f'<strong style="color:#003A70;">{naam}</strong>'
                + (
                    f'<br><span style="font-size:13px;color:#5F8495;">{beschrijving}</span>'
                    if beschrijving
                    else ""
                )
                + "</div>",
                unsafe_allow_html=True,
            )
    else:
        st.caption(
            _ls(
                "Geen feedbackthema\u2019s beschikbaar voor deze periode.",
                "Aucun th\u00e8me de feedback disponible pour cette p\u00e9riode.",
            )
        )


def render_tab_tickets_prioriteit(
    df: pd.DataFrame,
    lang: str,
    mode: str = "full",
    baseline_year: int | None = None,
    current_year: int | None = None,
    current_month: int | None = None,
    trend_start_month: int = 7,
) -> None:
    """DEV-tabblad Tickets & Prioriteit — werk in uitvoering.

    Args:
        df:                 Volledig (ongefilterd op datum) CSAT DataFrame voor de pijler.
        lang:               Taalcode ("nl" of "fr").
        mode:               Venstermodus — "full" of "trend" (uitbreidbaar).
        baseline_year:      Referentiejaar (bv. 2025).
        current_year:       Huidig jaar (bv. 2026).
        current_month:      Laatste afgeronde maand (1-12).
        trend_start_month:  Startmaand tendens-modus (standaard 7 = S2 = juli).
    """
    import math  # noqa: F401

    from csat.core.calculations import calc_hero_metrics_tickets, calc_issue_type_comparison

    def _ls(nl: str, fr: str) -> str:
        return fr if lang == "fr" else nl

    # Dynamisch label voor de referentieperiode (afhankelijk van venstermodus)
    _bl_yr = baseline_year or (datetime.now(tz=UTC).year - 1)
    _prev_label = f"S2 {_bl_yr}" if mode == "trend" else str(_bl_yr)
    metrics = calc_hero_metrics_tickets(
        df,
        mode=mode,
        baseline_year=baseline_year,
        current_year=current_year,
        current_month=current_month,
        trend_start_month=trend_start_month,
    )
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric(
        label="Meest voorkomend type",
        value=metrics["most_common_type"],
        delta=f"{metrics['most_common_type_pct']}% van alle tickets",
    )
    col_b.metric(
        label=_ls("Laagst scorend type", "Type avec le score le plus bas"),
        value=metrics["lowest_score_type"],
        delta=f"{metrics['lowest_score_type_value']}\u2605 \u2014 {_ls('laagste', 'le plus bas')}",
        delta_color="inverse",
    )
    col_c.metric(
        label=_ls("Grootste prioritaire groep", "Groupe prioritaire le plus grand"),
        value=metrics["largest_priority_group"],
        delta=(
            f"{metrics['largest_priority_pct']}% tickets"
            f" \u00b7 {metrics['largest_priority_neg_pct']}% {_ls('neg.', 'nég.')}"
        ),
    )
    kpi_ok = metrics["high_critical_ok"]
    _margin = str(abs(metrics["high_critical_margin"])).replace(".", ",")
    col_d.metric(
        label="% High/Critical (KPI \u226415%)",
        value=f"{metrics['high_critical_pct']}%",
        delta=_ls(
            f"{_margin}% onder target" if kpi_ok else f"{_margin}% boven target",
            f"{_margin}% sous l'objectif" if kpi_ok else f"{_margin}% au-dessus de l'objectif",
        ),
        delta_color="normal" if kpi_ok else "inverse",
    )
    st.divider()
    _cur_year = datetime.now(tz=UTC).year
    _type_d_issue = "Type d\u2019issue"
    st.markdown(
        f"<h4 style='margin:0 0 0 0;font-size:24px;font-weight:700;color:#1A1A1A;"
        f'font-family:"Source Sans","Source Sans Pro","Source Sans 3",sans-serif;'
        f"line-height:1.3;'>"
        f"{_ls('Issue type', _type_d_issue)} \u2014 {_ls('vergelijking', 'comparaison')} {_cur_year}</h4>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-top:-1rem'></div>", unsafe_allow_html=True)
    df_issue = calc_issue_type_comparison(
        df,
        mode=mode,
        baseline_year=baseline_year,
        current_year=current_year,
        current_month=current_month,
        trend_start_month=trend_start_month,
    )
    st.plotly_chart(
        _build_issue_type_chart(df_issue, chart_title="", prev_label=_prev_label),
        width="stretch",
        config=_CHART_CONFIG,
    )
    st.markdown(
        "<hr style='margin:0.4rem 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )
    # Sorteerbare detailtabel — 1cm onder de scheidingslijn geplaatst
    st.markdown(
        "<div style='margin-top:-1cm;height:0;overflow:hidden'></div>",
        unsafe_allow_html=True,
    )
    import math as _math

    def _fstar(v):
        return f"{v:.2f}\u2605" if not _math.isnan(v) else "\u2014"

    def _fpct(v):
        return f"{v:.1f}%" if not _math.isnan(v) else "\u2014"

    def _fdelta_s(v):
        return f"{v:+.2f}\u2605" if not _math.isnan(v) else "\u2014"

    def _fdelta_n(v):
        return f"{v:+.1f} ppt" if not _math.isnan(v) else "\u2014"

    df_tbl = pd.DataFrame(
        [
            {
                _ls("Type", "Type"): str(r["issue_type"]),
                f"Score {_prev_label}": _fstar(r["score_prev"]),
                "Score YTD": _fstar(r["score_curr"]),
                _ls("% Negatief", "% Négatif"): _fpct(r["pct_neg_curr"]),
                "\u0394 Score": _fdelta_s(r["delta_score"]),
                _ls("\u0394 Negatief", "\u0394 Négatif"): _fdelta_n(r["delta_neg"]),
            }
            for _, r in df_issue.iterrows()
        ]
    )
    _render_sortable_table(
        df_tbl,
        title=_ls(
            "\U0001f4cb Score per issue type \u2014 detail",
            "\U0001f4cb Score par type d\u2019issue \u2014 détail",
        ),
        show_title=True,
        delta_col="\u0394 Score",
        export_filename="issue_type_vergelijking.csv",
        col_widths=["32%", "13%", "13%", "11%", "11%", "13%"],
    )
    _col_neg = _ls("% Negatief", "% Négatif")
    _col_dneg = _ls("\u0394 Negatief", "\u0394 Négatif")
    st.markdown(
        "<div style='font-size:0.80rem;color:#5f8495;margin-top:-2.5rem;line-height:1.6;"
        "padding:0.35rem 0 0.35rem 0;'>"
        f"<b style='color:#3a5a7a'>{_col_neg}</b>: "
        + _ls(
            "aandeel tickets met score \u22642\u2605 in YTD",
            "part des tickets avec score \u22642\u2605 en cumul",
        )
        + "<br>"
        f"<b style='color:#3a5a7a'>{_col_dneg}</b>: "
        + _ls(
            f"verschil t.o.v. {_prev_label} in procentpunten, een negatieve waarde betekent verbetering (minder negatieve scores)",
            f"différence par rapport à {_prev_label} en points de pourcentage, une valeur négative signifie une amélioration",
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    # Insight-box issue type
    from csat.core.insights.insights_generator import InsightsGenerator

    _i18n = load_translations(lang)
    _ig = InsightsGenerator(i18n=_i18n, lang=lang)
    _insight_issue = _ig._generate_issue_type_insight(df_issue)
    st.markdown(
        f'<div style="background:#FEF5E7;border:1px solid rgba(230,126,34,0.3);'
        f'border-radius:8px;padding:10px 14px;margin-top:8px;font-size:13px;">'
        f'<strong style="color:#E67E22;">⚠ </strong>{_insight_issue}'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Blok 2b: Prioriteit vergelijking ──────────────────────────────────
    from csat.core.calculations import calc_priority_comparison

    st.markdown(
        f"<h4 style='margin:0 0 0 0;font-size:24px;font-weight:700;color:#1A1A1A;"
        f'font-family:"Source Sans","Source Sans Pro","Source Sans 3",sans-serif;'
        f"line-height:1.3;'>"
        f"{_ls('Prioriteit', 'Priorité')} \u2014 {_ls('vergelijking', 'comparaison')} {datetime.now(tz=UTC).year}</h4>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-top:-1rem'></div>", unsafe_allow_html=True)
    df_prio = calc_priority_comparison(
        df,
        mode=mode,
        baseline_year=baseline_year,
        current_year=current_year,
        current_month=current_month,
        trend_start_month=trend_start_month,
    )
    st.plotly_chart(
        _build_priority_chart(df_prio, prev_label=_prev_label),
        width="stretch",
        config=_CHART_CONFIG,
    )
    st.markdown(
        "<hr style='margin:0.4rem 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='margin-top:-1cm;height:0;overflow:hidden'></div>", unsafe_allow_html=True
    )
    _col_prio = _ls("Prioriteit", "Priorité")
    _col_neg_p = _ls("% Negatief", "% Négatif")
    _col_dneg_p = _ls("\u0394 Negatief", "\u0394 Négatif")
    df_prio_tbl = pd.DataFrame(
        [
            {
                _col_prio: str(r["priority"]),
                f"Score {_prev_label}": _fstar(r["score_prev"]),
                "Score YTD": _fstar(r["score_curr"]),
                _col_neg_p: _fpct(r["pct_neg_curr"]),
                "\u0394 Score": _fdelta_s(r["delta_score"]),
                _col_dneg_p: _fdelta_n(r["delta_neg"]),
            }
            for _, r in df_prio.iterrows()
        ]
    )
    _render_sortable_table(
        df_prio_tbl,
        title=_ls(
            "\U0001f4cb Score per prioriteit \u2014 detail",
            "\U0001f4cb Score par priorité \u2014 détail",
        ),
        show_title=True,
        delta_col="\u0394 Score",
        export_filename="prioriteit_vergelijking.csv",
        col_widths=["28%", "14%", "13%", "11%", "11%", "13%"],
    )
    st.markdown(
        "<div style='font-size:0.80rem;color:#5f8495;margin-top:-2.5rem;line-height:1.6;"
        "padding:0.35rem 0 0.35rem 0;'>"
        f"<b style='color:#3a5a7a'>{_col_neg_p}</b>: "
        + _ls(
            "aandeel tickets met score \u22642\u2605 in YTD",
            "part des tickets avec score \u22642\u2605 en cumul",
        )
        + "<br>"
        f"<b style='color:#3a5a7a'>{_col_dneg_p}</b>: "
        + _ls(
            f"verschil t.o.v. {_prev_label} in procentpunten, een negatieve waarde betekent verbetering (minder negatieve scores)",
            f"différence par rapport à {_prev_label} en points de pourcentage, une valeur négative signifie une amélioration",
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    # Insight-box prioriteit — zelfde stijl als issue type
    _insight_prio = _ig._generate_priority_insight(df_prio)
    st.markdown(
        f'<div style="background:#FEF5E7;border:1px solid rgba(230,126,34,0.3);'
        f'border-radius:8px;padding:10px 14px;margin-top:8px;font-size:13px;">'
        f'<strong style="color:#E67E22;">⚠ </strong>{_insight_prio}'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Blok 3: Feedbackthema's ───────────────────────────────────────────
    _thema_titel_nl = "🎯 Feedbackthema\u2019s \u2014 actiegericht"
    _thema_titel_fr = "🎯 Th\u00e8mes de feedback \u2014 orient\u00e9s action"
    st.markdown(
        f"<h4 style='margin:0 0 0 0;font-size:24px;font-weight:700;color:#1A1A1A;"
        f'font-family:"Source Sans","Source Sans Pro","Source Sans 3",sans-serif;'
        f"line-height:1.3;'>"
        f"{_ls(_thema_titel_nl, _thema_titel_fr)}</h4>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-top:-1rem'></div>", unsafe_allow_html=True)

    _themas = _ig._generate_feedback_themes(df)
    _render_feedback_themas(_themas, lang)

    st.markdown(
        "<div style='border-top:1px solid #D0DAE3;margin-top:2.0rem;'></div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Coming soon placeholder (niet-PHARMA pijlers)
# ---------------------------------------------------------------------------


def _render_coming_soon(t: dict, pillar_name: str) -> None:
    """Toon een 'Coming soon' placeholder voor pijlers zonder data in Fase 5a."""
    d = t["dashboard"]
    st.markdown(
        f"<div style='text-align:center;padding:3rem'>"
        f"<h2>⏳ {pillar_name}</h2>"
        f"<p style='font-size:1.2rem;color:{ZORGI_GREY_BLUE}'>{d['coming_soon']}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:  # noqa: C901
    """Streamlit entry point — configureert de pagina en rendert het volledige dashboard."""
    st.set_page_config(
        page_title="CSAT-Compass",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Session state initialiseren
    if "lang" not in st.session_state:
        st.session_state["lang"] = "nl"
    if "selected_pillar" not in st.session_state:
        st.session_state["selected_pillar"] = "pharma" if not DASHBOARD_PROD_MODE else "zorgi"
    if "selected_mode_key" not in st.session_state:
        st.session_state["selected_mode_key"] = "full"

    # Vertalingen laden (op basis van huidige session lang)
    lang = st.session_state["lang"]
    t = load_translations(lang)
    d = t["dashboard"]

    # ZORGI CSS injecteren (alleen styles — blokkeert niet)
    inject_css(st, prod_mode=DASHBOARD_PROD_MODE)

    # Datum voor topbalk (Belgisch formaat DD/MM/YYYY)
    # PROD-modus: enkel datum — DEMO-modus: datum + uur
    today = datetime.now(tz=UTC).date()
    if DASHBOARD_PROD_MODE:
        today_str = today.strftime("%d/%m/%Y")
    else:
        now_full = datetime.now(tz=UTC)
        today_str = now_full.strftime("%d/%m/%Y · %H:%M")

    # Placeholder voor topbalk — direct zichtbaar, pijlerinfo volgt na dataladen
    _topbar = st.empty()
    render_topbar(_topbar, today_str, prod_mode=DASHBOARD_PROD_MODE, version=_APP_VERSION)

    # Sidebar
    last_year, last_month = _last_complete_period(today)
    # Laad ruwe data vroeg (gecached — instant bij herrender) zodat de sidebar
    # de ziekenhuislijst kan tonen in het filter-multiselect.
    _df_raw = _load_df()
    selected_pillar, window_start, lang, selected_hospitals = _render_sidebar(
        t, today, last_year, last_month, df=_df_raw
    )

    # Niet-PHARMA pijlers → Coming soon
    if selected_pillar not in _ACTIVE_PILLARS:
        pillar_name = PILLAR_REGISTRY[selected_pillar].get("report_name", selected_pillar)
        render_topbar(
            _topbar,
            today_str,
            prod_mode=DASHBOARD_PROD_MODE,
            pillar_name=pillar_name,
            version=_APP_VERSION,
        )
        _render_coming_soon(t, pillar_name)
        # Sidebar-toggle knop (NA content — blokkeert rendering niet)
        inject_sidebar_toggle()
        return

    # PHARMA data laden en analyseren
    with st.spinner("Data laden…"):
        try:
            if selected_hospitals:
                # Ziekenhuisfilter actief → gefilterde df, niet gecached
                _df_filtered = _df_raw[_df_raw["hospital"].isin(selected_hospitals)]
                result = _run_analysis_on_df(
                    _df_filtered,
                    baseline_year=_BASELINE_YEAR,
                    current_year=last_year,
                    current_month=last_month,
                    pillar=selected_pillar,
                )
            else:
                # Geen filter → gecachede analyse op volledige dataset
                result = _run_analysis(
                    baseline_year=_BASELINE_YEAR,
                    current_year=last_year,
                    current_month=last_month,
                    pillar=selected_pillar,
                )
        except Exception as exc:  # noqa: BLE001
            st.error(f"❌ Data laden mislukt: {exc}")
            return

    # Dashboard-data voorbereiden (snel, niet gecached)
    data = DashboardExporter.prepare(result, window_start)

    # Topbar bijwerken met pijler- en periodeinfo
    _cur_label = period_label(f"{last_year}-{last_month:02d}", lang=lang)
    _full_start = period_label(f"{_BASELINE_YEAR}-01", lang=lang)
    _trend_start = period_label(_TREND_WINDOW_START[:7], lang=lang)
    full_window = f"{d['mode_full']} · {_full_start} → {_cur_label}"
    trend_window = f"{d['mode_trend']} · {_trend_start} → {_cur_label}"
    _active_window = trend_window if data.mode == "trend" else full_window
    render_topbar(
        _topbar,
        today_str,
        prod_mode=DASHBOARD_PROD_MODE,
        pillar_name=data.pillar_name,
        version=_APP_VERSION,
        full_window_label=_active_window,
        trend_window_label="",
    )

    # 6 tabs
    _tab_labels = [
        d["tab_summary"],
        d["tab_timeline"],
        d["tab_tickets"],
        d["tab_response"],
        d["tab_hospitals"],
        d["tab_targets"],
    ]

    def _save_active_tab() -> None:
        """Bewaar actieve tab-index (taalwissel-bestendig) bij elke tabbladwissel."""
        selected = st.session_state.get("zorgi_tabs", _tab_labels[0])
        if selected in _tab_labels:
            st.session_state["_zorgi_tab_idx"] = _tab_labels.index(selected)

    _tab_idx = max(0, min(len(_tab_labels) - 1, st.session_state.get("_zorgi_tab_idx", 0)))
    _default_tab = st.session_state.get("zorgi_tabs", _tab_labels[_tab_idx])
    if _default_tab not in _tab_labels:
        _default_tab = _tab_labels[_tab_idx]

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        _tab_labels,
        key="zorgi_tabs",
        default=_default_tab,
        on_change=_save_active_tab,
    )

    with tab1:
        _tab_summary(data, t, lang)
    with tab2:
        _tab_timeline(data, t, lang)
    with tab3:
        _dev_products = PILLAR_REGISTRY.get(selected_pillar, {}).get("products", [])
        # Gebruik gefilterde df als ziekenhuisfilter actief is
        _df_dev = (
            _df_raw[_df_raw["hospital"].isin(selected_hospitals)]
            if selected_hospitals
            else _load_df()
        )
        _df_dev = _df_dev[_df_dev[FILTER_COLUMN].isin(_dev_products)]
        _dev_mode = "trend" if data.mode == "trend" else "full"
        _dev_trend_start = int(_TREND_WINDOW_START[5:7])  # "2025-07-01" → 7
        render_tab_tickets_prioriteit(
            _df_dev,
            lang,
            mode=_dev_mode,
            baseline_year=_BASELINE_YEAR,
            current_year=last_year,
            current_month=last_month,
            trend_start_month=_dev_trend_start,
        )
    with tab4:
        _tab_response(data, t, lang)
    with tab5:
        _tab_hospitals(data, t, lang)
    with tab6:
        _tab_targets(data, t, lang)

    # Scroll-reset bij tabbladwissel: altijd naar boven bij activeren nieuw tabblad
    inject_tab_scroll_reset()
    inject_iframe_resize()

    # Sidebar-toggle knop injecteren (NA alle content — blokkeert rendering niet)
    inject_sidebar_toggle()


if __name__ == "__main__":
    main()
