# Rev619: keep plain `showrecent` truthful at the root

## Why

Micromax already had the exact and broad pieces for recent-file inspection:
- `recent_detail_row(PATH)` / `ed.recent-detail-row` exposed one exact recent entry without reopening it.
- `recent_detail_row_by_index(N)` already resolved the newest visible `#N` slot headlessly.
- prompt completion for `showrecent PATH|N|#N` already previewed that newest visible slot before Enter.

The seam was only at the runtime entry point. Plain `showrecent` already previewed one live MRU slot before Enter, but raw runtime `showrecent` still jumped straight to `usage: showrecent PATH|N|#N` after Enter. That made the calmest exact-inspection path hide the recent-file truth it already knew at the exact moment a human or future LLM most wanted confidence.

## What changed

- added shared `_recent_inventory_preview_summary()` in the editor core
- plain `showrecent` command-bar completion now uses that shared summary at the root
- raw runtime `showrecent` now prints the same summary before its usage hint
- the summary reuses the newest visible exact recent row so section, sample name, disk truth, and action truth stay aligned across prompt/runtime surfaces
- focused prompt/runtime tests pin the behavior

## Result

The root exact recent-file inspector stays usage-shaped while still telling the truth about the newest visible MRU entry before it asks for one exact `PATH|N|#N` token.

## Verification

Focused coverage lives in:

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
