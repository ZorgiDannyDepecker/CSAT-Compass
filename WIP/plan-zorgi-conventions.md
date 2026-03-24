# 📋 Plan van aanpak — ZORGI-Conventions opzetten

**Datum:** 23/03/2026
**Auteur:** Danny Depecker
**Status:** 🟡 In afwachting van goedkeuring

---

## 🎯 Doel

Centrale `ZORGI-Conventions\` map opzetten als **single source of truth** voor ZORGI-brede en PHARMA-team afspraken, zodat wijzigingen nog maar op één plaats beheerd worden.

---

## 🚧 Scope & beperkingen

| Item | Beslissing |
|---|---|
| Lopende projecten | ❌ Niet aanraken in deze sessie |
| Scripting project | ❌ Bewust uitgesloten — apart opruimactie later |
| CSAT-Compass | ✅ Doelproject voor sync |
| Q&A-Lab | ✅ Doelproject voor sync |

---

## 🗂️ Centrale mapstructuur (doelstelling)

```
Documents\AI\ZORGI-Conventions\
├── zorgi\                          ← Laag 1: bedrijfsbreed
│   ├── ZORGI_Design_System.md
│   ├── product-names.md            (nieuw)
│   └── tone-of-voice.md            (nieuw, minimaal skelet)
├── pharma\                         ← Laag 2: Danny's team
│   ├── project-conventies.md
│   ├── code-formatting.md
│   └── md-style-guide.md
└── assets\
    ├── img\                        ← heartbeat_*.png (6 stuks)
    └── fonts\                      ← Poppins-*.ttf
```

---

## 📌 Fasen

### Fase 1 — Verkenning *(lezen, geen schrijven)*

Bronbestanden inlezen om de meest actuele versies te bevestigen:

| Bestand | Locatie |
|---|---|
| Design System | `CSAT-Compass/docs/01-strategisch/ZORGI_Design_System.md` |
| project-conventies v2.3 | `CSAT-Compass/.github/instructions/project-conventies.instructions.md` |
| code-formatting v2.0 | `CSAT-Compass/.github/instructions/code-formatting.instructions.md` |
| md-style-guide v4.0 | `CSAT-Compass/.github/docs/md-style-guide.md` |

---

### Fase 2 — Mapstructuur aanmaken

Lege mappen aanmaken onder `Documents\AI\ZORGI-Conventions\`:
- `zorgi\`
- `pharma\`
- `assets\img\`
- `assets\fonts\`

---

### Fase 3 — Documenten consolideren *(schrijven naar ZORGI-Conventions)*

Elk document krijgt een versie-header (datum + herkomst) bovenaan.

| Bestand | Bron | Bestemming | Actie |
|---|---|---|---|
| `ZORGI_Design_System.md` | `CSAT-Compass/docs/01-strategisch/` | `zorgi\` | Kopiëren |
| `product-names.md` | Kleurregister overdracht + Design System | `zorgi\` | Nieuw aanmaken |
| `tone-of-voice.md` | Bestaande conventies als basis | `zorgi\` | Nieuw skelet |
| `project-conventies.md` | `CSAT-Compass/.github/instructions/` v2.3 | `pharma\` | Kopiëren |
| `code-formatting.md` | `CSAT-Compass/.github/instructions/` v2.0 | `pharma\` | Kopiëren |
| `md-style-guide.md` | `CSAT-Compass/.github/docs/` v4.0 | `pharma\` | Kopiëren |

---

### Fase 4 — Sync-script schrijven

`sync-conventions.ps1` — kopieert van `ZORGI-Conventions\` naar de doelprojecten:

- ✅ `CSAT-Compass\.github\`
- ✅ `Q&A-Lab\.github\`
- ❌ `Scripting` — bewust uitgesloten
- ⛔ `copilot-instructions.md` per project wordt **nooit aangepast**

---

### Fase 5 — Assets *(optioneel, aparte stap)*

Logo-assets en Poppins-fonts kopiëren naar `assets\img\` en `assets\fonts\`.

> ⚠️ Dit is de zwaarste stap (bestandskopieën). Doen we apart wanneer gewenst.

---

## ❓ Open vragen vóór start

| # | Vraag | Keuze |
|---|---|---|
| 1 | `product-names.md` en `tone-of-voice.md` aanmaken als skelet, of overslaan? | ⬜ Skelet aanmaken / ⬜ Overslaan |
| 2 | Fase 5 (assets) meteen mee opnemen? | ⬜ Ja / ⬜ Later |
| 3 | Sync-script (Fase 4) meteen schrijven na docs, of aparte sessie? | ⬜ Meteen / ⬜ Aparte sessie |

---

*Danny Depecker — 23/03/2026*
