# Rev0985 — atomic sparse simultaneous history and recovery journey

## Executive finding

The heart of Micromax is not the VM, its registries, or its audit corpus. It is a
calm editor whose powerful automation remains understandable when something goes
wrong. In that product, undo is both a daily interaction and the user's nearest
recovery boundary. A multi-cursor insertion of a few characters must not quietly
retain two complete copies of a million-character document per action.

Rev0985 replaces the immediate simultaneous-edit snapshot fallback with one
sparse atomic inverse group. Every changed splice records:

- its range in the original document;
- its range in the resulting document;
- the exact removed text; and
- the exact inserted text.

Undo and redo first validate *all* addressed slices against one immutable current
text. Only after every target matches is one new document constructed and
committed. A stale later splice therefore cannot leave an earlier splice
half-undone. Cursor, selection-anchor, cursor-id, and primary-cursor sidecars
remain one exact user action.

In the permanent 1,100,000-character, eight-cursor, ten-action witness, the
rev0984 broad-history reference accounts 22,005,600 retained text bytes. The
sparse product path accounts 560 bytes: a 22,005,040-byte, 99.997% reduction.
Median traced current allocation after history construction falls from 11,052,850
to 1,180,601 bytes (89.319%); median traced peak falls from 12,157,875 to
3,384,155 bytes (72.165%). Both shapes exactly undo and redo. These are Python
`tracemalloc` and logical-text measurements, not RSS, native memory, latency, or
a hard portable memory bound.

The revision also completes a bounded lived loop across a 350,000-character file:
large multi-cursor paste, headless render validation, query-replace cancellation,
save, undo, redo, an interrupted explicit save, restart recovery, and final save.
That journey matters more than another policy layer: it proves the compact row
survives the editor surfaces it exists to protect.

## Why this was the highest-risk unfinished path

Rev0983 fixed ordinary one-cursor history by retaining one inverse splice instead
of complete document generations. Rev0984 made retained text visible and bounded
at complete-row boundaries. But the common multi-cursor path still entered the
broad fallback:

1. capture complete before text and sidecars;
2. plan and apply all cursor edits against one source generation;
3. capture complete after text and sidecars; and
4. retain both generations in the history callback.

The byte budget limited accumulation, but it did not make the individual action
cheap. One small insertion group on a large file could immediately become an
oversized newest row. Because the newest row is intentionally preserved for
recovery, the budget could only report the overage; it could not correct the
representation.

This was a better target than a new undo architecture. The simultaneous planner
already provided the hard parts:

- one immutable source-coordinate space;
- deterministic ordering;
- exact duplicate coalescing;
- rejection of ambiguous same-start and overlapping edits;
- resulting coordinates for every planned replacement; and
- one text commit plus complete cursor/anchor rebasing.

The missing piece was a compact replay witness. Adding that witness at the
existing plan/application seam gives a large product gain without an undo tree,
new transaction graph, persistent journal, text-engine rewrite, or generic owner
framework.

## Representation: two coordinate spaces, one sparse group

`SimultaneousTextSplice` stores both old and new flat offsets:

```text
old_start, old_end   address the pre-edit document
new_start, new_end   address the post-edit document
old_text             exact source slice
new_text             exact replacement slice
```

`SimultaneousEditPlan.compact_history_witness()` projects the full planning
objects into a tuple of only changed splices. Equal replacements are omitted.
That omission is important: replacing a large selection with equal text can still
clear a selection or move a cursor, but its undo callbacks never need the equal
text. The resulting sidecar-only row has zero retained document-text charge.

Both coordinate spaces are necessary. Forward replay addresses old ranges;
inverse replay addresses new ranges. Adjacent deletes demonstrate why a single
post-edit cursor is not enough:

```text
source:  a b c d
edits:     delete b
             delete c
result:  a d
```

Both inverse insertions occur at resulting offset 1. The witness preserves source
order, allowing the replay builder to insert `b`, then `c`, at the same zero-width
position without inventing sequential cursor arithmetic.

A deletion immediately followed by a replacement is another valid same-resulting-
start case: the inverse first inserts the deleted slice and then replaces the
surviving post-edit range. Validation therefore rejects overlap, not every equal
start; zero-width rows may precede the next range at the same offset.

## Atomic replay and stale-history behavior

`replay_simultaneous_edit_witness()` has two distinct phases.

