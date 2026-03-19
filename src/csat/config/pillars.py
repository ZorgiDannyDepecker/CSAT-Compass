"""
Pijler-definities voor CSAT-Compass.
Koppelt product-waarden uit V_CSAT_1 aan de ZORGI-pijlers.
"""

# Pijler-register — alle ZORGI-pijlers inclusief overall
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
        "products": ["PHARMA"],
    },
    "care": {
        "name": "CARE",
        "name_fr": "CARE",
        "direction": "oost",
        "color": "#00AA44",
        "products": ["CARE"],
    },
    "care_admin": {
        "name": "CARE ADMIN",
        "name_fr": "CARE ADMIN",
        "direction": "west",
        "color": "#FF6600",
        "products": ["CARE ADMIN", "CARE_ADMIN"],
    },
    "erp4hc": {
        "name": "ERP4HC",
        "name_fr": "ERP4HC",
        "direction": "zuid",
        "color": "#9900CC",
        "products": ["ERP4HC"],
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
HIGH_CRITICAL_PRIORITIES = ["High", "Critical", "Highest"]

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
