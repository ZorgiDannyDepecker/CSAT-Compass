"""
Unit tests voor src/csat/utils/date_utils.py.
"""

import pandas as pd
import pytest

from csat.utils.date_utils import (
    filter_period,
    filter_year,
    filter_ytd,
    parse_period,
    period_label,
    previous_period,
    today_period,
)

# ------------------------------------------------------------------
# parse_period
# ------------------------------------------------------------------


class TestParsePeriod:
    """Tests voor periodestring-parsing."""

    def test_geldig_formaat(self) -> None:
        assert parse_period("2026-03") == (2026, 3)

    def test_geldig_formaat_januari(self) -> None:
        assert parse_period("2025-01") == (2025, 1)

    def test_geldig_formaat_december(self) -> None:
        assert parse_period("2025-12") == (2025, 12)

    def test_spaties_worden_genegeerd(self) -> None:
        assert parse_period("  2026-03  ") == (2026, 3)

    def test_ongeldig_formaat_raises(self) -> None:
        with pytest.raises(ValueError, match="Ongeldige periodestring"):
            parse_period("2026/03")

    def test_maand_buiten_bereik_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_period("2026-13")

    def test_te_weinig_delen_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_period("202603")

    def test_leeg_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_period("")


# ------------------------------------------------------------------
# previous_period
# ------------------------------------------------------------------


class TestPreviousPeriod:
    """Tests voor MoM-vorige maand berekening."""

    def test_normale_maand(self) -> None:
        assert previous_period("2026-03") == "2026-02"

    def test_overgang_jaar(self) -> None:
        assert previous_period("2026-01") == "2025-12"

    def test_december(self) -> None:
        assert previous_period("2026-12") == "2026-11"

    def test_nulpadding(self) -> None:
        assert previous_period("2026-10") == "2026-09"


# ------------------------------------------------------------------
# period_label
# ------------------------------------------------------------------


class TestPeriodLabel:
    """Tests voor leesbare periodeweergave."""

    def test_nl_maart(self) -> None:
        assert period_label("2026-03", lang="nl") == "Maart 2026"

    def test_nl_januari(self) -> None:
        assert period_label("2026-01", lang="nl") == "Januari 2026"

    def test_fr_mars(self) -> None:
        assert period_label("2026-03", lang="fr") == "Mars 2026"

    def test_fr_aout(self) -> None:
        assert period_label("2026-08", lang="fr") == "Août 2026"

    def test_december(self) -> None:
        assert period_label("2026-12", lang="nl") == "December 2026"


# ------------------------------------------------------------------
# filter_period
# ------------------------------------------------------------------


class TestFilterPeriod:
    """Tests voor maandfiltering."""

    def test_filtert_correct_op_periode(self, sample_df: pd.DataFrame) -> None:
        result = filter_period(sample_df, "2026-01")
        # jan 2026: SD-001 t/m SD-006 (PHARMA) + SD-009 t/m SD-012 (CARE) = 10 rijen
        assert len(result) == 10

    def test_leeg_bij_onbekende_periode(self, sample_df: pd.DataFrame) -> None:
        result = filter_period(sample_df, "2020-01")
        assert result.empty

    def test_retourneert_kopie(self, sample_df: pd.DataFrame) -> None:
        result = filter_period(sample_df, "2026-01")
        result["score"] = 99.0
        assert sample_df.loc[sample_df["key"] == "SD-001", "score"].values[0] != 99.0

    def test_februari(self, sample_df: pd.DataFrame) -> None:
        result = filter_period(sample_df, "2026-02")
        assert len(result) == 2
        assert set(result["key"]) == {"SD-007", "SD-008"}


# ------------------------------------------------------------------
# filter_year
# ------------------------------------------------------------------


class TestFilterYear:
    """Tests voor jaarfiltering."""

    def test_filtert_op_jaar(self, sample_df: pd.DataFrame) -> None:
        result = filter_year(sample_df, 2026)
        assert len(result) == 12  # alle rijen zijn 2026

    def test_leeg_bij_onbekend_jaar(self, sample_df: pd.DataFrame) -> None:
        result = filter_year(sample_df, 2020)
        assert result.empty


# ------------------------------------------------------------------
# filter_ytd
# ------------------------------------------------------------------


class TestFilterYtd:
    """Tests voor year-to-date filtering."""

    def test_ytd_jan(self, sample_df: pd.DataFrame) -> None:
        result = filter_ytd(sample_df, 2026, 1)
        assert len(result) == 10  # alleen januari

    def test_ytd_feb(self, sample_df: pd.DataFrame) -> None:
        result = filter_ytd(sample_df, 2026, 2)
        assert len(result) == 12  # jan + feb = alle rijen

    def test_ongeldige_maand_raises(self, sample_df: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="up_to_month"):
            filter_ytd(sample_df, 2026, 13)

    def test_retourneert_kopie(self, sample_df: pd.DataFrame) -> None:
        result = filter_ytd(sample_df, 2026, 1)
        result["score"] = 0.0
        assert sample_df["score"].iloc[0] != 0.0


# ------------------------------------------------------------------
# today_period
# ------------------------------------------------------------------


class TestTodayPeriod:
    """Tests voor huidig-maand helper."""

    def test_retourneert_geldig_formaat(self) -> None:
        result = today_period()
        jaar, maand = parse_period(result)
        assert 2020 <= jaar <= 2100
        assert 1 <= maand <= 12
