# Rev0980 audit — unchanged text is not permission to rescan it

## Highest-risk findings

Two ordinary editor loops still repeated whole-document work after rev0979.
Literal search rebuilt flat text, line starts, and every match for navigation,
status, and highlight repaint. Softwrap cursor/viewport helpers repeatedly walked
all logical lines before the target, and fixed-width rendering materialized every
row boundary of a long logical line even when only a screenful was visible.

The worker audit also found a cumulative deadlock route in the default
`forkserver` context. This cloudtainer starts fresh Python interpreters with
roughly 72 native tasks through startup-library side effects. Python explicitly
qualifies forkserver safety on its server remaining single-threaded; CPython then
uses `os.fork()` in that server. Isolated tests passed, but a cumulative screen
module stalled at different worker starts.

## Substantive correction

- Literal and regex search now share one exact immutable snapshot keyed by buffer
  identity/version, query semantics, and execution budget. Find, status, and
  highlight consume the same result until source or policy changes.
- A compact `array("Q")` Fenwick index stores visual-row counts by logical line.
  Exact prefix/inverse geometry is logarithmic after one cold build.
- Buffer mutations publish a small line-splice witness. One immediately following
  line-count-preserving edit of at most 256 rows refreshes only those counts;
  uncertain or structural changes rebuild safely.
- Fixed-width wrap count and row geometry use arithmetic rather than a complete
  boundary vector. Wordwrap computes its sequential break map once per visible
  logical line.
- Importable worker entrypoints now prefer `spawn`, then `forkserver`; the
  single-native-task compatibility fork remains narrow.

## Adjacent audit/refactor

The renderer no longer asks several helper layers to recompute the same boundary
list for each fragment. Pure geometry functions remain as a reference model, and
10,000 randomized line cases plus 1,000 randomized indexes cross-check the new
arithmetic/index behavior. A standalone fault injector proves that
`Process.start()` can block before the rev0979 result deadline begins.

## Waste corrected

On the reference cloudtainer, unchanged 100,000-line softwrap queries fall from
roughly 30–149 ms each to microseconds after the cold index build. One changed
line refreshes in tens of microseconds. Repeated literal search screen/status
work on a 3.1-million-character, 100,000-match buffer falls from tens of
milliseconds per call to approximately one millisecond or less after the initial
scan. A 20-million-character fixed-wrap line renders one screenful without a
boundary vector.

## Residual risk

The first search scan and cold geometry build remain eager. True wordwrap still
scans and stores breakpoints for the current line. External direct mutation of
`Buffer.lines` requires `touch_external()`. Spawn-first is safer but slower,
particularly under this cloudtainer's interpreter startup hooks, and process
construction/start remain outside the operation deadline. No Windows, complete
suite, rope, background index, generic worker pool, total-memory cap, syscall
filter, native-crash boundary, or hostile-plugin sandbox claim is made. See
`docs/937-search-snapshot-softwrap-prefix-spawn-first.md`.
