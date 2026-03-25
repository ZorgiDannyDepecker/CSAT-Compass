"""Diagnostisch script — PHARMA data per maand controleren."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from csat.config.pillars import PILLAR_REGISTRY
from csat.core.loaders import CsvLoader

loader = CsvLoader(ROOT / "data" / "fallback")
df = loader.load()

pharma_domain = PILLAR_REGISTRY["pharma"]["products"]
df_pharma = df[df["product_domain"].isin(pharma_domain)].copy()
df_pharma["maand"] = pd.to_datetime(df_pharma["created"]).dt.to_period("M").astype(str)

print("\nPHARMA per maand — tickets, gescoord, avg_score, pct_neg, pct_pos:")
print(f"{'Maand':<10} {'Tickets':>8} {'Gescoord':>9} {'avg':>6} {'pct_neg':>8} {'pct_pos':>8}")
print("-" * 57)
for maand in sorted(df_pharma["maand"].unique()):
    sub = df_pharma[df_pharma["maand"] == maand]
    scored = sub.dropna(subset=["score"])
    avg = round(float(scored["score"].mean()), 2) if not scored.empty else 0.0
    pct_neg = round(float((scored["score"] <= 2.0).sum() / len(scored) * 100), 1) if not scored.empty else 0.0
    pct_pos = round(float((scored["score"] >= 4.0).sum() / len(scored) * 100), 1) if not scored.empty else 0.0
    marker = " <--" if maand in ("2025-09", "2025-10", "2025-12") else ""
    print(f"{maand:<10} {len(sub):>8} {len(scored):>9} {avg:>6} {pct_neg:>7}% {pct_pos:>7}%{marker}")

