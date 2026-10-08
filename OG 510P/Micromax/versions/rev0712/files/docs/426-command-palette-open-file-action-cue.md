# Rev426? no, rev484: command-palette open-file action cue

Problem:
- rev479–rev483 made palette file and directory rows much more honest about state and target kind.
- But one tiny action seam still lagged for file targets that were already open.
- `open_file(...)` already switches to the existing buffer when the normalized path is open, yet palette `openpath` rows still only said things like `recent #1 [open] ...` or `existing file`.
- Right before Enter, the palette could already know more about what would happen than it was saying.

What changed:
- Added `_command_palette_file_action_cue(PATH)` in `src/micromax_editor/editor.py`.
- Visible file-completion rows now append one tiny action cue for already-open targets:
  - `current buffer` when the row resolves to the active buffer
  - `switch buffer` when the row resolves to another already-open buffer
- Exact typed `Open` rows append the same cue after their existing target-kind detail, for example:
  - `recent #1 [active, dirty] @ 2:1 | guide/intro.md | existing file | current buffer`
  - `recent #1 [open] @ 1:0 | guide/notes.md | switch buffer`

Why this matters:
- This is a trust/flow follow-up, not a new feature.
- The row you hit Enter on should tell the behavioral truth, not just the filesystem truth.
- When Micromax already knows a file target is open, the useful question is often not “does this path exist?” but “am I about to switch away, or stay here?”

Constraints kept:
- No new host capability.
- No new VM/editor surface area beyond one tiny formatting helper.
- The cue is only added when Micromax already knows the exact open-buffer mapping.
