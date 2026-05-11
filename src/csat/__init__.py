"""CSAT-Compass — ZORGI klanttevredenheidsanalyse."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("csat-compass")
except PackageNotFoundError:
    # Fallback: pakket niet geïnstalleerd — lees versie rechtstreeks uit pyproject.toml
    import tomllib
    from pathlib import Path

    _pyproject = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    try:
        with _pyproject.open("rb") as _f:
            __version__ = tomllib.load(_f)["project"]["version"]
    except Exception:
        __version__ = "dev"

# Releasedatum — PROD: vaste datum uit pyproject.toml | DEMO: live timestamp in app.py
import tomllib as _tomllib
from pathlib import Path as _Path

_pyproject_path = _Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
try:
    with _pyproject_path.open("rb") as _f:
        __release_date__: str = _tomllib.load(_f)["project"]["release-date"]
except Exception:
    __release_date__ = ""
