"""
CSV/Excel loader voor CSAT-data.
Gebruikt als fallback wanneer de SQL-connectie niet beschikbaar is.
Verwacht bestanden met kolomnamen conform V_CSAT_1.
"""

from pathlib import Path

import pandas as pd
from loguru import logger

from .base_loader import BaseLoader

DATE_COLUMNS = ["created", "satisfaction_date"]


class CsvLoader(BaseLoader):
    """Laadt CSAT-data vanuit CSV of Excel bestanden in de fallback-map."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def is_available(self) -> bool:
        """Controleer of de fallback-map bestaat en bestanden bevat."""
        if not self.path.exists():
            logger.warning(f"CSV-fallback map niet gevonden: {self.path}")
            return False
        files = list(self.path.glob("*.csv")) + list(self.path.glob("*.xlsx"))
        if not files:
            logger.warning(f"Geen CSV/Excel bestanden in: {self.path}")
            return False
        return True

    def load(
        self,
        pillar: str | None = None,
        period: str | None = None,
    ) -> pd.DataFrame:
        """
        Laad data vanuit het meest recente CSV of Excel bestand.

        Bestanden worden gesorteerd op naam (ISO-datumnotatie in bestandsnaam
        zorgt voor correcte chronologische volgorde).

        Args:
            pillar: Filter op product-kolom (bv. 'PHARMA') of None voor alles
            period: Filter op created-kolom in formaat 'YYYY-MM' of None voor alles

        Returns:
            Gefilterd DataFrame
        """
        csv_files = sorted(self.path.glob("*.csv"), reverse=True)
        xlsx_files = sorted(self.path.glob("*.xlsx"), reverse=True)
        all_files = list(csv_files) + list(xlsx_files)

        if not all_files:
            raise FileNotFoundError(f"Geen CSV/Excel bestanden gevonden in {self.path}")

        bestand = all_files[0]
        logger.info(f"[CsvLoader] Bestand geladen: {bestand.name}")

        if bestand.suffix == ".csv":
            df = pd.read_csv(bestand, parse_dates=DATE_COLUMNS)
        else:
            df = pd.read_excel(bestand, parse_dates=DATE_COLUMNS)

        df = self._validate_dataframe(df)

        # Filters toepassen
        if pillar:
            df = df[df["product"].str.upper() == pillar.strip().upper()]
        if period:
            df = df[df["created"].dt.to_period("M").astype(str) == period]

        return df
