# Rev0983 — compact splice undo and mission audit

## Executive finding

Micromax's heart is not “a tiny Forth” and not “a maximally proven editor.” It is
**a trustworthy, inhabitable editor whose end-user automation remains small
enough to understand and narrow enough to attribute**. The language is valuable
because configuration, macros, and plugins can share one explicit model; the
editor is valuable because it forces that model to survive ordinary human work.

The incoming archive has unusually strong failure-boundary engineering. It also
has a recurring imbalance: proof, archaeology, and coordinator policy are
expanding faster than evidence that the editor is pleasant to live in. The most
severe concrete defect found in this pass was a good example. Large buffers
automatically avoided full-document dirty hashing, yet each ordinary one-cursor
edit still retained full before/after document strings in undo history. The
visible `fastdirty` repair therefore removed one per-keystroke whole-document
cost while undo quietly reintroduced a larger retained-memory cost.

Rev0983 repairs that common path with an exact inverse splice. Insert, delete,
newline, tab, and paste retain only the replaced and inserted slices plus cursor
and selection sidecars when the action is the unambiguous one-cursor case.
Multi-cursor, query-replace, scripted aggregate, and specialized line-edit
transactions deliberately keep their broader snapshots until their geometry is
made equally explicit. This is a local correction, not a rope, broker, history
framework, or editor rewrite.

## What the project is really for

The shortest honest mission remains:

> a calm editor with explicit effects, visible provenance, recoverable failure,
> bounded host work, and headless truth

That sentence has two halves that must remain in tension.

The first half is **a calm editor**. Startup, movement, editing, search, save,
undo, plugins, and failure should feel coherent enough that a person chooses the
instrument repeatedly. Taste and flow are product requirements, not rewards to
collect after every possible boundary has been formalized.

The second half is **understandable automation**. Effects should not arrive
through ambient host access; delayed callbacks should not lose provenance;
failures should leave inspectable state; expensive host work should have a named
owner and finite claim. Headless truth is the semantic oracle that lets those
properties be tested without making curses the owner of behavior.

The language and VM are therefore means, but important means. They provide one
small compositional substrate for configuration, macros, and extensions. The
editor is not merely a demo for the VM: it is the pressure test that decides
whether least-authority end-user programming can remain usable.

## Incoming datacube: measured shape

The rev0982 archive contained 1,437 files and about 16.7 MB of unpacked member
bytes:

- 998 Markdown files and 403 Python files;
- 977 files under `docs/`, about 9.26 MB;
- 136 files under `src/`, about 3.53 MB;
- 252 files under `tests/`, about 2.74 MB;
- 20 files under `tools/`, about 0.68 MB;
- 906 numbered root documentation files spanning 902 numeric prefixes; and
- duplicate numbered prefixes at 32, 735, and 752.

The incoming `src/micromax_editor/editor.py` was 32,376 lines. Its `Editor`
class occupied about 30,819 lines, exposed roughly 1,344 methods, and initialized
about 105 attributes. Name families alone included about 139 snapshot/restore,
65 authority, 75 plugin, 257 prompt, 94 buffer, and 71 cleanup/dispose/remove/
close methods. Those counts are not proof of bad design, but they show that
coordination, ownership, and lifecycle policy are still encoded through one
large object and reviewer memory.

This archive is not under-tested. The stronger diagnosis is that **internal
correctness evidence has outpaced external product evidence**. Hundreds of
focused contracts can tell us that a boundary is exact while saying little
about whether a person used the editor for a week, whether common loops became
less tiring, or whether the visual hierarchy is calm. That is an evidence-mix
problem, not an argument for fewer tests.

## The severe defect: full-document generations hidden in ordinary undo

`fastdirty` is selected visibly for saved baselines of at least 1 MiB. It avoids
rehashing the full document after every mutation, accepting sticky dirty state
until the next clean baseline. That is a reasonable local response to immutable
Python text.

But ordinary editing still did this around each action:

1. call `_snapshot_undo_buffer_state()` before the edit;
2. retain `eb.buf.get_text()` in the snapshot closure;
3. apply the edit; and
4. retain another complete `get_text()` result after the edit.

On a large one-line buffer, Python's immutable splice already allocates a new
line. Retaining successive snapshot strings then kept prior document generations
alive. Ten one-character edits in a 4,000,000-character buffer produced a median
of 40,021,417 bytes of traced current allocation in the permanent snapshot
reference, with 36,018,087 bytes of incremental retained growth after the first
edit. The largest plain string reachable through an undo callback closure was
4,000,010 characters.

That was not merely a micro-optimization opportunity. It contradicted the
resource story presented to the user: the option that advertised a large-file
editing escape hatch did not own the history path triggered by the same
keystroke.

## The correction in rev0983

`Buffer.replace_range_with_witness()` now performs one normalized replacement
and returns `BufferSplice`:

- copied start, old-end, and new-end coordinates;
- exact old and new slices;
- and whether text actually changed.

Replay can provide `expected_old_text`. If the exact target slice no longer
matches, `BufferEditConflict` refuses the inverse rather than applying a stale
position-only edit. `UndoManager` now restores stack membership when an undo or
redo callback raises, so refusal does not silently discard the only history row
that describes the attempted recovery.

The editor chooses compact history only when the geometry is unambiguous:

- undo recording is active;
- query-replace is not live;
- exactly one cursor exists;
- exactly one edit is owned by cursor zero; and
- that cursor's selection is cleared by the action.

The row then retains the inverse splice plus cursor/selection/id/primary
sidecars. Identical replacement text can still produce a sidecar-only undo row,
which is necessary when typing over an equal selection clears the selection
without changing buffer text.

The compact path covers ordinary insert, newline, backward/forward delete,
paste, and tab actions. Indent, unindent, multi-cursor actions, query-replace,
line plans, and aggregate scripted transactions retain broad snapshots. Their
existing one-coordinate-space and rollback semantics are more important than
premature uniformity.

The permanent witness, run with five samples, 4,000,000 characters, and ten
one-character edits, reported:

| Shape | Traced current, median | Traced peak, median | Increment after first edit | Largest history closure string |
| --- | ---: | ---: | ---: | ---: |
| rev0982 snapshot reference | 40,021,417 B | 46,021,103 B | 36,018,087 B | 4,000,010 chars |
| rev0983 compact splice | 4,037,597 B | 14,036,197 B | 30,834 B | 1 char |

Within this narrow `tracemalloc` witness, current traced allocation fell 89.911%,
peak fell 69.501%, and incremental retained history after the first edit fell
99.914%. Both shapes performed exact ten-step undo and redo. These are Python
allocation observations on one Linux cloudtainer; they are not RSS, native-heap,
allocator, latency, or cross-platform bounds.

The remaining peak matters: a one-line Python string splice still builds a new
4 MB immutable line and temporarily reaches about 14 MB. Compact history removes
retained document generations; it does not make the line-vector buffer a
large-file text engine.

## What is missing now

### 1. A byte-owned history policy

History depth is unbounded and history has no byte budget. Compact insertion
rows are tiny, but deleting or replacing a huge range must retain the old slice;
multi-cursor and aggregate paths still retain full snapshots. A trustworthy
editor should eventually expose a per-buffer history budget, visible truncation,
and a clear answer to whether the oldest row, whole groups, or the current save
boundary wins.

The next history work should begin with accounting, not an undo tree. Give each
row an estimated retained-text cost, measure real sessions, then add a bounded
policy whose truncation is visible in feedback. Coalescing ordinary typing may
reduce object overhead, but it must preserve exact failure and selection
semantics.

### 2. Real large-edit journeys before a text-engine rewrite

The line vector remains simple and inspectable. That is a strength until measured
work says otherwise. The residual cases to profile are:

- repeated insertion near the middle of one very long line;
- repeated edits across many short lines;
- large delete/paste undo and redo;
- multi-cursor edits with broad snapshot fallback;
- save/recovery after large histories; and
- search, replace, render, and cancellation while history is retained.

