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
