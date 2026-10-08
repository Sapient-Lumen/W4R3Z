# Popen startup ownership and sparse editor hot paths (rev0982)

Rev0982 closes the next availability gap exposed by rev0981 and removes three
measured allocation cliffs from ordinary editor work. The common principle is
small, exact ownership: own the blocking phase a timeout claims to bound, and
retain only the coordinates later consumers actually need.

## Why this was the highest-risk unfinished work

Rev0981 made `multiprocessing.Process(...)` plus `Process.start()` caller-finite,
but the editor still constructed synchronous `subprocess.Popen(...)` objects on
the caller thread. Regex workers, browser launch, `ed.shell`, and bounded argv
execution therefore advertised timeouts that began only after process creation
returned. Python's subprocess documentation explicitly notes that initial
process creation cannot be interrupted on many platform APIs; a timeout may not
be observed until creation finishes.

At the same time, allocation measurements found product-path costs that grew
with coordinate count rather than visible work:

- true wordwrap could retain one Python integer/list cell per visual row;
- a cold 100,000-match literal search built tuple/int object graphs for line
  starts, span pairs, and duplicated start/end projections;
- complete replacement planning retained rich line/column/sample metadata for
  every match and repeatedly rescanned prefixes for sample coordinates;
- multicursor planning reboxed a caller-owned line-start index immediately
  before using it.

These are not abstract data-structure concerns. They sit in find, replace,
multicursor, and rendering loops—the lived editor mission—so they outrank a new
registry, generic broker, or speculative Wasm layer.

## Synchronous subprocess construction

### One deadline across construction and use

`micromax.subprocess_start.start_subprocess_with_deadline()` gives one temporary
daemon starter ownership of the synchronous constructor. Waiting for an earlier
unresolved constructor and running the new constructor consume one absolute
monotonic deadline. Callers then pass that same deadline into readiness or
execution:

- regex worker construction and its newline readiness handshake share one
  startup lease;
- bounded argv and shell construction and their process execution/capture share
  one operation lease.

A constructor that returns after the deadline never becomes caller-owned, even
if event wakeup and scheduler timing race near the boundary. Startup failure is
separate from timeout, preserving caller-visible mappings (`127` for unavailable,
`124` for timeout in process capture; protocol versus startup-timeout errors for
regex work).

### One unresolved constructor, not one thread per retry

A module-local gate permits at most one unresolved `Popen` constructor. Normal
constructors release it immediately after returning; running child processes are
not serialized. If a platform call never returns, later operations wait only
inside their own deadline and do not accumulate starter threads.

When the deadline wins, the starter remains sole owner. Any process that appears
later is terminated and reaped; Micromax capture-pipe descendants are released;
parent streams close; only then does the gate reopen. The deterministic witness
in `tools/reproduce_subprocess_start_stall.py` proves raw synchronous blocking,
bounded first and second callers, no second constructor invocation, late cleanup,
and successful later startup.

### Interruption-safe ownership transfer

The final ownership audit found two smaller but serious handoff windows. First,
an asynchronous interruption could arrive after `Popen` returned but before the
caller completed its wait/classify/return sequence. Second, bounded capture could
start one or more pipe threads and then be interrupted while starting the next,
leaving the outer wrapper with a process handle but no thread handles.

Rev0982 keeps the complete constructor handoff inside one exception path. A
completed child is reclaimed exactly once when that path is interrupted. An
interrupt during `Thread.start()` is treated conservatively even while the
thread identity is not yet published: the possible starter retains the gate and
late cleanup responsibility, so a retry cannot create a second unresolved
constructor. Ordinary thread-start failure still releases the gate.

Regex readiness, readiness-reader startup, and request exchange now share one
process-ownership region. General process capture keeps its prospective reader/
writer threads in the same owner as the child; partial startup, later capture
interruption, or protocol failure terminates the tree, drains or closes exact
capture pipes, joins every thread that actually started, and reaps the child
before re-raising. Cleanup failure cannot replace the original interruption.

The witness injects the constructor rather than manufacturing a real deadlock
with `preexec_fn`. Python documents `preexec_fn` as unsafe in threaded programs
because the child may deadlock before `exec`; using that hazard as the test
mechanism would teach the wrong production pattern.

## Sparse wordwrap geometry

`WordWrapLayout` scans one logical line once but records only native unsigned
checkpoints. A lookup resumes from the nearest checkpoint and performs at most
one checkpoint stride of exact wrap decisions. The stride grows for extreme
lines so retained checkpoint payload stays at or below 256 KiB even when width
is one character.

`VisualRowIndex` keeps a four-entry LRU of these exact line layouts. Long lines
are cached during row-count construction; shorter lines are cached only when a
caller actually asks for true-wordwrap geometry. Changed-line refresh evicts the
corresponding entry, while rebuild/configuration changes clear the cache.
Rendering now materializes only visible row bounds. Fixed wrapping remains
arithmetic. The historical pure helper still returns a complete list for callers
that explicitly request one; the editor hot path no longer does so.

