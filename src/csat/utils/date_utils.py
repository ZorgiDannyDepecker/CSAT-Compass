"""
Hulpfuncties voor datumverwerking en periode-filtering in CSAT-Compass.

Periodestrings worden altijd in het formaat 'YYYY-MM' verwacht en teruggegeven.
"""

from datetime import date

import pandas as pd


def parse_period(period: str) -> tuple[int, int]:
    """
    Parseer een periode-string naar (jaar, maand).

    Args:
        period: Periodestring in formaat 'YYYY-MM'

    Returns:
        Tuple (jaar, maand) als integers

    Raises:
        ValueError: Als het formaat niet klopt of waarden buiten bereik vallen
    """
    try:
        parts = period.strip().split("-")
        if len(parts) != 2:
            raise ValueError
        jaar, maand = int(parts[0]), int(parts[1])
        if not (1 <= maand <= 12):
            raise ValueError(f"Maandwaarde buiten bereik: {maand}")
        return jaar, maand
    except (AttributeError, ValueError) as exc:
        raise ValueError(
            f"Ongeldige periodestring: '{period}' — verwacht formaat 'YYYY-MM'"
        ) from exc


def filter_period(
    df: pd.DataFrame,
    period: str,
    date_col: str = "created",
) -> pd.DataFrame:
    """
    Filter een DataFrame op een specifieke maand.

    Args:
        df: DataFrame met een datumkolom
        period: Periodestring 'YYYY-MM'
        date_col: Naam van de datumkolom (standaard 'created')

    Returns:
        Gefilterd DataFrame (kopie)
    """
    jaar, maand = parse_period(period)
    col = pd.to_datetime(df[date_col])
    mask = (col.dt.year == jaar) & (col.dt.month == maand)
    return df.loc[mask].copy()


def filter_year(
    df: pd.DataFrame,
    year: int,
    date_col: str = "created",
) -> pd.DataFrame:
    """
    Filter een DataFrame op een volledig jaar.

    Args:
        df: DataFrame met een datumkolom
        year: Het doeljaar
        date_col: Naam van de datumkolom

    Returns:
        Gefilterd DataFrame (kopie)
    """
    col = pd.to_datetime(df[date_col])
    mask = col.dt.year == year
    return df.loc[mask].copy()


def filter_ytd(
    df: pd.DataFrame,
    year: int,
    up_to_month: int,
    date_col: str = "created",
) -> pd.DataFrame:
    """
    Filter op year-to-date: januari t/m up_to_month van het opgegeven jaar.

    Args:
        df: DataFrame met een datumkolom
        year: Het doeljaar
        up_to_month: Einmaand (inclusief), 1-12
        date_col: Naam van de datumkolom

    Returns:
        Gefilterd DataFrame (kopie)
    """
    if not (1 <= up_to_month <= 12):
        raise ValueError(f"up_to_month moet tussen 1 en 12 liggen, niet {up_to_month}")
    col = pd.to_datetime(df[date_col])
    mask = (col.dt.year == year) & (col.dt.month <= up_to_month)
    return df.loc[mask].copy()


def previous_period(period: str) -> str:
    """
    Geef de vorige maand terug als 'YYYY-MM' string.

    Args:
        period: Huidige periode 'YYYY-MM'

    Returns:
        Vorige maand als 'YYYY-MM' (bv. '2026-01' → '2025-12')
    """
    jaar, maand = parse_period(period)
    if maand == 1:
        return f"{jaar - 1}-12"
    return f"{jaar}-{maand - 1:02d}"


def period_label(period: str, lang: str = "nl") -> str:
    """
    Geef een leesbaar label voor een periode.

    Args:
        period: Periodestring 'YYYY-MM'
        lang: Taal 'nl' of 'fr'

    Returns:
        Leesbaar label (bv. 'Januari 2026' of 'Janvier 2026')
    """
    MAANDEN_NL = [  # noqa: N806
        "Januari",
        "Februari",
        "Maart",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Augustus",
        "September",
        "Oktober",
        "November",
        "December",
    ]
    MOIS_FR = [  # noqa: N806
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]
    jaar, maand = parse_period(period)
    namen = MAANDEN_NL if lang == "nl" else MOIS_FR
    return f"{namen[maand - 1]} {jaar}"


def today_period() -> str:
    """Geef de huidige maand terug als 'YYYY-MM' string."""
    today = date.today()  # noqa: DTZ011
    return f"{today.year}-{today.month:02d}"
