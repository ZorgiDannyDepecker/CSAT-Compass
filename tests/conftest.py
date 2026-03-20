"""
Gedeelde pytest-fixtures voor CSAT-Compass unit tests.

Bevat een sample DataFrame dat de structuur van [dbo].[V_CSAT_1] nabootst.
"""

import pandas as pd
import pytest

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _make_row(
    key: str,
    issue_type: str,
    priority: str,
    score: float | None,
    hospital: str,
    product: str,
    created: str,
    satisfaction_date: str | None = None,
    summary: str = "Test ticket",
    comment: str = "",
    product_domain: str = "Pharma",
    project_key: str = "SD30",
) -> dict:
    """Maak één rij aan conform V_CSAT_1 kolomstructuur."""
    return {
        "key": key,
        "issue_type": issue_type,
        "priority": priority,
        "summary": summary,
        "score": score,
        "comment": comment,
        "satisfaction_date": pd.Timestamp(satisfaction_date) if satisfaction_date else pd.NaT,
        "created": pd.Timestamp(created),
        "hospital": hospital,
        "product": product,
        "product_domain": product_domain,
        "project_key": project_key,
    }


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """
    Testdataset met 12 tickets verdeeld over 3 ziekenhuizen en 2 pijlers.

    Samenstelling:
    - 8 PHARMA-tickets (jan 2026: 6, feb 2026: 2)
    - 4 CARE-tickets (jan 2026: 4)
    - Reactiegraad PHARMA jan 2026: 5/6 = 83,3% (bewust onder 85% voor threshold-test)
    - High/Critical PHARMA jan 2026: 2/6 = 33,3% (bewust boven 15%)
    - Gemiddelde score PHARMA jan 2026: (4+3+5+2+5)/5 = 3,8
    """
    rijen = [
        # PHARMA — januari 2026 — AZ Groeninge
        _make_row(
            "SD-001", "Bug", "High", 4.0, "AZ Groeninge", "PHARMA", "2026-01-05", "2026-01-10"
        ),
        _make_row(
            "SD-002", "Bug", "Critical", 3.0, "AZ Groeninge", "PHARMA", "2026-01-08", "2026-01-12"
        ),
        _make_row(
            "SD-003", "Question", "Low", 5.0, "AZ Groeninge", "PHARMA", "2026-01-10", "2026-01-14"
        ),
        # PHARMA — januari 2026 — UZ Brussel
        _make_row(
            "SD-004",
            "Improvement",
            "Medium",
            2.0,
            "UZ Brussel",
            "PHARMA",
            "2026-01-15",
            "2026-01-20",
        ),
        _make_row(
            "SD-005", "Bug", "Medium", 5.0, "UZ Brussel", "PHARMA", "2026-01-18", "2026-01-22"
        ),
        _make_row("SD-006", "Bug", "Low", None, "UZ Brussel", "PHARMA", "2026-01-20"),  # geen score
        # PHARMA — februari 2026 — AZ Groeninge
        _make_row(
            "SD-007", "Bug", "High", 4.0, "AZ Groeninge", "PHARMA", "2026-02-03", "2026-02-08"
        ),
        _make_row(
            "SD-008", "Question", "Low", 3.0, "AZ Groeninge", "PHARMA", "2026-02-10", "2026-02-14"
        ),
        # CARE — januari 2026 — OLV Aalst
        _make_row("SD-009", "Bug", "Medium", 4.0, "OLV Aalst", "CARE", "2026-01-06", "2026-01-11"),
        _make_row("SD-010", "Bug", "Low", 5.0, "OLV Aalst", "CARE", "2026-01-12", "2026-01-16"),
        _make_row(
            "SD-011", "Improvement", "Low", 3.0, "OLV Aalst", "CARE", "2026-01-19", "2026-01-23"
        ),
        _make_row("SD-012", "Bug", "High", None, "OLV Aalst", "CARE", "2026-01-25"),  # geen score
    ]
    return pd.DataFrame(rijen)


@pytest.fixture
def pharma_jan_df(sample_df: pd.DataFrame) -> pd.DataFrame:
    """Subset: alleen PHARMA-tickets uit januari 2026."""
    mask = (
        (sample_df["product"] == "PHARMA")
        & (pd.to_datetime(sample_df["created"]).dt.year == 2026)
        & (pd.to_datetime(sample_df["created"]).dt.month == 1)
    )
    return sample_df.loc[mask].copy()


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """Leeg DataFrame met correcte kolomstructuur (randgeval tests)."""
    kolommen = [
        "key",
        "issue_type",
        "priority",
        "summary",
        "score",
        "comment",
        "satisfaction_date",
        "created",
        "hospital",
        "product",
        "product_domain",
        "project_key",
    ]
    df = pd.DataFrame(columns=kolommen)
    df["created"] = pd.to_datetime(df["created"])
    df["satisfaction_date"] = pd.to_datetime(df["satisfaction_date"])
    return df
