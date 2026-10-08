# Rev0984 — retained-history budget and changed-buffer transaction snapshots

## Executive finding

The heart of Micromax remains **a calm, trustworthy editor whose automation is
small enough to understand and narrow enough to attribute**. The VM, capability
model, headless contracts, worker owners, and release evidence matter only when
they make ordinary editing safer and more habitable. Rev0983 corrected the most
common undo-retention defect by replacing whole-document generations with exact
inverse splices for ordinary one-cursor edits. The highest-risk unfinished part
of that correction was ownership: history still had no measured byte policy,
and an aggregate transaction retained complete before/after state for every open
buffer even when it changed one character in only one of them.

Rev0984 closes that first ownership gap without adding an undo tree, broker,
generic registry, or text-engine rewrite:

- every undo row can declare the logical document text it retains per buffer;
- cached per-stack/per-buffer totals make status and no-op budget checks independent
  of history depth, while deque-backed prefix retirement avoids shifting every row;
- a local `undobytes` option supplies a soft per-buffer retained-text budget;
- recording a new row retires only complete oldest undo rows, never half of a
  compound edit, and consecutive mutation-compatible trim/overage feedback
  replaces its controlled tail instead of creating a second message history;
- the newest row is kept intact and an overage is reported rather than silently
  destroying the only immediate recovery path;
- `undostatus` exposes undo/redo depth, current-buffer usage/limit, and total
  accounted text;
- aggregate transactions retain full buffer state only for buffer objects that
  actually changed, while unchanged objects keep only the identity/name rows
  needed to reconstruct registry membership; and
- successful after-snapshots reuse unchanged text by buffer version and no
  longer perform an eager compatibility hash of every open document.

The default three-buffer, 4,000,000-character witness changes the retained
aggregate shape from six full-text snapshot rows and 24,000,001 retained text
bytes to two rows and 8,000,001 bytes. Median traced current allocation after
temporary snapshot owners are released falls from 24,010,323 to 8,010,799 bytes,
a 66.636% reduction. Median traced peak falls from 28,211,686 to 20,212,412
bytes, only 28.354%, because a rollback-capable transaction must still capture
an initial state for every open buffer it may mutate. That residual is now named
rather than obscured.

## Why this was the riskiest unfinished work

Rev0983 made ordinary typing cheap enough to stop retaining one complete
4,000,000-character document generation per keystroke. But the history owner
still had four contradictions.

First, it was unbounded. A compact insertion row may retain one byte, but a large
delete must retain the deleted slice; a multi-cursor or aggregate fallback can
retain complete documents. Counting rows cannot express that difference.

Second, aggregate collapse was visually honest but physically broad. A macro or
`ed.with-undo` invocation became one visible undo row, yet the row's two callback
closures held full before/after snapshots for every open buffer. With three
4,000,000-character documents and a one-character edit in the first, the row
retained roughly 24 MB of document text: before and after for all three buffers.
The unchanged buffers contributed two thirds of the retained payload.

Third, transaction capture performed hidden work even before retention was
considered. The old expression was equivalent to:

```python
getattr(buffer, "_saved_sig", buffer._text_signature(buffer.get_text()))
```

Python evaluates function arguments before calling `getattr`, so the fallback
`get_text()` and full text signature ran even when `_saved_sig` existed. The
snapshot then called `get_text()` again for the actual text field. Every open
buffer therefore paid an unnecessary full-document join/hash on every
transaction snapshot. Rev0984 captures text once, reuses the prior immutable
string when version is unchanged, and invokes the compatibility fallback only
when the attribute is actually absent. A regression replaces `_text_signature`
with a function that raises and proves the ordinary saved-signature path never
calls it.

Fourth, the first budget implementation made the memory policy itself a typing
hot-path liability: every new row rescanned all retained rows to recompute owner
totals, and prefix retirement used `list.pop(0)`, shifting the surviving history.
At steady state, a bounded history would therefore approach O(history) work per
keystroke even though its bytes no longer grew. The final implementation keeps
per-stack and per-owner totals incrementally, rebuilds them only when arbitrary
stack snapshots are restored, and stores each linear stack in a deque so oldest
row retirement is O(1). A deterministic 20,000-row probe observes zero historical
charge reads for two status queries plus a no-op budget check, and one charge read
when retiring one oldest row.

