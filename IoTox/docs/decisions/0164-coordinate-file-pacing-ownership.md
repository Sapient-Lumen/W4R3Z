# ADR 0164: Coordinate file-pacing ownership

Status: accepted and qualified at eight streams on direct UDP plus forced TCP, 2026-08-25.

## Context

ADR 0163's first exact clean-commit direct-UDP `bulk-8` proof, `pair.qrggya8w`, strongly activates
the receiver carrier window and improves render p95 from ADR 0162's 124.811 ms to 56.247 ms. Exact
owner p99 is 1.488 ms, all eight files progress, and the carrier records 1,456 admissions plus 1,454
rotations with zero carrier-control failures. The strict direct p95 target remains below 50 ms.

The 20 ms quantum rotates almost every service opportunity for the complete 32-second sample. The
receiving endpoint's older reactive event pacer also records 141 pause failures while its carrier
manager is independently pausing the same Tox receive. c-toxcore has an exact
`TOX_ERR_FILE_CONTROL_ALREADY_PAUSED` outcome for this ownership collision. Treating that outcome as
an undifferentiated provider failure loses the useful fact and risks assigning automatic resume
authority to the wrong scheduler.

Cancellation exposes a separate terminal race. Required file-chunk events can already be in the
Agent queue when accepted local cancellation removes the staging destination. Such bytes must never
be written, but their arrival is expected cancellation fallout rather than evidence that the peer
sent data without admission.

## Decision

The default incoming carrier rotation quantum becomes 50 ms. The one-file per-peer window remains
unchanged. This reduces pause/resume churn while preserving a bounded oldest-first turn: with eight
waiting files, one complete round is nominally bounded by 400 ms plus service/provider delay.

The reactive transport pacer recognizes `TOX_ERR_FILE_CONTROL_ALREADY_PAUSED` as external local
ownership. It does not add the transfer to its auto-resume set, does not count a provider failure,
and increments the content-free counter:

```text
transport-file-pacing-external-pause-count
```

The external owner remains solely responsible for resuming that pause. Other typed pause failures
retain their existing failure accounting. Strict proofs that contain the new counter require both
reactive pause/resume failure counters to be zero; historical proofs may omit the field.

Accepted local cancellation retains at most 1,024 incoming transfer keys as terminal tombstones.
Already-queued data/completion events for those keys are discarded successfully without a
descriptor, write, publication, or second provider control. A fresh Tox offer for the same key and
friend terminal state clear the classification. Unknown unadmitted keys remain protocol errors.

## Consequences

- Reactive queue protection and proactive carrier fairness now have explicit, non-overlapping resume
  ownership instead of interpreting a legitimate collision as failure.
- The larger quantum may increase an individual bulk file's wait while reducing carrier churn and
  interactive tail latency. The two-guest gate decides whether 50 ms is the useful default.
- Late events after accepted cancellation are fail-safe no-ops; malformed data without an exact
  cancellation tombstone remains rejected.
- Ratox v1 framing, Tox custom-packet selection, file bytes/IDs, sync manifests, authority, and
  route semantics remain frozen.

## Qualification

Deterministic mock-provider coverage forces one already-paused outcome, proves external ownership
count one and failure count zero, resumes only through the external caller, and completes the file.
The carrier test injects data and completion after accepted cancellation, proves both are harmless,
and retains protocol rejection for an unknown key. GCC Debug, ThreadSanitizer, flake evaluation, and
verifier compatibility are mandatory.

The scientific gate repeats the exact clean-commit direct-UDP `ratox-matrix-bulk-8` cell. It requires
all eight files to progress, positive carrier rotation, a positive or zero coherent external-pause
count, zero carrier/reactive control failures, no terminal file-transfer diagnostic, owner p99 below
2 ms, render p95 below 50 ms, complete resources/lifecycle evidence, and strict raw plus compact
verification.

## Direct-UDP result

Clean commit `63e845b904d4a7dbd85c9e11d92b58965314b4f4` produced strict compact proof
`.sandwurm/exports/pairs/pair.bo6l0der`. All eight files progressed by 170,498,931 aggregate bytes.
The receiving client recorded 512 admissions, 507 rotations, 77 exact external-pause handoffs, and
zero carrier/reactive failures; both event queues avoided required backpressure and ended empty.
There was no terminal file-transfer failure.

Render p50/p95/p99/max was 19.934/39.634/55.093/81.084 ms and owner p99 was 1.917 ms. The strict
direct p95 and common owner p99 gates both pass. Relative to the 20 ms proof, rotations fell 65%,
client/device event high-water fell from 577/297 to 228/168, and all-file progress increased. The
50 ms quantum and ownership coordination are accepted for the direct route. Forced TCP remains a
separate route-class gate.

Clean commit `1823531e10e2f62d460fb58fa72fd2ea9bc8d97f` then produced strict forced-TCP proof
`.sandwurm/exports/pairs/pair.pitcu1pk` with the identical binary. All eight files progressed by
139,548,606 bytes; the receiver recorded 742 admissions, 739 rotations, 58 typed handoffs, and zero
true failures. Render p50/p95/p99/max was 24.636/76.249/98.314/119.607 ms, owner p99 was 1.525 ms,
and no render reached 250 ms. The separate forced-TCP route gate passes. Higher stream counts remain
independent scientific gates.
