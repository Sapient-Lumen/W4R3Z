# Bounded typing history groups

Rev0988 turns sustained ordinary typing from one Python undo object graph per
keystroke into bounded, exact, user-visible bursts. It also audits the history
replacement seam, command boundaries, dataclass ownership, and replay geometry
rather than treating a smaller row count as sufficient proof.

## Heart of the mission

Micromax is trying to become a calm editor: typing should feel immediate, Undo
should remove an understandable burst, and keeping a file open for an ordinary
session should not manufacture thousands of tiny closures and duplicate cursor
snapshots. The point is not a generic transaction registry. The point is to
make the most common editing loop cheap and unsurprising while preserving exact
recovery.

The smallest useful rule is:

> Consecutive top-level one-character inserts, backspaces, or forward deletes
> may share one guarded splice row only while time, geometry, authority,
> buffer generation, sidecars, and action chronology remain continuous.

Everything else is a boundary.

## What had gone severely wrong

Rev0983 made each ordinary one-cursor edit compact in document-text terms: a row
retained only the inverse slice rather than two whole documents. That solved the
large-buffer text-copy cliff, but not the per-keystroke object cliff. Every
printable character still created:

- one `Edit` row;
- two callback closures;
- two complete cursor/selection/id/primary sidecar snapshots; and
- cached accounting and deque membership for a separate user-visible step.

For 10,000 adjacent ASCII characters, logical retained text was only 10,000 B,
but the independent-row path retained 10,000 rows, 20,000 sidecar snapshots,
and 160,000 callback closure cells. CPython `tracemalloc` measured 27,401,089 B
current and 27,420,822 B peak after editor/buffer construction. The logical
budget therefore told the truth about text while missing the dominant object
shape of this particular workload.

## Shipped behavior

### Conservative eligibility

Only a top-level primitive `InsertText`, `Backspace`, or `Delete` action can
produce a typing span. The edit must:

- change exactly one same-line code point;
- have one cursor, no selection, one stable cursor id, and primary index zero;
- advance the exact buffer version by one;
- match the expected before/after cursor geometry;
- carry the current runtime authority; and
- be recorded while the same top-level action serial is active.

Newline, tab, paste, selection replacement, multicursor work, nested actions,
macros, direct host mutation, and multi-code-point input remain ordinary rows.
This is intentionally narrower than every possible input method.

### Exact merge conditions

A new span joins the newest row only when all of these remain true:

- same live `EditorBuffer` identity;
- same edit kind and equal authority;
- consecutive action serials and contiguous buffer versions;
- exact equality between the prior after-sidecars and current before-sidecars;
- nonnegative elapsed time strictly below 500 ms;
- adjacent insertion/backspace/delete geometry; and
- combined payload no larger than 256 code points.

Insertion appends new text. Repeated Backspace prepends removed text while moving
the start left. Repeated forward Delete extends the original old range to the
right. The first before-sidecars and final after-sidecars are retained exactly.
Undo and redo still use `Buffer.replace_range_with_witness()` with expected old
text, so stale replay refuses without moving the history row.

### Deliberate boundaries

The following start a new user-visible history row even when text and timing
would otherwise look adjacent:

- a pause of exactly 500 ms or more;
- cursor motion, selection work, a no-op or failed action;
- any command-bar command, including Save;
- any `mx:` keybinding evaluation;
- newline, tab, paste, structural or simultaneous edits;
- a change in script/plugin authority;
- a nested action or macro replay;
- a buffer-version discontinuity or sidecar discontinuity;
- an edit-kind switch; and
- reaching the 256-code-point hard ceiling.

`run_action()` now owns a monotonic interaction serial and nesting depth. Direct
command and `mx:` dispatch cross a small explicit boundary context, preventing a
non-editing command between two characters from becoming invisible to history.

## Undo-manager refactor and audit findings

`UndoManager.replace_last(expected, edit)` is an identity-checked primitive. It
replaces only the exact newest row, updates per-owner and total retained-text
caches, and clears an abandoned redo branch just like a fresh edit. The common
redo clearing was extracted into `_clear_redo()`.

The audit found two correctness hazards while landing the feature:

1. **Dataclass ownership split.** The first placement of `TypingHistorySpan`
   accidentally ended the large `EditorBuffer` dataclass before save-recovery
   and disk-state fields. A real interrupted-save journey failed immediately.
   The span now follows the complete buffer owner, and that regression remains
   covered by the existing save/recovery suite.
2. **Lost replacement lease.** The first replacement wrapper would append the
   merged inverse if identity replacement failed. That row overlapped the still
   live prior row and could make the next Undo stale or destructive. A failed
   lease now returns to the caller, which records only the current primitive
   edit. A forced-failure regression proves two independent exact undos.

These are examples of why row-count tests alone are insufficient: both defects
could coexist with an apparently successful typing benchmark.

## Permanent measurement

`tools/measure_typing_history.py` compares the product path with the current
compact-splice runtime after disabling only automatic typing grouping. A
constant monotonic clock makes every keystroke time-adjacent. Both paths type,
undo to the exact empty state, and redo to the exact final text/cursor.