These defects mattered more than another policy registry. They sat directly on
undo, macro, and scripted transaction paths; they could consume memory in
proportion to open document size; and they weakened the promise that failed or
unwanted automation remains safely reversible.

## The accounting model

`UndoManager` remains a deliberately small linear owner. An `Edit` may now carry
zero or more frozen `RetainedTextCharge` rows:

- `owner`: an editor-owned buffer object, matched by identity;
- `label`: a user-facing buffer label captured for diagnostics; and
- `byte_count`: logical retained document text attributed to that owner.

The unit is the UTF-8 byte length with `surrogatepass`, matching the repository's
existing tolerance for isolated surrogate code points. ASCII uses `len()`
directly. Non-ASCII text is encoded in 64 Ki-character chunks so accounting does
not allocate a second full-document byte string just to measure it.

This is intentionally **logical retained text**, not `sys.getsizeof`, allocator
arena size, RSS, native memory, callback metadata, cursor vectors, or a hard
process-memory guarantee. It is exact for the dominant user-controlled payload
that current undo callbacks retain: Python strings containing document text.
The distinction is visible in code, command output, documentation, and the
measurement receipt.

Charges are produced at the existing history seams:

| History shape | Accounted text |
| --- | --- |
| compact one-cursor splice | exact old and new slices, identity-deduplicated |
| broad one-buffer snapshot | complete before and after text |
| aggregate transaction | before/after text only for changed buffer objects |
| sidecar-only row | one shared text object when a broad snapshot needs it; zero for a compact no-text splice |

Identity deduplication matters. If before and after snapshots share the same
immutable string because only cursor state changed, one object is retained and
one payload is charged. Equal but separately allocated strings are charged
separately because both remain reachable.

`retained_text_bytes()` can report all history or one owner. By default it
includes both undo and redo stacks: moving a row between the stacks does not
release its payload. Recording a new edit clears the abandoned redo branch
first, then enforces budgets, so accounting does not trim older recoverable
history to make room for bytes that have already become unreachable. Totals are
updated when a row enters, moves between, or leaves the stacks; ordinary status
and budget checks do not walk historical callbacks. Restoring an arbitrary
`UndoSnapshot` deliberately rebuilds the caches from its shared rows because
that operation already replaces stack membership wholesale and is not the
per-keystroke path.

## Budget semantics

`undobytes` is a numeric global/local option. The default is 33,554,432 logical
bytes per buffer. `0` means unlimited. A trusted user may set it globally or
locally; lower-authority scripts may read the value but may not write it. The
write restriction is not secrecy. It prevents an extension from silently
lowering recovery policy and causing trusted history to be retired by the next
edit.

The budget is soft for one reason: an undo row is the atomic recovery unit. After
recording a row, Micromax computes totals for every buffer charged by that row
and removes an oldest prefix of complete undo rows until the touched limits are
satisfied or only the newest row remains. It never:

- splits a multi-buffer transaction;
- deletes an arbitrary middle row;
- trims the redo stack while the user is traversing it; or
- silently discards the just-completed action because that one action is large.

Deleting a middle row from a global linear history can make later inverses replay
against a state they were not recorded from. Prefix removal preserves replay
chronology. A consequence is worth stating plainly: satisfying buffer A's limit
may also retire an older row for buffer B when that B row precedes the A row in
the global history. That is the honest cost of retaining one global chronological
stack. Independent per-buffer stacks would require an explicit cross-buffer
transaction ordering model, not a cosmetic refactor. Cached owner totals make
the over-budget predicate independent of history depth, and deque-backed prefix
retirement removes each expired oldest row without shifting the survivors. Once
a steady-state budget starts retiring one row per ordinary edit, consecutive trim
feedback rows that the current runtime authority may mutate are replaced as one
controlled tail. Trim counts and bytes accumulate, while overage rows describe only
the newest retained action. A lower-authority script cannot erase trusted rows; a
trusted user may replace lower-authority status just as elsewhere in the message
register.