### Phase 1: validate

For every splice, it selects the old or new coordinate space according to replay
direction and checks:

- offsets are ordered and inside the current document;
- the witnessed range length equals the expected slice length; and
- the current slice exactly equals the expected old/new text.

No buffer mutation occurs during this phase. A mismatch raises
`BufferEditConflict` with the splice number and geometry. `UndoManager` restores
the row to its original stack when a callback raises, so the user sees a stale
replay refusal without losing the recovery row.

This is deliberately local exact-slice validation, matching Micromax's compact
one-splice behavior. An unrelated equal-length edit outside all witnessed ranges
may survive undo. Any replay row with an empty expected source slice—undo of a
deletion or redo of an insertion—can validate coordinate geometry but has no
bytes at that zero-width point to authenticate; neighboring text remains outside
the target.
The guard is not a whole-document generation lock, and it cannot identify an
unrelated mutation that later recreates the exact expected slices at the exact
coordinates.

### Phase 2: construct and commit

After every target validates, replay walks the immutable current text once,
appending untouched spans and replacement slices to a parts list. It joins one
result and calls `Buffer.set_text()` once. Sidecars are then restored from the
before or after snapshot.

This is atomic with respect to stale text-target validation: no earlier splice is
committed before a later splice is checked. It is not a crash-atomic memory
transaction, and a Python process failure during construction remains outside the
undo contract.

## Product integration and refactor

The common seam is now `_apply_undoable_simultaneous_buffer_edits()`.

It chooses among three existing ownership shapes:

1. **One cursor, one owned edit:** retain the direct `BufferSplice`; this remains
   the smallest and most precise path.
2. **Immediate general simultaneous edit:** retain one
   `SimultaneousEditWitness` plus before/after sidecars.
3. **Live query-replace:** retain the existing broad session boundary because
   accepted answers form one delayed interaction transaction rather than one
   immediate edit call.

The sparse general path now covers ordinary multi-cursor typing, newline,
backspace/delete, tab/indent text replacement, paste, cut, and the
`ed.replace-selections`, `ed.replace-range`, and `ed.delete-range` hostcalls when
they have more than the direct-splice shape.

The refactor removed four duplicate snapshot-recording seams:

- `Cut` no longer calls a separate selection-deletion helper and manually records
  a broad row;
- `ed.replace-selections` uses the shared undoable application seam;
- `ed.replace-range` uses the shared seam; and
- `ed.delete-range` uses the shared seam.

The now-unused `_delete_selections()` helper was deleted. Clipboard and VM
operands retain their previous commit ordering: overlap or planning failure occurs
before text mutation, clipboard publication, or operand removal.

## Aggregate suppression audit — corrected scope

A deeper audit found that immediate cursor actions inside eligible macro replay or
`ed.with-undo` still called the local snapshot helper twice even though the outer
transaction suppresses and replaces those rows. Rev0985 applies such actions
directly when no query-replace session is live, eliminating two redundant local
helper calls per action.

The scope of this improvement must be stated precisely. Rev0984 had already made
`_snapshot_undo_buffer_state()` return a version sentinel under ordinary undo
suppression. Those calls copied cursor/selection/id sidecars; they did **not** copy
complete document strings when query-replace was absent. The deterministic probe
therefore reports local snapshot-helper calls falling from twenty to zero across
ten suppressed actions. It is a small allocation/control-flow cleanup, not the
large memory result of this revision.

Query-replace is explicitly excluded from the suppression fast path. Direct
commands and hostcalls may finalize that delayed interaction only after mutation,
using their pre-edit snapshot as the safe split between the accepted replacement
session and the external edit. A regression starts query-replace, accepts one
match, performs a direct range hostcall under suppressed recording, and proves the
session is closed while no local history row escapes the aggregate owner.

## Bounded product journey

The permanent journey in `tests/test_rev0985_sparse_simultaneous_history.py`
uses a 350,000-character file and crosses these boundaries in one scenario:

1. install two cursors and paste different values as one sparse history row;
2. assert the row accounts only six inserted bytes;
3. render and validate the public `micromax.screen.v1` contract;
4. enter query-replace and cancel without changing text or retained charge;
5. save the edited generation and establish it as the clean disk baseline;
6. undo exactly to the source and redo exactly to the saved generation;
7. make one further edit;
8. force the explicit save writer to fail while the private recovery journal
   captures the exact editor text;
