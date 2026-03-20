"""
Unit tests voor src/csat/config/settings.py.
Importeren van de module dekt alle module-level regels.
"""

from unittest.mock import patch

import csat.config.settings as settings

# ------------------------------------------------------------------
# Module-level constanten
# ------------------------------------------------------------------


class TestSettingsDefaults:
    """Controleer dat standaardwaarden correct worden ingeladen."""

    def test_db_server_default(self) -> None:
        assert settings.DB_SERVER == "ZRG0014WI"

    def test_db_name_default(self) -> None:
        assert settings.DB_NAME == "Lerni_DB"

    def test_db_schema_default(self) -> None:
        assert settings.DB_SCHEMA == "dbo"

    def test_db_view_default(self) -> None:
        assert settings.DB_VIEW == "V_CSAT_1"

    def test_db_user_default(self) -> None:
        assert settings.DB_USER == "csat_user"

    def test_db_driver_bevat_odbc(self) -> None:
        assert "ODBC" in settings.DB_DRIVER

    def test_log_level_default(self) -> None:
        assert settings.LOG_LEVEL == "INFO"

    def test_db_conn_bevat_server(self) -> None:
        assert "ZRG0014WI" in settings.DB_CONN

    def test_db_conn_bevat_driver(self) -> None:
        assert "pyodbc" in settings.DB_CONN

    def test_db_conn_bevat_trustservercertificate(self) -> None:
        assert "TrustServerCertificate=yes" in settings.DB_CONN

    def test_csv_fallback_path_is_path(self) -> None:
        from pathlib import Path

        assert isinstance(settings.CSV_FALLBACK_PATH, Path)

    def test_output_path_is_path(self) -> None:
        from pathlib import Path

        assert isinstance(settings.OUTPUT_PATH, Path)

    def test_log_path_is_path(self) -> None:
        from pathlib import Path

        assert isinstance(settings.LOG_PATH, Path)


# ------------------------------------------------------------------
# db_available()
# ------------------------------------------------------------------


class TestDbAvailable:
    """Test beide paden van db_available()."""

    def test_false_als_wachtwoord_leeg(self) -> None:
        with patch.object(settings, "DB_PASSWORD", ""):
            assert settings.db_available() is False

    def test_true_als_wachtwoord_ingesteld(self) -> None:
        with patch.object(settings, "DB_PASSWORD", "geheim123"):
            assert settings.db_available() is True