When a single newest row exceeds its limit, Micromax keeps it whole and reports:

```text
undo: newest change kept whole for main: 70000000 > undobytes 33554432
```

When older rows are retired, it reports their count and accounted payload:

```text
undo: trimmed 3 oldest changes (4194304 retained text bytes)
```

`undostatus` provides a stable inspection seam:

```text
undo: 12 undo, 2 redo; main 1048576/33554432 retained text bytes; 1572864 total
```

This is deliberately not a hard outer-limit implementation. Destroying the most
recent recovery row can be the right last-ditch choice under genuine process
memory pressure, but Micromax does not yet have a sufficiently truthful
cross-platform memory signal or a recovery UI for that decision. The current
policy prefers immediate recoverability and exposes the overage.

## Aggregate transaction compaction

A macro or scripted transaction must be able to roll back an arbitrary failure,
including changes to multiple buffers, names, active/MRU state, marks, recent
files, saved cursors, options, and cursor sidecars. The initial snapshot therefore
remains broad. The retained successful history row does not need to remain broad
for buffers that were unchanged.

Rev0984 compares before and after snapshots by `EditorBuffer` object identity and
full snapshot value. It then builds two retained callback snapshots:

- changed objects keep complete before/after state;
- unchanged objects keep `ref` and `name` only; and
- callback-dead input and nested undo snapshots are removed as before.

Undo/redo always rebuilds the complete buffer registry and global state from the
snapshot, but it restores buffer-local payload only for the changed object IDs.
This distinction is what makes membership exact without pinning unrelated text.
It also preserves object identity, which existing history callbacks require.

New, deleted, renamed, or locally modified buffers are changed objects. A
transaction that changes only marks or MRU state retains no document text but
still keeps the small membership rows needed to reconstruct the registry.

The successful after-snapshot accepts the initial snapshot as a reuse source. If
a live buffer has the same monotonic version, its prior immutable text string is
reused while all non-text state is recaptured. Changed buffers still materialize
new text. Rollback snapshots remain complete; no failure path depends on a
post-hoc guess about what might have changed.

## Permanent witness

`tools/measure_history_retention.py` records two shapes in the same runtime:

- `changed_buffers_only`: the product path; and
- `broad_snapshot_reference`: the rev0983 retained compound-row shape, keeping
  complete before/after snapshots for every open buffer.

The reference intentionally reproduces the retained shape, not every transient
instruction of the old implementation. Both shapes use current snapshot
capture, perform the same one-character edit, release temporary `before`/`after`
owners, force collection, and then inspect the one retained undo row. Both must
complete exact undo and redo.

Default receipt (`.artifacts/rev0984-history-retention.json`):

A final archive-member audit found that the old fixed `.artifacts` allowlist
silently omitted this receipt even though the context and revision ledger named
it. Revision packaging now carries canonical `rev####-lowercase-hyphen.json`
receipts without per-revision registry edits, rejects non-object or duplicate-key
JSON, and caps each receipt at 1 MiB before provenance capture.

| Metric | Broad snapshot reference | Changed buffers only |
| --- | ---: | ---: |
| open buffers | 3 | 3 |
| characters per buffer | 4,000,000 | 4,000,000 |
| full-text snapshot rows | 6 | 2 |
| retained snapshot text | 24,000,001 B | 8,000,001 B |
| accounted retained text | n/a | 8,000,001 B |
| traced current, median | 24,010,323 B | 8,010,799 B |
| traced peak, median | 28,211,686 B | 20,212,412 B |
| exact undo/redo | yes / yes | yes / yes |

The same tool performs an 80-edit budget journey with 128-character inserts and
a 4,096-byte limit. It retains exactly 32 complete rows and 4,096 logical bytes,
retires 48 oldest rows, emits one coalesced notice carrying the exact 48-row/6,144-byte
retirement total, and exactly undoes/redoes the remaining 32-row suffix.

