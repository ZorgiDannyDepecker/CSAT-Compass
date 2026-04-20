"""
ZORGI CARE-specifieke drempelwaarden en configuratie voor CSAT-analyse.

Drempelwaarden zijn initieel gelijkgesteld aan PHARMA-baseline (15% H/C).
Bijsturing mogelijk na gesprekken met CARE-manager.
"""

# Pijler-identificatie
PILLAR_KEY = "care"

# Filterwaarde in product_domain-kolom — bevestigd 20/04/2026
PRODUCT_FILTER = "CARE"

# ------------------------------------------------------------------
# KPI-drempelwaarden — gebaseerd op PHARMA-baseline
# ------------------------------------------------------------------

# ⚠️ REACTIEGRAAD — NIET MEETBAAR (zie ADR-006, 20/03/2026)
REACTIEGRAAD_MIN: float | None = None  # N/A — zie ADR-006
"""Reactiegraad drempel — niet activeerbaar zonder uitnodigingsdata."""

HIGH_CRITICAL_MAX: float = 15.0
"""Maximaal aandeel Blocker/Critical/Major-tickets in % t.o.v. totaal."""

# ------------------------------------------------------------------
# KPI-drempelwaarden — TBD na data-exploratie en managementgesprekken
# ------------------------------------------------------------------

AVG_SCORE_MIN: float | None = None
"""Minimale gemiddelde CSAT-score — in te vullen na data-exploratie."""

MOM_TREND_THRESHOLD: float | None = None
"""Significante MoM-variatie in scorepunten — in te vullen na baseline-exploratie."""

# ------------------------------------------------------------------
# Score-bereik
# ------------------------------------------------------------------

SCORE_MIN: int = 1
SCORE_MAX: int = 5

# ------------------------------------------------------------------
# Weergavenamen
# ------------------------------------------------------------------

PILLAR_NAME_NL: str = "CARE"
PILLAR_NAME_FR: str = "CARE"
PILLAR_DIRECTION: str = "→"  # Oost — U+2192 (Arrows-blok)