The committed 10,000-character witness is
`.artifacts/rev0988-typing-history.json`.

| Metric | Independent rows | Bounded groups | Reduction |
| --- | ---: | ---: | ---: |
| undo rows | 10,000 | 40 | 99.600% |
| retained sidecar snapshots | 20,000 | 80 | 99.600% |
| callback closure cells | 160,000 | 160 | 99.900% |
| traced current Python bytes | 27,401,089 | 146,456 | 99.466% |
| traced peak Python bytes | 27,420,822 | 168,877 | 99.384% |
| logical retained text | 10,000 B | 10,000 B | equal |

The final partial group contains 16 characters; every other row contains 256.
This is one same-runtime CPython sample. `tracemalloc` excludes RSS, allocator
arenas not attributed as traced Python allocations, and native memory. Elapsed
time is recorded as local context only and is not a portable performance claim.

## Correctness evidence

The exact boundary suite covers printable Unicode, the 500 ms equality edge,
movement and no-op boundaries, direct commands and the product `Ctrl-S` dispatch
path, newline/tab, selection replacement, multicursor edits, repeated Backspace,
repeated Delete, kind changes, the 256+1 ceiling, direct external buffer
mutation, stale replay, nested actions, authority changes, byte-budget trimming,
redo branching, forced replacement-lease loss, and manager cache accounting.

A seeded differential oracle runs mixed insert/backspace/delete/movement/no-op/
pause streams against an otherwise identical editor with grouping disabled.
State is compared after every operation. Each grouped row is then undone while
the reference undoes the corresponding primitive-row count, and the process is
repeated through redo. Text, cursors, anchors, ids, and primary cursor must match
at every group boundary.

The older rev0983 retention witness now advances a fake clock by one second per
edit so it continues to measure independent compact rows. Rev0984 budget tests
do the same where their subject is row trimming rather than grouping policy.

## Executed validation

The focused rev0983–rev0988 history lane passed 234 tests. Separate product
lanes passed default keybinding, action/command authority, hostcall transaction,
interaction authority, delayed query-replace, focused macro/command dispatch,
and interrupted-save recovery checks. `mxdoctor` passed all three bounded risk
lanes. Formatting, offline lint, bytecode compilation, current-revision audit,
generated effect/resource contract, and package-input policy checks also
passed. Optional `mypy` was not installed. This is strong focused evidence, not
a complete current full-suite claim.

## Online design evidence

Primary sources were reviewed on 2026-07-29:

- Scintilla documents that typing/deleting sequences are compressed into
  transactions for sensible Undo detail, nested transactions use the top-level
  scope, explicit begin/end markers may also isolate actions, and selection
  history has a minimum per-action memory cost:
  <https://scintilla.org/ScintillaDoc.html#UndoAndRedo>.
- CodeMirror 6 uses a 500 ms default, requires changed ranges to touch by
  default, restricts ordinary joining to joinable user events, and exposes
  `isolateHistory` before/after/full boundaries:
  <https://raw.githubusercontent.com/codemirror/commands/main/src/history.ts>.
- ProseMirror also defaults to 500 ms, always separates non-adjacent changes,
  and exposes `closeHistory()` to force a new event:
  <https://raw.githubusercontent.com/ProseMirror/prosemirror-history/master/src/history.ts>.
- Qt groups edits with nested `beginEditBlock()` / `endEditBlock()` and offers
  `joinPreviousEditBlock()` for explicit continuation:
  <https://doc.qt.io/qt-6/qtextcursor.html>.

Micromax adopts the shared direction—time plus adjacency plus explicit
boundaries—but adds a hard payload ceiling, exact version/sidecar continuity,
authority continuity, and guarded splice replay because its history also carries
script provenance and per-buffer byte budgets.

## What is still missing or risky

- The line-vector buffer still rebuilds an immutable Python line string on each
  character. Grouping removes retained object graphs, not the sustained typing
  CPU shape of one extremely long logical line.
- Code-point grouping is not grapheme-cluster or IME composition grouping.
  Multi-code-point insertions deliberately remain separate rows.
- A touched arbitrary aggregate transaction still retains complete old/new
  generations for each changed buffer.
- Accepted query-replace remains a broad delayed interaction and is now the
  highest-value measured history risk.
- Specialized planners and simultaneous replay can still construct complete
  result strings; huge logical lines remain an allocation/latency risk.
- `undobytes` remains logical retained document text, not callback, sidecar,
  dataclass, allocator, RSS, or native-memory accounting.
- History is linear, in-process, non-durable, and single-writer. It is not an
  undo tree, crash journal, thread-safe transaction log, or hostile-code
  boundary.

## What should change next

Measure a long accepted query-replace session with many answers, cancellations,
interleaving edits, and final Undo/Redo. Preserve the existing delayed-session
path as the executable oracle and compact it only if the measurement reproduces
a material retained-state or allocation cliff.

Separately profile sustained insertion into a very long line. The unchanged
elapsed cost in this revision's retained-memory work is a signal to locate the
actual mutation cost before considering a local text-engine change. Do not infer
a rope, piece table, generic transaction registry, persistent history, or undo
tree from the typing-row result alone.
