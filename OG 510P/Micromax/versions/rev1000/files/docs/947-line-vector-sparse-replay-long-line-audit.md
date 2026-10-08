# Line-vector sparse replay and very-long-line audit (rev0990)

## Why this was the next risk

Rev0989 made immediate multicursor and accepted query-replace history sparse, but
Undo and Redo still flattened the live buffer, built another complete result
string, and then split that string back into lines. The history row retained only
the changed slices, yet replay recreated two document-sized generations. That was
the clearest remaining mismatch between the mission and the implementation:
small, coherent edits should remain small in memory as well as in retained
history.

The adjacent concern was the line-vector buffer itself. Every mutation inside one
logical line rebuilds an immutable Python string. A piece table, rope, or gap
buffer would be a large architectural bet, so this revision measured insertion,
Backspace, Delete, and replacement in a 1.1-million-character logical line before
selecting a new text representation.

## Heart of the change

Trustworthy Undo must be atomic, exact, and unsurprising under pressure. Rev0990
keeps the existing sparse witness and line-oriented Buffer model, then removes
only the proven waste:

1. Resolve the sparse witness into direction-specific expected/replacement rows.
2. Build one compact line-start index over the authoritative line vector.
3. Validate every expected slice before publishing any mutation.
4. Walk the source vector once, reusing complete untouched line string objects
   and joining fragments only for touched result lines.
5. Commit the detached result vector through one owned `Buffer.replace_lines`
   mutation, preserving one version increment and one Undo action.

The flat-string replay remains as a pure reference oracle and for the exceptional
query-replace generation check. Product sparse history replay no longer calls
`Buffer.get_text()` or `Buffer.set_text()` under fast-dirty policy.

## Correctness and failure semantics

The line-vector path preserves the rev0989 contract:

- all splice coordinates are interpreted in one immutable source generation;
- adjacent deletions may undo as multiple insertions at the same zero-width
  offset, in source order;
- unrelated same-width text outside addressed slices survives;
- malformed geometry, out-of-range coordinates, or stale expected text raises
  `BufferEditConflict` before the buffer changes;
- the input vector remains untouched until the final commit;
- trailing empty lines, multiline replacement, Unicode text, empty documents,
  insertions, deletions, and replacements round-trip exactly; and
- Undo/Redo sidecars remain one coherent cursor/selection/id/primary action.

A seeded differential lane executes 2,000 plans with randomized Unicode,
newlines, insertions, deletions, replacements, adjacent ranges, and empty values.
The line-vector result must equal both the existing flat-text oracle and the
planner result in both directions. A larger development probe passed 20,000
cases before the permanent lane was selected.

A product test creates a 4,000-line buffer, records a two-cursor multiline edit,
then replaces `get_text` and `set_text` with traps. Undo and Redo still succeed,
commit exactly once each, increment the buffer version once each, and reproduce
the complete expected text.

## Permanent sparse replay witness

`tools/measure_line_vector_replay.py` and
`.artifacts/rev0990-line-vector-replay-long-line.json` compare two exact
round trips over a 1,099,999-character, 11,000-line document with 128 sparse
replacements. The reference reproduces the rev0989 shape; it is evidence only,
not a second product mode.

| Metric | Rev0989 flat reference | Rev0990 line-vector product | Change |
| --- | ---: | ---: | ---: |
| complete `get_text` calls | 2 | 0 | removed |
| complete `set_text` calls | 2 | 0 | removed |
| complete result strings | 2 | 0 | removed |
| line-vector commits | 0 | 2 | one per direction |
| complete document string generations | 4 | 0 | 100.000% reduction |
| traced current Python bytes, median | 3,838,032 | 225,440 | 94.126% reduction |
| traced peak Python bytes, median | 6,059,264 | 569,036 | 90.609% reduction |
| local elapsed, median | 0.012062 s | 0.029138 s | product is slower locally |
| exact Undo + Redo | yes | yes | preserved |

The result reuses 10,872 of 11,000 source line string objects (98.836%). The
line-vector path deliberately trades some local Python coordination time for a
large reduction in transient document-sized allocation. Timing is context, not a
portable latency claim.

`tracemalloc` covers traced Python allocation only. It does not measure RSS,
allocator arenas, native memory, operating-system pressure, or a hard bound.
The explicit call counts and exact round trip are the durable part of the
witness.

## Very-long-line attribution

The same tool executes product journeys in one 1,100,000-character logical line.
Insertion, Backspace, and Delete each perform 64 actions; replacement performs
32 selected one-character actions. Every case verifies final text and cursor,
then exact full Undo and Redo. Fast-dirty is Micromax's ordinary automatic policy
at this size; exact-dirty is the explicit reference policy.

| Operation | Fast-dirty local median | Exact-dirty local median | Exact signature passes avoided |
| --- | ---: | ---: | ---: |
| insert ×64 | 0.064644 s | 0.168649 s | 64 / 64 |
| Backspace ×64 | 0.064040 s | 0.174089 s | 64 / 64 |
| Delete ×64 | 0.060456 s | 0.162103 s | 64 / 64 |
| replace ×32 | 0.029642 s | 0.092744 s | 32 / 32 |

