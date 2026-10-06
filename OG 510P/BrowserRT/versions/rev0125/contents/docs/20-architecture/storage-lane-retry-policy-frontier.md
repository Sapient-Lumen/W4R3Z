# Storage-lane retry policy frontier

Carry-forward revision: rev0033

## Why this exists

`StorageLaneExecutor` can route fake-provider operations through a lane. That is not enough. A real runtime must also decide what happens when a provider operation fails.

Retries are dangerous because they can:

- duplicate side effects;
- amplify load;
- hide provider sickness;
- make failures nondeterministic;
- turn a small outage into a retry storm;
- blur claims around delivery and durability.

BrowserRT therefore introduces retry as a named contract surface.

## New runtime nouns

```txt
StorageLaneRetryPolicy
StorageLaneRetryController
```

A retry policy owns:

- maximum attempts;
- initial virtual delay ticks;
- multiplier;
- maximum virtual delay;
- deterministic jitter;
- retryable error codes;
- non-retryable error codes.

A retry controller owns:

- logical operation ids;
- attempt ids;
- delayed retry queue;
- virtual tick advancement;
- attempt history;
- success/failure classification;
- trace emission.

## Design rule

Retry is not resubmission by habit. Retry is a scheduled attempt under policy.

```txt
logical operation id != attempt id
```

That distinction is now part of the foundation because future storage, GPU, media, and mesh providers will all need to preserve intent across failed attempts.

## Testing posture

The rev0028 proof uses fake provider faults and virtual ticks. It intentionally does not use wall-clock timers. This keeps the release tier cheap and deterministic.

The next refinement should be model walks or admission-budget integration, not OPFS.

## Required trace vocabulary

```txt
storage-retry:create
storage-retry:submit
storage-retry:attempt-schedule
storage-retry:attempt-result
storage-retry:schedule-delay
storage-retry:ready
storage-retry:complete
storage-retry:fail-final
storage-retry:tick-advance
```

## Non-claims

- No OPFS storage-lane retry proof.
- No browser Worker storage-lane retry proof.
- No durability, fsync, quota, eviction, or crash-recovery claim.
- No exactly-once delivery claim.
- No retry-storm safety or production retry algorithm claim.
- No wall-clock timer, throughput, latency, or SLO claim.
- No cross-browser conformance claim.
