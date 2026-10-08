# Aggregate line-vector transactions: risk, repair, and residuals

Rev0992 removes the remaining complete-document string generations from
`ed.with-undo` and immediate macro transactions while preserving their broad,
arbitrary-quotation rollback contract. It also fixes a nested-history defect
found during the audit: aggregate Undo/Redo restored through a line-vector path
without announcing that mutation to an enclosing first-write transaction, so
the outer row could begin after the nested history change instead of at its true
entry state. A final source-level audit also found that version arithmetic could
misclassify rewind-plus-multiwrite history as one splice and undercharge
`undobytes`; rev0992 now carries an explicit transaction-local mutation witness.

## Heart of the mission

The mission is not “make Undo clever.” It is to make a calm editor whose visible
unit of work is both exact and proportionate:

- a quotation or macro may touch text, buffers, paths, dirty state, marks,
  registers, selections, search state, options, and history;
- success should become one understandable Undo step;
- failure should restore the exact in-process editor state the transaction owns;
- untouched buffers must remain untouched in memory as well as semantically; and
- changing one byte in a large buffer must not manufacture and retain two more
  complete document strings merely because the change was grouped.

The broad editor-state shell is still justified by the scripting contract. The
complete old/new text strings were not. Rev0992 changes only that content owner.

## What was severely wrong or wasteful

Before rev0992, first-write capture had already stopped eagerly joining every
open buffer. But once one buffer was touched, the transaction still generated a
complete old string at first write and a complete new string at finalization.
The success path retained both strings in history. The failure path retained a
complete old string long enough to roll back. A one-character edit in a
1,099,999-character buffer therefore paid document-scale allocation for a
transaction whose text delta was one character.

That waste was especially misleading because the live buffer was already a
canonical list of immutable line strings. Most edits replace one or a few line
objects and preserve the rest by identity. Joining the list discarded that
sharing, only for Undo to split the strings back into lines later.

The audit also found a correctness fault at the interaction between two exact
features. Aggregate Undo/Redo now restores a trusted line-vector snapshot. When
that restore happened inside a wider macro or `ed.with-undo`, it did not pass
through the normal mutation observer. The enclosing transaction could therefore
miss the nested history operation and capture its “before” state after Undo had
already changed the document. That outer row would be internally coherent but
wrong: its Undo could not return to the true state at macro entry.

This was not hypothetical. A macro beginning with Undo and then inserting text
reproduced it. The fix makes trusted line-vector restoration announce itself to
any active outer first-write observer before replacing the live vector.

The final diff audit found a second concrete fault in the new retained-byte fast
path. A macro could start at version N, Undo to N-1, perform two separated edits,
and finish at N+1. Version delta plus the final `BufferChange` then looked like
one monotonic splice even though that witness described only the last edit. The
reproducer charged 26 B where the conservative shared-line result was 37 B,
which could let old history survive an `undobytes` budget it should have
exceeded. The transaction observer now counts mutation boundaries, saturating at
two; the exact single-splice path is legal only when that explicit count is one.

## Shipped design

### 1. Shallow immutable content generations

`Buffer.snapshot_lines()` returns a tuple containing references to the current
canonical line strings. The tuple is detached from later list mutation, while
unchanged strings remain shared because Python strings are immutable.

A first-write transaction now proceeds as follows:

1. Capture the existing text-free editor-state shell.
2. Attach transaction-local pre-mutation observers to buffers present at
   entry.
3. At a buffer's first actual text write, retain one tuple of its current line
   references; do not call `get_text()`. Keep observing only to distinguish one
   mutation boundary from several, with the counter saturated at two.
4. Run the quotation or macro under its existing history policy.
5. For changed identities, retain one after tuple. Metadata-only changes may
   share one detached tuple between before and after.
6. Record one aggregate row only when durable editor state changed.
7. On failure, restore the old tuple plus the exact version, dirty, saved,
   sidecar, registry, and history state from the shell.

Undo and Redo install the trusted tuple through
`Buffer._restore_lines_snapshot()`. They do not derive transient dirty state or
publish a misleading incremental `BufferChange`; the surrounding snapshot owns
those exact fields. The restore first notifies an active mutation observer, so
nested transactions retain the true outer entry generation.

### 2. No generic transaction registry

This remains one narrow editor-owned mechanism:

