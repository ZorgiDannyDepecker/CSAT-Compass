"""
EvolutionExporter voor CSAT-Compass.

Genereert evolutie-rapporten in Nederlandstalige of Franstalige markdown
vanuit een EvolutionResult-object via Jinja2-templates en NL/FR i18n.

Talen: nl (Nederlands) + fr (Frans) — conform ZORGI tweetaligheidsbeleid.
Templates: docs/templates/evolutie-{lang}.md.j2
Output: output/evolutie-YYYY-{lang}.md

Fase 3g: InsightsGenerator geïntegreerd voor narratieve secties (beslissing 7).
"""

from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger

from csat.config.pillars import PILLAR_REGISTRY
from csat.config.settings import OUTPUT_PATH, TEMPLATES_PATH
from csat.core.analysers.evolution_result import EvolutionResult, KpiStatus
from csat.core.exporters.report_exporter import _format_date, _format_number
from csat.core.insights import InsightsGenerator
from csat.i18n import SUPPORTED_LANGS, load_translations


def _fmt_delta(value: float, decimals: int = 1) -> str:
    """
    Formatteer een delta-waarde met expliciete + of - prefix (ZORGI-getalnotatie).

    Args:
        value:    Delta-waarde
        decimals: Aantal decimalen

    Returns:
        Geformatteerde string, bv. +1,70 of -0,50

    Examples:
        >>> _fmt_delta(1.70, 2)
        '+1,70'
        >>> _fmt_delta(-0.5, 1)
        '-0,5'
    """
    sign = "+" if value >= 0 else ""
    return f"{sign}{_format_number(value, decimals)}"


def _hospital_status_label(lang: str):
    """
    Geeft een callable terug die een score omzet naar een statuslabel.

    Drempelwaarden:
        score == 5,00 → Excellent
        score >= 4,50 → Uitstekend / Excellent (FR)
        score >= 4,00 → Grenswaarde / Limite (FR)
        score >= 3,00 → Aandacht / Attention (FR)
        score <  3,00 → Kritiek / Critique (FR)

    Args:
        lang: 'nl' of 'fr'

    Returns:
        Callable (score: float) → str
    """
    if lang == "fr":
        _map = [
            (5.00, "✅ Excellent"),
            (4.50, "✅ Très bien"),
            (4.00, "🟡 Limite"),
            (3.00, "🟡 Attention"),
            (0.00, "🔴 Critique"),
        ]
    else:
        _map = [
            (5.00, "✅ Excellent"),
            (4.50, "✅ Uitstekend"),
            (4.00, "🟡 Grenswaarde"),
            (3.00, "🟡 Aandacht"),
            (0.00, "🔴 Kritiek"),
        ]

    def _label(score: float) -> str:
        for threshold, label in _map:
            if score >= threshold:
                return label
        return "—"  # pragma: no cover

    return _label


