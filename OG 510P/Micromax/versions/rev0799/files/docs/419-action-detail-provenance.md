# Rev477 — action detail rows now keep best-effort source provenance

## Why

Micromax already had the right tiny exact action surface: `showaction NAME` and
`action_detail_row(NAME)` / `ed.action-detail-row` exposed one editor action's
name and doc string for humans, scripts, and future UIs. But actions still lagged
just behind the other exact inspection rows. Commands kept group/span metadata,
visible words kept definition provenance, hooks kept definition provenance, and
docs topics kept backing paths — while actions still hid where the registered
callable came from.

That made action discovery slightly less trustworthy exactly where future
humans/LLMs were deciding whether one visible action was a built-in editor
behavior, a test helper, or a plugin-owned callback.

## What changed

- `action_detail_row(NAME)` now appends a best-effort `[file line col]` source span
  when the registered action callable comes from inspectable Python source
- `showaction NAME` and `help ACTION` now print that provenance when available
- prompt rows for `showaction NAME`, generic `help NAME`, `showtopic NAME`, and
  `apropos QUERY` action results now keep that same `defined at ...` metadata
  visible during selection
- the action hostcall contract stays tiny and explicit: `[name doc [file line col]|0]`

## Result

Exact action inspection stays small, but it stops hiding source provenance Micromax
already has. If one registered action already has an inspectable Python callable
behind it, the command surface, host surface, and prompt surface can all reuse
that same tiny honest fact.
