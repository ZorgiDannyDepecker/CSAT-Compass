"""
CSAT-Compass — Maandelijkse batch-runner.

Voert in één commando alle maandelijkse output uit:
  1. Vergelijkingsmatrix (NL + FR) via generate_matrix.py
  2. Evolutierapporten + optionele PNG-visualisaties voor alle pijlers
     (NL + FR) via generate_all_evolutions.py

Gebruik:
    python scripts/run_monthly.py
    python scripts/run_monthly.py --month 2026-03
    python scripts/run_monthly.py --month 2026-03 --pillar pharma care
    python scripts/run_monthly.py --month 2026-03 --no-charts
    python scripts/run_monthly.py --month 2026-03 --force-csv

Manual: docs/03-operationeel/tools/run-monthly.md
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Zorg dat src/ vindbaar is als het script rechtstreeks wordt aangeroepen
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from csat.config.pillars import PILLAR_REGISTRY  # noqa: E402
from csat.config.settings import LOG_PATH, OUTPUT_PATH  # noqa: E402
from csat.utils.date_utils import parse_period, previous_period, today_period  # noqa: E402
from csat.utils.logger import setup_logger  # noqa: E402

# Volgorde: ZORGI totaal eerst, daarna pijlers conform PILLAR_REGISTRY
_DEFAULT_PILLARS = ["zorgi", "pharma", "care", "care_admin", "erp4hc"]

_MAANDEN_NL = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]


def _derive_periods(target_month: str) -> dict[str, str]:
    """
    Leid alle periodestrings af uit de doelmaand.

    Args:
        target_month: Doelmaand in formaat 'YYYY-MM'

    Returns:
        Dict met sleutels: huidig_jaar, vorig_jaar,
        matrix_from, matrix_to,
        baseline_from, baseline_to,
        current_from, current_to
    """
    huidig_jaar = target_month[:4]
    vorig_jaar = str(int(huidig_jaar) - 1)
    return {
        "huidig_jaar": huidig_jaar,
        "vorig_jaar": vorig_jaar,
        "matrix_from": f"{huidig_jaar}-01",
        "matrix_to": target_month,
        "baseline_from": f"{vorig_jaar}-01",
        "baseline_to": f"{vorig_jaar}-12",
        "current_from": f"{huidig_jaar}-01",
        "current_to": target_month,
    }


def _month_label_nl(period: str) -> str:
    """
    Geeft een leesbaar maandlabel in het Nederlands.

    Args:
        period: Periodestring 'YYYY-MM'

    Returns:
        Leesbaar label, bv. 'maart 2026'
    """
    jaar, maand = parse_period(period)
    return f"{_MAANDEN_NL[maand - 1]} {jaar}"


def parse_args() -> argparse.Namespace:
    """Parseer commandoregelargumenten."""
    beschikbare_pijlers = sorted(PILLAR_REGISTRY.keys())

    parser = argparse.ArgumentParser(
        description="CSAT-Compass — maandelijkse batch-runner (matrix + evolutie + charts)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Voorbeelden:\n"
            "  python scripts/run_monthly.py\n"
            "  python scripts/run_monthly.py --month 2026-03\n"
            "  python scripts/run_monthly.py --month 2026-03 --pillar pharma care\n"
            "  python scripts/run_monthly.py --month 2026-03 --no-charts\n"
            "  python scripts/run_monthly.py --month 2026-03 --force-csv\n"
        ),
    )
    parser.add_argument(
        "--month",
        default=None,
        metavar="YYYY-MM",
        help="Doelmaand voor rapportage (standaard: vorige maand)",
    )
    parser.add_argument(
        "--pillar",
        nargs="+",
        default=_DEFAULT_PILLARS,
        choices=beschikbare_pijlers,
        help=f"Pijler(s) voor evolutierapporten — standaard alle: {_DEFAULT_PILLARS}",
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        default=False,
        help="Sla PNG-visualisaties over (standaard: charts AAN)",
    )
    parser.add_argument(
        "--force-csv",
        action="store_true",
        default=False,
        help="Forceer CSV-loader (omzeilt SQL — voor onderhoud of reproduceerbare runs)",
    )
    return parser.parse_args()


def _run_script(script: Path, extra_args: list[str]) -> subprocess.CompletedProcess:
    """
    Voer een scriptbestand uit als subprocess.

    Args:
        script: Pad naar het Python-scriptbestand
        extra_args: Aanvullende commandoregelargumenten

    Returns:
        CompletedProcess met returncode
    """
    cmd = [sys.executable, str(script), *extra_args]
    return subprocess.run(cmd, cwd=str(ROOT))  # noqa: S603


def main() -> None:
    """Hoofdfunctie: genereer alle maandelijkse output in één run."""
    args = parse_args()

    setup_logger(LOG_PATH)

    # Doelmaand bepalen — standaard vorige maand
    target_month: str = args.month or previous_period(today_period())

    # Periodes afleiden
    p = _derive_periods(target_month)
    huidig_jaar   = p["huidig_jaar"]
    baseline_from = p["baseline_from"]
    baseline_to   = p["baseline_to"]
    current_from  = p["current_from"]
    current_to    = p["current_to"]

    # Geen submap — bestanden gaan rechtstreeks in OUTPUT_PATH met timestamp in naam
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Aantal pijlers en outputberekening
    n_pijlers = len(args.pillar)
    n_md      = n_pijlers * 2                           # NL + FR per pijler
    n_png     = n_pijlers * 2 if not args.no_charts else 0  # NL + FR PNG
    n_matrix  = 2                                        # NL + FR matrix
    totaal    = n_matrix + n_md + n_png

    # Header tonen
    charts_label = "aan (NL + FR)" if not args.no_charts else "uit"
    maand_nl = _month_label_nl(target_month)

    print(f"\n[CSAT-Compass] Maandelijkse run — {maand_nl}")
    print("=" * 44)
    print(f"Doelmaand  : {target_month}")
    print(f"Baseline   : {baseline_from} → {baseline_to}")
    print(f"Current    : {current_from} → {current_to}")
    print(f"Pijlers    : {', '.join(args.pillar)}")
    print(f"Charts     : {charts_label}")
    print(f"Output     : output\\")
    print()

    start = time.monotonic()

    # --- Stap 1: Matrix (pharma — altijd de primaire pijler) ---
    print("[1/2] Matrix genereren (pharma) ...")
    matrix_args = [
        "--from", p["matrix_from"],
        "--to",   p["matrix_to"],
        "--pillar", "pharma",
        "--lang", "both",
        "--output", str(OUTPUT_PATH),
    ]
    result = _run_script(ROOT / "scripts" / "generate_matrix.py", matrix_args)
    if result.returncode != 0:
        print(f"\n[FOUT] Matrix genereren mislukt (exit code {result.returncode})")
        sys.exit(result.returncode)
    print()

    # --- Stap 2: Evolutierapporten (alle opgegeven pijlers) ---
    print(f"[2/2] Evolutierapporten genereren ({n_pijlers} pijler(s)) ...")
    evo_args: list[str] = [
        "--baseline", baseline_from, baseline_to,
        "--current",  current_from,  current_to,
        "--year", huidig_jaar,
        "--pillar", *args.pillar,
        "--output", str(OUTPUT_PATH),
    ]
    if not args.no_charts:
        evo_args.append("--chart")
    if args.force_csv:
        evo_args.append("--force-csv")

    result = _run_script(ROOT / "scripts" / "generate_all_evolutions.py", evo_args)
    if result.returncode != 0:
        print(f"\n[FOUT] Evolutierapporten genereren mislukt (exit code {result.returncode})")
        sys.exit(result.returncode)

    # --- Samenvatting ---
    duur = time.monotonic() - start
    print()
    print("=" * 44)
    print(f"Totaal: {totaal} bestanden gegenereerd in output\\")
    print(f"Duur  : {duur:.1f} seconden")
    print()


if __name__ == "__main__":
    main()

