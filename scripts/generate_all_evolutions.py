"""
CSAT-Compass — Evolutierapporten genereren voor ALLE pijlers.

Genereert in één run NL + FR evolutierapporten voor alle 5 ZORGI-pijlers.
Optioneel ook een matplotlib-visualisatie per pijler via --chart.

Gebruik:
    python scripts/generate_all_evolutions.py
    python scripts/generate_all_evolutions.py --baseline 2025-01 2025-12 --current 2026-01 2026-03
    python scripts/generate_all_evolutions.py --pillar pharma care
    python scripts/generate_all_evolutions.py --chart
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from csat.config.pillars import PILLAR_REGISTRY  # noqa: E402
from csat.config.settings import CSV_FALLBACK_PATH, DB_CONN, LOG_PATH, OUTPUT_PATH  # noqa: E402
from csat.core.analysers.evolution_analyser import EvolutionAnalyser  # noqa: E402
from csat.core.exporters.evolution_exporter import EvolutionExporter  # noqa: E402
from csat.core.exporters.evolution_visualiser import EvolutionVisualiser  # noqa: E402, F401
from csat.core.loaders import get_loader  # noqa: E402
from csat.utils.date_utils import parse_period, previous_period, today_period  # noqa: E402
from csat.utils.logger import setup_logger  # noqa: E402

# Volgorde: ZORGI totaal eerst, daarna pijlers alfabetisch
_DEFAULT_PILLARS = ["zorgi", "pharma", "care", "care_admin", "erp4hc"]


def _periods_range(from_p: str, to_p: str) -> list[str]:
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CSAT-Compass — evolutierapporten voor alle pijlers"
    )
    parser.add_argument(
        "--pillar",
        nargs="+",
        default=_DEFAULT_PILLARS,
        choices=list(PILLAR_REGISTRY.keys()),
        help=f"Pijler(s) — standaard alle: {_DEFAULT_PILLARS}",
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
        help="Huidige periode: VAN TOT (bv. 2026-01 2026-03)",
    )
    parser.add_argument(
        "--year",
        default=None,
        help="Jaarlabel voor bestandsnaam (standaard: afgeleid van current_label)",
    )
    parser.add_argument(
        "--chart",
        action="store_true",
        default=False,
        help="Genereer ook een 4-subplot PNG per pijler (evolutie-{pillar}-{jaar}.png)",
    )
    parser.add_argument(
        "--force-csv",
        action="store_true",
        default=False,
        help="Forceer CSV-loader (omzeilt SQL — voor onderhoud of reproduceerbare runs)",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="MAP",
        help=f"Uitvoermap (standaard: {OUTPUT_PATH})",
    )
    args = parser.parse_args()

    setup_logger(LOG_PATH)

    # Periodes
    if args.baseline:
        baseline_periods = _periods_range(args.baseline[0], args.baseline[1])
    else:
        from datetime import datetime  # noqa: PLC0415
        vorig_jaar = datetime.now().astimezone().year - 1
        baseline_periods = _periods_range(f"{vorig_jaar}-01", f"{vorig_jaar}-12")

    if args.current:
        current_periods = _periods_range(args.current[0], args.current[1])
    else:
        current_end = previous_period(today_period())
        current_year = current_end[:4]
        current_periods = _periods_range(f"{current_year}-01", current_end)

    print(f"\nBaseline : {baseline_periods[0]} - {baseline_periods[-1]} ({len(baseline_periods)} maanden)")
    print(f"Huidig   : {current_periods[0]} - {current_periods[-1]} ({len(current_periods)} maanden)")
    print(f"Pijlers  : {', '.join(args.pillar)}\n")

    # Data eenmalig laden
    loader = get_loader(DB_CONN, CSV_FALLBACK_PATH, force_csv=args.force_csv)
    df = loader.load()

    # Uitvoermap bepalen
    output_dir = Path(args.output) if args.output else OUTPUT_PATH

    # Loop over pijlers
    totaal = 0
    fouten: list[str] = []

    for pillar in args.pillar:
        try:
            analyser = EvolutionAnalyser(df, pillar_key=pillar)
            result = analyser.analyse(baseline_periods, current_periods)

            for lang in ["nl", "fr"]:
                exporter = EvolutionExporter(lang=lang, output_path=output_dir)
                pad = exporter.export(result, year=args.year)
                totaal += 1
                print(f"  [OK] [{lang.upper()}] {pillar:<12} -> {pad.name}")

            # Optionele visualisatie per pijler — NL én FR PNG
            if args.chart:
                for lang in ["nl", "fr"]:
                    vis = EvolutionVisualiser(result, lang=lang)
                    png_pad = vis.export(output_dir, year=args.year, timestamp=False)
                    totaal += 1
                    print(f"  [OK] [PNG-{lang.upper()}] {pillar:<12} -> {png_pad.name}")

        except Exception as exc:  # noqa: BLE001
            fouten.append(f"{pillar}: {exc}")
            print(f"  [FOUT] {pillar}: {exc}")

    print(f"\n>> {totaal} bestand(en) gegenereerd")
    if fouten:
        print(f">> {len(fouten)} fout(en): {fouten}")
    else:
        print(">> Alle pijlers succesvol verwerkt")


if __name__ == "__main__":
    main()

