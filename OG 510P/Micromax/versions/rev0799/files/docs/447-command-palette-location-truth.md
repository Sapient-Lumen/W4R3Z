# Command-palette location truth

Rev505 closes one small but important trust seam in Micromax's searchable
file-open loop.

Micromax already had the nearby honest surfaces:

- palette `Recent Files` rows reused exact MRU metadata plus tiny
  `existing file` / `new file` and `current buffer` / `switch buffer` truth
- typed `Open` rows and visible `openpath` file rows already kept the same
  disk/action truth for saved, missing, and already-open targets
- exact `showrecent PATH` inspection already exposed the same MRU/disk/action
  cues when one target was known exactly

But two tiny location seams still lingered inside those same rows:

- palette `Recent Files` rows could still spend their `info` slot repeating a
  basename the `menu` slot already showed, which hid the more useful answer of
  where reopen/save would actually land
- a relative typed `Open` row for an already-open unsaved file like
  `scratch.md` could still say `... | scratch.md | new file | current buffer`
  even though the interesting extra truth was the landing directory

## What landed

Rev505 keeps the follow-up deliberately small.

- `_command_palette_recent_file_row(...)` now treats the `info` slot as landing
  context: it prefers project-relative detail when that adds information and
  otherwise falls back to the section/parent path instead of repeating the
  basename already carried by `menu`
- `_command_palette_file_info(...)` now does the matching bare-filename new-file
  follow-up for exact typed `Open` rows, so already-open unsaved basename
  queries keep their landing directory visible too
- existing richer cases stay intact: nested/project-relative detail still wins
  when it adds information, and absolute-path queries still keep the exact path
  you typed

## Why this matters

This is a tiny trust/flow cleanup.

When Micromax already knows a row is pointing at one current unsaved buffer or
one exact recent target, the row should answer the next practical question —
*where is this thing?* — instead of spending its last bit of space repeating a
filename humans and future LLMs can already see in the menu/query.

## Focused tests

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_help_docs_buffers.py`
- `tests/test_editor_mx_commands_and_completion.py`
- `tests/test_tui_prompt_display_items.py`
