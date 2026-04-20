# Assets Context: Local Media Cache

In this room, we store the visual and typographic building blocks of the guides. The system is designed to be self-sufficient and offline-ready.

## Directory Structure
- **`/fonts`**: Contains `.woff2` files downloaded by `Renderer V5`. This ensures that even if Google Fonts is down, the PDFs render with the correct typography.
- **`/covers`**: Contains `.jpg` and `.png` files used for book covers.
    - **Contextual Fetching**: Images are auto-fetched from Unsplash based on project context if not present.
    - **Caching**: Images are saved using the `project_slug` to avoid redundant API calls.

## Asset Rules
1. **Never Manual**: Avoid manually adding fonts unless they are custom-licensed. Let the renderer handle Google Font downloads.
2. **Naming**: Cover images should follow the slug format: `project-name.jpg`.
3. **Attribution**: Every Unsplash image in `/covers` should have a corresponding `*_credit.txt` file.
