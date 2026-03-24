"""
CSAT-Compass — Evolutierapporten genereren voor ALLE pijlers.

Genereert in één run NL + FR evolutierapporten voor alle 5 ZORGI-pijlers.

Gebruik:
    python scripts/generate_all_evolutions.py
    python scripts/generate_all_evolutions.py --baseline 2025-01 2025-12 --current 2026-01 2026-03
    python scripts/generate_all_evolutions.py --pillar pharma care
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from csat.config.pillars import PILLAR_REGISTRY  # noqa: E402
from csat.config.settings import CSV_FALLBACK_PATH, DB_CONN, LOG_PATH  # noqa: E402
from csat.core.analysers.evolution_analyser import EvolutionAnalyser  # noqa: E402
from csat.core.exporters.evolution_exporter import EvolutionExporter  # noqa: E402
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
    args = parser.parse_args()

    setup_logger(LOG_PATH)

    # Periodes
    if args.baseline:
        baseline_periods = _periods_range(args.baseline[0], args.baseline[1])
    else:
        from datetime import UTC, datetime  # noqa: PLC0415
        vorig_jaar = datetime.now(tz=UTC).year - 1
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
    loader = get_loader(DB_CONN, CSV_FALLBACK_PATH)
    df = loader.load()

    # Loop over pijlers
    totaal = 0
    fouten: list[str] = []

    for pillar in args.pillar:
        try:
            analyser = EvolutionAnalyser(df, pillar_key=pillar)
            result = analyser.analyse(baseline_periods, current_periods)

            for lang in ["nl", "fr"]:
                exporter = EvolutionExporter(lang=lang)
                pad = exporter.export(result, year=args.year)
                totaal += 1
                print(f"  [OK] [{lang.upper()}] {pillar:<12} -> {pad.name}")

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

