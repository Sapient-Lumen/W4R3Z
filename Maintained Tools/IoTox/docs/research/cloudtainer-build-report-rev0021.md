# IoTox cloudtainer build report — rev0021

**Date:** 2026-08-17 America/New_York
**Version:** 0.21.0
**Revision:** rev0021
**Codename:** R7 Evidence Citadel
**Linked handoff revision:** rev0008

## 1. Scope

rev0021 constructs the observability and fail-closed evidence boundary required before the genuine
Ratox R7 complete-service matrix. It preserves the rev0020 default-off host/controller, authority,
replay, process, and signed restart-fence contracts, then adds:

```text
fixed-allocation owner queue-wait distributions with exact 2 ms gate coverage
coherent typed sensitive custom-lossless outcomes
separate controller and host retained-head pressure streaks and ages
nonzero nondecreasing service-relative Ratox lifecycle time
complete content-free runtime projection of the new evidence
bounded canonical R7 evidence parsing and deterministic qualification reports
opt-in deterministic owned-registry sharding for instrumented builds
```

This is construction and deterministic validation. No two-physical-host R7 sample set was created or
claimed in this session.

## 2. Implementation

### Queue-tail truth

`LatencyHistogram` keeps exact buckets for 0..4,096 microseconds and conservative inclusive
power-of-two upper bounds above that range. It emits deterministic nearest-rank p50, p95, and p99 with
an exactness flag, maximum, total count, and the exact number of observations at or above 2,000 us.
The three serialized owner lanes observe admission-to-execution waits under the existing command
mutex, so a runtime snapshot projects coherent totals and percentiles.

### Typed provider outcomes

Validated sensitive lossless sends record calls, owner/provider attempts, acceptance, SENDQ full,
peer not connected, peer not found, provider-contract rejection, and other failure under one dedicated
mutex. Before saturation a coherent snapshot preserves `calls >= attempts >= classified outcomes`;
one in-flight serialized provider operation may account for the strict inequality.

### Retained-send and lifecycle evidence

The Agent tracks controller and host retained send heads independently. Retryable rejection advances a
lifetime count, current streak, maximum streak, and steady-clock age. Acceptance, fatal rejection,
purge, route loss, or shutdown clears active pressure without erasing lifetime evidence. Ratox
lifecycle events now carry a service-relative nonzero nondecreasing steady microsecond value. Runtime
status and the private lifecycle journal project these values without terminal bytes, commands,
profile identifiers, paths, environment, or error payloads.

### Bounded R7 analyzer

`tools/analyze-ratox-r7.py` accepts one ASCII TSV evidence file. It freezes the complete-service path,
two physical hosts, c-toxcore 0.2.23, independent steady clocks without cross-host subtraction,
verified route observation, observed direct UDP and forced TCP, and 0/1/8/16/32/64 bulk-stream cells.
Every cell has 1,000..10,000 samples. File bytes, lines, line width, metadata, cell size, integer shape,
ordinals, stage sums, and one-commit/one-render/completion semantics are bounded and checked.

The analyzer uses deterministic integer nearest-rank percentiles. Every cell requires owner queue p99
strictly below 2,000 us and zero semantic failures. Direct UDP additionally requires p95 at most
50,000 us, p99 at most 100,000 us, and zero samples at or above 250,000 us. Forced TCP values are
reported without being mislabeled as direct-route qualification. Regular-file identity, no-follow
opening where available, input mutation, invalid ASCII, and malformed records fail closed.

## 3. Defects found and fixed during construction

1. Independent outcome counters could produce a concurrent snapshot that never existed. One mutex now
   protects the complete sensitive-send outcome vector.
2. Maximum queue wait alone could not distinguish one stall from a persistent tail. Fixed histograms
   now retain p50/p95/p99 and the exact >=2 ms count.
3. Coarse logarithmic buckets could hide the strict 2 ms boundary. Exact buckets extend through
   4,096 us and every projected percentile states whether it is exact.
4. Retained Ratox SENDQ pressure had no lane or age identity. Controller and host heads now retain
   separate streak and steady-age evidence.
5. Lifecycle order lacked a monotonic numeric coordinate. Service-relative steady microseconds are
   now nonzero and nondecreasing.
6. The first analyzer draft accepted zero-duration placeholders and lacked complete input/cell bounds.
   Nonzero end-to-end time and finite metadata, line, byte, ordinal, and per-cell contracts now fail
   closed.
7. The final default process run exposed a stale fixture assertion that still searched for device
   description `revision=20`. Product output correctly reported revision 21; both the compiled oracle
   and mock-node script now require `revision=21`.