Only longitudinal product evidence should authorize a piece table, piece tree,
rope, or gap buffer. Any replacement must stay behind `Buffer` semantics, keep
exact line/cursor witnesses, and be compared against current behavior with
seeded differential journeys.

### 3. Sustained-user and taste/flow evidence

The repository contains excellent boundary tests but no equally prominent daily
use ledger. Add a small product-evidence lane: a handful of realistic editing
transcripts, interaction counts, screenshots or compact screen fixtures, and
short observations from sustained use. Track whether startup, file switching,
find/replace, selection, multicursor, macro, save/recovery, and plugin failure
feel faster and clearer.

This should not become another giant telemetry subsystem. One concise living
record per release train is enough. The purpose is to make “trust, taste, flow”
observable rather than rhetorical.

### 4. A smaller coordinator, extracted by deletion

Rev0983 necessarily adds a local history seam to `Editor`, making the giant
coordinator slightly larger. That is acceptable as an emergency correction, but
it is not the desired steady state. The next extraction should occur only when a
second concrete consumer exists—most plausibly history byte accounting or edit
coalescing—and should delete more snapshot/restore policy from `Editor` than the
new owner adds.

Do not create a generic owner registry. A narrow `BufferHistory` or edit-row
owner earns existence only if it centralizes row cost, replay guards, grouping,
and truncation while reducing coordinator methods and tests.

### 5. Support and release truth

The project now has a pinned reproducible-release workflow and declared builder
versions, which is meaningful progress. It still declares development
dependencies as ranges, has no `pylock.toml`, no public signing/attestation
path, and no explicit supported filesystem/terminal/Windows process matrix.
Archive revision and package version are intentionally independent, but that
policy remains surprising to outside users unless release notes state it
plainly.

A practical sequence is: lock the release environment, publish a small
provenance statement, sign the artifact/provenance pair, then broaden the
platform matrix. Do not claim universal durability or process-tree containment
from one Linux filesystem and process model.

## What has become wasteful

### Revision archaeology is still a parallel product

The earlier context diet was correct, yet the repository still carries 906
numbered root docs and 977 documentation files. The problem is not preserving
history; it is paying root-level discovery, audit, context, packaging, and human
attention costs for every micro-outcome. Several deep audits have rediscovered
the same themes: giant `Editor`, proof machinery as a second product, stale
living direction, sparse schema debt, and missing real-user evidence.

Future revisions should bundle related outcomes, update living contracts, and
add a numbered note only when it records a durable finding, measured correction,
or changed public contract. Mechanical micro-notes belong in the revision index
or history bundle, not automatically at the docs root.

### Proof can displace finishing

`mxtest`, audit contracts, context generation, archive verification, and release
reproduction solve real cloudtainer problems. Their danger is becoming the work
that is always easier to make exact than the editor experience. The confidence
ladder should remain explicit:

1. fast semantic and pure-model checks;
2. focused product journeys and boundary integration;
3. slower process, packaging, reproduction, and release evidence.

A new proof surface should name the product risk it retires and the maintenance
cost it adds. Passing more audit booleans is not itself a user outcome.

### Snapshot-everything is a recurring local optimum

Broad snapshots made rollback easy and were reasonable while the editor was
small. They now appear across undo, plugin transactions, interactions, owner
cleanup, and recovery state. The mistake is not using snapshots; it is allowing
them to remain the default after a measured retention or authority problem
appears. Rev0983 demonstrates the preferred migration: preserve the broad
fallback, introduce one exact narrow witness for the common case, measure it,
and expand only when another path proves the same need.

## Research implications

The online sources support the local measurements without dictating a rewrite:

- Python documents that concatenating immutable sequences creates new objects
  and repeated construction can become quadratic. That explains why source-line
  rebuilding and retained generations must be measured rather than assumed
  cheap: <https://docs.python.org/3/library/stdtypes.html>.
- GNU Emacs undo lists record inserted ranges and deleted text/positions rather
  than whole buffer generations, and group rows at command boundaries. The
  relevant lesson is inverse data plus grouping, not copying Emacs's entire
  history model: <https://ftp.gnu.org/old-gnu/Manuals/elisp-manual-20-2.5/html_node/elisp_491.html>.
