# CSAT-Compass — Fase 5a: Streamlit Dashboard PHARMA-only

**Versie:** 1.1
**Laatst bijgewerkt:** 01/04/2026

**Doel:** Implementatie van een interactief Streamlit-dashboard voor de PHARMA-pijler
**Type:** Implementatie
**Auteur:** Danny Depecker + GHC + CD
**Status:** In planning

**Bestandsnaam:** fase5a-streamlit-dashboard.md
**Path:** docs/02-tactisch/fasen/

---

## 1. Overzicht

Fase 5a sluit de volledige CSAT-Compass-flow voor de PHARMA-pijler door de bestaande
Python-analyselaag (fasen 1–3g) te verbinden met een **interactief Streamlit-dashboard**.
Het dashboard is architectureel pijler-agnostisch opgezet zodat Fase 4 (CARE / CARE ADMIN /
ERP4HC) later een "flip-the-switch"-uitbreiding is.

De scope en structuur zijn gebaseerd op drie bronnen:

1. Het handover-document `WIP/handover-fase5a-2026-03-31.md`
2. De analyse van het HTML-referentiedashboard `WIP/dashboard_2026_04_01.html`
   (CSAT PHARMA Q1 2026 — 15 maanden data, jan 2025 t/m mrt 2026)
3. De peer review door Thomas Wyckstandt (01/04/2026) op `dashboard_2025.html` en
   `dashboard_vergelijking_25_26.html` — resultaat verwerkt in `dashboard_tendens_jul2025.html`

**T-shirt:** L
**Afhankelijkheid:** Fase 3g volledig afgerond (727 tests, 100% coverage, CI stabiel)
**Teststand bij start:** 727 tests — 100% coverage — CI stabiel (Python 3.11 / 3.12 / 3.13)

---

## 2. Deliverables

| Component | Bestand | Status |
|---|---|---|
| Streamlit app entry point | `src/dashboard/app.py` | ⬜ Leeg — te implementeren |
| Dashboard data helpers | `src/csat/core/exporters/dashboard_exporter.py` | ⬜ Leeg — te implementeren |
| Tests dashboard helpers | `tests/core/test_dashboard_exporter.py` | ⬜ Nieuw |
| i18n NL (dashboard-labels) | `src/csat/i18n/nl.json` | 🔄 Uitbreiden |
| i18n FR (dashboard-labels) | `src/csat/i18n/fr.json` | 🔄 Uitbreiden |
| Fase-document | `docs/02-tactisch/fasen/fase5a-streamlit-dashboard.md` | ✅ Dit bestand |

---

## 3. Strategische context

### 3.1 Waarom fase 5a vóór fase 4?

PHARMA is de enige volledig geïmplementeerde pijler. Fase 5a levert onmiddellijke
managementwaarde voor CEO Eric en COO Christian zonder te wachten op Fase 4.
De pijler-agnostische architectuur zorgt dat Fase 4-pijlers later eenvoudig worden
ingeschakeld via `PILLAR_REGISTRY`.

### 3.2 Referentiedashboards

**Primaire referentie:** `WIP/dashboard_2026_04_01.html` (opgesteld 01/04/2026) — CSAT-evolutie
PHARMA jan 2025 t/m mrt 2026. De kerncijfers voor Q1 2026:

| KPI | Waarde | vs volledig 2025 |
|---|---|---|
| CSAT Score Q1 2026 | **4.48★** | +1.05★ |
| Beste maand (mrt 2026) | **4.61★** / 31 resp. | Beste maand ooit |
| % Positief | **88.3%** | +32.5 ppt |
| % Negatief | **7.8%** | −27.7 ppt |
| Aaneengesloten maanden ≥ 4.0★ | **9** | jul 2025 → mrt 2026 |
| Kritieke accounts (< 2.5★) | **3** | GENT / BELOEIL / LIEGE |
| Score-KPI-targets bereikt | **3/3** | na 25% van het jaar |

**Tendensvenster referentie:** `Customer Satisfaction/dashboard_tendens_jul2025.html`
(opgesteld 01/04/2026) — actiegericht trendrapport jul 2025 → mrt 2026, zonder H1 2025-crisisruis.
Referentieontwerp voor de Tendensvenster-modus in Streamlit (zie §4.1).

