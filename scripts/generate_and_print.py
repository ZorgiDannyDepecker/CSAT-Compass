"""
CSAT-Compass — Genereer rapport en druk rechtstreeks af.

Combineert generate_evolution.py + md_to_pdf.py in één stap:
    1. Genereert het evolutierapport (NL, met grafiek)
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

CONVERTIEMAP_IN = Path(r"C:\Users\danndepe\Documents\Convertiemap\IN")
CONVERTIEMAP_OUT = Path(r"C:\Users\danndepe\Documents\Convertiemap\OUT")
MD_TO_PDF = Path(r"C:\Users\danndepe\Documents\AI\Q&A-Lab\code\md_to_pdf.py")
OUTPUT_PATH = ROOT / "output"


def main() -> None:
    parser = argparse.ArgumentParser(description="Genereer CSAT-rapport en druk af.")
    parser.add_argument("--pillar", default="pharma", help="Pijler (standaard: pharma)")
    parser.add_argument("--lang", default="nl", choices=["nl", "fr", "both"],
                        help="Taal (standaard: nl)")
    parser.add_argument("--no-print", action="store_true",
                        help="Enkel PDF genereren, niet afdrukken")
    parser.add_argument("--no-chart", action="store_true",
                        help="Zonder grafiek (geen PNG)")
    args = parser.parse_args()

    # ── Stap 1: Rapport genereren ─────────────────────────────────────
    print("[1/3] Rapport genereren...")
    gen_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "generate_evolution.py"),
        "--pillar", args.pillar,
        "--lang", args.lang,
    ]
    if not args.no_chart:
        gen_cmd.append("--chart")

    result = subprocess.run(gen_cmd, cwd=ROOT)
    if result.returncode != 0:
        print("[FOUT] Generatie mislukt - afbreken.")
        sys.exit(1)

    # ── Stap 2: MD + PNG kopiëren naar Convertiemap\IN ───────────────
    print("[2/3] Bestanden kopieren naar Convertiemap...")
    CONVERTIEMAP_IN.mkdir(parents=True, exist_ok=True)

    langs = ["nl", "fr"] if args.lang == "both" else [args.lang]
    copied = []

    for lang in langs:
        # MD-bestand
        md_src = OUTPUT_PATH / f"evolutie-{args.pillar}-2026-{lang}.md"
        if md_src.exists():
            shutil.copy2(md_src, CONVERTIEMAP_IN / md_src.name)
            copied.append(md_src.name)
            print(f"  [OK] {md_src.name} -> Convertiemap\\IN")

        # PNG-bestand (indien gegenereerd)
        if not args.no_chart:
            png_src = OUTPUT_PATH / f"evolutie-{args.pillar}-2026-{lang}.png"
            if png_src.exists():
                shutil.copy2(png_src, CONVERTIEMAP_IN / png_src.name)
                print(f"  [OK] {png_src.name} -> Convertiemap\\IN")

    if not copied:
        print("[FOUT] Geen gegenereerde bestanden gevonden in output/")
        sys.exit(1)

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

    subprocess.run(pdf_cmd)

    print(f"\n[OK] Klaar -- {len(copied)} rapport(en) verwerkt.")
    if args.no_print:
        print(f"   PDF staat in: {CONVERTIEMAP_OUT}")
    else:
        print("   Afdrukopdracht verzonden.")


if __name__ == "__main__":
    main()

