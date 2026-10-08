# Rev489 — command-palette parsecursor extensionless existing-target open row

Problem: the command palette had just learned to keep typed `Open` rows alive for parsecursor targets like `guide/:2` and `draft.md:3:7`, but its heuristic still only trusted the parsed target when that stripped path *looked* path-like on its own. That left one small but real gap in the same pick-before-open loop: existing extensionless targets such as `guide:2` or `intro:2` could still disappear from the palette even though Micromax could already recognize the parsed target as one real directory or file.

This was a trust/flow seam, not a new feature gap. Micromax already had the right nearby behavior:

- cursor-suffixed open targets already flowed through one shared `_parse_open_target(...)` helper
- the palette already kept exact typed `Open` rows once one query counted as path-like
- directory drill-down submit and exact file/open-buffer cues had already been tightened nearby

The fix stays deliberately small: `_looks_like_path_query(...)` now gives parsecursor-shaped queries one last capability-safe chance after parsing. If the parsed target already maps to one open buffer, one exact recent file/directory row, or — under `cap.fs-list` — one existing file or directory on disk, the palette keeps the same typed `Open` row instead of dropping it.

Why this matters:

- extensionless parsecursor targets stop feeling flaky or second-class beside `guide/:2` and `draft.md:3:7`
- the visible palette row now matches the real submit/open capability Micromax already has
- future humans/LLMs inspecting `ed.command-palette-rows QUERY` see the same tiny row the live palette shows

Focused coverage lives in:

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`
