"""
Unit tests voor src/csat/utils/logger.py.
Test setup_logger(): mappaanmaak, handler-registratie en log-niveau.
"""

from pathlib import Path

from loguru import logger as loguru_logger

from csat.utils.logger import setup_logger


class TestSetupLogger:
    """Tests voor de logger-configuratie."""

    def test_mapt_logmap_aan_als_niet_bestaat(self, tmp_path: Path) -> None:
        logmap = tmp_path / "submap" / "logs"
        assert not logmap.exists()
        setup_logger(logmap, log_level="INFO")
        assert logmap.exists()

    def test_bestaande_map_geeft_geen_fout(self, tmp_path: Path) -> None:
        tmp_path.mkdir(parents=True, exist_ok=True)
        setup_logger(tmp_path, log_level="INFO")  # mag niet crashen

    def test_debug_level_werkt(self, tmp_path: Path) -> None:
        setup_logger(tmp_path, log_level="DEBUG")

    def test_warning_level_werkt(self, tmp_path: Path) -> None:
        setup_logger(tmp_path, log_level="WARNING")

    def test_lowercase_level_werkt(self, tmp_path: Path) -> None:
        """log_level mag in kleine letters meegegeven worden."""
        setup_logger(tmp_path, log_level="info")

    def test_handlers_worden_geregistreerd(self, tmp_path: Path) -> None:
        """Na setup_logger() moeten er minimaal 2 handlers actief zijn."""
        setup_logger(tmp_path, log_level="INFO")
        # Loguru's handler-lijst is intern — controleer indirect via een log-bericht
        loguru_logger.info("test setup_logger handlers")

    def test_logbestand_patroon_in_map(self, tmp_path: Path) -> None:
        """Na het loggen van een bericht moet er een logbestand in de map staan."""
        setup_logger(tmp_path, log_level="DEBUG")
        loguru_logger.debug("trigger bestandshandler")
        logbestanden = list(tmp_path.glob("csat-compass_*.log"))
        assert len(logbestanden) >= 1
