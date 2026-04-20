# BACKLOG-005 — Personalisatie & Favorieten-tabblad

**Status:** Open
**Prioriteit:** Medium
**Aangemaakt:** 20/04/2026
**Auteur:** Danny Depecker + CD
**Context:** Advisory-sessie personalisatie 20/04/2026
**Geplande fase:** 5d (na Fase 5c)

---

## Achtergrond

Na hosting op een echte server wordt CSAT-Compass gedeeld met ~20 interne ZORGI-collega's
(Service Managers, management). Elke gebruiker heeft andere interessepunten en werkt vanuit
een andere pijler. Personalisatie verhoogt de dagelijkse bruikbaarheid zonder de gedeelde
datastructuur te raken.

---

## Scope

Drie samenhangende features die als één fase worden opgepakt:

1. **Gebruikersidentificatie** — e-mailadres als identifier (geen authenticatie)
2. **Profielpersistentie** — taalvoorkeur + default pijler bewaren per gebruiker
3. **Favorieten-tabblad** — persoonlijke selectie van max. 10 tegels uit bestaande tabbladen

---

## Architecturale Beslissingen

### Persistentiebackend: JSON-bestanden

Gebruikersprofielen worden opgeslagen als individuele JSON-bestanden in `data/profiles/`.

**Motivatie:**
- ~20 gebruikers = verwaarloosbare schaal (~20 bestanden van elk <2KB)
- Geen DB-migratie of tabelwijzigingen in `Lerni_DB` nodig
- Eenvoudig te debuggen, backuppen en handmatig te corrigeren
- Geen extra dependencies

**Bestandsnaamconventie:** `data/profiles/{email}.json`

**JSON-schema:**
```json
{
  "email": "danny.depecker@zorgi.be",
  "language": "nl",
  "default_pillar": "pharma",
  "favorites": [
    {"tab_id": "samenvatting", "tile_id": "T1", "pillar": "pharma", "order": 0},
    {"tab_id": "evolutie",    "tile_id": "T3", "pillar": "zorgi",  "order": 1}
  ],
  "updated_at": "2026-04-20T10:30:00"
}
```

### Authenticatie: e-mailadres als identifier

Geen wachtwoord, geen magic link. Gebruiker voert e-mailadres in bij eerste gebruik.
Sessiestatus via `st.session_state["user_email"]`.

**Motivatie:** Interne tool in vertrouwde ZORGI-omgeving. Wachtwoordbeheer creëert
onnodige friction voor ~20 collega's.

**Opmerking:** Bij page-refresh verliest Streamlit de session_state — login widget
verschijnt opnieuw. Verwacht gedrag. Cookie-persistentie via `streamlit-authenticator`
is een optie voor Fase 5e indien storend.

### Drag-and-drop volgorde

Favorieten zijn herorderbaar via drag-and-drop via `streamlit-sortables`
(wrapper rond SortableJS, native integratie met session_state).

---

## Functionele Vereisten

### Gebruikersidentificatie & profiel

1. Login widget bij opstarten indien geen actieve sessie
2. E-mailvalidatie (regex) in de widget
3. Eerste gebruik → standaardprofiel aanmaken (`language: nl`, `default_pillar: zorgi`)
4. Taalvoorkeur uit profiel vervangt de handmatige taalswitch in session_state
5. Default pijler uit profiel wordt toegepast als initiële pijlerselectie

### Favorieten-tabblad

1. Nieuw tabblad "Favorieten" in de bestaande tabbalk (positie: eerste tab)
2. Max. 10 tegels — afgedwongen met `st.toast`-melding bij overschrijding
3. Ster-icoon (☆/★) rechtsboven elke tegel in alle bestaande tabbladen
4. Drag-and-drop herordening van favorieten
5. Lege staat: onboardingboodschap met instructie
6. Render-strategie: hergebruik van bestaande `render_tile_X()`-functies
   (tegels tonen altijd actuele data, geen visuele afwijking)

---

## Nieuwe Modules

```
src/
  csat/
    user/
      __init__.py
      profile_manager.py       ← lees/schrijf/maak JSON-profielen
      favorites_manager.py     ← favorieten CRUD + volgorde
  dashboard/
    components/
      login_widget.py          ← e-mailinvoer + sessie-initialisatie
      favorites_tab.py         ← render Favorieten-tabblad
      favorite_toggle.py       ← ster-icoon component per tegel
```

### `profile_manager.py`

