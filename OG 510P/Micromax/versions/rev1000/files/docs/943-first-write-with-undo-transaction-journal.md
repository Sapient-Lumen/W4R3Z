# Rev0986 — first-write `ed.with-undo` transaction journal

## Executive finding

The heart of Micromax is a calm editing loop whose automation remains
understandable and recoverable. The VM, capability model, inventories, and audit
artifacts matter only when they protect that loop. `ed.with-undo` is therefore a
product boundary, not merely a hostcall: it promises that a script may perform a
compound change, the user sees one undo action, and a failure leaves no partial
edit behind.

That promise was correct but severely wasteful. Before rev0986, every
`ed.with-undo` invocation joined the complete text of **every open buffer before
the quotation ran**. It did so even when the quotation only moved a cursor, set a
mark, or inserted one character into one buffer. A failing quotation then
restored every captured text through `Buffer.set_text()`, reconstructing all open
line vectors whether they had changed or not. Rev0984 had already stopped
retaining unchanged buffer text in the eventual undo row, but the initial
rollback owner—and therefore peak work—remained broad.

Rev0986 replaces that eager text capture on the narrow `ed.with-undo` path with a
first-write in-memory journal:

1. capture the transaction's non-text editor state without joining buffer text;
2. attach a one-shot pre-mutation observer to each buffer that exists at the
   start;
3. join a buffer's old text only immediately before its first actual mutation;
4. capture after-text only for buffers whose state or membership changed; and
5. retain the same changed-buffer undo row used by rev0985.

The broad snapshot implementation remains executable as a differential oracle
and continues to own macro replay. This is deliberately not a generic
transaction framework.

In the permanent eight-buffer, 1,000,000-character-per-buffer witness, a
one-character successful transaction changes these measured temporary capture
costs:

| Metric | Eager reference | First-write product |
| --- | ---: | ---: |
| complete text joins | 9 | 2 |
| joined characters | 9,000,001 | 2,000,001 |
| old-text journal rows | 8 | 1 |
| median traced peak | 9,035,339 B | 2,038,868 B |
| median transaction time | 0.039639 s | 0.006187 s |
| retained undo text | 2,000,001 B | 2,000,001 B |
| exact undo / redo | yes / yes | yes / yes |

The peak reduction is 77.435%; joined text falls 77.778%. Retained history is
intentionally identical: this revision corrects temporary rollback ownership,
not the rev0984 changed-buffer retention shape.

The same edit followed by failure is more revealing:

| Metric | Eager reference | First-write product |
| --- | ---: | ---: |
| complete text joins | 8 | 1 |
| joined characters | 8,000,000 | 1,000,000 |
| old-text journal rows | 8 | 1 |
| median traced current after rollback | 12,870,296 B | 1,613,616 B |
| median traced peak | 20,886,816 B | 2,634,393 B |
| median transaction time | 0.093749 s | 0.014485 s |
| exact rollback / empty history | yes / yes | yes / yes |

The failure path now leaves untouched buffers' original line vectors in place
rather than rebuilding them from snapshots. The 87.387% traced-peak reduction is
Python `tracemalloc` evidence, not an RSS, allocator-arena, native-memory,
portable-latency, or hard-memory bound.

## Why this was the highest-risk unfinished work

The preceding revisions made ordinary undo sparse, made retained bytes visible
and bounded, and made simultaneous multi-cursor history sparse and atomic. Those
changes exposed the next cliff clearly: aggregate rollback still owned every
open document before it knew whether the quotation would touch any of them.

That cliff was especially harmful because it appeared at the exact point where a
plugin or script was trying to be a good citizen by grouping visible work into
one undo action. More open buffers meant more copying even when the operation was
local. A mark-only transaction could join megabytes of text and then retain zero
text. A failure could churn every large line vector while rolling back one small
edit. The cost was proportional to open workspace size, not mutation size.

The repair is small enough to reason about and broad enough to matter. It avoids
an undo-tree migration, a text-engine replacement, a persistent journal, a
background owner, or a registry of transaction participants. It uses the
existing buffer object identity, monotonic version, exact snapshot shell, undo
budget, and rollback restoration code.

## State shell versus text journal

`MacroReplaySnapshot` remains the one exact editor-state shape. Each buffer row
now says whether its `text` field is materialized. Ordinary macro snapshots keep
the historical eager default. A first-write shell stores an empty text field and
`text_captured=false`, while still capturing:

- buffer object identity, name, path, dirty mode, version, and saved signature;
- cursor, selection, cursor-id, primary-cursor, goal-column, selection-stack,
  and jump-list state;
- active buffer, MRU, marks, recent files, saved cursors, search state, and
  authority sidecars; and
- the pre-transaction undo snapshot.

The shell is broad because arbitrary hostcode may change those small state
surfaces. The expensive document strings are lazy.

