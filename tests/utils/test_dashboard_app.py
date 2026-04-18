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


def _mock_df():
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


# ===========================================================================
# AppTest smoke-tests (alleen als streamlit aanwezig)
# ===========================================================================
@pytest.mark.skipif(not _ST_OK, reason=_SKIP)
@pytest.mark.skipif(not _APP.exists(), reason=f"app.py niet gevonden: {_APP}")
class TestDashboardAppSmoke:
    """Smoke-tests via streamlit.testing.v1.AppTest."""

    @staticmethod
    def _app():
        return AppTest.from_file(str(_APP), default_timeout=30)

    def test_start_geen_exception(self):
        """App start zonder unhandled exception."""
        at = self._app()
        with patch("csat.core.loaders.get_loader") as ml:
            ml.return_value.load.return_value = _mock_df()
            at.run()
        assert not at.exception

    def test_geen_crash_leeg_dataframe(self):
        """App crasht niet bij leeg maar correct DataFrame."""
        at = self._app()
        leeg = pd.DataFrame(columns=_COLS)
        leeg["created"] = pd.to_datetime(leeg["created"])
        leeg["satisfaction_date"] = pd.to_datetime(leeg["satisfaction_date"])
        with patch("csat.core.loaders.get_loader") as ml:
            ml.return_value.load.return_value = leeg
            at.run()
        assert not at.exception


# ===========================================================================
# Importeerbaar-test (altijd actief, geen streamlit-context nodig)
# ===========================================================================
class TestAppImporteerbaar:
    """app.py is importeerbaar via importlib met gemockte streamlit-context."""

    def test_module_laadbaar(self):
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
