# Rev0980 changelog — exact search reuse and indexed softwrap geometry

## Search loop

- Generalized the active-search cache from regex-only containment to one exact
  literal-or-regex `SearchSnapshot` lease.
- Keyed reuse by buffer identity/version, query, search flavor, case policy,
  timeout, and match budget.
- Committed the exact candidate snapshot used by `find`, so navigation, status,
  highlight projection, and screen rendering cannot silently rescan unchanged
  source.
- Added regressions proving one scan across find/screen/status, one rescan after
  mutation, and reuse thereafter.

## Softwrap loop

- Added `BufferChange` line-splice witnesses to ordinary buffer mutation helpers.
- Added a compact version/configuration-owned `VisualRowIndex` with Fenwick
  prefix sums, logarithmic inverse lookup, and bounded changed-line refresh.
- Routed editor total-row, cursor, viewport, inverse movement, and visible-row
  geometry through the shared buffer-local index.
- Replaced fixed-width boundary-list allocation with constant-memory arithmetic
  for row count, start/end, capacity, and column mapping.
- Refactored rendering to compute true-wordwrap boundaries once per visible
  logical line and to materialize only visible fixed-wrap fragments.
- Preserved pure reference helpers and added deterministic randomized equivalence
  evidence.

## Worker lifecycle audit

- Changed isolated worker preference from forkserver-first to spawn-first after
  reproducing a multithreaded forkserver in this cloudtainer and cumulative
  worker stalls.
- Kept forkserver as a secondary importable context and the native-single-thread
  fork fallback only for non-importable shell/REPL entrypoints.
- Added `tools/reproduce_process_start_stall.py`, which pauses a private
  forkserver and demonstrates that `Process.start()` remains outside the
  post-start result deadline.
- Documented spawn startup latency as a real residual cost rather than hiding it
  behind the unsafe faster default.

## Research, audit, and handoff

- Added `docs/937-search-snapshot-softwrap-prefix-spawn-first.md` with measured
  baselines/final timings, official Python/CPython sources, implementation
  boundaries, and unresolved risks.
- Updated current mission, roadmap/worklist, decisions, security boundary,
  README, TODO, revision index, and generated context without adding a service,
  pool, registry, rope, or new doctrine budget.