---

## 4. Dashboardstructuur — sidebar + 6 tabs

### 4.1 Sidebar — twee weergave-modi

```
Sidebar
  ├─► Pijler:  [PHARMA ✅ | CARE ⏳ | CARE ADMIN ⏳ | ERP4HC ⏳]
  ├─► Modus:   [📊 Volledig (jan 2025→nu) | 📈 Tendensvenster (jul 2025→nu)]
  ├─► Periode: [baseline jaar] → [huidig jaar t/m maand]
  └─► Taal:    [NL | FR]
```

De **Tendensvenster-modus** is het directe gevolg van de Thomas Wyckstandt-review (zie handover §9.8).
Het toont enkel de actieve herstelperiode (jul 2025 → heden) zonder de H1 2025-crisisruis.
Referentieontwerp: `Customer Satisfaction/dashboard_tendens_jul2025.html`.

Gedragswijzigingen per modus:

| Element | Volledig venster | Tendensvenster |
|---|---|---|
| Tijdlijn startpunt | jan 2025 (15 mnd) | jul 2025 (9 mnd) |
| KPI-delta's | vs baseline 2025 (volledig jaar) | vs H2 2025 gemiddelde |
| Halfjaarvergelijking | H1 2025 / H2 2025 / Q1 2026 | H2 2025 / Q1 2026 |
| Rolvoortschrijdend gem. | niet zichtbaar | 3-maands gemiddelde zichtbaar |
| Primair gebruik | Jaarlijkse retrospectieve analyse | Huidig stuurinstrument |

### 4.2 Tab 1 — 🏆 Samenvatting

**Doel:** Executive overview voor management — één oogopslag

**Inhoud:**

- Highlight-box: eindoordeel kwartaal (tekst via `InsightsGenerator`)
- **8 KPI-kaarten** via `st.metric()` (zie §5)
- **ZH mini-signaalkaart** (nieuw — Thomas-feedback): 2-kolom compacte weergave
  - Links: Top 3 best (groen kader) — naam + score + badge
  - Rechts: Top 3 worst (rood kader) — naam + score + badge + "49% van neg. scores"
  - Verwijzing: "→ Zie Tab Ziekenhuizen voor volledige analyse"
- Totaalbeoordeling: verdict-cards per bevinding (checkmarks / waarschuwingen)
- Kerncijfers vergelijkingstabel: baseline vs huidig kwartaal vs vorige periode

### 4.3 Tab 2 — 📈 Tijdlijn

**Doel:** Evolutie zichtbaar maken in het geselecteerde venster

**Inhoud:**

- Combo-grafiek (Plotly): maandelijkse gemiddelde score (lijn) + volume (bar, dual y-as)
  - Volledig venster: 15 maanden, fasegebaseerde puntkleur (rood H1/groen H2/paars Q1)
  - Tendensvenster: 9 maanden, fasegebaseerde puntkleur (groen H2/paars Q1) + 3-maands rolgemiddelde
  - Referentielijn: 4.0★ (gestippeld)
- Maandoverzichtstabel: score, volume, fase-badge per maand (scrollable)
- Vergelijkingsbalk:
  - Volledig venster: H1 2025 / H2 2025 / Q1 2026 (grouped bar)
  - Tendensvenster: H2 2025 / Q1 2026 met procentuele evolutie

### 4.4 Tab 3 — 🎫 Tickets & Prioriteit

**Doel:** Issue type, prioriteit en terugkerende feedbackthema's als actie-input voor services

