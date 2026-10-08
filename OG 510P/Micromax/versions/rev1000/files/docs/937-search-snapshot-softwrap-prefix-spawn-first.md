# Exact search reuse, indexed softwrap geometry, and spawn-first workers (rev0980)

Rev0980 follows the measured unfinished work from rev0979 instead of adding a
rope, search service, worker pool, or another registry. Two ordinary editor hot
paths were still repeating whole-document work, and the existing isolated-worker
choice could deadlock in a host whose supposedly clean forkserver had acquired
native threads during interpreter startup.

## Repeated literal-search work

The active search register already had one authoritative whole-buffer result for
regex queries, but literal queries were rescanned for navigation, status, and
highlight repaint. On a 3,099,999-character buffer containing 100,000 literal
matches, rev0979 measured about **0.116 s** for `find`, then **0.146 s** for the
first unchanged screen, **0.071 s** for another unchanged screen, and **0.061 s**
for unchanged status on this Linux cloudtainer.

The editor now leases one immutable `SearchSnapshot` for both literal and regex
search. The key is exact rather than heuristic: buffer object identity, buffer
version, query, literal/regex flavor, case policy, timeout, and match budget must
all agree. `find` commits the candidate snapshot that navigation actually used;
status and visible match projection consume that same object. A buffer edit or
policy change causes one rescan and establishes the next exact lease.

The same benchmark now measures about **0.107 s** for the unavoidable first
literal scan, **0.021 s** for the first screen while unrelated models are cold,
**0.00115 s** for a second unchanged screen, and **0.000117 s** for unchanged
status. Call-count regressions are the stronger contract: `find`, screen, and
status perform one scan total; one edit causes exactly one additional scan and
then reuse.

## Softwrap geometry was quadratic in ordinary movement

Softwrapped cursor and viewport helpers repeatedly walked every logical line
before the target. A 100,000-line, 3,999,999-character document at width 40
measured roughly **57 ms** for each total-row query, **30 ms** for a cursor
projection, and **149 ms** for `ensure_cursor_visible()` in rev0979. These costs
were paid again although neither text nor wrap configuration had changed.

`VisualRowIndex` is a deliberately narrow acceleration layer:

- one unsigned visual-row count and one unsigned Fenwick-tree cell per logical
  line, stored in compact `array("Q")` objects;
- O(log n) prefix and inverse visual-row queries;
- an exact lease over buffer version, width, continuation-indent policy, and
  wordwrap mode; and
- an incremental refresh only when the consumer owns the immediately preceding
  version and the buffer publishes one exact line-count-preserving splice of at
  most 256 lines.

Buffer mutations now publish a small `BufferChange` witness with version,
starting line, old line count, and new line count. Width changes, wordwrap
changes, missed generations, line-count changes, large edits, or an explicit
`touch_external()` rebuild from the authoritative line vector instead of trying
to repair uncertain state.

On the same 100,000-line benchmark, the cold index build is about **66 ms** and
uses **1.6 MB** of array payload. Once built, median total-row and cursor queries
are about **2.5–5 microseconds**, `ensure_cursor_visible()` is about **25
microseconds**, and one changed-line refresh plus total query is about **27
microseconds**. This is not a claim about terminal drawing, wordwrap scanning,
or every editor action; it removes repeated prefix reconstruction from the
geometry owner.

## Fixed-width wrapping no longer allocates every boundary

The first index implementation still called the list-returning wrap helper merely
to count rows. The renderer also built a complete row-start list for a logical
line even when only a screenful was visible. That turns a single very long line
into one Python integer allocation per off-screen fragment.

Fixed-width wrapping is now exact arithmetic for row count, row start/end, row
capacity, and column-to-row mapping. Wordwrap keeps the sequential reference
algorithm because whitespace decisions depend on preceding text, but the visible
renderer computes its break list once per visible logical line rather than once
per fragment. Pure helpers remain as reference behavior and randomized tests
compare both modes.

A 20,000,000-character fixed-wrap line positioned at subline 200,000 rendered 24
rows in about **0.000128 s** on the reference cloudtainer. The geometry index for
that one logical line uses **16 bytes** of array payload, and the renderer
materializes only the 24 visible slices.

## Forkserver audit: the clean server was not clean

