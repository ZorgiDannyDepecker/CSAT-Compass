# ZORGI Design System & Branding Reference  

> **Golden source:** Dit bestand wordt beheerd in `PHARMA-Conventions\zorgi\`.
> **Versie overgenomen van:** `CSAT-Compass/docs/01-strategisch/zorgi_design_system.md`
> **Overgedragen op:** 24/03/2026

---

> **Purpose:** This document serves as the single source of truth for all ZORGI-branded design decisions when creating files, tools, presentations, documents, dashboards, and any other visual output. Always consult this reference to ensure brand consistency.

---

## 0. Available Brand Assets  

| Asset                        | Filename                              | Description                          |
|------------------------------|---------------------------------------|--------------------------------------|
| Heartbeat Icon (White, PNG)  | `Logo-icoon_144_x_144_px_wit.png`     | 144×144px, white on transparent, for dark backgrounds |
| ZORGI Logo (White, PNG)      | `Zorgi_wit.png`                       | Full wordmark, white — used in app topbar (`assets/img/`) |

> Place brand asset files in the same directory as this reference. When creating tools or artifacts, use relative paths to reference them.

---

## 1. Brand Identity  

- **Company Name:** ZORGI (always written in CAPITALS as a company name)
- **Tagline:** smarter care
- **Origin:** The name comes from Esperanto and means "to take care of"
- **Core Values:** Care, attention, quality, partnership, growth, innovation
- **Tone Keywords:** Empathetic, helpful, solution-oriented, transparent, personal, professional yet accessible

---

## 2. Color Palette  

### Primary Colors  

| Color Name      | HEX       | RGB             | CMYK           | Usage                                      |
|-----------------|-----------|-----------------|----------------|---------------------------------------------|
| Dark Blue       | `#003a70` | 0, 58, 112      | 100, 80, 32, 16| Primary brand color, headings (Kop 1, 4)    |
| Red             | `#dc2b26` | 220, 43, 38     | 5, 93, 91, 1   | Accent, logo gradient, highlights           |
| Purple          | `#7f4267` | 127, 66, 103    | 42, 76, 23, 31 | Logo gradient mid-tone, title bars          |

### Secondary Colors  

| Color Name      | HEX       | RGB             | CMYK           | Usage                                      |
|-----------------|-----------|-----------------|----------------|---------------------------------------------|
| Grey Blue       | `#5f8495` | 95, 132, 149    | 65, 36, 30, 12 | Headings (Kop 2), secondary text            |
| Light Blue      | `#609fce` | 96, 159, 206    | 63, 25, 5, 2   | Headings (Kop 3, 5), accents               |
| Ultra Light Blue| `#d7e7f3` | 215, 231, 243   | 12, 5, 0, 5    | Backgrounds, cards, containers              |

### Gradient  

- **Direction:** Left to right (or as overlay on images)
- **Stops:** Dark Blue (`#003a70`) → Purple (`#7f4267`) → Red (`#dc2b26`)
- **CSS:** `background: linear-gradient(to right, #003a70, #7f4267, #dc2b26);`
- **Usage:** Overlays on images, backgrounds, illustrative elements, hero sections

### Color Rules

- Use only brand colors in presentations, documents, and schemas
- The gradient can be used as overlay, background, or in illustrations
- Dark Blue is the dominant brand color for text and UI elements
- Red is used sparingly for emphasis and accents
- Ultra Light Blue is the preferred light background color

### Derived Pillar Colors

Pillar-specific colors not in the core palette are derived via mixing and documented here:

| Pillar     | Color Name   | HEX       | Derivation                                      |
|------------|--------------|-----------|------------------------------------------------|
| CARE ADMIN | Light Purple | `#a06b8a` | 60% mix: Purple `#7f4267` → Ultra Light Blue `#d7e7f3` |

---

## 3. Typography  

### Primary Font: Poppins (Google Font)  

| Style         | Weight      | Usage                                |
|---------------|-------------|--------------------------------------|
| ExtraBold     | 800         | Titles, headings, quotes, intros     |
| Light         | 300         | Body text, paragraphs               |

### Fallback Font: Verdana  

Use Verdana when Poppins is not available.

### Font Sizes (Word Documents)  

| Level       | Size    | Color          | Weight         |
|-------------|---------|----------------|----------------|
| Heading 1   | 16pt    | Dark Blue      | Poppins ExtraBold |
| Heading 2   | 14pt    | Grey Blue      | Poppins ExtraBold |
| Heading 3   | 12pt    | Light Blue     | Poppins ExtraBold |
| Heading 4   | 11pt    | Dark Blue      | Poppins ExtraBold |
| Heading 5   | 10.5pt  | Light Blue     | Poppins ExtraBold |
| Body Text   | 10.5pt  | Black          | Poppins Light     |

