# ISSUE-001 — CsvLoader.load(pillar=...) filtert op verkeerde kolom

**Status:** Resolved — gefixt 13/04/2026
**Ontdekt:** 13/04/2026 tijdens Console-validatie rij 9 KPI-Targets (Prompt B nazorg)
**Severity:** Medium *(productie-impact geverifieerd in Stap 4b — zie onderaan)*
**Gerelateerd aan:** Prompt B (KPI-Targets uitbreiding), `pillars.py` constante `FILTER_COLUMN`

---

## Probleem

`CsvLoader.load(pillar="PHARMA")` retourneert 0 rijen.

De filter werkt op de kolom `product` (productnamen zoals "Apotheek", "AZIS Pharmacy",
"ZORGI CARE"), niet op de kolom `product_domain` (waar "PHARMA" wel als waarde
voorkomt — 854 rijen in snapshot `v_csat_1_volledig_20260401-1251.csv`).

---

## Reproductie

```python
from src.csat.core.loaders.csv_loader import CsvLoader
from src.csat.config.settings import CSV_FALLBACK_PATH

loader = CsvLoader(CSV_FALLBACK_PATH)
df_filtered = loader.load(pillar="PHARMA")
print(len(df_filtered))  # 0 — verwacht: 854
```

---

## Verwacht gedrag

Filter op `product_domain` conform `pillars.py` constante `FILTER_COLUMN = "product_domain"`
en de bevestiging door Danny Depecker op 20/03/2026 (zie `pillars.py` docstring).

---

## Impact

- **Console-validaties:** moeten handmatig filteren via `df[df["product_domain"]=="PHARMA"]`
  als workaround
- **Productie `app.py`:** niet getroffen — zie Stap 4b hieronder
- **Toekomstige pillars** (CARE, CARE ADMIN, ERP4HC): zelfde bug zal optreden bij
  directe `loader.load(pillar=...)` aanroepen

---

## Voorgestelde fix (later — niet in scope Prompt B-bis)

In `csv_loader.py`: filter op `product_domain` met case-insensitive match, conform
`get_pillar_for_domain()` in `pillars.py`. Hergebruik die helperfunctie om duplicatie
te vermijden.

---

## Validatie van fix

Na implementatie moet `CsvLoader(path).load(pillar="PHARMA")` exact 854 rijen
retourneren op snapshot `v_csat_1_volledig_20260401-1251.csv`.

---

## Productie-impact (Stap 4b — geverifieerd 13/04/2026)

Alle productie-aanroepen in `src/dashboard/app.py` en scripts zijn gecontroleerd:

| Aanroep-locatie | Loader-type | Filter-strategie | Getroffen door bug? |
|---|---|---|---|
| `app.py:195` — `_load_df()` | CsvLoader of SqlLoader (via `get_loader()`) | `loader.load()` zonder `pillar`-argument | **Nee** |
| `_make_kc_dataframes()` | n.v.t. (gebruikt gecachte `_load_df()`) | Handmatige filter op `FILTER_COLUMN` via `PILLAR_REGISTRY` | **Nee** |
| `scripts/generate_matrix.py:151` | CsvLoader/SqlLoader | `loader.load()` zonder `pillar`-argument | **Nee** |
| `scripts/generate_evolution.py:126` | CsvLoader/SqlLoader | `loader.load()` zonder `pillar`-argument | **Nee** |
| `scripts/generate_all_evolutions.py:121` | CsvLoader/SqlLoader | `loader.load()` zonder `pillar`-argument | **Nee** |
| `scripts/export_data.py:91` | CsvLoader/SqlLoader | `loader.load()` zonder `pillar`-argument | **Nee** |

**Conclusie:** Geen enkele productie-aanroep gebruikt `loader.load(pillar=...)`.
De pilaar-filtering in `app.py` verloopt via `_make_kc_dataframes()` die rechtstreeks
op `FILTER_COLUMN` filtert — los van de buggy CsvLoader-methode.

**Severity blijft Medium** — enkel Console-validaties en directe loader-tests zijn getroffen.