9. prove disk still contains the last successful generation;
10. create a fresh editor, recover the journal entry into a dirty review buffer;
    and
11. save that recovered text and retire the journal entry.

This does not simulate sudden process death—the existing crash matrix owns that
claim—but it joins retained history to the real render, interaction, disk, and
restart-recovery surfaces rather than proving it only through closure inspection.

## Permanent measurement witness

Run:

```bash
PYTHONPATH=src python tools/measure_simultaneous_history.py \
  --chars 1100000 --cursors 8 --edits 10 --samples 3
```

The machine-readable receipt is
`.artifacts/rev0985-simultaneous-history.json`.

| Metric | Rev0984 broad immediate reference | Rev0985 sparse product path |
| --- | ---: | ---: |
| document characters | 1,100,000 | 1,100,000 |
| cursors × actions | 8 × 10 | 8 × 10 |
| history rows | 10 | 10 |
| accounted retained text | 22,005,600 B | 560 B |
| largest callback string | 1,100,560 chars | 7 chars |
| sparse witness splices | 0 | 80 |
| median traced current | 11,052,850 B | 1,180,601 B |
| median traced peak | 12,157,875 B | 3,384,155 B |
| exact undo / redo | yes / yes | yes / yes |

The reference uses the current simultaneous planner but records the broad
before/after history shape used by rev0984. It is evidence only, not a second
runtime mode. The measurement starts after the base editor and source document
exist, then records allocations produced while building history. It therefore
compares retained history shapes and edit-result allocations; it does not measure
full process residency.

The sparse path still materializes the complete result document while planning
and during replay. That is why peak allocation remains materially larger than the
560-byte logical history charge. Sidecar vectors, callbacks, dataclass objects,
allocator arenas, native memory, and the base document are outside `undobytes`.

## Adversarial evidence

The focused suite adds thirteen tests, including:

- 1,000 deterministic Unicode/newline edit plans with zero to ten non-overlapping
  ranges, each replayed exactly forward and backward;
- adjacent deletes whose inverse insertions share one offset;
- preservation of unrelated text after every witnessed target;
- exact multi-cursor backspace history geometry and sidecars;
- stale *later* inverse and forward targets proving every target validates before
  any undo or redo text change, plus successful replay after repair;
- a 1,100,000-character two-cursor paste retaining only three inserted bytes;
- equal multi-selection replacement retaining zero text while restoring selection
  sidecars;
- suppressed edit application bypassing redundant local snapshot-helper calls;
- the live query-replace suppression exception;
- cut and hostcall routes forced to fail if they attempt the old broad immediate
  snapshot seam;
- the render/save/undo/redo/interrupted-save/restart-recovery journey; and
- the executable measurement comparison.

Existing simultaneous-edit, query-replace interaction, and rev0984 history-budget
suites are run beside the new tests so the compact path does not silently weaken
coordinate, delayed-interaction, or budget semantics.

## Online research comparison

The design follows established edit-system shapes without importing a framework.

### CodeMirror 6

CodeMirror's `ChangeSet` represents a group of changes, stores the document
length, and applies only to a document with exactly that length:
<https://codemirror.net/docs/ref/>. That is a stronger generation precondition
than Micromax currently uses. Micromax instead validates every changed slice at
its recorded coordinates so unrelated text outside those ranges can survive.
The tradeoff is explicit: less false conflict, but no proof that the untouched
document is the original generation.

### ProseMirror

ProseMirror steps expose mappings from old positions to transformed positions and
can be inverted:
<https://prosemirror.net/docs/ref/>. Micromax's old/new coordinate pair is the
small local analogue. It does not introduce a general transform algebra because
the existing simultaneous plan already owns one immediate non-overlapping group.

### Language Server Protocol

LSP 3.17 states that text-edit ranges must not overlap and that no part of the
original document may be manipulated by more than one edit:
<https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>.
Micromax already used this source-coordinate rule. Rev0985 carries the same
validated group into inverse history instead of discarding its geometry and
falling back to whole snapshots.

### Scintilla