The same receipt includes a deterministic 20,000-row accounting probe:

| Accounting operation | Historical charge reads | Linear-rescan reference |
| --- | ---: | ---: |
| two retained-byte queries plus no-op budget check | 0 | 60,000 |
| retire one oldest row | 1 | at least one full-history scan plus retirement |

The probe does not infer complexity from wall-clock timing. Each synthetic charge
counts accesses to its byte field, so a hidden history rescan is an exact test
failure rather than a noisy benchmark regression.

Python documents `tracemalloc` as tracing memory blocks allocated by Python and
`get_traced_memory()` as returning current and peak traced block sizes. The
receipt therefore does not claim RSS, allocator arenas, native extension memory,
latency, or a portable process ceiling. It is a narrow retained-object witness,
which is exactly the question this revision changes.

## Research comparison

The implementation was checked against current primary documentation and source
on July 29, 2026.

### GNU Emacs

GNU Emacs's current `src/undo.c` counts saved text and other undo data, truncates
at undo boundaries, and normally preserves the most recent undo record. It has a
separate `undo-outer-limit` path for one “horribly big” command and warns that
without an outer limit one huge entry may exhaust memory. Current source defaults
are `undo-limit=160000`, `undo-strong-limit=240000`, and
`undo-outer-limit=24000000`.

Micromax borrows two durable ideas: measure bytes rather than only row count, and
truncate only at complete command boundaries. Current Emacs source also combines
consecutive adjacent insertions into one undo record. Micromax deliberately does
not copy that interaction policy in this revision: accounting and safe retirement
are resource-owner mechanics, while deciding how many typed characters one Undo
press should remove needs explicit cursor, motion, macro, selection, and save-point
boundaries. It also does not copy Emacs's outer-limit behavior yet. Emacs has a
mature garbage-collection and UI context for that last-ditch choice; Micromax
presently has only logical text accounting and should not imply a hard memory
guarantee.

Source:
`https://raw.githubusercontent.com/emacs-mirror/emacs/master/src/undo.c`

### Vim

Vim 9.2 documents `undolevels` as global or buffer-local and explicitly warns
that one change can already consume a large amount of memory. That supports the
need for a local policy and shows why a count alone is insufficient. Micromax
uses bytes as the primary control because its row shapes range from a one-byte
splice to two complete multi-megabyte transaction snapshots.

Source:
`https://vimhelp.org/options.txt.html` (`'undolevels'`, lines around the option)

### Python measurement scope

The Python 3.14 documentation describes `tracemalloc` as a tool for blocks
allocated by Python and defines `get_traced_memory()` as current and peak traced
sizes. The witness language follows that scope and does not relabel it as total
memory.

Source:
`https://docs.python.org/3/library/tracemalloc.html`

### Python oldest-row container

Python 3.14 documents deque appends and pops at either end as approximately
O(1), while `list.pop(0)` incurs O(n) memory movement. That distinction is
product-relevant here: once a byte budget reaches steady state, the editor may
retire one oldest row for every newly typed row. A front-removing list would make
that bounded-memory state progressively slower as the retained row count grows.
Micromax therefore keeps newest undo/redo operations at the right edge and
retires expired prefixes with `deque.popleft()`.

Source:
`https://docs.python.org/3/library/collections.html#collections.deque`

## Audit findings beyond the landed change

### 1. Peak rollback capture remains the largest transaction risk

Retained state is now proportional to changed buffers, but the initial rollback
snapshot still materializes text for every open buffer because an arbitrary
script may mutate any of them. In the default witness, retained current falls by
two thirds while peak falls by only 28.354%. The next transaction optimization
should target capture ownership, not invent a history registry.

A plausible future direction is first-write capture: a transaction installs a
small mutation journal, and each buffer/global owner records its old state only
when first mutated. That could remove all-open-buffer pre-copying. It is also
semantically risky because mutations enter through many editor, buffer, plugin,
and hostcall paths. It should be attempted only after an inventory proves there
is one interceptable mutation seam or after a narrower transaction type can use
it safely.

### 2. Broad fallback rows can still be larger than the budget

