# `showrecent` command-bar preview (rev538)

## Why

Micromax already knew how to answer one exact recent-file question through
`showrecent PATH|N|#N` and the stable `recent_detail_row(...)` surface. But
plain `showrecent` in the command bar still looked like a generic exact-command
row, and its registered command doc still claimed the command only accepted
`PATH`.

That was a small trust/flow seam: the exact recent-file inspector already
understood visible slots like `#N`, yet the first row humans and future LLMs
saw before Enter hid both the newest visible target and the real argument
contract.

## What changed

- new `Editor._prompt_showrecent_command_row(...)` reuses the existing exact
  recent-detail row for visible slot `#1`
- exact command completion for plain `showrecent` now keeps the ordinary
  command doc while replacing the generic hint with either:
  - `latest #1 ... · expects PATH|N|#N`
  - `no recent files · expects PATH|N|#N`
- the registered command/help doc now says:
  - `showrecent PATH|N|#N - show exact recent-file state without opening`

## Examples

- with one current MRU entry available, plain `showrecent` can preview as:
  - `latest #1 /tmp/demo | file.txt | existing file | current buffer · expects PATH|N|#N`
- with no remembered recent files, the same row now previews as:
  - `no recent files · expects PATH|N|#N`

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecent_command_previews_latest_visible_slot`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecent_command_previews_empty_inventory`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
