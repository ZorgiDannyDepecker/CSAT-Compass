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

import html
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Zorg dat src/ op het Python-pad staat bij directe streamlit-run
_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from csat import __version__  # noqa: E402
from csat.config.pillars import PILLAR_REGISTRY  # noqa: E402
from csat.config.settings import (  # noqa: E402
    CSV_FALLBACK_PATH,
    DASHBOARD_PROD_MODE,
    DB_CONN,
    db_available,
)
from csat.core.analysers.evolution_analyser import EvolutionAnalyser  # noqa: E402
from csat.core.analysers.evolution_result import EvolutionResult  # noqa: E402
from csat.core.exporters.dashboard_exporter import DashboardData, DashboardExporter  # noqa: E402
from csat.core.loaders import get_loader  # noqa: E402
from csat.i18n import load_translations  # noqa: E402
from csat.utils.branding import (  # noqa: E402
    apply_plotly_theme,
    inject_css,
    inject_sidebar_toggle,
    inject_tab_font_css,
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
_ACTIVE_PILLARS: frozenset[str] = frozenset({"pharma"})
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


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------


def _render_sidebar(
    t: dict, today: date, last_year: int, last_month: int
) -> tuple[str, str | None, str]:
    """
    Render de sidebar en geef (pillar_key, window_start, lang) terug.

    window_start is None voor Volledig venster, "2025-07-01" voor Tendensvenster.
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
        for k in pillar_options:
            if k == "zorgi":
                status = "✅" if k in _ACTIVE_PILLARS else "⏳"
                pillar_labels[k] = f"ZORGI {status}"
            else:
                status = "✅" if k in _ACTIVE_PILLARS else "⏳"
                pillar_labels[k] = f"{PILLAR_REGISTRY[k]['name']} {status}"
        # Herstel geselecteerde pijler uit session_state (bewaard bij taalwissel)
        _saved_pillar = st.session_state.get("selected_pillar", "zorgi")
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
        mode_full = d["mode_full"]
        mode_trend = d["mode_trend"]
        _tip_full = d.get("mode_full_help", "")
        _tip_trend = d.get("mode_trend_help", "")
        _colon = d.get("colon", ":")
        # HTML-escape voor veilige injectie (emoji's zijn veilig, < > & " wél escapen)
        _label_h = html.escape(d["mode_select"])
        _colon_h = html.escape(_colon)
        _mf_h = html.escape(mode_full)
        _mt_h = html.escape(mode_trend)
        # Tip-velden bevatten developer-controlled HTML (<span style=...>) — niet escapen
        _tipf_h = _tip_full
        _tipt_h = _tip_trend
        # Compacte tooltip-tekst: modusnaam + "vanaf/depuis" + vetgedrukte startmaand (2 regels, nowrap)
        _months_i18n = t.get("months", [])
        _trend_m_idx = int(_TREND_WINDOW_START[5:7]) - 1  # 6 → juli/juillet
        _m_full = _months_i18n[0] if _months_i18n else "jan"
        _m_trend = _months_i18n[_trend_m_idx] if len(_months_i18n) > _trend_m_idx else "jul"
        _vanaf = "données depuis" if lang == "fr" else "data vanaf"
        # Zelfde structuur als Pijler/Taal: st.markdown bold + radio collapsed.
        # Tooltip via pure CSS hover (geen Streamlit help-parameter nodig).
        st.markdown(
            f'<p class="zorgi-section-label">'
            f"<strong>{_label_h}</strong>&nbsp;"
            f'<span class="zorgi-help-tip" tabindex="0">?'
            f'<span class="zorgi-help-tip-content">'
            f"<span style='display:block'>"
            f"{_mf_h} &middot; {_vanaf} <span style='font-weight:700'>{_m_full}</span> {_BASELINE_YEAR}"
            f"</span>"
            f"<span style='display:block;margin-top:0.3rem'>"
            f"{_mt_h} &middot; {_vanaf} <span style='font-weight:700'>{_m_trend}</span> {_BASELINE_YEAR}"
            f"</span>"
            f"</span></span></p>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:2rem;min-height:2rem'></div>", unsafe_allow_html=True)
        # Herstel geselecteerde modus uit session_state (bewaard bij taalwissel)
        # Opslag als taalvrije sleutel "full"/"trend" — onafhankelijk van vertaling
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
            st.session_state["lang"] = new_lang
            st.rerun()
        st.divider()

    return selected_pillar, window_start, lang


# ---------------------------------------------------------------------------
# Grafieken (elk max 10 branches — conform McCabe)
# ---------------------------------------------------------------------------


def _chart_timeline(data: DashboardData, t: dict, lang: str) -> go.Figure:
    """
    Combo-grafiek: maandelijkse score (lijn + gekleurde punten) + ticketvolume (bar).

    In Tendensvenster-modus: extra rolvoortschrijdend 3-maands gemiddelde.
    """
    d = t["dashboard"]
    tl = data.timeline
    if not tl:
        return go.Figure()

    periods = [p.period for p in tl]
    x_labels = [period_label(p, lang=lang) for p in periods]
    scores = [p.avg_score for p in tl]
    volumes = [p.total_tickets for p in tl]

    # Fasegebaseerde puntkleur
    point_colors = []
    for p in tl:
        year, month = parse_period(p.period)
        if year <= _BASELINE_YEAR:
            point_colors.append(
                _PHASE_POINT_COLOR["S1"] if month <= 6 else _PHASE_POINT_COLOR["S2"]
            )
        else:
            point_colors.append(_PHASE_POINT_COLOR["Q"])

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Volume-bars (secondary y-as)
    fig.add_trace(
        go.Bar(
            x=x_labels,
            y=volumes,
            name=d["timeline_volume"],
            marker_color=ZORGI_ULTRA_LIGHT,
            marker_line_color=ZORGI_GREY_BLUE,
            marker_line_width=1,
            opacity=0.6,
        ),
        secondary_y=True,
    )

    # Score-lijn met gekleurde punten
    fig.add_trace(
        go.Scatter(
            x=x_labels,
            y=scores,
            mode="lines+markers",
            name=d["timeline_score"],
            line={"color": ZORGI_DARK_BLUE, "width": 2},
            marker={
                "color": point_colors,
                "size": 10,
                "line": {"color": ZORGI_DARK_BLUE, "width": 1},
            },
        ),
        secondary_y=False,
    )

    # Tendensvenster: rolvoortschrijdend gemiddelde
    if data.mode == "trend":
        rolling = pd.Series(scores).rolling(3, min_periods=1).mean().round(2).tolist()
        fig.add_trace(
            go.Scatter(
                x=x_labels,
                y=rolling,
                mode="lines",
                name=d["rolling_avg"],
                line={"color": ZORGI_PURPLE, "width": 2, "dash": "dot"},
            ),
            secondary_y=False,
        )

    fig.update_yaxes(title_text=d["timeline_score"], secondary_y=False, range=[0, 5.5])
    fig.update_yaxes(title_text=d["timeline_volume"], secondary_y=True)
    fig.update_layout(title=d["timeline_title"], barmode="overlay", legend={"orientation": "h"})
    return apply_plotly_theme(fig)


def _chart_period_comparison(data: DashboardData, t: dict) -> go.Figure:
    """Vergelijkingsbalk: gemiddelde score per periode-groep (H1/H2/Q1 enz.)."""
    d = t["dashboard"]
    groups = data.period_groups
    if not groups:
        return go.Figure()

    labels = [g.label for g in groups]
    scores = [g.avg_score for g in groups]
    totals = [g.total for g in groups]

    # Kleur per periode (S1=rood, S2=groen, Q=paars)
    colors = []
    for lbl in labels:
        if lbl.startswith("S1"):
            colors.append(_PHASE_POINT_COLOR["S1"])
        elif lbl.startswith("S2"):
            colors.append(_PHASE_POINT_COLOR["S2"])
        else:
            colors.append(_PHASE_POINT_COLOR["Q"])

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=scores,
            marker_color=colors,
            text=[f"{s:.2f}★<br>({tot} tickets)" for s, tot in zip(scores, totals, strict=False)],
            textposition="outside",
            hovertemplate="%{x}: %{y:.2f}★<extra></extra>",
        )
    )
    fig.update_layout(
        title=d["period_comparison_title"],
        yaxis={"title": d["timeline_score"], "range": [0, 5.5]},
    )
    fig.add_hline(
        y=4.0, line_dash="dash", line_color=ZORGI_GREY_BLUE, annotation_text="Target 4,0★"
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
    fig.add_trace(
        go.Bar(
            name=baseline_label,
            x=labels,
            y=[i.baseline_score for i in items],
            marker_color=ZORGI_GREY_BLUE,
        )
    )
    fig.add_trace(
        go.Bar(
            name=current_label,
            x=labels,
            y=[i.current_score for i in items],
            marker_color=ZORGI_LIGHT_BLUE,
        )
    )
    fig.update_layout(title=title, barmode="group", yaxis={"range": [0, 5.5]})
    return apply_plotly_theme(fig)


def _chart_response_time(data: DashboardData, t: dict) -> go.Figure:
    """Lijn-grafiek: gemiddelde responstijd per score-niveau (baseline gestippeld vs huidig)."""
    d = t["dashboard"]
    rt = data.response_time_by_score
    if not rt:
        return go.Figure()

    levels = sorted(rt.keys())
    x = [f"{lv}★" for lv in levels]
    baseline_days = [rt[lv].baseline_days for lv in levels]
    current_days = [rt[lv].current_days for lv in levels]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=baseline_days,
            mode="lines+markers",
            name=d["response_2025_legend"],
            line={"color": ZORGI_GREY_BLUE, "dash": "dot"},
            connectgaps=True,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=current_days,
            mode="lines+markers",
            name=d["response_current_legend"],
            line={"color": ZORGI_DARK_BLUE},
            connectgaps=True,
        )
    )
    fig.update_layout(
        title=d["response_chart_title"],
        yaxis_title="Dagen",
        xaxis_title="Score-niveau",
    )
    return apply_plotly_theme(fig)


def _chart_hospitals(data: DashboardData, t: dict) -> go.Figure:
    """Horizontal grouped bar chart: baseline vs huidige score per ziekenhuis (top + bottom)."""
    d = t["dashboard"]
    top = data.hospital_top5
    bottom = data.hospital_bottom5
    if not top and not bottom:
        return go.Figure()

    # Top + bottom samenvoegen, gesorteerd op huidige score (laag → hoog)
    top_entries = [(e.hospital, e.score, 0.0, "top") for e in top]
    bottom_entries = [(h.hospital, h.score, h.baseline_score, "bottom") for h in bottom]
    all_entries = sorted(top_entries + bottom_entries, key=lambda x: x[1])

    hospitals = [e[0] for e in all_entries]
    current_scores = [e[1] for e in all_entries]
    colors = [ZORGI_RED if e[3] == "bottom" else ZORGI_FUNC_POSITIVE for e in all_entries]

    fig = go.Figure(
        go.Bar(
            y=hospitals,
            x=current_scores,
            orientation="h",
            marker_color=colors,
            text=[f"{s:.2f}★" for s in current_scores],
            textposition="outside",
            hovertemplate="%{y}: %{x:.2f}★<extra></extra>",
            name=d["col_current"],
        )
    )
    fig.update_layout(
        title=d["hospital_chart_title"],
        xaxis={"title": d["timeline_score"], "range": [0, 5.5]},
    )
    fig.add_vline(x=4.0, line_dash="dash", line_color=ZORGI_GREY_BLUE)
    fig.add_vline(
        x=2.5,
        line_dash="dash",
        line_color=ZORGI_RED,
        annotation_text="Disengagement 2,5★",
    )
    return apply_plotly_theme(fig)


def _chart_kpi_targets(data: DashboardData, t: dict, lang: str) -> go.Figure:
    """Grouped bar chart: baseline / target / realisatie per KPI."""
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
    fig.add_trace(
        go.Bar(name=d["col_baseline"], x=labels, y=baselines, marker_color=ZORGI_GREY_BLUE)
    )
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
    fig.add_trace(
        go.Bar(name=d["col_realization"], x=labels, y=current_vals, marker_color=ZORGI_LIGHT_BLUE)
    )
    fig.update_layout(title=d["kpi_chart_title"], barmode="group")
    return apply_plotly_theme(fig)


# ---------------------------------------------------------------------------
# Tab-renders
# ---------------------------------------------------------------------------


def _tab_summary(data: DashboardData, t: dict, lang: str) -> None:
    """Tab 1 — Samenvatting: 8 KPI-kaarten, mini-signaalkaart, vergelijkingstabel."""
    d = t["dashboard"]
    ref_str = (
        d["vs_h2"] if data.mode == "trend" else d["vs_baseline"].format(label=data.baseline_label)
    )

    # --- 8 KPI-kaarten (2 rijen van 4) ---
    row1 = st.columns(4)
    row2 = st.columns(4)

    row1[0].metric(
        d["kpi_avg_score"],
        f"{data.kpi_avg_score:.2f}★",
        f"{data.kpi_avg_score_delta:+.2f}★ {ref_str}",
    )
    row1[1].metric(
        d["kpi_pct_positive"],
        f"{data.kpi_pct_positive:.1f}%",
        f"{data.kpi_pct_positive_delta:+.1f} ppt {ref_str}",
    )
    row1[2].metric(
        d["kpi_pct_negative"],
        f"{data.kpi_pct_negative:.1f}%",
        f"{data.kpi_pct_negative_delta:+.1f} ppt {ref_str}",
        delta_color="inverse",
    )
    row1[3].metric(
        d["kpi_best_month"],
        data.kpi_best_month_label,
        f"{data.kpi_best_month_score:.2f}★",
        delta_color="off",
    )

    row2[0].metric(d["kpi_responses"], str(data.kpi_responses_total), delta_color="off")
    row2[1].metric(
        d["kpi_streak"], f"{data.kpi_streak_months} {d['streak_unit']}", delta_color="off"
    )
    row2[2].metric(
        d["kpi_critical_accounts"],
        f"{data.kpi_critical_accounts} {d['critical_unit']}",
        delta_color="off",
    )
    row2[3].metric(
        d["kpi_targets_met"], f"{data.kpi_targets_met}/{data.kpi_targets_total}", delta_color="off"
    )

    st.divider()

    # --- ZH mini-signaalkaart ---
    st.markdown(f"#### {d['verdict_title']}")
    col_top, col_bot = st.columns(2)
    with col_top:
        st.markdown(f"**{d['top3_best']}**")
        for zh in data.zh_top3:
            st.markdown(f"🟢 **{zh.hospital}** — {zh.score:.2f}★ ({zh.tickets} tickets)")
    with col_bot:
        st.markdown(f"**{d['top3_worst']}**")
        for zh in data.zh_bottom3:
            icon = "🔴" if zh.disengagement_risk else "🟡"
            st.markdown(f"{icon} **{zh.hospital}** — {zh.score:.2f}★ ({zh.tickets} tickets)")
    st.caption(d["see_tab5"])

    st.divider()

    # --- Kerncijfers vergelijkingstabel ---
    st.markdown(f"#### {d['comparison_table_title']}")
    evo_t = t.get("evolution", {}).get("kpi", {})
    table_data = {
        d["col_metric"]: [evo_t.get(r.metric, r.metric) for r in data.comparison_rows],
        d["col_baseline"]: [r.baseline_value for r in data.comparison_rows],
        d["col_current"]: [r.current_value for r in data.comparison_rows],
        "Δ": [r.delta_value for r in data.comparison_rows],
    }
    st.dataframe(pd.DataFrame(table_data), hide_index=True, width="stretch")


def _tab_timeline(data: DashboardData, t: dict, lang: str) -> None:
    """Tab 2 — Tijdlijn: combo-grafiek + vergelijkingsbalk."""
    d = t["dashboard"]
    if not data.timeline:
        st.info(d["no_data"])
        return

    st.plotly_chart(_chart_timeline(data, t, lang), width="stretch")
    st.divider()
    st.plotly_chart(_chart_period_comparison(data, t), width="stretch")


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
        st.plotly_chart(fig, width="stretch")

        if data.trivial_pct_negative > 10 and data.trivial_avg_score > 0:
            st.warning(
                d["trivial_alert"].format(
                    score=f"{data.trivial_avg_score:.2f}",
                    pct=f"{data.trivial_pct_negative:.1f}",
                )
            )


def _tab_response(data: DashboardData, t: dict, lang: str) -> None:
    """Tab 4 — Responstijd: correlatie-panel + lijn-grafiek per score-niveau."""
    d = t["dashboard"]

    # --- Correlatie-ommekeer panel ---
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

    # --- Lijn-grafiek responstijd per score-niveau ---
    if data.response_time_by_score:
        st.plotly_chart(_chart_response_time(data, t), width="stretch")
    else:
        st.info(d["no_data"])


def _tab_hospitals(data: DashboardData, t: dict, lang: str) -> None:
    """Tab 5 — Ziekenhuizen: bar chart + top-5 tabel + bottom-5 tabel met oorzaakkolom."""
    d = t["dashboard"]
    evo_t = t.get("evolution", {}).get("theme", {})

    # --- Horizontal bar chart ---
    if data.hospital_top5 or data.hospital_bottom5:
        st.plotly_chart(_chart_hospitals(data, t), width="stretch")

    st.divider()

    # --- Top-5 tabel ---
    if data.hospital_top5:
        st.markdown(f"#### {d['top5_title']}")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        d["col_hospital"]: e.hospital,
                        d["col_score"]: f"{e.score:.2f}★",
                        d["col_tickets"]: e.tickets,
                        d["col_learning"]: "✅ Aanbevolen werkwijzen documenteren",
                    }
                    for e in data.hospital_top5
                ]
            ),
            hide_index=True,
            width="stretch",
        )

    st.divider()

    # --- Bottom-5 tabel + disengagement-alerts ---
    if data.hospital_bottom5:
        st.markdown(f"#### {d['bottom5_title']}")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        d["col_hospital"]: h.hospital,
                        d["col_score"]: f"{h.score:.2f}★",
                        d["col_tickets"]: h.tickets,
                        d["col_complaint"]: evo_t.get(h.cause, h.cause) if h.cause else "—",
                    }
                    for h in data.hospital_bottom5
                ]
            ),
            hide_index=True,
            width="stretch",
        )

        # Disengagement-alerts
        for h in data.hospital_bottom5:
            if h.disengagement_risk:
                st.error(
                    d["disengagement_alert"].format(
                        hospital=h.hospital,
                        score=f"{h.score:.2f}",
                        tickets=h.tickets,
                    )
                )


def _tab_targets(data: DashboardData, t: dict, lang: str) -> None:
    """Tab 6 — KPI Targets: grouped bar chart + overzichtstabel + bijgestelde targets-notitie."""
    d = t["dashboard"]
    kpi_names_i18n = t.get("evolution", {}).get("target_tracking", {}).get("kpi_names", {})
    status_i18n = t.get("evolution", {}).get("target_tracking", {})

    st.markdown(f"#### {d['kpi_targets_title']}")

    if data.kpi_targets:
        st.plotly_chart(_chart_kpi_targets(data, t, lang), width="stretch")

        # Overzichtstabel
        status_map = {
            "op_schema": status_i18n.get("op_schema", "✅"),
            "aandacht": status_i18n.get("aandacht", "⚠️"),
            "kritiek": status_i18n.get("kritiek", "🔴"),
        }
        ordered = {k.name: k for k in data.kpi_targets}
        rows = []
        for key in _KPI_TARGET_ORDER:
            if key not in ordered:
                continue
            kp = ordered[key]
            rows.append(
                {
                    d["col_kpi"]: kpi_names_i18n.get(kp.name, kp.name),
                    d["col_baseline"]: f"{kp.baseline:.2f}",
                    d["col_target"]: f"{kp.target:.2f}",
                    d["col_realization"]: f"{kp.current:.2f}",
                    d["col_status"]: status_map.get(kp.status, kp.status),
                }
            )
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    st.info(d["adjusted_targets_note"])


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


def main() -> None:
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
        st.session_state["selected_pillar"] = "zorgi"
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
    selected_pillar, window_start, lang = _render_sidebar(t, today, last_year, last_month)

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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            d["tab_summary"],
            d["tab_timeline"],
            d["tab_tickets"],
            d["tab_response"],
            d["tab_hospitals"],
            d["tab_targets"],
        ]
    )

    with tab1:
        _tab_summary(data, t, lang)
    with tab2:
        _tab_timeline(data, t, lang)
    with tab3:
        _tab_tickets(data, t, lang)
    with tab4:
        _tab_response(data, t, lang)
    with tab5:
        _tab_hospitals(data, t, lang)
    with tab6:
        _tab_targets(data, t, lang)

    # Tab-font CSS NA tabs injecteren (wint cascade van Streamlit emotion-CSS)
    inject_tab_font_css(st)

    # Sidebar-toggle knop injecteren (NA alle content — blokkeert rendering niet)
    inject_sidebar_toggle()


if __name__ == "__main__":
    main()
