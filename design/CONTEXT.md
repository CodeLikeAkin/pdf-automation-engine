# Design Context: Premium PDF Aesthetics

In this room, we focus on the visual quality and premium feel of the final output. We don't just "convert" text; we **design** digital experiences.

## What "Premium" Looks Like
- **Typography**: Use high-quality Google Fonts (Inter, Playfair Display, Montserrat). Avoid browser defaults.
- **Hierarchy**: Large, bold headers with subtle letter spacing.
- **Whitespace**: Generous margins and line heights (1.6 - 1.8).
- **Accents**: Subtle dividers, blockquotes with left-border accents, and stylized page numbers.
- **Colors**: Never use pure black (#000) or pure red. Use curated palettes (e.g., Deep Charcoal #1a1a1a, Soft Slate #334155).

## The Production Chain
1. **Source**: Markdown files from `/drafts`.
2. **Logic**: Pull rules from `skills/ui-ux-pro-max.md`.
3. **Drafting**: Use Python script in `/scripts`.
4. **Template**: CSS files in this folder (`premium-main.css`).
5. **Output**: Finished file in `/output`.

## Design Checklist for Claude
- Does the font match the topic? (Playfair for Health, Inter for Tech).
- Is the line height comfortable for long reading?
- Are the images (if any) high-resolution and properly aligned?
- Is there a clear Legal Disclaimer on the first page?
