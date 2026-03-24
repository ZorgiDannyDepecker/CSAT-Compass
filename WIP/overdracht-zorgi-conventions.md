# 🧭 Overdracht — ZORGI-Conventions centraliseren

**Datum:** 23/03/2026
**Van:** Claude Opus 4.6 Extended sessie (Design System integratie CSAT-Compass)
**Naar:** Nieuwe conversatie — ZORGI-Conventions opzetten
**Auteur:** Danny Depecker

---

## Wat is er gebeurd

In de vorige sessie hebben we het ZORGI Design System geïntegreerd in het CSAT-Compass project. Tijdens dat werk ontdekten we een breder probleem: ZORGI-afspraken (branding, conventies, code-formatting) leven verspreid over meerdere projecten als losse kopieën die uit sync lopen.

### Afgerond in CSAT-Compass (Fase A+B+C — volledig klaar)

- **Off-brand kleuren gefixt** in `pillars.py` en `branding.py` — 5 pijlers met unieke on-brand kleuren
- **Kleurschema Optie A besloten:** ZORGI=Dark Blue, PHARMA=Light Blue, CARE=Grey Blue, OAZIS=Light Purple (#a06b8a, afgeleide), ERP4HC=Purple. Rood gereserveerd voor alarmen
- **Logo-assets** (6 bestanden) opgenomen in `src/static/img/` met `LOGO_ASSETS` dict
- **Poppins TTF** bundeling voorbereid (download-script klaar, `apply_matplotlib_theme()` geschreven)
- **Jinja2-templates** bijgewerkt met logo in rapport-header
- **ADR-010** geschreven met alle beslissingen
- **Productnamen** gecorrigeerd: ERP4HC→ERP4HC²·⁰, ZORGI PHARMA→PHARMA, ZORGI CARE→CARE
- **Tests:** kleurvalidatie, cross-check pillars↔branding, logo-paden, brand guard, matplotlib

### Nog te doen: Poppins fonts downloaden

```powershell
# Run vanuit CSAT-Compass projectroot:
.\WIP\download-poppins.ps1
```
[23/03/2026 - DDP] done — fonts gedownload, in `WIP/poppins/` geplaatst. Klaar om te bundelen en in `assets/fonts/` te zetten.

---

## Het probleem dat we willen oplossen

### Huidige situatie — afspraken verspreid

| Document | CSAT-Compass | Scripting | Q&A-Lab |
|---|---|---|---|
| `md-style-guide.md` | v4.0 | v3.0 | v3.0 |
| `project-conventies.md` | v2.3 (nieuw formaat) | ouder formaat | ouder formaat |
| `code-formatting.md` | v2.0 | ouder formaat | ouder formaat |
| `ZORGI_Design_System.md` | ✅ aanwezig | ❌ ontbreekt | ❌ ontbreekt |
| Logo-assets | ✅ in src/static/img/ | ❌ ontbreekt | ❌ ontbreekt |
| Poppins fonts | ✅ voorbereid | ❌ ontbreekt | ❌ ontbreekt |

**Kernprobleem:** Eén wijziging vereist aanpassing in 3+ projecten. Versies lopen uit sync.

### Drie lagen van afspraken

| Laag | Bereik | Inhoud | Huidige locatie |
|---|---|---|---|
| **1 — ZORGI-breed** | Heel het bedrijf | Design System, productnamen, tone of voice | Nergens centraal |
| **2 — ZORGI PHARMA team** | Danny's projecten | project-conventies, code-formatting, md-style-guide | Gekopieerd per project |
| **3 — Per project** | Eén project | copilot-instructions.md, ADRs | In elk project apart (correct) |

### Beslissing: React niet opnemen

De ZORGI React Components Library (`@infohos/react-components` v0.1.6) is geanalyseerd via Storybook-export (2800 regels, opgeslagen in `Templates_Icons/react-storybook-docs.md`). Conclusie: **niet opnemen** — te afwijkend van het marcom Design System (Open Sans vs Poppins, apart kleurensysteem). React is een ander team, eigen Storybook als bron.

---

## Voorstel voor de nieuwe sessie

### Centrale mapstructuur

```
Documents\AI\ZORGI-Conventions\
├── zorgi/                          ← Laag 1: bedrijfsbreed
│   ├── ZORGI_Design_System.md      ← kleuren, fonts, logo-regels
│   ├── product-names.md            ← ZORGI, PHARMA, CARE, OAZIS, ERP4HC²·⁰
│   └── tone-of-voice.md            ← taalregels, NL/FR formaliteit
├── pharma/                         ← Laag 2: Danny's team
│   ├── project-conventies.md       ← één versie, niet drie
│   ├── code-formatting.md
│   └── md-style-guide.md
├── assets/                         ← Gedeelde bestanden
│   ├── img/                        ← heartbeat_*.png (6 stuks)
│   └── fonts/                      ← Poppins-*.ttf
└── sync-conventions.ps1            ← Kopieert naar elk project
```

### Wat het sync-script doet

- Kopieert `zorgi/*.md` + `pharma/*.md` → `.github/docs/` en `.github/instructions/` per project
- Kopieert `assets/` → `src/static/` per project (waar van toepassing)
- Raakt `copilot-instructions.md` per project **niet aan** — die is projectspecifiek
- Eén commando, alle projecten up-to-date

### Doelprojecten

| Project | Pad | Heeft `.github/` |
|---|---|---|
| CSAT-Compass | `Documents\AI\CSAT-Compass` | ✅ `.github/docs/` + `.github/instructions/` |
| Scripting | `Documents\AI\Scripting` | ✅ `.github/docs/` + `.github/instructions/` |
| Q&A-Lab | `Documents\AI\Q&A-Lab` | ✅ `.github/docs/` + `.github/instructions/` |

[23/03/2026 - DDP] 
Aandachtpunt: Scripting gaan we niet bijsturen. 
Ik zou in eerste instantie dit willen uitwerken in CSAT en daarna in Q&A-Lab, maar Scripting laten zoals het is. 
We kunnen altijd later nog een keer een opruimactie doen in Scripting als we dat willen.

---

## Relevante bestanden

### Bronnen voor de centrale map

| Bestand | Locatie | Rol |
|---|---|---|
| Design System (meest actueel) | `CSAT-Compass/docs/01-strategisch/ZORGI_Design_System.md` | Golden source voor kleuren, fonts, logo |
| Logo-assets (6 stuks) | `CSAT-Compass/src/static/img/heartbeat_*.png` | Gedeelde visuele assets |
| Logo-bronnen (13 stuks) | `Documents\AI\Templates_Icons/` | Originele bestanden |
| Poppins fonts | Nog te downloaden via `CSAT-Compass/WIP/download-poppins.ps1` | Gedeelde font-assets |
| project-conventies (nieuwste) | `CSAT-Compass/.github/instructions/project-conventies.instructions.md` v2.3 | Basis voor pharma/ |
| code-formatting (nieuwste) | `CSAT-Compass/.github/instructions/code-formatting.instructions.md` v2.0 | Basis voor pharma/ |
| md-style-guide (nieuwste) | `CSAT-Compass/.github/docs/md-style-guide.md` v4.0 | Basis voor pharma/ |
| React Storybook export | `Templates_Icons/react-storybook-docs.md` | Referentie — NIET opnemen |

### Voorstel-documenten uit vorige sessie

| Bestand | Locatie |
|---|---|
| Voorstel Design System v4 (definitief) | `voorstel-design-system-integratie-v4.md` (in output vorige sessie) |
| GHC-review | `CSAT-Compass/WIP/advisor-design-system-integratie.md` |
| GHC Fase A instructie | `CSAT-Compass/WIP/instructie-ghc-fase-a.md` |

---

## Kleurregister (besloten)

### Pijlerkleuren

| Pijler | Kleur | HEX |
|---|---|---|
| ZORGI | Dark Blue | `#003a70` |
| PHARMA | Light Blue | `#609fce` |
| CARE | Grey Blue | `#5f8495` |
| OAZIS (CARE ADMIN) | Light Purple | `#a06b8a` |
| ERP4HC²·⁰ | Purple | `#7f4267` |

### Reserveringen

| Kleur | HEX | Gereserveerd voor |
|---|---|---|
| Red | `#dc2b26` | Alleen trend-down, alarmen, waarschuwingen |
| Groen (extern) | `#00aa44` | trend-up (functioneel nodig, niet in ZORGI-palet) |

### Afgeleide

| Kleur | HEX | Afleiding |
|---|---|---|
| Light Purple | `#a06b8a` | 60%-punt gradient Purple→Ultra Light Blue |

---

## Gevraagd aan Claude in de nieuwe sessie

1. **Centrale `ZORGI-Conventions/` map opzetten** met de drie submappen (zorgi/, pharma/, assets/)
2. **Inhoud consolideren** — de nieuwste versie van elk document als basis nemen
3. **`sync-conventions.ps1`** schrijven dat naar de drie projecten kopieert
4. **Verouderde kopieën opruimen** — de oude versies in Scripting en Q&A-Lab vervangen

---

*Danny Depecker — 23/03/2026*
