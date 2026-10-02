# ADR 0161: Count scheduler-paused file transfers as present

Status: accepted, 2026-08-25.

## Context

The first exact direct-UDP `ratox-matrix-bulk-8` run after ADR 0160 completed all 1,000 terminal
samples and closed the terminal stream, but the guest failed immediately afterward. The load gate
counted only incoming records whose projection was `state=active`. ADR 0160 deliberately moves a
live transfer between `active` and `paused` to reserve semantic event-queue headroom. At the end of a
terminal sample interval, a correctly paced transfer can therefore be present, accepted, and
progressed without being active at that instant.

Recovery of a copy-on-write clone of the stopped client disk confirmed 2,705 matched local pacing
pause/resume cycles, zero pause or resume failures, zero required-event backpressure, and a final
event high-water of 137. The failed assertion was consequently measuring a scheduler phase, not
transfer loss. It also retained the stale `ratox-terminal-probe` failure label even though that probe
had completed.

## Decision

Bulk workload evidence accounts for each accepted incoming transfer in exactly one of two live
states:

```text
present = active + paused
```

Admission and post-sample progress gates require the exact expected `present` population. Progress
and position extrema include both states. A transfer in any other state does not count. The v2 live
progress checkpoint and v6 retained observation publish present, active, and paused counts
separately before and after sampling. The strict verifier requires the equation above and exact
expected population; it does not allow pause accounting to conceal a missing transfer.

Historical v1 through v5 observations retain their original active-only interpretation and remain
strictly verifiable. New v6 observations use `state-accounting=active-or-paused`. Live route-loss
evidence applies the same invariant to the unaffected routes. Failure reporting advances from the
terminal-probe phase to explicit bulk-progress and bulk-cancel phases before those operations begin.

## Consequences

- Scheduler phase is no longer confused with transfer existence or concurrency.
- The proof still requires every surviving transfer to have positive position and the exact total
  population to remain present throughout the post-sample checkpoint.
- Active and paused populations remain visible, so excessive pause duty cycle can be analyzed rather
  than erased by an aggregate count.
- This changes the Sandwurm measurement contract only. File bytes, c-toxcore controls, Ratox v1
  framing, authority, cancellation, and product pacing policy are unchanged.

## Diagnostic result

The failed private root is not qualification evidence and is not retained: it has no completed pair
manifest, receipts, resource intervals, or cancellation observation. Its extracted content-free terminal
capture is still useful science. It rendered 1,000/1,000 exact samples with p50/p95/p99/maximum
50.090/194.160/499.049/1,012.296 ms, 37 samples at or above 250 ms, and exact owner-queue p99
1.023 ms. Thus the harness defect did not explain away the eight-stream latency tail.

## Qualification

The clean committed rerun from `cbd8844` completed the full v6 lifecycle and strictly verified as
raw and compact evidence. All eight transfers were present before and after sampling; the final
checkpoint separated seven active plus one paused, all eight had positive position, cancellation
accepted all eight controls in one round, and transfer state reached empty. Client/device event
high-water was 134/138 with zero required waits and 2,917/2,996 matched pacing cycles with no
failures.

The measurement correction is accepted. The performance cell is a valid failure: direct render
p50/p95/p99/maximum was 47.629/144.120/179.491/264.277 ms, with one 250 ms miss. Exact owner p99
was only 0.420 ms. The retained compact proof is `.sandwurm/exports/pairs/pair.y0d97_ng`. This rules
out owner-queue and semantic-event saturation as the primary eight-stream tail and selects
multi-transfer pacing fairness/shared-carrier burst science before treating higher populations as
qualified.
