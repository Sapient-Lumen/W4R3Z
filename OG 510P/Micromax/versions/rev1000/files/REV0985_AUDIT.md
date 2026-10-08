# Rev0985 audit — atomic sparse simultaneous history

The deep implementation, research, measurement, and residual-risk record is
`docs/942-atomic-sparse-simultaneous-history.md`.

## Heart of the mission

Micromax is a calm editor for understandable least-authority automation. Undo,
rendering, save, and recovery must protect the lived editing loop; policy and
evidence are useful only when they make that loop more trustworthy.

## Severe corrected defect

Immediate multi-cursor edits still retained complete before and after document
strings. A few inserted bytes on a large file could become one oversized newest
history row that the rev0984 budget correctly preserved but could not compact.

Rev0985 projects the existing one-source simultaneous plan into old/new-coordinate
splices. Undo and redo validate every expected target against one current text
before committing one result, so a stale later splice cannot leave an earlier
inverse half-applied. Equal replacements retain only sidecars.

The permanent 1,100,000-character, eight-cursor, ten-action witness reduces
accounted retained text from 22,005,600 to 560 bytes (99.997%), median traced
current allocation from 11,052,850 to 1,180,601 bytes (89.319%), and median
traced peak from 12,157,875 to 3,384,155 bytes (72.165%), with exact undo/redo.

## Refactor and product evidence

`Cut`, `ed.replace-selections`, `ed.replace-range`, and `ed.delete-range` now use
the shared undoable simultaneous-edit seam; the duplicate broad recording code
and dead `_delete_selections` helper are gone.

The bounded product journey now crosses large sparse paste, public headless
render validation, query-replace cancellation, save, undo, redo, an interrupted
explicit save, restart recovery, and final commit while disk retains its last
good generation until the recovered buffer is explicitly saved.

A suppression audit removed two redundant local snapshot-helper calls per
eligible aggregate action. Rev0984 already used a version sentinel there, so this
is sidecar/control-flow cleanup—not a second full-document memory claim. Live
query-replace remains on the broad finalization path and has a regression.

## Missing or still risky

- Planning and replay still materialize complete result text.
- Query-replace, specialized line plans, and arbitrary aggregate transactions
  retain broader snapshots.
- Initial aggregate rollback capture still visits every open buffer.
- `undobytes` excludes callbacks, dataclasses, sidecars, allocator/native memory,
  RSS, and metadata-only rows; typing is not coalesced.
- Exact slice validation is local, not a whole-document generation proof;
  deletion undo and insertion redo have empty source slices and can authenticate
  only coordinate geometry, not neighboring bytes.
- Sustained-use/taste evidence, signed/hermetic release, and explicit platform
  support remain incomplete.

## What should change next

Measure sustained typing object cost and undo feel before coalescing. Prototype
first-write transaction capture behind one narrow path while broad rollback
remains the differential oracle. Measure accepted query-replace sessions before
compacting them. Prefer sustained product evidence and net coordinator deletion
over another doctrine or registry layer.

## What should not change yet

Do not add an undo tree, persistent or independent per-buffer history graph,
piece table, broker, watcher, background index, generic transaction owner, or
Wasm host without measured product pressure and an executable compatibility
oracle.
