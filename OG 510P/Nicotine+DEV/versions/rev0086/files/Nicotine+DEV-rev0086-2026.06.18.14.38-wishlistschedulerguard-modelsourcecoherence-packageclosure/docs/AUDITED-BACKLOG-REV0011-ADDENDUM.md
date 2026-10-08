# Audited backlog addendum — rev0011

## Front-lane status

- U-123 remains a strict report-candidate.
- PB-01/U-168+U-176 remains a strict report-candidate and is stronger than in rev0010 because it now has a maintainer-grade pytest witness plus compatibility baselines.
- No production-ready disclosure text exists.

## PB-01 refactor

PB-01 is now the canonical peer primary-election report:

```text
PB-01 = U-168 + U-176
U-165 = PierceFireWall support path only
U-171 = address/server-trust family, separate
U-181 = pending message/backpressure family, separate
U-185 = cancellation-token family, separate
```

## Next queued batch

The next narrow batch should be TR-STATUS-01:

```text
U-158 — UploadFailed/UploadDenied claimed username + virtual path can drive download abort/retry state.
U-166 — PlaceInQueueResponse claimed username + virtual path can update queued-download queue position.
```

The goal is to determine whether these share a real request/response provenance harness or whether U-166 is only low-value UI queue-position hardening.
