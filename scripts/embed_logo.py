"""
embed_logo.py — ZORGI HTML-rapport logo embedder

Embedt Zorgi_wit.png als base64 in een HTML-rapport zodat het logo zichtbaar
blijft bij een offline weergave (zonder externe bestandsreferentie).

Gebruik:
    python scripts/embed_logo.py                          # standaard bestand
    python scripts/embed_logo.py mijn_rapport.html        # specifiek bestand in Downloads
    python scripts/embed_logo.py --help

Werkwijze:
    1. Zoekt het HTML-bestand in Downloads (of via argument)
    2. Vervangt het SVG-logo-blok (<!-- ZORGI logo ... </svg>) door een <img>-tag
    3. Valt terug op src="Zorgi_wit.png" vervangen als er geen SVG-blok is
    4. Schrijft het resultaat als <origineel_naam>_embedded.html

Vereiste: assets/img/Zorgi_wit.png aanwezig in de CSAT-Compass-root.
"""

import argparse
import base64
import re
import sys
from pathlib import Path

# ── Paden ────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets" / "img" / "Zorgi_wit.png"
DOWNLOADS = Path.home() / "Downloads"

# Standaard kandidaten (in volgorde van voorkeur)
DEFAULT_CANDIDATES = [
    "zorgi_analytics_q1_2026.html",
    "zorgi_wvi_q1_2026.html",
    "zorgi_wvi_q1_2026_FINAL.html",
]


def _find_html(filename: str | None) -> Path:
    """Zoek het HTML-bestand op basis van opgegeven naam of standaardkandidaten."""
    if filename:
        candidates = [DOWNLOADS / filename, Path(filename)]
    else:
        candidates = [DOWNLOADS / naam for naam in DEFAULT_CANDIDATES]

    for p in candidates:
        if p.exists():
            return p

    if filename:
        print(f"FOUT: '{filename}' niet gevonden (ook niet als absoluut pad).")
    else:
        print("FOUT: geen standaard HTML-bestand gevonden in Downloads.")
        print("Verwacht één van:")
        for naam in DEFAULT_CANDIDATES:
            print(f"  {DOWNLOADS / naam}")
        print("Of geef het bestandsnaam als argument mee.")
    sys.exit(1)


def embed(html_path: Path) -> Path:
    """Embedt het logo en schrijft het resultaat terug. Geeft het outputpad terug."""
    if not LOGO.exists():
        print(f"FOUT: logo niet gevonden op {LOGO}")
        sys.exit(1)

    b64 = base64.b64encode(LOGO.read_bytes()).decode()
    data_uri = f"data:image/png;base64,{b64}"
    img_tag = (
        f'<img src="{data_uri}" height="40" '
        f'style="display:block;flex-shrink:0" alt="ZORGI">'
    )

    html = html_path.read_text(encoding="utf-8")

    # Stap 1: vervang SVG-logo-blok
    svg_patroon = re.compile(r"<!-- ZORGI logo.*?</svg>", re.DOTALL)
    patched, n_svg = svg_patroon.subn(img_tag, html)

    if n_svg == 0:
        # Stap 2: fallback — vervang src-placeholder
        patched = html.replace('src="Zorgi_wit.png"', f'src="{data_uri}"')
        if patched == html:
            print("WAARSCHUWING: noch SVG-blok noch src-placeholder gevonden.")
            print("Logo was mogelijk al ingebed — geen wijzigingen aangebracht.")
            return html_path

    stem = html_path.stem.removesuffix("_FINAL")
    out = html_path.parent / f"{stem}_embedded.html"
    out.write_text(patched, encoding="utf-8")
    return out


def main() -> None:
    """Verwerk CLI-argumenten en voer de embed uit."""
    parser = argparse.ArgumentParser(
        description="Embedt Zorgi_wit.png als base64 in een HTML-rapport."
    )
    parser.add_argument(
        "bestand",
        nargs="?",
        help="Bestandsnaam (in Downloads) of volledig pad naar het HTML-rapport.",
    )
    args = parser.parse_args()

    html_path = _find_html(args.bestand)
    out = embed(html_path)

    b64_len = len(base64.b64encode(LOGO.read_bytes()).decode())
    print(f"Logo ingebed ({b64_len:,} base64-tekens)")
    print(f"Opgeslagen: {out}")
    print("Open dit bestand in uw browser.")


if __name__ == "__main__":
    main()

