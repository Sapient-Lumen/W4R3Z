# Rev494 — command-palette parsecursor partial extensionless completion

Problem: rev489 taught exact extensionless parsecursor targets like `guide:2` and `intro:2` to keep the typed `Open` row, while rev490/rev493 taught explicit partial path queries like `guide/i:2` and `guide/s:2` to keep visible completion rows. But one adjacent current-directory seam still lingered in the same pick-before-open loop. Queries like `gu:2` and `intr:2` could still disappear entirely, even though Micromax already had enough capability-gated filesystem information to list `guide/` or `intro` as visible completion candidates from the current directory.

Why it matters:
- the palette felt inconsistent right where trust matters most: explicit partial paths stayed visible, but partial extensionless names in the current directory still vanished
- submit/open already understood the same parsecursor suffix through one shared helper, so the gap lived only in the "should I show path rows at all?" gate
- future humans/LLMs reading `commandpick` behavior need one small explicit note explaining why completion-aware path detection is still capability-gated rather than globally permissive

What changed:
- added `_parse_path_completion_query(...)` as one tiny shared helper for parsecursor-aware query splitting
- `_looks_like_path_query(...)` now gives parsecursor-shaped queries one extra capability-gated completion-aware check: if the parsed target itself is not already enough evidence, Micromax asks whether the parsed target's parent directory contains any matching child candidate
- `_path_completion_rows(...)` now reuses that same helper, so the heuristic and the visible completion rows stay aligned

Examples:
- `gu:2` can now surface `guide/:2` with `drill down`
- `intr:2` can now surface `intro:2` with `cursor 2:0`
- selecting those rows still drills down or opens at the same landed target as before

Tests:
- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
