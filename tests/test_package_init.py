"""Tests voor csat.__init__ — versie-initialisatie en alle fallback-paden.

Dekt de drie codepaden:
1. Normaal pad: importlib.metadata.version() geeft versie terug.
2. Fallback pad: PackageNotFoundError → versie gelezen uit pyproject.toml.
3. Dev-fallback (regels 16-17): beide bovenstaande falen → __version__ = 'dev'.
"""

import sys
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import patch

import pytest


def _purge_csat() -> None:
    """Verwijder alle gecachte csat-modules zodat __init__.py opnieuw wordt uitgevoerd."""
    for key in list(sys.modules.keys()):
        if key == "csat" or key.startswith("csat."):
            del sys.modules[key]


@pytest.fixture(autouse=True)
def _isolate_csat_module():
    """Zorg voor een schone module-state vóór én na elke test.

    Na de test worden de originele csat-modules hersteld zodat andere
    testbestanden (die klassen bij import-time inladen) hun module-referenties
    niet verliezen. Zonder herstel zouden patch()-aanroepen in andere tests
    een nieuw module-object patchen terwijl de al-geïmporteerde klassen
    nog de globals van het originele object gebruiken.
    """
    # Sla de actuele csat-modules op vóór de test
    saved = {k: v for k, v in sys.modules.items() if k == "csat" or k.startswith("csat.")}
    _purge_csat()
    yield
    _purge_csat()
    # Herstel de originele modules zodat andere tests ongestoord blijven
    sys.modules.update(saved)


def test_version_from_metadata() -> None:
    """Normaal pad: __version__ via importlib.metadata.version()."""
    import csat  # noqa: PLC0415

    assert isinstance(csat.__version__, str)
    assert len(csat.__version__) > 0


def test_version_from_pyproject_fallback() -> None:
    """Fallback pad: PackageNotFoundError → versie uit pyproject.toml."""
    with patch(
        "importlib.metadata.version",
        side_effect=PackageNotFoundError("csat-compass"),
    ):
        import csat  # noqa: PLC0415

    assert isinstance(csat.__version__, str)
    assert csat.__version__ != "dev"


def test_version_dev_fallback() -> None:  # dekt regels 16-17
    """Dev-fallback: zowel metadata als pyproject.toml niet beschikbaar → 'dev'."""
    with (
        patch(
            "importlib.metadata.version",
            side_effect=PackageNotFoundError("csat-compass"),
        ),
        patch.object(Path, "open", side_effect=OSError("bestand niet leesbaar")),
    ):
        import csat  # noqa: PLC0415

    assert csat.__version__ == "dev"
