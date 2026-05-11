# CSAT-Compass - Operations Runbook

**Versie:** 1.2
**Laatst bijgewerkt:** 05/05/2026

**Doel:** Operationele procedures voor de dagelijkse en maandelijkse werking van CSAT-Compass
**Type:** Runbook
**Auteur:** Danny Depecker + GHC
**Status:** Actief

**Bestandsnaam:** operations-runbook.md
**Path:** docs/03-operationeel/

---

## 1. Omgeving activeren

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\Activate.ps1
```

Verifieer de teststand na grote wijzigingen:

```powershell
.venv\Scripts\python.exe -m pytest --no-cov -q
```

---

## 2. Maandelijkse run — standaardprocedure

### Stap 1 — Voer de batch-runner uit

```powershell
.venv\Scripts\python.exe scripts/run_monthly.py --month YYYY-MM
```

### Stap 2 — Controleer de output

- Verwacht: **30 bestanden** in `output/YYYY-MM-DD/{pijler}/` (per pijler een submap)
  - 10 matrices (NL + FR per pijler)
  - 10 evolutierapporten (NL + FR per pijler)
  - 10 PNG-visualisaties (NL + FR per pijler)
- Controleer de consolefeedback op fouten (`[FOUT]`)

### Stap 3 — Verspreid de rapporten

- NL-rapporten: intern PHARMA-team
- FR-rapporten: Franstalige ziekenhuiscontacten
- Dashboard: CEO Eric + COO Christian (Fase 5 — gepland)

---

## 3. Noodprocedure — SQL niet beschikbaar

Als de connectie naar `ZRG0014WI/Lerni_DB` niet beschikbaar is:

### 3a — Controleer de fallback-CSV

```powershell
Get-ChildItem data\fallback\ | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

### 3b — Maak een verse snapshot als de CSV verouderd is

```powershell
.venv\Scripts\python.exe scripts/export_data.py --snapshot
```

### 3c — Voer de maandelijkse run uit met CSV-fallback

```powershell
.venv\Scripts\python.exe scripts/run_monthly.py --month YYYY-MM --force-csv
```

---

## 4. Individuele scripts

### Matrix alleen

```powershell
.venv\Scripts\python.exe scripts/generate_matrix.py `
    --from 2026-01 --to 2026-03 --pillar pharma --lang both
```

### Evolutierapport één pijler

```powershell
.venv\Scripts\python.exe scripts/generate_evolution.py `
    --pillar pharma `
    --baseline 2025-01 2025-12 `
    --current 2026-01 2026-03 `
    --chart
```

### Evolutierapporten alle pijlers

```powershell
.venv\Scripts\python.exe scripts/generate_all_evolutions.py `
    --baseline 2025-01 2025-12 `
    --current 2026-01 2026-03 `
    --chart
```

### Data exporteren (snapshot)

```powershell
.venv\Scripts\python.exe scripts/export_data.py --snapshot
.venv\Scripts\python.exe scripts/export_data.py --year 2025
.venv\Scripts\python.exe scripts/export_data.py --all
```

---

## 5. Databron

| Parameter | Waarde |
|---|---|
| Server | `ZRG0014WI/Lerni_DB` |
| View | `[dbo].[V_CSAT_1]` |
| Filterkolom | `product_domain` |
| Fallback-pad | `data/fallback/` |
| CSV-omgevingsvariabele | `CSAT_CSV_FALLBACK_PATH` |

**Fallback activeren via omgevingsvariabele:**

```powershell
$env:CSAT_CSV_FALLBACK_PATH = "data\fallback"
```

---

## 6. Logs

Logbestanden staan in `logs/`. Bij onverwachte fouten:

```powershell
Get-ChildItem logs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 3
Get-Content logs\<recentste-logbestand>.log | Select-Object -Last 50
```

---

## 7. CI/CD

GitHub Actions voert bij elke push uit:

- `pytest` op Python 3.11, 3.12 en 3.13
- Coverage-rapport naar Codecov

Lokale lint voor commit:

```powershell
.\tools\lint.ps1
```

---

## 8. Referenties

| Document | Beschrijving |
|---|---|
| `docs/03-operationeel/tools/run-monthly.md` | Gebruiksgids batch-runner |
| `docs/03-operationeel/tools/run-special.md` | Gebruiksgids special runner (instelbare begindatum) |
| `docs/03-operationeel/tools/export-data.md` | Gebruiksgids data-export |
| `docs/03-operationeel/kwaliteitscontrole.md` | Kwaliteitscontroles op output |
| `docs/02-tactisch/implementatie-gids.md` | Overzicht alle implementatiefasen |
| `docs/01-strategisch/architectuur-beslissingen.md` | ADRs — alle architectuurkeuzes |

---

## 9. Nieuw maand checklist

Bij het begin van elke nieuwe maand (bijv. start mei → verwerk april-data):

