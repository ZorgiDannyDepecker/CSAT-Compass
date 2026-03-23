# CSAT-Compass - Advisor: Design System integratie v3

**Versie:** 1.0  
**Laatst bijgewerkt:** 23/03/2026  

**Doel:** Technische review van voorstel-design-system-integratie-v3.md — bevestigingen, correcties en nieuwe bevindingen op basis van codebase-analyse  
**Type:** Reference  
**Auteur:** GHC  
**Status:** Draft  

**Bestandsnaam:** advisor-design-system-integratie.md  
**Path:** WIP/  

> Beoordeeld voorstel: `voorstel-design-system-integratie-v3.md` (23/03/2026, Danny Depecker + Claude)  
> Codebase geverifieerd op: 23/03/2026

---

## Inhoudsopgave

1. [Bevestigde bevindingen](#1-bevestigde-bevindingen)
2. [Correcties op het voorstel](#2-correcties-op-het-voorstel)
3. [Nieuwe bevindingen — niet vermeld in voorstel](#3-nieuwe-bevindingen--niet-vermeld-in-voorstel)
4. [Impact per actiepunt](#4-impact-per-actiepunt)
5. [Aanbevolen aanpak](#5-aanbevolen-aanpak)

---

## 1. Bevestigde bevindingen

De volgende analyses in het voorstel zijn correct en bevestigd na codebase-inspectie:

| Bevinding | Locatie | Status voorstel |
|---|---|---|
| 5 off-brand kleuren in `pillars.py` | `src/csat/config/pillars.py` | ✅ Correct — `#003366`, `#0066CC`, `#00AA44`, `#FF6600`, `#9900CC` alle bevestigd |
| `zorgi-report.css` volledig conform | `src/static/zorgi-report.css` | ✅ Correct — alle CSS-variabelen, headers, gradients en tabellen zijn on-brand |
| `ZORGI_Design_System.md` niet in repo | `docs/01-strategisch/` | ✅ Correct — bestand ontbreekt |
| Geen `src/static/fonts/` directory | `src/static/` | ✅ Correct — enkel `zorgi-report.css` aanwezig |
| Geen `src/static/img/` directory | `src/static/` | ✅ Correct — lege map, geen logo-assets |
| ADR-010 is de juiste nummering | `docs/01-strategisch/architectuur-beslissingen.md` | ✅ Correct — laatste ADR is ADR-009 |
| `trend-up` gebruikt `#00aa44` (extern groen) | `branding.py` en `zorgi-report.css` | ✅ Correct — functioneel noodzakelijk, buiten ZORGI-palet |
| Rood gereserveerd voor `trend-down` | `branding.py` L.139 en `zorgi-report.css` L.213 | ✅ Correct — consistent in beide bestanden |

---

## 2. Correcties op het voorstel

### 2.1 🔴 Kritiek — `PILLAR_COLORS` in `branding.py` is ook off-brand

Het voorstel classificeert `branding.py` als "✅ Goed — kleuren kloppen met Design System".
Dit klopt **niet**. Na inspectie van de werkelijke inhoud (`branding.py` L.28–34):

```python
PILLAR_COLORS: dict[str, str] = {
    "zorgi":      "#003a70",  # ✅ correct
    "pharma":     "#003a70",  # ❌ kopie van zorgi — zou #609fce moeten zijn
    "care":       "#609fce",  # ❌ verwisseld — zou #5f8495 moeten zijn
    "care_admin": "#5f8495",  # ❌ zou #a06b8a moeten zijn
    "erp4hc":     "#7f4267",  # ✅ correct
}
```

Dit betekent:

- `pharma` en `zorgi` delen dezelfde kleur → **ononderscheidbaar in multi-pijler grafieken**
- `PILLAR_COLORWAY` bevat een duplicaat: `["#003a70", "#003a70", "#609fce", "#5f8495", "#7f4267"]`
- Acties A3 en A4 zijn dus **groter in scope** dan het voorstel aangeeft — niet enkel uitbreiden maar corrigeren

### 2.2 🟡 Inconsistentie — `.streamlit/config.toml` bestaat niet

Het voorstel beschrijft deze als "✅ OK — minimaal maar correct".
Het bestand is **nergens aanwezig in de repository** (ook niet als leeg bestand).
Streamlit draait zonder enige themaconfiguratie. Actie B3 moet dit meenemen.

### 2.3 🟡 Scopefout — `app.py` is volledig leeg

Het voorstel (§ Fase B3) spreekt van "~5 regels" toevoegen voor `st.logo()` en `st.set_page_config`.
`src/dashboard/app.py` is een **leeg bestand** — er is geen bestaande app om regels aan toe te voegen.
De werkelijke scope van B3 omvat het opzetten van de volledige Streamlit-structuur,
niet enkel het toevoegen van logo-calls.

Zelfde situatie voor `dashboard_exporter.py` en `matrix_exporter.py` — beide leeg.

### 2.4 🟡 Scopefout — Logo in PDF vereist wél template-aanpassing

Het voorstel stelt in §5 ("Wat NIET nodig is"):

> "Jinja2-templates aanpassen — Templates zijn taalgericht, niet visueel — CSS doet het werk"

Dit is **incorrect** voor de logo-integratie in de rapport-header (B4).
De huidige `rapport-nl.md.j2` template (L.1–27) is pure Markdown zonder HTML-elementen.
Een `<img>` tag voor het logo vereist wél een aanpassing aan de templates, **en** een aanpassing in
`report_exporter.py` om het logo-pad door te geven aan de Jinja2-context.

### 2.5 🟡 Framing — Matplotlib is niet "versterken" maar "nieuw bouwen"

Het voorstel beschrijft `apply_matplotlib_theme()` (B2) als versterking van bestaande grafieken.
Matplotlib wordt **nergens in de huidige codebase gebruikt** — geen enkel `.py` bestand
importeert of roept matplotlib aan, ondanks dat het in `requirements.txt` staat (voor fase 3-4).
B2 is geen uitbreiding van iets bestaands, maar de eerste matplotlib-integratie in het project.
Scope en prioriteit kunnen heroverwogen worden.

---

## 3. Nieuwe bevindingen — niet vermeld in voorstel

### 3.1 🔴 Branding — `erp4hc.name` mist superscript

In `pillars.py` L.54–63:

```python
"erp4hc": {
    "name":    "ERP4HC",       # ❌ mist superscript
    "name_fr": "ERP4HC",       # ❌ mist superscript
    "report_name":    "ERP4HC²·⁰",  # ✅ correct
    "report_name_fr": "ERP4HC²·⁰",  # ✅ correct
}
```

`name` en `name_fr` worden gebruikt in interne logging en pijler-sleuteldisplay.
Conform de branding-tabel is de correcte schrijfwijze overal `ERP4HC²·⁰`.
Dit is een kleine maar consistente branding-afwijking.

### 3.2 🔴 Testdekking — Kleurwaarden niet gevalideerd in tests

`tests/config/test_pillars.py` L.23 controleert dat de `color`-sleutel aanwezig is,
maar valideert de **waarde** niet:

```python
verplicht = {"name", "name_fr", "direction", "color", "products"}
```

De 5 off-brand kleuren in `pillars.py` passeren de volledige testsuite onopgemerkt.
Acties A7 en A8 zijn terecht, maar er ontbreekt ook een test die de kleuren in `pillars.py`
vergelijkt met de waarden in `PILLAR_COLORS` (of met het toegestane palet).

### 3.3 🟡 Kleur — `PLOTLY_LAYOUT.colorway` gebruikt rood als grafiekkleur

In `branding.py` L.50–57:

```python
"colorway": [
    COLORS["dark_blue"],
    COLORS["light_blue"],
    COLORS["grey_blue"],
    COLORS["purple"],
    COLORS["red"],     # ← rood als 5e grafiekleur
],
```

Dit staat haaks op de beslissing in §3.1 en §7 van het voorstel, waarbij rood
**uitsluitend** gereserveerd blijft voor trend-down, alarmen en KPI-waarschuwingen.
Na implementatie van de correcte `PILLAR_COLORWAY` (A4) zou `PLOTLY_LAYOUT.colorway`
bijgewerkt moeten worden zodat het de pijlerkleuren volgt (inclusief `#a06b8a`)
in plaats van rood als fallback te gebruiken.

### 3.4 🟢 Vraagteken — `report_name` voor CARE is "ZORGI CARE"

In `pillars.py` L.35–44:

```python
"care": {
    "report_name":    "ZORGI CARE",
    "report_name_fr": "ZORGI CARE",
}
```

"ZORGI CARE" staat niet in de branding-tabel — het product heet officieel `CARE`.
Het voorstel vermeldt dit niet. Vraag voor Danny: is "ZORGI CARE" een bewuste
keuze voor de rapporten of een onbedoelde afwijking van de branding-tabel?

---

## 4. Impact per actiepunt

Bijgestelde inschatting per actiepunt op basis van de werkelijke codebase:

| # | Actie | Scope in voorstel | Bijgestelde scope | Opmerking |
|---|---|---|---|---|
| A2 | `pillars.py` kleuren | 🔧 5 regels | 🔧 5 regels | ✅ Juist ingeschat |
| A3 | `PILLAR_COLORS` aligneren | 🔧 Klein | 🔧 Klein + corrigeren | Pharma/Care verwisseld — niet alleen uitbreiden |
| A4 | `PILLAR_COLORWAY` bijwerken | 🔧 1 regel | 🔧 1 regel | ✅ Juist — maar volgorde moet ook kloppen |
| A5 | Logo-assets kopiëren | 📋 Kopiëren | 📋 Kopiëren | ✅ Juist ingeschat |
| A6 | `LOGO_ASSETS` dict | 🔧 ~12 regels | 🔧 ~12 regels | ✅ Juist ingeschat |
| A7 | Kleurentest | 🧪 1 test | 🧪 2 tests | Extra: vergelijk `pillars.py` ↔ `PILLAR_COLORS` |
| A8 | Logo-paden test | 🧪 1 test | 🧪 1 test | ✅ Juist ingeschat |
| B2 | `apply_matplotlib_theme()` | 🔧 ~40 regels | 🔧 ~40 regels (nieuw) | Geen bestaande basis — volledig nieuw |
| B3 | Logo Streamlit | 🔧 ~5 regels | 🔧 M+ | `app.py` is leeg — volledige app-structuur nodig |
| B4 | Logo PDF rapport-header | 🔧 ~10 regels | 🔧 ~20 regels | Vereist ook template-aanpassing |
| C1 | ADR-010 | 📝 Nieuw ADR | 📝 Nieuw ADR + §3.3 | Voeg `PLOTLY_LAYOUT` colorway-beslissing toe |

---

## 5. Aanbevolen aanpak

### 5.1 Volgorde handhaven — Fase A heeft prioriteit

De volgorde in het voorstel (A → B → C) is correct. Fase A lost de "single source of truth"
op voor alle toekomstige output en kan volledig worden uitgevoerd zonder dat andere
onderdelen functioneel zijn.

### 5.2 Splits B3 van de overige B-acties

B3 (logo in Streamlit) is afhankelijk van een werkende `app.py`. Behandel B3 als een
**aparte taak** die hoort bij de Streamlit-fase (fase 5 in de roadmap), niet bij de
branding-sprint.

### 5.3 Voeg twee extra acties toe aan Fase A

| # | Extra actie | Bestand | Effort |
|---|---|---|---|
| A9 | Fix `PLOTLY_LAYOUT.colorway` — vervang rood door `#a06b8a` als 5e kleur | `src/csat/utils/branding.py` | 🔧 1 regel |
| A10 | Fix `erp4hc.name` en `erp4hc.name_fr` naar `ERP4HC²·⁰` | `src/csat/config/pillars.py` | 🔧 2 regels |

### 5.4 Bevestiging vragen voor §3.4

Klaren voor rapport-generatie met de nieuwe branding: is `report_name` "ZORGI CARE"
intentioneel of moet dit "CARE" zijn conform de branding-tabel?

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | --------------- | ------ |
| 1.0 | 23/03/2026 | Initiële review op basis van codebase-analyse vs voorstel v3 | GHC |

