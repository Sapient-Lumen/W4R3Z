# Line-vector genuine multi-range planning audit (rev0991)

## Executive finding

Micromax's genuine multi-range edit path had become the last immediate-edit
hot path that converted the canonical line vector into one complete source
string, constructed one complete result string, split that result back into
lines, and then scanned the result again for cursor mapping. The sparse Undo row
was already compact, so this transient whole-document work was pure planning and
publication overhead.

Rev0991 removes that shape without changing the text engine or weakening the
one-source-generation rule. Genuine multi-range edits now:

- snapshot canonical line objects by reference;
- build one compact source line-start index;
- resolve every request into original-generation flat offsets;
- coalesce exact duplicates and reject ambiguous overlap before mutation;
- build one detached result line vector, joining only touched output lines;
- preserve complete untouched line string objects;
- retain only exact changed old/new slices when immediate history needs them;
- publish through one `Buffer.replace_lines()` mutation; and
- map owners, passive cursors, and selection anchors through the same compact
  edit geometry used by the flat reference planner.

The flat planner remains executable as a differential oracle. This is a narrow
repair of a reproduced product cost, not a rope, piece-tree, transaction
framework, owner registry, or second document model.

## Heart of the mission

The editor should make a small user action feel small while preserving trust:
all ranges must mean the same thing, ambiguous edits must fail before visible
state changes, Undo must remain exact, and implementation machinery must not
quietly multiply work with document size.

Micromax's real mission is not maximal abstraction. It is a calm, serious,
scriptable editor whose effects, provenance, failure, and resource costs remain
inspectable. Here that means preserving original-coordinate multicursor
semantics and one atomic publication while deleting a document-sized detour.

## Why this was the highest-risk unfinished path

Rev0989 made one-range edits local. Rev0990 made sparse grouped Undo/Redo
line-vector-native. That left one conspicuous asymmetry: the initial application
of two or more ranges still called `Buffer.get_text()`, planned over a complete
immutable string, produced another complete string, and called
`Buffer.set_text()`.

This was risky for three reasons:

1. It sat directly in typing, paste, newline, deletion, indentation, and range
   hostcall journeys whenever more than one cursor was active.
2. It defeated the memory-shape improvements already made in sparse history.
3. It encouraged a false choice between tolerating whole-document copies and
   replacing the entire line-array text engine.

A lived 1,099,999-character / 11,000-line / 128-edit witness reproduced material
pressure, so the planner—not the text representation—was the correct boundary to
change.

## Shipped implementation

### One shared geometry core

`_build_indexed_edits()` now owns duplicate coalescing, owner validation,
overlap refusal, source/result offset geometry, and owner destinations for both
planners. `_map_offset_through_indexed_edits()` and
`_compact_history_witness()` likewise keep mapping and sparse inverse semantics
shared. The flat planner is therefore a useful oracle rather than a drifting
second interpretation.

Every request is clamped against one pre-edit source generation. Exact duplicate
ranges and replacement text coalesce while retaining all distinct owners. Any
other same-start or overlapping pair fails before result construction or buffer
mutation. Adjacent ranges remain valid.

### Canonical line-vector result construction

`_LineVectorReplayBuilder` is now shared by sparse history replay and immediate
multi-range application. It walks source coordinates monotonically, emits
replacement fragments, and joins only a touched output line. A complete source
line encountered with no pending fragment is appended by exact object reference.

The result is detached before publication, preserving the previous all-or-none
planning boundary. `Buffer.replace_lines()` remains the single mutation witness,
so one user action produces one version increment.

### Exact sidecars without result text

Flat offsets remain the compact mapping currency. The product path retains a
source and result line-start array, then converts mapped offsets directly back to
line/column coordinates. It does not need a complete result string to position
cursor owners, passive cursors, or anchors.

### No discarded history slices

Immediate sparse history needs exact old text only for changed ranges. Rev0991
first compares a source range against normalized replacement text in place. An
equal replacement is a sidecar-only action: it retains no text, allocates no
source-range copy, builds no result vector, and still records exact before/after
cursor and selection sidecars when those change.

