"""
CSAT-Compass — Maandelijkse mail-distributie (Deel C, Fase 7B).

Zoekt de nieuwste gedateerde outputmap, converteert de onepager en het
tendens-rapport (Deel B, Cowork) naar PDF, en verstuurt ze automatisch via
Outlook naar de PHARMA-collega's (Tom De Laere, Thomas Wyckstandt,
Erwin Casier), met Danny in CC.

Beslissingen Danny Depecker 26/08/2026 — zie
docs/02-tactisch/fasen/fase7-maandelijkse-distributie.md §8:
- Enkel onepager + tendens als bijlage (geen data-driven PDF's).
- Enkel NL.
- Volautomatisch .Send() — geen .Display()-tussenstap.
- Danny staat in CC op elke verstuurde mail.

Bedoeld te draaien via Windows Taakplanner, ná Deel A (07:00) en Deel B
(Cowork, dag 2, 09:00) — bv. dag 2, 09:30.

Gebruik:
    python scripts/mail_maandelijks.py
    python scripts/mail_maandelijks.py --dry-run   # bouwt de mail, opent als concept, verstuurt niet
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from csat.config.settings import MAIL_CC, MAIL_SUBJECT_PREFIX, MAIL_TO, OUTPUT_PATH  # noqa: E402

MD_TO_PDF = Path(r"C:\Users\danndepe\Documents\AI\Q&A-Lab\code\md_to_pdf.py")


def nieuwste_output_map() -> Path:
    """Zoek de meest recente gedateerde map onder output\\ (formaat YYYY-MM-DD).

    Geeft altijd een absoluut pad terug, ongeacht of CSAT_OUTPUT_PATH relatief is
    en ongeacht de working directory waarin het script gestart wordt (belangrijk
    voor zowel Taakplanner-runs als de Outlook-COM-aanroep verderop, die geen
    relatieve paden aanvaardt).
    """
    output_root = OUTPUT_PATH.resolve()
    if not output_root.exists():
        raise FileNotFoundError(f"Outputmap bestaat niet: {output_root}")
    mappen = [p for p in output_root.iterdir() if p.is_dir() and len(p.name) == 10 and p.name[4] == "-"]
    if not mappen:
        raise FileNotFoundError(f"Geen gedateerde outputmappen gevonden in {output_root}")
    return max(mappen, key=lambda p: p.name)


def vind_rapport(map_: Path, prefix: str) -> Path:
    """Vind het meest recente .md-bestand dat met prefix begint (bv. 'onepager-') in map_."""
    kandidaten = sorted(map_.glob(f"{prefix}*-nl.md"))
    if not kandidaten:
        raise FileNotFoundError(
            f"Geen bestand gevonden met prefix '{prefix}' in {map_} "
            f"— is Deel B (Cowork) al gedraaid voor deze maand?"
        )
    return kandidaten[-1]


def converteer_naar_pdf(md_pad: Path) -> Path:
    """Converteer een los .md-bestand naar PDF via md_to_pdf.py, in dezelfde map.

    Geeft een absoluut pad terug (zie nieuwste_output_map voor de reden).
    """
    cmd = [sys.executable, str(MD_TO_PDF), str(md_pad)]
    result = subprocess.run(cmd, cwd=ROOT)  # noqa: S603
    if result.returncode != 0:
        raise RuntimeError(f"PDF-conversie mislukt voor {md_pad}")
    pdf_pad = md_pad.with_suffix(".pdf").resolve()
    if not pdf_pad.exists():
        raise FileNotFoundError(f"Verwachte PDF niet gevonden na conversie: {pdf_pad}")
    return pdf_pad


def verstuur_mail(onepager_pdf: Path, tendens_pdf: Path, periode: str, dry_run: bool) -> None:
    """Stel de Outlook-mail samen en verstuur ze (of open als concept bij dry-run).

    Bij dry-run gaan Aan en CC bewust enkel naar MAIL_CC (Danny) i.p.v. de echte
    ontvangers — zo kan een per ongeluk verstuurd testconcept nooit bij
    Tom, Thomas of Erwin terechtkomen.
    """
    import win32com.client  # lokaal geïmporteerd — enkel nodig op Windows

    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    if dry_run:
        mail.To = MAIL_CC
        mail.CC = ""
        mail.Subject = f"[DRY-RUN] {MAIL_SUBJECT_PREFIX} — Maandelijkse rapportage {periode}"
    else:
        mail.To = MAIL_TO
        mail.CC = MAIL_CC
        mail.Subject = f"{MAIL_SUBJECT_PREFIX} — Maandelijkse rapportage {periode}"
    mail.HTMLBody = (
        "<p>Collega's,</p>"
        f"<p>In bijlage de maandelijkse CSAT-rapportage ({periode}) zijnde "
        "de onepager en het uitgebreidere tendensrapport.</p>"
        "<p>Vriendelijke groeten,<br>"
        "Danny <em><small>(geautomatiseerde rapportage)</small></em></p>"
    )
    mail.Attachments.Add(str(onepager_pdf))
    mail.Attachments.Add(str(tendens_pdf))

    if dry_run:
        mail.Display()
        print(f"[DRY-RUN] Mail geopend als concept, enkel naar {MAIL_CC} (test-adres) — niet verstuurd.")
    else:
        mail.Send()
        print(f"[OK] Mail verstuurd naar {MAIL_TO} (CC: {MAIL_CC})")


def main() -> None:
    """Zoek de nieuwste rapporten, converteer naar PDF en verstuur de maandelijkse mail."""
    parser = argparse.ArgumentParser(description="Verstuur de maandelijkse CSAT-mail (Deel C).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Bouw de mail en open als concept in Outlook, verstuur niet",
    )
    args = parser.parse_args()

    if not MAIL_TO:
        print("[FOUT] CSAT_MAIL_TO is niet ingesteld in .env — afbreken.")
        sys.exit(1)

    print("[1/3] Nieuwste outputmap zoeken...")
    map_ = nieuwste_output_map()
    periode = map_.name
    periode_display = f"{periode[8:10]}/{periode[5:7]}/{periode[:4]}"
    print(f"  -> {map_}")

    print("[2/3] Onepager en tendens naar PDF converteren...")
    onepager_md = vind_rapport(map_, "onepager-")
    tendens_md = vind_rapport(map_, "tendens-")
    onepager_pdf = converteer_naar_pdf(onepager_md)
    tendens_pdf = converteer_naar_pdf(tendens_md)
    print(f"  -> {onepager_pdf.name}")
    print(f"  -> {tendens_pdf.name}")

    print("[3/3] Mail samenstellen en versturen...")
    verstuur_mail(onepager_pdf, tendens_pdf, periode_display, args.dry_run)


if __name__ == "__main__":
    main()