**Volgorde inhoud (feedbackthema's eerst — Thomas-feedback):**

1. **Feedbackthema's actiekaarten** — 4 `st.container`-blokken met kleurgecodeerde achtergrond,
   elk met: thema-naam + percentage + citaatfragment + concrete aanbevolen actie:
   - 🔴 Lange responstijden (43%) → SLA-monitoring + alerts bij 50% & 80% SLA-verbruik
   - 🟠 Incomplete oplossingen (29%) → Verplicht slotbericht + kwaliteitscheck vóór sluiting
   - 🟡 Communicatieproblemen (21%) → Standaardtemplates NL/FR + empathie-training
   - 🟡 Gebrek aan urgentie (14%) → Escalatieprotocol Critical · 4-uren reactieregel

2. **Issue type analyse** — Grouped bar-chart (Plotly): score per type (Incident/RfC/RfI) + detailtabel met % negatief + delta. Alert-box bij Incident < target: "Slotbericht + root cause verplicht".

3. **Prioriteit analyse** — Grouped bar-chart (Plotly): score per prioriteit (Blocker→Trivial) + detailtabel. Alert-box bij Trivial > 14% negatief: "Kwaliteitsreview Trivial-tickets aanbevolen".

### 4.5 Tab 4 — ⏱️ Responstijd

**Doel:** Responstijd-correlatie en de ommekeer 2025 → Q1 2026 visualiseren

**Inhoud:**

- Correlatie-panel (3 `st.container`-blokken — tekstueel):
  1. 2025: r = −0.313 — "Wachttijd is het probleem" (gem. negatief: 32 dagen)
  2. Q1 2026: positief patroon — "Kwaliteit is het probleem" (gem. negatief: < 2 dagen)
  3. Conclusie: nieuw evenwicht — SLA-monitoring uitbreiden met kwaliteitsmetingen
- Lijn-grafiek (Plotly, 2 series): gemiddelde responstijd per score-niveau (baseline gestippeld vs cumulatief)
- Detailtabel: responstijd per score-niveau + evolutie + interpretatie

### 4.6 Tab 5 — 🏥 Ziekenhuizen

**Doel:** Per-ziekenhuis prestatie en risicodetectie

**Inhoud:**

- Horizontal grouped bar-chart (Plotly): baseline vs huidig — kleurgecodeerd (groen ≥ 4.5 / rood < 2.5)
- **Top-5 tabel** met kolom "Leerpunt" (wat maakt dit ZH succesvol?)
- **Bottom-5 tabel** (uitgebreid van bottom-3 — Thomas-feedback) met kolom "Voornaamste klacht":

  | Ziekenhuis | Score | Resp. | Q1 tickets | Voornaamste klacht |
  |---|---|---|---|---|
  | LIEGE_CHR-CITADELLE | 2.00★ | 9 | +2 | Responstijden > 9 mnd · FR-support ontbreekt |
  | GENT_JANPALFIJN | 2.49★ | 88 | +1 | Langste responstijden · trekt gem. −0.27★ |
  | BELOEIL_EPICURA | 2.50★ | 38 | +3 | Incomplete oplossingen · FR-taalkloof |
  | OOSTENDE_AZ | 3.88★ | 8 | n.b. | Grenswaarde — bewaken |
  | VERVIERS_PELTZER | 4.00★ | 5 | n.b. | Laag volume — statistische grens |

  > Data-noot: bottom-5 is gebaseerd op cumulatieve periode (jan 2025–mrt 2026, 328 resp., 49 ZH).
  > LIEGE/GENT/BELOEIL zijn de enige drie ZH < 2.5★ met ≥ 5 responses in 2025 geïsoleerd.

- **Disengagement-alert** (`st.error()`): automatisch getoond bij score < 2.5★ EN < 6 Q1-tickets:
  - Naam + score + Q1-ticketvolume + aanbeveling "Proactieve outreach directie vereist"

### 4.7 Tab 6 — 🎯 KPI Targets

**Doel:** KPI-doelstellingen bewaken en bijstelling faciliteren

**Inhoud:**

- Grouped bar-chart (Plotly): baseline / target / realisatie per KPI (5 KPI's)
- Detailtabel: huidige status per KPI + badge (bereikt / in progress / onbekend)
- Bijgestelde targets-sectie: aanbevelingen voor opwaartse herziening (zie §7.2)
- Interactieve targetaanpassing (ronde 2): `st.number_input` per KPI-sleutel

---

## 5. KPI-kaarten — 8 `st.metric()` blokken

| # | Label (NL) | Berekening | Volledig venster delta | Tendensvenster delta |
|---|---|---|---|---|
| 1 | CSAT Score | `current_avg_score` | vs baseline 2025 | vs H2 2025 gem. |
| 2 | % Positief | `pct_positive` | vs baseline 2025 | vs H2 2025 gem. |
| 3 | % Negatief | `pct_negative` | vs baseline 2025 | vs H2 2025 gem. |
| 4 | Beste maand | `best_month_name + score` | — | — |
| 5 | Responses (periode) | `total_responses` | — | — |
| 6 | Maanden ≥ 4.0★ | `consecutive_months_above_4` | — | — |
| 7 | Kritieke accounts | `count(score < 2.5)` | — | — |
| 8 | Score-targets bereikt | `n_targets_met / 3` | — | — |

---

## 6. Architectuur

### 6.1 Databeschrijving

```text
SQL/CSV → DataLoader
    → EvolutionAnalyser.analyse(pillar_key="pharma")
        → EvolutionResult
            → DashboardExporter.prepare(result, window_start=...)
                → dashboard_data: dict (gecached via @st.cache_data)
                    → app.py (Streamlit rendering)
```

### 6.2 DashboardExporter — verantwoordelijkheden

`src/csat/core/exporters/dashboard_exporter.py` (leeg — te implementeren):

- `prepare(result: EvolutionResult, window_start: str | None = None) → dict`
  - `window_start=None` → Volledig venster (jan 2025 → nu)
  - `window_start="2025-07-01"` → Tendensvenster (jul 2025 → nu)
- `get_kpi_cards(data: dict) → list[KPICard]`: 8 metric-blokken met waarde + delta
- `get_timeline_data(data: dict) → DataFrame`: maandelijkse score + volume (gefilterd op window)
- `get_issue_type_data(data: dict) → DataFrame`: per issue type baseline vs huidig
- `get_priority_data(data: dict) → DataFrame`: per prioriteit baseline vs huidig
- `get_response_time_data(data: dict) → DataFrame`: responstijd per score-niveau
- `get_hospital_data(data: dict) → DataFrame`: per ZH score + delta + voornaamste klacht
- `get_target_tracking(data: dict) → DataFrame`: baseline / target / realisatie
- `detect_disengagement(data: dict) → list[dict]`: ZH onder score + ticket drempel
- `get_zh_mini_card(data: dict) → tuple[list, list]`: (top3, bottom3) voor Tab 1 mini-kaart

### 6.3 Pijler-agnostisch patroon

```python
# app.py — vereenvoudigd patroon
pillar_key   = st.sidebar.selectbox("Pijler", list(PILLAR_REGISTRY.keys()))
modus        = st.sidebar.radio("Modus", ["Volledig", "Tendensvenster"])
window_start = "2025-07-01" if modus == "Tendensvenster" else None

if pillar_key == "pharma":
    result = EvolutionAnalyser(pillar_key="pharma").analyse(...)
    data   = DashboardExporter.prepare(result, window_start=window_start)
    render_tabs(data, lang=st.session_state["lang"])
else:
    st.info(t("coming_soon", lang))
```

---

## 7. KPI-targets — huidige en aanbevolen waarden

### 7.1 Huidige targets in settings.py (fase 3g)

| KPI-sleutel | Huidig target |
|---|---|
| `avg_score_min` | ≥ 4.00★ |
| `high_critical_max` | ≤ 15.0% |
| `pct_positive_min` | ≥ 75% |
| `pct_negative_max` | ≤ 15% |
| `avg_response_days_max` | ≤ 10.0 dagen |
| `pct_with_comment_min` | ≥ 40% |
| `hospital_retention_min` | ≥ 50% |

### 7.2 Aanbevolen bijstelling na Q1 2026

| KPI-sleutel | Huidig target | Aanbevolen nieuw target | Q1 realisatie |
|---|---|---|---|
| `avg_score_min` | ≥ 4.00★ | **≥ 4.50★** | 4.48★ |
| `pct_positive_min` | ≥ 75% | **≥ 90%** | 88.3% |
| `pct_negative_max` | ≤ 15% | **≤ 5%** | 7.8% |

> **Beslissing:** Targets worden **niet** gewijzigd in `settings.py` vóór start fase 5a.
> De bijstelling is een managementbeslissing die wordt gefaciliteerd via Tab 6 (KPI Targets).

---

## 8. Nieuwe InsightsGenerator-functionaliteit

### 8.1 Correlatie-ommekeer detectie

```python
def detect_correlation_reversal(self, result: EvolutionResult) -> Finding | None:
    """Detecteert ommekeer van responstijd-correlatie (negatief → positief)."""
    baseline_corr = result.baseline_correlation_score  # al gepland (fase 3g §9.2)
    current_corr  = result.current_correlation_score   # nieuw veld
    if baseline_corr < 0 and current_corr > 0:
        return Finding(
            type="correlation_reversal",
            severity="info",
            message_key="finding_correlation_reversal",
            action_key="action_closing_quality"
        )
    return None
```

### 8.2 Disengagement-detectie

```python
def detect_disengagement(self, data: dict) -> list[dict]:
    """Detecteert ZH met chronisch lage score EN laag kwartaalvolume."""
    SCORE_THRESHOLD  = 2.5   # Instelbaar via settings.py
    TICKET_THRESHOLD = 6     # Minimum kwartaaltickets
    return [
        {"hospital": h, "score": s, "q1_tickets": t, "main_complaint": c}
        for h, s, t, c in data["hospital_details"]
        if s < SCORE_THRESHOLD and t < TICKET_THRESHOLD
    ]
```

### 8.3 ZH mini-signaalkaart data

```python
def get_zh_mini_card(self, data: dict) -> tuple[list, list]:
    """Levert (top3, bottom3) voor de mini-signaalkaart in Tab 1 Samenvatting."""
    ranked = sorted(data["hospital_summary"], key=lambda x: x["score"])
    return ranked[-3:][::-1], ranked[:3]  # top3, bottom3
```

### 8.4 Trivial-ticket bevinding versterken

Bestaande logica uitbreiden met expliciete actieaanbeveling wanneer Trivial-prioriteit
zowel de laagste score als het hoogste negatief% heeft (drempel: negatief% > 12%).

---

## 9. Acceptatiecriteria fase 5a

- [ ] Dashboard start zonder errors: `streamlit run src/dashboard/app.py`
- [ ] PHARMA-data correct geladen via SQL of CSV fallback
- [ ] Tendensvenster-toggle schakelt tijdlijn, delta's en vergelijkingsperiode correct om
- [ ] Tab 1 (Samenvatting): 8 KPI-kaarten + ZH mini-signaalkaart (top 3 / bottom 3)
- [ ] Tab 2 (Tijdlijn): 15 mnd (Volledig) of 9 mnd (Tendensvenster), correcte puntkleur
- [ ] Tab 2 (Tendensvenster): 3-maands rolgemiddelde zichtbaar
- [ ] Tab 3 (Tickets & Prioriteit): feedbackthema's actiekaarten bovenaan, dan bar-charts
- [ ] Tab 4 (Responstijd): correlatie-ommekeer-panel + lijn-grafiek
- [ ] Tab 5 (Ziekenhuizen): bottom-5 met oorzaakkolom + disengagement-alert
- [ ] Tab 6 (KPI Targets): grouped bar-chart baseline/target/realisatie
- [ ] NL/FR-toggle werkt zonder herstart
- [ ] CARE / CARE ADMIN / ERP4HC tonen "Coming soon" placeholder
- [ ] ZORGI kleurenpalet correct (via `zorgi_theme.py`)
- [ ] `dashboard_exporter.py` volledig getest — 100% coverage bewaard
- [ ] `window_start`-parameter correct doorgegeven en gefilterd in alle methoden

---

## 10. Bewust buiten scope fase 5a

| Functionaliteit | Reden | Wanneer |
|---|---|---|
| CARE / CARE ADMIN / ERP4HC data | Pijleranalysers zijn stubs | Fase 4 |
| ZORGI overall aggregatie | Vereist Fase 4 | Fase 6 |
| PDF-export vanuit dashboard | Complexiteit — ronde 2 | Ronde 2 |
| Geavanceerde ZH-filtering (klikbaar per ZH) | Complexiteit — ronde 2 | Ronde 2 |
| Interactieve target-aanpassing in settings.py | Complexiteit | Ronde 2 of fase 5b |
| FR-template voor correlatie-teksten | Ronde 2 | Ronde 2 |
| Tendensvenster met instelbare startdatum | Complexiteit | Ronde 2 |

---

## 11. Technische stack

| Tool | Versie | Doel |
|---|---|---|
| Streamlit | ≥ 1.32 | Dashboard framework |
| Plotly | ≥ 5.20 | Interactieve grafieken |
| pandas | ≥ 2.0 | Datamanipulatie |
| Python | 3.11+ | — |

```powershell
# Virtuele omgeving activeren (al aanwezig)
.venv\Scripts\Activate.ps1

# Dashboard starten
streamlit run src/dashboard/app.py
```

---

## 12. Aandachtspunten

- `dashboard_exporter.py` is leeg — dit is de **eerste** klasse die geïmplementeerd wordt
- Vermijd directe EvolutionAnalyser-aanroepen in Streamlit callbacks — altijd via `DashboardExporter` + `@st.cache_data`
- `window_start`-parameter in `prepare()` filtert de dataset vóór alle berekeningen — cache per (pillar, window_start, periode) combinatie
- Alle UI-labels via `nl.json` / `fr.json` — geen hardcoded strings in `app.py`
- De PNG van `EvolutionVisualiser` kan als tijdelijke tussenoplossing worden geëmbed
- Output-pad via `dated_output_dir()` — consistent houden met batch-runner
- ZORGI corporate proxy blokkeert pip-audit — CVE-scans via `/cve` in GHC Chat
- Correlatie-ommekeer vereist nieuw veld `current_correlation_score` in `EvolutionResult`
- Disengagement-drempelwaarden in `settings.py` opnemen (niet hardcoden)
- Feedbackthema's actiekaarten zijn **statische tekstblokken** — geen extra databerekening nodig, wel i18n-sleutels voor NL/FR

---

## 13. Referenties

| Document | Pad |
|---|---|
| Handover fase 5a (v1.2) | `WIP/handover-fase5a-2026-03-31.md` |
| Dashboard Q1 2026 (primaire ref.) | `WIP/dashboard_2026_04_01.html` |
| **Tendensvenster (referentieontwerp)** | **`Customer Satisfaction/dashboard_tendens_jul2025.html`** |
| Projectplan high-level | `docs/01-strategisch/projectplan-highlevel.md` |
| Fase 3g (context InsightsGenerator) | `docs/02-tactisch/fasen/fase3g-evolutie-rapport-verfijning.md` |
| Fase 3f (advieskader) | `docs/02-tactisch/fasen/fase3f-evolutie-advieskader.md` |
| Implementatiegids | `docs/02-tactisch/implementatie-gids.md` |
| ZORGI Design System | `docs/01-strategisch/ZORGI_Design_System.md` |
| Operations Runbook | `docs/03-operationeel/operations-runbook.md` |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
|---|---|---|---|
| 1.0 | 01/04/2026 | Initiële versie — gebaseerd op handover + analyse dashboard Q1 2026 | Danny Depecker + CD |
| 1.1 | 01/04/2026 | §1 derde referentiebron toegevoegd (Thomas-review); §3.2 tendensvenster referentie; §4.1 sidebar Tendensvenster-modus + gedragstabel; §4.2 ZH mini-signaalkaart; §4.3 feedbackthema's actiekaarten als eerste inhoud Tab 3; §4.6 bottom-5 + oorzaakkolom; §5 KPI-tabel uitgebreid met Tendensvenster-delta; §6.2 window_start param + get_zh_mini_card; §6.3 pijler-agnostisch patroon bijgewerkt; §8.3 nieuwe methode; §9 acceptatiecriteria uitgebreid; §10 scope bijgewerkt; §12 aandachtspunten bijgewerkt | Danny Depecker + CD |
