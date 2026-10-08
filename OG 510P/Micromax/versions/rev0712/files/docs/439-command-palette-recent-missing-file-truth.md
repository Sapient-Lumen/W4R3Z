Rev497 note: command-palette `Recent Files` rows now keep missing-file truth too — when a remembered recent path no longer exists on disk, the row appends `new file` so deleted recent files and unsaved open buffers stop reading like ordinary saved-file MRU entries.

# Command-palette recent-file missing-file truth (rev497)

Micromax already had two nearby honest surfaces:

- exact `recent_detail_row(PATH)` / `showrecent PATH` rows kept MRU index plus active/open/dirty/readonly/cursor state visible
- typed `Open` rows and visible `openpath` file rows already appended `new file` when one remembered path had drifted away from the filesystem

But one first-class execution seam still lagged behind that model: the palette's own `recentfile` rows still looked like ordinary saved-file entries even after the backing path had vanished. That mattered in exactly the trust-first place where humans or future LLMs decide whether Enter is a boring reopen, a risky unsaved revisit, or a deleted-path surprise.

Rev497 keeps the fix tiny:

- `_command_palette_recent_file_row(...)` now does one capability-gated missing-file check
- when the remembered recent path no longer exists on disk, the visible row appends `new file`
- this covers both deleted closed recent files and still-open unsaved buffers that already sit in MRU state

The intent is simple: if a visible `Recent Files` row would now reopen as a new-file target rather than an existing-file target, Micromax should say so before Enter.
