# Encoding (rev199)

Micromax now treats text encoding as a real per-buffer editor option instead of a
hardcoded `utf-8` status token.

## Why

Before rev199, the editor always opened and saved files as UTF-8, while the
status/config surface only *looked* like it had a meaningful `encoding` field.
That meant non-UTF-8 workflows had no honest shared-core path, and future UIs or
scripts would have had to special-case file I/O instead of trusting the editor
model.

## Current rule

- `encoding` is now an ordinary string option (default `utf-8`)
- ordinary `open_file(...)` decodes existing files with the configured encoding
- ordinary `save()` encodes using the effective buffer-local encoding
- the user-facing option spelling stays visible in status/config surfaces
- Python codec aliases are normalized only at the actual encode/decode boundary
- docs/help buffers keep using their existing explicit UTF-8 docs path

## Main touch points

- `src/micromax_editor/editor.py`
  - `_install_default_options()`
  - `new_buffer(...)`
  - `_normalize_encoding_name(...)`
  - `open_file(...)`
  - `save()`
  - `status_model()`
- `tests/test_editor_fs_open_save.py`
- `tests/test_editor_statusline.py`

## Examples

```text
set encoding latin-1
open notes.txt
```

```text
setlocal encoding cp1252
save
```

This keeps the contract small and explicit: file I/O follows the effective
editor option, while the in-memory buffer model still stays ordinary Unicode
text.
