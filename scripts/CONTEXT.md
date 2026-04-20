# Scripts Context: Automation Engine

In this room, we are software engineers building the pipeline. Our goal is a "Single Command" output system.

## The Production Chain
1. **Runner**: Orchestrates the project.
2. **Researcher**: Fetches facts.
3. **Drafter**: Converts facts into Markdown with metadata headers.
4. **Renderer (V5)**: Transforms Markdown + Design CSS into PDF with advanced features.
5. **Verifier**: Runs the "Screenshot Loop" to check for errors.

## Engineering Rules
- **Modularity**: One script per task (e.g., `renderer_v5.py`).
- **Resilience**:
    - **Font Caching**: Downloads Google Fonts locally to `assets/fonts/` for offline reliability.
    - **Cover Caching**: Checks `assets/covers/` using `project_slug` before fetching from Unsplash.
- **Smart Waits**: Replaces hardcoded timeouts with `document.fonts.ready` and `networkidle` listeners.
- **Validation**: Strict metadata validation ensures project slugs and themes are correctly formatted.
- **Logging**: Detailed path logging for design system (`MASTER.md`) discovery.

## Current Priorities
- Standardize all project workflows to use `Renderer V5`.
- Ensure all new drafts include proper metadata headers.
- Optimize the Unsplash fallback logic for faster image retrieval.
