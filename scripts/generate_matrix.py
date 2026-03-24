"""
CSAT-Compass — Vergelijkingsmatrix genereren.

Analyseert meerdere periodes voor een opgegeven pijler en exporteert
de resultaten als vergelijkingsmatrix (NL en/of FR).

Gebruik:
    python scripts/generate_matrix.py --from 2026-01
    python scripts/generate_matrix.py --from 2026-01 --to 2026-03
    python scripts/generate_matrix.py --from 2026-01 --pillar pharma --lang nl
    python scripts/generate_matrix.py --from 2025-06 --to 2025-12 --pillar pharma --lang both

Manual: docs/03-operationeel/tools/generate-matrix.md
"""

import argparse
import sys
from pathlib import Path

# Zorg dat src/ vindbaar is als het script rechtstreeks wordt aangeroepen
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from csat.config.pillars import PILLAR_REGISTRY  # noqa: E402
from csat.config.settings import CSV_FALLBACK_PATH, DB_CONN, OUTPUT_PATH  # noqa: E402
from csat.core.analysers.base_analyser import KpiResult  # noqa: E402
from csat.core.analysers.pillar_analyser import PillarAnalyser  # noqa: E402
from csat.core.exporters.matrix_exporter import MatrixExporter  # noqa: E402
from csat.core.loaders import get_loader  # noqa: E402
from csat.utils.date_utils import parse_period, today_period  # noqa: E402
from csat.utils.logger import setup_logger  # noqa: E402

# Beschikbare taalopties
_LANG_CHOICES = ("nl", "fr", "both")


def _periods_range(from_period: str, to_period: str) -> list[str]:
    """
    Genereer een gesorteerde lijst van maandperiodes tussen from_period en to_period (inclusief).

    Args:
        from_period: Startperiode 'YYYY-MM'
        to_period:   Eindperiode 'YYYY-MM'

    Returns:
        Lijst van periodestrings, bv. ['2026-01', '2026-02', '2026-03']

    Raises:
        ValueError: Als to_period voor from_period valt
    """
    from_jaar, from_maand = parse_period(from_period)
    to_jaar, to_maand = parse_period(to_period)

    if (to_jaar, to_maand) < (from_jaar, from_maand):
        raise ValueError(
            f"--to '{to_period}' valt vóór --from '{from_period}'"
        )

    periodes = []
    jaar, maand = from_jaar, from_maand
    while (jaar, maand) <= (to_jaar, to_maand):
        periodes.append(f"{jaar}-{maand:02d}")
        maand += 1
        if maand > 12:
            maand = 1
            jaar += 1
    return periodes


def parse_args() -> argparse.Namespace:
    """Parseer commandoregelargumenten."""
    beschikbare_pijlers = sorted(PILLAR_REGISTRY.keys())

    parser = argparse.ArgumentParser(
        description="Genereer een CSAT-vergelijkingsmatrix voor een pijler over meerdere periodes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Voorbeelden:\n"
            "  python scripts/generate_matrix.py --from 2026-01\n"
            "  python scripts/generate_matrix.py --from 2026-01 --to 2026-03\n"
            "  python scripts/generate_matrix.py --from 2026-01 --pillar pharma --lang nl\n"
            "  python scripts/generate_matrix.py --from 2025-06 --to 2025-12 --lang both\n"
        ),
    )
    parser.add_argument(
        "--from",
        dest="from_period",
        required=True,
        metavar="YYYY-MM",
        help="Startperiode van de matrix (verplicht)",
    )
    parser.add_argument(
        "--to",
        dest="to_period",
        default=None,
        metavar="YYYY-MM",
        help="Eindperiode van de matrix (standaard: huidige maand)",
    )
    parser.add_argument(
        "--pillar",
        default="pharma",
        choices=beschikbare_pijlers,
        metavar="PIJLER",
        help=f"Pijlersleutel — kies uit: {', '.join(beschikbare_pijlers)} (standaard: pharma)",
    )
    parser.add_argument(
        "--lang",
        default="both",
        choices=_LANG_CHOICES,
        help="Taal van de output: nl, fr of both (standaard: both)",
    )
    return parser.parse_args()


def main() -> None:
    """Hoofdfunctie: laad data, analyseer per periode en exporteer de matrix."""
    args = parse_args()

    # Logger initialiseren
    setup_logger(ROOT / "logs", log_level="INFO")

    # Eindperiode standaard = huidige maand
    to_period = args.to_period or today_period()

    # Periodelijst opbouwen
    try:
        periodes = _periods_range(args.from_period, to_period)
    except ValueError as exc:
        print(f"\n[FOUT] {exc}\n")
        sys.exit(1)

    pillar = args.pillar
    pillar_naam = PILLAR_REGISTRY[pillar].get("report_name", pillar.upper())

    print(f"\n[*] CSAT-Compass — Vergelijkingsmatrix")
    print(f"    Pijler  : {pillar_naam}")
    print(f"    Periode : {args.from_period} -> {to_period} ({len(periodes)} maand(en))")
    print(f"    Taal    : {args.lang}")
    print()

    # Data laden
    print("[*] Data laden vanuit V_CSAT_1 ...")
    loader = get_loader(DB_CONN, CSV_FALLBACK_PATH)
    df = loader.load()
    print(f"    {len(df):,} tickets geladen")

    # Analyser initialiseren
    analyser = PillarAnalyser(df, pillar_key=pillar)

    # KPI's berekenen per periode
    print(f"\n[*] KPI's berekenen voor {len(periodes)} periode(s) ...")
    resultaten: list[KpiResult] = []
    for periode in periodes:
        result = analyser.analyse(periode)
        resultaten.append(result)
        print(f"    {periode}  —  {result.total_tickets:>4} tickets | "
              f"gem. score {result.avg_score:.2f} | H/C {result.high_critical_ratio:.1f}%")

    # Matrix exporteren
    print()
    talen = ["nl", "fr"] if args.lang == "both" else [args.lang]
    gegenereerde_bestanden: list[Path] = []

    for taal in talen:
        exporter = MatrixExporter(lang=taal, output_path=OUTPUT_PATH)
        pad = exporter.export(resultaten)
        gegenereerde_bestanden.append(pad)

    # Samenvatting
    print("[OK] Matrix gegenereerd:")
    for pad in gegenereerde_bestanden:
        print(f"     {pad}")
    print()


if __name__ == "__main__":
    main()

