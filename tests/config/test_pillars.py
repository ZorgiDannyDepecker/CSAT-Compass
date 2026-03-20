"""
Unit tests voor src/csat/config/pillars.py.
Dekt PILLAR_REGISTRY structuur + get_pillar_for_product() volledig.
"""

from csat.config.pillars import (
    HIGH_CRITICAL_PRIORITIES,
    PILLAR_REGISTRY,
    VIEW_COLUMNS,
    get_pillar_for_product,
)

# ------------------------------------------------------------------
# PILLAR_REGISTRY structuur
# ------------------------------------------------------------------


class TestPillarRegistry:
    """Basiscontroles op de registry-structuur."""

    def test_alle_pijlers_aanwezig(self) -> None:
        verwacht = {"zorgi", "pharma", "care", "care_admin", "erp4hc"}
        assert set(PILLAR_REGISTRY.keys()) == verwacht

    def test_elke_pijler_heeft_verplichte_sleutels(self) -> None:
        verplicht = {"name", "name_fr", "direction", "color", "products"}
        for key, config in PILLAR_REGISTRY.items():
            assert verplicht.issubset(config.keys()), f"Sleutel ontbreekt in pijler '{key}'"

    def test_pharma_product_correct(self) -> None:
        assert "PHARMA" in PILLAR_REGISTRY["pharma"]["products"]

    def test_care_product_correct(self) -> None:
        assert "CARE" in PILLAR_REGISTRY["care"]["products"]

    def test_zorgi_geen_producten(self) -> None:
        """zorgi is aggregatie — geen directe productfilter."""
        assert PILLAR_REGISTRY["zorgi"]["products"] == []


class TestHighCriticalPriorities:
    def test_high_aanwezig(self) -> None:
        assert "High" in HIGH_CRITICAL_PRIORITIES

    def test_critical_aanwezig(self) -> None:
        assert "Critical" in HIGH_CRITICAL_PRIORITIES

    def test_highest_aanwezig(self) -> None:
        assert "Highest" in HIGH_CRITICAL_PRIORITIES


class TestViewColumns:
    def test_ticket_id_kolom(self) -> None:
        assert VIEW_COLUMNS["ticket_id"] == "key"

    def test_score_kolom(self) -> None:
        assert VIEW_COLUMNS["score"] == "score"


# ------------------------------------------------------------------
# get_pillar_for_product — alle paden
# ------------------------------------------------------------------


class TestGetPillarForProduct:
    """Volledige dekking van get_pillar_for_product() — regels 79-88."""

    def test_pharma(self) -> None:
        assert get_pillar_for_product("PHARMA") == "pharma"

    def test_care(self) -> None:
        assert get_pillar_for_product("CARE") == "care"

    def test_care_admin_met_spatie(self) -> None:
        assert get_pillar_for_product("CARE ADMIN") == "care_admin"

    def test_care_admin_met_underscore(self) -> None:
        assert get_pillar_for_product("CARE_ADMIN") == "care_admin"

    def test_erp4hc(self) -> None:
        assert get_pillar_for_product("ERP4HC") == "erp4hc"

    def test_onbekend_product(self) -> None:
        assert get_pillar_for_product("ONBEKEND") == "unknown"

    def test_lege_string(self) -> None:
        assert get_pillar_for_product("") == "unknown"

    def test_case_insensitive_lowercase(self) -> None:
        assert get_pillar_for_product("pharma") == "pharma"

    def test_case_insensitive_mixed(self) -> None:
        assert get_pillar_for_product("PhArMa") == "pharma"

    def test_witruimte_wordt_genegeerd(self) -> None:
        assert get_pillar_for_product("  PHARMA  ") == "pharma"

    def test_zorgi_sleutel_nooit_teruggegeven(self) -> None:
        """zorgi is aggregatiepijler — mag nooit als productmatch teruggegeven worden."""
        result = get_pillar_for_product("ZORGI")
        assert result == "unknown"
