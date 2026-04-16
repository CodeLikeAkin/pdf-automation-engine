# Project Context & Design Philosophy

## Core Mission
To produce premium, editorial-grade digital guides that feel like high-end physical books. The system must prioritize visual excellence, sophisticated typography, and intuitive layouts.

## Design Principles (V5+)
1. **Adaptive Aesthetics**: 
   - Every new topic must have a distinct "feel" and color DNA.
   - Avoid rigidity. Do not default to the same "Warm Taupe & Gold" for every guide.
   - Use intuition to select color palettes that match the subject matter (e.g., Green/Terracotta for Health, Deep Blue for Professionalism).
2. **Creative Flexibility**:
   - The V5 structure (Cover, TOC, Openers) is the foundation, but the creative execution within that structure should evolve.
   - Balance creativity with the technical stability of the bug fixes already implemented (Visual hierarchy, TOC logic, full-bleed openers).
3. **No Placeholders**: 
   - All assets should be high-fidelity. Use AI-generated images and curated palettes to maintain a premium feel.

## Technical Guardrails
- **Zero Inline CSS**: All styling must live in standalone CSS files within `/design`.
- **Clean Architecture**: Python handles data extraction; Playwright handles visual rendering.
- **Preserve Bug Fixes**: Any creative iterations must maintain the 10 core design fixes established in Renderer V5 (Type scale, no orphans, proper chapter segmentation).

## Content Strategy
- **Nigerian Context**: For culturally specific guides, prioritize local ingredients, terminology, and social nuances (e.g., Owambes, local superfoods).
- **Author Personas**: Match the tone to the persona (e.g., Dr. Olumide Balogun for medical guides).
