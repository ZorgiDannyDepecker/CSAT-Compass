"""
Matrix exporter voor CSAT-Compass.

Genereert vergelijkingsmatrices over meerdere periodes vanuit een lijst
van KpiResult-objecten via Jinja2-templates en NL/FR i18n-vertalingen.

Talen: nl (Nederlands) + fr (Frans) — conform ZORGI tweetaligheidsbeleid.
Templates: docs/templates/matrix-{lang}.md.j2
Output: output/matrix-YYYY-{lang}.md
"""

from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger

from csat.config.pillars import PILLAR_REGISTRY
from csat.config.settings import OUTPUT_PATH, TEMPLATES_PATH
from csat.core.analysers.base_analyser import KpiResult
from csat.core.exporters.report_exporter import _format_date, _format_number, _format_period_label
from csat.i18n import SUPPORTED_LANGS, load_translations

# Drempel voor trendbepaling (absoluut verschil in gem. score)
_TREND_THRESHOLD = 0.1


class MatrixExporter:
    """
    Genereert CSAT-vergelijkingsmatrices in Nederlandstalige of Franstalige markdown.

    Laadt Jinja2-templates uit docs/templates/ en i18n-vertalingen uit
    src/csat/i18n/, en schrijft de output naar output/matrix-YYYY-{lang}.md.

    Args:
        lang:            Taalcode — 'nl' (standaard) of 'fr'
        templates_path:  Pad naar de Jinja2-templates (standaard TEMPLATES_PATH)
        output_path:     Uitvoermap voor matrices (standaard OUTPUT_PATH)
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
            autoescape=select_autoescape([]),  # Markdown — geen HTML-escaping
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._env.filters["fmt"] = _format_number
        self._env.filters["fmt_mom"] = lambda v, d=1: ("+" if v >= 0 else "") + _format_number(v, d)

    # ------------------------------------------------------------------
    # Publieke methoden
    # ------------------------------------------------------------------

    def render(self, results: list[KpiResult]) -> str:
        """
        Render de matrix als markdown-string (zonder bestandsschrijving).

        Args:
            results: Lijst van KpiResult — meerdere periodes van dezelfde pijler

        Returns:
            Volledige markdown-string van de matrix

        Raises:
            ValueError: Als de lijst leeg is
        """
        if not results:
            raise ValueError("Lege resultatenlijst — minstens één KpiResult vereist")

        template_name = f"matrix-{self._lang}.md.j2"
        template = self._env.get_template(template_name)
        context = self._build_context(results)
        return template.render(**context)

    def export(self, results: list[KpiResult]) -> Path:
        """
        Render de matrix en schrijf naar de outputmap.

        Bestandsnaamconventie: matrix-YYYY-{lang}.md
        Aanmaakpad wordt aangemaakt als het nog niet bestaat.

        Args:
            results: Lijst van KpiResult — meerdere periodes van dezelfde pijler

        Returns:
            Absoluut pad naar het gegenereerde bestand
        """
        year = results[0].period[:4]
        content = self.render(results)
        output_file = self._output_path / f"matrix-{year}-{self._lang}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")
        logger.info(f"[MatrixExporter:{self._lang}] Matrix geschreven → {output_file}")
        return output_file

    # ------------------------------------------------------------------
    # Interne helpers — periode-groepering
    # ------------------------------------------------------------------

    def _period_to_quarter(self, period_raw: str) -> str:
        """
        Zet 'YYYY-MM' om naar kwartaallabel 'Q1 YYYY'.

        Args:
            period_raw: Periodestring 'YYYY-MM'

        Returns:
            Kwartaallabel, bv. 'Q1 2025'
        """
        jaar = int(period_raw[:4])
        maand = int(period_raw[5:7])
        kwartaal = (maand - 1) // 3 + 1
        return f"Q{kwartaal} {jaar}"

    def _period_to_year(self, period_raw: str) -> str:
        """
        Geeft het jaar terug als string uit 'YYYY-MM'.

        Args:
            period_raw: Periodestring 'YYYY-MM'

        Returns:
            Jaar als string, bv. '2025'
        """
        return period_raw[:4]

    def _ordered_groups(self, periods_raw: list[str], group_fn) -> list[str]:
        """
        Geeft een geordende, deduplicate lijst van groepslabels terug.

        Args:
            periods_raw: Gesorteerde lijst van 'YYYY-MM' strings
            group_fn:    Functie die een period_raw omzet naar een groepslabel

        Returns:
            Geordende lijst van unieke groepslabels
        """
        seen: list[str] = []
        for p in periods_raw:
            label = group_fn(p)
            if label not in seen:
                seen.append(label)
        return seen

    def _aggregate_matrix(
        self,
        hospitals: list[str],
        periods_raw: list[str],
        score_lookup: dict,
        group_fn,
        group_labels: list[str],
    ) -> tuple[
        dict[str, dict[str, float | None]],
        dict[str, dict[str, float | None]],
        dict[str, dict[str, float | None]],
    ]:
        """
        Aggregeer scores, H/C-ratio's en volumes per groep (kwartaal of jaar).

        Aggregatiemethode:
        - Gem. score : gewogen gemiddelde op basis van scored_ticketsdf        - H/C-ratio  : totaal high_critical_count / totaal total_tickets * 100
        - Volume     : som van total_tickets

        Args:
            hospitals:    Lijst van ziekenhuisnamen
            periods_raw:  Gesorteerde lijst van 'YYYY-MM' periodestrings
            score_lookup: Dict {period_raw: per_hospital_dict}
            group_fn:     Functie die period_raw omzet naar groepslabel
            group_labels: Geordende lijst van groepslabels

        Returns:
            Tuple van drie matrices (score, hc, volume) als
            dict {hospital: {groepslabel: float | None}}
        """
        score_agg: dict[str, dict[str, float | None]] = {
            h: {g: None for g in group_labels} for h in hospitals
        }
        hc_agg: dict[str, dict[str, float | None]] = {
            h: {g: None for g in group_labels} for h in hospitals
        }
        vol_agg: dict[str, dict[str, float | None]] = {
            h: {g: None for g in group_labels} for h in hospitals
        }

        for hospital in hospitals:
            for group in group_labels:
                periods_in_group = [p for p in periods_raw if group_fn(p) == group]
                total_tickets = 0
                total_scored = 0
                weighted_score_sum = 0.0
                total_hc = 0
                has_data = False

                for p in periods_in_group:
                    per_h = score_lookup.get(p, {}).get(hospital)
                    if per_h is None:
                        continue
                    has_data = True
                    t = per_h.get("total_tickets", 0)
                    s = per_h.get("scored_tickets", 0)
                    avg = per_h.get("avg_score", 0.0)
                    hc = per_h.get("high_critical_count", 0)
                    total_tickets += t
                    total_scored += s
                    weighted_score_sum += avg * s
                    total_hc += hc

                if has_data and total_tickets > 0:
                    vol_agg[hospital][group] = float(total_tickets)
                    hc_agg[hospital][group] = (total_hc / total_tickets) * 100.0
                if has_data and total_scored > 0:
                    score_agg[hospital][group] = weighted_score_sum / total_scored

        return score_agg, hc_agg, vol_agg

    # ------------------------------------------------------------------
    # Interne helper — context opbouwen
    # ------------------------------------------------------------------

    def _build_context(self, results: list[KpiResult]) -> dict:  # noqa: C901
        """
        Bouw de Jinja2-templatecontext op vanuit een lijst van KpiResult-objecten.

        Args:
            results: Lijst van KpiResult gesorteerd op periode

        Returns:
            Dict met alle template-variabelen
        """
        t = self._translations
        months: list = t["months"]

        # Periodes chronologisch sorteren
        sorted_results = sorted(results, key=lambda r: r.period)
        periods_raw = [r.period for r in sorted_results]
        periods = [_format_period_label(p, months) for p in periods_raw]

        # Pijlerinfo ophalen
        pillar = sorted_results[0].pillar
        pillar_info = PILLAR_REGISTRY.get(pillar, {})
        if self._lang == "fr":
            pillar_name = pillar_info.get(
                "report_name_fr", pillar_info.get("name_fr", pillar.upper())
            )
        else:
            pillar_name = pillar_info.get("report_name", pillar_info.get("name", pillar.upper()))

        # Alle unieke ziekenhuizen over alle periodes — ONBEKEND altijd onderaan
        all_hospitals: set[str] = set()
        for r in sorted_results:
            all_hospitals.update(r.per_hospital.keys())
        hospitals = sorted(all_hospitals, key=lambda h: (h == "ONBEKEND", h))

        # Lookups per ziekenhuis x periode opbouwen
        score_lookup: dict[str, dict[str, dict]] = {
            r.period: r.per_hospital for r in sorted_results
        }

        score_matrix: dict[str, dict[str, float | None]] = {}
        hc_matrix: dict[str, dict[str, float | None]] = {}
        volume_matrix: dict[str, dict[str, float | None]] = {}

        for hospital in hospitals:
            score_matrix[hospital] = {}
            hc_matrix[hospital] = {}
            volume_matrix[hospital] = {}
            for p_raw, p_label in zip(periods_raw, periods, strict=False):
                per_h = score_lookup.get(p_raw, {}).get(hospital)
                score_matrix[hospital][p_label] = per_h.get("avg_score") if per_h else None
                hc_matrix[hospital][p_label] = per_h.get("high_critical_ratio") if per_h else None
                volume_matrix[hospital][p_label] = (
                    float(per_h.get("total_tickets", 0)) if per_h else None
                )

        # Rankings: gemiddelde score over alle periodes, ONBEKEND uitgesloten
        ranking_data: list[tuple[int, str, float]] = []
        for hospital in hospitals:
            if hospital == "ONBEKEND":
                continue
            scores = [v for v in score_matrix[hospital].values() if v is not None]
            if scores:
                overall_avg = sum(scores) / len(scores)
                ranking_data.append((0, hospital, overall_avg))

        ranking_data.sort(key=lambda x: x[2], reverse=True)
        rankings = [(i + 1, h, avg) for i, (_, h, avg) in enumerate(ranking_data)]

        # Trend: vergelijk eerste en laatste periode per ziekenhuis
        trend_labels = t["matrix"]["trends"]
        trends: list[tuple[str, str]] = []
        for hospital in hospitals:
            scores_chronological: list[float] = [
                v for p in periods if (v := score_matrix[hospital][p]) is not None
            ]
            if len(scores_chronological) < 2:
                trend_label = trend_labels["na"]
            else:
                delta = scores_chronological[-1] - scores_chronological[0]
                if delta > _TREND_THRESHOLD:
                    trend_label = trend_labels["up"]
                elif delta < -_TREND_THRESHOLD:
                    trend_label = trend_labels["down"]
                else:
                    trend_label = trend_labels["stable"]
            trends.append((hospital, trend_label))

        # Kwartaaloverzicht
        quarters = self._ordered_groups(periods_raw, self._period_to_quarter)
        quarterly_score_matrix, quarterly_hc_matrix, quarterly_volume_matrix = (
            self._aggregate_matrix(
                hospitals, periods_raw, score_lookup, self._period_to_quarter, quarters
            )
        )

        # Jaaroverzicht
        year_labels = self._ordered_groups(periods_raw, self._period_to_year)
        yearly_score_matrix, yearly_hc_matrix, yearly_volume_matrix = self._aggregate_matrix(
            hospitals, periods_raw, score_lookup, self._period_to_year, year_labels
        )

        year = sorted_results[0].period[:4]
        generated_date = _format_date(datetime.now(tz=UTC).date())

        return {
            "t": t,
            "year": year,
            "generated_date": generated_date,
            "pillar": pillar,
            "pillar_name": pillar_name,
            "periods": periods,
            "hospitals": hospitals,
            "score_matrix": score_matrix,
            "hc_matrix": hc_matrix,
            "volume_matrix": volume_matrix,
            "rankings": rankings,
            "trends": trends,
            "quarters": quarters,
            "quarterly_score_matrix": quarterly_score_matrix,
            "quarterly_hc_matrix": quarterly_hc_matrix,
            "quarterly_volume_matrix": quarterly_volume_matrix,
            "year_labels": year_labels,
            "yearly_score_matrix": yearly_score_matrix,
            "yearly_hc_matrix": yearly_hc_matrix,
            "yearly_volume_matrix": yearly_volume_matrix,
            "lang": self._lang,
        }
