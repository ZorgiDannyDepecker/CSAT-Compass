"""
Unit tests voor src/csat/utils/date_utils.py.
"""

import re
from pathlib import Path

import pandas as pd
import pytest

from csat.utils.date_utils import (
    dated_output_dir,
    filter_period,
    filter_year,
    filter_ytd,
    parse_period,
    period_label,
    previous_period,
    timestamped_output_dir,
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


# ------------------------------------------------------------------
# timestamped_output_dir
# ------------------------------------------------------------------


class TestTimestampedOutputDir:
    """Tests voor de timestamped submap-helper."""

    @pytest.mark.unit
    def test_maakt_submap_aan(self, tmp_path: Path) -> None:
        """Submap wordt aangemaakt als ze nog niet bestaat."""
        result = timestamped_output_dir(tmp_path)
        assert result.exists()
        assert result.is_dir()

    @pytest.mark.unit
    def test_submap_is_kind_van_base_path(self, tmp_path: Path) -> None:
        """Submap ligt direct onder de opgegeven basismap."""
        result = timestamped_output_dir(tmp_path)
        assert result.parent == tmp_path

    @pytest.mark.unit
    def test_submapnaam_formaat(self, tmp_path: Path) -> None:
        """Submapnaam voldoet aan patroon YYYY-MM-DD_HHMM."""
        result = timestamped_output_dir(tmp_path)
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{4}", result.name)

    @pytest.mark.unit
    def test_idempotent_bij_bestaande_map(self, tmp_path: Path) -> None:
        """Twee aanroepen met dezelfde minuut geven dezelfde map terug zonder fout."""
        result1 = timestamped_output_dir(tmp_path)
        result2 = (
            timestamped_output_dir.__wrapped__(tmp_path)
            if hasattr(timestamped_output_dir, "__wrapped__")
            else timestamped_output_dir(tmp_path)
        )
        # Beide paden bestaan — geen FileExistsError
        assert result1.exists()
        assert result2.exists()


# ------------------------------------------------------------------
# dated_output_dir
# ------------------------------------------------------------------


class TestDatedOutputDir:
    """Tests voor de datum-submap-helper (YYYY-MM-DD formaat)."""

    @pytest.mark.unit
    def test_maakt_submap_aan(self, tmp_path: Path) -> None:
        """Submap wordt aangemaakt als ze nog niet bestaat."""
        result = dated_output_dir(tmp_path)
        assert result.exists()
        assert result.is_dir()

    @pytest.mark.unit
    def test_submap_is_kind_van_base_path(self, tmp_path: Path) -> None:
        """Submap ligt direct onder de opgegeven basismap."""
        result = dated_output_dir(tmp_path)
        assert result.parent == tmp_path

    @pytest.mark.unit
    def test_submapnaam_formaat_datum(self, tmp_path: Path) -> None:
        """Submapnaam voldoet aan patroon YYYY-MM-DD (enkel datum, geen tijd)."""
        result = dated_output_dir(tmp_path)
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", result.name)

    @pytest.mark.unit
    def test_geen_tijdstempel_in_naam(self, tmp_path: Path) -> None:
        """Submapnaam bevat geen uur/minuut — enkel datum."""
        result = dated_output_dir(tmp_path)
        assert "_" not in result.name

    @pytest.mark.unit
    def test_idempotent(self, tmp_path: Path) -> None:
        """Twee aanroepen op dezelfde dag geven hetzelfde pad zonder fout."""
        result1 = dated_output_dir(tmp_path)
        result2 = dated_output_dir(tmp_path)
        assert result1 == result2
        assert result1.exists()


# ------------------------------------------------------------------
# parse_period — extra randgevallen
# ------------------------------------------------------------------


class TestParsePeriodExtra:
    """Extra randgevallen voor parse_period."""

    def test_nulpadding_maand(self) -> None:
        """Maand zonder nulpadding wordt correct geparseerd."""
        result = parse_period("2026-3")
        assert result == (2026, 3)

    def test_maand_nul_raises(self) -> None:
        """Maand 0 is ongeldig."""
        with pytest.raises(ValueError):
            parse_period("2026-00")

    def test_negatieve_maand_raises(self) -> None:
        """Negatieve maand is ongeldig."""
        with pytest.raises(ValueError):
            parse_period("2026--1")

    def test_alleen_jaar_raises(self) -> None:
        """Enkel jaargetal zonder maand raises ValueError."""
        with pytest.raises(ValueError):
            parse_period("2026")

    def test_te_veel_delen_raises(self) -> None:
        """Drie delen raises ValueError."""
        with pytest.raises(ValueError):
            parse_period("2026-03-01")

    def test_geen_string_raises(self) -> None:
        """None of niet-string input raises ValueError."""
        with pytest.raises((ValueError, AttributeError)):
            parse_period(None)  # type: ignore[arg-type]


# ------------------------------------------------------------------
# period_label — alle 12 maanden + taalfallback
# ------------------------------------------------------------------


class TestPeriodLabelVolledig:
    """Volledige maandnamen NL + FR voor alle 12 maanden."""

    @pytest.mark.parametrize(
        "maand_nr, verwacht_nl, verwacht_fr",
        [
            (1, "Januari", "Janvier"),
            (2, "Februari", "Février"),
            (3, "Maart", "Mars"),
            (4, "April", "Avril"),
            (5, "Mei", "Mai"),
            (6, "Juni", "Juin"),
            (7, "Juli", "Juillet"),
            (8, "Augustus", "Août"),
            (9, "September", "Septembre"),
            (10, "Oktober", "Octobre"),
            (11, "November", "Novembre"),
            (12, "December", "Décembre"),
        ],
    )
    def test_alle_maanden_nl_fr(self, maand_nr: int, verwacht_nl: str, verwacht_fr: str) -> None:
        """Elke maand geeft het correcte NL- én FR-label."""
        periode = f"2026-{maand_nr:02d}"
        assert period_label(periode, lang="nl") == f"{verwacht_nl} 2026"
        assert period_label(periode, lang="fr") == f"{verwacht_fr} 2026"

    def test_onbekende_taal_valt_terug_op_fr(self) -> None:
        """Een onbekende taalcode valt terug op Frans (geen crash)."""
        result = period_label("2026-03", lang="de")
        assert "2026" in result
        assert isinstance(result, str)


# ------------------------------------------------------------------
# previous_period — extra gevallen
# ------------------------------------------------------------------


class TestPreviousPeriodExtra:
    """Extra randgevallen voor previous_period."""

    def test_alle_maanden_no_jaarovergangen(self) -> None:
        """Maanden 2 t/m 12 blijven in hetzelfde jaar."""
        for m in range(2, 13):
            periode = f"2026-{m:02d}"
            result = previous_period(periode)
            jaar, maand = parse_period(result)
            assert maand == m - 1
            assert jaar == 2026

    def test_jaarovergang_terug(self) -> None:
        """Januari 2026 → December 2025."""
        assert previous_period("2026-01") == "2025-12"

    def test_jaar_2000_overgang(self) -> None:
        """Januari 2000 → December 1999."""
        assert previous_period("2000-01") == "1999-12"

    def test_nulpadding_resultaat(self) -> None:
        """Resultaat heeft altijd 2 cijfers voor de maand."""
        result = previous_period("2026-10")
        assert result == "2026-09"
        result2 = previous_period("2026-03")
        assert result2 == "2026-02"


# ------------------------------------------------------------------
# filter_period / filter_year / filter_ytd — custom date_col
# ------------------------------------------------------------------


@pytest.fixture
def df_custom_col(sample_df: pd.DataFrame) -> pd.DataFrame:
    """Sample DataFrame met 'satisfaction_date' als primaire datumkolom."""
    return sample_df.copy()


class TestFilterCustomCol:
    """Tests voor filtering met een aangepaste datumkolom."""

    def test_filter_period_custom_col(self, df_custom_col: pd.DataFrame) -> None:
        """filter_period werkt correct met satisfaction_date als kolom."""
        result = filter_period(df_custom_col, "2026-01", date_col="satisfaction_date")
        # satisfaction_date januari 2026: SD-001 t/m SD-005 + SD-009 t/m SD-011
        assert len(result) > 0
        daten = pd.to_datetime(result["satisfaction_date"])
        assert all(daten.dt.year == 2026)
        assert all(daten.dt.month == 1)

    def test_filter_year_custom_col(self, df_custom_col: pd.DataFrame) -> None:
        """filter_year werkt correct met satisfaction_date als kolom."""
        result = filter_year(df_custom_col, 2026, date_col="satisfaction_date")
        assert len(result) > 0
        daten = pd.to_datetime(result["satisfaction_date"].dropna())
        assert all(daten.dt.year == 2026)

    def test_filter_ytd_custom_col(self, df_custom_col: pd.DataFrame) -> None:
        """filter_ytd werkt correct met satisfaction_date als kolom."""
        result = filter_ytd(df_custom_col, 2026, 2, date_col="satisfaction_date")
        assert len(result) > 0
        daten = pd.to_datetime(result["satisfaction_date"].dropna())
        assert all(daten.dt.year == 2026)
        assert all(daten.dt.month <= 2)


# ------------------------------------------------------------------
# filter_ytd — grensgevallen
# ------------------------------------------------------------------


class TestFilterYtdGrenzen:
    """Grensgevallen voor filter_ytd."""

    def test_maand_1_boundary(self, sample_df: pd.DataFrame) -> None:
        """up_to_month=1 is de ondergrens — mag niet raisen."""
        result = filter_ytd(sample_df, 2026, 1)
        assert isinstance(result, pd.DataFrame)

    def test_maand_12_boundary(self, sample_df: pd.DataFrame) -> None:
        """up_to_month=12 is de bovengrens — mag niet raisen."""
        result = filter_ytd(sample_df, 2026, 12)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(filter_year(sample_df, 2026))

    def test_maand_0_raises(self, sample_df: pd.DataFrame) -> None:
        """up_to_month=0 is ongeldig."""
        with pytest.raises(ValueError, match="up_to_month"):
            filter_ytd(sample_df, 2026, 0)

    def test_maand_13_raises(self, sample_df: pd.DataFrame) -> None:
        """up_to_month=13 is ongeldig."""
        with pytest.raises(ValueError, match="up_to_month"):
            filter_ytd(sample_df, 2026, 13)

    def test_kopie_onafhankelijk(self, sample_df: pd.DataFrame) -> None:
        """Wijziging aan resultaat raakt origineel niet."""
        result = filter_ytd(sample_df, 2026, 12)
        original_score = sample_df["score"].iloc[0]
        result["score"] = -1.0
        assert sample_df["score"].iloc[0] == original_score


# ------------------------------------------------------------------
# filter_year — grensgevallen
# ------------------------------------------------------------------


class TestFilterYearExtra:
    """Extra gedragsgevallen voor filter_year."""

    def test_retourneert_kopie(self, sample_df: pd.DataFrame) -> None:
        """Wijziging aan resultaat raakt origineel sample_df niet."""
        result = filter_year(sample_df, 2026)
        original_score = sample_df["score"].iloc[0]
        result["score"] = -99.0
        assert sample_df["score"].iloc[0] == original_score

    def test_geen_dubbele_rijen(self, sample_df: pd.DataFrame) -> None:
        """filter_year geeft geen duplicaten terug."""
        result = filter_year(sample_df, 2026)
        assert result.duplicated(subset=["key"]).sum() == 0


# ------------------------------------------------------------------
# today_period — uitgebreider
# ------------------------------------------------------------------


class TestTodayPeriodExtra:
    """Extra gedragsgevallen voor today_period."""

    def test_parse_retourneert_huidig_jaar(self) -> None:
        """Het jaar van today_period is het actuele kalenderjaar."""
        import datetime

        result = today_period()
        jaar, _ = parse_period(result)
        assert jaar == datetime.date.today().year  # noqa: DTZ011

    def test_formaat_is_yyyy_mm(self) -> None:
        """today_period retourneert altijd YYYY-MM met nulpadding."""
        result = today_period()
        assert re.fullmatch(r"\d{4}-\d{2}", result)
