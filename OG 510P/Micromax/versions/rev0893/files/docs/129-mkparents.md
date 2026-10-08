# Save-time parent creation (`mkparents`) (rev188)

Rev188 adds a tiny shared `mkparents` option to the editor core.

## What it does

- `mkparents` (bool, default `false`)
- when enabled, manual saves create missing parent directories for the current
  buffer path before writing the file
- this applies to ordinary `save` and `saveas` flows because both reuse the same
  shared `Editor.save()` path

## First-pass policy

This landing stays intentionally small:

- it does **not** invent a backup/recovery subsystem
- it does **not** silently rewrite paths
- it only creates directories that are already implied by the target file path
- if `mkparents=false`, the old `FileNotFoundError` behavior stays intact
- if some parent path component is an existing file rather than a directory, the
  underlying filesystem error still surfaces honestly

## Why this shape

micro already exposes `mkparents` as a save-path option rather than a separate
file-management command, which is a good fit for Micromax's headless-first
editor core.

That makes this feature another shared save-path normalization/policy decision,
like `rmtrailingws` and `eofnewline`, instead of a TUI-only convenience.

## Where to look

- option registry: `src/micromax_editor/editor.py::_install_default_options`
- save path: `src/micromax_editor/editor.py::save`
- tests: `tests/test_editor_fs_open_save.py`, `tests/test_portability_suite.py`
