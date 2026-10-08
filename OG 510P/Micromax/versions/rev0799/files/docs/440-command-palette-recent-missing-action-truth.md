Rev498 note: command-palette `Recent Files` rows now keep missing-file action truth too — deleted closed recent files append `empty buffer @ 1:0`, while unsaved open buffers append `current buffer` / `switch buffer`, so visible MRU rows stop saying only that the path is missing and start saying what Enter will do.

# Command-palette recent-file missing action truth (rev498)

Micromax already had the nearby honest surfaces:

- `recentfile` rows now appended `new file` when one remembered path no longer existed on disk
- visible `openpath` file rows already appended tiny action cues like `current buffer`, `switch buffer`, and `empty buffer @ 1:0`
- the actual open path stayed capability-gated and headless-first

But one first-class execution seam still lagged behind that model: once a missing remembered path had been admitted back into the `Recent Files` list, the row still stopped at `new file`. That hid an important distinction right where trust matters most:

- a deleted closed recent file will reopen as one brand-new empty buffer
- an unsaved open buffer will not create anything new at all; Enter just revisits the already-open buffer

Rev498 keeps the fix tiny and local to `_command_palette_recent_file_row(...)`:

- when the remembered path is missing, reuse `_command_palette_file_action_cue(...)` to append `current buffer` or `switch buffer` if one live buffer already owns that path
- otherwise append `empty buffer @ 1:0`
- keep the existing `new file` cue so disk truth stays visible too

The intent is simple: once Micromax shows one missing-path MRU row, it should say not only that the path is gone, but also whether Enter revisits a live buffer or lands in a new empty one.
