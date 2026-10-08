Rev499 note: command-palette `Recent Files` rows now keep live-buffer action truth for existing files too — active/open MRU rows append `current buffer` / `switch buffer`, so first-class recent-file picks stop exposing only state and start saying what Enter will do.

# Command-palette recent-file live action truth (rev499)

Micromax already had the nearby honest surfaces:

- `recentfile` rows already reused exact MRU metadata like recency, active/open state, dirty/readonly flags, and current cursor position
- missing remembered paths already appended `new file`, and missing-path MRU rows now also appended `current buffer` / `switch buffer` or `empty buffer @ 1:0`
- adjacent `openpath` file rows already appended tiny action cues like `current buffer` and `switch buffer` for live existing files

But one first-class execution seam still lagged behind that model: once an existing path had been admitted into the `Recent Files` list, the row still stopped at `[active]` or `[open]`. That kept the state visible, but it still hid one important distinction right where trust and flow matter most:

- an active recent file does not really open anything new; Enter just revisits the current buffer
- a non-active open recent file does not perform a full reopen either; Enter switches to one already-live buffer

Rev499 keeps the fix tiny and local to `_command_palette_recent_file_row(...)`:

- reuse `_command_palette_file_action_cue(...)` for existing recent-file targets too, not just missing remembered paths
- append `current buffer` for the active live buffer and `switch buffer` for another already-open live buffer
- keep the stronger missing-file behavior from rev498 unchanged, including `empty buffer @ 1:0` when no live buffer exists

The intent is simple: once Micromax shows one first-class MRU row, it should say not only what state that target is in, but also whether Enter revisits the current buffer or switches to another live one.
