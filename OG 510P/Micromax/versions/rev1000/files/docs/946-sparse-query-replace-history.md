# Sparse query-replace history and local one-range rebasing

Rev0989 removes the broad delayed-history boundary from accepted query-replace
without weakening its exact buffer-generation, source-plan, authority, prompt,
selection, or stale-session behavior. It also removes the complete-document
planner from every one-range edit, including one-range hostcalls in a
multi-cursor buffer.

## Heart of the mission

Micromax is trying to become a calm editor people can trust and inhabit. A long
confirm-each replacement session is ordinary editing, not an exceptional batch
job. Each answer should therefore cost roughly the changed match and the local
sidecars—not several copies and scans of the complete document—and Undo should
remain one understandable action.

The narrow rule shipped here is:

> Plan the immutable match set once, retain exact old/new slices for accepted
> matches, and emit one atomically replayed sparse history row when the delayed
> interaction ends.

This is not a generic transaction registry, document revision graph, undo tree,
or text-engine rewrite. It repairs one measured product loop with an exact
reference and keeps the broader interaction owner intact.

## What had gone severely wrong

Rev0988's query-replace semantics were correct, but every accepted answer had a
linear document-size cost even when the match was a few characters:

1. the current match start and end were converted through two live
   cursor-to-offset scans;
2. the whole live buffer was materialized to validate one old slice;
3. the whole live buffer was copied again as the session's owned generation;
4. selecting the next planned match materialized the whole live buffer; and
5. two offset-to-cursor conversions each materialized the whole buffer again.

The final undo row then retained complete before and after document generations.
For `N` accepted matches, the reproduced answer path performs `5N - 2`
whole-document materializations. This was especially wasteful because the
planner already owned one immutable source generation and the accepted matches
were non-overlapping, ordered rows.

The permanent 1,100,000-character / 128-match witness reproduces that exact
shape: 638 answer-time complete materializations totaling 701,677,312
characters, plus 2,199,616 B of accounted retained text in two broad callback
generations. The editor was repeatedly proving the same document facts at the
wrong granularity.

## Shipped design

### One immutable planning source

`begin_query_replace()` still obtains the complete bounded match set and regex
capture expansion before capture mode begins. The exact session-start text is
retained once as `source_text`. It remains the source-coordinate oracle and the
exceptional stale-boundary reconstruction input.

The session no longer retains a broad `(text, cursors, anchors, ids, primary)`
`before` snapshot or an `owned_text` copy after every accepted answer. It retains
only:

- one immutable source string;
- the initial cursor/selection/id/primary sidecars;
- monotonic source and current offsets plus one mapped line/column cursor; and
- one exact `SimultaneousTextSplice` for each accepted text-changing match.

### Monotonic source-to-current mapping

Planned matches are ordered and non-overlapping. The interaction therefore walks
from the previous source match end to the next start exactly once. It advances
line/column geometry through bounded source spans with `str.count()` and
`str.rfind()` bounds rather than slicing the unchanged gap or rescanning the live
buffer from the beginning.

For each selected row, Micromax verifies:

- source offsets remain monotonic and inside the immutable source;
- the derived current offsets equal the planner offsets plus the accumulated
  accepted-length delta; and
- `Buffer.get_range_text()` at the derived line/column range equals the exact
  source slice.

The existing weak buffer-identity and `Buffer.version` lease remains the first
stale-state guard. The local content witness catches a mapping defect before the
wrong span can be edited. No answer or next-match selection needs live
`Buffer.get_text()` in the fast-dirty path.

### Exact accepted-slice journal

A text-changing accepted match appends one row containing:

- `old_start` / `old_end` in the session-start source;
- `new_start` / `new_end` in the final accepted-result coordinate space;
- the exact old source slice; and
- the normalized replacement slice.

Rows must remain monotonic in both coordinate spaces. Equal-text accepted rows
retain no document payload, while the interaction may still produce a
sidecar-only history action.

At completion, cancellation after accepted rows, navigation finalization, or
successful lifecycle cleanup, the owner records one `SimultaneousEditWitness`
plus exact before/after sidecars. Undo and redo first validate every addressed
slice against one immutable current text, then build and commit one result. A
stale later splice cannot leave an earlier splice half-applied, and unrelated
same-width text outside the addressed slices is preserved.

### Exceptional stale and post-hoc boundaries

Ordinary finalization trusts the refreshed identity/version lease. The rare
paths that already crossed a mutation boundary reconstruct the session-owned
result by replaying the sparse witness against `source_text` and compare that
with the supplied boundary text. This preserves the previous fail-closed rule:
an untracked interleaving edit is never silently absorbed into the delayed
transaction.

The reconstruction is intentionally exceptional. It does not restore a
per-answer whole-document copy to the common path.

## One-range edit refactor

The audit found a second avoidable full-document path. `_apply_simultaneous_buffer_edits()`
used the immutable whole-document planner whenever a buffer had secondary
cursors, even when the operation contained exactly one replacement range. There
is no overlap or ordering problem to solve in that case.

The one-range path now calls `Buffer.replace_range_with_witness()` once and maps
every cursor and retained selection anchor with local line/column geometry:

- positions before the range stay fixed;
- positions inside the range collapse to the replacement boundary according to
  affinity;
- positions on the old end map to the new end; and
- suffix lines/columns shift by the replacement's exact geometry.

