# BACKLOG-006 — SLA's (INT & EXT) als aparte KPI

**Status:** Open
**Prioriteit:** Medium
**Aangemaakt:** 20/04/2026
**Auteur:** Danny Depecker
**Context:** Advisory-sessie 20/04/2026

---

## Achtergrond

Momenteel worden SLA-gegevens niet opgenomen als zelfstandige KPI in CSAT-Compass.
SLA-naleving is echter een directe indicator van servicekwaliteit en een relevante
aanvulling op de CSAT-scores — een ticket kan positief beoordeeld worden terwijl
de SLA toch overschreden was, of omgekeerd.

Er wordt een onderscheid gemaakt tussen twee SLA-types:

- **INT (intern):** interne SLA-afspraken binnen ZORGI
- **EXT (extern):** externe SLA-afspraken met de klant (ziekenhuis)

Beide types dienen als **aparte KPI** opgenomen te worden, niet samengevoegd.

---

## Scope

- Nieuwe KPI `sla_int` en `sla_ext` toevoegen aan de analyselaag
- Weergave in Streamlit-dashboard (tegels + grafieken)
- Weergave in maand- en evolutierapporten (NL/FR)
- Databron: te bevestigen (kolommen in `V_CSAT_1` of `V_CSAT_2` — zie aandachtspunten)

---

## Functionele Vereisten

1. **Twee aparte KPI's:** `sla_int` en `sla_ext` — nooit samengevoegd weergegeven
2. **Metriek (voorstel):** nalevingspercentage per periode — `% tickets binnen SLA`
   - Formule: `tickets binnen SLA / totaal tickets * 100`
3. **Drempelwaarden (te bevestigen):** groen/oranje/rood per SLA-type
4. **Weergave in dashboard:** aparte tegels per SLA-type, vergelijkbaar met bestaande KPI-tegels
5. **Weergave in rapporten:** nieuwe rij in KPI-overzichtstabel (NL/FR tweetalig)
6. **Tweetaligheid:**
   - NL: `Interne SLA`, `Externe SLA`
   - FR: `SLA interne`, `SLA externe`

---

## Technische Aandachtspunten

- **Databron:** te bevestigen welke view (`V_CSAT_1` of `V_CSAT_2`) de SLA-kolommen bevat
  en wat de exacte kolomnamen zijn
- **Nieuwe velden in `KpiResult`:**
  - `sla_int_pct: float = 0.0` — nalevingspercentage interne SLA
  - `sla_ext_pct: float = 0.0` — nalevingspercentage externe SLA
- **`BaseAnalyser`:** nieuwe methoden `_calc_sla_int()` en `_calc_sla_ext()`
- **Drempelwaarden:** toe te voegen aan `settings.py` als configureerbare constanten
  (analoog aan `AVG_SCORE_MIN` en `HIGH_CRITICAL_MAX`)
- **Dashboard:** nieuwe tegels in Samenvatting-tab; ook zichtbaar in alle vensters
  (volledig, tendensvenster, maandvenster)
- **Rapporten:** KPI-tabel uitbreiden in `insights_generator.py`

---

## Openstaande Vragen

| Vraag | Status |
|---|---|
| Welke view bevat de SLA-kolommen: `V_CSAT_1` of `V_CSAT_2`? | ❓ Te bevestigen |
| Exacte kolomnamen voor INT en EXT SLA in de view? | ❓ Te bevestigen |
| Drempelwaarden voor groen/oranje/rood per SLA-type? | ❓ Te bevestigen |
| Zijn SLA-gegevens beschikbaar voor alle pijlers of enkel PHARMA? | ❓ Te bevestigen |

---

## Afhankelijkheden

- BACKLOG-003 (`V_CSAT_2` + DEV-filter) — mogelijk gedeelde databron
- BACKLOG-002 (maandvenster) — SLA-KPI's dienen ook zichtbaar in het maandvenster

---

## Wanneer Oppakken

Blocker: bevestiging van databron en kolomnamen voor SLA INT/EXT.
Technische implementatie kan daarna in één fase samen met of na BACKLOG-003.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
|---|---|---|---|
| 0.1 | 20/04/2026 | Initieel document | Danny Depecker |
