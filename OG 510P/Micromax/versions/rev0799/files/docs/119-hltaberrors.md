# Tab-error cue / `hltaberrors` (rev178)

Rev178 adds a tiny `hltaberrors` option to the minimal curses TUI.

## What it does

- `hltaberrors` (bool, default `false`)
- when `tabstospaces=true`, **literal tab characters** are highlighted
- when `tabstospaces=false`, **space characters in the initial indent run** are highlighted
- the cue is visual-only: it does not change buffer contents or add diagnostics to
  the headless editor model

The current rendering uses the same simple reverse+dim cue as `hltrailingws`.

## Scope / policy

This first pass is intentionally tiny and renderer-local:

- tab/space mismatch is computed from the **logical line**
- only the intersection with the **current visible fragment** is highlighted
- that keeps softwrap and horizontal scroll honest without pretending Micromax
  already has a richer indentation-diagnostics model

So under softwrap, a wrapped continuation row only shows the cue if the visible
fragment actually contains a mismatching tab/space character.

## Why this shape

micro already exposes `hltaberrors` as a simple display toggle, which is a good fit
for Micromax's current headless-first editor core: helpful scanability without another
persistent span/diagnostic subsystem.

Micromax already had one real indentation policy knob — `tabstospaces` — so the
smallest honest follow-up was to let the TUI reuse that policy directly rather than
invent a second mismatch rule.

## Files

- option: `src/micromax_editor/editor.py::_install_default_options`
- renderer helper: `src/micromax_editor/tui.py::tab_error_spans`
- tests: `tests/test_tui_hltaberrors.py`, `tests/test_portability_suite.py`