class EvolutionExporter:
    """
    Genereert CSAT-evolutierapporten in Nederlandstalige of Franstalige markdown.

    Laadt Jinja2-templates uit docs/templates/ en i18n-vertalingen uit
    src/csat/i18n/, en schrijft de output naar output/evolutie-YYYY-{lang}.md.

    Args:
        lang:            Taalcode — 'nl' (standaard) of 'fr'
        templates_path:  Pad naar de Jinja2-templates (standaard TEMPLATES_PATH)
        output_path:     Uitvoermap voor rapporten (standaard OUTPUT_PATH)
    """

    def __init__(
        self,
        lang: str = "nl",
        templates_path: Path | None = None,
        output_path: Path | None = None,
    ) -> None:
        if lang not in SUPPORTED_LANGS:
            raise ValueError(f"Niet-ondersteunde taal: '{lang}' — kies uit {SUPPORTED_LANGS}")

        self._lang = lang
        self._templates_path = Path(templates_path) if templates_path else TEMPLATES_PATH
        self._output_path = Path(output_path) if output_path else OUTPUT_PATH
        self._translations = load_translations(lang)

        self._env = Environment(
            loader=FileSystemLoader(str(self._templates_path)),
            autoescape=select_autoescape([]),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._env.filters["fmt"] = _format_number
        self._env.filters["fmt_delta"] = _fmt_delta

    # ------------------------------------------------------------------
    # Publieke methoden
    # ------------------------------------------------------------------

    def render(self, result: EvolutionResult, chart_filename: str = "") -> str:
        """
        Render het evolutierapport als markdown-string (zonder bestandsschrijving).

        Args:
            result:         EvolutionResult van een EvolutionAnalyser.analyse() aanroep
            chart_filename: Bestandsnaam van de bijbehorende PNG (inclusief tijdstempel).
                            Leeg = geen grafiekreferentie in rapport.

        Returns:
            Volledige markdown-string van het rapport
        """
        template_name = f"evolutie-{self._lang}.md.j2"
        template = self._env.get_template(template_name)
        context = self._build_context(result, chart_filename=chart_filename)
        return template.render(**context)

    def export(
        self,
        result: EvolutionResult,
        year: str | None = None,
        ts_suffix: str = "",
    ) -> Path:
        """
        Render het rapport en schrijf het naar de outputmap.

        Bestandsnaamconventie: evolutie-{pillar}-{jaar}-{lang}[{ts_suffix}].md (NL)
                               evolution-{pillar}-{year}-{lang}[{ts_suffix}].md (FR)
        De bijbehorende PNG krijgt dezelfde ts_suffix — zo blijft de referentie altijd correct.

        Args:
            result:    EvolutionResult van een pijleranalyse
            year:      Jaarlabel voor bestandsnaam (standaard: current_label of huidig jaar)
            ts_suffix: Tijdstempel-suffix voor bestandsnaam én PNG-referentie
                       (bv. '_20260401-1435'). Leeg = geen tijdstempel.

        Returns:
            Absoluut pad naar het gegenereerde bestand
        """
        jaar = year or result.current_label or str(datetime.now(tz=UTC).year)
        jaar_safe = jaar.replace(" ", "-").replace("/", "-")
        # Taalafhankelijk bestandsprefix: NL = evolutie, FR = evolution
        prefix = "evolution" if self._lang == "fr" else "evolutie"
        stem = f"{prefix}-{result.pillar}-{jaar_safe}-{self._lang}"
        output_file = self._output_path / f"{stem}{ts_suffix}.md"
        chart_filename = f"{stem}{ts_suffix}.png"

        content = self.render(result, chart_filename=chart_filename)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")
        logger.info(f"[EvolutionExporter:{self._lang}] Rapport geschreven → {output_file}")
        return output_file

    # ------------------------------------------------------------------
    # Intern — context opbouwen
    # ------------------------------------------------------------------

    def _build_context(self, result: EvolutionResult, chart_filename: str = "") -> dict:
        """
        Bouw de Jinja2-templatecontext op vanuit een EvolutionResult.

        Args:
            result: EvolutionResult na evolutie-analyse

        Returns:
            Dict met alle template-variabelen
        """
        t = self._translations
        generated_date = _format_date(datetime.now(tz=UTC).date())

        pillar_info = PILLAR_REGISTRY.get(result.pillar, {})
        if self._lang == "fr":
            pillar_name = pillar_info.get(
                "report_name_fr", pillar_info.get("name_fr", result.pillar.upper())
            )
        else:
            pillar_name = pillar_info.get(
                "report_name", pillar_info.get("name", result.pillar.upper())
            )

        # KPI-statuslabels
        status_labels = t.get("evolution", {}).get("status", {})
        kpi_status_map = {
            KpiStatus.OK: status_labels.get("ok", "✅ OK"),
            KpiStatus.WARNING: status_labels.get("warning", "⚠️ Aandacht"),
            KpiStatus.AT_RISK: status_labels.get("at_risk", "🔴 Risico"),
            KpiStatus.UNKNOWN: status_labels.get("unknown", "⏳ Onbekend"),
        }

        def kpi_label(key: str) -> str:
            return str(kpi_status_map.get(result.kpi_status.get(key, KpiStatus.UNKNOWN), "—"))

        # Trend-breedte label
        trend_labels = t.get("evolution", {}).get("trend", {})
        trend_breadth_label = trend_labels.get(result.trend_breadth, result.trend_breadth)

        # Delta's
        delta_pct_pos = round(result.current_pct_positive - result.baseline_pct_positive, 1)
        delta_pct_neg = round(result.current_pct_negative - result.baseline_pct_negative, 1)
        delta_hc = round(result.current_hc_ratio - result.baseline_hc_ratio, 1)
        delta_response = round(
            result.current_avg_response_days - result.baseline_avg_response_days, 1
        )

        # --- Fase 3g: InsightsGenerator aanroepen (beslissing 7) ---
        # Seed = rapportdatum als int voor reproduceerbaarheid bij herhaalde runs
        seed = int(datetime.now(tz=UTC).strftime("%Y%m%d"))
        insights_gen = InsightsGenerator(i18n=t, lang=self._lang, seed=seed)
        insights = insights_gen.generate(result)

        # KPI target tracking labels
        target_tracking_labels = t.get("evolution", {}).get("target_tracking", {})

        def target_status_label(status: str) -> str:
            return str(target_tracking_labels.get(status, status))

        def kpi_target_name(name: str) -> str:
            return str(target_tracking_labels.get("kpi_names", {}).get(name, name))

        # Kritieke accounts (score < 3,0★) en aandachtsaccounts (3,0★ ≤ score < 4,0★)
        # Gesorteerd op score oplopend — min. 1 ticket in huidige periode
        _crit_thr = 3.0
        _attn_thr = 4.0
        critical_hospitals = sorted(
            [
                h
                for h in result.hospital_comparison
                if h.current_score is not None
                and h.current_total > 0
                and h.current_score < _crit_thr
            ],
            key=lambda h: h.current_score or 0.0,
        )
        attention_hospitals = sorted(
            [
                h
                for h in result.hospital_comparison
                if h.current_score is not None
                and h.current_total > 0
                and _crit_thr <= h.current_score < _attn_thr
            ],
            key=lambda h: h.current_score or 0.0,
        )

        return {
            "t": t,
            "lang": self._lang,
            "pillar_id": result.pillar,
            "generated_date": generated_date,
            "pillar_name": pillar_name,
            "baseline_label": result.baseline_label,
            "current_label": result.current_label,
            # Kerncijfers
            "baseline_total": result.baseline_total,
            "current_total": result.current_total,
            "baseline_avg_score": result.baseline_avg_score,
            "current_avg_score": result.current_avg_score,
            "delta_avg_score": result.delta_avg_score,
            "baseline_pct_positive": result.baseline_pct_positive,
            "current_pct_positive": result.current_pct_positive,
            "baseline_pct_negative": result.baseline_pct_negative,
            "current_pct_negative": result.current_pct_negative,
            "baseline_hc_ratio": result.baseline_hc_ratio,
            "current_hc_ratio": result.current_hc_ratio,
            "baseline_avg_response_days": result.baseline_avg_response_days,
            "current_avg_response_days": result.current_avg_response_days,
            "baseline_n_hospitals": result.baseline_n_hospitals,
            "current_n_hospitals": result.current_n_hospitals,
            # Delta's
            "delta_pct_pos": delta_pct_pos,
            "delta_pct_neg": delta_pct_neg,
            "delta_hc": delta_hc,
            "delta_response": delta_response,
            # KPI-status strings
            "kpi_status_avg_baseline": kpi_label("avg_score_baseline"),
            "kpi_status_avg_current": kpi_label("avg_score_current"),
            "kpi_status_hc_baseline": kpi_label("high_critical_baseline"),
            "kpi_status_hc_current": kpi_label("high_critical_current"),
            "kpi_status_trend": kpi_label("trend"),
            # Tijdlijn + breakdowns
            "monthly_timeline": result.monthly_timeline,
            "by_issue_type": result.by_issue_type,
            "by_priority": result.by_priority,
            "response_time_by_score": result.response_time_by_score,
            # Ziekenhuizen
            "hospital_comparison": sorted(result.hospital_comparison, key=lambda h: h.hospital),
            "hospitals_disappeared": result.hospitals_disappeared,
            "hospitals_new": result.hospitals_new,
            # Thema's
            "negative_themes": result.negative_themes,
            # Trend
            "trend_is_structural": result.trend_is_structural,
            "trend_breadth": result.trend_breadth,
            "trend_breadth_label": trend_breadth_label,
            # --- Fase 3g: nieuwe context-variabelen ---
            "insights": insights,
            "baseline_summary": result.baseline_summary,
            "current_summary": result.current_summary,
            "score_distribution_baseline": result.score_distribution_baseline,
            "score_distribution_current": result.score_distribution_current,
            "response_time_insight": result.response_time_insight,
            "negative_cases": result.negative_cases,
            "kpi_targets": result.kpi_targets,
            "benchmark_h2": result.benchmark_h2,
            "hospital_shortlist": result.hospital_shortlist,
            "hospital_retention_pct": result.hospital_retention_pct,
            # KPI target tracking hulpfuncties
            "target_status_label": target_status_label,
            "kpi_target_name": kpi_target_name,
            # Grafiek
            "chart_filename": chart_filename,
            # Top5 / Bottom5 ziekenhuizen
            "hospital_top5": result.hospital_top5,
            "hospital_bottom5": result.hospital_bottom5,
            "hospital_ranking_min_tickets": result.hospital_ranking_min_tickets,
            "hospital_bottom_min_tickets": result.hospital_bottom_min_tickets,
            "hospital_status": _hospital_status_label(self._lang),
            # Kritieke en aandachtsaccounts (score-categorieën)
            "critical_hospitals": critical_hospitals,
            "attention_hospitals": attention_hospitals,
        }
