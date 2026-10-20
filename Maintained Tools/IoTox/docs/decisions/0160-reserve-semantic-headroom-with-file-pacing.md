# ADR 0160: Reserve semantic headroom with explicit file pacing

Status: accepted, 2026-08-24.

## Context

ADR 0159 restored required per-chunk file events after removing them exposed severe reliable-carrier
head-of-line blocking. The descriptor-only two-guest rerun recovered terminal render p95 from
505.064 ms to 51.146 ms, but the client event queue reached its exact 1,024-entry limit and spent
248.625 ms in 1,227 required-event waits. Interactive owner p99 remained 3.972 ms, above the strict
2 ms loaded budget.

Required-event backpressure is the final lossless safety net, not a bulk scheduler. Letting file
callbacks consume every event slot couples c-toxcore production, the Agent consumer, and unrelated
semantic delivery at the queue's failure boundary. Removing that coupling without retaining a rate
limit recreates the much worse shared-carrier failure measured by ADR 0159.

## Decision

Reserve most of the 1,024-entry semantic event queue. At 64 pending events, schedule a local
`tox_file_control(PAUSE)` for each active synchronous outgoing or incoming data transfer that
produced the pressure. Execute that control only after `tox_iterate()` returns; ordinary c-toxcore
APIs are never entered recursively from callbacks. Resume a scheduler-paused transfer only after the
queue drains to 16 events and the pause has lasted at least 5 ms. Interactive and control owner work
runs before any resume and before the next provider iteration.

The thresholds are explicit product configuration:

```text
--file-pacing-high-events N
--file-pacing-low-events N
--file-pacing-hold-us N
```

Enabled pacing requires `0 <= low < high < max_pending_events` and a 100..1,000,000 us hold. Both
watermarks may be zero only for focused queue-contract tests. Pause failure leaves required-event
backpressure as the fail-safe; it never permits a semantic event to disappear.

An explicit local PAUSE takes ownership of an already scheduler-paused transfer without issuing a
second pause, and the scheduler will not resume it. Explicit RESUME/CANCEL, peer cancellation,
disconnect, completion, and shutdown clear scheduler state. No pacing state is durable or an
authority fact.

## Consequences

- The event queue has a large semantic reserve instead of serving as the normal file-rate governor.
- The reliable carrier receives bounded 5 ms file gaps in which sparse Ratox work can advance. This
  is scheduling, not a claim of transport priority or independent congestion domains.
- Runtime status exposes paused transfers, configured watermarks/hold, pause/resume/failure counts,
  and total/maximum successful hold time. New bilateral Ratox proofs require the complete set when
  any pacing field is present; historical proofs without it remain valid.
- Per-chunk required events remain in place for exact bookkeeping and lossless failure behavior.
  Their queue waits should become exceptional, but qualification—not construction—decides that.
- Ratox v1 framing, file bytes, transfer integrity, authority, and route identity remain unchanged.

## Qualification

The exact clean-commit two-Sandwurm-guest direct-UDP `ratox-matrix-bulk-1` run from `5305e7d` passes.
All 1,000 samples rendered and closed beside one simultaneous 1 GiB transfer per role. Render p95
was 42.727 ms, owner p99 was 1.499 ms, and no sample reached 100 or 250 ms. Client/device event
high-water fell from the prior 1,024/765 to 180/130, with zero required-event waits.

The scheduler made 853/876 matched pause/resume transitions, recorded zero pause/resume failures,
and quiesced with no paced transfer on either role. The strict raw proof passed, its compact proof
`.sandwurm/exports/pairs/pair.a4j1uirz` reverified after the audited 2.4 GiB raw-root reclamation, and
both final Agent status records bind the complete pacing evidence. The direct-route `bulk-1` branch
therefore advances without requiring the protected route. The matched exact forced-TCP cell also
passes its route-independent owner gate at 1.452 ms p99, with render p95/p99 reported separately at
57.594/70.044 ms, zero 250 ms misses, queue high-water 183/102, and zero pacing failures. Higher
load cells remain separate gates.
