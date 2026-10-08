# Statusline row policy (rev207)

Micromax already had a `statusline` option and a tiny reference formatter, but until rev207 the
minimal curses TUI still reserved the bottom row even when `statusline=false`.

That meant the option hid the text without actually reclaiming the screen space.

## What changed

The curses TUI now treats `statusline=false` as real layout policy:

- the status row is **not reserved** when the option is disabled
- the editing viewport gets that row back
- `prompt`, `infobar`, and `keymenu` rows still stack relative to the
  **actually visible** status bar, not an invisible placeholder row

So these combinations now behave honestly:

- `statusline=true`, `infobar=true` → buffer + infobar + statusline
- `statusline=false`, `infobar=true` → buffer + infobar
- `statusline=false`, `infobar=false` → buffer uses the full terminal height
- `statusline=false` with an active prompt → the prompt still uses the bottom row

## Why keep this renderer-local

This is still a UI/layout rule, not shared editor state.

The headless editor already exposes the important shared pieces (`status_model()`,
active prompt state, messages, viewport size). The curses frontend is simply being
more honest about how many terminal rows it actually needs.

That keeps the archive easy to evolve by hand:

- future frontends can make their own row-allocation choices
- tests can validate the current TUI layout deterministically
- we avoid promoting "invisible UI chrome" into the headless editor model

## Tests

Focused regression coverage lives in `tests/test_tui_keymenu.py`:

- `test_render_statusline_false_reclaims_bottom_row_when_no_other_bottom_chrome`
- `test_render_statusline_false_still_keeps_prompt_on_bottom_row`

## Related docs

- `docs/97-statusline.md`
- `docs/146-keymenu.md`
- `docs/147-infobar.md`
