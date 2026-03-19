"""
Instellingen voor CSAT-Compass.
Laadt configuratie uit omgevingsvariabelen (.env bestand).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Basis projectmap bepalen en .env laden
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# --- Database configuratie ---
DB_SERVER = os.getenv("CSAT_DB_SERVER", "ZRG0014WI")
DB_NAME = os.getenv("CSAT_DB_NAME", "Lerni_DB")
DB_SCHEMA = os.getenv("CSAT_DB_SCHEMA", "dbo")
DB_VIEW = os.getenv("CSAT_DB_VIEW", "V_CSAT_1")
DB_USER = os.getenv("CSAT_DB_USER", "csat_user")
DB_PASSWORD = os.getenv("CSAT_DB_PASSWORD", "")
DB_DRIVER = os.getenv("CSAT_DB_DRIVER", "ODBC Driver 18 for SQL Server")

# Volledige connectiestring opbouwen (SQL Server authenticatie)
DB_CONN = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
    f"?driver={DB_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"
)

# --- Paden ---
CSV_FALLBACK_PATH = Path(os.getenv("CSAT_CSV_FALLBACK_PATH", str(BASE_DIR / "data" / "fallback")))
OUTPUT_PATH = Path(os.getenv("CSAT_OUTPUT_PATH", str(BASE_DIR / "output")))
TEMPLATES_PATH = BASE_DIR / "docs" / "templates"
I18N_PATH = Path(__file__).resolve().parent.parent / "i18n"
LOG_PATH = Path(os.getenv("CSAT_LOG_PATH", str(BASE_DIR / "logs")))

# --- Logging ---
LOG_LEVEL = os.getenv("CSAT_LOG_LEVEL", "INFO")


def db_available() -> bool:
    """Controleer of een DB-wachtwoord beschikbaar is voor connectie."""
    return bool(DB_PASSWORD)
