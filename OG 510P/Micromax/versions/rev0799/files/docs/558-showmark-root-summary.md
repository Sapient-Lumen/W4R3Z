# Rev617: keep plain `showmark` truthful at the root

## Why

Micromax already had the exact and broad pieces for mark inspection:
- `mark_detail_row(NAME)` / `ed.mark-detail-row` exposed one exact mark without jumping.
- `mark_inventory_rows()` / `marks` exposed the live register headlessly.
- prompt completion for `showmark NAME` already reused the exact mark row once a name existed.

The seam was only at the entry point. Plain `showmark` still fell back to generic command text before Enter, and raw runtime `showmark` still jumped straight to `usage: showmark NAME` after Enter. That made the calmest inspection path hide the live mark state it already knew.

## What changed

- added shared `_mark_inventory_preview_summary()` in the editor core
- plain `showmark` command-bar completion now uses that summary at the root
- raw runtime `showmark` now prints the same summary before its usage hint
- the summary prefers a `[here]` mark first, then an active-buffer mark, so the most relevant navigation anchor stays visible
- focused prompt/runtime tests pin the behavior

## Result

The root exact mark inspector stays usage-shaped while still telling the truth about the live mark set before it asks for one exact mark name.
