# Rev482: command-palette typed `Open` rows keep exact target context

This is a tiny trust/flow follow-up to rev480/rev481's palette path-context
cleanup.

Micromax already had the right nearby pieces:

- visible file completion rows reused exact recent/open state when one target
  already mapped to a known file
- visible directory rows reused exact `recent_dir_detail_row(DIR)` state when
  one folder already matched a known recent bucket
- selecting a palette file row already reported the landed target explicitly

But one adjacent seam still lagged behind the rest of that loop: the palette's
explicit typed `Open` row — the row people actually hit `Enter` on after typing
an exact path — still said only `path-like query`.

That hid useful truth exactly where Micromax should be most boring and honest:

- if the typed target was already an open/recent file, the final `Open` row did
  not say so
- if the typed target was already a known recent directory, the final `Open`
  row did not say drill-down would keep you in a live bucket
- if capability-gated filesystem inspection was available, the row still did
  not tell you whether the typed path already existed or would become a new
  file path on save

Rev482 keeps the fix deliberately small:

- `_command_palette_open_path_row(...)` now gives `menu=open` rows the same
  tiny exact file/directory context helpers already used by nearby visible rows
- exact typed file targets now reuse the same recent/open metadata the file-side
  palette rows already trust
- exact typed directory targets now reuse the same recent-directory count/state
  metadata the directory rows already trust
- when `cap.fs-list` allows exact target inspection, typed `Open` rows now also
  distinguish `existing file`, `directory`, and `new file`
- focused tests pin both the live `command_palette_apropos_rows()` surface and
  the hostcall `ed.command-palette-rows QUERY` contract

Focused coverage lives in:

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`

The goal is simple: the row you hit `Enter` on should tell the truth about what
Micromax is about to open.