Multi-cursor edits, query-replace, specialized line plans, and aggregate changed
buffers still use complete snapshots. The byte budget prevents accumulation of
many such rows, but it preserves one oversized newest row. A 500 MB delete or
transaction can therefore remain a 500 MB recovery obligation. This is visible,
not solved.

The next exact-inverse candidate is simultaneous multi-cursor editing. It already
computes a non-overlapping source-coordinate edit plan. A compact row could retain
the old/new slices plus the full cursor sidecars, provided undo replay validates
all target slices atomically before any mutation. That is more promising than a
new text engine and directly reduces the fallback named here.

### 3. Metadata-only history is still unbounded

`undobytes` counts document text, not `Edit` objects, closures, cursor arrays,
authority snapshots, or zero-text sidecar rows. A pathological stream of
metadata-only changes can grow without crossing the byte limit. This revision
avoids pretending otherwise. Real sustained-use measurements should determine
whether a secondary row/count or estimated-overhead limit is needed.

### 4. Tiny edits are not coalesced

One typed character remains one row. The text payload is bounded, but callback
and sidecar overhead can dominate long typing sessions. Coalescing adjacent
ordinary inserts could improve both interaction and memory, but it changes the
meaning of one Undo press and interacts with selection, cursor motion, macro
boundaries, save points, and stale-target guards. It should follow a product
journey and explicit grouping rules, not be hidden inside accounting.

### 5. The global chronology has a user-visible tradeoff

A local byte limit operating on one global stack can evict an older row from
another buffer as part of the prefix. The alternative—independent per-buffer
histories plus a transaction graph—would be materially more complex. The current
tradeoff is acceptable for a small linear owner because it preserves exact
replay order and emits visible truncation. Sustained use should determine
whether the global model is actually surprising before an undo tree or per-buffer
owner is authorized.

### 6. Documentation remains too large relative to product evidence

This revision adds one deep audit because the user requested it and because the
resource contract needed exact semantics. It should not restart revision
archaeology as the main product. The next work should spend more lines in tests,
journeys, and code than in doctrine.

## What should change next

The highest-value sequence is:

1. **Complete one large retained-history journey.** Exercise a large delete and
   paste, multi-cursor fallback, save, recovery, search/replace, render, undo,
   redo, and cancellation in one bounded scenario. Record both retained text and
   user-visible outcomes.
2. **Compact simultaneous multi-cursor history if the journey confirms it is the
   dominant fallback.** Reuse the existing immutable edit plan and add atomic
   target validation; do not introduce a new history abstraction first.
3. **Measure sustained typing overhead and Undo feel.** Only then specify
   coalescing boundaries or a secondary row cap.
4. **Prototype first-write transaction capture behind one narrow path.** Keep the
   broad rollback snapshot as oracle until seeded differential tests establish
   exact equivalence.
5. **Extract a history owner only if these additions let `Editor` lose more code
   than the owner gains.** Accounting alone is not a reason to create another
   coordinator.
6. **Rebalance release evidence.** The project still needs completed sustained-use
   transcripts, explicit platform support, locked inputs, and signed provenance
   more than another general-purpose registry.

## Scope and non-claims

Rev0984 does not provide:

- a hard process-memory bound or outer-limit kill switch;
- accounting for Python object overhead, native memory, RSS, or allocator arenas;
- persistent undo, an undo tree, independent per-buffer chronology, or typing
  coalescing;
- compact inverse geometry for multi-cursor, query-replace, line-plan, or all
  aggregate transaction changes;
- copy-on-write/first-write rollback capture;
- a rope, piece table, piece tree, gap buffer, background index, broker, watcher,
  generic owner registry, Wasm host, or hostile-code sandbox; or
- Windows, filesystem, terminal, or long-duration performance evidence beyond
  the tests and Linux cloudtainer witness named in this revision.

The revision makes one resource owner honest and materially smaller. That is
forward product work: the editor can now tell a user how much document text its
history retains, retire old complete recovery units under a visible local
policy, and avoid charging untouched open documents to a one-buffer transaction.
