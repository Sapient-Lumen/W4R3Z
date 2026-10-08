# Rev0983 changelog

## Runtime and editor

- Added frozen `BufferSplice` inverse witnesses and `BufferEditConflict` guarded replay.
- Added `Buffer.replace_range_with_witness()` and kept `replace_range()` as its cursor-returning compatibility seam.
- Added compact one-cursor undo recording for ordinary insert, newline, backward/forward delete, paste, and tab.
- Retained broad snapshot fallback for multi-cursor, unowned plans, query-replace, specialized line edits, and aggregate scripted transactions.
- Restored undo/redo stack membership when an edit callback raises.
- Added explicit stale undo/redo refusal feedback.

## Evidence

- Added `tools/measure_undo_retention.py`, which compares compact splice history with the rev0982 snapshot action shape and verifies exact undo/redo.
- Added multiline roundtrip, exact-target conflict, failure-safe stack, closure-retention, sidecar-only, and stale-feedback tests.
- Added the deep mission/resource audit in `docs/940-compact-splice-undo-mission-audit.md`.

## Scope

This revision does not bound total history, large removed slices, multi-cursor/aggregate snapshot retention, immutable line-copy peaks, RSS/native memory, or cross-platform performance. It adds no text-engine rewrite, history tree, broker, registry, watcher, background index, or Wasm boundary.
