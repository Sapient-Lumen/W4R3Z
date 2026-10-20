# ADR 0162: Resume paced files in bounded oldest-first batches

Status: accepted, 2026-08-25; lifecycle qualified, latency target not met.

## Context

ADR 0160 successfully reserves the semantic event queue, but its low-water action resumes every
eligible scheduler-paused transfer in one toxcore-owner turn. That is harmless for `bulk-1`. In the
valid direct-UDP `bulk-8` cell, however, both roles accumulated about 129.5 seconds of pacing hold,
individual holds reached 187/177 ms, render p95 reached 144.120 ms, and one sample crossed 250 ms.
At the same time owner p99 was 0.420 ms, event high-water stayed below 140, required-event waits were
zero, and remote stage-to-output p95 was 13.581 ms.

The remaining tail is therefore not evidence for a larger owner or semantic queue. Releasing many
file producers together at every low-water transition is a synchronized-burst candidate on the one
shared reliable carrier.

## Decision

Resume scheduler-paused files in bounded batches. The default batch is one transfer per toxcore
owner iteration. Among eligible files, select the oldest pause first; use the transport key only as
a deterministic tie-break. A successfully resumed file leaves the paused set, and if it reaches
high water again its new pause timestamp places it behind older waiters. A resume failure refreshes
its pause time, so another eligible transfer can receive the next turn.

The explicit configuration is:

```text
--file-pacing-resume-batch N
```

`N` must be positive, no greater than 1,024 at the CLI, and no greater than the configured semantic
event limit. The default is one. Each batch is followed by an ordinary toxcore iteration before the
owner considers another batch. The high/low watermarks, minimum hold, required-event fallback,
interactive/control command priority, callback reentrancy rule, and manual pause ownership are
unchanged.

Runtime status adds:

```text
transport-file-pacing-resume-batch-limit
transport-file-pacing-resume-batch-count
transport-file-pacing-resume-batch-maximum
```

Strict proof verification accepts complete absence for historical ADR 0160/0161 evidence. Once any
batch field appears, all three are required, the maximum may not exceed the limit, and successful
resume count must fit the retained batch accounting.

## Consequences

- Low-water drain grants file producers an observable fair turn instead of a synchronized release.
- Batch one deliberately trades some aggregate file throughput for an opportunity to advance sparse
  interactive traffic between producers. The A/B decides whether that trade is useful.
- Oldest-first selection is process-local scheduling state, not durable authority, transfer identity,
  protocol priority, or a separate congestion domain.
- Ratox v1 framing and all file bytes/controls remain unchanged.

## Qualification plan

The deterministic mock-provider gate starts three concurrent producers, requires all three to become
scheduler-paused, completes every producer without semantic backpressure, and proves singleton batch
count/maximum plus zero pause/resume failures. GCC Debug and TSan remain required.

The scientific gate is an exact clean-commit repeat of direct-UDP `ratox-matrix-bulk-8`, compared
with `pair.y0d97_ng`. It must retain all 1,000 samples, exact v6 present/progress accounting,
cancel-to-empty, close, bilateral status/resources, strict raw verification, and compact export.

Two clean runs from commit `dbcba87` are retained. `pair.dwo77gs0` is a valid lifecycle proof but
not a treatment observation: neither side paused once, file progress collapsed to 375,654 aggregate
bytes, CPU fell to about 5% of one core, and render p95 reached 504.428 ms while remote
stage-to-output p95 remained 9.999 ms. It exposes a carrier-starvation state below the reactive
event-queue trigger.

`pair.xs9phpya` exercised 3,167/2,658 singleton resume batches with zero control failures or required
event waits. Against `pair.y0d97_ng`, render p95 improved from 144.120 to 124.811 ms, p99 from
179.491 to 161.242 ms, maximum from 264.277 to 188.401 ms, and 250 ms misses from one to zero.
However, p50 worsened from 47.629 to 56.349 ms and p95 remains far above the 50 ms direct-route
target. Keep the bounded fair default as a lifecycle-safe partial tail improvement; do not advance
the eight-stream latency cell. The next scheduler must constrain carrier load before callback/event
pressure, not merely choose how already-paused producers resume.
