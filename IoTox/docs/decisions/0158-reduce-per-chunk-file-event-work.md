# ADR 0158: Reduce per-chunk file-event work

Status: superseded in part by ADR 0159, 2026-08-24. The retained receive descriptor and
backpressure diagnostics remain accepted; outgoing progress coalescing does not.

## Context

The first strict direct-UDP `ratox-matrix-bulk-1` rerun after ADR 0157 completed and closed all
1,000 samples, proving that periodic Ratox service no longer stalls behind required file events. It
did not meet the R7 latency gate: render p95 was 71.698 ms against 50 ms, and interactive owner-queue
p99 was 7.114 ms against a strict below-2 ms target. Render p99 remained 96.588 ms, no sample reached
250 ms, and remote stage-to-output p95 was 15.654 ms.

The cell moves simultaneous 1 GiB finite files in both directions while sampling the terminal. At
the observed interval, the client consumed 80.2% of one CPU and the device 97.3%. The production
sender had already supplied each 1,371-byte chunk synchronously inside c-toxcore's callback, but it
still queued a required Agent bookkeeping event for every accepted request. The receiver also
duplicated and closed its already pinned destination descriptor around every positional write.
Neither operation adds integrity, authority, terminal truth, or completion truth.

## Decision

For an outgoing transfer with a transport-owned synchronous source, emit required progress on the
first accepted nonterminal request and each subsequent 256 KiB high-water crossing. Count every
suppressed request explicitly. Terminal requests, typed source/send failures, offers, controls, and
all incoming chunk bytes remain required and uncoalesced.

The incoming manager keeps its one no-follow, inode-validated destination descriptor for the entire
receive. It holds the existing transfer mutex across each bounded `pwrite` and position update rather
than performing `F_DUPFD_CLOEXEC`, `pwrite`, and `close` per provider chunk. Local pause/cancel/list
operations may wait for that one bounded write; they cannot change or close the descriptor during it.

Transport status now exposes current and maximum pending events, coalesced inline progress count,
and count/total/maximum time for required-event backpressure. These are monotonic content-free
diagnostics, not relaxed delivery semantics.

## Consequences

- Successful outgoing progress is sampled, not exact per chunk. The final callback is still exact,
  and an explicit live list returns the manager's latest sampled outgoing position.
- Incoming bytes, ordering, positional validation, destination identity, and atomic completion are
  unchanged.
- The receive mutex may be held across a filesystem write. The provider chunk is bounded to the
  configured maximum (1,371 bytes in the qualified provider), so this removes descriptor churn
  without authorizing an unbounded blocking operation.
- The counters distinguish event-queue saturation from provider/network tails in the next exact VM
  rerun. They do not themselves change the R7 budgets.
- This optimization precedes a dedicated-route decision because the first loaded owner queue was
  already above target; route isolation alone would not remove local owner/event work.

## Evidence

- A transport regression supplies a complete inline file, observes only its first nonterminal
  progress event plus terminal completion, and requires the exact suppressed-event count.
- Existing file-transfer tests retain out-of-order, cancellation, descriptor identity, completion,
  and restart coverage. Runtime tests freeze every new diagnostic field.
- The 30-group owned registry and all 45 GCC ThreadSanitizer entries pass; five delegated-cgroup
  host-capability oracles retain their named skips. Exact committed two-guest `bulk-1`
  requalification is required before this becomes accepted latency evidence.
