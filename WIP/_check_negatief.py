"""Tijdelijk analysescript — controle % negatief rechtsboven per maand."""
import pandas as pd

# Laad de fallback CSV
df = pd.read_csv("data/fallback/v_csat_1_2025-heden.csv", sep=";", low_memory=False)

# Datumkolommen omzetten
df["satisfaction_date"] = pd.to_datetime(df["satisfaction_date"], errors="coerce")
df["created"] = pd.to_datetime(df["created"], errors="coerce")

# Toon alle unieke product_domain waarden (om filter te verifiëren)
print("=== Unieke product_domain waarden in CSV ===")
for v in sorted(df["product_domain"].dropna().unique()):
    print(f"  {v}")
print()

# Filter PHARMA — enige waarde in deze CSV is "PHARMA"
pharma_products = ["PHARMA"]
print(f"PHARMA filter op: {pharma_products}\n")

mask = df["product_domain"].str.strip().str.upper().isin(pharma_products)
pharma = df[mask].copy()
print(f"Totaal PHARMA tickets in fallback CSV: {len(pharma)}\n")

# Definitie van negatief: score <= 2.0 als % van gescoorde tickets
print("=== DEFINITIE rechtsboven: % negatief ===")
print("  Formule: (tickets met score <= 2) / (gescoorde tickets) × 100\n")

# Volledige maandoverzicht 2025 via satisfaction_date
print("=== Overzicht per maand 2025 (via satisfaction_date) ===")
print(f"{'Maand':<12} {'Totaal':>8} {'Gescoord':>10} {'Score<=2':>10} {'% Neg':>8}")
print("-" * 55)

for maand in [f"2025-{m:02d}" for m in range(1, 13)]:
    sub = pharma[pharma["satisfaction_date"].dt.to_period("M").astype(str) == maand]
    scored = sub[sub["score"].notna()]
    neg = scored[scored["score"] <= 2.0]
    pct = round(len(neg) / len(scored) * 100, 1) if len(scored) > 0 else None
    pct_str = f"{pct}%" if pct is not None else "GEEN DATA"
    marker = " ← LEEG" if len(sub) == 0 else (" ← geen score" if len(scored) == 0 else "")
    print(f"{maand:<12} {len(sub):>8} {len(scored):>10} {len(neg):>10} {pct_str:>8}{marker}")

# Extra check: tickets met created in 09/10/12 maar satisfaction_date in andere maand
print("\n=== Tickets met created in 09/10/12-2025 — waar zit hun satisfaction_date? ===")
for maand_nr, maand_naam in [(9, "sep"), (10, "okt"), (12, "dec")]:
    sub = pharma[
        (pharma["created"].dt.year == 2025) &
        (pharma["created"].dt.month == maand_nr)
    ]
    print(f"\nCreated in {maand_naam}-2025: {len(sub)} tickets")
    if len(sub) > 0:
        dist = sub["satisfaction_date"].dt.to_period("M").astype(str).value_counts().sort_index()
        for periode, count in dist.items():
            print(f"  satisfaction_date in {periode}: {count} tickets")
        geen_sat = sub["satisfaction_date"].isna().sum()
        if geen_sat > 0:
            print(f"  Geen satisfaction_date (NaT): {geen_sat} tickets")