| Methode | Beschrijving |
|---|---|
| `load_profile(email)` | Laad profiel; maak standaardprofiel aan bij eerste gebruik |
| `save_profile(profile)` | Schrijf profiel terug (atomisch via `tempfile`) |
| `get_language(email)` | Geef taalvoorkeur terug |
| `set_language(email, lang)` | Sla taalvoorkeur op |
| `get_default_pillar(email)` | Geef default pijler terug |
| `set_default_pillar(email, pillar)` | Sla default pijler op |

### `favorites_manager.py`

| Methode | Beschrijving |
|---|---|
| `get_favorites(email)` | Geef geordende favorietenlijst terug |
| `add_favorite(email, tab_id, tile_id, pillar)` | Voeg toe (max 10) |
| `remove_favorite(email, tab_id, tile_id, pillar)` | Verwijder favoriet |
| `is_favorite(email, tab_id, tile_id, pillar)` | Bool check |
| `reorder(email, new_order)` | Sla nieuwe volgorde op |
| `is_full(email)` | Bool — 10/10 bereikt? |

`add_favorite` gooit geen exception bij vol — retourneert
`{"success": False, "reason": "max_reached"}`.

---

## Impactanalyse Bestaande Code

| Bestand | Wijziging | Impact |
|---|---|---|
| `app.py` | Login-check vóór `main()` + Favorieten-tab in tabbalk | Laag |
| `render_tile_X()` functies | `pillar` als expliciet parameter (context-agnostisch) | Medium |
| `branding.py` | Geen wijzigingen | Geen |
| `nl.json` / `fr.json` | Nieuwe i18n-sleutels (zie hieronder) | Laag |

### Nieuwe i18n-sleutels

```json
{
  "favorites_tab_label":    "Favorieten",
  "favorites_empty_message":"Nog geen favorieten. Voeg tegels toe via het ster-icoon (☆).",
  "favorites_max_reached":  "Maximum van 10 favorieten bereikt.",
  "login_title":            "Welkom bij CSAT-Compass",
  "login_email_label":      "E-mailadres",
  "login_email_placeholder":"voornaam.naam@zorgi.be",
  "login_submit_label":     "Starten",
  "login_email_invalid":    "Voer een geldig e-mailadres in.",
  "profile_language_label": "Taal",
  "profile_pillar_label":   "Standaard pijler"
}
```

---

## Dependencies

| Package | Gebruik | Al aanwezig? |
|---|---|---|
| `streamlit-sortables` ≥0.3 | Drag-and-drop in Favorieten-tab | ❌ Toevoegen aan `requirements.txt` |

Geen andere nieuwe dependencies.

---

## Datamap-uitbreiding

```
data/
  profiles/              ← nieuw te creëren
    .gitkeep
```

**`.gitignore` aanvulling:**
```
data/profiles/*.json
```

Profielen bevatten e-mailadressen — niet in git opnemen (GDPR-voorzorg).

---

## Implementatievolgorde (wanneer opgestart)

| Stap | Actie |
|---|---|
| 1 | `data/profiles/` aanmaken + `.gitignore` bijwerken |
| 2 | `profile_manager.py` + unit tests |
| 3 | `favorites_manager.py` + unit tests |
| 4 | `login_widget.py` |
| 5 | `app.py`: login-check + profiel-initialisatie |
| 6 | `nl.json` + `fr.json` uitbreiden |
| 7 | `render_tile_X()`: `pillar`-parameter expliciet maken |
| 8 | `favorite_toggle.py` |
| 9 | `favorites_tab.py` |
| 10 | `streamlit-sortables` integreren |
| 11 | Integratie- en regressietests |
| 12 | `_APP_VERSION` → `v0.6` |

GHC-prompts: één methode per prompt, nooit `render()` of gedeelde stijl-utilities aanraken.

---

## Toekomstige Uitbreidingen (buiten scope)

| Idee | Fase | Opmerking |
|---|---|---|
| Azure AD SSO | 5e | Vervangt e-mail-identifier zonder datastructuurwijziging |
| Cookie-persistentie | 5e | Via `streamlit-authenticator` cookie-modus |
| Notificatie-e-mail (maandelijkse samenvatting) | 6.x | Veld `notification_email: bool` voorzien in schema |
| Gebruikersrollen (`viewer` / `manager` / `admin`) | 6.x | Veld `role` toe te voegen aan schema |
| Profielbeheer-UI in dashboard | 5d-ext | Taal/pijler wijzigen zonder opnieuw in te loggen |

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
|---|---|---|---|
| 0.1 | 20/04/2026 | Initieel — aangemaakt vanuit advisory-sessie 20/04/2026 | Danny Depecker + CD |
