"""
Tijdelijk preview-script — genereert een realistische CSAT-Compass PNG
met volledig 2025 (baseline) + Q1 2026 (current) en 8 ziekenhuizen.

Gebruik: python WIP/_gen_preview_png.py
"""

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import matplotlib

matplotlib.use("Agg")

import pandas as pd

from csat.core.analysers.evolution_analyser import EvolutionAnalyser
from csat.core.exporters.evolution_visualiser import EvolutionVisualiser

random.seed(42)

# ── Configuratie ───────────────────────────────────────────────────────────
HOSPITALS = [
    "AZ Groeninge",
    "UZ Brussel",
    "OLV Aalst",
    "AZ Sint-Jan",
    "UZ Leuven",
    "CHU Liège",
    "AZ Delta",
    "ZOL Genk",
]
PRIORITIES = ["Blocker", "Critical", "Major", "Minor", "Trivial"]
ISSUE_TYPES = ["Bug", "Question", "Improvement", "Task"]

rows = []
key_counter = 1


def _make_row(year, month, hospital, priority, issue_type, score, resp_offset):
    day = random.randint(1, 28)
    created = f"{year}-{month:02d}-{day:02d}"
    sat_day = day + resp_offset
    sat_date = None
    if score is not None and sat_day <= 28:
        sat_date = f"{year}-{month:02d}-{sat_day:02d}"
    return {
        "key": f"SD-{key_counter:04d}",
        "issue_type": issue_type,
        "priority": priority,
        "summary": "Test ticket",
        "score": score,
        "comment": "",
        "satisfaction_date": pd.Timestamp(sat_date) if sat_date else pd.NaT,
        "created": pd.Timestamp(created),
        "hospital": hospital,
        "product": "Apotheek",
        "product_domain": "PHARMA",
        "project_key": "SD30",
    }


# ── 2025: volledig jaar — dalend scoreprofiel eerste helft, licht herstel tweede helft
for month in range(1, 13):
    is_crisis = month <= 6
    n_tickets = random.randint(18, 35)
    for _ in range(n_tickets):
        hospital = random.choice(HOSPITALS)
        priority = random.choices(
            PRIORITIES,
            weights=[15, 20, 25, 25, 15] if is_crisis else [5, 10, 20, 35, 30],
        )[0]
        issue_type = random.choice(ISSUE_TYPES)
        raw_score = random.choices(
            [1, 2, 3, 4, 5],
            weights=[15, 25, 30, 20, 10] if is_crisis else [5, 15, 25, 30, 25],
        )[0]
        score = float(raw_score) if random.random() > 0.08 else None
        resp = random.randint(5, 20)
        rows.append(_make_row(2025, month, hospital, priority, issue_type, score, resp))
        key_counter += 1

# ── 2026 Q1: verbeterd scoreprofiel, kortere responstijd, ZOL Genk verdwijnt
for month in range(1, 4):
    n_tickets = random.randint(12, 22)
    for _ in range(n_tickets):
        hospital = random.choice(HOSPITALS[:-1])  # ZOL Genk (index 7) afwezig
        priority = random.choices(PRIORITIES, weights=[3, 7, 18, 38, 34])[0]
        issue_type = random.choice(ISSUE_TYPES)
        raw_score = random.choices([1, 2, 3, 4, 5], weights=[3, 8, 18, 38, 33])[0]
        score = float(raw_score) if random.random() > 0.05 else None
        resp = random.randint(1, 5)
        rows.append(_make_row(2026, month, hospital, priority, issue_type, score, resp))
        key_counter += 1

df = pd.DataFrame(rows)
n_2025 = len(df[df["created"].dt.year == 2025])
n_2026 = len(df[df["created"].dt.year == 2026])
print(f"Dataset: {len(df)} tickets  |  2025: {n_2025}  |  2026 Q1: {n_2026}")

# ── Analyse ────────────────────────────────────────────────────────────────
baseline_periods = [f"2025-{m:02d}" for m in range(1, 13)]
current_periods = [f"2026-{m:02d}" for m in range(1, 4)]

analyser = EvolutionAnalyser(df, pillar_key="pharma")
result = analyser.analyse(
    baseline_periods,
    current_periods,
    baseline_label="Volledig 2025",
    current_label="jan-mrt 2026",
)

print(
    f"Analyse: baseline avg={result.baseline_avg_score:.2f}  "
    f"current avg={result.current_avg_score:.2f}  "
    f"delta={result.delta_avg_score:+.2f}  "
    f"structureel={result.trend_is_structural}"
)
print(f"Tijdlijn: {len(result.monthly_timeline)} maanden")
print(f"Ziekenhuizen: {len(result.hospital_comparison)}")

# ── Export ─────────────────────────────────────────────────────────────────
vis = EvolutionVisualiser(result)
out = vis.export(ROOT / "output", year="2026")
print(f"PNG gegenereerd: {out}")