8. A single Clang sanitizer CTest invocation repeatedly stalled when the long one-binary process oracle
   immediately followed all sixteen instrumented registry shards. The same binary passed alone, and
   the established isolated registry/nonregistry lanes passed completely. Final sanitizer evidence is
   therefore retained as two explicit invocations rather than treating a runner interaction as a
   product result.

## 4. Toolchain

```text
Linux 6.18.35 x86_64
GCC 14.2.0
Clang 17.0.0
CMake 3.31.6
Ninja 1.12.1
Python 3.13.5
Git 2.47.3
```

The built identity reported:

```text
IoTox 0.21.0 rev0021
```

## 5. GCC Debug warnings-as-errors

The final monolithic direct registry reported:

```text
tests=292 selected=292 shard=0/1 failures=0
```

The complete default CTest surface passed:

```text
14/14 targets
```

This includes the monolithic contamination-sensitive registry, native PTY process, private terminal
controller process, one-binary Agent/control lifecycle, Ratox restart fence, authority ceremony, CLI
contracts, and the analyzer malformed-input matrix.

A separate four-shard build passed 17/17 CTest targets. Each shard selected exactly 73 checks, so the
aggregate was exactly 292/292 with no omission or duplication. Configure values `0`, `65`, `abc`, and
`01` all failed before generation, proving the canonical `1..64` boundary.

## 6. Clang 17 AddressSanitizer and UndefinedBehaviorSanitizer

The sanitizer preset compiled the complete product, exact provider doubles, process fixtures, and all
owned tests with sixteen deterministic registry shards.

Isolated final lanes passed:

```text
16/16 owned-registry shards; aggregate selection 292/292
13/13 nonregistry process, CLI, and analyzer targets
29/29 aggregate targets across the two invocations
```

No AddressSanitizer or UndefinedBehaviorSanitizer diagnostic was emitted by either final lane. The
single-invocation runner stall described above is not represented as a passing result and is not used
to weaken the isolated gates.

## 7. Analyzer and file-boundary validation

The embedded analyzer self-test passed. It covers deterministic reports, a valid 12,000-sample
matrix, strict 1,999/2,000 us owner behavior, direct-route misses, duplicate/gapped ordinals,
undersized and oversized cells, zero and leading-zero values, impossible local stages, metadata and
line overflow, NUL/non-ASCII records, regular-file analysis, symlink refusal, and invalid encoding.

The analyzer proves that supplied evidence matches ADR 0070. It cannot prove that metadata is honest,
that two physical hosts were used, that the route was observed independently, or that experiment
clocks were instrumented correctly.

## 8. Evidence files

```text
artifacts/rev0021/gcc-debug-build.log
artifacts/rev0021/gcc-debug-ctest.log
artifacts/rev0021/owned-registry.log
artifacts/rev0021/gcc-shard4-configure.log
artifacts/rev0021/gcc-shard4-build.log
artifacts/rev0021/gcc-shard4-ctest.log
artifacts/rev0021/gcc-shard4-selection.log
artifacts/rev0021/invalid-shard-configurations.log
artifacts/rev0021/ratox-r7-analyzer.log
artifacts/rev0021/clang-asan-ubsan-configure.log
artifacts/rev0021/clang-asan-ubsan-build.log
artifacts/rev0021/clang-asan-ubsan-registry-ctest.log
artifacts/rev0021/clang-asan-ubsan-shard-selection.log
artifacts/rev0021/clang-asan-ubsan-process-ctest.log
artifacts/rev0021/toolchain-and-identity.txt
artifacts/rev0021/validation-summary.txt
artifacts/rev0021/SHA256SUMS
artifacts/reports/validation-summary.txt
```

## 9. Research boundary

Primary references were rechecked and retained in `docs/research/sources.md`: OpenTelemetry metric
histogram semantics, Linux monotonic clock behavior, RFC 6374 measurement principles, CMake/CTest test
properties, Clang sanitizer documentation, and the pinned c-toxcore 0.2.23 provider boundary. They
define upstream behavior and do not audit IoTox.

ADRs 0069 and 0070 freeze the implementation and evidence contracts. The detailed source review is
`docs/research/ratox-r7-observability-rev0021.md`.

## 10. Nonclaims and next work

rev0021 does not prove public Tox bootstrap, NAT traversal, relay availability, direct UDP route
identity, forced-TCP route containment, two-physical-host latency, reconnect convergence under field
conditions, CPU/RSS/context-switch or power targets, hardware power-cut durability, complete Linux
sandboxing, rollback resistance against an equivalent owner or restored snapshot, or production
support readiness.

The next R7 action is to execute the canonical matrix on two retained physical hosts, preserve raw
samples and route/procedure provenance, run this revision's analyzer, and review every cell and
non-latency resource measure. R8 remains independent review, deployment, recovery, and support policy.
