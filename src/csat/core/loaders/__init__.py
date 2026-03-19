"""
DataLoader factory voor CSAT-Compass.
Selecteert automatisch SQL- of CSV-loader op basis van beschikbaarheid.
"""

from pathlib import Path

from loguru import logger

from .base_loader import BaseLoader
from .csv_loader import CsvLoader
from .sql_loader import SqlLoader

__all__ = ["BaseLoader", "CsvLoader", "SqlLoader", "get_loader"]


def get_loader(
    db_conn: str,
    csv_path: Path | str,
    force_csv: bool = False,
) -> BaseLoader:
    """
    Selecteer de juiste loader op basis van beschikbaarheid.

    Strategie:
    1. Probeer SqlLoader — bij succes: gebruik SQL
    2. Bij fout of force_csv=True: gebruik CsvLoader
    3. Als ook CSV niet beschikbaar: gooi RuntimeError

    Args:
        db_conn:   SQLAlchemy connectiestring naar ZRG0014WI/Lerni_DB
        csv_path:  Pad naar de CSV-fallback map
        force_csv: Forceer CSV-loader (handig voor unit tests)

    Returns:
        SqlLoader of CsvLoader
    """
    if not force_csv:
        sql = SqlLoader(db_conn)
        if sql.is_available():
            logger.info("DataLoader: SQL-loader actief (ZRG0014WI/Lerni_DB)")
            return sql
        logger.warning("DataLoader: SQL niet bereikbaar — fallback naar CSV")

    csv = CsvLoader(Path(csv_path))
    if not csv.is_available():
        raise RuntimeError(
            f"Geen databron beschikbaar — SQL niet bereikbaar én geen CSV-bestanden in {csv_path}"
        )

    logger.info(f"DataLoader: CSV-loader actief ({csv_path})")
    return csv
