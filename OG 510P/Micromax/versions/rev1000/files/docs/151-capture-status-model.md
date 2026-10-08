# Capture status model (rev210)

Rev209 made capture keymodes like `qreplace` and `openurl` *visibly honest* in the curses TUI by showing a real one-line bottom prompt and mode-aware keymenu hints.

Rev210 takes the next small step: the editor now publishes that same capture state through the shared status model so future statuslines, UIs, scripts, tests, and LLMs do not need to scrape TUI-only strings or peer into private editor fields.

## New shared fields

`Editor.status_model()` now includes these keys when a capture keymode is active:

- `capture_kind` — active capture keymode name (`qreplace`, `openurl`)
- `capture_summary` — short question/header text
- `capture_detail` — actionable subject (`search -> replacement`, pending URL)
- `capture_progress` — compact ordinal summary when available (for example `1/2`)
- `capture_source` — origin label for `openurl` (`help`, `cursor`, `command`)
- `capture_search` / `capture_replace` — query-replace details
- `capture_url` — pending URL for `openurl`
- `capture_examined`, `capture_count`, `capture_replaced` — tiny numeric details for query-replace

When no capture mode is active, these fields fall back to empty strings / zeroes.

## Why keep this shared?

Micromax has been winning by moving small truths into shared editor-side models instead of burying them in one frontend.

This follows the same pattern as earlier shared surfaces like:

- `prompt_current_position` / `prompt_position_summary`
- `prompt_current_preview`
- `search_summary`
- `buffer_summary`

The goal is not a new prompt subsystem. It is just a tiny, inspectable snapshot of what the editor is already doing.

## TUI reuse

The curses helper `capture_prompt_text(ed, width=...)` now builds its displayed line from the shared status-model fields instead of recomputing wording from private editor internals.

That keeps one more user-visible string aligned across:

- bottom-row capture prompts
- headless `showstatus` / `ed.status-summary`
- statusline templates that want to render `$(capture_kind)` or `$(capture_progress)`
- future UIs/LLMs that want to inspect active confirmation state directly

## Example

During query-replace:

```text
status["capture_kind"]     == "qreplace"
status["capture_summary"]  == "?replace [1/2]"
status["capture_detail"]   == "one -> X"
status["capture_progress"] == "1/2"
```

During open-url confirmation from help:

```text
status["capture_kind"]    == "openurl"
status["capture_summary"] == "?open external link from help"
status["capture_detail"]  == "https://micro-editor.github.io/"
status["capture_source"]  == "help"
```

## Portability sibling

Rev210 also adds one tiny JSON portability case:

- `catch-success-hides-exception-frame-from-rdepth`

Source:

```text
[ rdepth ] catch
```

Expected stack:

```text
[0, 0]
```

This keeps Micromax's visible return-stack contract explicit for future Rust/WASM hosts: internal exception-frame bookkeeping should not leak into portable `rdepth` observations on successful protected execution.
