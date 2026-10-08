# Statusline strings (rev73)

Micromax-editor exposes a structured `status_model()` for scripts/tests, and a small reference
formatter `statusline_text(width)` used by the minimal TUI.

This is inspired by micro’s split status format idea (left/right format strings with directives
like `$(filename)`, `$(line)`, `$(col)`, and `$(opt:filetype)`), while keeping Micromax’s default
formatter extremely small for now.

## `status_model()` additions

The status model already had most structural fields. We added a few portable “statusline staples”:

- `encoding`: currently always `"utf-8"` (the editor reads/writes UTF‑8 today)
- `fileformat`: currently always `"unix"` (LF)
- `percentage`: 0..100 based on the primary cursor line and the total line count
- `cursor_summary`: `"N/M"` for primary cursor index + cursor count
- `selection_summary`: selection count string

These are meant to be **stable, scriptable primitives** so future UIs don’t need to re-derive them.

## `statusline_text(width)`

`statusline_text(width)` formats a micro-esque single line with a left filename section and a
right “token” section that includes:

- `ft:<filetype>`
- `enc:<encoding>`
- `unix` (fileformat)
- cursor position and percentage
- cursor/selection counts
- mode and one-shot keymode hints
- macro recording/playback flags

If the line is too narrow, the formatter truncates the left side first; if even the right side
doesn’t fit, it shows the **end** of the right side (keeping mode/key hints visible).

## Future direction

As of **rev72**, Micromax-editor exposes micro-esque `statusformatl`/`statusformatr` templating.

## `statusformatl` / `statusformatr`

These are simple format strings where directives are embedded as `$()` expressions.

Examples:

- `$(filename)$(modified)$(readonly)`
- `ft:$(opt:filetype) $(position)$(cur)$(sel) $(percentage)% $(mode)$(keymode)$(macro)`

Escape a literal `$` as `$$`.

## Hostcall helpers

For scripts/plugins that want to reuse the same renderer:

- `ed.statusfmt` ( template -- s ) render a statusformat template against the current `status_model()`
- `ed.statusline-text` ( width -- s ) render the full statusline string for a given width

### Supported directives

We intentionally match micro’s core directive names (so you can port settings) and add a few
editor-specific conveniences.

Micro-compatible:
- `$(filename)`
- `$(modified)`
- `$(line)` / `$(col)` / `$(lines)` / `$(percentage)`
- `$(opt:NAME)` — option value (buffer-local overrides apply)
- `$(bind:ACTION_SPEC)` — representative key bound to an action spec
- `$(overwrite)` — present for compatibility (currently empty)

Micromax-editor extensions:
Tiny conditional:
- `$(if:COND|THEN|ELSE)`
  - `COND` is a directive-like expression (e.g. `modified` or `opt:filetype`)
  - `THEN` / `ELSE` are templates (they can contain `$()` directives)
  - escape a literal `|` as `\|`

- `$(readonly)` / `$(ro)`
- `$(cur)` / `$(cursors)` — ` cur:N/M`
- `$(sel)` / `$(sels)` — ` sel:K` (only when K>0)
- `$(keymode)` / `$(km)` — ` [name]` (with `!` when one-shot)
- `$(macro)` — ` REC` / ` PLAY`

Fallback: if a directive name matches a key in `status_model()`, that value is substituted.

## Reference formatter

`statusline_text(width)` now renders by evaluating `statusformatl` and `statusformatr` and then
right-justifying the right side. The truncation behavior (trim left first; keep right tail if
needed) remains deterministic and well-tested.


## References
- micro options (statusformat directives): https://github.com/zyedidia/micro/blob/master/runtime/help/options.md
- example statusformat strings mentioning filetype/encoding: https://github.com/zyedidia/micro/issues/1419
