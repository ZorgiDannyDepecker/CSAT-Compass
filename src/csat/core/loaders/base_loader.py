"""
Abstracte basisklasse voor alle CSAT-data loaders.
Definieert de gemeenschappelijke interface voor SQL- en CSV-loaders.
"""

from abc import ABC, abstractmethod

import pandas as pd
from loguru import logger

# Verplichte kolomnamen vanuit V_CSAT_1
REQUIRED_COLUMNS = [
    "key", "issue_type", "priority", "summary", "score",
    "comment", "satisfaction_date", "created",
    "hospital", "product", "product_domain", "project_key",
]


class BaseLoader(ABC):
    """Abstracte loader — elke concrete loader implementeert load() en is_available()."""

    @abstractmethod
    def load(
        self,
        pillar: str | None = None,
        period: str | None = None,
    ) -> pd.DataFrame:
        """
        Laad CSAT-data in een pandas DataFrame.

        Args:
            pillar: Pijlerfilter op product-kolom (bv. 'PHARMA') of None voor alles
            period: Periodefilter in formaat 'YYYY-MM' op created-kolom of None voor alles

        Returns:
            DataFrame met kolomnamen conform V_CSAT_1
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Controleer of de databron bereikbaar is."""
        pass

    def _validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Basisvalidatie van het geladen DataFrame.
        Logt een waarschuwing bij ontbrekende kolommen.
        """
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            logger.warning(f"Ontbrekende kolommen in DataFrame: {missing}")
        logger.info(
            f"[{self.__class__.__name__}] {len(df):,} rijen geladen "
            f"({len(df.columns)} kolommen)"
        )
        return df

