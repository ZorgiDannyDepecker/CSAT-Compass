"""
Pijler-definities voor CSAT-Compass.
Koppelt product-waarden uit V_CSAT_1 aan de ZORGI-pijlers.
"""

# Pijler-register — alle ZORGI-pijlers inclusief overall
# Product-waarden bevestigd via df["product"].value_counts() op V_CSAT_1 (20/03/2026)
# ⚠️ Producten zonder pijler (ECO/BOEK, H++/EPR, OmniPro, HRM, enz.) — te bevestigen door Danny
PILLAR_REGISTRY: dict[str, dict] = {
    "zorgi": {
        "name": "ZORGI",
        "name_fr": "ZORGI",
        "direction": "centrum",
        "color": "#003366",
        "products": [],  # aggregatie — geen directe productfilter
    },
    "pharma": {
        "name": "PHARMA",
        "name_fr": "PHARMA",
        "direction": "noord",
        "color": "#0066CC",
        "products": ["Apotheek", "AZIS Pharmacy"],  # bevestigd 20/03/2026
    },
    "care": {
        "name": "CARE",
        "name_fr": "CARE",
        "direction": "oost",
        "color": "#00AA44",
        "products": ["ZORGI CARE"],  # bevestigd 20/03/2026
    },
    "care_admin": {
        "name": "CARE ADMIN",
        "name_fr": "CARE ADMIN",
        "direction": "west",
        "color": "#FF6600",
        "products": ["Oazis", "ZORGI Care Admin"],  # bevestigd 20/03/2026
    },
    "erp4hc": {
        "name": "ERP4HC",
        "name_fr": "ERP4HC",
        "direction": "zuid",
        "color": "#9900CC",
        "products": ["ERP4HC2.0", "ERP4HC"],  # bevestigd 20/03/2026
        # ⚠️ Te bevestigen: ECO/BOEK (327), HRM (193), PADM/TARFAC (108) ook ERP?
    },
}

# Kolomnamen zoals ze voorkomen in [dbo].[V_CSAT_1]
VIEW_COLUMNS = {
    "ticket_id": "key",
    "issue_type": "issue_type",
    "priority": "priority",
    "summary": "summary",
    "score": "score",
    "comment": "comment",
    "satisfaction_date": "satisfaction_date",
    "created": "created",
    "hospital": "hospital",
    "product": "product",
    "product_domain": "product_domain",
    "project_key": "project_key",
}

# Prioriteitswaarden die als High/Critical worden beschouwd
# Bevestigd via df["priority"].value_counts() op V_CSAT_1 (20/03/2026)
# Jira-schaal: Blocker > Critical > Major > Minor > Trivial
# ⚠️ Major is nog te bevestigen door Danny — staat nu wel inbegrepen
HIGH_CRITICAL_PRIORITIES = ["Blocker", "Critical", "Major"]

# Score-bereik (wordt bevestigd na eerste data-exploratie)
SCORE_MIN = 1
SCORE_MAX = 5


def get_pillar_for_product(product: str) -> str:
    """
    Geef de pijlersleutel terug op basis van de product-waarde uit de view.

    Args:
        product: Waarde uit de product-kolom van V_CSAT_1

    Returns:
        Pijlersleutel (pharma, care, care_admin, erp4hc) of 'unknown'
    """
    if not product:
        return "unknown"
    product_upper = product.strip().upper()
    for pillar_key, pillar_config in PILLAR_REGISTRY.items():
        if pillar_key == "zorgi":
            continue
        for p in pillar_config["products"]:
            if p.upper() == product_upper:
                return pillar_key
    return "unknown"
