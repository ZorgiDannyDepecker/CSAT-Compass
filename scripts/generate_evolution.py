"""
CSAT-Compass — Evolutierapport genereren.

Vergelijkt een baseline-jaar met een lopende periode en exporteert
het evolutierapport als NL en/of FR markdown. Optioneel ook een
matplotlib-visualisatie (PNG) via de --chart vlag.

Gebruik:
    python scripts/generate_evolution.py --pillar pharma
    python scripts/generate_evolution.py --pillar care --lang both
    python scripts/generate_evolution.py --pillar zorgi --baseline 2025-01 2025-12 --current 2026-01 2026-03
    python scripts/generate_evolution.py --pillar pharma --baseline-label "Volledig 2025" --current-label "jan-mrt 2026"
    python scripts/generate_evolution.py --pillar pharma --chart
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from csat.config.pillars import PILLAR_REGISTRY  # noqa: E402
from csat.config.settings import CSV_FALLBACK_PATH, DB_CONN, LOG_PATH, OUTPUT_PATH  # noqa: E402
from csat.core.analysers.evolution_analyser import EvolutionAnalyser  # noqa: E402
from csat.core.exporters.evolution_exporter import EvolutionExporter  # noqa: E402
from csat.core.exporters.evolution_visualiser import EvolutionVisualiser  # noqa: E402
from csat.core.loaders import get_loader  # noqa: E402
from csat.utils.date_utils import dated_output_dir, parse_period, previous_period, today_period  # noqa: E402
from csat.utils.logger import setup_logger  # noqa: E402

_LANG_CHOICES = ("nl", "fr", "both")


def _periods_range(from_p: str, to_p: str) -> list[str]:
    """Genereer lijst van periodes tussen from_p en to_p (inclusief)."""
    fy, fm = parse_period(from_p)
    ty, tm = parse_period(to_p)
    result = []
    y, m = fy, fm
    while (y, m) <= (ty, tm):
        result.append(f"{y}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return result


def main() -> None:  # noqa: C901
    parser = argparse.ArgumentParser(
        description="CSAT-Compass — evolutierapport genereren (NL + FR)"
    )
    parser.add_argument(
        "--pillar",
        default="pharma",
        choices=list(PILLAR_REGISTRY.keys()),
        help="Pijler (standaard: pharma)",
    )
    parser.add_argument(
        "--baseline",
        nargs=2,
        metavar=("VAN", "TOT"),
        default=None,
        help="Baseline periode: VAN TOT (bv. 2025-01 2025-12)",
    )
    parser.add_argument(
        "--current",
        nargs=2,
        metavar=("VAN", "TOT"),
        default=None,
        help="Huidige periode: VAN TOT (bv. 2026-01 2026-03). Standaard: lopend jaar t/m vorige maand.",
    )
    parser.add_argument(
        "--baseline-label",
        default=None,
        help="Aangepast label voor baseline (bv. 'Volledig 2025')",
    )
    parser.add_argument(
        "--current-label",
        default=None,
        help="Aangepast label voor huidig (bv. 'jan-mrt 2026')",
    )
    parser.add_argument(
        "--lang",
        default="both",
        choices=_LANG_CHOICES,
        help="Taal van het rapport (standaard: both)",
    )
    parser.add_argument(
        "--year",
        default=None,
        help="Jaarlabel voor bestandsnaam (standaard: afgeleid van current_label)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=f"Uitvoermap (standaard: {OUTPUT_PATH})",
    )
    parser.add_argument(
        "--chart",
        action="store_true",
        default=False,
        help="Genereer ook een 4-subplot PNG-visualisatie (evolutie-{pillar}-{jaar}.png)",
    )
    parser.add_argument(
        "--force-csv",
        action="store_true",
        default=False,
        help="Forceer CSV-loader (omzeilt SQL — voor onderhoud of reproduceerbare runs)",
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        default=False,
        help="Sla datum/tijdstempel in bestandsnaam over (standaard: timestamp AAN)",
    )

    args = parser.parse_args()

    setup_logger(LOG_PATH)

    # Data laden
    loader = get_loader(DB_CONN, CSV_FALLBACK_PATH, force_csv=args.force_csv)
    df = loader.load()

    # Periodes opbouwen
    if args.baseline:
        baseline_periods = _periods_range(args.baseline[0], args.baseline[1])
    else:
        # Standaard: volledig vorig jaar

        huidig_jaar = datetime.now().astimezone().year
        vorig_jaar = huidig_jaar - 1
        baseline_periods = _periods_range(f"{vorig_jaar}-01", f"{vorig_jaar}-12")

    if args.current:
        current_periods = _periods_range(args.current[0], args.current[1])
    else:
        # Standaard: lopend jaar t/m vorige maand
        current_end = previous_period(today_period())
        current_year = current_end[:4]
        current_periods = _periods_range(f"{current_year}-01", current_end)

    # Analyse
    analyser = EvolutionAnalyser(df, pillar_key=args.pillar)
    result = analyser.analyse(
        baseline_periods,
        current_periods,
        baseline_label=args.baseline_label,
        current_label=args.current_label,
    )

    # Uitvoermap — datumsubmap binnen OUTPUT_PATH (YYYY-MM-DD)
    base_path = Path(args.output) if args.output else OUTPUT_PATH
    output_path = dated_output_dir(base_path)

    # Tijdstempel voor bestandsnamen — standaard AAN, uit te schakelen via --no-timestamp
    ts_suffix = "" if args.no_timestamp else f"_{datetime.now().astimezone().strftime('%Y%m%d-%H%M')}"

    # Export — ts_suffix rechtstreeks meegeven, geen post-hoc rename nodig
    exported: list[Path] = []
    langs = ["nl", "fr"] if args.lang == "both" else [args.lang]

    for lang in langs:
        exporter = EvolutionExporter(
            lang=lang,
            output_path=output_path,
        )
        pad = exporter.export(result, year=args.year, ts_suffix=ts_suffix)
        exported.append(pad)
        print(f"[OK] [{lang.upper()}] {pad}")

    print(f"\n>> {len(exported)} bestand(en) gegenereerd in {exported[0].parent}")

    # Optionele visualisatie — NL en/of FR PNG afhankelijk van --lang
    if args.chart:
        vis_langs = ["nl", "fr"] if args.lang == "both" else [args.lang]
        for lang in vis_langs:
            vis = EvolutionVisualiser(result, lang=lang)
            png_pad = vis.export(output_path, year=args.year, ts_suffix=ts_suffix)
            print(f"[OK] [PNG-{lang.upper()}] {png_pad}")
        print(f">> {len(vis_langs)} visualisatie(s) gegenereerd")


if __name__ == "__main__":
    main()
