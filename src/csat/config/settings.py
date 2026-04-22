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
TEMPLATES_PATH = Path(os.getenv("CSAT_TEMPLATES_PATH", str(BASE_DIR / "docs" / "templates")))
I18N_PATH = Path(__file__).resolve().parent.parent / "i18n"
LOG_PATH = Path(os.getenv("CSAT_LOG_PATH", str(BASE_DIR / "logs")))

# --- Logging ---
LOG_LEVEL = os.getenv("CSAT_LOG_LEVEL", "INFO")

# --- Analyseperiode ---
# Enkel data vanaf deze datum wordt meegenomen in analyses en rapporten.
# Beslissing Danny Depecker 20/03/2026 — zie ADR-007.
ANALYSE_START_DATE: str = os.getenv("CSAT_ANALYSE_START_DATE", "2025-01-01")

# --- KPI-drempelwaarden ---
# Minimale aanvaardbare gemiddelde CSAT-score (schaal 1-5).
# Beslissing Danny Depecker 22/03/2026 — zie ADR-009.
# Gebaseerd op stabiele periode jun-dec 2025 (~4,50) en 2026 YTD (4,43).
# Drempel bewust iets lager dan huidig niveau: ruimte voor tijdelijke schommelingen.
AVG_SCORE_MIN: float = float(os.getenv("CSAT_AVG_SCORE_MIN", "4.0"))

# Maximale aanvaardbare High/Critical-ratio (percentage).
# Beslissing Danny Depecker 20/03/2026 — zie ADR-007.
HIGH_CRITICAL_MAX: float = float(os.getenv("CSAT_HIGH_CRITICAL_MAX", "15.0"))

# --- KPI-targets voor target tracking (Fase 3g — fase3f-evolutie-advieskader.md §G) ---
# Beslissing DDP 29/03/2026 — 7 targets, zie fase3f sectie G.
# Minimaal % positieve scores (score >= 4).
PCT_POSITIVE_MIN: float = float(os.getenv("CSAT_PCT_POSITIVE_MIN", "75.0"))
# Maximaal % negatieve scores (score <= 2).
PCT_NEGATIVE_MAX: float = float(os.getenv("CSAT_PCT_NEGATIVE_MAX", "15.0"))
# Maximale gemiddelde responstijd in dagen.
AVG_RESPONSE_DAYS_MAX: float = float(os.getenv("CSAT_AVG_RESPONSE_DAYS_MAX", "10.0"))
# Minimaal % tickets met een klantcomment (klantbetrokkenheid).
PCT_WITH_COMMENT_MIN: float = float(os.getenv("CSAT_PCT_WITH_COMMENT_MIN", "40.0"))
# Minimale retentie van baseline-ziekenhuizen in huidige periode.
HOSPITAL_RETENTION_MIN: float = float(os.getenv("CSAT_HOSPITAL_RETENTION_MIN", "50.0"))


def db_available() -> bool:
    """Controleer of een DB-wachtwoord beschikbaar is voor connectie."""
    return bool(DB_PASSWORD)


# --- Dashboard weergave-modus ---
# CSAT_DASHBOARD_MODE = "prod"  → Deploy-knop en drie-puntjes-menu verborgen (standaard)
# CSAT_DASHBOARD_MODE = "demo"  → volledig zichtbaar (dev/test)
# Standaard = "prod"; overschrijf met env-var CSAT_DASHBOARD_MODE=demo voor dev
DASHBOARD_MODE: str = os.getenv("CSAT_DASHBOARD_MODE", "prod").lower()
DASHBOARD_PROD_MODE: bool = DASHBOARD_MODE == "prod"
