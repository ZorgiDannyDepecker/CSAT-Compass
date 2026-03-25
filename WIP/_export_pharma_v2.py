"""
Export PHARMA 2025-heden met extra datum-kolommen (zonder tijdstip).

Voegt toe:
  created_datum        — enkel de datum van created          (YYYY-MM-DD)
  satisfaction_datum   — enkel de datum van satisfaction_date (YYYY-MM-DD, leeg als NaT)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from csat.config.pillars import PILLAR_REGISTRY
from csat.core.loaders import CsvLoader

loader = CsvLoader(ROOT / "data" / "fallback")
df = loader.load()

# Filter PHARMA + vanaf 2025
pharma_products = PILLAR_REGISTRY["pharma"]["products"]
df_pharma = df[df["product_domain"].isin(pharma_products)].copy()
df_pharma = df_pharma[pd.to_datetime(df_pharma["created"]) >= "2025-01-01"].copy()
df_pharma = df_pharma.sort_values("created").reset_index(drop=True)

# Extra datum-kolommen — enkel de datumstempel, geen tijdstip
df_pharma["created_datum"] = pd.to_datetime(df_pharma["created"]).dt.date
df_pharma["satisfaction_datum"] = pd.to_datetime(
    df_pharma["satisfaction_date"], errors="coerce"
).dt.date  # leeg (NaT) als er geen score-datum is

# Kolom-volgorde: datum-kolommen direct naast de originelen
kolommen = [
    "key", "issue_type", "priority", "summary", "score", "comment",
    "created", "created_datum",
    "satisfaction_date", "satisfaction_datum",
    "hospital", "product", "product_domain", "project_key",
]
df_pharma = df_pharma[kolommen]

# Export
uit = ROOT / "output" / "v_csat_1_pharma_2025-heden_v2.csv"
df_pharma.to_csv(uit, index=False, sep=";", encoding="utf-8-sig")

print(f"Rijen             : {len(df_pharma)}")
print(f"Periode           : {df_pharma['created_datum'].min()} tot {df_pharma['created_datum'].max()}")
print(f"Met satisfaction  : {df_pharma['satisfaction_datum'].notna().sum()} / {len(df_pharma)}")
print(f"Kolommen          : {list(df_pharma.columns)}")
print(f"Bestand           : {uit}")

