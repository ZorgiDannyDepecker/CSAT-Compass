# 📋 Plan van aanpak — PHARMA-Conventions opzetten

**Datum:** 24/03/2026
**Auteur:** Danny Depecker
**Status:** 🟢 Goedgekeurd — klaar om uit te voeren

---

## 🎯 Doel

Centrale `PHARMA-Conventions\` map opzetten als **single source of truth** voor ZORGI-brede en PHARMA-team afspraken, zodat wijzigingen nog maar op één plaats beheerd worden.

---

## 🚧 Scope & beperkingen

| Item | Beslissing |
|---|---|
| Lopende projecten | ❌ Niet aanraken in deze sessie |
| Scripting project | ❌ Bewust uitgesloten — apart opruimactie later |
| CSAT-Compass | ❌ Bewust uitgesloten — apart opruimactie later |
| Q&A-Lab | ✅ Doelproject voor sync |

---

## 🗂️ Centrale mapstructuur (doelstelling)

```
Documents\AI\PHARMA-Conventions\
├── zorgi\                          ← Laag 1: bedrijfsbreed
│   ├── zorgi_design_system.md
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
| Design System | `CSAT-Compass/docs/01-strategisch/zorgi_design_system.md` |
| project-conventies v2.3 | `CSAT-Compass/.github/instructions/project-conventies.instructions.md` |
| code-formatting v2.0 | `CSAT-Compass/.github/instructions/code-formatting.instructions.md` |
| md-style-guide v4.0 | `CSAT-Compass/.github/docs/md-style-guide.md` |

---

### Fase 2 — Mapstructuur aanmaken

Lege mappen aanmaken onder `Documents\AI\PHARMA-Conventions\`:
- `zorgi\`
- `pharma\`
- `assets\img\`
- `assets\fonts\`

---

### Fase 3 — Documenten consolideren *(schrijven naar PHARMA-Conventions)*

Elk document krijgt een versie-header (datum + herkomst) bovenaan.

| Bestand | Bron | Bestemming | Actie |
|---|---|---|---|
| `zorgi_design_system.md` | `CSAT-Compass/docs/01-strategisch/` | `zorgi\` | Kopiëren + naamsgeving bijsturen |
| `product-names.md` | Kleurregister overdracht + Design System | `zorgi\` | Nieuw aanmaken ✅ |
| `tone-of-voice.md` | Bestaande conventies als basis | `zorgi\` | Nieuw skelet ✅ |
| `project-conventies.md` | `CSAT-Compass/.github/instructions/` v2.3 | `pharma\` | Kopiëren |
| `code-formatting.md` | `CSAT-Compass/.github/instructions/` v2.0 | `pharma\` | Kopiëren |
| `md-style-guide.md` | `CSAT-Compass/.github/docs/` v4.0 | `pharma\` | Kopiëren |

---

### Fase 4 — Sync-script schrijven *(latere sessie)*

`sync-conventions.ps1` — kopieert van `PHARMA-Conventions\` naar de doelprojecten:

- ❌ `CSAT-Compass\.github\` — bewust uitgesloten
- ✅ `Q&A-Lab\.github\`
- ❌ `Scripting\.github\` — bewust uitgesloten
- ⛔ `copilot-instructions.md` per project wordt **nooit aangepast**

> 🕐 Dit script wordt in een latere sessie uitgewerkt, nadat de inhoud van `PHARMA-Conventions\` stabiel en gevalideerd is.

---

### Fase 5 — Assets *(opnemen in huidige sessie)*

Logo-assets en Poppins-fonts kopiëren naar `assets\img\` en `assets\fonts\`:

| Bron | Bestemming |
|---|---|
| `CSAT-Compass/src/static/img/heartbeat_*.png` (6 stuks) | `assets\img\` |
| `CSAT-Compass/WIP/poppins/*.ttf` | `assets\fonts\` |

---

## ✅ Beslissingen

| # | Vraag | Beslissing |
|---|---|---|
| 1 | `product-names.md` en `tone-of-voice.md` aanmaken? | ✅ Beide aanmaken |
| 2 | Fase 5 (assets) meteen mee opnemen? | ✅ Ja, in deze sessie |
| 3 | Sync-script (Fase 4) meteen schrijven? | 🕐 Latere sessie |

---

*Danny Depecker — 24/03/2026*
