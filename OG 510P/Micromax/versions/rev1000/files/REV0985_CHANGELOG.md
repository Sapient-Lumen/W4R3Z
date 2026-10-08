# Rev0985 changelog

## Runtime and editor

- Added immutable sparse simultaneous-edit witnesses with old/new coordinate
  ranges and exact old/new slices.
- Added atomic all-target validation before one undo/redo text commit, including
  adjacent deletes whose inverse insertions share one offset.
- Added grouped sparse history rows with exact cursor, selection-anchor,
  cursor-id, and primary-cursor sidecars plus logical retained-text charges.
- Preserved the direct one-cursor `BufferSplice` path as the smallest common row.
- Kept live query-replace on its broad delayed-session finalization boundary.
- Routed `Cut`, `ed.replace-selections`, `ed.replace-range`, and
  `ed.delete-range` through the shared undoable simultaneous-edit seam.
- Removed duplicate manual snapshot recording and the dead
  `_delete_selections()` helper.
- Skipped redundant local snapshot-helper calls for ordinary edits already owned
  by suppressed macro/`ed.with-undo` transactions; preserved query-replace
  finalization semantics.

## Evidence

- Added `tools/measure_simultaneous_history.py` and
  `.artifacts/rev0985-simultaneous-history.json`.
- Added 1,000 seeded Unicode/newline plan roundtrips, adjacent-inverse,
  outside-range preservation, undo/redo stale-later-target atomicity, large
  sparse retention, sidecar-only, aggregate
  suppression, qreplace-boundary, Cut/hostcall seam, product-recovery-journey,
  and executable-witness regressions.
- Added the deep audit and online comparison in
  `docs/942-atomic-sparse-simultaneous-history.md`.

## Scope

This revision compacts immediate simultaneous history. Planning/replay still
construct complete result text. Query-replace, specialized line plans, and
arbitrary aggregate transactions remain broad. Logical text accounting is not a
hard RSS/object/native-memory bound, and typing coalescing, persistent history,
undo trees, text-engine replacement, signed release, and cross-platform support
remain outside the claim.
