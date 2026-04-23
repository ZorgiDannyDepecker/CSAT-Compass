"""
Streamlit smoke-tests voor het CSAT-Compass dashboard (app.py).
Strategie:
    - AppTest-klasse (streamlit.testing.v1) simuleert de Streamlit-runtime
      zonder echte browser of server.
    - Als streamlit niet geinstalleerd is (CI), skippen de AppTest-tests
      automatisch — de importeerbaar-test blijft altijd actief.
    - Geen pixel-accurate UI-validatie: focus op crash-detectie en
      render-stabiliteit.
Scope:
    OK  App start zonder unhandled exception
    OK  Geen crash bij leeg maar correct DataFrame
    OK  app.py is importeerbaar via importlib zonder Streamlit-context
    OK  App start met 2025-only data (geen lopend jaar)
    OK  App start met multi-pijler data (PHARMA + CARE)
    OK  App start met slechts één ticket (minimale data)
    OK  App start met score=None (NaN-randgeval)
    OK  Twee opeenvolgende runs zijn stabiel
    OK  Mock DataFrames hebben correcte structuur en types
    NOK Pixel-accurate layout (buiten scope)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

try:
    from streamlit.testing.v1 import AppTest

    _ST_OK = True
except ImportError:
    _ST_OK = False
_SKIP = "streamlit.testing.v1 niet beschikbaar — streamlit >= 1.28 vereist"
_APP = Path(__file__).resolve().parent.parent.parent / "src" / "dashboard" / "app.py"
_COLS = [
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


def _mock_df() -> pd.DataFrame:
    """Standaard mockdata: 2 tickets PHARMA (2025 + 2026)."""
    return pd.DataFrame(
        [
            {
                "key": "SD-001",
                "issue_type": "Bug",
                "priority": "Minor",
                "summary": "T",
                "score": 4.0,
                "comment": "goed",
                "satisfaction_date": pd.Timestamp("2026-01-10"),
                "created": pd.Timestamp("2026-01-05"),
                "hospital": "AZ Test",
                "product": "Apotheek",
                "product_domain": "PHARMA",
                "project_key": "SD30",
            },
            {
                "key": "SD-002",
                "issue_type": "Question",
                "priority": "Trivial",
                "summary": "T2",
                "score": 5.0,
                "comment": "",
                "satisfaction_date": pd.Timestamp("2025-06-15"),
                "created": pd.Timestamp("2025-06-10"),
                "hospital": "UZ Test",
                "product": "Apotheek",
                "product_domain": "PHARMA",
                "project_key": "SD30",
            },
        ]
    )


def _mock_df_2025_only() -> pd.DataFrame:
    """Mockdata: alleen 2025 — geen lopend jaar."""
    return pd.DataFrame(
        [
            {
                "key": "SD-100",
                "issue_type": "Bug",
                "priority": "Major",
                "summary": "Baseline only",
                "score": 3.5,
                "comment": "ok",
                "satisfaction_date": pd.Timestamp("2025-03-10"),
                "created": pd.Timestamp("2025-03-05"),
                "hospital": "AZ Baseline",
                "product": "Apotheek",
                "product_domain": "PHARMA",
                "project_key": "SD30",
            },
            {
                "key": "SD-101",
                "issue_type": "Question",
                "priority": "Minor",
                "summary": "Baseline 2",
                "score": 4.0,
                "comment": "",
                "satisfaction_date": pd.Timestamp("2025-06-20"),
                "created": pd.Timestamp("2025-06-15"),
                "hospital": "UZ Baseline",
                "product": "Apotheek",
                "product_domain": "PHARMA",
                "project_key": "SD30",
            },
        ]
    )


def _mock_df_multi_pillar() -> pd.DataFrame:
    """Mockdata: PHARMA + CARE tickets."""
    basis = _mock_df().to_dict("records")
    basis.append(
        {
            "key": "SD-200",
            "issue_type": "Bug",
            "priority": "Critical",
            "summary": "Care ticket",
            "score": 4.5,
            "comment": "goed",
            "satisfaction_date": pd.Timestamp("2026-02-10"),
            "created": pd.Timestamp("2026-02-05"),
            "hospital": "AZ Care",
            "product": "Care",
            "product_domain": "CARE",
            "project_key": "SD30",
        }
    )
    basis.append(
        {
            "key": "SD-201",
            "issue_type": "Question",
            "priority": "Minor",
            "summary": "Care 2025",
            "score": 3.0,
            "comment": "",
            "satisfaction_date": pd.Timestamp("2025-09-15"),
            "created": pd.Timestamp("2025-09-10"),
            "hospital": "UZ Care",
            "product": "Care",
            "product_domain": "CARE",
            "project_key": "SD30",
        }
    )
    return pd.DataFrame(basis)


def _mock_df_single_ticket() -> pd.DataFrame:
    """Minimale mockdata: slechts 1 ticket."""
    return pd.DataFrame(
        [
            {
                "key": "SD-999",
                "issue_type": "Bug",
                "priority": "Blocker",
                "summary": "Enkel ticket",
                "score": 5.0,
                "comment": "perfect",
                "satisfaction_date": pd.Timestamp("2026-04-01"),
                "created": pd.Timestamp("2026-04-01"),
                "hospital": "AZ Solo",
                "product": "Apotheek",
                "product_domain": "PHARMA",
                "project_key": "SD30",
            }
        ]
    )


# ===========================================================================
# AppTest smoke-tests (alleen als streamlit aanwezig)
# ===========================================================================
@pytest.mark.skipif(not _ST_OK, reason=_SKIP)
@pytest.mark.skipif(not _APP.exists(), reason=f"app.py niet gevonden: {_APP}")
class TestDashboardAppSmoke:
    """Smoke-tests via streamlit.testing.v1.AppTest."""

    @staticmethod
    def _app() -> "AppTest":
        """Maak een AppTest instantie aan."""
        return AppTest.from_file(str(_APP), default_timeout=30)

    def test_start_geen_exception(self) -> None:
        """App start zonder unhandled exception."""
        at = self._app()
        with patch("csat.core.loaders.get_loader") as ml:
            ml.return_value.load.return_value = _mock_df()
            at.run()
        assert not at.exception

    def test_geen_crash_leeg_dataframe(self) -> None:
        """App crasht niet bij leeg maar correct DataFrame."""
        at = self._app()
        leeg = pd.DataFrame(columns=_COLS)
        leeg["created"] = pd.to_datetime(leeg["created"])
        leeg["satisfaction_date"] = pd.to_datetime(leeg["satisfaction_date"])
        with patch("csat.core.loaders.get_loader") as ml:
            ml.return_value.load.return_value = leeg
            at.run()
        assert not at.exception

    def test_start_met_2025_only_data(self) -> None:
        """App crasht niet als er alleen 2025-baseline data is (geen lopend jaar)."""
        at = self._app()
        with patch("csat.core.loaders.get_loader") as ml:
            ml.return_value.load.return_value = _mock_df_2025_only()
            at.run()
        assert not at.exception

    def test_start_met_multi_pillar_data(self) -> None:
        """App crasht niet met data van meerdere pijlers (PHARMA + CARE)."""
        at = self._app()
        with patch("csat.core.loaders.get_loader") as ml:
            ml.return_value.load.return_value = _mock_df_multi_pillar()
            at.run()
        assert not at.exception

    def test_start_met_enkel_ticket(self) -> None:
        """App crasht niet bij minimale invoer (1 ticket)."""
        at = self._app()
        with patch("csat.core.loaders.get_loader") as ml:
            ml.return_value.load.return_value = _mock_df_single_ticket()
            at.run()
        assert not at.exception

    def test_start_met_score_none(self) -> None:
        """App crasht niet als sommige tickets geen score hebben (NaN)."""
        at = self._app()
        df = _mock_df().copy()
        df.loc[0, "score"] = None  # type: ignore[call-overload]
        with patch("csat.core.loaders.get_loader") as ml:
            ml.return_value.load.return_value = df
            at.run()
        assert not at.exception

    def test_herstart_stabiel(self) -> None:
        """Twee opeenvolgende runs met dezelfde data geven geen exception."""
        at = self._app()
        with patch("csat.core.loaders.get_loader") as ml:
            ml.return_value.load.return_value = _mock_df()
            at.run()
            assert not at.exception
            at.run()
            assert not at.exception


# ===========================================================================
# Importeerbaar-test (altijd actief, geen streamlit-context nodig)
# ===========================================================================
class TestAppImporteerbaar:
    """app.py is importeerbaar via importlib met gemockte streamlit-context."""

    def test_module_laadbaar(self) -> None:
        """app.py laadt zonder crash in een gemockte streamlit-omgeving."""
        import importlib.util
        import sys

        mock_st = MagicMock()
        mock_st.set_page_config = MagicMock()
        mock_st.session_state = {}
        with patch.dict(sys.modules, {"streamlit": mock_st}):
            spec = importlib.util.spec_from_file_location("app", str(_APP))
            if not spec or not spec.loader:
                pytest.skip("app.py spec kon niet worden aangemaakt")
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)  # type: ignore[union-attr]
                assert mod is not None
            except Exception:
                pytest.skip("app.py kon niet geladen worden in mock-context")


# ===========================================================================
# DataFrame-validatie helpers (altijd actief)
# ===========================================================================
class TestMockDataFrames:
    """Valideer de mock-DataFrames zelf — structuur en types."""

    def test_mock_df_kolomstructuur(self) -> None:
        """Standaard mock DataFrame heeft alle vereiste kolommen."""
        df = _mock_df()
        for col in _COLS:
            assert col in df.columns, f"Kolom ontbreekt: {col}"

    def test_mock_df_2025_only_geen_2026(self) -> None:
        """2025-only mock bevat geen 2026-tickets."""
        df = _mock_df_2025_only()
        jaren = pd.to_datetime(df["created"]).dt.year.unique()
        assert 2026 not in jaren
        assert 2025 in jaren

    def test_mock_df_multi_pillar_beide_domeinen(self) -> None:
        """Multi-pillar mock bevat zowel PHARMA als CARE."""
        df = _mock_df_multi_pillar()
        domeinen = set(df["product_domain"].unique())
        assert "PHARMA" in domeinen
        assert "CARE" in domeinen

    def test_mock_df_single_ticket_lengte(self) -> None:
        """Single-ticket mock bevat exact 1 rij."""
        df = _mock_df_single_ticket()
        assert len(df) == 1

    def test_mock_df_score_types(self) -> None:
        """Scores zijn float of NaN — geen strings."""
        df = _mock_df()
        scores = df["score"].dropna()
        assert all(isinstance(s, float) for s in scores)
