# CSAT-Compass — Instructie GHC: Fase A uitvoeren

**Datum:** 23/03/2026
**Opdracht:** Voer alle Fase A acties uit conform voorstel-design-system-integratie-v4.md
**Context:** Dit document is opgesteld door Claude na overleg met Danny Depecker. GHC voert de code-wijzigingen en tests uit in PyCharm. Claude doet Fase B+C apart.

**Bronnen in repo:**

- Voorstel: `voorstel-design-system-integratie-v4.md`
- GHC-review: `WIP/advisor-design-system-integratie.md`
- Design System: wordt als A1 toegevoegd

---

## Volgorde van uitvoering

Voer de acties uit in de onderstaande volgorde. Run `pytest` na elke groep wijzigingen.

---

## A1 — Design System toevoegen aan repo

**Kopieer** `C:\Users\danndepe\Documents\AI\Templates_Icons\ZORGI_Design_System.md`
**Naar** `docs/01-strategisch/ZORGI_Design_System.md`

Geen inhoudelijke wijzigingen.

---

## A2 — Pijlerkleuren in `pillars.py` vervangen

**Bestand:** `src/csat/config/pillars.py`

Vervang de `color`-waarde in elk item van `PILLAR_REGISTRY`:

| Pijler | HUIDIG | NIEUW |
|---|---|---|
| `zorgi` | `"#003366"` | `"#003a70"` |
| `pharma` | `"#0066CC"` | `"#609fce"` |
| `care` | `"#00AA44"` | `"#5f8495"` |
| `care_admin` | `"#FF6600"` | `"#a06b8a"` |
| `erp4hc` | `"#9900CC"` | `"#7f4267"` |

Voeg bij elke kleur een commentaar toe met de kleurnaam:

```python
"color": "#003a70",  # Dark Blue — conform ZORGI Design System
"color": "#609fce",  # Light Blue — conform ZORGI Design System
"color": "#5f8495",  # Grey Blue — conform ZORGI Design System
"color": "#a06b8a",  # Light Purple — afgeleide 60% gradient Purple→ULB
"color": "#7f4267",  # Purple — conform ZORGI Design System
```

---

## A10 — Fix `erp4hc.name` en `name_fr` → superscript

**Bestand:** `src/csat/config/pillars.py` (zelfde bestand als A2)

In het `erp4hc`-blok, vervang:

```python
# HUIDIG
"name": "ERP4HC",
"name_fr": "ERP4HC",

# NIEUW
"name": "ERP4HC²·⁰",
"name_fr": "ERP4HC²·⁰",
```

`report_name` en `report_name_fr` zijn al correct — niet aanraken.

---

## A11 — Fix `report_name` voor pharma en care

**Bestand:** `src/csat/config/pillars.py` (zelfde bestand als A2)

In het `pharma`-blok, vervang:

```python
# HUIDIG
"report_name": "ZORGI PHARMA",
"report_name_fr": "ZORGI PHARMA",

# NIEUW
"report_name": "PHARMA",
"report_name_fr": "PHARMA",
```

In het `care`-blok, vervang:

```python
# HUIDIG
"report_name": "ZORGI CARE",
"report_name_fr": "ZORGI CARE",

# NIEUW
"report_name": "CARE",
"report_name_fr": "CARE",
```

---

## A3 — `PILLAR_COLORS` in `branding.py` corrigeren

**Bestand:** `src/csat/utils/branding.py`

Vervang het volledige `PILLAR_COLORS`-blok:

```python
# HUIDIG
PILLAR_COLORS: dict[str, str] = {
    "zorgi": "#003a70",  # Dark Blue — centrum
    "pharma": "#003a70",  # Noord
    "care": "#609fce",  # Oost
    "care_admin": "#5f8495",  # West
    "erp4hc": "#7f4267",  # Zuid
}

# NIEUW
PILLAR_COLORS: dict[str, str] = {
    "zorgi": "#003a70",       # Dark Blue — centrum
    "pharma": "#609fce",      # Light Blue — noord
    "care": "#5f8495",        # Grey Blue — oost
    "care_admin": "#a06b8a",  # Light Purple — west (afgeleide gradient)
    "erp4hc": "#7f4267",      # Purple — zuid
}
```

