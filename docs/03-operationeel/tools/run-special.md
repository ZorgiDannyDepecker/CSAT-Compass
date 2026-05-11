# CSAT-Compass - run_special.py

**Versie:** 1.0
**Laatst bijgewerkt:** 11/05/2026

**Doel:** Operationele gebruiksgids voor de special runner (instelbare begindatum)
**Type:** Tool-documentatie
**Auteur:** Danny Depecker + GHC
**Status:** Actief

**Bestandsnaam:** run-special.md
**Path:** docs/03-operationeel/tools/

---

## Samenvatting

`scripts/run_special.py` genereert dezelfde output als de standaard maandelijkse run,
maar met een **instelbare begindatum**. Hiermee is het mogelijk om analyses te beperken
tot een specifieke startperiode — onafhankelijk van de reguliere ZORGI-rapportage.

**Typisch gebruik:** intern PHARMA-beeld op basis van data **vanaf juli 2025** t/m de
volledige afgelopen maand, ter aanvulling van (niet ter vervanging van) het ZORGI-geheel.

Per pijler worden **6 bestanden** gegenereerd — identiek aan de standaardstructuur:

| Bestand | Inhoud |
|---|---|
| `matrix-{pijler}-{start}-nl/fr_...md` | Maandmatrix NL + FR (start t/m huidig) |
| `evolutie-{pijler}-{start}-nl/fr_...md` | Evolutierapport NL + FR |
| `evolutie-{pijler}-{start}-nl/fr_...png` | Visualisatie NL + FR |

**Bestandsnamen bevatten altijd de begindatum** — zo is het onderscheid met de
standaard output (`evolutie-care-2026-nl_...md`) direct zichtbaar
(`evolutie-care-2025-07-nl_...md`).

**Volledig commando:**

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe scripts/run_special.py --start 2025-07 --chart
```

---

## Wanneer gebruiken

| Situatie | Script |
|---|---|
| Maandelijkse standaardrapportage (volledig jaar 2025 als baseline) | `run_monthly.py` |
| Intern PHARMA-beeld — data enkel vanaf een specifieke maand | `run_special.py` |
| Adhoc evolutie voor één pijler met vrije periodes | `generate_evolution.py` |

---

## Gebruik

### Standaardrun (begindatum = juli 2025, vorige maand als einddatum)

```powershell
.venv\Scripts\python.exe scripts/run_special.py --start 2025-07 --chart
```

### Specifieke doelmaand

```powershell
.venv\Scripts\python.exe scripts/run_special.py --start 2025-07 --month 2026-04 --chart
```

### Selectie van pijlers

```powershell
.venv\Scripts\python.exe scripts/run_special.py --start 2025-07 --pillar pharma care --chart
```

### Zonder PNG-visualisaties

```powershell
.venv\Scripts\python.exe scripts/run_special.py --start 2025-07
```

### Zonder vergelijkingsmatrix

```powershell
.venv\Scripts\python.exe scripts/run_special.py --start 2025-07 --chart --no-matrix
```

### Noodrun (SQL niet beschikbaar)

```powershell
.venv\Scripts\python.exe scripts/run_special.py --start 2025-07 --chart --force-csv
```

Vereist dat `data/fallback/` een recente CSV-export bevat (zie `export_data.py`).

---

## Argumenten

| Argument | Beschrijving | Standaard |
|---|---|---|
| `--start YYYY-MM` | Begindatum van de analyse — baseline start hier | `2025-07` |
| `--month YYYY-MM` | Einddatum huidige periode | vorige maand |
| `--pillar ...` | Pijlers (een of meer) | alle 5: zorgi pharma care care_admin erp4hc |
| `--chart` | Genereer PNG-visualisaties (NL + FR per pijler) | uit |
| `--no-matrix` | Sla vergelijkingsmatrices over | uit (matrix AAN) |
| `--force-csv` | SQL omzeilen, CSV-fallback forceren | uit |
| `--output MAP` | Alternatieve basisuitvoermap | `output/` |

---

## Periodelogica

De begindatum (`--start`) bepaalt automatisch de splitsing:

| Parameter | Afleiding | Voorbeeld (--start 2025-07 --month 2026-04) |
|---|---|---|
| Baseline van | `--start` | `2025-07` |
| Baseline tot | einde van het startjaar | `2025-12` |
| Current van | 1 januari volgend jaar | `2026-01` |
| Current tot | `--month` | `2026-04` |
| Matrix van | `--start` | `2025-07` |
| Matrix tot | `--month` | `2026-04` |

> ⚠️ `--start` en `--month` **moeten in verschillende jaren vallen**.
> De splitsing baseline/current loopt altijd op de jaargrens (31 december / 1 januari).

---

## Output

Bestanden worden weggeschreven naar de **gewone per-pijler mappenstructuur** in `output/`:

```text
output/
  YYYY-MM-DD/
    zorgi/
      matrix-zorgi-2025-07-nl_TIMESTAMP.md
      matrix-zorgi-2025-07-fr_TIMESTAMP.md
      evolutie-zorgi-2025-07-nl_TIMESTAMP.md
      evolutie-zorgi-2025-07-fr_TIMESTAMP.md
      evolutie-zorgi-2025-07-nl_TIMESTAMP.png
      evolutie-zorgi-2025-07-fr_TIMESTAMP.png
    pharma/
      matrix-pharma-2025-07-nl_TIMESTAMP.md  ← let op: "2025-07" i.p.v. "2026"
      ...
    care/      ...
    care_admin/ ...
    erp4hc/    ...
```

**Totaal bij volledige run** (`--chart`): **30 bestanden**
(10 matrices + 10 evolutierapporten + 10 PNG's)

### Onderscheid met standaard output

| | Standaard (`run_monthly.py`) | Special (`run_special.py`) |
|---|---|---|
| Bestandsnaam | `evolutie-care-2026-nl_...md` | `evolutie-care-2025-07-nl_...md` |
| Baseline | volledig 2025 (jan–dec) | H2 2025 (jul–dec) |
| Mappenstructuur | `output/.../care/` | `output/.../care/` (zelfde) |

---

## Probleemoplossing

| Symptoom | Oorzaak | Oplossing |
|---|---|---|
| `ValueError: --start moet in een eerder jaar liggen` | `--start` en `--month` vallen in hetzelfde jaar | Kies een `--start` in het jaar vóór `--month` |
| `ConnectionError` bij start | SQL Server niet bereikbaar | Gebruik `--force-csv` |
| `0 rijen geladen` voor een pijler | Geen data in die periode | Controleer of de startdatum niet te recent is |
| Matrix-bestand mist | Pijler-fout tijdens matrix-stap | Bekijk `[FOUT]`-regel in console + `logs/` |
| PNG ontbreekt | `--chart` niet meegegeven | Herrun met `--chart --no-matrix` (matrix niet opnieuw aanmaken) |

---

## Gerelateerde scripts

| Script | Gebruik |
|---|---|
| `scripts/run_monthly.py` | Standaard maandelijkse run (volledig jaar 2025 als baseline) |
| `scripts/generate_evolution.py` | Evolutierapport voor één pijler met vrije periodes |
| `scripts/generate_matrix.py` | Enkel de matrix genereren |
| `scripts/export_data.py` | CSV-snapshot aanmaken voor fallback |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 11/05/2026 | Initiële versie | Danny Depecker + GHC |

