"""Export PHARMA tickets vanaf 2025 naar CSV."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from csat.config.pillars import PILLAR_REGISTRY
from csat.core.loaders import CsvLoader

loader = CsvLoader(ROOT / "data" / "fallback")
df = loader.load()

pharma_products = PILLAR_REGISTRY["pharma"]["products"]
df_pharma = df[df["product_domain"].isin(pharma_products)].copy()
df_pharma = df_pharma[pd.to_datetime(df_pharma["created"]) >= "2025-01-01"].copy()
df_pharma = df_pharma.sort_values("created").reset_index(drop=True)

uit = ROOT / "output" / "v_csat_1_pharma_2025-heden.csv"
df_pharma.to_csv(uit, index=False, sep=";", encoding="utf-8-sig")

print(f"Rijen   : {len(df_pharma)}")
print(f"Periode : {df_pharma['created'].min().date()} tot {df_pharma['created'].max().date()}")
print(f"Bestand : {uit}")

