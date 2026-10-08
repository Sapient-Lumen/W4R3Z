# Softwrap (rev73, expanded rev198)

Micromax Editor is headless-first, but it already has a shared **viewport model** so UI layers
(TUI today, other frontends later) can agree on scrolling and cursor visibility.

This doc defines the current **softwrap** contract.

## Options

- `softwrap` (bool, default `false`)
- `softwrap.contindent` (int, default `-1`)
- `wordwrap` (bool, default `false`)

When `softwrap=true`:
- long logical lines are wrapped to the viewport width
- if `wordwrap=true`, wrapped rows prefer breaking at spaces when possible
- horizontal scrolling is disabled (`left_col` is forced to `0`)
- vertical movement + scrolling are defined in **visual rows** (wrapped fragments)

Continuation indent (`softwrap.contindent`) controls the indentation applied to wrapped fragments:
- `-1` = auto (use the original line's leading whitespace, clamped)
- `0` = off
- `>0` = fixed number of columns

This is a UX convenience (the indent is *visual*, not buffer text).

## Viewport model

Viewport state lives in the headless core and is exposed via `ed.viewport`:

- `top_line`: logical line index
- `top_subline`: wrap-row index (0-based) within `top_line` when softwrap is enabled
- `left_col`: horizontal scroll (forced to `0` under softwrap)
- `height`, `width`: viewport size in character cells

When `softwrap=false`, `top_subline` is always `0` and the viewport behaves like a traditional
`top_line + left_col` scroller.

## Rendering model

The core exposes:

- `Editor.view_rows(height=H, width=W) -> list[(line_index, start_col, fragment)]`

Each returned element represents a *screen row*:
- `line_index`: the logical buffer line being rendered
- `start_col`: the starting character column for this fragment (wrap start in the underlying line)
- `fragment`: the substring to display (length ≤ `W`, but may include a continuation-indent prefix)

When `softwrap=false`, `start_col` is the viewport's `left_col` for every row.

When `softwrap=true`, a single logical line can appear in multiple rows. If the viewport begins
mid-line (non-zero `top_subline`), the first returned row begins at that wrap row. With `wordwrap=true`, row boundaries prefer the final whitespace that fits on the current row before falling back to hard wrapping.

Continuation indent behavior:
- the first visual row uses the full width `W`
- subsequent rows render as: `(" " * contindent) + line[start : start + (W - contindent)]`
- `start_col` remains the *true* start column in the underlying line (not counting the visual prefix)

Notes:
- This is a rendering model, not a UI. It intentionally ignores styling/spans for now.
- Tabs are treated as single characters here; a renderer can expand tabs to visual columns later.

## Cursor + movement model

The core exposes:

- `Editor.cursor_view_pos(height=H, width=W) -> (y, x)`

This maps the primary cursor into the current viewport's screen rows.

When `softwrap=true`, the default vertical cursor actions (`CursorUp` / `CursorDown`, plus
`PageUp` / `PageDown`) move and scroll by visual rows (wrapped fragments), not by logical lines. Rev185 extends that same rule to `pageoverlap`, so wrapped paging can keep a few prior visual rows visible between page jumps just like ordinary views keep prior logical rows visible.

`StartOfLine` / `EndOfLine` become **visual-row Home/End** under softwrap:
- `StartOfLine` moves to the start column of the current wrapped fragment
- `EndOfLine` moves to the end column of the current wrapped fragment

## Scroll margin interaction (rev175)

The shared viewport model now also honors `scrollmargin`.

When `softwrap=true`:
- the margin is measured in **visual rows**, not logical lines
- wrapped continuation rows count as ordinary context rows
- scrolling still updates `top_line` + `top_subline`, so future UIs/LLMs can observe the
  same wrapped-row origin without reproducing the policy themselves

This keeps the first implementation tiny and shared: no TUI-only special case, no alternate
softwrap scroll policy.

## Known limitations / follow-ons

- Word wrapping is still intentionally tiny: it prefers visible whitespace breakpoints, but long unbroken tokens still hard-wrap by width and there is no list-aware hanging-indent logic yet.
- Tabs are treated as width 1 in the core model (a renderer can expand them).
- Continuation indent is based on leading whitespace and does not yet implement list-aware hanging indents.