---

## A4 — `PILLAR_COLORWAY` bijwerken

**Bestand:** `src/csat/utils/branding.py`

`PILLAR_COLORWAY` is gedefinieerd als `list(PILLAR_COLORS.values())`. Na de correctie in A3 klopt de inhoud automatisch. **Controleer** dat de volgorde na A3 correct is:

```python
# Verwacht resultaat na A3:
["#003a70", "#609fce", "#5f8495", "#a06b8a", "#7f4267"]
# centrum → noord → oost → west → zuid
```

Geen code-wijziging nodig als de dict-volgorde in A3 correct is (Python 3.7+ behoudt insertie-volgorde).

---

## A9 — Fix `PLOTLY_LAYOUT.colorway` — rood vervangen

**Bestand:** `src/csat/utils/branding.py`

In het `PLOTLY_LAYOUT`-dict, vervang de `colorway`-lijst:

```python
# HUIDIG
"colorway": [
    COLORS["dark_blue"],
    COLORS["light_blue"],
    COLORS["grey_blue"],
    COLORS["purple"],
    COLORS["red"],
],

# NIEUW
"colorway": [
    COLORS["dark_blue"],
    COLORS["light_blue"],
    COLORS["grey_blue"],
    "#a06b8a",              # Light Purple — OAZIS
    COLORS["purple"],
],
```

**Let op:** rood (`COLORS["red"]`) wordt verwijderd uit de colorway. Rood is uitsluitend gereserveerd voor `trend-down` en alarmen.

---

## A5 — Logo-assets kopiëren en hernoemen

**Bron:** `C:\Users\danndepe\Documents\AI\Templates_Icons`
**Doel:** `src/static/img/` (map aanmaken als deze niet bestaat)

| Kopieer | Hernoem naar |
|---|---|
| `Logo-icoon_144_x_144_px_wit.png` | `heartbeat_144_wit.png` |
| `Logo-icoon 144 x 144 px.png` | `heartbeat_144_kleur.png` |
| `Logo-icoon 512 x 512 px wit.png` | `heartbeat_512_wit.png` |
| `Logo-icoon 512 x 512 px.png` | `heartbeat_512_kleur.png` |
| `ZORGI_hartje_transparant.png` | `heartbeat_hires_transparant.png` |
| `Zorgi_hartje.png` | `heartbeat_klein_kleur.png` |

**Niet kopiëren:** alle andere bestanden (cirkel-varianten, 192px-varianten, .md).

---

## A6 — `LOGO_ASSETS` dict toevoegen aan `branding.py`

**Bestand:** `src/csat/utils/branding.py`

Voeg toe **na** het `COLORS`-blok en **voor** `PILLAR_COLORS`:

```python
from pathlib import Path

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
_IMG_DIR = _STATIC_DIR / "img"
_FONTS_DIR = _STATIC_DIR / "fonts"

# =============================================================================
# Logo-assets — conform Design System sectie 4
# =============================================================================

LOGO_ASSETS: dict[str, Path] = {
    "heartbeat_144_wit": _IMG_DIR / "heartbeat_144_wit.png",
    "heartbeat_144_kleur": _IMG_DIR / "heartbeat_144_kleur.png",
    "heartbeat_512_wit": _IMG_DIR / "heartbeat_512_wit.png",
    "heartbeat_512_kleur": _IMG_DIR / "heartbeat_512_kleur.png",
    "heartbeat_hires_transparant": _IMG_DIR / "heartbeat_hires_transparant.png",
    "heartbeat_klein_kleur": _IMG_DIR / "heartbeat_klein_kleur.png",
}
```

**Let op:** de `from pathlib import Path` staat mogelijk al bovenaan het bestand. Controleer en voorkom dubbele imports.

Update ook de module-docstring bovenaan:

```python
# HUIDIG
"""Gebaseerd op .github/docs/zorgi-design-system.md — single source of truth."""

# NIEUW
"""Gebaseerd op docs/01-strategisch/ZORGI_Design_System.md — single source of truth."""
```

---

## A7 — Validatietests kleuren

**Bestand:** `tests/utils/test_branding.py`

