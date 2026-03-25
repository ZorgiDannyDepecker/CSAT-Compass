# 🔀 Analyse copilot-instructions.md — Afwijkingen & unieke secties

**Datum:** 24/03/2026
**Auteur:** Danny Depecker
**Bron:** Q&A-Lab + Scripting + CSAT-Compass (alle drie geanalyseerd)
**Status:** 📊 Analyse — input voor PHARMA-Conventions

---

## 🟠 Secties aanwezig in sommige maar niet alle projecten

---

### 1 — Number Formatting

| Project | Aanwezig |
|---|---|
| Scripting | ✅ Aanwezig |
| CSAT-Compass | ✅ Aanwezig (licht andere voorbeeldteksten, zelfde regels) |
| Q&A-Lab | ❌ Ontbreekt |

**Aanbeveling:** ➕ Toevoegen aan `copilot-base.instructions.md` — universeel toepasbaar.
Voorbeeldteksten mogen generiek zijn (niet projectspecifiek).

---

### 2 — Git Operations — `--no-pager` regel

| Project | Aanwezig |
|---|---|
| Scripting | ✅ Aanwezig |
| CSAT-Compass | ✅ Aanwezig |
| Q&A-Lab | ❌ Ontbreekt |

**Aanbeveling:** ➕ Toevoegen aan `copilot-base.instructions.md` — universeel nuttig.

---

### 3 — Documentation Structure (3-Layer principe)

| Project | Aanwezig |
|---|---|
| Scripting | ✅ Aanwezig |
| CSAT-Compass | ✅ Aanwezig |
| Q&A-Lab | ❌ Ontbreekt |

**Principe:** Drie lagen — strategisch (WAAROM) / tactisch (HOE) / operationeel (DAGELIJKS).
Concrete bestandsnamen verschillen per project.

**Aanbeveling:** ➕ Principe toevoegen aan `pharma/project-conventies.md`.
Concrete mapinhoud blijft projectspecifiek in de eigen `copilot-instructions.md`.

---

### 4 — Versiehistorie Formatting

| Project | Aanwezig |
|---|---|
| Q&A-Lab | ✅ Aanwezig |
| Scripting | ✅ Aanwezig |
| CSAT-Compass | ❌ Ontbreekt |

**Inhoud:** Geen bold formatting in versiehistorie-tabellen — reguliere tekst voor alle cellen.

**Aanbeveling:** ➕ Toevoegen aan `copilot-base.instructions.md` + aanvullen in CSAT-Compass.

---

### 5 — File Search Preferences — extra exclusies

| Project | Extra exclusies |
|---|---|
| Q&A-Lab | Enkel de standaard 6 mappen |
| Scripting | Enkel de standaard 6 mappen |
| CSAT-Compass | ✅ `data/` (ruwe ticketingdata) + `output/` (gegenereerde rapporten) |

**Aanbeveling:** Standaard 6 mappen → basisbestand.
Projectspecifieke exclusies → eigen `copilot-instructions.md`.

---

### 6 — Security — PII & geanonimiseerde data

| Project | Aanwezig |
|---|---|
| Scripting | ✅ Basis security (geen credentials, geen patiëntdata, read-only prod) |
| CSAT-Compass | ✅ Uitgebreid: + geen PII, + werken met geanonimiseerde data, + sample datasets eerst |
| Q&A-Lab | ❌ Ontbreekt |

**Aanbeveling:** Generieke security-regels (geen credentials, geen patiëntdata) → `copilot-base.instructions.md`.
CSAT-specifieke regels (PII, geanonimiseerde ticketingdata) → CSAT `copilot-instructions.md`.

---

### 7 — Database Environment

| Project | Aanwezig |
|---|---|
| Scripting | ✅ MS SQL Server, DBHub v0.16.0, DEV/PROD databases, IP-adres |
| CSAT-Compass | ❌ Niet van toepassing |
| Q&A-Lab | ❌ Niet van toepassing |

**Aanbeveling:** 🔒 Volledig projectspecifiek — blijft in Scripting.

---

### 8 — Branding & productnamen

| Project | Aanwezig |
|---|---|
| CSAT-Compass | ✅ Uitgebreide sectie: productnamen, kleuren, tone of voice, schrijftips, design checklist |
| Scripting | ❌ Ontbreekt |
| Q&A-Lab | ❌ Ontbreekt |