- one text-free shell;
- one per-start-buffer observer with a saturated mutation-boundary witness;
- one before tuple per actually touched buffer;
- one after tuple per changed buffer; and
- the existing broad state restore callback.

There is no new transaction graph, owner registry, rope, piece tree, persistent
revision store, or second text model. Arbitrary quotations remain exact even
when they cannot emit a composable list of text inverses.

### 3. Honest retained-text accounting

`undobytes` remains logical retained UTF-8 text accounting, not Python heap or
RSS accounting. For line-vector aggregate rows, rev0992 charges:

- the complete logical before generation;
- the after vector's logical separators; and
- after-line content not shared with the before generation.

The common one-splice path uses the buffer's existing exact `BufferChange`
witness to identify the changed after-line span without scanning every line by
identity, but only when the transaction-local observer recorded exactly one
mutation boundary and the version/geometry checks also agree. Multi-write,
rewound-history, restore, or external paths use a conservative shared
prefix/suffix fallback. The fallback may overcharge a changed middle, but never
charges more content than two complete logical documents.

An earlier audit implementation built a Python identity set proportional to the
line count. It made the accounting itself dominate the small-edit transaction
and erased much of the latency win under `tracemalloc`. That implementation was
rejected. Accounting must not recreate the resource cliff it is measuring.

Pointer arrays, tuple/list objects, snapshot dataclasses, sidecars, callbacks,
allocator arenas, native memory, and RSS remain outside `undobytes`. The release
docs say so explicitly.

## Permanent evidence

Both witnesses use eight open buffers, each 1,099,999 characters, with
`fastdirty` enabled to isolate transaction capture. They compare an executable
same-runtime eager reference with the rev0992 product. Timings are local
`tracemalloc` context, not portable latency claims.

### `ed.with-undo` success

| Metric | Eager reference | Rev0992 product | Change |
| --- | ---: | ---: | ---: |
| complete `get_text()` joins | 9 | 0 | removed |
| joined document characters | 9,899,992 | 0 | removed |
| old-content capture rows | 8 | 1 | touched buffer only |
| logical retained text | 2,199,999 B | 1,113,828 B | 49.371% lower |
| traced current Python bytes | 2,216,234 | 236,745 | 89.313% lower |
| traced peak Python bytes | 9,935,882 | 259,641 | 97.387% lower |
| elapsed median | 0.011525 s | 0.004956 s | contextual only |
| forward / Undo / Redo | exact | exact | preserved |

The product retains the complete before generation because arbitrary rollback
needs it, but it shares unchanged line strings into the after generation rather
than retaining a second complete document string.

### `ed.with-undo` failure

| Metric | Eager reference | Rev0992 product | Change |
| --- | ---: | ---: | ---: |
| complete joins | 8 | 0 | removed |
| joined characters | 8,799,992 | 0 | removed |
| traced current Python bytes | 14,178,632 | 115,360 | 99.186% lower |
| traced peak Python bytes | 22,995,344 | 246,632 | 98.927% lower |
| exact rollback | yes | yes | preserved |

### Immediate macro success, failure, and navigation

The macro witness preserves return value, final text, rollback, Undo, and Redo.
Success removes 9 complete joins and reduces traced peak from 9,937,075 B to
261,666 B (97.367%). Failure removes 8 joins and reduces traced peak from
22,999,389 B to 250,725 B (98.910%). Navigation-only replay remains outside
history and reduces traced peak from 8,827,504 B to 34,765 B (99.606%).

### Ordinary mutation seam

The transaction observer remains absent from ordinary mutation when no
aggregate is active. In the existing 150,000-cycle insert/delete microloop, the
product is 1.178% over the branch-free control. A permanent line-wrapper
prototype remains rejected at 11.618% overhead. This is a Python microloop, not
end-to-end editor latency, but it protects the hot seam from a bureaucratic
wrapper architecture.

Permanent artifacts:

- `.artifacts/rev0992-with-undo-line-vector-transactions.json`
- `.artifacts/rev0992-macro-line-vector-transactions.json`

## Correctness and regression evidence

Rev0992 adds or strengthens tests for:

- a 4,096-line `ed.with-undo` edit with `Buffer.get_text()` trapped;
- exact before/after tuple generations and untouched-line object sharing;
- exact logical UTF-8 accounting for non-ASCII text;
- failed quotation rollback with version, dirty state, saved signature, and
  history preserved;
