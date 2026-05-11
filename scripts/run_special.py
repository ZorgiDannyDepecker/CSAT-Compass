"""
CSAT-Compass — Special runner (instelbare begindatum, alle pijlers).

Genereert evolutierapporten waarbij de analyse start vanaf een instelbare
begindatum (standaard: juli 2025) t/m de volledige afgelopen maand.

De begindatum bepaalt de splitsing:
  Baseline : --start t/m einde van dat jaar        (bv. 2025-07 -> 2025-12)
  Current  : 1 januari volgend jaar t/m --month    (bv. 2026-01 -> 2026-04)

De begindatum wordt ALTIJD opgenomen in de outputbestandsnamen, bv.:
  evolutie-pharma-2026_vanaf-2025-07-nl_20260511-1552.md

Gebruik:
    python scripts/run_special.py
    python scripts/run_special.py --start 2025-07
    python scripts/run_special.py --start 2025-07 --month 2026-04
    python scripts/run_special.py --start 2025-07 --pillar pharma care
    python scripts/run_special.py --start 2025-07 --chart
    python scripts/run_special.py --start 2025-10 --force-csv

Manual: docs/03-operationeel/tools/run-special.md
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from csat.config.pillars import PILLAR_REGISTRY  # noqa: E402
from csat.config.settings import CSV_FALLBACK_PATH, DB_CONN, LOG_PATH, OUTPUT_PATH  # noqa: E402
from csat.core.analysers.evolution_analyser import EvolutionAnalyser  # noqa: E402
from csat.core.analysers.pillar_analyser import PillarAnalyser  # noqa: E402
from csat.core.exporters.evolution_exporter import EvolutionExporter  # noqa: E402
from csat.core.exporters.evolution_visualiser import EvolutionVisualiser  # noqa: E402
from csat.core.exporters.matrix_exporter import MatrixExporter  # noqa: E402
from csat.core.loaders import get_loader  # noqa: E402
from csat.utils.date_utils import dated_output_dir, parse_period, previous_period, today_period  # noqa: E402
from csat.utils.logger import setup_logger  # noqa: E402

_DEFAULT_PILLARS = ["zorgi", "pharma", "care", "care_admin", "erp4hc"]
_DEFAULT_START   = "2025-07"

_MAANDEN_NL = [
    "jan", "feb", "mrt", "apr", "mei", "jun",
    "jul", "aug", "sep", "okt", "nov", "dec",
]


def _periods_range(from_p: str, to_p: str) -> list[str]:
    """Genereer lijst van periodestrings tussen from_p en to_p (inclusief)."""
    fy, fm = parse_period(from_p)
    ty, tm = parse_period(to_p)
    periods: list[str] = []
    y, m = fy, fm
    while (y, m) <= (ty, tm):
        periods.append(f"{y}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return periods


def _derive_periods(start: str, target_month: str) -> tuple[list[str], list[str]]:
    """
    Leid baseline- en current-periodes af uit de begindatum en doelmaand.

    Args:
        start:        Begindatum analyse, formaat 'YYYY-MM' (bv. '2025-07')
        target_month: Einddatum huidige periode, formaat 'YYYY-MM' (bv. '2026-04')

    Returns:
        Tuple (baseline_periods, current_periods)

    Raises:
        ValueError: Als start en target_month in hetzelfde jaar vallen.
    """
    s_year, _ = parse_period(start)
    t_year, _ = parse_period(target_month)

    if s_year >= t_year:
        raise ValueError(
            f"--start ({start}) moet in een eerder jaar liggen dan --month ({target_month}). "
            f"Baseline en current moeten in verschillende jaren vallen."
        )

    baseline_periods = _periods_range(start, f"{s_year}-12")
    current_periods  = _periods_range(f"{t_year}-01", target_month)

    return baseline_periods, current_periods


def parse_args() -> argparse.Namespace:
    """Parseer commandoregelargumenten."""
    beschikbare_pijlers = sorted(PILLAR_REGISTRY.keys())

    parser = argparse.ArgumentParser(
        description="CSAT-Compass — Special runner met instelbare begindatum (alle pijlers)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Voorbeelden:\n"
            "  python scripts/run_special.py\n"
            "  python scripts/run_special.py --start 2025-07\n"
            "  python scripts/run_special.py --start 2025-07 --month 2026-04\n"
            "  python scripts/run_special.py --start 2025-07 --pillar pharma care\n"
            "  python scripts/run_special.py --start 2025-07 --chart\n"
            "  python scripts/run_special.py --start 2025-10 --force-csv\n"
        ),
    )
    parser.add_argument(
        "--start",
        default=_DEFAULT_START,
        metavar="YYYY-MM",
        help=f"Begindatum van de analyse — baseline start hier (standaard: {_DEFAULT_START})",
    )
    parser.add_argument(
        "--month",
        default=None,
        metavar="YYYY-MM",
        help="Doelmaand / einddatum huidige periode (standaard: vorige maand)",
    )
    parser.add_argument(
        "--pillar",
        nargs="+",
        default=_DEFAULT_PILLARS,
        choices=beschikbare_pijlers,
        help=f"Pijler(s) — standaard alle: {_DEFAULT_PILLARS}",
    )
    parser.add_argument(
        "--chart",
        action="store_true",
        default=False,
        help="Genereer ook een 4-subplot PNG per pijler per taal (NL + FR)",
    )
    parser.add_argument(
        "--no-matrix",
        action="store_true",
        default=False,
        help="Sla de vergelijkingsmatrix over (standaard: matrix AAN)",
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
        help=f"Basisuitvoermap (standaard: {OUTPUT_PATH})",
    )
    return parser.parse_args()


def main() -> None:  # noqa: C901
    """Hoofdfunctie: genereer special evolutierapporten voor alle opgegeven pijlers."""
    args = parse_args()

    setup_logger(LOG_PATH)

    target_month: str = args.month or previous_period(today_period())

    try:
        baseline_periods, current_periods = _derive_periods(args.start, target_month)
    except ValueError as exc:
        print(f"\n[FOUT] {exc}")
        sys.exit(1)

    # Begindatum als jaarlabel → zit direct in de bestandsnaam
    # Voorbeeld: --start 2025-07 → evolutie-care-2025-07-nl_20260511-1648.md
    year_label = args.start   # bv. "2025-07"

    # Alle periodes samen (matrix overspant het volledige bereik: start t/m target)
    all_periods = _periods_range(args.start, target_month)

    # Basisuitvoermap (datumsubmap, pijlermap wordt per pijler aangemaakt)
    base_path = Path(args.output) if args.output else OUTPUT_PATH
    dated_dir = dated_output_dir(base_path)

    # Leesbare labels voor in het rapport
    s_year, s_month = parse_period(args.start)
    _, cur_end_m    = parse_period(target_month)
    current_year    = target_month[:4]
    baseline_label  = f"{_MAANDEN_NL[s_month - 1]}-dec {s_year}"
    current_label   = f"jan-{_MAANDEN_NL[cur_end_m - 1]} {current_year}"

    n_pijlers = len(args.pillar)
    n_matrix  = n_pijlers * 2 if not args.no_matrix else 0
    n_md      = n_pijlers * 2
    n_png     = n_pijlers * 2 if args.chart else 0

    print(f"\n[CSAT-Compass] Special run — begindatum: {args.start}")
    print("=" * 54)
    print(f"Begindatum : {args.start}  (zichtbaar als jaarlabel in bestandsnamen)")
    print(f"Baseline   : {baseline_periods[0]} -> {baseline_periods[-1]}  ({len(baseline_periods)} maanden)")
    print(f"Huidig     : {current_periods[0]} -> {current_periods[-1]}  ({len(current_periods)} maanden)")
    print(f"Matrix     : {all_periods[0]} -> {all_periods[-1]}  ({len(all_periods)} maanden — {'aan' if not args.no_matrix else 'uit'})")
    print(f"Pijlers    : {', '.join(args.pillar)}")
    print(f"Charts     : {'aan (NL + FR)' if args.chart else 'uit'}")
    print(f"Output     : output\\{dated_dir.name}\\{{pijler}}\\  (gewone mappenstructuur)")
    print(f"Verwacht   : {n_matrix + n_md + n_png} bestand(en)")
    print()

    start_time = time.monotonic()

    loader = get_loader(DB_CONN, CSV_FALLBACK_PATH, force_csv=args.force_csv)
    df = loader.load()

    ts_suffix = f"_{datetime.now().astimezone().strftime('%Y%m%d-%H%M')}"

    totaal = 0
    fouten: list[str] = []

    for pillar in args.pillar:
        # Normale pijlermap: output/YYYY-MM-DD/{pillar}/
        output_dir = dated_dir / pillar
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # --- Matrix (alle periodes samen: start t/m target) ---
            if not args.no_matrix:
                pillar_analyser = PillarAnalyser(df, pillar_key=pillar)
                matrix_results = [pillar_analyser.analyse(p) for p in all_periods]
                for lang in ["nl", "fr"]:
                    mx = MatrixExporter(lang=lang, output_path=output_dir)
                    pad = mx.export(matrix_results, pillar_key=pillar)
                    # Hernoem: vervang automatisch jaarlabel door begindatum + timestamp
                    # matrix-{pillar}-2025-nl.md → matrix-{pillar}-2025-07-nl_...md
                    nieuw_pad = output_dir / f"matrix-{pillar}-{args.start}-{lang}{ts_suffix}.md"
                    pad.rename(nieuw_pad)
                    totaal += 1
                    print(f"  [OK] [MTX-{lang.upper()}] {pillar:<10} -> {nieuw_pad.name}")

            # --- Evolutierapport ---
            analyser = EvolutionAnalyser(df, pillar_key=pillar)
            result   = analyser.analyse(
                baseline_periods,
                current_periods,
                baseline_label=baseline_label,
                current_label=current_label,
            )

            for lang in ["nl", "fr"]:
                exporter = EvolutionExporter(lang=lang, output_path=output_dir)
                pad = exporter.export(result, year=year_label, ts_suffix=ts_suffix)
                totaal += 1
                print(f"  [OK] [{lang.upper()}] {pillar:<12} -> {pad.name}")

            if args.chart:
                for lang in ["nl", "fr"]:
                    vis = EvolutionVisualiser(result, lang=lang)
                    png_pad = vis.export(output_dir, year=year_label, ts_suffix=ts_suffix)
                    totaal += 1
                    print(f"  [OK] [PNG-{lang.upper()}] {pillar:<10} -> {png_pad.name}")

        except Exception as exc:  # noqa: BLE001
            fouten.append(f"{pillar}: {exc}")
            print(f"  [FOUT] {pillar}: {exc}")

    duur = time.monotonic() - start_time
    print()
    print("=" * 54)
    print(f"Totaal : {totaal} bestand(en) in output\\{dated_dir.name}\\{{pijler}}\\")
    print(f"Duur   : {duur:.1f} s")
    if fouten:
        print(f"Fouten : {len(fouten)} -- {fouten}")
    else:
        print("Status : alle pijlers succesvol verwerkt")
    print()


if __name__ == "__main__":
    main()

