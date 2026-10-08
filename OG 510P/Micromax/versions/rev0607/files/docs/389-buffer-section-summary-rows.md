# Rev447 — buffer buckets get one tiny broad summary row

## What changed

Micromax already had strong current-buffer discovery surfaces:

- plain `buffers` exposed the active/dirty/readonly/position inventory for humans
- `ed.buffer-inventory-rows` exposed that same flat register to scripts and future UIs
- `bufferpick [QUERY]` and `ed.buffer-section-rows` exposed grouped visible buckets like `Help`, `Scratch`, project roots, and plain `Buffers`

But one small inspectability seam still remained: buffer discovery was stronger at flat full inventory and full grouped browse state than at the simpler first question future humans/LLMs often ask before drilling in:

> what broad buffer buckets are visible right now?

Rev447 keeps the fix deliberately small:

- add `buffer_section_summary_rows(QUERY)` in the editor core
- expose it as `ed.buffer-section-summary-rows`
- add plain `showbuffergroups [QUERY]` for humans

## Row shape

`buffer_section_summary_rows(QUERY)` / `ed.buffer-section-summary-rows` return:

```
[label count sample_name sample_detail]
```

Where:

- `label` is the visible buffer bucket (`Help`, `Scratch`, a project root, a parent directory, or `Buffers`)
- `count` is the number of currently visible buffers in that bucket
- `sample_name` reuses the first visible buffer name in that bucket
- `sample_detail` reuses that first row's detail text

Examples:

- `['Help', 1, 'help:guide', '1 lines']`
- `['Scratch', 2, '*scratch*', '1 lines']`
- `['/tmp/proj', 1, '/tmp/proj/file.txt', '/tmp/proj/file.txt | 1 lines']`

The shape intentionally stays tiny. Full grouped browse state still belongs to `bufferpick` / `ed.buffer-section-rows`.

## Why this matters

This is a small trust/flow improvement for Micromax's everyday navigation surface.

Future humans, scripts, and LLMs can already inspect the flat current-buffer inventory and can already open grouped browse state, but there was still no official first-stop register for the smaller broad question of what buffer buckets are visible right now. The new summary rows and plain `showbuffergroups [QUERY]` keep that answer inspectable without opening the live picker, scraping section headers, or walking every grouped row.

## Focused tests

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- recent-file sections still only expose their full grouped project/directory row shapes, not a lighter broad summary sibling
- some exact inventory surfaces still depend on plain command formatting even when the adjacent grouped/summary layers are now shared
