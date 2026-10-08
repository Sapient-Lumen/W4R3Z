# Statusline layout model (rev213)

Micromax already had a shared `status_model()` and a deterministic reference
formatter `statusline_text(width)`, but one small piece of bottom chrome was
still private to the formatter itself:

- what are the rendered left/right segments?
- how much padding sits between them?
- which side was truncated?
- what exact single-line row did that produce?

Rev213 lifts that tiny layout policy into one shared editor helper and hostcall:

- `Editor.statusline_model(width: int) -> map`
- `ed.statusline-model` / convenience word `statusline-model`

## Returned shape

`statusline_model(width)` returns a small text-first map:

```text
{
  "active": 0|1,
  "width": n,
  "left_raw": "...",
  "right_raw": "...",
  "left": "...",
  "right": "...",
  "padding": "   ",
  "padding_width": n,
  "truncated_left": 0|1,
  "truncated_right": 0|1,
  "text": "final single-line status row"
}
```

Notes:
- `left_raw` / `right_raw` are the rendered template outputs before clipping.
- `left` / `right` are the visible post-truncation segments.
- `text` is the exact row that `statusline_text(width)` now returns.
- when `statusline=false` or `width<=0`, the model stays inactive and `text` is empty.

## Policy

The layout policy stays intentionally tiny and deterministic:

1. render `statusformatl` and `statusformatr`
2. trim surrounding whitespace from the right side
3. if the right side alone is too wide, keep its tail
4. otherwise truncate the left side first
5. fill the gap with spaces

This is the same policy Micromax was already using; rev213 just makes it
inspectable instead of hiding it inside one formatter function.

## Why this matters

This keeps the archive friendlier to future humans/LLMs and future UI work:

- tests can assert statusline layout without brittle string archaeology
- scripts can inspect visible statusline pieces directly
- future UIs can reuse or intentionally replace the tiny reference policy
- the final row text still remains available through `statusline_text(width)`

## Related docs

- `docs/69-editor-statusline-model.md`
- `docs/97-statusline.md`
- `docs/153-bottom-rows-model.md`
- `docs/31-host-api.md`
