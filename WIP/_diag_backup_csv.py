"""Diagnostisch script — volledige inhoudcontrole van v_csat_1_volledig_backup.csv."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

PAD = ROOT / "output" / "v_csat_1_volledig_backup.csv"

df = pd.read_csv(PAD, sep=";", encoding="utf-8-sig", parse_dates=["created", "satisfaction_date"])

print(f"\n{'='*55}")
print(f"  Bestand : {PAD.name}")
print(f"  Grootte : {PAD.stat().st_size / 1024:.1f} KB")
print(f"{'='*55}")

# --- Basisinfo ---
print(f"\n[1] BASISINFO")
print(f"  Rijen totaal     : {len(df):,}")
print(f"  Kolommen         : {len(df.columns)}")
print(f"  Ontbrekende kol. : {list(set(df.columns) ^ {'key','issue_type','priority','summary','score','comment','satisfaction_date','created','hospital','product','product_domain','project_key'})}")

# --- Datumbereik ---
print(f"\n[2] DATUMBEREIK (created)")
print(f"  Vroegste datum   : {df['created'].min()}")
print(f"  Laatste datum    : {df['created'].max()}")
print(f"  Jaren aanwezig   : {sorted(df['created'].dt.year.dropna().unique().tolist())}")

# --- Verdeling per jaar ---
print(f"\n[3] TICKETS PER JAAR")
jaar_counts = df.groupby(df['created'].dt.year).size()
for jaar, n in jaar_counts.items():
    print(f"  {jaar} : {n:>6,} tickets")

# --- product_domain verdeling ---
print(f"\n[4] PRODUCT_DOMAIN VERDELING")
for dom, n in df['product_domain'].value_counts().items():
    print(f"  {str(dom):<20} : {n:>6,}")

# --- Score volledigheid ---
scored = df.dropna(subset=["score"])
print(f"\n[5] SCORES")
print(f"  Gescoord         : {len(scored):,} / {len(df):,}  ({len(scored)/len(df)*100:.1f}%)")
print(f"  Score min/max    : {scored['score'].min()} / {scored['score'].max()}")
print(f"  Gem. score       : {scored['score'].mean():.2f}")
print(f"  Score 1          : {(scored['score']==1).sum():,}")
print(f"  Score 2          : {(scored['score']==2).sum():,}")
print(f"  Score 3          : {(scored['score']==3).sum():,}")
print(f"  Score 4          : {(scored['score']==4).sum():,}")
print(f"  Score 5          : {(scored['score']==5).sum():,}")

# --- Duplicaten ---
dupes = df.duplicated(subset=["key"]).sum()
print(f"\n[6] KWALITEIT")
print(f"  Dubbele keys     : {dupes:,}")
print(f"  Lege hospitals   : {df['hospital'].isna().sum():,}")
print(f"  Lege product_dom : {df['product_domain'].isna().sum():,}")

# --- Vergelijk met 2025-heden ---
PAD2 = ROOT / "output" / "v_csat_1_2025-heden.csv"
if PAD2.exists():
    df2 = pd.read_csv(PAD2, sep=";", encoding="utf-8-sig", parse_dates=["created"])
    print(f"\n[7] VERGELIJKING MET v_csat_1_2025-heden.csv")
    print(f"  Volledig backup  : {len(df):,} rijen  ({df['created'].min().date()} tot {df['created'].max().date()})")
    print(f"  2025-heden       : {len(df2):,} rijen  ({df2['created'].min().date()} tot {df2['created'].max().date()})")

print(f"\n{'='*55}\n")

