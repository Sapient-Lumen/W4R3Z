# Rev268: help navigator headings should reuse outline breadcrumbs

Rev266 taught `helpoutlinepick` how to expose and reuse parent-heading
breadcrumb sections (`Top`, document title, `Guide`, `Guide › Links`, ...).

`helpnavpick` still had one small mismatch: it merged headings and links into one
useful navigator, but all heading rows still lived in a single generic
`Headings` bucket even though the outline picker already knew the more honest
section labels.

That drift mattered in a few small places:

- empty-query browse windows could only say `Headings` instead of the heading
  region actually on screen
- `Alt-Up` / `Alt-Down` section jumps treated all heading rows as one block even
  when the outline picker already had better boundaries
- `prompt_current_section`, preview text, and headless status surfaces lost the
  parent breadcrumb context for heading rows inside `helpnavpick`

Rev268 keeps the fix tiny:

- `help_nav_section_rows(query)` now starts from the same grouped heading shape
  already exposed by `help_outline_section_rows(query)`
- heading rows inside `helpnavpick` now reuse the same breadcrumb labels the
  outline picker shows live
- link rows keep the existing `helplinkpick` grouping policy, so docs/files/
  external (or heading-based link grouping) still behave the same
- browse-window budgeting and section jumps now operate on those more honest
  heading groups automatically

That keeps the combined docs navigator aligned with the shared grouped-picker
substrate instead of inventing a second heading-group policy just for one prompt.

Focused coverage:

- `tests/test_editor_helpnavpick.py`
- `tests/test_editor_help_picker_browse_budget.py`
- `tests/test_editor_statusline.py`

Files touched:

- `src/micromax_editor/editor.py`
- `docs/01-llm-start-here.md`
- `docs/41-decisions-log.md`
- `docs/43-worklist.md`
- `docs/64-editor-prompt-completion.md`
- `docs/98-help-browser.md`
- `README.md`
- `TODO.md`
- `tools/mxcontext.py`
