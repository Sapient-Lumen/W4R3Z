# Scroll margin / viewport context (rev175)

Rev175 adds a tiny shared `scrollmargin` option to the editor's viewport logic.

## Option

- `scrollmargin` (int, default `0`)

Meaning:
- keep at least that many **vertical context rows** above and below the primary cursor
  when the viewport scrolls
- applies in the shared headless viewport model, so the current curses TUI and future
  UIs inherit the same behavior automatically
- under `softwrap=true`, the margin is measured in **visual rows** (wrapped fragments),
  not logical document lines

The current pass is intentionally small:
- vertical only
- no separate horizontal margin policy yet
- clamped to at most half the viewport height (rounded down), so the “safe band” never
  becomes contradictory in tiny windows

## Why this way

Micro documents `scrollmargin` as the margin at which the view starts scrolling, and Vim/Neovim's
`scrolloff` guidance points to the same UX lesson: a little persistent context around the cursor
makes movement feel calmer than only scrolling once the cursor hits the last visible row.

For Micromax, the important design choice was to keep this in the **shared viewport contract**,
not as a curses-only tweak. That means:
- `ensure_cursor_visible()` owns the rule
- headless tests can validate it directly
- future frontends/LLM tooling do not need to reinvent when the window should move

## Softwrap interaction

When `softwrap=true`, Micromax already treats vertical movement and scrolling in visual rows.
`scrollmargin` follows the same rule:
- wrapped continuation rows count as normal visible context rows
- `top_line` / `top_subline` still describe the viewport origin
- the cursor keeps its margin in wrapped-row space when possible

## Files/tests

- editor core: `src/micromax_editor/editor.py`
- docs: `docs/94-softwrap.md`, `docs/43-worklist.md`, `docs/41-decisions-log.md`
- tests: `tests/test_editor_viewport_and_typing.py`, `tests/test_editor_softwrap.py`
