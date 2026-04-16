"""
Patch app.py met alle Fase 5a wijzigingen.
Uitvoeren: python tools/_patch_app.py
"""
import re
from pathlib import Path

APP = Path("src/dashboard/app.py")
src = APP.read_text(encoding="utf-8")

# ── 1. DEV-sectie invoegen vóór "Coming soon placeholder" ─────────────────
DEV_CODE = r'''
# ---------------------------------------------------------------------------
# DEV-tabblad — tijdelijk ontwikkeltabblad Tickets & Prioriteit (Fase 5a)
# ---------------------------------------------------------------------------


def _build_issue_type_chart(df_comparison):
    """Horizontale bar chart voor issue type vergelijking — Plotly/ZORGI-stijl."""
    import math
    COLOR_OK = ZORGI_FUNC_POSITIVE
    COLOR_BAD = ZORGI_RED
    COLOR_NEUTRAL = ZORGI_DARK_BLUE
    COLOR_2025 = "#A7B4C1"  # 1. gewijzigd van #C5D0D8
    df_sorted = df_comparison.sort_values(
        "issue_type", ascending=True, na_position="last"
    ).reset_index(drop=True)
    types = df_sorted["issue_type"].tolist()
    scores_prev = df_sorted["score_prev"].tolist()
    scores_curr = df_sorted["score_curr"].tolist()
    counts_prev = (df_sorted["count_prev"].tolist()
                   if "count_prev" in df_sorted.columns else [0] * len(types))
    counts_curr = (df_sorted["count_curr"].tolist()
                   if "count_curr" in df_sorted.columns else [0] * len(types))
    n = len(types)
    _bar_w = 0.35  # iets kleiner van 0.40 → 0.35
    ytd_colors = []
    for sp, sc in zip(scores_prev, scores_curr):
        if not math.isnan(sc) and not math.isnan(sp):
            ytd_colors.append(COLOR_OK if sc >= sp else COLOR_BAD)
        else:
            ytd_colors.append(COLOR_NEUTRAL)
    all_sc = [s for s in scores_prev + scores_curr if not math.isnan(s)]
    x_max = round(max(all_sc) + 0.2, 1) if all_sc else 5.5
    x_min = max(0.0, round(min(all_sc) - 0.3, 1)) if all_sc else 0.0

    def _score_text(v):
        return f"\u00a0\u00a0{v:.2f}\u2605" if not math.isnan(v) else ""

    fig = go.Figure()
    # 2025-balk — lichtgrijs, score buiten
    fig.add_trace(go.Bar(
        name="2025", y=types, x=scores_prev, orientation="h",
        marker_color=COLOR_2025,
        text=[_score_text(v) for v in scores_prev],
        textposition="outside",
        textfont={"size": 9, "color": "#7A8D97"},
        width=_bar_w, offset=-_bar_w,
        hovertemplate="%{y} 2025: %{x:.2f}\u2605<extra></extra>",
    ))
    # YTD-balk — gekleurde bars, score buiten
    fig.add_trace(go.Bar(
        name="YTD", y=types, x=scores_curr, orientation="h",
        marker_color=ytd_colors,
        text=[_score_text(v) for v in scores_curr],
        textposition="outside",
        textfont={"size": 9, "color": "#444444"},
        width=_bar_w, offset=0.0, showlegend=False,
        hovertemplate="%{y} YTD: %{x:.2f}\u2605<extra></extra>",
    ))
    # Legenda-dummies
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker={"symbol": "square", "size": 12, "color": COLOR_OK},
        name="YTD (verbetering)",
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker={"symbol": "square", "size": 12, "color": COLOR_BAD},
        name="YTD (verslechtering)",
    ))
    # 6. Ticketaantallen binnenin via annotaties — wit
    for t_name, vp, cp, vc, cc in zip(types, scores_prev, counts_prev, scores_curr, counts_curr):
        if not math.isnan(vp) and cp > 0:
            fig.add_annotation(
                x=x_min + 0.05, y=t_name, text=f"{int(cp)} t",
                showarrow=False, xanchor="left",
                font={"size": 10, "color": "#ffffff"}, yshift=10,
            )
        if not math.isnan(vc) and cc > 0:
            fig.add_annotation(
                x=x_min + 0.05, y=t_name, text=f"{int(cc)} t",
                showarrow=False, xanchor="left",
                font={"size": 10, "color": "#ffffff"}, yshift=-10,
            )
    # 4+5. Legenda bottom = top datasectie; modebar right = datasectie right
    fig.update_layout(
        title="", barmode="overlay",
        xaxis={"title": "", "range": [x_min, x_max], "gridcolor": "#edf2f7",
               "ticksuffix": "\u2605", "tickformat": ".1f"},
        yaxis={"title": "", "autorange": "reversed"},
        height=max(250, n * 72 + 80),
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.05,
                "xanchor": "center", "x": 0.5, "itemsizing": "constant"},
        margin={"t": 50, "b": 10, "r": 0},
        modebar_remove=["pan2d", "autoScale2d"],
    )
    return apply_plotly_theme(fig)


def render_tab_dev_tickets(
    df: pd.DataFrame,
    lang: str,
    mode: str = "full",
    baseline_year: int | None = None,
    current_year: int | None = None,
    current_month: int | None = None,
    trend_start_month: int = 7,
) -> None:
    """DEV-tabblad Tickets & Prioriteit — werk in uitvoering."""
    import math  # noqa: F401
    from csat.core.calculations import calc_hero_metrics_tickets, calc_issue_type_comparison
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
        label="Laagst scorend type",
        value=metrics["lowest_score_type"],
        delta=f"{metrics['lowest_score_type_value']}\u2605 \u2014 laagste",
        delta_color="inverse",
    )
    col_c.metric(
        label="Grootste prioritaire groep",
        value=metrics["largest_priority_group"],
        delta=(f"{metrics['largest_priority_pct']}% tickets"
               f" \u00b7 {metrics['largest_priority_neg_pct']}% neg."),
    )
    kpi_ok = metrics["high_critical_ok"]
    _margin = str(abs(metrics["high_critical_margin"])).replace(".", ",")
    col_d.metric(
        label="% High/Critical (KPI \u226415%)",
        value=f"{metrics['high_critical_pct']}%",
        delta=f"{_margin}% onder target" if kpi_ok else f"{_margin}% boven target",
        delta_color="normal" if kpi_ok else "inverse",
    )
    st.divider()
    # 3. Titel als onderdeel van de Plotly-figuur — geen gap tussen titel en grafiek
    df_issue = calc_issue_type_comparison(
        df,
        mode=mode,
        baseline_year=baseline_year,
        current_year=current_year,
        current_month=current_month,
        trend_start_month=trend_start_month,
    )
    st.plotly_chart(
        _build_issue_type_chart(df_issue, chart_title=f"Issue type \u2014 vergelijking {datetime.now(tz=UTC).year}", prev_label=_prev_label),
        width="stretch",
        config=_CHART_CONFIG,
    )
    st.markdown(
        "<hr style='margin:0.4rem 0 0.8rem 0;border:none;border-top:1px solid #e0e8f0'>",
        unsafe_allow_html=True,
    )
    # Sorteerbare detailtabel — analoog aan Ziekenhuizen-tab
    import math as _math
    def _fstar(v):
        return f"{v:.2f}\u2605" if not _math.isnan(v) else "\u2014"
    def _fpct(v):
        return f"{v:.1f}%" if not _math.isnan(v) else "\u2014"
    def _fdelta_s(v):
        return f"{v:+.2f}\u2605" if not _math.isnan(v) else "\u2014"
    def _fdelta_n(v):
        return f"{v:+.1f} ppt" if not _math.isnan(v) else "\u2014"
    df_tbl = pd.DataFrame([
        {
            "Type":                     str(r["issue_type"]),
            f"Score {_prev_label}":     _fstar(r["score_prev"]),
            "Score YTD":                _fstar(r["score_curr"]),
            "% Negatief":               _fpct(r["pct_neg_curr"]),
            "\u0394 Score":             _fdelta_s(r["delta_score"]),
            "\u0394 Negatief":          _fdelta_n(r["delta_neg"]),
        }
        for _, r in df_issue.iterrows()
    ])
    st.markdown("#### \U0001f4cb Score per issue type \u2014 detail")
    st.markdown("<div style='margin-bottom:0.1rem'></div>", unsafe_allow_html=True)
    _render_sortable_table(
        df_tbl,
        title="",
        show_title=False,
        delta_col="\u0394 Score",
        export_filename="issue_type_vergelijking.csv",
        col_widths=["32%", "13%", "13%", "11%", "11%", "13%"],
    )
    st.markdown(
        "<div style='font-size:0.80rem;color:#5f8495;margin-top:-0.6rem;line-height:1.6'>"
        "<b style='color:#3a5a7a'>% Negatief</b>: aandeel tickets met score \u22642\u2605 in YTD<br>"
        f"<b style='color:#3a5a7a'>\u0394 Negatief</b>: verschil t.o.v. {_prev_label} in procentpunten, "
        "een negatieve waarde betekent verbetering (minder negatieve scores)"
        "</div>",
        unsafe_allow_html=True,
    )

'''