Scintilla exposes grouped undo actions and makes selection-history retention an
explicit option with a documented per-action memory cost:
<https://scintilla.org/ScintillaDoc.html>. Two lessons apply here. First, one
multi-cursor invocation should remain one user action. Second, cursor/selection
sidecars are real retained state even after document text becomes sparse. This
revision measures document text separately and does not pretend sidecars are free.
Scintilla also coalesces typing-like actions; Micromax deliberately postpones
that behavior until sustained typing and undo feel are measured.

### VS Code piece tree — speculation, not a mandate

VS Code's text-buffer reimplementation describes a piece table/tree that avoids
large-string concatenation and accelerates line lookup:
<https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation>.
The maintained implementation is published at
<https://github.com/microsoft/vscode-textbuffer>. This suggests a possible future
answer if Micromax's complete-result planning, very long lines, or large-file
replay remain dominant after local fixes. It does **not** justify replacing the
current line-vector buffer now. Rev0985 removes the dominant retained-history
cost without changing the text engine; future engine work should require
longitudinal latency/peak evidence and a compatibility oracle.

## Audit findings and remaining risk

### Corrected now

1. **Immediate multi-cursor history retained two complete document generations.**
   It now retains only changed slices and sidecars.
2. **A stale later splice could have been dangerous in a naïve sequential
   inverse.** Replay validates the complete group before one commit.
3. **Cut and three hostcalls duplicated broad snapshot bookkeeping.** They now
   share the same tested seam.
4. **A dead selection-deletion helper obscured ownership.** It is removed.
5. **Suppressed aggregate steps still executed redundant local snapshot-helper
   work.** Ordinary suppressed steps now apply directly; the query-replace
   boundary remains protected.

### Still open

1. **Planning and replay allocate complete result text.** Retained history is
   sparse, but peak construction is not.
2. **Query-replace remains broad.** Its accepted answers span a delayed session
   and currently own one full session before/after boundary. Compacting it needs
   a measured session-level witness, not reuse of an immediate-action row by
   assertion.
3. **Specialized line plans and arbitrary aggregate transactions remain broad.**
   Their rollback/identity semantics are more important than premature
   unification.
4. **Initial aggregate rollback capture still visits every open buffer.** A
   first-write prototype remains the most promising next memory correction, but
   broad capture must stay as a differential oracle until failure cases agree.
5. **History object count is not bounded.** Tiny typing rows are not coalesced;
   `undobytes` does not count callback/dataclass/sidecar overhead.
6. **Local slice guards are not document-generation proofs.** Coincidentally
   restored target text can pass after unrelated history. Empty-source replay—
   deletion undo or insertion redo—authenticates geometry rather than
   neighboring bytes.
7. **`Editor` remains a large coordinator.** This revision removes duplicate
   call-site bookkeeping but does not extract another owner merely to move code.
8. **Sustained-use, taste, release, and platform evidence remain weaker than
   internal correctness evidence.**

## What should change next

The next revision should remain product- and measurement-led:

1. measure sustained typing history object/sidecar cost and actual Undo grouping
   expectations before implementing coalescing or a secondary row-count limit;
2. prototype first-write transaction capture behind one narrow `ed.with-undo` or
   macro path, comparing every success/failure result with the broad initial
   snapshot oracle;
3. measure a long accepted query-replace session before deciding whether its
   broad retained row now dominates;
4. exercise the editor in a concise sustained-use lane—startup, project movement,
   editing, search, save/recovery, plugin failure, and visual hierarchy—rather
   than adding more registries; and
5. finish signed/hermetic release and explicit filesystem, terminal, and Windows
   support evidence.

Do not add an undo tree, independent per-buffer history graph, persistent undo,
piece tree, broker, watcher, background index, generic transaction framework, or
Wasm host by anticipation. The next architecture change must retire a measured
product risk and preferably delete more coordinator code than it introduces.

## Scope and non-claims

Rev0985 claims:

- compact immediate simultaneous history for the integrated edit/action/hostcall
  paths;
- exact all-target validation before one text commit;
- exact cursor/selection/id/primary sidecar replay;
- visible stale-conflict refusal with stack membership preserved;
- logical retained-text accounting for sparse groups;
- one bounded render/save/undo/redo/recovery journey; and
- the specific Linux-cloudtainer tests and measurements recorded in
  `REV0985_TESTS.md`.

It does not claim a hard memory bound, RSS reduction on every Python build,
latency bound, crash-atomic in-memory undo, persistent history, global generation
validation, complete-suite pass, signed release, or cross-platform execution.
