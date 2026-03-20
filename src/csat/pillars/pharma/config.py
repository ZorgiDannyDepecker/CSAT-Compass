"""
ZORGI PHARMA-specifieke drempelwaarden en configuratie voor CSAT-analyse.

Drempelwaarden reactiegraad en High/Critical zijn bevestigd door het team.
Overige drempelwaarden (avg_score, MoM-trend) worden ingevuld na data-exploratie.
"""

# Pijler-identificatie
PILLAR_KEY = "pharma"

# Productfilter — exacte waarde zoals ze voorkomt in de product-kolom van V_CSAT_1
# ⚠️ Te bevestigen na de eerste DB-connectie via df["product"].value_counts()
PRODUCT_FILTER = "ZORGI PHARMA"

# ------------------------------------------------------------------
# KPI-drempelwaarden — bevestigd door team
# ------------------------------------------------------------------

REACTIEGRAAD_MIN: float = 85.0
"""Minimale reactiegraad in % — tickets met een CSAT-score t.o.v. totaal."""

HIGH_CRITICAL_MAX: float = 15.0
"""Maximaal aandeel High/Critical-tickets in % t.o.v. totaal."""

# ------------------------------------------------------------------
# KPI-drempelwaarden — TBD na data-exploratie
# ------------------------------------------------------------------

AVG_SCORE_MIN: float | None = None
"""Minimale gemiddelde CSAT-score — in te vullen na df["score"].describe()."""

MOM_TREND_THRESHOLD: float | None = None
"""Significante MoM-variatie in scorepunten — in te vullen na baseline-exploratie."""

# ------------------------------------------------------------------
# Score-bereik — te bevestigen via df["score"].describe()
# ------------------------------------------------------------------

SCORE_MIN: int = 1
SCORE_MAX: int = 5

# ------------------------------------------------------------------
# Weergavenamen
# ------------------------------------------------------------------

PILLAR_NAME_NL: str = "ZORGI PHARMA"
PILLAR_NAME_FR: str = "ZORGI PHARMA"
PILLAR_DIRECTION: str = "↑"  # Noord — U+2191 (Arrows-blok)