### Web/App Equivalents (recommended)  

| Level       | Size     | Color          | Font                  |
|-------------|----------|----------------|-----------------------|
| H1          | 2rem     | `#003a70`      | Poppins 800           |
| H2          | 1.75rem  | `#5f8495`      | Poppins 800           |
| H3          | 1.5rem   | `#609fce`      | Poppins 800           |
| H4          | 1.25rem  | `#003a70`      | Poppins 800           |
| H5          | 1.125rem | `#609fce`      | Poppins 800           |
| Body        | 1rem     | `#1a1a1a`      | Poppins 300           |

### Loading Poppins (Web)  

```html
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;800&display=swap" rel="stylesheet">
```

```css
font-family: 'Poppins', 'Verdana', sans-serif;
```

---

## 4. Logo  

### Logo Asset — Heartbeat Icon (White)  

- **File:** `Logo-icoon_144_x_144_px_wit.png`
- **Size:** 144 × 144 px
- **Variant:** White on transparent — use on dark backgrounds, Dark Blue headers, gradient overlays
- **Format:** PNG with transparency

```html
<!-- Example: header icon -->
<img src="Logo-icoon_144_x_144_px_wit.png" alt="ZORGI" width="36" height="36" />
```

### Structure  

- The logo consists of a **heartbeat icon** (gradient bars) + **"ZORGI"** wordmark + **"smarter care"** baseline
- The heartbeat icon symbolizes: progress, future-orientation, partnership, growth, and care

### Usage Rules  

| Context                              | What to Use                          |
|--------------------------------------|--------------------------------------|
| First/last page of documents         | Full logo (icon + wordmark + baseline) |
| Internal pages of documents          | Heartbeat icon only                  |
| Light backgrounds                    | Color logo                           |
| Dark/busy backgrounds                | White logo                           |
| Only when required by partners       | Black logo                           |

### Minimum Sizes  

- Full logo: **40mm** minimum width
- Heartbeat icon alone: **10mm** minimum width

### Logo Don'ts  

- Never use the color logo on dark or busy backgrounds
- Never distort or modify the logo

---

## 5. Graphic Elements  

### Dot Pattern  

- A distinctive **dot grid pattern** is used throughout communications
- Available in: **Dark Blue** and **White** only
- **Allowed modifications:** Cropping, scaling up/down
- **Not allowed:** Color changes, distortion, reshaping

### Shape Language  

- All graphic elements and image frames use **rounded corners** or are **fully rounded**
- Title bars use rounded/pill shapes (typically in Purple or Light Blue)
- Use **icons** to support visual flows and schemas

### Rounded Corners CSS Reference  

```css
/* Standard rounded corners */
border-radius: 16px;

/* Pill-shaped elements (title bars) */
border-radius: 9999px;

/* Circular elements */
border-radius: 50%;

/* Asymmetric rounded (one corner) - used on image frames */
border-radius: 0 40px 0 0;
```

---

## 6. Photography Style  

- **Focus:** People and innovation
- **Style:** Colorful, vibrant, dynamic, high-contrast
- **Lighting:** Natural light and/or soft blurs (bokeh)
- **Image frames:** Always with one or more rounded corners

---

## 7. Tone of Voice  

### Core Principle: Client-Centric  

Always put the recipient at the center, whether they are a client, partner, or colleague.

### Tone Characteristics  

| Characteristic                        | Example                                                     |
|---------------------------------------|-------------------------------------------------------------|
| Empathetic & understanding            | "We understand this is important to you..."                 |
| Helpful & solution-oriented           | "We're happy to think along with you..."                    |
| Transparent & clear                   | "To help you properly, we explain step by step..."          |
| Personal & tailored                   | "Dear [Name], we have a proposal that fits your needs..."   |
| Consistently professional, accessible | "We're here for you if you have questions..."               |

### Formality Rules  

- **External communication:** Use formal "u" (you-formal in Dutch)
- **Internal communication:** Use informal "je" (you-informal in Dutch)

### Writing Tips — Prefer Simple Language  

| Don't say                        | Say instead  |
|----------------------------------|--------------|
| Met betrekking tot / In verband met | Over         |
| Aan de hand van                  | Met          |
| Met uitzondering van             | Behalve      |
| In geval dat                     | Als          |
| In overeenstemming met           | Volgens      |

---

## 8. Product Name Spelling  

Always use these exact capitalizations:

