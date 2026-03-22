"""
i18n-module voor CSAT-Compass.

Laadt taalspecifieke vertalingstabellen uit JSON-bestanden
voor gebruik in Jinja2-templates en overige rapportagecomponenten.

Ondersteunde talen: nl (Nederlands), fr (Frans)
"""

import json
from pathlib import Path
from typing import Any

_I18N_DIR = Path(__file__).parent

SUPPORTED_LANGS: tuple[str, ...] = ("nl", "fr")


def load_translations(lang: str) -> dict:
    """
    Laad de vertalingstabel voor de opgegeven taal.

    Args:
        lang: Taalcode — 'nl' of 'fr'

    Returns:
        Dict met alle vertalingssleutels voor de taal

    Raises:
        ValueError: Als de taalcode niet ondersteund wordt
        FileNotFoundError: Als het JSON-bestand ontbreekt
    """
    if lang not in SUPPORTED_LANGS:
        raise ValueError(f"Niet-ondersteunde taal: '{lang}' — kies uit {SUPPORTED_LANGS}")
    path = _I18N_DIR / f"{lang}.json"
    with path.open(encoding="utf-8") as f:
        result: dict[str, Any] = json.load(f)
        return result
