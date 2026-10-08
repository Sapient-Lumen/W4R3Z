# Rev490 — command-palette parsecursor completion rows keep cursor suffixes

Problem: the command palette had just learned to keep typed `Open` rows alive for parsecursor-shaped queries like `draft.md:3:7`, `guide/:2`, and extensionless existing targets such as `guide:2`. But one small flow seam still lingered inside the same pick-before-open loop: filesystem completion still listed against the raw `path:line[:col]` text, so a partial query like `guide/i:2` collapsed to one typed `Open` row even though Micromax could already parse the target and complete `guide/intro.md`.

This was a trust/flow seam, not a new capability gap. Micromax already had the right nearby behavior:

- submit/open already reused one shared `_parse_open_target(...)` helper
- the palette already kept exact typed `Open` rows once one parsecursor-shaped query counted as path-like
- selecting one visible file completion row already flowed through the same `openpath` submit path as the typed row

The fix stays deliberately small: `_path_completion_rows(...)` now reuses `_parse_open_target(...)` before deciding which directory/prefix to list, and file completion rows preserve the typed cursor suffix on the completed candidate itself. A query like `guide/i:2` can now surface `guide/intro.md:2`, and selecting that visible completion row still opens the completed file at `2:0` instead of silently dropping back to a plain path. `_command_palette_open_path_row(...)` also now reuses parsed file targets for visible completion-row context so suffixed file candidates still benefit from the same recent/open cues as ordinary file rows.

Why this matters:

- parsecursor-shaped completion queries stop collapsing to one lonely typed `Open` row
- the visible row you pick now stays aligned with the real submit/open target, including the cursor suffix
- future humans/LLMs inspecting `ed.command-palette-rows QUERY` see the same suffixed file candidate that the live palette shows

Focused coverage lives in:

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`
