"""
Pijler-definities voor CSAT-Compass.
Filtert op de kolom 'product_domain' uit V_CSAT_1.

Bevestigd door Danny Depecker op 20/03/2026 via Excel-review van V_CSAT_1:
- Filterkolom: product_domain
- Relevante waarden: PHARMA, CARE, CARE ADMIN, ERP
- Genegeerd: BI, EXTRAMUROS, HRM, MOBILE
"""

# Kolom waarop de pijlerfilter toegepast wordt — bevestigd 20/03/2026
FILTER_COLUMN = "product_domain"

# Pijler-register — alle ZORGI-pijlers inclusief overall
# 'products' = waarden uit de kolom product_domain (niet product)
PILLAR_REGISTRY: dict[str, dict] = {
    "zorgi": {
        "name": "ZORGI",
        "name_fr": "ZORGI",
        "report_name": "ZORGI",
        "report_name_fr": "ZORGI",
        "direction": "centrum",
        "color": "#003a70",  # Dark Blue — conform ZORGI Design System
        # Aggregatie van alle 4 relevante domeinen — sluit BI/EXTRAMUROS/HRM/MOBILE uit
        "products": ["PHARMA", "CARE", "CARE ADMIN", "ERP"],
    },
    "pharma": {
        "name": "PHARMA",
        "name_fr": "PHARMA",
        "report_name": "ZORGI PHARMA",
        "report_name_fr": "ZORGI PHARMA",
        "direction": "noord",
        "color": "#609fce",  # Light Blue — conform ZORGI Design System
        "products": ["PHARMA"],
    },
    "care": {
        "name": "CARE",
        "name_fr": "CARE",
        "report_name": "CARE",
        "report_name_fr": "CARE",
        "direction": "oost",
        "color": "#5f8495",  # Grey Blue — conform ZORGI Design System
        "products": ["CARE"],
    },
    "care_admin": {
        "name": "CARE ADMIN",
        "name_fr": "CARE ADMIN",
        "report_name": "OAZIS",
        "report_name_fr": "OAZIS",
        "direction": "west",
        "color": "#a06b8a",  # Light Purple — afgeleide pillar-kleur (60% menging Purple #7f4267 → Ultra Light Blue #d7e7f3)
        "products": ["CARE ADMIN"],
    },
    "erp4hc": {
        "name": "ERP4HC²·⁰",
        "name_fr": "ERP4HC²·⁰",
        "report_name": "ERP4HC²·⁰",
        "report_name_fr": "ERP4HC²·⁰",
        "direction": "zuid",
        "color": "#7f4267",  # Purple — conform ZORGI Design System
        "products": ["ERP"],
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

# Prioriteitswaarden die als hoog-kritisch worden beschouwd
# Jira-schaal in V_CSAT_1: Blocker > Critical > Major > Minor > Trivial
# Bevestigd door Danny op 20/03/2026
HIGH_CRITICAL_PRIORITIES = ["Blocker", "Critical", "Major"]

# Score-bereik — bevestigd via data-exploratie 20/03/2026
SCORE_MIN = 1
SCORE_MAX = 5


def get_pillar_for_domain(domain: str) -> str:
    """
    Geef de pijlersleutel terug op basis van product_domain uit V_CSAT_1.

    Args:
        domain: Waarde uit de product_domain-kolom (bv. 'PHARMA', 'ERP')

    Returns:
        Pijlersleutel (pharma, care, care_admin, erp4hc) of 'unknown'
    """
    if not domain:
        return "unknown"
    domain_upper = domain.strip().upper()
    for pillar_key, pillar_config in PILLAR_REGISTRY.items():
        if pillar_key == "zorgi":
            continue
        for p in pillar_config["products"]:
            if p.upper() == domain_upper:
                return pillar_key
    return "unknown"
