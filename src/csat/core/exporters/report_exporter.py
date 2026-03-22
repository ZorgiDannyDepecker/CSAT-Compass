"""
Report exporter voor CSAT-Compass.

Genereert maandelijkse markdown-rapporten vanuit KpiResult-objecten
via Jinja2-templates en NL/FR i18n-vertalingen.

Talen: nl (Nederlands) + fr (Frans) — conform ZORGI tweetaligheidsbeleid.
Templates: docs/templates/rapport-{lang}.md.j2
Output: output/rapport-YYYY-MM-{lang}.md
"""

from datetime import UTC, date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger

from csat.config.pillars import PILLAR_REGISTRY
from csat.config.settings import OUTPUT_PATH, TEMPLATES_PATH
from csat.core.analysers.base_analyser import KpiResult
from csat.i18n import SUPPORTED_LANGS, load_translations

# ---------------------------------------------------------------------------
# Hulpfuncties — getal- en datumformattering
# ---------------------------------------------------------------------------


def _format_number(value: float, decimals: int = 1) -> str:
    """
    Formatteer een getal conform ZORGI-standaard: punt als duizendtalscheider,
    komma als decimaalteken.

    Args:
        value:    Te formatteren getal
        decimals: Aantal decimalen (standaard 1)

    Returns:
        Geformatteerde string, bv. 1.234,5 of 0,00

    Examples:
        >>> _format_number(1234.5, 1)
        '1.234,5'
        >>> _format_number(15.3, 1)
        '15,3'
    """
    formatted = f"{value:,.{decimals}f}"  # Python US-formaat: "1,234.5"
    return formatted.replace(",", "TSEP").replace(".", ",").replace("TSEP", ".")


def _format_mom(value: float, decimals: int = 1) -> str:
    """
    Formatteer een MoM-trendwaarde met expliciete + of - prefix.

    Args:
        value:    MoM-waarde (positief = verbetering)
        decimals: Aantal decimalen (standaard 1)

    Returns:
        Geformatteerde string, bv. +0,2 of -0,5

    Examples:
        >>> _format_mom(0.2, 1)
        '+0,2'
        >>> _format_mom(-0.5, 1)
        '-0,5'
    """
    sign = "+" if value >= 0 else ""
    return f"{sign}{_format_number(value, decimals)}"


def _format_date(d: date) -> str:
    """
    Formatteer een datum als DD/MM/YYYY (ZORGI-standaard).

    Args:
        d: Te formatteren datum

    Returns:
        Datumstring, bv. 20/03/2026
    """
    return d.strftime("%d/%m/%Y")


def _format_period_label(period: str, months: list) -> str:
    """
    Zet een periodestring 'YYYY-MM' om naar een leesbare maand-jaar string.

    Args:
        period: Periodestring, bv. '2026-03'
        months: Lijst van 12 maandnamen (index 0 = eerste maand)

    Returns:
        Leesbare string, bv. 'maart 2026' (NL) of 'mars 2026' (FR)

    Raises:
        ValueError: Als de periodestring niet het verwachte formaat heeft
    """
    parts = period.split("-")
    if len(parts) < 2:
        raise ValueError(f"Ongeldige periodestring: '{period}' — verwacht 'YYYY-MM'")
    year, month = parts[0], int(parts[1])
    return f"{months[month - 1]} {year}"


# ---------------------------------------------------------------------------
# ReportExporter
# ---------------------------------------------------------------------------


class ReportExporter:
    """
    Genereert CSAT-maandrapportages in Nederlandstalige of Franstalige markdown.

    Laadt Jinja2-templates uit docs/templates/ en i18n-vertalingen uit
    src/csat/i18n/, en schrijft de output naar output/rapport-YYYY-MM-{lang}.md.

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
            autoescape=select_autoescape([]),  # Markdown — geen HTML-escaping
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._env.filters["fmt"] = _format_number
        self._env.filters["fmt_mom"] = _format_mom

    # ------------------------------------------------------------------
    # Publieke methoden
    # ------------------------------------------------------------------

    def render(self, result: KpiResult) -> str:
        """
        Render het rapport als markdown-string (zonder bestandsschrijving).

        Args:
            result: KpiResult van een pijleranalyse

        Returns:
            Volledige markdown-string van het rapport
        """
        template_name = f"rapport-{self._lang}.md.j2"
        template = self._env.get_template(template_name)
        context = self._build_context(result)
        return template.render(**context)

    def export(self, result: KpiResult) -> Path:
        """
        Render het rapport en schrijf het naar de outputmap.

        Bestandsnaamconventie: rapport-YYYY-MM-{lang}.md
        Aanmaakpad wordt aangemaakt als het nog niet bestaat.

        Args:
            result: KpiResult van een pijleranalyse

        Returns:
            Absoluut pad naar het gegenereerde bestand
        """
        content = self.render(result)
        output_file = self._output_path / f"rapport-{result.period}-{self._lang}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")
        logger.info(f"[ReportExporter:{self._lang}] Rapport geschreven → {output_file}")
        return output_file

    # ------------------------------------------------------------------
    # Interne helper — context opbouwen
    # ------------------------------------------------------------------

    def _build_context(self, result: KpiResult) -> dict:
        """
        Bouw de Jinja2-templatecontext op vanuit een KpiResult.

        Args:
            result: KpiResult na pijleranalyse

        Returns:
            Dict met alle template-variabelen
        """
        t = self._translations
        months: list = t["months"]

        period_label = _format_period_label(result.period, months)
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

        mom_score = getattr(result, "mom_score", 0.0)

        hc_ok = result.high_critical_ratio <= 15.0

        # Ziekenhuizen gesorteerd: ONBEKEND altijd onderaan
        sorted_hospitals = sorted(
            result.per_hospital.items(),
            key=lambda x: (x[0] == "ONBEKEND", x[0]),
        )
        has_unknown = "ONBEKEND" in result.per_hospital

        return {
            "t": t,
            "period": result.period,
            "period_label": period_label,
            "generated_date": generated_date,
            "pillar": result.pillar,
            "pillar_name": pillar_name,
            "total_tickets": result.total_tickets,
            "scored_tickets": result.scored_tickets,
            "avg_score": result.avg_score,
            "high_critical_ratio": result.high_critical_ratio,
            "high_critical_count": result.high_critical_count,
            "n_hospitals": len(result.hospitals),
            "mom_score": mom_score,
            "hc_ok": hc_ok,
            "per_hospital": sorted_hospitals,
            "has_unknown": has_unknown,
            "lang": self._lang,
        }
