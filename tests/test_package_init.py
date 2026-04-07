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
    """Zorg voor een schone module-state voor én na elke test."""
    _purge_csat()
    yield
    _purge_csat()


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