ANCHOR = "# ---------------------------------------------------------------------------\n# Coming soon placeholder (niet-PHARMA pijlers)"
assert ANCHOR in src, "Ankerpunt niet gevonden!"
src = src.replace(ANCHOR, DEV_CODE + "\n" + ANCHOR, 1)

# ── 2. Tab-labels uitbreiden in main() ────────────────────────────────────
OLD_TABS = '''    _tab_labels = [
        d["tab_summary"],
        d["tab_timeline"],
        d["tab_tickets"],
        d["tab_response"],
        d["tab_hospitals"],
        d["tab_targets"],
    ]'''
NEW_TABS = '''    _tab_labels = [
        d["tab_summary"],
        d["tab_timeline"],
        d["tab_tickets"],
        d["tab_response"],
        d["tab_hospitals"],
        d["tab_targets"],
        "DEV Tickets & Prioriteit",
    ]'''
assert OLD_TABS in src, "Tab-labels niet gevonden!"
src = src.replace(OLD_TABS, NEW_TABS, 1)

# ── 3. st.tabs unpacking ──────────────────────────────────────────────────
OLD_STABS = "    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs("
NEW_STABS = "    tab1, tab2, tab3, tab4, tab5, tab6, tab_dev = st.tabs("
assert OLD_STABS in src, "st.tabs niet gevonden!"
src = src.replace(OLD_STABS, NEW_STABS, 1)

