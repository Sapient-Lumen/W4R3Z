# Rev495 — command-palette parsecursor known-path completion

Problem: rev490/rev493/rev494 taught the command palette to keep parsecursor-shaped filesystem completions visible, but one adjacent editor-state seam still lingered. Queries like `scr:2` could still disappear entirely when the matching target was an already-open unsaved buffer or another recent path Micromax already knew, because the palette only treated filesystem children as completion evidence.

Why it matters:
- the palette felt less trustworthy for live editor state than for on-disk state, even though switching back to an unsaved buffer is one of the safest, most common editing loops
- submit/open already understood the same parsecursor target once fully spelled, so the gap lived only in the path-like heuristic and the visible completion candidate list
- future humans/LLMs reading this archive need one explicit note that capability-gated filesystem completion can still be supplemented by already-known editor-owned path state without widening the host boundary

What changed:
- added `_path_completion_base_prefix(...)` so path-like detection and visible completion rows share one tiny base/prefix split
- added `_known_path_completion_candidates(...)` so partial path queries can reuse already-known open-buffer and recent-path state from the same parent directory
- `_looks_like_path_query(...)` now treats parsecursor-shaped queries as path-like when one such known candidate exists beside the resolved parent directory
- `_path_completion_rows(...)` now appends those known candidates after real filesystem hits while avoiding duplicates

Examples:
- `scr:2` can now surface `scratch.md:2` for an unsaved open buffer
- that row still shows the same exact buffer truth Micromax already knew, such as `current buffer | goto 1:0`
- selecting the row still lands on the already-open buffer instead of inventing a new file target

Tests:
- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
