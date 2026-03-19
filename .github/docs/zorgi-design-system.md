# ZORGI - Design System & Branding Reference

**Versie:** 1.0  
**Laatst bijgewerkt:** 19/03/2026  

**Doel:** Single source of truth voor alle ZORGI-branded design beslissingen  
**Type:** Reference  
**Auteur:** Danny Depecker  
**Status:** Approved  

**Bestandsnaam:** zorgi-design-system.md  
**Path:** .github/docs/  

> Origineel ontvangen als `ZORGI_Design_System.md` — hernoemd conform ZORGI PHARMA bestandsnaamconventie (kebab-case).  
> Brandingvragen: <marcom@zorgi.be>

---

## Inhoudsopgave

1. [Brand identity](#1-brand-identity)
2. [Kleurenpalet](#2-kleurenpalet)
3. [Typografie](#3-typografie)
4. [Logo](#4-logo)
5. [Grafische elementen](#5-grafische-elementen)
6. [Fotografie stijl](#6-fotografie-stijl)
7. [Tone of voice](#7-tone-of-voice)
8. [Productnamen spelling](#8-productnamen-spelling)
9. [Presentatieprincipes](#9-presentatieprincipes)
10. [CSS variabelen (web/app)](#10-css-variabelen-webapp)
11. [Tailwind utility classes](#11-tailwind-utility-classes)
12. [Design checklist](#12-design-checklist)

---

## 0. Beschikbare brand assets

| Asset | Bestandsnaam | Beschrijving |
|---|---|---|
| Heartbeat Icon (wit, PNG) | `Logo-icoon_144_x_144_px_wit.png` | 144×144px, wit op transparant — voor donkere achtergronden |

> Plaats brand asset bestanden in dezelfde map als dit referentiedocument.

---

## 1. Brand identity

- **Bedrijfsnaam:** ZORGI (altijd in HOOFDLETTERS als bedrijfsnaam)
- **Tagline:** smarter care
- **Oorsprong:** De naam komt uit het Esperanto en betekent "zorgen voor"
- **Kernwaarden:** Zorg, aandacht, kwaliteit, partnerschap, groei, innovatie
- **Toon sleutelwoorden:** Empathisch, behulpzaam, oplossingsgericht, transparant, persoonlijk, professioneel maar toegankelijk

---

## 2. Kleurenpalet

### Primaire kleuren

| Kleur | HEX | RGB | CMYK | Gebruik |
|---|---|---|---|---|
| Dark Blue | `#003a70` | 0, 58, 112 | 100, 80, 32, 16 | Primaire brandkleur, koppen (H1, H4) |
| Red | `#dc2b26` | 220, 43, 38 | 5, 93, 91, 1 | Accent, logo gradient, highlights |
| Purple | `#7f4267` | 127, 66, 103 | 42, 76, 23, 31 | Logo gradient middentoon, titelbalk |

### Secundaire kleuren

| Kleur | HEX | RGB | CMYK | Gebruik |
|---|---|---|---|---|
| Grey Blue | `#5f8495` | 95, 132, 149 | 65, 36, 30, 12 | Koppen (H2), secundaire tekst |
| Light Blue | `#609fce` | 96, 159, 206 | 63, 25, 5, 2 | Koppen (H3, H5), accenten |
| Ultra Light Blue | `#d7e7f3` | 215, 231, 243 | 12, 5, 0, 5 | Achtergronden, kaarten, containers |

### Gradient

- **Richting:** Links naar rechts (of als overlay op afbeeldingen)
- **Stops:** Dark Blue (`#003a70`) → Purple (`#7f4267`) → Red (`#dc2b26`)
- **CSS:** `background: linear-gradient(to right, #003a70, #7f4267, #dc2b26);`
- **Gebruik:** Overlays op afbeeldingen, achtergronden, illustratieve elementen, hero-secties

### Kleurregels

- Gebruik uitsluitend brandkleuren in presentaties, documenten en schema's
- De gradient kan worden gebruikt als overlay, achtergrond of in illustraties
- Dark Blue is de dominante brandkleur voor tekst en UI-elementen
- Red wordt spaarzaam gebruikt voor nadruk en accenten
- Ultra Light Blue is de aanbevolen lichte achtergrondkleur

---

## 3. Typografie

### Primair lettertype: Poppins (Google Font)

| Stijl | Gewicht | Gebruik |
|---|---|---|
| ExtraBold | 800 | Titels, koppen, citaten, intro's |
| Light | 300 | Bodytekst, alinea's |

### Fallback lettertype: Verdana

Gebruik Verdana wanneer Poppins niet beschikbaar is.

### Lettergroottes (Word-documenten / PDF)

| Niveau | Grootte | Kleur | Gewicht |
|---|---|---|---|
| Kop 1 / H1 | 16pt | Dark Blue `#003a70` | Poppins ExtraBold |
| Kop 2 / H2 | 14pt | Grey Blue `#5f8495` | Poppins ExtraBold |
| Kop 3 / H3 | 12pt | Light Blue `#609fce` | Poppins ExtraBold |
| Kop 4 / H4 | 11pt | Dark Blue `#003a70` | Poppins ExtraBold |
| Kop 5 / H5 | 10,5pt | Light Blue `#609fce` | Poppins ExtraBold |
| Bodytekst | 10,5pt | Zwart `#1a1a1a` | Poppins Light |

### Web/App equivalenten

| Niveau | Grootte | Kleur | Font |
|---|---|---|---|
| H1 | 2rem | `#003a70` | Poppins 800 |
| H2 | 1,75rem | `#5f8495` | Poppins 800 |
| H3 | 1,5rem | `#609fce` | Poppins 800 |
| H4 | 1,25rem | `#003a70` | Poppins 800 |
| H5 | 1,125rem | `#609fce` | Poppins 800 |
| Body | 1rem | `#1a1a1a` | Poppins 300 |

---

## 4. Logo

### Logo asset — Heartbeat Icon (wit)

- **Bestand:** `Logo-icoon_144_x_144_px_wit.png`
- **Afmeting:** 144 × 144 px
- **Variant:** Wit op transparant — gebruik op donkere achtergronden, Dark Blue headers, gradient overlays
- **Formaat:** PNG met transparantie

### Gebruiksregels

| Context | Wat te gebruiken |
|---|---|
| Eerste/laatste pagina van documenten | Volledig logo (icoon + woordmerk + baseline) |
| Interne pagina's van documenten | Alleen heartbeat-icoon |
| Lichte achtergronden | Kleurenlogo |
| Donkere/drukke achtergronden | Wit logo |
| Alleen bij partnersvereiste | Zwart logo |

### Minimale afmetingen

- Volledig logo: minimaal **40mm** breedte
- Heartbeat-icoon alleen: minimaal **10mm** breedte

### Logo verboden

- Gebruik het kleurenlogo nooit op donkere of drukke achtergronden
- Vervormen of aanpassen van het logo is niet toegestaan

---

## 5. Grafische elementen

### Stippelpatroon

- Een kenmerkend **stippelraster** wordt doorheen alle communicatie gebruikt
- Beschikbaar in: **Dark Blue** en **Wit** only
- Toegestaan: Bijsnijden, schaal aanpassen
- Niet toegestaan: Kleurwijzigingen, vervorming, hervorming

### Vormentaal

- Alle grafische elementen en afbeeldingskaders gebruiken **afgeronde hoeken** of zijn **volledig rond**
- Titelbalken gebruiken afgeronde/pill-vormen (typisch in Purple of Light Blue)

### Afgeronde hoeken — CSS referentie

```css
/* Standaard afgeronde hoeken */
border-radius: 16px;

/* Pill-vorm (titelbalken) */
border-radius: 9999px;

/* Cirkelvorm */
border-radius: 50%;

/* Asymmetrisch afgerond (afbeeldingskaders) */
border-radius: 0 40px 0 0;
```

---

## 6. Fotografie stijl

- **Focus:** Mensen en innovatie
- **Stijl:** Kleurrijk, levendig, dynamisch, hoog contrast
- **Belichting:** Natuurlijk licht en/of zachte blur (bokeh)
- **Afbeeldingskaders:** Altijd met één of meer afgeronde hoeken

---

## 7. Tone of voice

### Kernprincipe: klantgericht

Plaats altijd de ontvanger centraal, of het nu een klant, partner of collega is.

### Toonkenmerken

| Kenmerk | Voorbeeld |
|---|---|
| Empathisch en begripvol | "We begrijpen dat dit belangrijk voor u is..." |
| Behulpzaam en oplossingsgericht | "We denken graag met u mee..." |
| Transparant en duidelijk | "Om u goed te helpen, leggen we stap voor stap uit..." |
| Persoonlijk en op maat | "Beste [Naam], we hebben een voorstel dat bij uw noden past..." |
| Consistent professioneel, toegankelijk | "We staan voor u klaar als u vragen heeft..." |

### Formaliteitsregels

- **Externe communicatie:** Formeel "u"
- **Interne communicatie:** Informeel "je"

### Schrijftips — eenvoudige taal

| Niet zeggen | Zeg in de plaats |
|---|---|
| Met betrekking tot / In verband met | Over |
| Aan de hand van | Met |
| Met uitzondering van | Behalve |
| In geval dat | Als |
| In overeenstemming met | Volgens |

---

## 8. Productnamen spelling

Gebruik altijd deze exacte schrijfwijzen:

| Product | Spelling |
|---|---|
| Bedrijfsnaam | **ZORGI** |
| Care-product | **CARE** |
| Ziekenhuis IS | **OAZIS** |
| Pharma-product | **ZORGI PHARMA** |
| ERP-product | **ERP4HC²·⁰** |

> Opmerking: "Zorgi" (kleine letter) wordt alleen gebruikt bij verwijzing naar de Esperanto-woordoorsprong.

---

## 9. Presentatieprincipes

Zes principes voor goede slides:

1. **Één boodschap per slide**
2. **Eenvoud is de sleutel**
3. **Kies de grafische weg** (gebruik visuals boven tekst)
4. **Contrast in je boodschap**
5. **Toon het met kleur**
6. **Witruimte** (laat ademruimte)

---

## 10. CSS variabelen (web/app)

```css
:root {
  /* Primaire kleuren */
  --zorgi-dark-blue:        #003a70;
  --zorgi-red:              #dc2b26;
  --zorgi-purple:           #7f4267;

  /* Secundaire kleuren */
  --zorgi-grey-blue:        #5f8495;
  --zorgi-light-blue:       #609fce;
  --zorgi-ultra-light-blue: #d7e7f3;

  /* Gradient */
  --zorgi-gradient: linear-gradient(to right, #003a70, #7f4267, #dc2b26);

  /* Typografie */
  --zorgi-font-primary:        'Poppins', 'Verdana', sans-serif;
  --zorgi-font-weight-heading: 800;
  --zorgi-font-weight-body:    300;

  /* Spacing & radius */
  --zorgi-radius-sm:     8px;
  --zorgi-radius-md:     16px;
  --zorgi-radius-lg:     24px;
  --zorgi-radius-xl:     40px;
  --zorgi-radius-pill:   9999px;
  --zorgi-radius-circle: 50%;

  /* Tekstkleuren */
  --zorgi-text-heading-1: #003a70;
  --zorgi-text-heading-2: #5f8495;
  --zorgi-text-heading-3: #609fce;
  --zorgi-text-body:      #1a1a1a;
  --zorgi-text-on-dark:   #ffffff;

  /* Achtergronden */
  --zorgi-bg-light: #d7e7f3;
  --zorgi-bg-dark:  #003a70;
  --zorgi-bg-white: #ffffff;
}
```

---

## 11. Tailwind utility classes

Bij gebruik van Tailwind CSS in React-artifacts:

```text
Dark Blue:        text-[#003a70]  bg-[#003a70]  border-[#003a70]
Red:              text-[#dc2b26]  bg-[#dc2b26]  border-[#dc2b26]
Purple:           text-[#7f4267]  bg-[#7f4267]  border-[#7f4267]
Grey Blue:        text-[#5f8495]  bg-[#5f8495]  border-[#5f8495]
Light Blue:       text-[#609fce]  bg-[#609fce]  border-[#609fce]
Ultra Light Blue: text-[#d7e7f3]  bg-[#d7e7f3]  border-[#d7e7f3]

Afgeronde hoeken: rounded-2xl (16px) | rounded-3xl (24px) | rounded-full (pill/circle)
Font:             font-light (body) | font-extrabold (headings)
```

---

## 12. Design checklist

Voor elk branded output, verifieer:

- [ ] Font is Poppins (ExtraBold voor koppen, Light voor body) of Verdana fallback
- [ ] Uitsluitend brandkleuren gebruikt (geen off-brand tinten)
- [ ] ZORGI is geschreven in HOOFDLETTERS (als bedrijfsnaam)
- [ ] Productnamen gebruiken correcte schrijfwijze
- [ ] Hoeken zijn afgerond (geen scherpe rechthoeken voor containers/afbeeldingen)
- [ ] Gradient loopt Dark Blue → Purple → Red (indien gebruikt)
- [ ] Logo volgt gebruiksregels (wit op donker, kleur op licht)
- [ ] Toon is empathisch, oplossingsgericht en klantgericht
- [ ] Eenvoudige, directe taal verkozen boven formeel/bureaucratisch taalgebruik
- [ ] Voldoende witruimte bewaard
- [ ] Fotografie (indien gebruikt) is levendig, mensen/innovatie gefocust, met natuurlijk licht

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ---------------------------------------------------- | -------------- |
| 1.0 | 19/03/2026 | Initiële versie — ontvangen van ZORGI marcom, hernoemd naar kebab-case, NL vertaling headers | Danny Depecker |
