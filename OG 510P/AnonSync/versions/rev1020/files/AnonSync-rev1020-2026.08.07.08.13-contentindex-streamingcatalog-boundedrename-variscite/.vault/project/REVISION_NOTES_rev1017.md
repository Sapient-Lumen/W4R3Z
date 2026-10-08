# Revision notes — rev1017

## Product move

Rev1017 turns rev1016's one-instant Linux resource observer into a bounded
multi-share time series. `anonsync_sync resources-watch` samples the existing
owner-only `resources\n` request on a fixed schedule, records compact aggregate
points and per-process peak envelopes, and fails closed if any socket begins
serving a different process lifetime.

This is the measurement seam needed before deciding whether one process per
share is acceptable for Linux/headless multi-terabyte media trees. It is not a
resource governor or a claim that the target workload already fits.

## C++ changes

- Added the explicit
  `anonsync.local-process-resources.series.v1` response schema.
- Added `anonsync_sync resources-watch` with one through 256 sockets, two
  through 1,024 samples, a one-millisecond through one-hour interval, and one
  total deadline of at most 24 hours.
- Anchored every scheduled point to command start rather than accumulating
  drift from previous round completion.
- Added exact PID/start-tick identity continuity across every round. Restart,
  replacement, or alias drift is terminal.
- Added compact point totals, first/last totals, element-wise observed aggregate
  peaks, per-process first/last/peak envelopes, cumulative `getrusage` deltas,
  schedule-lag accounting, and round-span accounting.
- Kept the retained shape O(processes + samples); no process-by-sample full
  response matrix is retained.
- Centralized socket selection, checked resource arithmetic, deadline handling,
  identity proof, and round sampling across one-shot and time-series commands.
- Preserved the released one-shot aggregate v1 schema and behavior.

## Runtime and adjacent refactor

- Expanded the real-process regression to 246 checks.
- Added a 16-point, 75-millisecond series in which a fixture touches another
  48 MiB after sampling begins; the series must expose at least a 40 MiB rise in
  anonymous PSS and private resident memory.
- Added fixed-schedule, peak, delta, compact-shape, alias, changed-identity,
  impossible-schedule, one-total-deadline, status-isolation, and cleanup proofs.
- Moved the fixture's page-size query before `mmap`, closing a constructor throw
  window before RAII ownership existed.
- Added a focused rev1017 source-shape audit and structural/package binding.
- Excluded transient remount losses, obsolete worktrees, and interrupted build
  products from release authority.

## Compatibility

Synchronization protocol generations, durable database schemas, payload
formats, local `resources\n` request, one-shot aggregate v1 response, peer
authentication, and service status schemas are unchanged. `resources-watch` is
a new CLI-only diagnostic composition over the existing exact local request.

## Deliberate boundaries

The series is sequential and diagnostic. It does not stop target processes,
produce an atomic multi-process cutpoint, catch every between-point transient,
attribute page cache or allocator fragmentation, measure cgroup pressure,
impose budgets, consolidate shares, prove Android support, or establish a
multi-terabyte memory result.

## Validation

Exact rev1017 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), independent 55/55 product tests, and 250/250 documentation-independent non-product tests; the two final documentation-sensitive audits then passed for complete 307/307 registry accounting. Focused GCC proofs passed 45 Linux process-resource checks and 246 real-process resource-series checks. Source audits passed 27/27 focused resource-boundary checks and 675/675 structural-authority checks. A fresh Clang 17 ASan/UBSan product graph completed 284/284 edges and all 55/55 product tests passed with leak detection and halt-on-error. The exact rev1016 parent passed 41/41 wrapper-aware package checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Transient remount losses, predictable-path validators, divergent startup prototypes, interrupted runs, and their build products are excluded.

## Release cutpoint

Archive: `AnonSync-rev1017-2026.08.07.00.36-resourcewatch-peakenvelope-restartfence-oligoclase.zip`

Codename: `oligoclase`
