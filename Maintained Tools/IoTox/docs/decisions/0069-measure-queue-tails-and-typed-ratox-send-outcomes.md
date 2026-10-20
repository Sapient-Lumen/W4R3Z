# ADR 0069: Measure queue tails and typed Ratox send outcomes

Status: accepted
Date: 2026-08-17

## Context

Ratox R7 qualification needs evidence about latency distribution and transient transport pressure, not
only lifetime totals and a maximum. A maximum cannot distinguish one isolated stall from a persistent
tail, and a generic send failure count cannot distinguish c-toxcore SENDQ pressure from route loss,
peer deletion, malformed use of the provider contract, or an unknown failure.

The existing transport owner is serialized, but runtime status may be read concurrently. Any new
outcome accounting therefore has to publish coherent snapshots. It must also remain fixed-allocation
on the owner path and must not persist terminal bytes, profile identifiers, paths, commands, or error
payloads.

Primary references rechecked for this decision:

```text
https://opentelemetry.io/docs/specs/otel/metrics/data-model/
https://opentelemetry.io/docs/specs/otel/metrics/sdk/
https://man7.org/linux/man-pages/man3/clock_gettime.3.html
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
```

## Decision

### Queue-wait distribution

Each interactive, control, and bulk owner lane records monotonic queue-wait observations in one
fixed-allocation lifetime histogram. Values from zero through 4,096 microseconds have exact buckets.
Larger values use conservative inclusive power-of-two upper bounds. The projection publishes
nearest-rank p50, p95, and p99 together with an `exact` flag, the exact lifetime maximum, and an exact
count of observations at or above 2,000 microseconds.

The exact region deliberately spans the strict R7 owner gate (`p99 < 2,000 us`). A value at the
boundary cannot be rounded into a passing bucket. Values above the exact region remain useful for
triage without claiming precision that the histogram does not retain. Counters saturate rather than
wrap.

### Sensitive lossless outcomes

Validated `send_sensitive_lossless` calls publish coherent lifetime counts for:

```text
calls
toxcore attempts
accepted
send queue full
peer not connected
peer not found
provider contract rejection
other failure
```

The call count is advanced before owner admission. The attempt count is advanced only when the owner
begins the provider operation. Exactly one classified outcome is then recorded for that attempt.
Snapshots are copied under one dedicated mutex, so before saturation they preserve:

```text
calls >= attempts >= sum(classified outcomes)
```

The final inequality may be strict only while the serialized owner has one provider call in flight.
Local argument rejection before the validated call boundary is not counted as a provider outcome.

### Retained-head pressure

The Agent separately tracks the controller-to-host and host-to-controller retained Ratox send heads.
A retryable `resource_exhausted` or `unavailable` result advances that lane's lifetime rejection count,
current streak, maximum streak, and steady-clock age. Acceptance, fatal rejection, route purge,
offline transition, and shutdown clear only the active streak and age. Lifetime totals remain.

### Lifecycle time and runtime projection

Ratox lifecycle records carry a service-relative steady-clock microsecond value. The value is nonzero
and nondecreasing even when the underlying clock returns equal adjacent readings. Runtime status
projects every histogram percentile and exactness flag, every typed sensitive-send counter, both
retained-head lanes, and the lifecycle steady time. Content-bearing terminal data remains excluded.

## Consequences

R7 runs can distinguish owner scheduling delay from provider SENDQ pressure and route failure. A
runtime reader receives internally consistent send accounting and can detect both persistent and
transient retained-head stalls. Exactness flags prevent downstream tools from presenting a coarse
upper bound as an exact percentile.

The histogram is cumulative for the process lifetime. It does not by itself segment warmup from
steady state, correlate samples across two hosts, or prove a physical route. The retained-head age is
a live local observation and resets when the head clears. None of these counters establish R7
qualification without the separate bounded evidence contract.

## Rejected alternatives

- **Keep only maximum queue wait.** A maximum cannot describe tail prevalence or enforce a percentile
  gate.
- **Use floating-point percentile estimation.** The decision boundary is integral microseconds and
  must remain deterministic across toolchains.
- **Use logarithmic buckets at the 2 ms boundary.** Bucket rounding could turn a boundary failure into
  an apparent pass.
- **Publish only a generic send-failure total.** It hides the operational distinction between SENDQ,
  route state, peer deletion, contract rejection, and unknown failure.
- **Put terminal content into exemplars.** That would violate the content-free runtime evidence
  boundary.
