"""Vergelijking created vs satisfaction_date groepering voor PHARMA."""
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

df_pharma["created_mnd"] = pd.to_datetime(df_pharma["created"]).dt.to_period("M").astype(str)
df_pharma["sat_mnd"] = pd.to_datetime(df_pharma["satisfaction_date"], errors="coerce").dt.to_period("M").astype(str)

print("\nVERGELIJKING: created vs satisfaction_date groepering (PHARMA 2025-heden)")
print(f"\n{'Maand':<10} {'n(created)':>12} {'avg(created)':>13} {'n(sat_date)':>12} {'avg(sat_date)':>14} {'verschil':>9}")
print("-" * 75)

alle_maanden = sorted(set(df_pharma["created_mnd"].tolist() + df_pharma["sat_mnd"].tolist()))

for maand in alle_maanden:
    # Op created
    sub_c = df_pharma[df_pharma["created_mnd"] == maand].dropna(subset=["score"])
    avg_c = round(float(sub_c["score"].mean()), 2) if not sub_c.empty else None

    # Op satisfaction_date
    sub_s = df_pharma[df_pharma["sat_mnd"] == maand].dropna(subset=["score"])
    avg_s = round(float(sub_s["score"].mean()), 2) if not sub_s.empty else None

    n_c = len(sub_c) if not sub_c.empty else 0
    n_s = len(sub_s) if not sub_s.empty else 0

    verschil = ""
    if avg_c is not None and avg_s is not None and avg_c != avg_s:
        verschil = f"  !! {avg_s - avg_c:+.2f}"

    avg_c_str = f"{avg_c:.2f}" if avg_c is not None else "—"
    avg_s_str = f"{avg_s:.2f}" if avg_s is not None else "—"

    print(f"{maand:<10} {n_c:>12} {avg_c_str:>13} {n_s:>12} {avg_s_str:>14}{verschil}")

