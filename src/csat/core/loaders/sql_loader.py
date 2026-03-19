"""
SQL-loader voor CSAT-data.
Verbindt rechtstreeks met [dbo].[V_CSAT_1] op ZRG0014WI via SQL Server authenticatie.
"""

import pandas as pd
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from .base_loader import BaseLoader

DATE_COLUMNS = ["created", "satisfaction_date"]


class SqlLoader(BaseLoader):
    """Laadt CSAT-data rechtstreeks vanuit de SQL Server view V_CSAT_1."""

    VIEW = "[dbo].[V_CSAT_1]"

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string
        self._engine = None

    def _get_engine(self):
        """Initialiseer de SQLAlchemy engine (lazy loading)."""
        if self._engine is None:
            self._engine = create_engine(
                self.connection_string,
                fast_executemany=True,
            )
        return self._engine

    def is_available(self) -> bool:
        """Test de connectie met de database."""
        try:
            engine = self._get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.debug("[SqlLoader] Connectie geslaagd")
            return True
        except OperationalError as fout:
            logger.warning(f"[SqlLoader] Connectie mislukt: {fout}")
            return False

    def load(
        self,
        pillar: str | None = None,
        period: str | None = None,
    ) -> pd.DataFrame:
        """
        Laad data vanuit [dbo].[V_CSAT_1].

        Args:
            pillar: Filter op product-kolom (bv. 'PHARMA') of None voor alles
            period: Filter op created-kolom in formaat 'YYYY-MM' of None voor alles

        Returns:
            DataFrame met alle kolommen van V_CSAT_1
        """
        query = f"SELECT * FROM {self.VIEW}"
        conditions = []

        if pillar:
            conditions.append(f"product = '{pillar.strip()}'")
        if period:
            jaar, maand = period.split("-")
            conditions.append(
                f"YEAR(created) = {jaar} AND MONTH(created) = {int(maand)}"
            )

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        logger.info(f"[SqlLoader] Query: {query}")

        engine = self._get_engine()
        df = pd.read_sql(
            text(query),
            engine,
            parse_dates=DATE_COLUMNS,
        )
        return self._validate_dataframe(df)