### 9.1 — Data run

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe scripts/run_monthly.py
```

Vervang eventueel `run_monthly.py` door `run_monthly.py --month YYYY-MM` als een specifieke maand nodig is.

### 9.2 — Output verificatie

- [ ] 30 bestanden aanwezig in `output\YYYY-MM-DD\` (2 matrix + 10 rapporten + 10 PNG per pijler)
- [ ] Geen `[FOUT]`-meldingen in de consolefeedback
- [ ] Controleer logbestand als twijfel: `Get-Content logs\<recentste>.log | Select-Object -Last 30`

### 9.3 — PDF-conversie (optioneel)

Als PDF-versies gewenst zijn:

> ⚠️ **Belangrijk:** Kopieer altijd zowel het `.md`-bestand **als** de bijbehorende `.png` naar `IN\`.
> Zonder de PNG wordt de grafiek (§13 Visuele analyse) weggelaten uit de PDF.

```powershell
# Alle bestanden uit één pijlermap in één keer (md + png)
Copy-Item "output\YYYY-MM-DD\pharma\*" "C:\Users\danndepe\Documents\Convertiemap\IN\"
```

Dan in Copilot Chat:

- `/pdf` — converteren + afdrukken
- `/pdf zonder printen` — alleen converteren, niet afdrukken

### 9.4 — Distributie rapporten

| Versie | Ontvangers |
|---|---|
| NL-rapporten (`*-nl.md` / `.pdf`) | Intern PHARMA-team: Tom, Wilfried, Frédéric, Thomas |
| FR-rapporten (`*-fr.md` / `.pdf`) | Franstalige ziekenhuiscontacten |
| Dashboard | CEO Eric + COO Christian (zodra gehost — Fase 5) |

### 9.5 — Dashboard

- Dashboard leest live via SQL (`ZRG0014WI`) → automatisch up-to-date
- Lokaal testen: `streamlit run src/dashboard/app.py`
- Productie-deploy nog niet actief (zie `hosting-deployment.md`)

### 9.6 — Periodieke onderhoudstaken (maandelijks)

- [ ] CVE-scan uitvoeren: typ `/cve` in Copilot Chat
- [ ] Voortgangsnotitie toevoegen in `docs/progression/`
- [ ] Eventuele openstaande issues in `docs/issues/` controleren
- [ ] Git-status nakijken en committen: `/git`

### 9.7 — Referentiedata bijhouden

| Maand | Run uitgevoerd | Output OK | Verspreid | Notities |
|---|:---:|:---:|:---:|---|
| 2026-03 | ✅ | ✅ | ✅ | — |
| 2026-04 | ✅ | ✅ | ⬜ | Run 05/05/2026 — verdelen nog te doen |

---

## 10. Special run — intern beeld met instelbare begindatum

Naast de standaard maandelijkse run bestaat er een **special runner** voor analyses
die starten op een andere datum dan januari. Typisch gebruik: intern PHARMA-beeld
vanaf **juli 2025**.

> Volledig verschil met de standaardrun: zie `docs/03-operationeel/tools/run-special.md`.

### 10.1 — Wanneer uitvoeren

Voer `run_special.py` uit wanneer:

- een intern beeld gewenst is op basis van data **vanaf juli 2025** (of een andere maand)
- de PHARMA-pijler apart geanalyseerd moet worden t.o.v. het ZORGI-totaalplaatje
- maandelijks, aanvullend aan `run_monthly.py` — niet ter vervanging

### 10.2 — Volledige run (aanbevolen)

```powershell
cd C:\Users\danndepe\Documents\AI\CSAT-Compass
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe scripts/run_special.py --start 2025-07 --chart
```

Verwacht: **30 bestanden** in `output\YYYY-MM-DD\{pijler}\`
(10 matrices + 10 evolutierapporten + 10 PNG's)

### 10.3 — Uitvoerstructuur

Bestanden staan in **dezelfde mappenstructuur** als de standaard run.
Het onderscheid is zichtbaar in de bestandsnaam:

| Type | Standaard | Special |
|---|---|---|
| Evolutierapport NL | `evolutie-care-2026-nl_...md` | `evolutie-care-2025-07-nl_...md` |
| Matrix NL | `matrix-care-2026-nl_...md` | `matrix-care-2025-07-nl_...md` |

### 10.4 — Checklist special run

- [ ] Omgeving actief (`Activate.ps1`)
- [ ] Run uitgevoerd met `--start 2025-07 --chart`
- [ ] 30 bestanden aanwezig — geen `[FOUT]`-meldingen
- [ ] Bestandsnamen bevatten `2025-07` als jaarlabel
- [ ] PDF-conversie indien gewenst (zie §9.3)

### 10.5 — Noodrun (SQL niet beschikbaar)

```powershell
.venv\Scripts\python.exe scripts/run_special.py --start 2025-07 --chart --force-csv
```

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 26/03/2026 | Initiële versie — fasen 1 t/m 3e operationeel | Danny Depecker + GHC |
| 1.1 | 21/04/2026 | §8 referenties uitgebreid | Danny Depecker + GHC |
| 1.2 | 05/05/2026 | §9 Nieuw maand checklist toegevoegd incl. PDF-procedure met PNG-vereiste | Danny Depecker + GHC |
| 1.3 | 11/05/2026 | §10 Special run toegevoegd; §8 run-special.md toegevoegd aan referenties | Danny Depecker + GHC |
