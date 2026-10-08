# Rev492 — command-palette parsecursor new-file empty-buffer landing cue

Problem: rev491 taught parsecursor-shaped existing-file targets that were not already open to append a tiny `cursor line:col` request cue, and already-open buffer targets already kept the stronger exact `goto line:col` cue. But one adjacent action-honesty seam still lingered for genuinely missing file targets: a query like `draft.md:3:7` still rendered only `new file | PARENT` even though Micromax already knew that opening a brand-new empty buffer must land at `1:0`.

This was a trust/flow seam, not a new capability gap. Micromax already had the right nearby behavior:

- submit/open already reused one shared `_parse_open_target(...)` helper
- already-open unsaved paths already kept honest `new file` filesystem truth
- opening one brand-new file already created an empty buffer whose clamped landing was exactly `1:0`

The fix stays deliberately small: `_command_palette_new_file_landing_cue(...)` now lets the exact typed `Open` row append a tiny `empty buffer @ 1:0` cue for parsecursor-shaped new-file targets when no live buffer exists. Existing-file targets that are not already open still keep the softer `cursor line:col` request cue instead, and already-open buffers still keep the exact `goto line:col` form.

Why this matters:

- parsecursor-shaped new-file rows stop going visually silent about the real post-open landing
- the visible row now tells the truth about what Enter will do for one brand-new file without pretending Micromax can honor the typed line/column in a file that does not exist yet
- future humans/LLMs inspecting `ed.command-palette-rows QUERY` see the same tiny distinction between exact empty-buffer landings, requested existing-file cursor motion, and exact live-buffer motion

Focused coverage lives in:

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`