| Product        | Spelling        | Incorrect |
|----------------|-----------------|-----------|
| Company name   | **ZORGI**       | Zorgi / zorgi |
| Care product   | **CARE**        | Care / care |
| Hospital IS    | **OAZIS**       | Oazis / oazis |
| Pharma product | **ZORGI PHARMA**| Zorgi Pharma / ZORGI pharma |
| ERP product    | **ERP4HC²·⁰**  | ERP4HC / erp4hc |

> Note: "Zorgi" (lowercase) is only used when referring to the Esperanto word origin.

---

## 9. Presentation Principles  

Six principles for good slides:

1. **One message per slide**
2. **Simplicity is key**
3. **Choose the graphic route** (use visuals over text)
4. **Contrast in your message**
5. **Show it with color**
6. **Whitespace** (leave breathing room)

---

## 10. Quick Reference — CSS Variables  

```css
:root {
  /* Primary Colors */
  --zorgi-dark-blue: #003a70;
  --zorgi-red: #dc2b26;
  --zorgi-purple: #7f4267;

  /* Secondary Colors */
  --zorgi-grey-blue: #5f8495;
  --zorgi-light-blue: #609fce;
  --zorgi-ultra-light-blue: #d7e7f3;

  /* Gradient */
  --zorgi-gradient: linear-gradient(to right, #003a70, #7f4267, #dc2b26);

  /* Typography */
  --zorgi-font-primary: 'Poppins', 'Verdana', sans-serif;
  --zorgi-font-weight-heading: 800;
  --zorgi-font-weight-body: 300;

  /* Spacing & Radius */
  --zorgi-radius-sm: 8px;
  --zorgi-radius-md: 16px;
  --zorgi-radius-lg: 24px;
  --zorgi-radius-xl: 40px;
  --zorgi-radius-pill: 9999px;
  --zorgi-radius-circle: 50%;

  /* Text Colors */
  --zorgi-text-heading-1: #003a70;
  --zorgi-text-heading-2: #5f8495;
  --zorgi-text-heading-3: #609fce;
  --zorgi-text-body: #1a1a1a;
  --zorgi-text-on-dark: #ffffff;

  /* Background */
  --zorgi-bg-light: #d7e7f3;
  --zorgi-bg-dark: #003a70;
  --zorgi-bg-white: #ffffff;
}
```

---

## 11. Quick Reference — Tailwind Utility Classes  

```text
Dark Blue:        text-[#003a70]  bg-[#003a70]  border-[#003a70]
Red:              text-[#dc2b26]  bg-[#dc2b26]  border-[#dc2b26]
Purple:           text-[#7f4267]  bg-[#7f4267]  border-[#7f4267]
Grey Blue:        text-[#5f8495]  bg-[#5f8495]  border-[#5f8495]
Light Blue:       text-[#609fce]  bg-[#609fce]  border-[#609fce]
Ultra Light Blue: text-[#d7e7f3]  bg-[#d7e7f3]  border-[#d7e7f3]

Rounded corners: rounded-2xl (16px) | rounded-3xl (24px) | rounded-full (pill/circle)
Font:            font-light (body) | font-extrabold (headings)
```

---

## 12. Design Checklist  

Before delivering any branded output, verify:

- [ ] Font is Poppins (ExtraBold for headings, Light for body) or Verdana fallback
- [ ] Only brand colors are used (no off-brand hues)
- [ ] ZORGI is written in ALL CAPS (as company name)
- [ ] Product names use correct capitalization (see section 8)
- [ ] Corners are rounded (no sharp rectangles for containers/images)
- [ ] Gradient flows Dark Blue → Purple → Red (if used)
- [ ] Logo follows usage rules (white on dark, color on light)
- [ ] Tone is empathetic, solution-oriented, and client-centric
- [ ] Simple, direct language is preferred over formal/bureaucratic phrasing
- [ ] Sufficient whitespace is maintained
- [ ] Photography (if used) is vibrant, people/innovation focused, with natural light

---

*Contact for branding support: <marcom@zorgi.be>*

---

## Versiehistorie  

| Versie | Datum | Wijzigingen | Auteur                                   |
| ------ | ---------- | ----------- |------------------------------------------|
| 1.0 | 24/03/2026 | Overgenomen van CSAT-Compass — golden source gecentraliseerd in PHARMA-Conventions | Marcom + Thijs Mestdagh + Danny Depecker |
| 1.1 | 18/04/2026 | Zorgi_wit.png toegevoegd aan asset-tabel; afgeleide pillar-kleur CARE ADMIN gedocumenteerd | CD |