A seeded differential audit compared row counts, row starts, row bounds, and
column-to-row inversion against the rev0981 behavior without a mismatch. A
broader output probe also matched rev0981 exactly across 350 literal-search
cases, 350 literal-replacement plans, and 1,000 wrap geometries. A one-million-
character width-1 regression proves the checkpoint payload ceiling.

## Compact search and replacement truth

Search snapshots now own line starts and parallel span starts/ends in
`array('Q')` storage. Literal matching streams directly into those arrays;
`span_starts` and `span_ends` are views over the same owner rather than duplicate
tuples. Public sequence behavior remains read-only, and debug representations
show bounded head/tail samples so logging cannot recreate the complete object
graph.

The exact retained coordinate payload is therefore:

`8 * line_count + 16 * match_count` bytes on this platform's 8-byte `Q` cells.

Replacement planning separates the compact edit needed to apply text
(`start`, `end`, `new`) from the rich `ReplaceMatch` compatibility row. The
product planner applies compact edits and materializes only the requested sample
rows. Interactive query-replace retains compact immutable edits and recovers the
old source slice lazily from its witnessed session-start text. Rich compatibility
callers still receive full rows, but one forward newline walk replaces repeated
cumulative prefix rescans.

Line-start generation uses repeated native `str.find("\\n")` calls rather than a
Python callback per character. Simultaneous-edit planning accepts the caller's
`Sequence[int]` directly and no longer duplicates a compact line index as a
Python tuple.

## Measured Python-allocation evidence

The paired rev0981/rev0982 run used Python 3.13.5 on the same Linux cloudtainer
and `tracemalloc`. These are Python-tracked allocations, not RSS, total heap,
native allocations, or a cross-platform performance claim.

| Product path | rev0981 peak | rev0982 peak | rev0981 time | rev0982 time |
| --- | ---: | ---: | ---: | ---: |
| editor view, 1.55M-character true-wordwrap line | 818,568 B | 8,460 B | 0.203 s | 0.152 s |
| cold literal search, 100,000 matches / 100,000 lines | 26,730,947 B | 5,053,227 B | 0.496 s | 0.203 s |
| complete literal replace plan, 20,000 matches | 4,745,580 B | 2,825,420 B | 0.469 s | 0.290 s |

The permanent `tools/measure_hotpath_allocations.py` witness also observed a
one-million-character, width-10 true-wordwrap layout with 100,000 visual rows
retaining 12,504 coordinate bytes; 100,000 one-character search matches retained
exactly 1,600,008 coordinate bytes. Run-to-run timings are supporting evidence,
not promises.

## Online research used

Primary references consulted for this revision:

- Python subprocess documentation: https://docs.python.org/3/library/subprocess.html
- Python array documentation: https://docs.python.org/3/library/array.html
- Python tracemalloc documentation: https://docs.python.org/3/library/tracemalloc.html
- CPython subprocess implementation (supplementary): https://github.com/python/cpython/blob/main/Lib/subprocess.py

The design follows the documented limitation rather than pretending
`communicate(timeout=...)` reaches backward into constructor internals. Compact
numeric arrays and phase-local `tracemalloc` peaks are used only for the claims
their documentation supports.

## Audit findings and residual risk

The audit also removed repeated argv/shell capture setup, bounded packed-object
`repr`, replaced Python character iteration in line indexing, made the shared-
deadline host-process regression deterministic instead of scheduler/sleep
dependent, closed the completed-child interruption window, and moved partial
capture-thread teardown into the owner that still has the thread handles.

Deliberately unclaimed boundaries remain:

- starter-thread creation has no independent timeout; an interruption before
  native-thread publication is handled conservatively and can retain the gate
  even if no starter ultimately appears;
- one permanently blocked platform constructor can retain one daemon thread and
  the gate forever, although callers and retries remain finite;
- operation-specific late cleanup is synchronous in the starter and can delay
  gate recovery if cleanup code itself blocks;
- readiness and capture I/O thread creation are not independently deadline-
  preemptible, although partial-start interruption now reclaims every published
  process, pipe, and thread handle;
- normal constructors briefly serialize, so this is availability containment,
  not launch acceleration or fairness;
- no Windows execution or Job Object process-tree evidence was obtained;
- `array('Q')` bounds retained coordinate storage, not source text, replacement
  strings, regex-worker results, RSS, or native allocator behavior;
- true wordwrap still requires a complete first scan of the logical line and can
  consume CPU proportional to its length;
- compatibility APIs that explicitly request all wrap starts or all rich replace
  rows can still allocate proportional output;
- a rope/piece table, background indexer, resident process broker, and generic
  memory governor are not introduced.

## Recommended next work

The next evidence should come from Windows process creation/capture teardown and
from complete real-user journeys over very large files, not from another
abstraction layer. In parallel, profile buffer text copying and undo snapshot
retention under repeated large edits; only adopt a rope/piece table if measured
product paths—not architectural fashion—justify the semantic and recovery cost.
