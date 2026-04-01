"""
CSAT-Compass — Genereer rapport en druk rechtstreeks af.

Combineert generate_evolution.py + md_to_pdf.py in één stap:
    1. Genereert het evolutierapport (NL, met grafiek) in een timestamped submap
    2. Kopieert MD + PNG naar Convertiemap\\IN
    3. Converteert naar PDF en stuurt naar printer

Gebruik:
    python scripts/generate_and_print.py
    python scripts/generate_and_print.py --pillar pharma --lang nl
    python scripts/generate_and_print.py --pillar pharma --lang both
    python scripts/generate_and_print.py --no-print   # enkel PDF, niet afdrukken
    python scripts/generate_and_print.py --no-chart   # zonder grafiek
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from csat.config.settings import OUTPUT_PATH  # noqa: E402
from csat.utils.date_utils import timestamped_output_dir  # noqa: E402

CONVERTIEMAP_IN = Path(r"C:\Users\danndepe\Documents\Convertiemap\IN")
CONVERTIEMAP_OUT = Path(r"C:\Users\danndepe\Documents\Convertiemap\OUT")
MD_TO_PDF = Path(r"C:\Users\danndepe\Documents\AI\Q&A-Lab\code\md_to_pdf.py")


def main() -> None:
    """Genereer CSAT-rapport en stuur naar printer."""
    parser = argparse.ArgumentParser(description="Genereer CSAT-rapport en druk af.")
    parser.add_argument("--pillar", default="pharma", help="Pijler (standaard: pharma)")
    parser.add_argument("--lang", default="nl", choices=["nl", "fr", "both"],
                        help="Taal (standaard: nl)")
    parser.add_argument("--no-print", action="store_true",
                        help="Enkel PDF genereren, niet afdrukken")
    parser.add_argument("--no-chart", action="store_true",
                        help="Zonder grafiek (geen PNG)")
    args = parser.parse_args()

    # Timestamped outputmap aanmaken — alle bestanden van deze run komen hier
    run_output = timestamped_output_dir(OUTPUT_PATH)

    # ── Stap 1: Rapport genereren ─────────────────────────────────────
    print("[1/3] Rapport genereren...")
    gen_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "generate_evolution.py"),
        "--pillar", args.pillar,
        "--lang", args.lang,
        "--output", str(run_output),
    ]
    if not args.no_chart:
        gen_cmd.append("--chart")

    result = subprocess.run(gen_cmd, cwd=ROOT)  # noqa: S603
    if result.returncode != 0:
        print("[FOUT] Generatie mislukt - afbreken.")
        sys.exit(1)

    # ── Stap 2: MD + PNG kopiëren naar Convertiemap\IN ───────────────
    print("[2/3] Bestanden kopieren naar Convertiemap...")
    CONVERTIEMAP_IN.mkdir(parents=True, exist_ok=True)

    # Bestanden ophalen via glob — geen hardcoded namen nodig
    md_bestanden = list(run_output.glob("evolutie-*.md"))
    png_bestanden = list(run_output.glob("evolutie-*.png")) if not args.no_chart else []
    te_kopieren = md_bestanden + png_bestanden

    if not te_kopieren:
        print(f"[FOUT] Geen gegenereerde bestanden gevonden in {run_output}")
        sys.exit(1)

    for src in te_kopieren:
        shutil.copy2(src, CONVERTIEMAP_IN / src.name)
        print(f"  [OK] {src.name} -> Convertiemap\\IN")

    # ── Stap 3: PDF conversie (+ afdrukken) ──────────────────────────
    print("[3/3] PDF conversie en afdrukken...")
    pdf_cmd = [
        sys.executable,
        str(MD_TO_PDF),
        "--batch",
        str(CONVERTIEMAP_IN),
        str(CONVERTIEMAP_OUT),
        "-d",  # bronbestand verwijderen na conversie
    ]
    if not args.no_print:
        pdf_cmd.append("-p")  # afdrukken

    subprocess.run(pdf_cmd)  # noqa: S603

    print(f"\n[OK] Klaar -- {len(md_bestanden)} rapport(en) verwerkt.")
    print(f"   Output: {run_output}")
    if args.no_print:
        print(f"   PDF staat in: {CONVERTIEMAP_OUT}")
    else:
        print("   Afdrukopdracht verzonden.")


if __name__ == "__main__":
    main()

