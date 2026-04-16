---
name: pdf-design
description: >
  Use this skill whenever the user wants to CREATE a visually designed PDF guide, eBook, workbook,
  business plan, brand manual, report, proposal, or any multi-page document that should look
  professional and polished. This skill defines layouts, color systems, typography, and page structures
  for high-fidelity PDF production.
---

# PDF Design Skill
## How to Produce Publication-Quality PDF Guides Autonomously

This skill defines the visual language and structural requirements for professional multi-page PDFs generated via HTML/CSS rendering (e.g., Playwright).

### CORE PIPELINE
1. **Content**: Structured Markdown (sections, headings, lists).
2. **Metadata**: Design system selection (A, B, C, or D).
3. **Rendering**: Wrap in HTML + Design System CSS -> Render to PDF.

---

## DESIGN SYSTEMS

### SYSTEM A: "Warm Editorial" (Wellness, Workbooks)
- **Colors**: Cream (`#F5F0EB`) bg, Terracotta (`#8B4A2B`) accent.
- **Typography**: Playfair Display (Headings) + Lato (Body).
- **Vibe**: Organic, wellness-focused, warm.

### SYSTEM B: "Corporate Professional" (Business Plans, Reports)
- **Colors**: White (`#FFFFFF`) bg, Deep Green/Navy (`#1B4332`) accent.
- **Typography**: Montserrat (Headings) + Source Sans Pro (Body).
- **Vibe**: Structured, trustworthy, clinical.

### SYSTEM C: "Minimal Modern" (Brand Guidelines, Strategy)
- **Colors**: Near-white (`#FAFAFA`) bg, Black (`#1A1A1A`) accent.
- **Typography**: Inter (All-caps display, regular body).
- **Vibe**: High-end, architectural, bold.

### SYSTEM D: "Classic Editorial" (How-to Guides, eBooks)
- **Colors**: White bg, Warm Taupe (`#B8A898`) accent, Charcoal text.
- **Typography**: Cormorant Garamond (Headings) + Raleway (Body).
- **Vibe**: Sophisticated, readable, traditional but fresh.

### SYSTEM V: "Vanguard" (High-End Strategy, Premium Editorial)
- **Colors**: Deep Slate Navy bg, Vibrant Gold/Amber accent.
- **Typography**: Playfair Display (Headings) + Inter (Body).
- **Vibe**: Cinematic, ultra-premium, high-fidelity (Dark Mode).

---

## PAGE LAYOUT TEMPLATES

### 1. COVER PAGE
- High-impact visual.
- Full-bleed accent color or background image.
- Large title, subtitle, and branding.

### 2. TABLE OF CONTENTS
- Clean hierarchy with page numbers.
- System-specific separators (dots, lines, or whitespace).

### 3. CHAPTER OPENERS
- Full-page or half-page accent color blocks.
- Large section numbers (e.g., "01").
- Brief introductory summary.

### 4. CONTENT PAGES
- Consistent margins (20mm recommended).
- Alternating layouts (e.g., text left/image right).
- Page numbers in footer or header band.

---

## DESIGN DECISION FRAMEWORK

| Document Type | Recommended System |
|---------------|-------------------|
| Wellness, Lifestyle, Workbooks | System A |
| Business Plans, Data Reports | System B |
| Brand Guidelines, Pitch Decks | System C |
| Educational Guides, Digital eBooks | System D |
| High-End Guides, Premium Strategy | System V |

---

## QUALITY CHECKLIST
- [ ] Cover page exists and follows the selected system.
- [ ] Table of Contents is present and accurate.
- [ ] Consistent color palette (max 3 colors).
- [ ] Typography scale is consistent across all pages.
- [ ] Page numbers are included on all content pages.
- [ ] High contrast between text and background.
