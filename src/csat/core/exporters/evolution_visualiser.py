"""
EvolutionVisualiser voor CSAT-Compass.

Genereert een 4-subplot matplotlib PNG-visualisatie vanuit een EvolutionResult.

Subplots:
    1. Maandelijkse gemiddelde CSAT-score — lijndiagram
    2. % Negatief per maand — staafdiagram
    3. HC-ratio: baseline vs huidig — staafdiagram
    4. Delta per ziekenhuis — horizontaal staafdiagram (top/bottom, max 15)

Output: output/evolutie-{pillar}-{jaar}.png — taalversie-onafhankelijk
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from csat.config.pillars import PILLAR_REGISTRY
from csat.config.settings import AVG_SCORE_MIN, HIGH_CRITICAL_MAX
from csat.core.analysers.evolution_result import EvolutionResult
from csat.utils.branding import COLORS, apply_matplotlib_theme
from csat.utils.zorgi_theme import (
    ZORGI_BODY_TEXT,
    ZORGI_BORDEAUX,
    ZORGI_CHART_BG,
    ZORGI_DARK_BLUE,
    ZORGI_FUNC_POSITIVE,
    ZORGI_GREY_BLUE,
    ZORGI_LIGHT_BLUE,
    ZORGI_RED,
    ZORGI_ULTRA_LIGHT,
)

# Functionele aliassen — lokale namen voor leesbaarheid in deze module
FUNC_POSITIVE = ZORGI_FUNC_POSITIVE  # Groen — positieve delta bars (Optie B)
FUNC_NEGATIVE = ZORGI_RED  # Rood — negatieve delta bars
FUNC_CRISIS = ZORGI_RED  # Rood — hoge % negatief bars

# Prioriteitsvolgorde (Jira-schaal hoog → laag) en kleuren per prioriteit
PRIORITY_ORDER: list[str] = ["Blocker", "Critical", "Major", "Minor", "Trivial"]
PRIORITY_COLORS: dict[str, str] = {
    "Blocker": "#7f0000",  # Donker rood — ernstigste
    "Critical": ZORGI_RED,  # ZORGI rood
    "Major": "#e8835c",  # Oranje-rood — afgeleide tint
    "Minor": ZORGI_LIGHT_BLUE,  # ZORGI lichtblauw
    "Trivial": "#b8cfe0",  # Lichtblauw — donkerder dan #d7e7f3, lichter dan Minor
}

# --- Technische constanten ---
_DPI_SCREEN: int = 150
_DPI_PRINT: int = 300
_FIG_WIDTH: float = 15.0
_FIG_HEIGHT: float = 10.0
_MAX_HOSPITALS: int = 15

# ── i18n vertalingstabel NL / FR ──────────────────────────────────────────────
_TRANSLATIONS: dict[str, dict[str, str]] = {
    "nl": {
        "trend_structural": "Structureel",
        "trend_not_structural": "Niet structureel",
        "sub1_title": "Gemiddelde CSAT-score per maand",
        "sub1_ylabel": "Score (1-5)",
        "sub1_min_label": "Min. {val}",
        "sub2_title": "% Negatief per maand",
        "sub2_ylabel": "% negatief",
        "sub2_threshold": "{val}% drempel",
        "sub2_no_data": "Geen data",
        "sub3_title": "Prioriteitscompositie per maand",
        "sub3_ylabel": "% van tickets",
        "sub3_threshold": "% Blocker + Critical",
        "sub3_ticket_label": "# tickets",
        "sub3_no_data": "Geen data",
        "sub4_title": "\u0394 Score per ziekenhuis (beste \u2192 slechtste)",
        "sub4_xlabel": "\u0394 gemiddelde score",
        "sub4_ticket_explainer": "aantal {baseline}/{current}",
        "sub4_no_data": "Geen vergelijkbare data",
    },
    "fr": {
        "trend_structural": "Structurel",
        "trend_not_structural": "Non structurel",
        "sub1_title": "Score CSAT moyen par mois",
        "sub1_ylabel": "Score (1-5)",
        "sub1_min_label": "Min. {val}",
        "sub2_title": "% N\u00e9gatif par mois",
        "sub2_ylabel": "% n\u00e9gatif",
        "sub2_threshold": "Seuil {val}%",
        "sub2_no_data": "Pas de donn\u00e9es",
        "sub3_title": "Composition des priorit\u00e9s par mois",
        "sub3_ylabel": "% des tickets",
        "sub3_threshold": "% Bloqueur + Critique",
        "sub3_ticket_label": "# tickets",
        "sub3_no_data": "Pas de donn\u00e9es",
        "sub4_title": "\u0394 Score par h\u00f4pital (meilleur \u2192 moins bon)",
        "sub4_xlabel": "\u0394 score moyen",
        "sub4_ticket_explainer": "nombre {baseline}/{current}",
        "sub4_no_data": "Pas de donn\u00e9es comparables",
    },
}
# ─────────────────────────────────────────────────────────────────────────────


def _fmt_delta(value: float, decimals: int = 2) -> str:
    """
    Formatteer een delta-waarde met expliciete +/- prefix (ZORGI-getalnotatie).

    Args:
        value:    Delta-waarde
        decimals: Aantal decimalen (standaard 2)

    Returns:
        Geformatteerde string, bv. '+1,70' of '-0,50'
    """
    sign = "+" if value >= 0 else ""
    formatted = f"{value:.{decimals}f}".replace(".", ",")
    return f"{sign}{formatted}"


def _extract_year(label: str) -> str:
    """
    Extraheer het viercijferige jaar uit een current/baseline label.

    Ondersteunt labels zoals '2026', 'jan-mrt 2026', '2025-2026'.

    Args:
        label: Periodeomschrijving

    Returns:
        Viercijferig jaargetal als string, of het label zelf als fallback
    """
    import re

    match = re.search(r"\b(20\d{2})\b", label)
    return match.group(1) if match else label


def _style_ax(ax) -> None:
    """
    Pas ZORGI-leesbaarheidsstandaard toe op tick-kleuren van een Axes-object.

    Overschrijft de globale rcParams en forceert alpha=1.0 + fontweight='normal'
    op alle ticklabels.

    Args:
        ax: Matplotlib Axes
    """
    ax.tick_params(axis="both", colors=ZORGI_BODY_TEXT, labelsize=8.5)
    ax.xaxis.label.set_color(ZORGI_BODY_TEXT)
    ax.yaxis.label.set_color(ZORGI_BODY_TEXT)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_color(ZORGI_BODY_TEXT)
        lbl.set_alpha(1.0)
        lbl.set_fontweight("normal")


def _style_legend(legend) -> None:
    """
    Pas ZORGI-leesbaarheidsstandaard toe op een matplotlib Legend.

    Geeft het kader een witte achtergrond en forceert donkere,
    volledig-ondoorzichtige tekst op alle legendaitems.

    Args:
        legend: Matplotlib Legend object (of None — dan no-op)
    """
    if legend is None:
        return
    frame = legend.get_frame()
    frame.set_alpha(0.92)
    frame.set_facecolor("white")
    frame.set_edgecolor(ZORGI_GREY_BLUE)
    for text in legend.get_texts():
        text.set_color(ZORGI_BODY_TEXT)
        text.set_fontweight("normal")
        text.set_alpha(1.0)


def _build_tick_labels(pts) -> list[str]:
    """
    Bouw x-as ticklabels waarbij maand 01 vervangen wordt door het jaargetal.

    Dit integreert het jaar op de as zelf zodat geen aparte annotaties nodig zijn.
    Alle labels krijgen dezelfde stijl — geen italic, geen kleurverschil.

    Args:
        pts: Lijst van MonthlyDataPoint-objecten gesorteerd op periode

    Returns:
        Lijst van strings: jaargetal op positie "01", maandnummer (MM) voor de rest.
        Voorbeeld: ["2025", "02", "03", ..., "12", "2026", "02", "03"]
    """
    labels = []
    for pt in pts:
        maand = pt.period[5:7]  # "MM" uit "YYYY-MM"
        jaar = pt.period[:4]  # "YYYY" uit "YYYY-MM"
        labels.append(jaar if maand == "01" else maand)
    return labels


class EvolutionVisualiser:
    """
    Genereert CSAT-evolutie-visualisaties als 4-subplot matplotlib-figuur.

    Gebruik render() voor een Figure zonder bestandsschrijving, of export()
    om direct een PNG-bestand te schrijven.

    Args:
        result: EvolutionResult van een EvolutionAnalyser.analyse() aanroep
        lang:   Taalcode 'nl' (standaard) of 'fr' — bepaalt alle teksten in de figuur
    """

    def __init__(self, result: EvolutionResult, lang: str = "nl") -> None:
        self._result = result
        self._lang = lang if lang in _TRANSLATIONS else "nl"
        pillar_info = PILLAR_REGISTRY.get(result.pillar, {})
        self._pillar_color: str = pillar_info.get("color", COLORS["dark_blue"])
        self._pillar_name: str = pillar_info.get("report_name", result.pillar.upper())

    def _t(self, key: str, **kwargs) -> str:
        """Geef de vertaling voor key in de ingestelde taal, met optionele format-args."""
        tekst = _TRANSLATIONS[self._lang].get(key, key)
        return tekst.format(**kwargs) if kwargs else tekst

    # ------------------------------------------------------------------
    # Publieke methoden
    # ------------------------------------------------------------------

    def render(self):  # -> plt.Figure
        """
        Render de 4-subplot figuur als matplotlib Figure (geen bestandsschrijving).

        Returns:
            Matplotlib Figure met 4 subplots
        """
        import matplotlib.gridspec as gridspec
        import matplotlib.pyplot as plt

        apply_matplotlib_theme()

        # ZORGI Design System rcParams — overschrijft apply_matplotlib_theme():
        # - DejaVu Sans als primair font: volledige Unicode-dekking (pijl U+2192, delta U+0394).
        #   Poppins mist deze glyphs en glyph-level fallback is niet beschikbaar in
        #   matplotlib 3.10 op Windows. DejaVu Sans is altijd aanwezig in matplotlib.
        #   Poppins blijft als fallback voor eventuele toekomstige glyph-uitbreiding.
        # - Alle tekst- en tickkleuren -> ZORGI_BODY_TEXT
        plt.rcParams.update(
            {
                "font.family": "sans-serif",
                "font.sans-serif": ["DejaVu Sans", "Verdana", "Poppins"],
                "font.weight": "normal",
                "axes.titleweight": "bold",
                "axes.labelweight": "normal",
                "text.color": ZORGI_BODY_TEXT,
                "axes.labelcolor": ZORGI_BODY_TEXT,
                "xtick.color": ZORGI_BODY_TEXT,
                "ytick.color": ZORGI_BODY_TEXT,
                "axes.facecolor": ZORGI_CHART_BG,
                "figure.facecolor": ZORGI_CHART_BG,
                "axes.titlesize": 11,
                "axes.labelsize": 9,
                "xtick.labelsize": 8.5,
                "ytick.labelsize": 8.5,
                "legend.fontsize": 8.5,
            }
        )

        r = self._result

        fig = plt.figure(figsize=(_FIG_WIDTH, _FIG_HEIGHT))
        fig.patch.set_facecolor(ZORGI_CHART_BG)

        # 45/55 verdeling: rechterkolom iets breder voor ziekenhuisnamen
        gs = gridspec.GridSpec(
            2,
            2,
            figure=fig,
            hspace=0.50,
            wspace=0.40,
            width_ratios=[1, 1.2],
            height_ratios=[1, 1],
        )
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])

        # Globale achtergrond, spines en gridlines — identiek op alle 4 subplots
        for ax in (ax1, ax2, ax3, ax4):
            ax.set_facecolor(ZORGI_CHART_BG)
            for spine in ax.spines.values():
                spine.set_edgecolor(ZORGI_GREY_BLUE)
                spine.set_linewidth(0.6)
            ax.set_axisbelow(True)
            ax.yaxis.grid(True, color=ZORGI_ULTRA_LIGHT, linewidth=0.8, zorder=0)
            ax.xaxis.grid(False)

        # Supertitel — ZORGI Dark Blue conform Design System §3
        trend_label = (
            self._t("trend_structural")
            if r.trend_is_structural
            else self._t("trend_not_structural")
        )
        delta_str = _fmt_delta(r.delta_avg_score)
        fig.suptitle(
            f"CSAT-Compass \u2014 {self._pillar_name}"
            f"  |  {r.baseline_label} \u2192 {r.current_label}"
            f"  |  \u0394 {delta_str}  [{trend_label}]",
            fontsize=13,
            color=ZORGI_DARK_BLUE,
            fontweight="bold",
            y=0.98,
        )

        self._draw_subplot1_score(ax1, r)
        self._draw_subplot2_pct_neg(ax2, r)
        self._draw_subplot3_priority_composition(ax3, r)
        self._draw_subplot4_hospitals(ax4, r)

        fig.subplots_adjust(top=0.93, bottom=0.08, left=0.08, right=0.97, hspace=0.50, wspace=0.40)
        return fig

    def export(
        self,
        output_path: Path,
        year: str | None = None,
        timestamp: bool = True,
        ts_suffix: str | None = None,
    ) -> Path:
        """
        Render de figuur en schrijf naar output_path/evolutie-{pillar}-{jaar}-{lang}[_{ts}].png.

        Args:
            output_path: Map waar het PNG-bestand geschreven wordt
            year:        Jaarlabel voor bestandsnaam (standaard: afgeleid van current_label)
            timestamp:   Voeg datum/tijd toe aan bestandsnaam (standaard: True).
                         Wordt genegeerd als ts_suffix opgegeven is.
            ts_suffix:   Expliciete tijdstempel-suffix (bv. '_20260401-1435').
                         Gebruik dit om exact dezelfde suffix als de bijbehorende MD te garanderen.
                         None = val terug op timestamp-parameter.

        Returns:
            Absoluut pad naar het gegenereerde PNG-bestand
        """
        from datetime import datetime  # noqa: PLC0415

        import matplotlib.pyplot as plt

        fig = self.render()
        jaar = year or _extract_year(self._result.current_label) or "2026"
        jaar_safe = jaar.replace(" ", "-").replace("/", "-")

        if ts_suffix is not None:
            ts = ts_suffix
        else:
            ts = f"_{datetime.now().astimezone().strftime('%Y%m%d-%H%M')}" if timestamp else ""

        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        pad = output_path / f"evolutie-{self._result.pillar}-{jaar_safe}-{self._lang}{ts}.png"

        fig.savefig(pad, dpi=_DPI_SCREEN, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        logger.info(f"[EvolutionVisualiser] Visualisatie geschreven \u2192 {pad}")
        return pad

    # ------------------------------------------------------------------
    # Subplot 1 — maandelijkse score-evolutie (lijndiagram)
    # ------------------------------------------------------------------

    def _draw_subplot1_score(self, ax, r: EvolutionResult) -> None:
        """Subplot 1: lijndiagram met maandelijkse gemiddelde CSAT-score baseline vs huidig."""
        from matplotlib.lines import Line2D  # noqa: PLC0415

        timeline = sorted(r.monthly_timeline, key=lambda p: p.period)

        if not timeline:
            ax.set_title(
                "Gemiddelde CSAT-score per maand", color=ZORGI_GREY_BLUE, fontweight="bold"
            )
            ax.text(
                0.5,
                0.5,
                "Geen data",
                ha="center",
                va="center",
                transform=ax.transAxes,
                color=ZORGI_BODY_TEXT,
            )
            _style_ax(ax)
            return

        current_year = _extract_year(r.current_label)
        baseline_pts = [p for p in timeline if not p.period.startswith(current_year)]
        current_pts = [p for p in timeline if p.period.startswith(current_year)]

        if not baseline_pts and not current_pts:  # pragma: no cover
            mid = len(timeline) // 2
            baseline_pts = timeline[:mid]
            current_pts = timeline[mid:]

        x_b = list(range(len(baseline_pts)))
        offset = len(x_b)  # direct aansluitend — geen lege positie
        x_c = list(range(offset, offset + len(current_pts)))

        scores_b = [p.avg_score for p in baseline_pts]
        scores_c = [p.avg_score for p in current_pts]

        # Baseline-lijn -> ZORGI Light Blue (gestippeld, iets teruggetrokken)
        if x_b and scores_b:
            ax.plot(
                x_b,
                scores_b,
                color=ZORGI_LIGHT_BLUE,
                alpha=0.85,
                linestyle="--",
                linewidth=1.5,
                marker="o",
                markersize=4,
                label=r.baseline_label,
                zorder=3,
            )

        # Current-lijn -> ZORGI Dark Blue (vol, prominent)
        if x_c and scores_c:
            ax.plot(
                x_c,
                scores_c,
                color=ZORGI_DARK_BLUE,
                alpha=1.0,
                linestyle="-",
                linewidth=2.0,
                marker="o",
                markersize=5,
                label=r.current_label,
                zorder=3,
            )

        # Verbindingssegment baseline -> current voor één doorgaande lijn
        if x_b and x_c and scores_b and scores_c:
            ax.plot(
                [x_b[-1], x_c[0]],
                [scores_b[-1], scores_c[0]],
                color=ZORGI_GREY_BLUE,
                linestyle="-",
                linewidth=1.2,
                alpha=0.5,
                zorder=2,
            )

        # Drempellijn Min. 4.0 -> ZORGI Bordeaux (functionele kleur, alle 4 subplots)
        ax.axhline(
            AVG_SCORE_MIN,
            color=ZORGI_BORDEAUX,
            linestyle="--",
            linewidth=1.0,
            alpha=0.7,
            label=self._t("sub1_min_label", val=f"{AVG_SCORE_MIN:.1f}"),
            zorder=4,
        )

        # Jaargrens-lijn -> vlak voor eerste maand van het nieuwe jaar, donkerder
        if x_b and x_c:
            scheiding = x_c[0] - 0.5  # direct naast de eerste nieuwe-jaar positie
            ax.axvline(
                scheiding,
                color=ZORGI_DARK_BLUE,
                linestyle=":",
                linewidth=1.4,
                alpha=0.6,
                zorder=1,
            )

        all_x = x_b + x_c
        all_labels = _build_tick_labels(baseline_pts) + _build_tick_labels(current_pts)
        ax.set_xticks(all_x)
        ax.set_xticklabels(
            all_labels,
            rotation=0,
            ha="center",
            fontsize=8.5,
            color=ZORGI_BODY_TEXT,
            fontweight="normal",
        )

        # Totaal tickets boven elk datapunt — subtiel, analoog aan subplot 3
        for xi, pt in zip(all_x, timeline, strict=False):
            if pt.total_tickets > 0 and pt.avg_score > 0:
                ax.text(
                    xi,
                    pt.avg_score + 0.08,
                    str(pt.total_tickets),
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    fontweight="normal",
                    color=ZORGI_GREY_BLUE,
                )

        ax.set_ylim(0, 6.0)
        ax.set_xlim(left=x_b[0] - 0.5, right=x_c[-1] + 0.5)
        ax.set_title(self._t("sub1_title"), color=ZORGI_GREY_BLUE, fontsize=11, fontweight="bold")
        ax.set_ylabel(self._t("sub1_ylabel"), fontsize=9, color=ZORGI_BODY_TEXT)

        handles, _ = ax.get_legend_handles_labels()
        ticket_handle = Line2D(
            [0],
            [0],
            color="none",
            marker=r"$\ 99$",
            markersize=8,
            markerfacecolor=ZORGI_GREY_BLUE,
            markeredgewidth=0,
            label=self._t("sub3_ticket_label"),
        )
        handles.append(ticket_handle)

        leg = ax.legend(
            handles=handles,
            loc="upper left",
            bbox_to_anchor=(0.01, 0.99),
            borderaxespad=0,
            framealpha=0.92,
            facecolor="white",
            edgecolor=ZORGI_GREY_BLUE,
            fontsize=8.5,
            labelcolor=ZORGI_BODY_TEXT,
        )
        _style_legend(leg)
        _style_ax(ax)

    # ------------------------------------------------------------------
    # Subplot 2 — % negatief per maand (staafdiagram)
    # ------------------------------------------------------------------

    def _draw_subplot2_pct_neg(self, ax, r: EvolutionResult) -> None:  # noqa: C901
        """Subplot 2: staafdiagram % negatief per maand, rood boven 15%."""
        from matplotlib.lines import Line2D  # noqa: PLC0415

        timeline = sorted(r.monthly_timeline, key=lambda p: p.period)

        if not timeline:
            ax.set_title(self._t("sub2_title"), color=ZORGI_GREY_BLUE, fontweight="bold")
            ax.text(
                0.5,
                0.5,
                self._t("sub2_no_data"),
                ha="center",
                va="center",
                transform=ax.transAxes,
                color=ZORGI_BODY_TEXT,
            )
            _style_ax(ax)
            return

        current_year = _extract_year(r.current_label)
        baseline_pts = [p for p in timeline if not p.period.startswith(current_year)]
        current_pts = [p for p in timeline if p.period.startswith(current_year)]

        if not baseline_pts and not current_pts:  # pragma: no cover
            mid = len(timeline) // 2
            baseline_pts = timeline[:mid]
            current_pts = timeline[mid:]

        n_b = len(baseline_pts)
        gap = 0  # direct aansluitend — geen lege positie
        x_b = list(range(n_b))
        x_c = list(range(n_b + gap, n_b + gap + len(current_pts)))

        def _bar_color(pct: float) -> str:
            """Crisis (>15%) -> ZORGI Red; herstel (<=15%) -> ZORGI Light Blue."""
            return FUNC_CRISIS if pct > HIGH_CRITICAL_MAX else ZORGI_LIGHT_BLUE

        for xi, pt in zip(x_b, baseline_pts, strict=False):
            ax.bar(
                xi,
                pt.pct_negative,
                color=_bar_color(pt.pct_negative),
                alpha=0.6,
                width=0.7,
                zorder=2,
            )

        for xi, pt in zip(x_c, current_pts, strict=False):
            ax.bar(
                xi,
                pt.pct_negative,
                color=_bar_color(pt.pct_negative),
                alpha=1.0,
                width=0.7,
                zorder=2,
            )

        # Drempellijn 15% -> ZORGI Bordeaux (identiek aan subplot 1)
        all_x = x_b + x_c
        if all_x:
            ax.axhline(
                HIGH_CRITICAL_MAX,
                color=ZORGI_BORDEAUX,
                linestyle="--",
                linewidth=1.0,
                alpha=0.7,
                label=self._t("sub2_threshold", val=f"{HIGH_CRITICAL_MAX:.0f}"),
                zorder=5,
            )

        # Jaargrens-lijn -> vlak voor eerste maand van het nieuwe jaar, donkerder
        if x_b and x_c:
            scheiding = x_c[0] - 0.5  # direct naast de eerste nieuwe-jaar positie
            ax.axvline(
                scheiding,
                color=ZORGI_DARK_BLUE,
                linestyle=":",
                linewidth=1.4,
                alpha=0.6,
                zorder=1,
            )

        max_pct = max(pt.pct_negative for pt in timeline) if timeline else HIGH_CRITICAL_MAX
        # Schaal y-as dynamisch op de data — niet altijd tot 100.
        # Minimum: 2x drempel zodat de drempellijn altijd goed zichtbaar is.
        # Maximum: 100 (percentage kan niet hoger).
        # Effect: bij lage waarden (< 20%) worden bars proportioneel leesbaar.
        # Extra headroom bovenaan houdt ticketaantal-annotaties zichtbaar.
        y_top = max(HIGH_CRITICAL_MAX * 2 + 4.0, min(104.0, max_pct + 8.0))
        ax.set_ylim(0, y_top)

        all_labels = _build_tick_labels(baseline_pts) + [""] * gap + _build_tick_labels(current_pts)
        tick_x = list(range(n_b + gap + len(current_pts)))
        ax.set_xticks(tick_x)
        ax.set_xticklabels(
            all_labels,
            rotation=0,
            ha="center",
            fontsize=8.5,
            color=ZORGI_BODY_TEXT,
            fontweight="normal",
        )

        if x_b and x_c:
            ax.set_xlim(left=x_b[0] - 0.5, right=x_c[-1] + 0.5)

        # Totaal tickets boven elke staaf — subtiel, analoog aan subplot 3
        for xi, pt in zip(all_x, timeline, strict=False):
            if pt.total_tickets > 0:
                ax.text(
                    xi,
                    pt.pct_negative + 1.5,
                    str(pt.total_tickets),
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    fontweight="normal",
                    color=ZORGI_GREY_BLUE,
                )

        ax.set_title(self._t("sub2_title"), color=ZORGI_GREY_BLUE, fontsize=11, fontweight="bold")
        ax.set_ylabel(self._t("sub2_ylabel"), fontsize=9, color=ZORGI_BODY_TEXT)

        handles, _ = ax.get_legend_handles_labels()
        ticket_handle = Line2D(
            [0],
            [0],
            color="none",
            marker=r"$\ 99$",
            markersize=8,
            markerfacecolor=ZORGI_GREY_BLUE,
            markeredgewidth=0,
            label=self._t("sub3_ticket_label"),
        )
        handles.append(ticket_handle)

        leg = ax.legend(
            handles=handles,
            loc="upper right",
            framealpha=0.92,
            facecolor="white",
            edgecolor=ZORGI_GREY_BLUE,
            fontsize=8.5,
            labelcolor=ZORGI_BODY_TEXT,
        )
        _style_legend(leg)
        _style_ax(ax)

    # ------------------------------------------------------------------
    # Subplot 3 — prioriteitscompositie per maand (gestapeld staafdiagram)
    # ------------------------------------------------------------------

    def _draw_subplot3_priority_composition(self, ax, r: EvolutionResult) -> None:  # noqa: C901
        """
        Subplot 3: gestapeld staafdiagram prioriteitscompositie per maand.

        Toont het procentuele aandeel van elke Jira-prioriteit per maand,
        gesorteerd op tijdlijn (baseline → huidig). Een lijndiagram bovenop
        toont de gecumuleerde HC-ratio (Blocker+Critical+Major) per maand.
        """
        import matplotlib.patches as mpatches  # noqa: PLC0415
        from matplotlib.lines import Line2D  # noqa: PLC0415

        timeline = sorted(r.monthly_timeline, key=lambda p: p.period)

        if not timeline:
            ax.set_title(self._t("sub3_title"), color=ZORGI_GREY_BLUE, fontweight="bold")
            ax.text(
                0.5,
                0.5,
                self._t("sub3_no_data"),
                ha="center",
                va="center",
                transform=ax.transAxes,
                color=ZORGI_BODY_TEXT,
            )
            _style_ax(ax)
            return

        current_year = _extract_year(r.current_label)
        baseline_pts = [p for p in timeline if not p.period.startswith(current_year)]
        current_pts = [p for p in timeline if p.period.startswith(current_year)]

        if not baseline_pts and not current_pts:  # pragma: no cover
            mid = len(timeline) // 2
            baseline_pts = timeline[:mid]
            current_pts = timeline[mid:]

        x_b = list(range(len(baseline_pts)))
        offset = len(x_b)
        x_c = list(range(offset, offset + len(current_pts)))
        all_x = x_b + x_c

        # -- Stap 1: data voorbereiden --
        pct_data: dict[str, list[float]] = {p: [] for p in PRIORITY_ORDER}
        hc_pct_per_maand: list[float] = []

        for pt in timeline:
            total = sum(pt.priority_counts.values()) if pt.priority_counts else 0
            if total == 0:
                for prio in PRIORITY_ORDER:
                    pct_data[prio].append(0.0)
                hc_pct_per_maand.append(0.0)
            else:
                for prio in PRIORITY_ORDER:
                    pct_data[prio].append(pt.priority_counts.get(prio, 0) / total * 100)
                hc = sum(pt.priority_counts.get(p, 0) for p in ["Blocker", "Critical"])
                hc_pct_per_maand.append(hc / total * 100)

        # Baseline = 0.6, current = 1.0
        alphas = [0.6 if pt.period < f"{current_year}-01" else 1.0 for pt in timeline]

        # -- Stap 2: gestapelde staven --
        bottoms = [0.0] * len(all_x)
        for prio in PRIORITY_ORDER:
            vals = pct_data[prio]
            # Teken per staaf afzonderlijk voor correcte alpha per maand
            for i, (xi, val, alpha) in enumerate(zip(all_x, vals, alphas, strict=False)):
                ax.bar(
                    xi,
                    val,
                    bottom=bottoms[i],
                    color=PRIORITY_COLORS.get(prio, ZORGI_GREY_BLUE),
                    alpha=alpha,
                    width=0.7,
                    zorder=2,
                )
                bottoms[i] += val

        # -- Stap 2b: totaal tickets annotatie bovenaan elke staaf --
        for xi, pt in zip(all_x, timeline, strict=False):
            total = sum(pt.priority_counts.values()) if pt.priority_counts else 0
            if total > 0:
                ax.text(
                    xi,
                    101.5,
                    str(total),
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    fontweight="normal",
                    color=ZORGI_GREY_BLUE,  # lichtere kleur — treedt terug achter de staven
                )

        # -- Stap 3: HC-ratio lijn bovenop --
        if all_x and hc_pct_per_maand:
            ax.plot(
                all_x,
                hc_pct_per_maand,
                color=ZORGI_BORDEAUX,
                linestyle="--",
                linewidth=1.2,
                alpha=0.85,
                marker="o",
                markersize=3,
                zorder=5,
                label=self._t("sub3_threshold"),
            )

        # -- Stap 4: drempellijn --
        ax.axhline(
            HIGH_CRITICAL_MAX,
            color=ZORGI_BORDEAUX,
            linestyle=":",
            linewidth=1.0,
            alpha=0.5,
            zorder=4,
        )

        # -- Stap 5: jaargrens-lijn --
        if x_b and x_c:
            scheiding = x_c[0] - 0.5
            ax.axvline(
                scheiding,
                color=ZORGI_DARK_BLUE,
                linestyle=":",
                linewidth=1.4,
                alpha=0.6,
                zorder=1,
            )

        # -- Stap 6: horizontale legenda boven de grafiek (Trivial → Blocker + HC-lijn) --
        _legenda_volgorde = ["Trivial", "Minor", "Major", "Critical", "Blocker"]
        prio_handles = [
            mpatches.Patch(color=PRIORITY_COLORS[p], label=p) for p in _legenda_volgorde
        ]
        hc_handle = Line2D(
            [0],
            [0],
            color=ZORGI_BORDEAUX,
            linestyle="--",
            linewidth=1.2,
            marker="o",
            markersize=3,
            label=self._t("sub3_threshold"),
        )
        ticket_handle = Line2D(
            [0],
            [0],
            color="none",
            marker=r"$\ 99$",
            markersize=8,
            markerfacecolor=ZORGI_GREY_BLUE,
            markeredgewidth=0,
            label=self._t("sub3_ticket_label"),
        )
        handles = [*prio_handles, hc_handle, ticket_handle]
        leg = ax.legend(
            handles=handles,
            loc="upper left",
            bbox_to_anchor=(0.0, 1.0),  # binnenin plotruimte, linkerbovenhoek
            borderaxespad=0.5,
            ncols=len(handles),  # alle items op één rij
            frameon=True,  # wit kader — identiek aan kwadranten 1, 2 en 4
            framealpha=0.92,
            facecolor="white",
            edgecolor=ZORGI_GREY_BLUE,
            fontsize=7.5,  # licht verkleind zodat 6 items op één rij passen
            labelcolor=ZORGI_BODY_TEXT,
            handlelength=1.0,
            handletextpad=0.4,
            columnspacing=0.8,
        )
        _style_legend(leg)

        # -- Stap 7: assen en titels --
        all_labels = _build_tick_labels(baseline_pts) + _build_tick_labels(current_pts)
        ax.set_xticks(all_x)
        ax.set_xticklabels(
            all_labels,
            rotation=0,
            ha="center",
            fontsize=8.5,
            color=ZORGI_BODY_TEXT,
            fontweight="normal",
        )
        if x_b and x_c:
            ax.set_xlim(left=x_b[0] - 0.5, right=x_c[-1] + 0.5)
        ax.set_ylim(0, 118)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_title(
            self._t("sub3_title"),
            color=ZORGI_GREY_BLUE,
            fontsize=11,
            fontweight="bold",
            fontfamily="DejaVu Sans",  # #1 — consistent met aslabels en legenda
        )
        ax.set_ylabel(self._t("sub3_ylabel"), fontsize=9, color=ZORGI_BODY_TEXT)
        _style_ax(ax)

    # ------------------------------------------------------------------
    # Subplot 4 — top/bottom ziekenhuizen (horizontaal staafdiagram)
    # ------------------------------------------------------------------

    def _draw_subplot4_hospitals(self, ax, r: EvolutionResult) -> None:  # noqa: C901
        """Subplot 4: horizontaal staafdiagram delta per ziekenhuis (beste -> slechtste).

        Ziekenhuizen zonder baseline-data (baseline_total == 0) worden uitgesloten
        van de delta-ranking. Hun delta zou vergeleken worden met de default 0.0-score,
        wat statistisch misleidend is. Ze worden gelogd als 'nieuwe instappers'.
        Toekomstige verbetering: apart tonen als 'nieuwe instappers'-sectie (backlog).
        """
        # Stap 1: beide periodes aanwezig én baseline heeft effectieve data
        vergelijkbaar = [
            h
            for h in r.hospital_comparison
            if h.current_score is not None and h.baseline_score is not None and h.baseline_total > 0
        ]

        # Nieuwe instappers (2026-data maar geen 2025-baseline) apart loggen
        nieuwe_instappers = [
            h.hospital
            for h in r.hospital_comparison
            if h.current_score is not None and h.baseline_total == 0
        ]
        if nieuwe_instappers:
            logger.info(
                f"[Subplot 4] {len(nieuwe_instappers)} nieuwe instapper(s) uitgesloten "
                f"uit delta-ranking (geen baseline-data): {nieuwe_instappers}"
            )

        if not vergelijkbaar:
            ax.set_title(self._t("sub4_title"), color=ZORGI_GREY_BLUE, fontweight="bold")
            ax.text(
                0.5,
                0.5,
                self._t("sub4_no_data"),
                ha="center",
                va="center",
                transform=ax.transAxes,
                color=ZORGI_BODY_TEXT,
            )
            _style_ax(ax)
            return

        # current_score is gegarandeerd niet-None door vergelijkbaar-filter hierboven
        # 4-tuple: (hospital, delta, baseline_total, current_total)
        met_delta = [
            (
                h.hospital,
                round(h.current_score - h.baseline_score, 2),  # type: ignore[operator]
                h.baseline_total,
                h.current_total,
            )
            for h in vergelijkbaar
        ]
        met_delta.sort(key=lambda x: x[1], reverse=True)

        if len(met_delta) > _MAX_HOSPITALS:
            half = _MAX_HOSPITALS // 2
            top = met_delta[:half]
            bottom = met_delta[-half:]
            seen: set[str] = set()
            gefilterd: list[tuple[str, float, int, int]] = []
            for item in top + bottom:
                if item[0] not in seen:
                    seen.add(item[0])
                    gefilterd.append(item)
            met_delta = sorted(gefilterd, key=lambda x: x[1], reverse=True)

        ziekenhuizen = [item[0] for item in met_delta]
        deltas = [item[1] for item in met_delta]
        baseline_totals = [item[2] for item in met_delta]
        current_totals = [item[3] for item in met_delta]

        # Optie B: FUNC_POSITIVE (groen) voor verbetering, FUNC_NEGATIVE (rood) voor verslechtering
        kleuren = [FUNC_POSITIVE if d > 0 else FUNC_NEGATIVE for d in deltas]
        y_pos = list(range(len(ziekenhuizen)))

        ax.barh(y_pos, deltas, color=kleuren, alpha=0.85, height=0.6, zorder=2)
        # Nul-lijn -> ZORGI Bordeaux (identiek aan drempellijnen subplot 1-3)
        ax.axvline(0, color=ZORGI_BORDEAUX, linestyle="--", linewidth=1.0, alpha=0.7, zorder=5)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(ziekenhuizen, fontsize=7.5, color=ZORGI_BODY_TEXT, fontweight="normal")
        ax.tick_params(axis="y", which="both", length=0, labelsize=7.5, colors=ZORGI_BODY_TEXT)
        for lbl in ax.get_yticklabels():
            lbl.set_color(ZORGI_BODY_TEXT)
            lbl.set_alpha(1.0)
            lbl.set_fontweight("normal")

        ax.set_title(
            self._t("sub4_title"),
            color=ZORGI_GREY_BLUE,
            fontsize=11,
            fontweight="bold",
        )
        ax.set_xlabel(self._t("sub4_xlabel"), fontsize=9, color=ZORGI_BODY_TEXT)

        for yi, delta, b_tot, c_tot in zip(
            y_pos, deltas, baseline_totals, current_totals, strict=False
        ):
            # Delta-waarde aan het einde van de bar
            delta_label = _fmt_delta(delta)
            offset = 0.03 if delta >= 0 else -0.03
            ha_delta = "left" if delta >= 0 else "right"
            ax.text(
                delta + offset,
                yi,
                delta_label,
                ha=ha_delta,
                va="center",
                fontsize=8,
                color=ZORGI_BODY_TEXT,
                fontweight="normal",
                clip_on=False,
            )

            # Ticket-count naast de nul-lijn: #{baseline}/{current}
            # Positieve of nul bar (>= 0) → tekst links van nul (vrij vlak)
            # Negatieve bar (< 0)          → tekst rechts van nul (vrij vlak)
            ticket_label = f"#{b_tot}/{c_tot}"
            if delta >= 0:
                ax.text(
                    -0.06,
                    yi,
                    ticket_label,
                    ha="right",
                    va="center",
                    fontsize=7.5,
                    color=ZORGI_GREY_BLUE,
                    fontweight="normal",
                    clip_on=False,
                )
            else:
                ax.text(
                    0.06,
                    yi,
                    ticket_label,
                    ha="left",
                    va="center",
                    fontsize=7.5,
                    color=ZORGI_GREY_BLUE,
                    fontweight="normal",
                    clip_on=False,
                )

        min_delta = min(deltas) if deltas else -1.0
        max_delta = max(deltas) if deltas else 1.0
        ax.set_xlim(left=min_delta - 0.5, right=max_delta + 0.8)

        # Legenda rechtsboven — zelfde stijl als de andere kwadranten
        # Dummy invisible handle zodat ax.legend() enkel de tekstlabel toont
        from matplotlib.lines import Line2D  # noqa: PLC0415

        dummy_value = Line2D([0], [0], color="none", label="#99/99")
        dummy_explainer = Line2D(
            [0],
            [0],
            color="none",
            label=self._t(
                "sub4_ticket_explainer",
                baseline=r.baseline_label,
                current=r.current_label,
            ),
        )
        leg = ax.legend(
            handles=[dummy_value, dummy_explainer],
            loc="upper right",
            framealpha=0.92,
            facecolor="white",
            edgecolor=ZORGI_GREY_BLUE,
            fontsize=8.5,
            labelcolor=ZORGI_BODY_TEXT,
            handlelength=0,
            handletextpad=0,
            ncols=2,
            columnspacing=0.4,
        )
        _style_legend(leg)
        # Voor subplot 4 moet de placeholder grijs zijn, maar de uitleg zwart blijven.
        legend_texts = leg.get_texts()
        if legend_texts:
            legend_texts[0].set_color(ZORGI_GREY_BLUE)
        if len(legend_texts) > 1:
            legend_texts[1].set_color(ZORGI_BODY_TEXT)

        _style_ax(ax)
