# Fileformat (rev196)

Micromax now treats line endings as a real per-buffer editor option instead of a
statusline placeholder.

## Why

Before rev196, the status model always reported `fileformat=unix`, but
`open_file(...)` decoded files in a way that immediately erased whether the file
had been LF or CRLF on disk. That made the status/config surface look more
finished than the shared editor behavior really was.

The new rule stays intentionally small:

- buffers still store logical text normalized to `\n`
- `open_file(...)` now preserves raw newline information long enough to guess the
  on-disk format best-effort (`CRLF` => `dos`, otherwise `unix`)
- `save()` writes LF for `fileformat=unix` and CRLF for `fileformat=dos`
- `setlocal fileformat dos` immediately affects future saves without rewriting the
  in-memory buffer model

## Current scope

This first pass is deliberately conservative:

- text encoding is now a separate option (`docs/140-encoding.md`) rather than being bundled into fileformat
- there is no mixed-line-ending preservation mode
- the internal buffer model stays newline-normalized and portable
- status/model/template surfaces now report the effective option honestly

## Main touch points

- `src/micromax_editor/editor.py`
  - `_install_default_options()`
  - `new_buffer(...)`
  - `_detect_fileformat_from_text(...)`
  - `open_file(...)`
  - `save()`
  - `status_model()`
- `tests/test_editor_fs_open_save.py`
- `tests/test_editor_statusline.py`

## Examples

```text
setlocal fileformat dos
save
```

This writes CRLF line endings on the next save while leaving the buffer's
in-memory text model normalized to `\n`.
