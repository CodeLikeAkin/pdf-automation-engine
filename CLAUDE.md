# PDF Content Factory

You are an expert Content Engineer helping with the production of premium, sellable editorial guides.

## Workspaces
- `/planning`: Topic research, chapter outlines, and audience definitions.
- `/research`: Raw topic data, verified facts, and references.
- `/drafts`: High-quality markdown drafts for chapters.
- `/design`: CSS templates, brand assets, and PDF layout logic.
- `/scripts`: Python automation scripts for research, drafting, and rendering.
- `/skills`: Rule-based experts (Humanizer, UI/UX, Visual Audit).
- `/output/[topic_name]`: Isolated project folders.
  - `/logs`: Build data and error tracking.
  - `/preview`: Screenshots and renders for verification.
  - `/final`: The verified, premium PDF.

## Production Routing Table
| Task | Go To | Read | Skills |
| :--- | :--- | :--- | :--- |
| Brainstorming | `/planning` | `CONTEXT.md` | - |
| Fact-checking | `/research` | `CONTEXT.md` | - |
| Drafting Book | `/drafts` | `CONTEXT.md` | `co-authoring`, `humanizer` |
| Style & Design | `/design` | `CONTEXT.md` | `ui-ux-pro-max` |
| Running Automation | `/scripts` | `CONTEXT.md` | - |

## Naming Conventions
- Planning: `[topic]_spec.md`
- Drafts: `[topic]_[title]_draft.md`
- Design: `[style]-template.css`
- Output: `[topic]_final_v[version].pdf`

## Operational Rules
1. Always check the `CONTEXT.md` in the target folder before starting a task.
2. Ask before creating new top-level folders.
3. Keep tokens low by only reading what is relevant to the current "Room".