All eight policy/operation combinations round-trip exactly. Under exact-dirty,
Undo back to the saved generation becomes clean. Under fast-dirty, mutations
remain conservatively dirty until save, which is the documented policy rather
than a failed oracle.

The evidence separates two costs:

- immutable line-string rebuilding remains linear in logical-line length and is
  still real; and
- exact dirty tracking adds another complete signature pass after every
  mutation and was the larger repeated cost in this measured loop.

Micromax already auto-selects fast-dirty for saved baselines at or above one MiB,
so the measured product loop avoids the second pass without weakening save
correctness. This does **not** prove that immutable long-line rebuilding is cheap
at every size or workload. It proves only that this witness does not justify a
text-engine migration yet.

## Online research and design judgment

Sources were retrieved on 2026-07-29.

- VS Code's official text-buffer reimplementation describes why its original
  line array was attractive for ordinary line lookup, why extreme files forced
  a piece tree, and why real profiling overturned assumptions about the hottest
  methods. It also records the read-side and object-allocation tradeoffs of the
  new representation. That argues for measured migration, not selecting a rope
  or piece table by reputation.
  <https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation>
- Python's built-in-types documentation states that immutable sequence
  concatenation creates new objects and recommends accumulating pieces followed
  by `str.join()` for linear construction. The replay builder therefore gathers
  touched fragments and joins once per output line rather than repeatedly
  extending a complete document string.
  <https://docs.python.org/3/library/stdtypes.html>
- CodeMirror's system guide defines multi-change coordinates against the
  original document, and its `ChangeSet` reference records the source document
  length. Micromax retains the same useful invariant while additionally
  authenticating exact expected slices so unrelated same-width edits can survive
  outside the targets.
  <https://codemirror.net/docs/guide/>
  <https://codemirror.net/docs/ref/>
- GNU Emacs documents an invisible buffer gap used to accelerate nearby
  insertion and deletion. A per-line gap remains a plausible future response if
  lived Micromax evidence isolates repeated editing in one enormous logical line
  as a product cliff, but it is not free: moving edits, line materialization,
  aliases, history witnesses, search, and render consumers would all need new
  invariants.
  <https://www.gnu.org/software/emacs/manual/html_node/elisp/The-Buffer-Gap.html>

## Audit findings and refactor boundary

- **Corrected:** sparse replay retained tiny slices but reconstructed complete
  current/result strings. The product path now remains line-vector-native.
- **Corrected:** flat replay and line replay had separate validation logic during
  the first implementation pass. Direction resolution and all-row validation
  are now shared, leaving the flat path as a trustworthy oracle rather than a
  drifting duplicate.
- **Corrected:** whole-line strings outside touched geometry can now retain object
  identity through replay, reducing both allocation and copying.
- **Kept deliberately:** one atomic complete vector publication. Applying sparse
  line edits in place from right to left would reduce pointer copying but would
  make failure during commit harder to reason about and would publish multiple
  mutation boundaries unless Buffer gained a larger transaction API.
- **Kept deliberately:** the ordinary line-array representation. The measured
  long-line product path is finite and exact; changing every read/search/render
  consumer now would be riskier than the reproduced problem.
- **Not hidden:** the line-vector product is slower than the flat reference in
  this local many-line replay measurement. The gain is transient-memory shape
  and elimination of document strings, not a latency claim.

## Validation and release scope

The permanent focused lanes passed 110 core history/retention/measurement tests
and 216 multicursor/query-replace/macro tests in disjoint file sets. The doctor
preflight, 172-case portability corpus, generated effect contract, lint,
formatting, context, and structural audit also passed. A monolithic 3,439-test
run was collected but the outer cloudtainer command window terminated it before
completion; this revision therefore does not claim a complete full-suite pass.

## What remains risky

1. Genuine multi-range application still flattens source/result text during the
   initial edit plan; this revision changes history replay, not simultaneous
   planning.
2. Query-replace still owns one immutable complete planning source.
3. Exact-dirty policy can still materialize/hash complete text after replay;
   large buffers use fast-dirty by default unless explicitly overridden.
4. One enormous logical line still requires one new full line string for a
   mutation and for a changed replay result. The line-vector optimization is
   strongest when a document has many independently reusable lines.
5. `replace_lines` copies the result pointer vector before publication. A future
   owned-vector commit could remove that extra list only with an explicit alias
   contract and measured many-million-line pressure.
6. Length-changing unrelated edits before recorded offsets still make replay
   fail closed. A richer rebasing model would need stronger identity than local
   text coincidence.
7. Aggregate `ed.with-undo` and immediate macro rows still retain complete
   touched-buffer before/after generations.
8. Signed/hermetic release evidence and explicit cross-platform support remain
   incomplete.

## Highest-value next work

Use a lived product witness, not a synthetic doctrine expansion, to choose among
these two directions:

- remove complete immutable source/result planning from genuine multi-range
  editing while preserving overlap detection and exact cursor mapping; or
- reproduce a user-visible long-line cliff beyond the current automatic
  fast-dirty repair and prototype the smallest per-line segmented representation
  behind the existing Buffer API.

Do not introduce a generic transaction registry, undo tree, persistent document
revision graph, or wholesale piece-tree migration without that evidence.