`FirstWriteTransactionJournal` owns the shell and a map from buffer object ID to
old text. Every buffer present at transaction start receives a one-shot observer.
The first mutation joins the current text and stores it under that identity. The
observer disarms only after capture succeeds. If `get_text()` or the callback
fails, the mutation is not attempted and the observer remains armed for a retry.

New buffers need no old text. Removed unchanged buffers can materialize their old
text at finalization because their original object is still reachable through the
shell. A removed buffer that was mutated already has a first-write row. A
metadata- or cursor-only buffer change may share one current string between the
before and after states. A mark-only transaction materializes no buffer strings
at all.

At finalization, Micromax captures another text-free shell, computes changed
buffer identities, and materializes only the required before/after strings. Any
initial buffer whose version changed without a first-write row fails closed. The
same invariant is checked before rollback. This keeps the old broad snapshot as
a compatibility oracle while making missed owned mutation impossible to silently
commit through the new path.

## Mutation boundary audit and refactor

Lazy rollback is only trustworthy when old text is captured before every owned
write. The audit covered every `Buffer._lines` mutation and every direct source
mutation of `Buffer.lines`.

`Buffer.observe_before_text_mutation()` is now the common pre-write seam. The
owned mutations call it immediately before assignment or splice:

- `set_text()`;
- single- and multi-line `insert()`;
- single- and multi-line `delete_range()`;
- witnessed range replacement;
- complete line-vector replacement;
- line delete; and
- line duplicate.

The line-oriented source planner was the one editor-owned bypass. It previously
performed `eb.buf.lines[:] = lines` and then called `touch_external()`. That is
too late for first-write capture: the old generation is already gone when the
notification runs. Rev0986 adds `Buffer.replace_lines()` and routes the line plan
through it, giving the operation one pre-write witness, one mutation, and one
version/dirty update. A source scan now finds no editor-owned direct line-vector
writes outside `Buffer`.

`Buffer.lines` remains mutable for compatibility. During an observed transaction,
a caller retrieving it receives a live `MutableSequence` view whose index,
slice, insertion, deletion, append, extension, clear, pop, remove, reverse,
sort, and in-place multiplication operations announce the pre-write boundary.
Outside a transaction, `Buffer.lines` is still the exact raw backing `list`.

That last detail protects the ordinary editing hot path. An initial prototype
made the line vector a permanent Python list subclass. The permanent witness now
measures that rejected shape at 1.073525 seconds versus 0.963281 seconds for the
branch-free control across 150,000 insert/delete cycles: 11.445% slower. The
shipped raw-list plus cold empty-observer branch measures 0.975788 seconds,
1.298% above the control in the same five-sample microloop. This is not an
end-to-end latency benchmark, but it prevented an optimization for rare aggregate
transactions from taxing every keystroke.

A Python embedder that retained the raw list *before* observation may still mutate
that stale alias without crossing the view. That unsupported hostile-alias case
remains explicit residual risk. Editor-owned paths do not retain such aliases.

## Atomicity corrections beyond memory

The old hostcall rolled back quotation failures, but after-state capture and undo
recording happened outside the rollback `try`. A failure during finalization
could therefore leave successful quotation edits in place without a completed
transaction row.

Rev0986 treats finalization as part of the transaction. Failure while materializing
after-state or recording the aggregate undo row restores:

- the first-write text journal;
- the pre-transaction editor state;
- the pre-transaction undo snapshot; and
- the VM data stack captured after consuming the hostcall operands.

The regression injects a failure *after* the record helper has added an undo row
and proves editor state, history depth, and VM stack return to their pre-call
values. This is an in-process exception guarantee. It does not claim process-crash
atomicity, message-log rollback, or durable storage.

Nested `ed.with-undo` remains one outer user action. Both observers see the first
write, but the inner row is suppressed by the outer owner; the top-level before
and after states replay exactly.

## Permanent measurement witness

Run:

```bash
PYTHONPATH=src python tools/measure_first_write_transactions.py \
  --output .artifacts/rev0986-first-write-transactions.json
```

The tool executes the eager and first-write control flows inside the same current
runtime. It enables `fastdirty` so exact dirty hashing does not obscure
transaction capture. The success cases both use the current changed-buffer row,
which is why retained bytes match. The failure cases both restore the exact old
state and retain no row. Complete-string join calls and characters are counted at
`Buffer.get_text()` during the measured transaction.

The machine-readable receipt is
`.artifacts/rev0986-first-write-transactions.json`.

## Adversarial and differential evidence

`tests/test_rev0986_first_write_transactions.py` contains 92 tests. The most
important boundaries are:

- every owned buffer mutation captures the old text and old version before
  writing;
- a failed capture blocks the mutation and leaves the one-shot observer armed;
- ordinary buffers expose the raw list, while an active transaction exposes the
  observed view only until first write;
- index/slice assignment, deletion, insert, append, extend, clear, pop, remove,
  reverse, sort, in-place add, and in-place multiply all announce before writing;
