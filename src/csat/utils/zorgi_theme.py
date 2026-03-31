"""
ZORGI Design System — kleuren- en typografie-constanten.
Golden source: PHARMA-Conventions/zorgi/zorgi_design_system.md
Dit bestand is de Python-representatie van het officiële ZORGI Design System.
Regels:
- Primaire en secundaire kleuren komen rechtstreeks uit de golden source.
- .github/docs/zorgi_design_system.md is een read-only kopie — nooit aanpassen.
- Aanvullingskleuren zijn expliciet gedocumenteerd als functionele uitbreidingen
  met verwijzing naar het betreffende ADR.
Gebruik:
    from csat.utils.zorgi_theme import ZORGI_DARK_BLUE, ZORGI_BORDEAUX
    from csat.utils.zorgi_theme import ZORGI_PILLAR_COLORS, ZORGI_GRADIENT_STOPS
"""

from __future__ import annotations

# == Primaire kleuren (Design System §2 — Primary Colors) =====================
ZORGI_DARK_BLUE = "#003a70"  # Primary brand color — titels, assen, kop 1 & 4
ZORGI_RED = "#dc2b26"  # Accent — logo gradient, highlights, negatieve bars
ZORGI_PURPLE = "#7f4267"  # Logo gradient mid-tone — title bars, kop 5
# == Secundaire kleuren (Design System §2 — Secondary Colors) =================
ZORGI_GREY_BLUE = "#5f8495"  # Kop 2, secundaire tekst, subplot-titels
ZORGI_LIGHT_BLUE = "#609fce"  # Kop 3, accenten, baseline-lijn
ZORGI_ULTRA_LIGHT = "#d7e7f3"  # Achtergronden, kaarten, containers
# == Basiskleuren ==============================================================
ZORGI_WHITE = "#ffffff"
ZORGI_BODY_TEXT = "#1a1a1a"  # Body text, as-labels, tick-tekst
# == Gradient (Design System §2) ==============================================
# Richting: links naar rechts — Dark Blue naar Purple naar Red
ZORGI_GRADIENT_CSS = "linear-gradient(to right, #003a70, #7f4267, #dc2b26)"
ZORGI_GRADIENT_STOPS: tuple[str, str, str] = (ZORGI_DARK_BLUE, ZORGI_PURPLE, ZORGI_RED)
# == Pijlerkleuren (kompasmetafoor — conform PILLAR_REGISTRY) =================
ZORGI_PILLAR_COLORS: dict[str, str] = {
    "zorgi": ZORGI_DARK_BLUE,  # Centrum
    "pharma": ZORGI_LIGHT_BLUE,  # Noord
    "care": ZORGI_GREY_BLUE,  # Oost
    "care_admin": "#a06b8a",  # West — afgeleide 60%-gradient Purple naar ULB
    "erp4hc": ZORGI_PURPLE,  # Zuid
}
# == Typografie (Design System §3) ============================================
ZORGI_FONT_PRIMARY = "Poppins"
ZORGI_FONT_FALLBACK = "Verdana"
ZORGI_FONT_STACK = f"'{ZORGI_FONT_PRIMARY}', '{ZORGI_FONT_FALLBACK}', sans-serif"
# == Functionele uitbreidingen ================================================
# Niet in het officiële ZORGI Design System — bewust gedocumenteerde uitzonderingen.
# Bordeaux — drempel- en referentielijnen in matplotlib (alle 4 subplots).
# Visueel neutraal tussenpunt op de ZORGI-gradient (Dark Blue -> Purple -> Red).
# Voldoende contrast op ZORGI_ULTRA_LIGHT achtergrond zonder datalijnen te domineren.
# Ref: ADR-012 (architectuur-beslissingen.md) + fase3d-evolutie-visualisatie.md §4
ZORGI_BORDEAUX = "#722F37"
# Licht Paars — OAZIS/care_admin pijlerkleur.
# Afgeleid als 60%-gradient tussenstap Purple (#7f4267) naar Ultra Light (#d7e7f3).
ZORGI_LIGHT_PURPLE = "#a06b8a"
# Functioneel groen — positieve delta-bars in evolutie-visualisatie (Optie B).
# Groen heeft semantische waarde (verbetering) als visuele taal voor de lezer.
# Bewuste uitzondering op ZORGI Design System.
# Ref: fase3d-evolutie-visualisatie.md §4.4 (Optie B)
ZORGI_FUNC_POSITIVE = "#2e7d32"
# Chart/plot achtergrond — matplotlib figuur- en subplot-achtergrond.
# Lichter dan ZORGI_ULTRA_LIGHT (#d7e7f3) voor betere leesbaarheid op papier.
# Behoudt de ZORGI-blauwtint (B=254 dominant) in tegenstelling tot neutraal grijs.
# Gridlijnen blijven op ZORGI_ULTRA_LIGHT voor subtiel contrast op deze achtergrond.
ZORGI_CHART_BG = "#f7fbfe"