**Inhoud (CSAT-Compass):**

| Product | Correcte spelling |
|---|---|
| Bedrijfsnaam | ZORGI |
| Care-product | CARE |
| Care Admin | OAZIS |
| Pharma-product | ZORGI PHARMA |
| ERP-product | ERP4HC²·⁰ |

Kleuren (6 CSS-variabelen), tone of voice (extern: u / intern: je), schrijftips eenvoudige taal,
design checklist voor GHC.

**Aanbeveling:** 🏆 Hoogste prioriteit voor centralisatie.
Kerninhoud (productnamen, kleuren, tone of voice) → `zorgi/zorgi_design_system.md` + `zorgi/product-names.md`.
Design checklist + schrijftips → `zorgi/tone-of-voice.md`.

---

### 9 — Projectspecifieke afkortingen CSAT

| Project | Aanwezig |
|---|---|
| CSAT-Compass | ✅ CSAT + SD30 |
| Scripting | ❌ Niet van toepassing |
| Q&A-Lab | ❌ Niet van toepassing |

**Aanbeveling:** 🔒 Projectspecifiek — blijft in CSAT `copilot-instructions.md`.

---

### 10 — Evolutie-template & tweetaligheid NL/FR

| Project | Aanwezig |
|---|---|
| CSAT-Compass | ✅ Beide aanwezig |
| Scripting | ❌ Niet van toepassing |
| Q&A-Lab | ❌ Niet van toepassing |

**Aanbeveling:** 🔒 Volledig projectspecifiek voor CSAT — rapport NL/FR, bestandsnaamconventie.

---

### 11 — /GIT commando (volledige implementatie)

| Project | Status |
|---|---|
| Scripting | ✅ Volledig uitgewerkt — 3 flows (direct / lint only / lint+commit) |
| CSAT-Compass | ✅ Volledig uitgewerkt — identiek aan Scripting |
| Q&A-Lab | ❌ Enkel vermeld in overzichtstabel, geen implementatie |

**Aanbeveling:** ➕ Implementatie toevoegen aan `copilot-base.instructions.md`.
Uitrol naar Q&A-Lab via het sync-script.

---

### 12 — /cve commando (volledige implementatie)

| Project | Status |
|---|---|
| CSAT-Compass | ✅ Volledig uitgewerkt — proxy-proof, batch per 20 packages, CVE-tabel |
| Q&A-Lab | ❌ Vermeld in overzichtstabel maar niet geïmplementeerd |
| Scripting | ❌ Niet aanwezig |

**Analyse:** De implementatie bevat geen CSAT-specifieke logica, paden of data.
Het is een generieke Python package CVE-scanner die:
- `pip list` uitleest (werkt in elk Python-project)
- proxy-proof werkt achter het ZORGI-netwerk (geldt voor alle projecten)
- resultaten toont in een neutrale overzichtstabel

Het commando is enkel in CSAT uitgewerkt omdat het daar als eerste nodig was.

**Aanbeveling:** ➕ Toevoegen aan `copilot-base.instructions.md` — even nuttig voor
Scripting en Q&A-Lab. Uitrol naar die projecten via het sync-script.

---

### 13 — /smd commando

| Project | Status |
|---|---|
| Scripting | ✅ Volledig uitgewerkt — Schema Monitor Diagnose met padverwijzingen |
| CSAT-Compass | ❌ Niet van toepassing |
| Q&A-Lab | ❌ Niet van toepassing |

**Aanbeveling:** 🔒 Projectspecifiek — blijft in Scripting.

---

### 14 — Document frontmatter & versieheader

| Project | Aanwezig |
|---|---|
| CSAT-Compass | ✅ `applyTo: '**/*'` frontmatter + volledige versieheader (versie, datum, status) |
| Scripting | ❌ Geen frontmatter, geen versieheader |
| Q&A-Lab | ❌ Geen frontmatter, geen versieheader |

**Aanbeveling:** ➕ CSAT-formaat is het meest volwassen — als standaard overnemen voor
alle projecten. Toevoegen aan `copilot-base.instructions.md` als template.

---

### 15 — Repository Structure