Voeg **twee** nieuwe testklassen toe:

```python
from csat.config.pillars import PILLAR_REGISTRY

# Toegestaan kleurenpalet: ZORGI Design System + afgeleide
ALLOWED_COLORS = {
    "#003a70",   # Dark Blue
    "#dc2b26",   # Red
    "#7f4267",   # Purple
    "#5f8495",   # Grey Blue
    "#609fce",   # Light Blue
    "#d7e7f3",   # Ultra Light Blue
    "#a06b8a",   # Light Purple (afgeleide — ADR-010)
}


class TestPijlerkleuren:
    """Validatie: alle pijlerkleuren zijn on-brand."""

    def test_alle_pijlerkleuren_in_toegestaan_palet(self) -> None:
        for key, config in PILLAR_REGISTRY.items():
            kleur = config["color"].lower()
            assert kleur in ALLOWED_COLORS, (
                f"Pijler '{key}' heeft off-brand kleur {kleur} — "
                f"toegestaan: {ALLOWED_COLORS}"
            )

    def test_pillar_colors_consistent_met_registry(self) -> None:
        """PILLAR_COLORS in branding.py moet exact overeenkomen met pillars.py."""
        for key in PILLAR_COLORS:
            assert key in PILLAR_REGISTRY, f"'{key}' in PILLAR_COLORS maar niet in PILLAR_REGISTRY"
            assert PILLAR_COLORS[key].lower() == PILLAR_REGISTRY[key]["color"].lower(), (
                f"Pijler '{key}': branding.py={PILLAR_COLORS[key]}, "
                f"pillars.py={PILLAR_REGISTRY[key]['color']}"
            )
```

---

## A8 — Validatietest logo-paden

**Bestand:** `tests/utils/test_branding.py`

```python
from csat.utils.branding import LOGO_ASSETS


class TestLogoAssets:
    """Validatie: alle logo-assets bestaan op schijf."""

    def test_alle_logo_paden_bestaan(self) -> None:
        for naam, pad in LOGO_ASSETS.items():
            assert pad.exists(), f"Logo-asset '{naam}' niet gevonden: {pad}"

    def test_minstens_6_assets(self) -> None:
        assert len(LOGO_ASSETS) >= 6
```

---

## Verificatie na alle acties

1. **Run `pytest`** — alle bestaande + nieuwe tests moeten slagen
2. **Run `ruff check src/`** — geen linting-fouten
3. **Run `mypy src/`** — geen type-fouten
4. **Visuele check:** open `src/csat/config/pillars.py` en bevestig dat elke pijler een unieke kleur heeft
5. **Visuele check:** open `src/static/img/` en bevestig dat 6 PNG-bestanden aanwezig zijn

---

## Wat GHC NIET moet doen

- **Niet** `src/dashboard/app.py` aanraken (leeg — wordt later gebouwd)
- **Niet** Jinja2-templates wijzigen (dat doet Claude in Fase B)
- **Niet** `report_exporter.py` wijzigen (dat doet Claude in Fase B)
- **Niet** `apply_matplotlib_theme()` toevoegen (dat doet Claude in Fase B)
- **Niet** `add_watermark()` toevoegen (dat doet Claude in Fase B)
- **Niet** ADR-010 schrijven (dat doet Claude in Fase C)
- **Niet** `.streamlit/config.toml` aanpassen (is correct en bestaat wél, ondanks GHC-review §2.2)
- **Niet** `zorgi-report.css` aanpassen (is al conform)
- **Niet** Poppins TTF-bestanden downloaden (dat doet Claude in Fase B)

---

## Samenvatting wijzigingen per bestand

| Bestand | Acties | Type |
|---|---|---|
| `docs/01-strategisch/ZORGI_Design_System.md` | A1 | 📋 Nieuw (kopiëren) |
| `src/csat/config/pillars.py` | A2, A10, A11 | 🔧 Wijzigen |
| `src/csat/utils/branding.py` | A3, A4, A6, A9 | 🔧 Wijzigen |
| `src/static/img/` (6 bestanden) | A5 | 📋 Nieuw (kopiëren + hernoemen) |
| `tests/utils/test_branding.py` | A7, A8 | 🧪 Uitbreiden |
