# Rev546 - showrecentdir exact slot miss preview

Make the exact recent-directory inspector keep its visible-slot miss truth before Enter too.

## Why

Micromax already had most of this trust loop in place:

- `showrecentdir DIR|N|#N` already reports `showrecentdir: no such recent directory: ...` after Enter
- plain `showrecentdir` already previews the newest visible recent-directory bucket before Enter
- recent-facing rows already speak the visible `#N` slot dialect consistently

But one small seam remained while typing an exact visible slot. A query like `showrecentdir #9` could drop back to a blank generic row because completion discarded the missing token before Micromax could reuse the same exact-miss truth the command itself already knew.

## What changed

- add `Editor._prompt_exact_recentdir_row(...)`
- reuse that helper for `showrecentdir` argument completion rows
- preserve typed `N|#N` tokens for `showrecentdir` completion when the user clearly asked for one exact visible slot
- render `no such recent directory` in the command bar for missing visible-slot tokens
- keep the existing after-Enter command message unchanged

## Result

If Micromax can tell that `showrecentdir` is being asked for one exact visible recent-directory slot, it now says `no such recent directory` before Enter instead of going blank.

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentdir_slot_miss_stays_honest`
- `tests/test_editor_buffer_mru_and_closeall.py::test_recent_dir_detail_row_and_showrecentdir_surface`