- line-vector restore notifying an enclosing first-write observer;
- a macro that performs Undo of an existing aggregate row and then edits,
  proving the outer row starts at the true macro-entry document;
- a rewind-plus-two-separated-writes macro whose final version is exactly
  `before + 1`, proving that only an explicit one-mutation witness may use the
  `BufferChange` accounting fast path (37 B conservative charge, not 26 B);
- zero-join success, failure, and navigation witnesses for both aggregate
  owners; and
- differential retained-content labels and exact forward/Undo/Redo semantics
  against the eager reference.

The eager implementation remains test and measurement code only. It is useful as
an oracle precisely because it is too expensive to remain the product path.

## Online comparison and why Micromax stays narrower

The online references support the design direction without dictating Micromax's
representation:

- CodeMirror's `ChangeSet.invert` requires the document as it existed before the
  changes. This reinforces that exact inversion needs an authoritative prior
  generation, but CodeMirror has a composable change model that arbitrary
  Micromax quotations do not necessarily produce.
- ProseMirror models edits as invertible and mappable `Step` values chained in a
  transform. That is the right shape for structured document operations, but
  widening Micromax's arbitrary editor quotations into a universal step algebra
  would be a much larger semantic project than the measured problem requires.
- Scintilla groups nested sequences and undoes only the top-level sequence as a
  unit, while ordinary navigation is not document history. That matches
  Micromax's visible outer grouping and navigation-only macro policy.
- Python documents shallow copy as a new compound object containing references
  to existing objects, and strings as immutable sequences. Those facts justify
  a detached tuple of shared line strings as an exact in-process generation.

Sources retrieved 2026-07-29:

- CodeMirror Reference Manual: https://codemirror.net/docs/ref/
- ProseMirror Reference Manual: https://prosemirror.net/docs/ref/
- Scintilla Documentation, Undo and Redo: https://scintilla.org/ScintillaDoc.html
- Python `copy` documentation: https://docs.python.org/3/library/copy.html
- Python built-in `str` documentation: https://docs.python.org/3/library/stdtypes.html
- Python tutorial, lists and shallow slices: https://docs.python.org/3/tutorial/introduction.html

## What is still missing

This is a substantial correction, not completion of the editor mission.

1. **Sustained-use evidence is still thin.** Internal invariants are stronger
   than one lived journey spanning startup, project movement, editing, search,
   save/recovery, plugin failure, and visual hierarchy. That is now the highest
   product risk because the remaining failures may be connective rather than
   local algorithms.
2. **Line-vector snapshots are O(number of lines).** A before tuple, after tuple,
   and restore list copy pointers even for one-character edits. The measured
   documents show this is far cheaper than joined strings, but a many-million-
   line file can still make pointer generations material.
3. **One huge logical line is still monolithic.** Editing it rebuilds one Python
   string. Rev0990 separated exact-dirty hashing from line rebuilding, but a
   user-visible long-line cliff still needs reproduction before any segmented
   per-line representation is justified.
4. **Query-replace keeps one complete planning source.** That owner is delayed
   and semantically different; change it only from measured interaction
   pressure, not symmetry.
5. **The non-text shell is broad.** Exact arbitrary rollback copies cursor,
   selection, mark, register, search, option, MRU, and other sidecars. This is
   deliberate today, but a sustained journey may expose a more useful narrow
   owner.
6. **History is in-process and linear.** It is not durable, thread-safe,
   branching, collaborative, or crash-atomic. Disk/process/network/native and
   wall-clock effects remain outside aggregate rollback.
7. **Logical accounting is not a memory bound.** It excludes pointer/object
   overhead and can conservatively overcharge a multi-write middle. It is a
   visible policy unit, not a heap profiler.

## What should change next

The next revision should stop descending the same local history seam and run one
concise sustained-use journey through the editor's trust/taste/flow loop. It
should look for connective breakage, confusing feedback, visual hierarchy debt,
and failure recovery that unit tests do not reveal. The next representation
experiment should happen only if that journey or a reproduced long-line test
shows a user-visible cliff.

Do not respond to the remaining risks by introducing a generic transaction
registry, persistent undo graph, rope, piece tree, background index, or broad
cache framework. The pattern that has worked is narrower: reproduce one real
cliff, preserve one exact oracle, repair the smallest owner, measure it, and
leave explicit residuals.