- defensive empty-vector canonicalization in line delete/duplicate also announces
  before changing the backing vector;
- three large untouched buffers are monkeypatched so any accidental text join
  fails the transaction test;
- a mark-only transaction is forbidden from joining any buffer text and retains
  zero text while undoing and redoing the mark;
- forty seeded successful mixed-buffer operations compare first-write state,
  retained charges, undo, and redo against the eager oracle;
- twenty seeded failures compare exact rollback and history against the eager
  oracle;
- direct line-view mutation during observation is still transactionally
  reversible;
- nested transaction grouping yields one outer row;
- a large quotation failure restores text, version, dirty state, history, and VM
  stack; and
- injected finalization failure restores the prior row stack as well as editor
  state.

The focused transaction, macro, hostcall, line-plan, multi-cursor,
simultaneous-edit, rev0984 history-budget, rev0985 sparse-history, and rev0986
union completes 212 tests. Publication evidence records only the commands that
were actually run.

## Online research comparison

The design borrows narrow ideas, not claims, from mature systems.

### Qt edit blocks: user-visible grouping

Qt's `QTextCursor.beginEditBlock()` groups a series of document operations so
they appear as one undo/redo operation, and nested blocks take their scope from
the top-most pair:
<https://doc.qt.io/qt-6/qtextcursor.html#beginEditBlock>. That matches
Micromax's user-facing `ed.with-undo` contract and nested behavior. Qt does not
imply that Micromax must copy every document before opening the block.

### SQLite rollback journals: original state at first write

SQLite describes writing the original content of pages that will be altered to a
rollback journal before changing them:
<https://www.sqlite.org/atomiccommit.html#creating_a_rollback_journal_file>.
The useful analogy is ownership timing: preserve original state before the first
write to the unit that needs rollback, rather than copying every possible unit in
advance.

Micromax is much weaker and narrower. Its unit is currently a complete touched
buffer, the journal is ordinary process memory, there is no checksum, fsync,
lock, crash recovery, or durable commit marker, and stale raw aliases are not a
concurrency boundary. The comparison explains the first-write shape; it does not
confer database atomicity.

### CodeMirror change inversion: pre-change information is necessary

CodeMirror's `ChangeSet.invert(doc)` requires the document as it existed before
the changes: <https://codemirror.net/docs/ref/#state.ChangeSet.invert>. That
reinforces the timing requirement: inverse information cannot be reconstructed
reliably after arbitrary mutation unless the old generation or exact removed
slices were captured first.

Micromax's immediate one-cursor and simultaneous-edit rows already retain exact
slices. `ed.with-undo` is more general: quotations may create, close, rename, or
change multiple buffers and global registers, so rev0986 keeps one complete old
string per touched pre-existing buffer rather than pretending every operation can
already emit a sparse composable inverse.

## What remains missing or risky

This revision removes the workspace-size multiplier from `ed.with-undo`; it does
not finish transaction or history work.

- A one-character aggregate edit in one million-character buffer still owns the
  complete old and new text for that changed buffer. Immediate editor actions are
  sparse, but arbitrary quotations do not yet emit a composable edit journal.
- Macro replay still takes an eager all-open-buffer rollback snapshot. It remains
  the broad differential oracle and should only migrate after a macro-specific
  failure/authority measurement.
- Accepted query-replace sessions retain their broader delayed transaction
  boundary. They need their own measured compact representation rather than an
  assumption that immediate edit witnesses compose safely across interaction
  time.
- The non-text shell still copies cursor, selection, jump, and small global state
  for every open buffer. Text dominated the measured case, but pathological
  sidecar stacks could become the next aggregate cost.
- A raw line-list alias retained before observation can bypass first-write
  capture. Public callers must obtain `lines` inside the operation and call
  `touch_external()` after unsupported direct mutation; private `_lines` access
  is outside the application boundary.
- The observer seam is single-process and not thread-safe. Micromax does not
  claim concurrent writers.
- The journal is not durable. Process death remains the job of save/recovery
  infrastructure, not in-memory undo.
- Sustained typing coalescing and undo feel are still unmeasured. Fewer objects
  are not automatically a better editing experience.

## What should change next

The next aggregate work should be chosen by measurement, not by extending this
journal into a framework. A macro witness should count all-open-buffer joins and
failed-replay reconstruction under realistic recorded actions. If it reproduces
this cliff, macro playback can reuse the first-write owner while preserving the
current broad path as oracle. Accepted query-replace should be measured
separately because delayed user interaction and external interleaving make its
boundary different.

After those two aggregate paths, sustained typing deserves product-level work:
measure row count, object retention, and the feel of undo breaks across pauses,
movement, paste, and script boundaries before adding coalescing.

Do not add a generic transaction registry, independent per-buffer history graph,
undo tree, persistent journal, piece table, background worker, or new policy
layer merely because this seam exists. The useful direction is fewer complete
copies and stronger lived recovery with the smallest owner that can prove it.
