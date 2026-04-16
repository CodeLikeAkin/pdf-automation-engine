# Scripts Context: Automation Engine

In this room, we are software engineers building the pipeline. Our goal is a "Single Command" output system.

## The Production Chain
1. **Runner**: Orchestrates the project.
2. **Researcher**: Fetches facts.
3. **Drafter**: Converts facts into Markdown.
4. **Renderer**: Transforms Markdown + Design CSS into PDF.
5. **Verifier**: Runs the "Screenshot Loop" to check for errors.
6. **Auto-Fixer**: If Verifier finds errors, return to step 4 or 2 automatically.

## Engineering Rules
- **Modularity**: One script per task (e.g., `researcher.py`, `renderer.py`).
- **Error Handling**: Always check if the `/output` folder exists before saving.
- **Independence**: The scripts should work for ANY topic passed in as an argument.
- **Aesthetics First**: The Renderer MUST pull from the `/design` folder to ensure the PDF looks premium.

## Current Priorities
- Generalize the `research_and_draft.py` to accept any topic.
- Improve the `renderer.py` to use advanced CSS (flexbox, grid) for better PDF layouts.
