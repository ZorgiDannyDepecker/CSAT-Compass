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
    Selecteer de juiste loader op basis van beschikbaarheid en data-aanwezigheid.

    Strategie:
    1. force_csv=True  → direct naar CsvLoader, SQL wordt niet geprobeerd
    2. SQL bereikbaar + data aanwezig (>0 rijen) → SqlLoader
    3. SQL bereikbaar maar 0 rijen → waarschuwing + fallback naar CsvLoader
    4. SQL niet bereikbaar of load-fout → waarschuwing + fallback naar CsvLoader
    5. CSV ook niet beschikbaar → RuntimeError

    De testlading in stap 2/3 is acceptabel: V_CSAT_1 is klein (<10.000 rijen).

    Args:
        db_conn:   SQLAlchemy connectiestring naar ZRG0014WI/Lerni_DB
        csv_path:  Pad naar de CSV-fallback map
        force_csv: Forceer CSV-loader (omzeilt SQL — voor onderhoud of reproduceerbare runs)

    Returns:
        SqlLoader of CsvLoader

    Raises:
        RuntimeError: Als geen enkele databron beschikbaar of niet-leeg is
    """
    if not force_csv:
        sql = SqlLoader(db_conn)
        if sql.is_available():
            try:
                test_df = sql.load()
                if len(test_df) > 0:
                    logger.info("DataLoader: SQL-loader actief (ZRG0014WI/Lerni_DB)")
                    return sql
                logger.warning(
                    "DataLoader: SQL bereikbaar maar V_CSAT_1 geeft 0 rijen — "
                    "fallback naar CSV (mogelijke DB-storing of onderhoud)"
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"DataLoader: SQL-lading mislukt ({exc}) — fallback naar CSV")
        else:
            logger.warning("DataLoader: SQL niet bereikbaar — fallback naar CSV")

    csv = CsvLoader(Path(csv_path))
    if not csv.is_available():
        raise RuntimeError(
            f"Geen databron beschikbaar — SQL niet bereikbaar of leeg "
            f"én geen CSV-bestanden in {csv_path}"
        )

    logger.info(f"DataLoader: CSV-loader actief ({csv_path})")
    return csv
