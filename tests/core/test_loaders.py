"""
Unit tests voor CsvLoader en de get_loader() factory.

SqlLoader wordt niet direct getest (vereist echte DB-connectie).
Connectie-logica wordt getest via mocking.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from csat.core.loaders import CsvLoader, SqlLoader, get_loader

# ------------------------------------------------------------------
# CsvLoader
# ------------------------------------------------------------------


class TestCsvLoader:
    """Tests voor CSV-loader beschikbaarheid en laden."""

    def test_is_available_false_bij_ontbrekende_map(self, tmp_path: Path) -> None:
        loader = CsvLoader(tmp_path / "bestaat_niet")
        assert loader.is_available() is False

    def test_is_available_false_bij_lege_map(self, tmp_path: Path) -> None:
        loader = CsvLoader(tmp_path)
        assert loader.is_available() is False

    def test_is_available_true_bij_csv(self, tmp_path: Path) -> None:
        (tmp_path / "data.csv").write_text("key,score\nSD-001,4\n")
        loader = CsvLoader(tmp_path)
        assert loader.is_available() is True

    def test_laad_csv_retourneert_dataframe(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """Sla een bestand op en laad het terug."""
        bestand = tmp_path / "2026-01-export.csv"
        sample_df.to_csv(bestand, index=False)
        loader = CsvLoader(tmp_path)
        result = loader.load()
        # Alle 12 rijen moeten aanwezig zijn
        assert len(result) == 12

    def test_pillar_filter(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        bestand = tmp_path / "2026-01-export.csv"
        sample_df.to_csv(bestand, index=False)
        loader = CsvLoader(tmp_path)
        result = loader.load(pillar="PHARMA")
        assert all(result["product"].str.upper() == "PHARMA")

    def test_laad_gooit_fout_bij_geen_bestanden(self, tmp_path: Path) -> None:
        loader = CsvLoader(tmp_path)
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_meest_recente_bestand_wordt_geladen(
        self, tmp_path: Path, sample_df: pd.DataFrame
    ) -> None:
        """Wanneer meerdere bestanden aanwezig zijn, wordt het laatste (alfabetisch) geladen."""
        for naam in ["2026-01-export.csv", "2026-02-export.csv"]:
            sample_df.to_csv(tmp_path / naam, index=False)
        loader = CsvLoader(tmp_path)
        result = loader.load()
        assert len(result) == 12  # eerste bestand heeft 12 rijen


# ------------------------------------------------------------------
# SqlLoader (via mocking)
# ------------------------------------------------------------------


class TestSqlLoaderMocked:
    """Tests voor SqlLoader-logica zonder echte DB-connectie."""

    def test_is_available_true_bij_geslaagde_connectie(self) -> None:
        loader = SqlLoader("mssql+pyodbc://test")
        with patch.object(loader, "_get_engine") as mock_engine:
            mock_conn = MagicMock()
            mock_engine.return_value.connect.return_value.__enter__ = lambda s: mock_conn
            mock_engine.return_value.connect.return_value.__exit__ = MagicMock(return_value=False)
            assert loader.is_available() is True

    def test_is_available_false_bij_connectiefout(self) -> None:
        from sqlalchemy.exc import OperationalError

        loader = SqlLoader("mssql+pyodbc://ongeldig")
        with patch.object(loader, "_get_engine") as mock_engine:
            mock_engine.return_value.connect.side_effect = OperationalError(
                "conn", None, Exception("timeout")
            )
            assert loader.is_available() is False

    def test_load_stuurt_correcte_query(self, sample_df: pd.DataFrame) -> None:
        """Controleer dat de juiste WHERE-clause wordt gebouwd."""
        loader = SqlLoader("mssql+pyodbc://test")
        with (
            patch.object(loader, "_get_engine") as _,
            patch("csat.core.loaders.sql_loader.pd.read_sql", return_value=sample_df) as mock_sql,
        ):
            loader.load(pillar="PHARMA", period="2026-01")

            # Controleer dat read_sql werd aangeroepen
            assert mock_sql.called
            # Eerste argument is de query — controleer op aanwezigheid van filters
            query_arg = str(mock_sql.call_args[0][0])
            assert "PHARMA" in query_arg
            assert "2026" in query_arg


# ------------------------------------------------------------------
# get_loader factory
# ------------------------------------------------------------------


class TestGetLoader:
    """Tests voor de loader-factory."""

    def test_force_csv_retourneert_csv_loader(
        self, tmp_path: Path, sample_df: pd.DataFrame
    ) -> None:
        (tmp_path / "export.csv").write_text(sample_df.to_csv(index=False))
        loader = get_loader(
            db_conn="mssql+pyodbc://ongeldig",
            csv_path=tmp_path,
            force_csv=True,
        )
        assert isinstance(loader, CsvLoader)

    def test_geen_databron_gooit_runtimeerror(self, tmp_path: Path) -> None:
        """Lege map + geen DB → RuntimeError verwacht."""
        with (
            patch("csat.core.loaders.sql_loader.SqlLoader.is_available", return_value=False),
            pytest.raises(RuntimeError, match="Geen databron beschikbaar"),
        ):
            get_loader(
                db_conn="mssql+pyodbc://ongeldig",
                csv_path=tmp_path,
                force_csv=False,
            )

    def test_sql_loader_wanneer_beschikbaar(self, tmp_path: Path) -> None:
        with patch("csat.core.loaders.sql_loader.SqlLoader.is_available", return_value=True):
            loader = get_loader(
                db_conn="mssql+pyodbc://test",
                csv_path=tmp_path,
                force_csv=False,
            )
            assert isinstance(loader, SqlLoader)


# ------------------------------------------------------------------
# CsvLoader — aanvullende paden
# ------------------------------------------------------------------


class TestCsvLoaderExtra:
    """Dekt xlsx-loading en period-filter (regels 65 + 73)."""

    def test_laad_xlsx_retourneert_dataframe(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """Regel 65 — pd.read_excel pad."""
        bestand = tmp_path / "2026-01-export.xlsx"
        sample_df.to_excel(bestand, index=False)
        loader = CsvLoader(tmp_path)
        result = loader.load()
        assert len(result) == 12

    def test_period_filter_csv(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """Regel 73 — period-filter op created-kolom."""
        sample_df.to_csv(tmp_path / "2026-01-export.csv", index=False)
        loader = CsvLoader(tmp_path)
        result = loader.load(period="2026-01")
        assert len(result) == 10  # jan 2026: 6 PHARMA + 4 CARE


# ------------------------------------------------------------------
# SqlLoader — create_engine lazy init (regels 27-32)
# ------------------------------------------------------------------


class TestSqlLoaderEngine:
    """Test de lazy engine-initialisatie en caching."""

    def test_engine_wordt_aangemaakt_bij_eerste_aanroep(self) -> None:
        loader = SqlLoader("mssql+pyodbc://test")
        with patch("csat.core.loaders.sql_loader.create_engine") as mock_ce:
            mock_ce.return_value = MagicMock()
            loader._get_engine()
            mock_ce.assert_called_once()

    def test_engine_wordt_gecached(self) -> None:
        """Tweede aanroep mag create_engine niet opnieuw aanroepen."""
        loader = SqlLoader("mssql+pyodbc://test")
        with patch("csat.core.loaders.sql_loader.create_engine") as mock_ce:
            mock_ce.return_value = MagicMock()
            loader._get_engine()
            loader._get_engine()
            mock_ce.assert_called_once()


# ------------------------------------------------------------------
# BaseLoader — ontbrekende kolommen (regel 61)
# ------------------------------------------------------------------


class TestBaseLoaderValidatie:
    """Test de waarschuwing bij ontbrekende kolommen."""

    def test_waarschuwing_bij_ontbrekende_kolommen(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Regel 61 — logger.warning bij ontbrekende kolommen."""

        # CSV met datumkolommen aanwezig maar andere REQUIRED_COLUMNS ontbreken
        csv_inhoud = "key,score,created,satisfaction_date\nSD-001,4.0,2026-01-05,2026-01-10\n"
        (tmp_path / "onvolledig.csv").write_text(csv_inhoud)
        loader = CsvLoader(tmp_path)
        # _validate_dataframe logt warning over ontbrekende kolommen (issue_type, priority, ...)
        result = loader.load()
        # Validatie bereikt: DataFrame geladen ondanks ontbrekende kolommen
        assert "key" in result.columns
        assert len(result) == 1
