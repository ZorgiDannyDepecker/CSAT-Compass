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

        Bestanden worden gesorteerd op wijzigingsdatum (mtime) zodat altijd
        de meest recente snapshot gebruikt wordt, ongeacht de bestandsnaam.

        Args:
            pillar: Filter op product_domain-kolom (bv. 'PHARMA') of None voor alles
            period: Filter op created-kolom in formaat 'YYYY-MM' of None voor alles

        Returns:
            Gefilterd DataFrame
        """
        all_files = sorted(
            list(self.path.glob("*.csv")) + list(self.path.glob("*.xlsx")),
            key=lambda f: f.stat().st_mtime,
            reverse=True,  # meest recent eerst
        )

        if not all_files:
            raise FileNotFoundError(f"Geen CSV/Excel bestanden gevonden in {self.path}")

        bestand = all_files[0]
        from datetime import datetime  # noqa: PLC0415

        mtime = (
            datetime.fromtimestamp(bestand.stat().st_mtime).astimezone().strftime("%Y-%m-%d %H:%M")
        )
        logger.info(f"[CsvLoader] Bestand geladen: {bestand.name} (gewijzigd: {mtime})")

        if bestand.suffix == ".csv":
            df = pd.read_csv(
                bestand,
                sep=";",
                encoding="utf-8-sig",
                parse_dates=["created"],
            )
        else:
            df = pd.read_excel(bestand, parse_dates=["created"])

        # satisfaction_date apart parsen met dayfirst=True — Belgisch formaat DD/MM/YYYY HH:MM
        if "satisfaction_date" in df.columns:
            df["satisfaction_date"] = pd.to_datetime(
                df["satisfaction_date"], format="mixed", dayfirst=True, errors="coerce"
            )

        df = self._validate_dataframe(df)

        # Filters toepassen
        if pillar:
            df = df[df["product_domain"].str.upper() == pillar.strip().upper()]
        if period:
            df = df[df["created"].dt.to_period("M").astype(str) == period]

        return df
