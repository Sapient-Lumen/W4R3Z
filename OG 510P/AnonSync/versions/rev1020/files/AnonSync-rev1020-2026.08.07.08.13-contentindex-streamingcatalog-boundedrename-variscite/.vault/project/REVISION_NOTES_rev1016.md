# Revision notes — rev1016

## Product move

Rev1016 turns rev1015's whole-process memory question into an owner-visible
Linux measurement surface. The local private socket accepts one exact
`resources\n` request, and the shipping CLI can aggregate one through 256
one-process-per-share services under one total deadline.

The snapshot reports peer-bound PID/start-time identity, current RSS/PSS and
anonymous/file/shared-memory PSS, private/shared resident memory, swap,
`getrusage` counters, open descriptors, and threads. Ordinary status remains
procfs-cold. The surface is diagnostic-only and cannot change synchronization
or retention authority.

## C++ changes

- Added `sync_linux_process_resources.hpp/.cpp` with one bounded single-read
  `/proc/self/smaps_rollup` parser, `/proc/self/stat` identity observation,
  descriptor/thread census, `getrusage`, strict JSON rendering, and strict JSON
  parsing.
- Added the exact `resources\n` request to the private local status socket.
- Added the PID-bound local resource query client.
- Added `anonsync_sync resources` with repeated `--socket`, a hard 256-process
  frontier, duplicate-path rejection, duplicate-live-process rejection,
  overflow-checked sums, and one aggregate steady-clock deadline.
- Added explicit output caveats for RSS shared-page double counting, kernel PSS
  share adjustment, sequential non-atomic samples, diagnostic-only semantics,
  and the procfs-cold ordinary status boundary.

## Runtime and audit changes

- Added a 45-check focused Linux parser/live-observer regression.
- Extended the local private-socket regression to 165 checks.
- Added a real two-process/three-socket aggregate regression. One fixture
  touches 48 MiB of anonymous memory; the regression proves exact PSS/private
  delta visibility, checked aggregate equality, same-process alias rejection,
  one total timeout, ordinary-status isolation, and clean drain.
- Added a dedicated source-shape audit and structural/release-package binding.
- Stopped and excluded an obsolete validator rooted in a discarded worktree.

## Compatibility

Synchronization protocol generation, durable database schemas, payload formats,
source-manifest checkpoint format, peer authentication, and service status
schemas are unchanged. `resources\n` is a new explicit local diagnostic request;
existing `status\n` bytes and behavior are unchanged.

## Deliberate boundaries

This is not a multi-terabyte memory result, resource admission controller,
cgroup observer, allocator profiler, page-cache attribution engine, multi-share
supervisor, Android port, or garbage collector. It provides the measurement
seam needed to make those decisions from real service evidence.

## Validation

Exact rev1016 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), a no-work bundled-SQLite re-attestation, independent 55/55 product tests, and 252/252 non-product tests for all 307/307 registered tests. Focused GCC proofs passed 45 Linux process-resource, 165 local private-socket, and 42 real-process aggregate checks. Source audits passed 22/22 focused resource-boundary checks and 667/667 structural-authority checks. A fresh Clang 17 ASan/UBSan product graph completed 284/284 edges and all 55/55 product tests passed with leak detection and halt-on-error. The exact rev1015 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Predictable-path validators, the post-freeze divergent source delta, interrupted runs, and their build products are excluded.

## Release cutpoint

Archive: `AnonSync-rev1016-2026.08.06.22.55-processresources-pssaggregate-deadlinefence-clinohumite.zip`

Codename: `clinohumite`
