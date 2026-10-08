# Rev491 — command-palette parsecursor existing-file cursor request cue

Problem: rev487 taught parsecursor-shaped file targets that already mapped to one live buffer to append an exact `goto line:col` cue, and rev490 taught parsecursor-shaped partial queries like `guide/i:2` to keep visible file completion rows such as `guide/intro.md:2`. But one adjacent action-honesty seam still lingered for existing files that were *not* already open: the row text kept the typed `:line[:col]` suffix while the info column still said only `existing file | PARENT`, so the last visible decision row went quiet about the cursor request right before Enter.

This was a trust/flow seam, not a new capability gap. Micromax already had the right nearby behavior:

- submit/open already reused one shared `_parse_open_target(...)` helper
- the palette already preserved the typed cursor suffix on visible file completion rows
- already-open buffer targets already had the stronger exact `goto line:col` cue

The fix stays deliberately small: `_command_palette_open_cursor_request_cue(...)` now lets visible file completion rows and exact typed `Open` rows append a tiny `cursor line:col` cue when the target is one existing file but not one already-open buffer. Already-open buffers still keep the exact `goto line:col` form, so Micromax only claims precision when it can clamp against the live buffer itself.

Why this matters:

- existing-file parsecursor rows stop going visually silent about the typed cursor request
- the visible row now says a little more about what Enter will try to do, without pretending the landing is exact when Micromax has not opened the file yet
- future humans/LLMs inspecting `ed.command-palette-rows QUERY` see the same tiny distinction between requested cursor motion and exact live-buffer motion

Focused coverage lives in:

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`
