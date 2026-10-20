# Ratox R7 observability and evidence gate — rev0021

Date: 2026-08-17
Status: construction and deterministic validation; no two-physical-host qualification claim

## Question

What must exist before IoTox can run the R7 complete-service matrix without hiding owner-thread tail
latency, retained SENDQ pressure, typed c-toxcore failure causes, lifecycle order, or malformed input?

## Source review

Primary references rechecked:

```text
https://opentelemetry.io/docs/specs/otel/metrics/data-model/
https://opentelemetry.io/docs/specs/otel/metrics/sdk/
https://man7.org/linux/man-pages/man3/clock_gettime.3.html
https://www.rfc-editor.org/info/rfc6374/
https://cmake.org/cmake/help/latest/command/set_tests_properties.html
https://cmake.org/cmake/help/latest/prop_test/PROCESSORS.html
https://clang.llvm.org/docs/AddressSanitizer.html
https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
```

Applied interpretation:

- histogram buckets must state their bounds and cannot be presented as exact quantiles when only a
  range was retained;
- the 2 ms owner decision boundary needs exact local representation;
- process-local event durations and ages use a monotonic/steady clock rather than wall time;
- end-to-end measurements must avoid subtracting unsynchronized cross-host clocks;
- CTest resource and timeout properties are explicit, and sanitizer runs should fail on the first
  diagnostic rather than burying it in one extremely long process.

The sources define upstream semantics and test-tool behavior. They do not review IoTox or validate an
R7 run.

## Construction

rev0021 adds four connected evidence layers.

### Owner queue tails

`LatencyHistogram` is fixed-allocation and cumulative. Microseconds 0..4096 are exact; larger values
map to conservative inclusive power-of-two upper bounds. It exports nearest-rank p50/p95/p99 with
exactness flags, maximum, count, and the exact number at or above 2,000 us. The three owner traffic
classes record waits under the existing command mutex, and coherent runtime snapshots project the
full result.

### Provider and retained-head outcomes

The sensitive custom-lossless path records validated calls, provider attempts, acceptance, SENDQ full,
not connected, not found, provider contract rejection, and other failure under one dedicated mutex.
The Agent independently records retryable rejection totals, live streak, maximum streak, and
steady-clock age for controller and host retained heads. Accepted, fatal, purged, offline, and shutdown
transitions clear active pressure without erasing lifetime totals.

### Lifecycle evidence

Every Ratox lifecycle event receives a service-relative nonzero nondecreasing steady-clock microsecond
value. The private runtime journal includes it but continues to exclude terminal bytes, commands,
paths, profile identifiers, environment, and error payloads.

### Qualification parser

The R7 analyzer requires a bounded canonical two-route by six-load-cell matrix. It verifies exact
metadata, regular-file/no-follow input, ASCII and record shape, per-cell sample bounds, contiguous
ordinals, canonical uint64 values, feasible local-stage sums, one input commit, one render copy, and
completion. It computes deterministic nearest-rank reports and applies the strict owner p99 and direct
UDP gates from ADR 0070. Its embedded self-test includes passing, boundary, malformed, oversize,
symlink, and encoding cases.

## Findings during implementation

1. Reading independent atomic outcome counters could yield a snapshot that never existed. One mutex
   now protects the typed outcome vector and its invariants.
2. A maximum queue wait could not distinguish one stall from a sustained tail. Fixed histograms retain
   p50/p95/p99 without heap allocation on the owner path.
3. Coarse exponential buckets around 2 ms could hide a strict-boundary failure. Exact buckets extend
   beyond the gate.
4. A retrying retained packet was visible only as a generic transport failure. Controller and host
   lanes now expose streak and age independently.
5. An evidence parser without file, line, cell, integer, and ordinal bounds could turn qualification
   into an unbounded or ambiguous operation. Every dimension is now finite and malformed input fails
   closed.
6. A syntactically valid zero end-to-end duration could represent an uninitialized placeholder. The
   duration is now required to be nonzero.
7. One monolithic sanitizer process can exceed execution windows even when individual checks are
   healthy. Sanitizer presets shard the existing deterministic registry while the ordinary default
   remains monolithic.

## Evidence boundary

The owned tests prove deterministic histogram math, strict 2 ms behavior, conservative bucket flags,
typed provider classification, concurrent snapshot invariants, lane-separated retained pressure,
lifecycle monotonicity, runtime projection, parser fail-closed behavior, and shard configuration.

They do not supply the physical experiment. rev0021 makes R7 measurable and rejects malformed result
sets; it does not claim direct UDP, forced TCP, public bootstrap, two physical hosts, latency targets,
power behavior, or independent route observation. Those remain explicit field evidence.
