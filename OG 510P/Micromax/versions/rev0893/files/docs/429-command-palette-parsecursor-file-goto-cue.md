# Rev487: command-palette parsecursor file rows keep exact goto cues for open buffers

This is a tiny trust/flow follow-up to rev484/rev486's palette path cleanup.

Micromax already had the right nearby pieces:

- already-open file targets appended a tiny `current buffer` / `switch buffer` cue
- exact typed `Open` rows already kept `existing file` / `new file` truth
- parsecursor-shaped opens already landed at the typed cursor on submit

But one adjacent seam still lagged behind that same loop: when a parsecursor-shaped
file target already mapped to an open buffer, the exact typed `Open` row still
read like a static buffer witness even though pressing `Enter` would move the
cursor inside that live buffer.

That left one small trust/flow gap exactly where Micromax should be most boring
and honest:

- `guide/intro.md:1:0` could still render as `recent #1 [active] @ 2:1 | ... | current buffer`
  even though submit would move the cursor back to `1:0`
- the row already knew enough to distinguish `current buffer` from `switch buffer`,
  but it still hid the last cursor-motion part of that action
- unsaved/open buffers had the same seam: Micromax could know the exact live
  clamp target without saying it

Rev487 keeps the fix deliberately small:

- exact typed `Open` rows now append one tiny `goto line:col` cue when a
  parsecursor-shaped file target already maps to an open buffer
- the cue is clamped against the live buffer, so already-open unsaved targets
  stay exact too
- focused tests pin both the live `command_palette_apropos_rows()` surface and
  the hostcall `ed.command-palette-rows QUERY` contract

Focused coverage lives in:

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`

The goal is simple: when a visible palette row already knows `Enter` will move
the cursor inside an open buffer, it should say so before you commit.