# ── 4. with-blok toevoegen ────────────────────────────────────────────────
OLD_WITH = "    with tab6:\n        _tab_targets(data, t, lang)"
NEW_WITH = ("    with tab6:\n        _tab_targets(data, t, lang)\n"
            "    with tab_dev:\n"
            "        _df_dev = _load_df()\n"
            "        _dev_products = PILLAR_REGISTRY.get(selected_pillar, {}).get('products', [])\n"
            "        _df_dev = _df_dev[_df_dev[FILTER_COLUMN].isin(_dev_products)]\n"
            "        render_tab_dev_tickets(_df_dev, lang)")
assert OLD_WITH in src, "with tab6 niet gevonden!"
src = src.replace(OLD_WITH, NEW_WITH, 1)

# ── 5. Taalwissel-labels ──────────────────────────────────────────────────
OLD_LANG = '''            _new_labels = [
                _new_d["tab_summary"],
                _new_d["tab_timeline"],
                _new_d["tab_tickets"],
                _new_d["tab_response"],
                _new_d["tab_hospitals"],
                _new_d["tab_targets"],
            ]'''
NEW_LANG = '''            _new_labels = [
                _new_d["tab_summary"],
                _new_d["tab_timeline"],
                _new_d["tab_tickets"],
                _new_d["tab_response"],
                _new_d["tab_hospitals"],
                _new_d["tab_targets"],
                "DEV Tickets & Prioriteit",
            ]'''
assert OLD_LANG in src, "Taalwissel-labels niet gevonden!"
src = src.replace(OLD_LANG, NEW_LANG, 1)

APP.write_text(src, encoding="utf-8")
print(f"Patch toegepast — {len(src.splitlines())} regels")

# Syntax check
import ast
ast.parse(src)
print("Syntax OK")

