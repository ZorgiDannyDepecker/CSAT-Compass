"""
CSAT-Compass — Product-pijler exploratiescript
Gebruik: python scripts/explore_products.py

Verbindt met V_CSAT_1, analyseert de product-kolom en exporteert
een overzicht naar output/product-pijler-mapping.csv zodat Danny
de pijlertoewijzing kan controleren en bevestigen.
"""

import sys
from pathlib import Path

# Zorg dat src/ vindbaar is
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from csat.config.pillars import PILLAR_REGISTRY  # noqa: E402
from csat.config.settings import CSV_FALLBACK_PATH, DB_CONN  # noqa: E402
from csat.core.loaders import get_loader  # noqa: E402
from csat.utils.logger import setup_logger  # noqa: E402

# ------------------------------------------------------------------
# Logger
# ------------------------------------------------------------------

setup_logger(ROOT / "logs", log_level="INFO")

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

# Bouw opzoektabel: product (uppercase) → pijlersleutel
PRODUCT_TO_PILLAR: dict[str, str] = {}
for pillar_key, pillar_cfg in PILLAR_REGISTRY.items():
    if pillar_key == "zorgi":
        continue
    for p in pillar_cfg["products"]:
        PRODUCT_TO_PILLAR[p.strip().upper()] = pillar_key


def pijler_voor_product(product: str) -> str:
    """Geef de pijlersleutel terug op basis van de product-kolom (hoofdletterongevoelig)."""
    return PRODUCT_TO_PILLAR.get(product.strip().upper(), "!! NIET GEMAPT")


# ------------------------------------------------------------------
# Data laden
# ------------------------------------------------------------------

print("\n[*] Data laden vanuit V_CSAT_1 ...")
loader = get_loader(DB_CONN, CSV_FALLBACK_PATH)
df = loader.load()
print(f"    {len(df):,} tickets geladen\n")

# ------------------------------------------------------------------
# Aggregatie per product
# ------------------------------------------------------------------

print("[*] Filterkolom voor pijlers: 'product'\n")

agg = (
    df.groupby("product", dropna=False)
    .agg(
        tickets=("key", "count"),
        gem_score=("score", "mean"),
        vroegste=("created", "min"),
        laatste=("created", "max"),
    )
    .reset_index()
    .sort_values("tickets", ascending=False)
)

# Pijlertoewijzing toevoegen
agg["pijler"] = agg["product"].apply(pijler_voor_product)
agg["gem_score"] = agg["gem_score"].round(2)
agg["vroegste"] = pd.to_datetime(agg["vroegste"]).dt.strftime("%Y-%m-%d")
agg["laatste"] = pd.to_datetime(agg["laatste"]).dt.strftime("%Y-%m-%d")

# Kolommen herordenen
agg = agg[["product", "pijler", "tickets", "gem_score", "vroegste", "laatste"]]

# ------------------------------------------------------------------
# Weergave in terminal
# ------------------------------------------------------------------

totaal = agg["tickets"].sum()
niet_gemapt = agg[agg["pijler"] == "!! NIET GEMAPT"]["tickets"].sum()

print(f"{'PRODUCT':<35} {'PIJLER':<20} {'TICKETS':>8}  {'GEM.SCORE':>10}  {'VROEGSTE':>12}  {'LAATSTE':>12}")
print("-" * 105)

for _, rij in agg.iterrows():
    vlag = "  <- niet gemapt" if rij["pijler"] == "!! NIET GEMAPT" else ""
    print(
        f"{str(rij['product']):<35} {str(rij['pijler']):<20} {int(rij['tickets']):>8}"
        f"  {str(rij['gem_score']):>10}  {str(rij['vroegste']):>12}  {str(rij['laatste']):>12}"
        f"{vlag}"
    )

print("-" * 105)
print(f"\n[i] Totaal: {totaal:,} tickets")
print(f"    Gemapt:      {totaal - niet_gemapt:,} ({(totaal - niet_gemapt) / totaal * 100:.1f}%)")
print(f"    Niet gemapt: {niet_gemapt:,} ({niet_gemapt / totaal * 100:.1f}%)")
print(f"\n[i] Filterkolom: 'product' — exact zoals weergegeven in bovenstaande tabel")
print("    De pijler-analyser vergelijkt case-insensitief op deze waarden.\n")

# ------------------------------------------------------------------
# CSV exporteren
# ------------------------------------------------------------------

output_dir = ROOT / "output"
output_dir.mkdir(parents=True, exist_ok=True)
csv_pad = output_dir / "product-pijler-mapping.csv"

agg.to_csv(csv_pad, index=False, encoding="utf-8-sig", sep=";")
print(f"[OK] CSV geexporteerd naar: {csv_pad}\n")
print("     Open het bestand in Excel om pijlertoewijzingen te reviewen.")
print("     Kolom 'pijler' = '!! NIET GEMAPT' = actie vereist\n")