| Project | Aanwezig | Mappen |
|---|---|---|
| Scripting | ✅ | `.github/`, `docs/`, `code/`, `tools/`, `archive/` |
| CSAT-Compass | ✅ | `.github/`, `archive/`, `data/`, `docs/`, `scripts/`, `src/`, `tools/`, `output/`, `tests/`, `WIP/` |
| Q&A-Lab | ❌ | Ontbreekt |

**Aanbeveling:** 🔒 Projectspecifiek — mappenstructuur verschilt logisch per project.

---

## 🐛 Fouten & inconsistenties

---

### F1 — Workspace Purpose Scripting — copy-paste fout

| Project | Inhoud |
|---|---|
| Scripting | "Q&A and laboratory project for testing and experimenting..." ← **FOUT** |
| Q&A-Lab | "Q&A and laboratory project for testing and experimenting..." |

Scripting heeft de Workspace Purpose van Q&A-Lab gekopieerd. Scripting zou moeten verwijzen
naar Scriptorium en SQL-validatie.

**Actie:** 🐛 Corrigeren in Scripting bij volgende revisie.

---

### F2 — /GIT implementatie ontbreekt in Q&A-Lab

Q&A-Lab vermeldt `/GIT` in de overzichtstabel maar heeft geen implementatie.
Scripting én CSAT-Compass hebben identieke, volledige implementaties.

**Actie:** ➕ Implementatie kopiëren via sync-script zodra `/GIT` in `copilot-base.instructions.md` staat.

---

### F3 — Versiehistorie Formatting ontbreekt in CSAT-Compass

Q&A-Lab en Scripting hebben expliciet de regel dat versiehistorie-tabellen geen bold
formatting mogen bevatten. CSAT-Compass mist deze sectie — maar past de regel
wel toe in de eigen versiehistorie-tabel.

**Actie:** ➕ Toevoegen via sync-script zodra sectie in basisbestand staat.

---

## 📊 Overzichtstabel custom commands (alle drie projecten)

| Commando | Scripting | Q&A-Lab | CSAT-Compass | Na centralisatie |
|---|:---:|:---:|:---:|---|
| `/pdf` | ✅ | ✅ | ✅ | ✅ Reeds in alle drie |
| `/advies` | ✅ | ✅ | ✅ | ✅ Reeds in alle drie |
| `/GIT` | ✅ | ⚠️ | ✅ | ➕ Via basisbestand naar Q&A-Lab |
| `/cve` | ❌ | ❌ | ✅ | ➕ Via basisbestand naar alle drie |
| `/smd` | ✅ | ❌ | ❌ | 🔒 Blijft Scripting-specifiek |

---

## 📌 Samenvatting aanbevelingen

| Sectie | Actie | Bestemming |
|---|---|---|
| Number Formatting | ➕ Toevoegen | `copilot-base.instructions.md` |
| `--no-pager` git-regel | ➕ Toevoegen | `copilot-base.instructions.md` |
| Versiehistorie Formatting | ➕ Toevoegen | `copilot-base.instructions.md` |
| Document frontmatter + header | ➕ CSAT-formaat als standaard | `copilot-base.instructions.md` |
| Security regels (generiek) | ➕ Toevoegen | `copilot-base.instructions.md` |
| /GIT implementatie | ➕ Toevoegen + uitrol Q&A-Lab | `copilot-base.instructions.md` |
| /cve implementatie | ➕ Generaliseren + uitrol alle drie | `copilot-base.instructions.md` |
| 3-Layer docs principe | ➕ Principe toevoegen | `pharma/project-conventies.md` |
| Branding (productnamen, kleuren) | ➕ Centraliseren | `zorgi/product-names.md` + `zorgi/zorgi_design_system.md` |
| Tone of voice + schrijftips | ➕ Centraliseren | `zorgi/tone-of-voice.md` |
| Custom commands overzichtstabel | 📄 Centraal bijhouden | `pharma/custom-commands-overzicht.md` |
| Workspace Purpose Scripting | 🐛 Corrigeren | `Scripting/copilot-instructions.md` |
| DB-omgeving Scripting | 🔒 Projectspecifiek | Blijft in Scripting |
| CSAT afkortingen + NL/FR regels | 🔒 Projectspecifiek | Blijft in CSAT-Compass |
| /smd | 🔒 Projectspecifiek | Blijft in Scripting |
| Repository Structure | 🔒 Projectspecifiek | Per project apart |

---

*Danny Depecker — 24/03/2026*
