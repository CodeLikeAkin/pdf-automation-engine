# Skill: Visual Audit (The Screenshot Loop)
**Objective**: Critically evaluate the final output to ensure zero errors and premium aesthetics.

## Reasoning Rules for the "Eyes"
1. **Layout Integrity**: Scan for "Widows" (single words at the end of a block) and "Orphans" (single lines at the top of a page). Fix them by adjusting margins.
2. **Text Clipping**: Ensure no headers or images cross the page boundaries.
3. **Typography Consistency**: Check that all fonts loaded correctly. If a page defaults to 'Times New Roman' or 'Arial', the CSS link is broken.
4. **Emotional Resonance**: Look at the cover. Does it feel like a "Premium Product"? If it's too busy or the colors are off, trigger an Auto-Fix.
5. **Legibility**: Are call-out boxes clearly separated from the body text?

## Auto-Fix Triggers
- **Trigger**: "Text Overflow" -> **Fix**: Decrease font size or increase body margin.
- **Trigger**: "Low Contrast" -> **Fix**: Darken the secondary text colors in CSS.
- **Trigger**: "Robotic Layout" -> **Fix**: Inject a new "Call-Out" block or pullquote.
