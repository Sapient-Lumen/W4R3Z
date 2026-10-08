# Rev488 — command-palette parsecursor relative-file open row

Problem: the command palette already knew how to *submit* relative parsecursor file targets like `draft.md:3:7`, but its path heuristic only looked at the raw query text. That meant the exact typed `Open` row could disappear entirely for one small but real editing loop: typing a relative filename plus cursor suffix from inside the palette.

This was a flow/trust seam, not a new feature gap. Micromax already had the right nearby behavior:

- `open draft.md:3:7` already parsed and opened correctly when `set parsecursor true`
- typed `Open` rows already kept exact file/directory/new-file context once the query counted as path-like
- recent/open buffer cues and directory drill-down cues were already being tightened nearby

The fix stays deliberately small: `_looks_like_path_query(...)` now gives parsecursor-shaped queries one extra chance by reusing `_parse_open_target(...)` before deciding whether the query is path-like. If the parsed target is obviously path-like (for example `draft.md`), the palette keeps the same exact typed `Open` row instead of dropping it.

Why this matters:

- the visible palette row now matches the submit/open capability Micromax already had
- relative parsecursor file opens stop feeling flaky or special-cased
- future humans/LLMs inspecting `ed.command-palette-rows QUERY` see the same row the live palette shows

Focused coverage lives in:

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`
