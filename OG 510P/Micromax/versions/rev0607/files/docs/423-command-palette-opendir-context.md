# Rev481: command-palette directory rows keep exact recent-directory context

This is a tiny trust/flow follow-up to rev454/rev480's recent-directory and
palette path-completion cleanup.

Micromax already had the right ingredients:

- `recent_dir_detail_row(DIR)` / `ed.recent-dir-detail-row` could answer one
  exact recent-directory question without reopening `recentdirpick`
- `showrecentdir DIR` already gave humans the same tiny count/state summary
- rev480 taught visible palette file rows to reuse exact recent/open metadata
  instead of collapsing every filesystem hit back to a blank generic row

But one adjacent seam still lagged behind the rest of that loop: visible
palette **directory** rows still only showed the parent listing directory, even
when Micromax already knew that one visible folder was an active recent bucket
with multiple open/dirty files inside it.

That mattered in the same trust-first moment as the recent-file cleanup:

- before drilling into a directory, humans/LLMs should be able to see whether
  it is already live in the session
- the command palette should not hide exact recent-directory state behind a
  separate `showrecentdir DIR` detour when one visible row has already resolved
  to that exact bucket
- fallback rows should stay lightweight, but known rows should stay honest

Rev481 keeps the change deliberately small:

- `_command_palette_open_path_row(...)` now reuses `recent_dir_detail_row(DIR)`
  for visible `menu=dir` rows when that directory is already a known recent
  bucket
- those rows now show a tiny `recent dir: N files [...]` summary with active,
  open, dirty, and readonly counts when non-zero
- ordinary non-recent directory rows still keep the older lightweight parent
  cue, so the palette does not grow a second directory-inventory system

Focused coverage lives in:

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_mx_commands_and_completion.py`

The goal is simple: if one palette directory row already maps to one exact
recent-directory bucket, Micromax should keep that tiny honest state visible
before drill-down instead of pretending it is just another generic folder name.
