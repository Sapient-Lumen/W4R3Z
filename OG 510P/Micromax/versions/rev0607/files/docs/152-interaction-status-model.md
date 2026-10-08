# Shared interaction status model (rev211)

Rev209 made capture keymodes like `qreplace` and `openurl` show an honest bottom-row prompt in the minimal curses TUI. Rev210 made capture state inspectable through `status_model()`.

Rev211 takes the same idea one small step further: the editor now publishes one tiny unified bottom-row interaction snapshot for *ordinary prompts* and *capture keymodes* alike.

## New shared fields

`Editor.status_model()` now also includes:

- `interaction_active` — `1` when an ordinary prompt or capture keymode owns the bottom row
- `interaction_kind` — prompt/capture kind such as `command`, `find`, `palette`, `qreplace`, `openurl`
- `interaction_prefix` — the tiny visible prompt prefix (`:`, `/`, `?`)
- `interaction_summary` — the compact prompt/capture head text
- `interaction_detail` — the current preview/detail payload when one exists
- `interaction_position` — compact ordinal/search progress such as `1/3` or `2/9 • Commands 2/6`
- `interaction_line` — the full single-line bottom-row prompt/capture text before width clipping

## Why keep this shared?

Micromax has been winning by moving tiny editor truths into shared headless models instead of burying them in one frontend.

Before rev211, future UIs or LLMs could inspect many ingredients of the active prompt/capture surface, but still had to *reconstruct* the visible line from scattered fields such as:

- `prompt_kind` / `prompt_text`
- `prompt_position_summary`
- `prompt_current_preview`
- `search_summary`
- `capture_summary` / `capture_detail`

Now the editor itself publishes the final tiny interaction summary it already means to show.

## Example

During a command palette session:

```text
status["interaction_kind"]     == "palette"
status["interaction_summary"]  == ":status"
status["interaction_position"] == "1/4 • Commands 1/4"
status["interaction_detail"]   == "Commands: showstatus — show portable statusline summary"
status["interaction_line"]     == ":status  [1/4 • Commands 1/4]  | Commands: showstatus — show portable statusline summary"
```

During query-replace:

```text
status["interaction_kind"]     == "qreplace"
status["interaction_summary"]  == "?replace [1/2]"
status["interaction_position"] == "1/2"
status["interaction_detail"]   == "one -> X"
status["interaction_line"]     == "?replace [1/2]  | one -> X"
```

## TUI reuse

The minimal curses renderer now reuses `status_model()["interaction_line"]` for both ordinary prompts and capture keymodes.

That keeps one more visible bottom-row string aligned across:

- live prompt rendering
- live capture rendering
- `showstatus` / `ed.status-summary`
- statusline templates via ordinary status fields
- future UIs/scripts/LLMs that want to inspect active prompt/capture state directly

## Portability sibling

Rev211 also adds one tiny JSON portability case:

- `catch-success-counts-only-user-return-stack-items`

Source:

```text
[ 7 >r rdepth r> ] catch
```

Expected stack:

```text
[1, 7, 0]
```

This keeps Micromax's visible return-stack contract explicit for future Rust/WASM hosts: when protected execution succeeds, visible `rdepth` should count only user-pushed `>r` items, not hidden exception-frame bookkeeping.
