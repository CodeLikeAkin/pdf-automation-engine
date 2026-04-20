# Design System Context: Project-Specific DNA

In this room, we manage the individual identities of our guides. We use a "Token Injection" architecture to keep the core renderer clean.

## The "MASTER.md" Pattern
Every project folder in this directory (e.g., `taming-the-silent-killer`) must contain a `MASTER.md` file.

### Required Sections in MASTER.md:
1. **CSS Variables**: A table containing `--color-primary`, `--color-accent`, etc.
2. **Typography Import**: A `css` block containing the Google Fonts `@import` or local `@font-face` rules.

## How it works
1. The **Renderer V5** extracts the `project_slug` from the Markdown metadata.
2. it searches for `design-system/[slug]/MASTER.md`.
3. If found, it injects the tokens and fonts into the HTML template.
4. If NOT found, it falls back to the default "Premium" theme.

## Best Practices
- **Isolation**: Each project should have its own folder.
- **Specifics**: Use this folder to override the global `system_v5_*.css` rules for unique branding.
