# Design Context: Premium PDF Aesthetics

In this room, we focus on the visual quality and premium feel of the final output. We don't just "convert" text; we **design** digital experiences.

## Architecture: The "Design System"
- **Master Rules**: Each project uses a `design-system/[project-slug]/MASTER.md` file for custom tokens and fonts.
- **Renderer V5**: Automatically detects and applies these design systems based on the `project_slug`.
- **Local Assets**: All fonts are cached locally in `assets/fonts/` to ensure typography is consistent and renders perfectly without internet dependence.

## What "Premium" Looks Like
- **Typography**: High-quality Google Fonts (Inter, Playfair Display, Montserrat). Now fully cached locally.
- **Hierarchy**: Clear type scale (46pt covers, 40pt chapter headers, 9.8pt body).
- **Structure**: Dedicated full-bleed chapter openers with ghost numbering.
- **Accents**: Gold-accented strategy boxes, stylized TOC with numbered entries, and premium footers.

## The Production Chain
1. **Source**: Markdown files with metadata headers.
2. **Logic**: Renderer V5 pulls tokens from `MASTER.md`.
3. **Template**: Clean HTML/CSS architecture (`template_v5.html` + `system_v5_*.css`).
4. **Rendering**: Playwright-driven capture with `networkidle` and font-loading guarantees.

## Design Checklist
- Does the `project_slug` match the `design-system` folder name?
- Are the primary/secondary colors defined as CSS variables in `MASTER.md`?
- Is the cover blurb optimized for the target market?
