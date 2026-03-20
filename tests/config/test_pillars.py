"""
Unit tests voor src/csat/config/pillars.py.
Dekt PILLAR_REGISTRY structuur + get_pillar_for_domain() volledig.
"""

from csat.config.pillars import (
    FILTER_COLUMN,
    HIGH_CRITICAL_PRIORITIES,
    PILLAR_REGISTRY,
    VIEW_COLUMNS,
    get_pillar_for_domain,
)


class TestPillarRegistry:
    """Basiscontroles op de registry-structuur."""

    def test_alle_pijlers_aanwezig(self) -> None:
        verwacht = {"zorgi", "pharma", "care", "care_admin", "erp4hc"}
        assert set(PILLAR_REGISTRY.keys()) == verwacht

    def test_elke_pijler_heeft_verplichte_sleutels(self) -> None:
        verplicht = {"name", "name_fr", "direction", "color", "products"}
        for key, config in PILLAR_REGISTRY.items():
            assert verplicht.issubset(config.keys()), f"Sleutel ontbreekt in pijler '{key}'"

    def test_pharma_domein_correct(self) -> None:
        assert "PHARMA" in PILLAR_REGISTRY["pharma"]["products"]

    def test_care_domein_correct(self) -> None:
        assert "CARE" in PILLAR_REGISTRY["care"]["products"]

    def test_care_admin_domein_correct(self) -> None:
        assert "CARE ADMIN" in PILLAR_REGISTRY["care_admin"]["products"]

    def test_erp_domein_correct(self) -> None:
        assert "ERP" in PILLAR_REGISTRY["erp4hc"]["products"]

    def test_zorgi_aggregeert_alle_vier_domeinen(self) -> None:
        """zorgi filtert op alle 4 domeinen — sluit BI/EXTRAMUROS/HRM/MOBILE uit."""
        zorgi_products = PILLAR_REGISTRY["zorgi"]["products"]
        for domein in ["PHARMA", "CARE", "CARE ADMIN", "ERP"]:
            assert domein in zorgi_products


class TestFilterColumn:
    def test_filterkolom_is_product_domain(self) -> None:
        assert FILTER_COLUMN == "product_domain"


class TestHighCriticalPriorities:
    def test_blocker_aanwezig(self) -> None:
        assert "Blocker" in HIGH_CRITICAL_PRIORITIES

    def test_critical_aanwezig(self) -> None:
        assert "Critical" in HIGH_CRITICAL_PRIORITIES

    def test_major_aanwezig(self) -> None:
        assert "Major" in HIGH_CRITICAL_PRIORITIES

    def test_trivial_niet_aanwezig(self) -> None:
        assert "Trivial" not in HIGH_CRITICAL_PRIORITIES

    def test_minor_niet_aanwezig(self) -> None:
        assert "Minor" not in HIGH_CRITICAL_PRIORITIES


class TestViewColumns:
    def test_ticket_id_kolom(self) -> None:
        assert VIEW_COLUMNS["ticket_id"] == "key"

    def test_score_kolom(self) -> None:
        assert VIEW_COLUMNS["score"] == "score"

    def test_product_domain_kolom(self) -> None:
        assert VIEW_COLUMNS["product_domain"] == "product_domain"


class TestGetPillarForDomain:
    """Volledige dekking van get_pillar_for_domain()."""

    def test_pharma(self) -> None:
        assert get_pillar_for_domain("PHARMA") == "pharma"

    def test_care(self) -> None:
        assert get_pillar_for_domain("CARE") == "care"

    def test_care_admin(self) -> None:
        assert get_pillar_for_domain("CARE ADMIN") == "care_admin"

    def test_erp(self) -> None:
        assert get_pillar_for_domain("ERP") == "erp4hc"

    def test_onbekend_domein(self) -> None:
        assert get_pillar_for_domain("BI") == "unknown"

    def test_extramuros_genegeerd(self) -> None:
        assert get_pillar_for_domain("EXTRAMUROS") == "unknown"

    def test_hrm_genegeerd(self) -> None:
        assert get_pillar_for_domain("HRM") == "unknown"

    def test_mobile_genegeerd(self) -> None:
        assert get_pillar_for_domain("MOBILE") == "unknown"

    def test_lege_string(self) -> None:
        assert get_pillar_for_domain("") == "unknown"

    def test_case_insensitive(self) -> None:
        assert get_pillar_for_domain("pharma") == "pharma"

    def test_case_insensitive_mixed(self) -> None:
        assert get_pillar_for_domain("PhArMa") == "pharma"

    def test_witruimte_wordt_genegeerd(self) -> None:
        assert get_pillar_for_domain("  PHARMA  ") == "pharma"

    def test_zorgi_sleutel_nooit_teruggegeven(self) -> None:
        """zorgi is aggregatiepijler — mag nooit als domeinmatch teruggegeven worden."""
        assert get_pillar_for_domain("ZORGI") == "unknown"
