# Shared flat screen-row model (rev222)

Micromax now publishes one tiny flat `screen_rows_model(lines, cols)` snapshot plus hostcall `ed.screen-rows`.

Why it exists:
- `screen_model(...)` was already a decent whole-screen map, but many tests / scripts / future LLM handoffs really want the plainer question: **what ordered visible text rows are on screen right now?**
- answering that from `screen_model(...)` still required overlaying viewport rows, prompt-panel rows, and bottom chrome by `screen_y`
- the new model keeps that boring composition in the shared editor core instead of every caller re-implementing it slightly differently

Shape:
- `rows`: ordered row maps for each visible screen `y`
- each row carries plain `text`, `kind`, `screen_y`, width, cursor-here metadata, and a few source-specific fields
- viewport rows preserve line/start-col/continuation metadata
- prompt-panel rows preserve picker `type` / `row_kind` / `selected`
- bottom rows preserve `kind` / `slot`

Non-goals:
- this is **not** a styled render tree
- it does not try to encode syntax highlighting, search highlighting, cursorline styling, or docs-browser emphasis overlays
- the curses TUI still owns visual styling

Portability sibling:
- the JSON portability corpus now also includes `nested-catch-success-preserves-outer-visible-return-stack-value`, the success-path twin of the recent nested-throw `r@` visibility case
