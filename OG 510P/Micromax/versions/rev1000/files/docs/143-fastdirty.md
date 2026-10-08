# Fast dirty tracking (`fastdirty`) (rev0984)

Micromax treats `fastdirty` as an ordinary editor option. Rev0979 also selects a
visible buffer-local value for large saved baselines so exact dirty accounting
does not become a per-keystroke product tax. Rev0983 removed whole-document
generations from ordinary one-cursor undo; rev0984 adds visible `undobytes`
retained-text ownership so the dirty and history paths no longer contradict one
another.

## Current rule

- The global default remains `fastdirty=false`.
- In exact mode, the buffer compares the current logical text signature with the
  last clean baseline. Undo or later edits can therefore clear `dirty` when the
  document truly returns to the saved text.
- In fast mode, the first mutation makes `dirty` sticky until the next successful
  save/open baseline reset.
- A newly opened or created buffer whose saved UTF-8 baseline is at least **1
  MiB** receives an explicit local `fastdirty=true` when the global option is
  false.
- The automatic choice is ordinary option state: `show fastdirty` exposes it and
  `setlocal fastdirty false` restores exact comparison for that buffer.
- Buffers below the threshold keep exact return-to-clean behavior by default.
  Global/local option commands and hostcalls continue to resynchronize the live
  buffer policy through the existing option path.

## Exact signature implementation

Exact mode still represents the logical document as LF-joined text, preserving
the prior BLAKE2b digest, UTF-8 `surrogatepass` policy, and byte count. For
ordinary values, native join-and-encode remains the fast path. For larger values,
the joined string is encoded and hashed in 64 KiB character slices, avoiding a
second full-document UTF-8 byte allocation. Initial line splitting and the joined
logical string are still eager; this is not a rope or an incremental hash tree.

The audit tried a Python per-line signature walker to avoid that joined string as
well. On the same many-short-line workload it measured about **21.9 ms per
mutation at 1 MiB** and **149 ms at 4 MiB**, versus about **2.22 ms** and **8.90
ms** for the rev0978 native join path. That 10–17× regression was removed. The
final explicit exact path stays near the prior speed while the default large-file
edit path uses the sticky flag.

## Why this shape

Upstream micro documents `fastdirty` as the accuracy/performance switch and
currently auto-enables it for larger files. Micromax uses a more conservative,
measured 1 MiB threshold, keeps the choice visible and reversible, and does not
add a background hash worker, index service, or storage rewrite before another
product journey demonstrates that need.

## Rev0983–rev0984 undo correction

The fast-dirty threshold originally removed full-document signature work from each ordinary mutation, but rev0982 undo still captured complete before/after document text around the same action. Rev0983 closes that common-path contradiction: one-cursor insert, delete, newline, tab, and paste retain exact old/new slices plus cursor/selection sidecars. Rev0984 then gives those and broad fallback rows explicit logical retained-text ownership, a visible per-buffer `undobytes` soft limit, cached/deque-backed whole-row retirement, and changed-buffer-only aggregate retention. Multi-cursor, query-replace, line-plan, and changed-buffer aggregate transactions still keep broad snapshots; the newest row may exceed the limit and this is not a hard process-memory bound. See `docs/940-compact-splice-undo-mission-audit.md` and `docs/941-retained-history-budget-transaction-snapshot-compaction.md`.

## Boundaries

Automatic fast mode intentionally gives up exact undo-to-clean recognition until
save. The threshold is a Linux-cloudtainer product heuristic rather than a
portable latency guarantee. Exact baseline creation, explicit exact mode,
search, replacement planning, rendering, line geometry, and many mutations
remain linear or eager. The result-channel memory work in rev0979 does not make
this a total-memory boundary.

## Pointers

- buffer signatures and threshold: `src/micromax_editor/buffer.py`
- visible buffer-local selection: `src/micromax_editor/editor.py`
- focused behavior/equivalence tests: `tests/test_editor_fastdirty.py`
- measured revision record: `docs/936-worker-full-frame-deadline-large-buffer-fastdirty.md`
