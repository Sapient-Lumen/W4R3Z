# Rev427? no, rev485: command-palette open-row unsaved file truth

Problem:
- rev482–rev484 taught palette path rows to tell much more of the truth: exact typed `Open` rows can now say `existing file`, `directory`, `current buffer`, `switch buffer`, and `drill down`.
- But one tiny trust seam still lingered for unsaved paths that were already open in a buffer.
- After `open_file(...)` created a new buffer for a missing path, the exact typed `Open` row could still collapse back to only `recent ... | current buffer` or `switch buffer`, which quietly implied disk truth Micromax did not actually have.
- Right before Enter, the palette could already know both things: the path is open as a buffer **and** the file still does not exist on disk.

What changed:
- Tightened `_command_palette_open_path_row(...)` in `src/micromax_editor/editor.py`.
- When capability-gated filesystem inspection is allowed, exact typed `Open` rows now keep disk truth even for already-open file targets:
  - `existing file` still appears for open buffers backed by a real file
  - `new file` now also appears for open buffers whose path is still missing on disk
- The same row still keeps the tiny action cue from rev484, for example:
  - `recent #1 [active] @ 1:0 | scratch.md | new file | current buffer`
  - `recent #1 [open] @ 1:0 | scratch.md | new file | switch buffer`

Why this matters:
- This is another trust/flow follow-up, not a new feature.
- Buffer truth and disk truth should not fight each other in the last decision row.
- If Micromax already knows a target is an unsaved open buffer, the palette should not silently imply that the file exists just because the buffer does.

Constraints kept:
- No new host capability.
- No new command/hostcall surface area.
- The extra `new file` cue only appears when Micromax is already allowed to inspect that target path.
