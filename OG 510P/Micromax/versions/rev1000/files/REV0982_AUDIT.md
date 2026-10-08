# Rev0982 audit — own Popen construction; retain sparse coordinates

## Highest-risk findings

Rev0981's worker deadline still began after synchronous `subprocess.Popen(...)`
returned. Regex worker, browser, shell, and bounded argv callers could therefore
freeze in a phase their advertised timeout did not own. Online Python
documentation confirms that initial process creation is not interruptible on
many platform APIs.

Allocation audit evidence also found three product-path cliffs: complete true-
wordwrap boundary lists, duplicated tuple/int search geometry, and rich replace
rows plus repeated prefix rescans. Multicursor planning duplicated its existing
line index, and debug `repr` could accidentally rematerialize complete packed
coordinates.

## Substantive correction

- Added one finite, single-pending owner for synchronous Popen construction.
- Shared one absolute deadline with regex readiness and process execution/capture.
- Transferred late process, process-tree, pipe-owner, stream, and reap ownership
  to the timed-out starter.
- Closed asynchronous-interruption windows after constructor completion, during
  ambiguous starter-thread publication, during regex readiness, and after only
  part of a capture thread set has started.
- Refactored duplicate argv/shell construction and capture policy through one
  `_run_captured_process` path.
- Added sparse checkpointed true-wordwrap geometry and a four-line LRU in the
  visual-row index; rendering materializes visible fragments only.
- Packed search line starts and span coordinates in native unsigned arrays and
  streamed literal matches directly into final storage.
- Split compact replacement edits from rich compatibility/sample rows; changed
  query-replace to retain the compact immutable plan.
- Reused compact line-start indexes across simultaneous-edit planning and moved
  newline discovery into native `str.find` loops.

## Audit/refactor corrections

The final audit replaced a scheduler-dependent wall-clock test with a fake-clock
absolute-deadline witness, bounded packed-coordinate representations, added
changed-line wordwrap-cache eviction tests, and added an index-only sequence
regression that fails if multicursor planning reboxes the complete source index.
It then found and repaired two ownership defects: a completed child could be
orphaned by interruption before return, and partially started capture readers
could lose their owner. Deterministic regressions now exercise both defects,
including the `Thread.start()` interval before `ident` publication. A seeded
cross-revision probe matched rev0981 output exactly across 350 searches, 350
replacement plans, and 1,000 wrap geometries.

## Measured evidence

Paired Python 3.13.5 `tracemalloc` observations on the same Linux cloudtainer:
editor true-wordwrap view peak fell from 818,568 to 8,460 bytes; cold 100,000-
match search peak from 26,730,947 to 5,053,227 bytes; 20,000-match replace-plan
peak from 4,745,580 to 2,825,420 bytes. These are Python-tracked allocations,
not RSS or total heap. The permanent witness records exact compact payloads.

The deterministic constructor witness observed a raw injected constructor still
blocked after 0.05 seconds, two bounded callers returning in about 0.05 seconds,
zero second-factory calls, completed late cleanup, and successful later start.

## Residual risk

One never-returning constructor retains one daemon starter and the gate; callers
remain finite but cleanup cannot finish. Starter/readiness/capture thread
creation and cleanup callback execution have no independent preemption. An
interrupt before starter identity publication conservatively leaves the gate to
a possible starter and can therefore retain it even if no thread appears. Normal
starts briefly serialize. Windows process-tree behavior is unproved. Sparse
geometry bounds retained coordinates but not first-scan CPU, source text, undo
snapshots, regex result text, native memory, or explicit compatibility APIs that
request complete rich geometry. See
`docs/939-popen-deadline-sparse-hotpaths.md`.
