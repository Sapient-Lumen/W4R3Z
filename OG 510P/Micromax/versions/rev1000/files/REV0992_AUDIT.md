# Rev0992 audit — aggregate line-vector transactions

The deep implementation, measurement, research, and residual-risk record is
`docs/949-aggregate-line-vector-transactions-audit.md`.

## Heart of the mission

Arbitrary quotations and macros must remain exact editor-state transactions, but
a one-character change in a large buffer must not create and retain complete old
and new document strings. Rev0992 keeps the broad rollback shell and replaces
its touched-buffer content generations with shallow immutable line-vector
snapshots.

## Severe corrected waste

In the permanent eight-buffer / 1,099,999-character-per-buffer
`ed.with-undo` witness, a one-character successful transaction falls from nine
complete joins and 9,899,992 joined characters to zero. Traced peak Python
allocation falls from 9,935,882 B to 259,641 B (97.387%), and logical retained
text falls from 2,199,999 B to 1,113,828 B (49.371%). Failure rollback falls from
22,995,344 B traced peak to 246,632 B (98.927%) with exact state restored.

Immediate macro success, failure, and navigation also join no complete document.
Their traced peak reductions are 97.367%, 98.910%, and 99.606% respectively.

## Correctness defects found and fixed

The audit reproduced an outer macro that begins by undoing an existing aggregate
row. Trusted line-vector Undo/Redo restoration did not notify an enclosing
first-write observer, so the outer transaction could capture the post-Undo text
instead of its true entry generation. `Buffer._restore_lines_snapshot()` now
announces the mutation before replacing the live vector. Nested Undo/edit/Undo/
Redo regressions pin the exact outer boundary.

A final source diff audit found a second defect: Undo could rewind a version,
two separated edits could advance it to exactly `before + 1`, and the last
`BufferChange` could then be mistaken for the whole transaction. The reproducer
undercharged `undobytes` at 26 B instead of the conservative 37 B. The aggregate
observer now saturates an explicit mutation-boundary count at two, and exact
single-splice accounting is legal only when that count is one.

## Shipped change

`Buffer.snapshot_lines()` returns one detached tuple of immutable canonical line
strings. First-write capture retains that tuple only for actually touched
pre-existing buffers; finalization retains changed after tuples; rollback,
Undo, and Redo restore those generations plus the exact state shell. Untouched
line strings remain shared by identity. Success, failure, and navigation product
paths call neither `Buffer.get_text()` nor `Buffer.set_text()` under the measured
fast-dirty boundary.

Retained-text accounting uses the existing exact `BufferChange` witness only
when the explicit transaction-local count proves one mutation boundary; rewound
or multi-write shapes use a conservative shared-prefix/suffix fallback. A
per-line identity-set prototype was rejected because its measurement overhead
erased much of the small-edit win.

## Research and scope

CodeMirror and ProseMirror reinforce authoritative prior generations and
invertible changes; Scintilla reinforces nested top-level grouping and excluding
navigation from document history. Python's shallow-copy and immutable-string
contracts justify a detached pointer vector with shared line objects. Micromax
does not generalize arbitrary quotations into a universal step algebra and adds
no generic transaction registry, rope, piece tree, or second text model.

## Validation evidence

The core transaction/history lane passes 207 tests covering the new aggregate
line-vector regressions, first-write `ed.with-undo`, immediate macro replay,
failed rollback, Unicode accounting, bounded history, and exact forward/Undo/
Redo. Adjacent authority and named-macro coverage passes 68 tests; sparse
simultaneous and query-replace history coverage passes 23 tests.

Release hygiene passes independently: revision index 1, living docs 4, generated
context 7, structural audit 4, effect contracts 5, and archive generation and
verification 53 tests. The archive lane initially caught a stale rev0991
`MICROMAX-CONTEXT.json` inside an otherwise rev0992 tree; regenerating the
context snapshot closed that lineage mismatch before packaging. Portability is
172/172. The doctor's bounded 19 + 9 + 3 tests pass; after the combined
wrapper stalled in this cloudtainer, its final three checks were rerun and passed
individually. Formatting, lint, Python compilation, generated effect help,
context checks, and audit metrics are clean.

A monolithic pytest invocation collected 3,455 tests but exceeded a 20-minute
cloudtainer ceiling, so this revision makes no complete-full-suite claim. A
larger selected union likewise exceeded its budget after exposing only the now
fixed living-doc size/casing drift. The bounded, attributable lanes above are
the publication evidence.

## Remaining risk

Line-vector snapshots still copy O(number of lines) pointers, one huge logical
line still rebuilds one immutable string, query-replace still owns one delayed
planning source, the non-text arbitrary-rollback shell remains broad, logical
`undobytes` excludes object/pointer/native/RSS overhead, and history remains
linear, in-process, non-durable, and single-writer. The highest next product risk
is now missing sustained-use evidence across the complete trust/taste/flow loop.
