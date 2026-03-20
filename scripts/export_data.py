"""
CSAT-Compass — Data-exportscript voor V_CSAT_1.

Exporteert data vanuit V_CSAT_1 naar een CSV-bestand in de output-map.
Standaard: alle tickets van het opgegeven jaar (standaard 2025).
Gebruik --all om de volledige dataset zonder datumfilter te exporteren.

Gebruik:
    python scripts/export_data.py                # 2025-data
    python scripts/export_data.py --year 2026    # 2026-data
    python scripts/export_data.py --since 2025   # 01/01/2025 tot vandaag (2025 + 2026)
    python scripts/export_data.py --all          # volledige dataset

Manual: docs/03-operationeel/tools/export-data.md
"""

import argparse
import sys
from datetime import date
from pathlib import Path

# Zorg dat src/ vindbaar is als het script rechtstreeks wordt aangeroepen
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from csat.config.settings import CSV_FALLBACK_PATH, DB_CONN, OUTPUT_PATH  # noqa: E402
from csat.core.loaders import get_loader  # noqa: E402
from csat.utils.date_utils import filter_year  # noqa: E402
from csat.utils.logger import setup_logger  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parseer commandoregelargumenten."""
    parser = argparse.ArgumentParser(
        description="Exporteer V_CSAT_1 data naar CSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Voorbeelden:\n"
            "  python scripts/export_data.py                # 2025-data\n"
            "  python scripts/export_data.py --year 2026    # 2026-data\n"
            "  python scripts/export_data.py --since 2025   # 01/01/2025 tot vandaag\n"
            "  python scripts/export_data.py --all          # volledige dataset\n"
        ),
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        metavar="JJJJ",
        help="Exporteer tickets aangemaakt in dit jaar",
    )
    parser.add_argument(
        "--since",
        type=int,
        default=None,
        metavar="JJJJ",
        help="Exporteer tickets van 01/01/JJJJ tot vandaag (bv. --since 2025)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="export_all",
        help="Exporteer de volledige dataset zonder datumfilter",
    )
    return parser.parse_args()


def main() -> None:
    """Hoofdfunctie: laad data, filter op gewenste periode en exporteer naar CSV."""
    args = parse_args()

    # Logger initialiseren
    setup_logger(ROOT / "logs", log_level="INFO")

    print("\n[*] Data laden vanuit V_CSAT_1 ...")
    loader = get_loader(DB_CONN, CSV_FALLBACK_PATH)
    df: pd.DataFrame = loader.load()
    print(f"    {len(df):,} tickets geladen")

    vandaag = date.today()

    if args.export_all:
        # Geen filter — volledige dataset
        bestandsnaam = "v_csat_1_volledig.csv"
        label = "volledige dataset"
    elif args.since:
        # Van 01/01/since-jaar tot vandaag — dekt meerdere jaren
        startdatum = pd.Timestamp(f"{args.since}-01-01")
        einddatum = pd.Timestamp(vandaag)
        df = df[pd.to_datetime(df["created"]).between(startdatum, einddatum)].copy()
        bestandsnaam = f"v_csat_1_{args.since}-heden.csv"
        label = f"01/01/{args.since} → {vandaag.strftime('%d/%m/%Y')}"
    else:
        # Enkel het opgegeven jaar (standaard: 2025)
        jaar = args.year if args.year else 2025
        df = filter_year(df, jaar)
        bestandsnaam = f"v_csat_1_{jaar}.csv"
        label = f"jaar {jaar}"

    print(f"    {len(df):,} tickets na filter ({label})")

    # Output-map aanmaken als die nog niet bestaat
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    csv_pad = OUTPUT_PATH / bestandsnaam

    # Exporteren met puntkomma als scheidingsteken (Excel-compatibel)
    df.to_csv(csv_pad, index=False, sep=";", encoding="utf-8-sig")

    print(f"\n[OK] Geëxporteerd naar: {csv_pad}")
    print(f"     Open in Excel via Gegevens → Uit tekst/CSV (scheidingsteken: puntkomma)\n")


if __name__ == "__main__":
    main()