The audit also found a subtler net-zero case: individually changing adjacent
rows can compose back into the exact source document, such as deleting one line
separator while an adjacent normalized insertion restores it. The line planner
now compares the completed result vector against the source without flattening.
An exact aggregate cancellation reuses the source vector and line index, emits
an empty text witness, and remains sidecar-only through application, Undo, and
Redo. The flat oracle applies the same final-generation rule.

When an outer `ed.with-undo` or macro transaction suppresses per-action history,
changed ranges are also compared in place and no per-action old slice is
captured. The outer transaction remains the broad rollback/Undo owner. This does
not remove that owner's complete touched-buffer generation; it removes a nested
copy that would be discarded.

## Permanent measurement

`tools/measure_multirange_planning.py` and
`.artifacts/rev0991-line-vector-multirange-planning.json` compare the exact
rev0990 application shape with the rev0991 product path. Both cases plan 128
same-generation replacements in a 1,099,999-character, 11,000-line document,
map 131 cursor and 131 anchor sidecars, capture the same 128 sparse history
splices / 768 retained text characters, publish one edit, and prove exact result,
Undo, and Redo.

| Metric | Rev0990 flat reference | Rev0991 line-vector product | Change |
| --- | ---: | ---: | ---: |
| complete `get_text` calls | 1 | 0 | removed |
| complete `set_text` calls | 1 | 0 | removed |
| complete result strings | 1 | 0 | removed |
| complete document-string generations | 2 | 0 | 100.000% reduction |
| line-vector commits | 0 | 1 | one atomic publication |
| traced current Python bytes, median | 2,840,512 | 226,168 | 92.038% reduction |
| traced peak Python bytes, median | 4,162,760 | 631,536 | 84.829% reduction |
| reused source line objects | 0 | 10,872 | 98.836% of lines |
| local elapsed, median | 0.027934 s | 0.026075 s | contextual only |
| sidecars/history/result/Undo/Redo | exact | exact | preserved |

The sidecar digest is identical between paths. The product path is faster in
this local run, but no portable latency improvement is claimed: CPython version,
allocator state, hardware, and fixture shape all matter. The durable evidence is
zero complete planning/publication strings, exact behavior, and materially lower
traced allocation.

`tracemalloc` covers traced Python allocation. It does not bound RSS, allocator
arenas, native memory, callbacks, sidecars, operating-system pressure, or a
portable hard limit. `Buffer.replace_lines()` still copies the result pointer
vector before taking ownership.

## Correctness evidence

The permanent rev0991 tests include:

- 2,000 seeded Unicode and multiline plans differentially equal to the flat
  planner for result text, source/result lengths, owner offsets, sparse history,
  left/right position affinity, and text-change classification;
- a 5,000-line product action with `get_text()` and `set_text()` replaced by
  traps, proving one commit for application, Undo, and Redo and exact untouched
  line-object reuse;
- exact duplicate-owner coalescing;
- overlap refusal before result construction;
- equal multiline replacements that allocate neither source-range text nor a
  result vector;
- adjacent component edits that cancel to the exact source generation and
  therefore publish no text during application, Undo, or Redo;
- changed-range-only history capture; and
- suppressed aggregate application that cannot call the old-range materializer.

A separate development fuzz probe matched the flat oracle across 30,000 plans,
including Unicode, reversed ranges, LF/CR/CRLF replacement normalization, both
history-capture modes, and up to twenty edits. The permanent test remains the
smaller deterministic lane.

## Online research and design judgment

Primary sources were retrieved on 2026-07-29.

- CodeMirror's state package describes an immutable tree-shaped document with
  efficient offset/line indexing, structure-sharing updates, and iteration over
  document parts without copying or concatenating one large string. Its
  `ChangeSet` API also carries the pre-change document length. Micromax keeps
  its simpler line array, but adopts the narrower lesson that multi-change
  geometry and traversal do not require flattening the whole document.
  <https://github.com/codemirror/state/blob/main/src/README.md>
  <https://codemirror.net/docs/ref/#state.ChangeSet>
- VS Code's official text-buffer reimplementation records both why line arrays
  are attractive for ordinary line lookup and why extreme line counts led to a
  piece tree. It also warns that unnecessary line-content/sub-string creation
  is wasteful and says real profiling overturned assumptions about the hottest
  methods. Rev0991 removes the reproduced planner copies without treating that
  result as permission for a text-engine migration.
  <https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation>
