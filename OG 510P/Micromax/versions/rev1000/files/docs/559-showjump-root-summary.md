# Rev618: keep plain `showjump` truthful at the root

## Why

Micromax already had the exact and broad pieces for jumplist inspection:
- `jump_detail_row(N)` / `ed.jump-detail-row` exposed one exact visible jump slot without mutating history.
- `jump_history_rows()` / `jumps` already exposed the live jumplist register headlessly and at runtime.
- prompt completion for `showjump INDEX|#N` already reused the exact jump row once a slot token existed.

The seam was only at the entry point. Plain `showjump` previewed one current slot before Enter, but raw runtime `showjump` still jumped straight to `usage: showjump INDEX|#N` after Enter. That made the calmest exact-inspection path hide the live jumplist state it already knew at the exact moment a human or future LLM most wanted confidence.

## What changed

- added shared `_jump_inventory_preview_summary()` in the editor core
- plain `showjump` command-bar completion now uses that summary at the root
- raw runtime `showjump` now prints the same summary before its usage hint
- the summary reuses the current exact jump row, so count, slot, lane, target, position, and preview all stay aligned across prompt/runtime surfaces
- focused prompt/runtime tests pin the behavior

## Result

The root exact jumplist inspector stays usage-shaped while still telling the truth about the live jump history before it asks for one exact slot token.

## Verification

Focused coverage lives in:

- `tests/test_editor_jumppick.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