- CodeMirror describes changes as `{from, to, insert}` and its `ChangeSet` can be
  inverted against the prior document. That reinforces explicit change geometry
  and document compatibility: <https://codemirror.net/docs/ref/> and
  <https://codemirror.net/examples/change/>.
- VS Code's text-buffer reimplementation moved from line arrays to a piece table
  and then a balanced piece tree after real large-file failures. Its most useful
  lesson is methodological: actual hot paths contradicted assumptions, and data
  structure plus runtime rewrite should not be combined:
  <https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation>.
- The Python packaging specification now defines `pylock.toml` for reproducible
  installation environments: <https://packaging.python.org/en/latest/specifications/pylock-toml/>.
- SLSA 1.2 defines provenance as verifiable information about where, when, and
  how artifacts were produced. Micromax's embedded receipts are a good local
  seed but not yet a distributed signed provenance claim:
  <https://slsa.dev/spec/v1.2/build-provenance>.
- WIT worlds define explicit imports and exports, and resources represent
  host-owned entities across a component boundary. This remains a useful future
  vocabulary only after Micromax's extension surface is smaller; it is not a
  reason to introduce Wasm now:
  <https://component-model.bytecodealliance.org/design/worlds.html> and
  <https://component-model.bytecodealliance.org/using-wit-resources.html>.

## Staged correction plan

### Now

- Keep compact one-cursor splice undo green across insert, delete, newline, tab,
  paste, selection replacement, stale-target refusal, and exact redo.
- Add history-cost accounting and complete large-file journeys.
- Give product evidence—startup, navigation, save/recovery, plugin failure, and
  visual hierarchy—the same release prominence as safety proofs.
- Obtain Windows process-construction/capture/tree evidence before adding Job
  Object machinery or claiming parity.

### Next

- Add a visible per-buffer history byte budget with group-safe truncation.
- Expand compact deltas to multi-edit plans only when their exact inverse and
  cursor mapping are already available; do not regress atomic overlap failure.
- Extract a history owner only when byte accounting/coalescing lets it remove
  coordinator code.
- Lock release inputs with an appropriate `pylock.toml` or equivalent exact
  builder material, then publish signed provenance.
- Compact old revision notes into history bundles and make the default docs root
  primarily living contracts and substantive audits.

### Later, only if measured

- Introduce a piece table/tree behind `Buffer` if repeated large-edit journeys
  remain unacceptable after compact history and local line-copy repairs.
- Define a small versioned extension world and consider an out-of-process or Wasm
  host only after imports, exports, values, resources, cancellation, and failure
  semantics are narrower than current `Editor` internals.
- Add a second renderer/consumer before expanding screen cell or grapheme
  contracts.

### Stop doing

- Do not add a broker, pool, watcher, background symbol index, generic owner
  registry, or rope by anticipation.
- Do not solve each retained resource with a still larger global snapshot.
- Do not describe focused cloudtainer evidence as a total-memory,
  cross-platform, or hostile-code containment claim.
- Do not let a new audit note substitute for changing a living product loop.

## Residual boundaries of this revision

Compact undo protects only the ordinary one-cursor owned splice path. It does
not bound total history, large deleted slices, multi-cursor snapshots, aggregate
script snapshots, source-line copying, RSS/native memory, allocator behavior, or
out-of-band mutations that coincidentally leave the expected text at the old
coordinates. The exact-slice guard is local, not a global document-generation
proof.

The code remains intentionally linear history. No branching undo, persistence,
cross-buffer transaction, generic edit journal, or text-engine replacement is
claimed. The repair is successful because it makes the common path materially
truer to the mission while keeping the next decisions evidence-driven.

## Reproduction

```bash
PYTHONPATH=src python tools/measure_undo_retention.py
PYTHONPATH=src pytest -q tests/test_rev0983_undo_retention.py tests/test_multicursor_edit_journey.py
```
