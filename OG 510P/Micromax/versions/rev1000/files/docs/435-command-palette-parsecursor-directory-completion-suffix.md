# Rev493 — command-palette parsecursor directory completion suffix

Problem: rev490 taught parsecursor-shaped partial file queries to keep visible completion rows like `guide/intro.md:2`, but one adjacent directory-side seam still lingered in the same pick-before-open loop. A query like `guide/s:2` could already keep the exact typed `Open` row and submit/open already knew how to parse the target, yet the visible directory completion candidate still rendered only as `guide/sub/`. That dropped the typed `:2` suffix from the visible row, which meant the candidate could fall out of the ranked result set even though selecting it would still drill down successfully.

This was a flow seam, not a new capability gap. Micromax already had the important nearby behavior:

- `_parse_open_target(...)` already treated `guide/sub/:2` as the directory `guide/sub/` plus one parsed cursor request
- rev486 already made typed directory rows behaviorally honest by keeping `directory | drill down` aligned with submit
- `_path_completion_rows(...)` already preserved the typed suffix for file candidates, so parsecursor-shaped file completion rows stayed visible

The fix stays deliberately small: `_path_completion_rows(...)` now preserves the typed parsecursor suffix on visible directory candidates too. That means a partial directory query like `guide/s:2` can surface `guide/sub/:2` as one visible completion row, while the info column still says `PARENT | drill down` so Micromax does not pretend the cursor suffix means anything inside a directory.

Why this matters:

- partial directory drill-down queries stop losing their visible completion rows right before Enter
- visible row text stays aligned with the parsed submit target instead of silently dropping part of what the user typed
- future humans/LLMs inspecting `ed.command-palette-rows QUERY` see the same parsecursor continuity for directory completion rows that file completion rows already had

Focused coverage lives in:

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`