- Python's built-in-types documentation states that repeated concatenation of
  immutable sequences creates new objects and can become quadratic, and advises
  accumulating strings for one `str.join()`. The shared builder therefore joins
  fragments once per touched output line while complete untouched line objects
  pass through directly.
  <https://docs.python.org/3/library/stdtypes.html#common-sequence-operations>

These sources support the data-shape direction, not Micromax's measured numbers
or correctness claims. Those come from the checked-in differential tests and
machine-readable local witness below. The inference remains deliberately narrow:
original-generation change geometry and piecewise construction are useful;
a piece tree is not yet proven necessary for Micromax's present workload.

## Executed validation

The final source generation passed 290 history, simultaneous-edit, retention,
transaction, measurement, and rev0991 tests, followed by 104 adjacent
query-replace, macro, line-geometry, typing, and feature tests in a disjoint file
batch. Living-document/context/effect checks passed 21 tests, and archive,
handoff-manifest, and evidence-tool checks passed 61 tests. The doctor preflight
passed its 19 + 9 + 3 bounded lanes; the portability corpus passed all 172
cases; formatting, lint, structural audit, generated effect/resource contracts,
and context checks passed.

The resumable release manifest is current but deliberately partial: one clean
four-file batch records 12 passing tests, with 64 batches not run. This revision
makes no complete-full-suite, signed, hermetic, Windows, terminal, or sudden-
power-loss claim.

## Audit findings

### Corrected

- Genuine multi-range application no longer flattens the complete source.
- Planning no longer owns a complete result string or splits it back into lines.
- Cursor/anchor mapping no longer scans a complete result string.
- Exact duplicate, overlap, mapping, and witness logic is shared with the flat
  oracle.
- Complete untouched line strings retain object identity.
- Equal replacements no longer allocate discarded old slices, even when history
  capture is enabled.
- Component edits that cancel to the exact source generation no longer create a
  false dirty/version transition or retain replay-dead component text.
- Suppressed aggregate actions no longer capture discarded per-action old text.
- The measurement tool now retains exact source objects when checking identity,
  avoiding allocator-address-reuse false positives, and emits a compact sidecar
  digest instead of thousands of coordinate rows.

### Kept deliberately

- One detached complete line-pointer vector is built before one atomic commit.
- `Buffer.replace_lines()` copies that pointer vector to preserve alias safety.
- The authoritative line-array representation remains unchanged.
- Query-replace retains one immutable planning source because its interaction
  spans time and buffer generations rather than one synchronous action.
- Aggregate `ed.with-undo` and immediate macro rows retain complete old/new text
  for each touched buffer because arbitrary quotations do not yet emit
  composable sparse inverses.

## What remains missing or risky

1. A touched aggregate transaction can still retain complete old and new
   generations. This is now the clearest remaining document-sized history owner
   and should be measured from a real macro or `ed.with-undo` pressure case.
2. Query-replace still retains one complete immutable planning source for the
   duration of the interaction.
3. One enormous logical line still rebuilds one immutable Python string per
   mutation. Rev0990 showed exact dirty hashing was the larger repeated cost in
   its witness, not that long-line rebuilding is harmless at every scale.
4. `replace_lines()` still copies a complete result pointer vector. An
   ownership-transfer API needs a concrete many-million-line failure and an
   explicit alias contract.
5. Exact-dirty policy may still materialize/hash complete text after the commit;
   large saved buffers default visibly to fast-dirty unless overridden.
6. Length-changing unrelated edits before recorded sparse offsets still fail
   replay closed rather than rebase.
7. Internal correctness evidence remains stronger than sustained-use, visual
   taste, platform, filesystem/terminal, and signed/hermetic release evidence.

## Highest-value next work

Measure aggregate transaction retention with one real `ed.with-undo` or
immediate-macro journey that changes a small slice of a large buffer. Preserve
rollback and arbitrary-quotation semantics; do not create a generic transaction
registry. In parallel, add one concise sustained-use journey spanning startup,
project movement, edit/search, save/recovery, plugin failure, and visual
hierarchy. A text-engine migration remains contingent on a reproduced user cliff
that the existing fast-dirty and line-vector corrections do not solve.
