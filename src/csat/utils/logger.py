"""
Loguru-configuratie voor CSAT-Compass.
Configureert console- en bestandslogging met dagelijkse rotatie naar logs/.
"""

import sys
from pathlib import Path

from loguru import logger as _logger

# Exporteer de geconfigureerde logger als module-level object
logger = _logger


def setup_logger(log_path: Path, log_level: str = "INFO") -> None:
    """
    Configureer de Loguru logger voor CSAT-Compass.

    Verwijdert de standaard Loguru handler en voegt twee handlers toe:
    - Console: kleurrijk, compact, niveau conform log_level
    - Bestand: volledig, dagelijkse rotatie, 30 dagen bewaren

    Args:
        log_path: Map waar de logbestanden worden opgeslagen
        log_level: Minimaal logniveau voor console (DEBUG / INFO / WARNING / ERROR)
    """
    # Verwijder standaard Loguru stderr-handler
    _logger.remove()

    # Console handler — kleur + compact formaat
    _logger.add(
        sys.stderr,
        level=log_level.upper(),
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # Bestandshandler — dagelijkse rotatie, 30 dagen bewaren
    log_path.mkdir(parents=True, exist_ok=True)
    _logger.add(
        log_path / "csat-compass_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} — {message}",
        rotation="00:00",  # roteer elke dag om middernacht
        retention="30 days",  # bewaar logbestanden 30 dagen
        encoding="utf-8",
        enqueue=True,  # thread-safe asynchroon schrijven
    )

    _logger.debug(f"[logger] Logbestanden worden geschreven naar: {log_path}")
