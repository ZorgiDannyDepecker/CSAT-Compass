"""
Gedeelde pytest-fixtures voor CSAT-Compass unit tests.

Bevat een sample DataFrame dat de structuur van [dbo].[V_CSAT_1] nabootst.
Filterkolom voor pijlers: product_domain (bevestigd 20/03/2026)
"""

import pandas as pd
import pytest


def _make_row(
    key: str,
    issue_type: str,
    priority: str,
    score: float | None,
    hospital: str,
    product: str,
    product_domain: str,
    created: str,
    satisfaction_date: str | None = None,
    summary: str = "Test ticket",
    comment: str = "",
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


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """
    Testdataset met 12 tickets verdeeld over 3 ziekenhuizen en 2 pijlers.

    Filterkolom: product_domain (bevestigd 20/03/2026)
    - 8 PHARMA-tickets (product_domain='PHARMA', jan 2026: 6, feb 2026: 2)
    - 4 CARE-tickets  (product_domain='CARE',   jan 2026: 4)
    - Blocker/Critical/Major PHARMA jan 2026: 2/6 = 33,3% (bewust boven 15%)
    - Gemiddelde score PHARMA jan 2026: (4+3+5+2+5)/5 = 3,8
    - SD-006 en SD-012 hebben geen score (randgeval test)
    """
    rijen = [
        # PHARMA — januari 2026 — AZ Groeninge
        _make_row(
            "SD-001",
            "Bug",
            "Blocker",
            4.0,
            "AZ Groeninge",
            "Apotheek",
            "PHARMA",
            "2026-01-05",
            "2026-01-10",
        ),
        _make_row(
            "SD-002",
            "Bug",
            "Critical",
            3.0,
            "AZ Groeninge",
            "Apotheek",
            "PHARMA",
            "2026-01-08",
            "2026-01-12",
        ),
        _make_row(
            "SD-003",
            "Question",
            "Trivial",
            5.0,
            "AZ Groeninge",
            "Apotheek",
            "PHARMA",
            "2026-01-10",
            "2026-01-14",
        ),
        # PHARMA — januari 2026 — UZ Brussel
        _make_row(
            "SD-004",
            "Improvement",
            "Minor",
            2.0,
            "UZ Brussel",
            "Apotheek",
            "PHARMA",
            "2026-01-15",
            "2026-01-20",
        ),
        _make_row(
            "SD-005",
            "Bug",
            "Minor",
            5.0,
            "UZ Brussel",
            "Apotheek",
            "PHARMA",
            "2026-01-18",
            "2026-01-22",
        ),
        _make_row(
            "SD-006", "Bug", "Trivial", None, "UZ Brussel", "Apotheek", "PHARMA", "2026-01-20"
        ),
        # PHARMA — februari 2026 — AZ Groeninge
        _make_row(
            "SD-007",
            "Bug",
            "Major",
            4.0,
            "AZ Groeninge",
            "Apotheek",
            "PHARMA",
            "2026-02-03",
            "2026-02-08",
        ),
        _make_row(
            "SD-008",
            "Question",
            "Trivial",
            3.0,
            "AZ Groeninge",
            "Apotheek",
            "PHARMA",
            "2026-02-10",
            "2026-02-14",
        ),
        # CARE — januari 2026 — OLV Aalst
        _make_row(
            "SD-009",
            "Bug",
            "Minor",
            4.0,
            "OLV Aalst",
            "ZORGI CARE",
            "CARE",
            "2026-01-06",
            "2026-01-11",
        ),
        _make_row(
            "SD-010",
            "Bug",
            "Trivial",
            5.0,
            "OLV Aalst",
            "ZORGI CARE",
            "CARE",
            "2026-01-12",
            "2026-01-16",
        ),
        _make_row(
            "SD-011",
            "Improvement",
            "Trivial",
            3.0,
            "OLV Aalst",
            "ZORGI CARE",
            "CARE",
            "2026-01-19",
            "2026-01-23",
        ),
        _make_row("SD-012", "Bug", "Major", None, "OLV Aalst", "ZORGI CARE", "CARE", "2026-01-25"),
    ]
    return pd.DataFrame(rijen)


@pytest.fixture
def pharma_jan_df(sample_df: pd.DataFrame) -> pd.DataFrame:
    """Subset: alleen PHARMA-tickets (product_domain='PHARMA') uit januari 2026."""
    mask = (
        (sample_df["product_domain"] == "PHARMA")
        & (pd.to_datetime(sample_df["created"]).dt.year == 2026)
        & (pd.to_datetime(sample_df["created"]).dt.month == 1)
    )
    return sample_df.loc[mask].copy()


@pytest.fixture
def evolution_df() -> pd.DataFrame:
    """
    Testdataset voor EvolutionAnalyser — bevat baseline (2025) + current (2026) data.

    PHARMA-pijler, 3 ziekenhuizen: AZ Groeninge, UZ Brussel, OLV Aalst.
    OLV Aalst verdwijnt in de current-periode (hospital_disappeared).

    Verwachte waarden bij baseline=["2025-06","2025-07"], current=["2026-01","2026-02"]:
    - Baseline: 6 tickets, 5 gescoord, avg=2,80, pct_pos=20,0%, pct_neg=40,0%
    - Current:  4 tickets, 4 gescoord, avg=4,50, pct_pos=100,0%, pct_neg=0,0%
    - Delta:    +1,70
    - Baseline HC (Blocker/Critical/Major): 3/6 = 50,0%
    - Current HC: 0/4 = 0,0%
    - Baseline responstijd: (15+15+13+9+10)/5 = 12,4 d
    - Current responstijd:  (1+2+2+2)/4 = 1,75 → 1,8 d
    - Thema's: responstijd (EB-001) + onvolledig (EB-003) → beide OPGELOST in current
    """
    rijen = [
        # 2025-06 — AZ Groeninge (lage scores, keywords voor thema-detectie)
        _make_row(
            "EB-001",
            "Bug",
            "Blocker",
            2.0,
            "AZ Groeninge",
            "Apotheek",
            "PHARMA",
            "2025-06-05",
            "2025-06-20",
            comment="te lang gewacht",
        ),
        _make_row(
            "EB-002",
            "Bug",
            "Critical",
            3.0,
            "AZ Groeninge",
            "Apotheek",
            "PHARMA",
            "2025-06-10",
            "2025-06-25",
        ),
        # 2025-06 — UZ Brussel
        _make_row(
            "EB-003",
            "Question",
            "Trivial",
            2.0,
            "UZ Brussel",
            "Apotheek",
            "PHARMA",
            "2025-06-15",
            "2025-06-28",
            comment="nog steeds niet opgelost",
        ),
        # 2025-07 — UZ Brussel + OLV Aalst
        _make_row(
            "EB-004",
            "Bug",
            "Major",
            4.0,
            "UZ Brussel",
            "Apotheek",
            "PHARMA",
            "2025-07-01",
            "2025-07-10",
        ),
        _make_row(
            "EB-005",
            "Improvement",
            "Minor",
            3.0,
            "OLV Aalst",
            "Apotheek",
            "PHARMA",
            "2025-07-05",
            "2025-07-15",
        ),
        _make_row(
            "EB-006",
            "Bug",
            "Minor",
            None,
            "OLV Aalst",
            "Apotheek",
            "PHARMA",
            "2025-07-08",
        ),
        # 2026-01 — AZ Groeninge (hoge scores)
        _make_row(
            "EC-001",
            "Bug",
            "Trivial",
            5.0,
            "AZ Groeninge",
            "Apotheek",
            "PHARMA",
            "2026-01-05",
            "2026-01-06",
        ),
        _make_row(
            "EC-002",
            "Question",
            "Minor",
            4.0,
            "AZ Groeninge",
            "Apotheek",
            "PHARMA",
            "2026-01-10",
            "2026-01-12",
        ),
        # 2026-02 — UZ Brussel (hoge scores)
        _make_row(
            "EC-003",
            "Bug",
            "Trivial",
            5.0,
            "UZ Brussel",
            "Apotheek",
            "PHARMA",
            "2026-02-05",
            "2026-02-07",
        ),
        _make_row(
            "EC-004",
            "Improvement",
            "Trivial",
            4.0,
            "UZ Brussel",
            "Apotheek",
            "PHARMA",
            "2026-02-10",
            "2026-02-12",
        ),
    ]
    return pd.DataFrame(rijen)


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
