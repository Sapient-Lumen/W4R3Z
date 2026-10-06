# Admission control and watermark frontier

Revision: rev0028

## Purpose

Define the first BrowserRT overload-governance scaffold: a tiny deterministic admission controller that can sit in front of mailboxes, storage providers, and future scheduler lanes.

## Contract shape

```ts
const controller = createWatermarkAdmissionController({
  lowWatermarkBytes,
  highWatermarkBytes,
  hardLimitBytes,
  criticalMinPriority,
  rejectMinPriorityWhileCongested,
  trace
})

const admission = controller.tryAdmit({ bytes, priority, label })
controller.release(admission.leaseId)
controller.markProviderUnhealthy(reason)
controller.markProviderHealthy(reason)
```

## Policy ladder

```txt
watermark-only
watermark-plus-priority
watermark-plus-provider-health
credit-based
adaptive-concurrency
fair-queue-budgeting
cross-tab admission mesh
```

rev0025 stops at `watermark-plus-provider-health`.

## Required invariants

- Rejecting an admission must not mutate in-flight byte count.
- Crossing the high watermark must be traced.
- Recovery below the low watermark must be traced.
- Critical/user-blocking work may bypass congestion only up to the hard limit.
- Hard limit rejection must beat all other acceptance paths.
- Provider-unhealthy rejection must be visible and reversible.
- The controller must be deterministic under a scripted command sequence.

## Relationship to spill mailbox

A spill mailbox absorbs pressure after admission. An admission controller decides whether a producer may add pressure at all.

Together they create a safer ladder:

```txt
admit to memory
spill to provider
reject low-priority work
protect critical work within hard cap
recover when bytes drain
```

## Non-claims

No fairness across many producers, no MPSC safety, no browser Worker path, no OPFS provider health, no adaptive latency sampling, no throughput measurement.