A seeded 1,000-case differential test compares both left and right affinity
against the former full planner across random multiline documents, ranges,
replacements, and points. A real multi-cursor range-hostcall test monkeypatches
the full planner to fail, then proves exact text and sidecars through Undo and
Redo. The general planner remains reserved for genuine multi-range conflict and
mapping work.

## Permanent measurement

`tools/measure_qreplace_history.py` excludes initial planning and begins with the
first immutable match selected. `fastdirty` is enabled to isolate the delayed
interaction from exact small-buffer dirty hashing. The evidence-only rev0988
reference reproduces its two cursor scans, live validation, owned-generation
copy, next-match materialization, two offset conversions, and broad before/after
history. Both paths must finish with one history row and pass exact full Undo and
Redo before a report is accepted.

The committed witness is `.artifacts/rev0989-qreplace-history.json`.

| Metric | Rev0988 broad reference | Rev0989 sparse path | Reduction |
| --- | ---: | ---: | ---: |
| answer-time full-document materializations | 638 | 0 | 100.000% |
| materialized answer characters | 701,677,312 | 0 | 100.000% |
| accounted retained text | 2,199,616 B | 771 B | 99.965% |
| full-document callback generations | 2 | 0 | 100.000% |
| sparse history rows / splices | 0 / 0 | 1 / 128 | — |
| maximum callback string | 1,100,000 chars | 6 chars | 99.999%+ |
| traced current Python allocation | 2,229,353 B | 96,972 B | 95.650% |
| traced peak Python allocation | 4,432,470 B | 1,217,087 B | 72.542% |
| exact Undo / Redo | yes / yes | yes / yes | equal |

The sparse peak still includes the one immutable planning source kept live for
the interaction. Elapsed medians—1.512159 s for the reproduced broad shape and
0.048102 s for the sparse path—are local context only, not portable performance
claims. `tracemalloc` is not RSS, allocator-arena, native-memory, or a hard
resource bound.

## Failure and geometry evidence

The focused coverage includes:

- a live `Buffer.get_text()` trap after planning, proving answers and ordinary
  finalization do not materialize the complete live document;
- exact retained callback strings for a large three-match session;
- preservation of an unrelated equal-width external change during later sparse
  Undo and Redo;
- atomic refusal when only a later accepted slice is stale;
- multiline replacements, deletion, adjacent matches, skipped rows, Unicode,
  equal replacements, and secondary cursor/selection sidecars;
- a 257-match mixed accept/skip session with multiline replacement and monotonic
  source/final witness geometry;
- 160 seeded complete sessions from randomized nonzero source origins, with
  randomized decisions, multiline/Unicode source gaps, variable replacement
  geometry, and secondary cursor/selection sidecars;
- randomized bounded source-span cursor advancement versus the slice reference;
  and
- randomized local one-range cursor mapping versus the full planner.

The older compact-row retention test now advances its injected clock beyond the
rev0988 grouping window. That test is about independent row shape; changing its
witness avoids weakening the shipped typing-group policy merely to preserve an
obsolete assumption.

## Online design comparison

Primary sources reviewed on 2026-07-29 support the narrow architecture without
implying identical implementations:

- CodeMirror's `ChangeSet.invert(doc)` requires the document before a change,
  reinforcing that inverse construction belongs at the witnessed pre-change
  boundary rather than at delayed whole-document finalization:
  <https://codemirror.net/docs/ref/#state.ChangeSet.invert>.
- ProseMirror steps expose maps from positions in the old document to positions
  in the new document, matching the need to keep explicit source/result
  coordinate spaces for a sequence of edits:
  <https://prosemirror.net/docs/ref/#transform.StepMap>.
- Scintilla documents compressed typing/deleting history and nested explicit
  undo actions, supporting one user-visible row for a coherent interaction
  rather than one row per primitive mutation:
  <https://scintilla.org/ScintillaDoc.html#UndoAndRedo>.
- GNU Emacs query-replace delegates the confirm-each loop to `perform-replace`
  and consumes a live answer at each selected match. This is an interaction
  comparison only; Micromax retains its own preplanned bounded match set and
  sparse history representation:
  <https://github.com/emacs-mirror/emacs/blob/master/lisp/replace.el>.

The shared direction is to separate interaction grouping, inverse data, and
position mapping. Micromax adds exact buffer identity/version leases, captured
script authority, bounded planning, local old-text checks, and all-slice atomic
replay because those are part of its host contract.

## What remains risky

- Initial literal/regex planning still owns one immutable complete source string.
- Sparse Undo and Redo still materialize one complete current and result string
  before `Buffer.set_text()`; replay retention is sparse, replay construction is
  not.
- Exact dirty mode may still hash a small document after every accepted
  mutation. Saved buffers at or above 1 MiB visibly auto-select sticky
  `fastdirty` unless the user opts back into exact tracking.
- An unrelated length-changing edit before a recorded offset makes sparse replay
  fail closed. Same-width changes outside addressed slices can be preserved.
- Specialized line-plan history and touched aggregate macro/`ed.with-undo` rows
  still retain broader document generations for their own contracts.
- The line-vector buffer rebuilds an immutable Python line string for every
  character mutation. Very long logical lines are now the highest-value measured
  editing risk.
- History remains linear, in-process, non-durable, and single-writer.

## Highest-value next work

Profile sustained insertion, deletion, and replacement in a very long logical
line with exact text, cursor, dirty, Undo, and Redo oracles. The goal is to locate
whether Python line-string rebuilding, dirty tracking, rendering projection, or
history replay is now dominant. Change the text representation only if that
measurement proves a material lived-loop cliff and a smaller local repair is
insufficient.
