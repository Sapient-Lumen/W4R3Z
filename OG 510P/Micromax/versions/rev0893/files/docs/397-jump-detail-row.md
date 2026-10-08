# Rev455 — jumplist history gets one tiny exact detail row

## What changed

Micromax already had the right broad jumplist surfaces:

- plain `jumps` exposed the current/back/forward trail for humans
- `jump_history_rows()` / `ed.jump-history-rows` exposed that same ordered register to scripts and future UIs
- `jumppick [QUERY]` / `ed.jump-section-rows` exposed grouped browse state by `Current`, `Back`, and `Forward`

But one small inspectability seam still remained: there was still no official side-effect-free exact answer to the smaller question future humans/LLMs often ask next:

> what is true about this one jump entry right now?

Rev455 keeps the fix deliberately small:

- add `jump_detail_row(INDEX)` in the editor core
- expose it as `ed.jump-detail-row`
- add plain `showjump INDEX` for humans
- make `showjump` completion reuse that same exact metadata

## Row shape

`jump_detail_row(INDEX)` / `ed.jump-detail-row` return:

```text
[query index lane depth buffer position preview]
```

Where:

- `query` preserves the caller's requested index spelling
- `index` is the canonical 1-based jumplist entry index
- `lane` is `current`, `back`, or `forward`
- `depth` is `0` for the current row or the 1-based actionable distance on that side
- `buffer` is the owning buffer name
- `position` is the stored `line:col` cursor target
- `preview` is the trimmed source line preview already used by the flat jumplist register

## Why this matters

This keeps jumplist history coherent at three useful scales:

- flat inventory via `jumps` / `ed.jump-history-rows`
- grouped browse state via `jumppick` / `ed.jump-section-rows`
- one exact side-effect-free row via `showjump INDEX` / `jump_detail_row(INDEX)` / `ed.jump-detail-row`

That is a small trust win because scripts and future UIs no longer need to move through history just to inspect one known entry, and a small flow win because the human command path now matches the headless row exactly.