Rev0979 preferred `forkserver` before `spawn` to avoid cloning the editor's live
threads while retaining fast child startup. A cumulative screen-model run then
stalled in different documentation tests although each test passed alone. The
host process reported one Python thread but roughly 72 native tasks. A fresh
Python interpreter in this cloudtainer also began with roughly 72 native tasks
because startup hooks imported numerical libraries; setting the common numerical
thread ceilings before interpreter launch reduced that fresh process to one
native task.

Python's multiprocessing documentation states the relevant qualification:
`forkserver` is single-threaded **unless system libraries or preloaded imports
spawn threads as a side effect**. CPython's forkserver then serves requests with
`os.fork()`. This host therefore violated the condition that made forkserver the
safe default for Micromax.

Micromax now prefers `spawn`, then `forkserver`, for importable entrypoints.
`spawn` starts a fresh worker interpreter instead of asking a potentially
multithreaded server to fork. The compatibility `fork` fallback remains limited
to a complete native-task count of one for non-importable `python -c`, stdin, or
REPL entrypoints. The library still returns a per-operation context and does not
change the embedding application's global multiprocessing start method.

The correction is safety-first, not free. Python documents spawn as slower, and
this instrumented cloudtainer makes it unusually expensive because every fresh
interpreter runs heavy startup hooks. The complete 50-test screen-layout module
passed under the uncapped hostile host with spawn-first, but required **205.43
s**. An isolated picker test took **8.15 s** under pytest. Those are harness/host
observations, not general product latency claims, and they keep process startup
as a visible unresolved performance and deadline boundary.

## Process.start remains outside the result deadline

`tools/reproduce_process_start_stall.py` starts its own forkserver, pauses the
server with `SIGSTOP`, and invokes `Process.start()` in a separate thread. The
call remained blocked throughout a 0.35-second observation and recovered only
after `SIGCONT`. The result-channel deadline cannot act because it begins after
startup.

Spawn-first removes the demonstrated multithreaded-forkserver route from the
default, but it does not make process construction or `Process.start()`
preemptible. A future launcher owner should be justified by a supported product
stall or a portable child-start protocol, not by adding a generic process pool
in anticipation.

## Audit/refactor details

- Replaced the regex-only result lease with one exact active-search snapshot
  owner shared by literal and regex paths.
- Moved repeated softwrap prefix scans behind one buffer-local compact index.
- Added exact line-splice witnesses to every ordinary `Buffer` mutation helper.
- Removed repeated wrap-boundary computation inside visible-row rendering.
- Replaced fixed-wrap boundary vectors with constant-memory arithmetic.
- Preserved pure geometry helpers as executable reference functions instead of
  rewriting behavior and tests together.
- Added an adversarial standalone `Process.start()` fault injector rather than
  claiming the post-start result deadline covers startup.

## Primary sources

- Python multiprocessing contexts and start methods, including spawn startup,
  multithreaded-fork hazards, and the forkserver side-effect qualification:
  https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
- CPython 3.13.5 forkserver implementation, including server launch and
  `os.fork()` in the request loop:
  https://github.com/python/cpython/blob/v3.13.5/Lib/multiprocessing/forkserver.py
- CPython 3.13.5 forkserver process launcher and connection path:
  https://github.com/python/cpython/blob/v3.13.5/Lib/multiprocessing/popen_forkserver.py

## Deliberately narrow claims

- The first search scan still builds flat text, line starts, and up to the
  existing 100,000-match budget. The cache removes repeat work; it is not an
  incremental search index or background service.
- The geometry index has an O(number of logical lines) cold build and rebuilds
  after line-count changes, large/missed/unknown edits, or wrap-configuration
  changes. It is not a rope, piece table, text index, or total-memory cap.
- Public mutable access to `Buffer.lines` remains for compatibility; an external
  in-place mutation must call `touch_external()` or any versioned derived cache
  can be stale.
- True wordwrap still scans the current line sequentially and materializes the
  current visible line's break vector. A huge wordwrapped line remains eager.
- Unsigned row counts are finite machine-sized cells, not an allocation quota.
- Spawn is slower than forkserver, can still stall during process creation, and
  requires an importable safe main module. Positive operation timeouts still do
  not own process construction/start.
- No Windows execution evidence, complete-suite claim, generic worker host,
  syscall filter, native-crash container, hostile-plugin sandbox, or arbitrary
  process-tree guarantee is added.
