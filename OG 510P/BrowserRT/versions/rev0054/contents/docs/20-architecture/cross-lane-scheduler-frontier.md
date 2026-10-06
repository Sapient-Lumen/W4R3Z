# Cross-lane scheduler frontier

Revision: rev0028

`CrossLaneScheduler` is the rev0025 baby scheduler primitive. It is intentionally fake-provider and deterministic: it does not run real workers, OPFS, WebGPU, render, media, or mesh providers. Its job is to make the lane vocabulary concrete before future sessions spend expensive browser or provider budget.

## Contract earned now

A task has:

```txt
id
lane
priority
flowId
cost
dependsOn
fallbackLanes
payload/metadata
```

A lane has:

```txt
id
rank
capacity
quantum
maxQueuedCost
health
queued cost
in-flight task set
deficit counter
trace events
```

The current dispatch loop is deliberately small:

1. walk lanes by deterministic lane rank;
2. skip unhealthy lanes unless the task was routed at enqueue time through a healthy fallback lane;
3. skip lanes at capacity;
4. skip tasks whose dependencies are not complete;
5. add lane quantum and dispatch only when the head task has enough deficit;
6. require explicit `complete(taskId)` before capacity is released and dependency consumers can proceed.

This is not a final scheduling algorithm. It is a contract proof surface that lets future sessions argue about lanes, capacity, provider health, dependencies, routing, cost, deficit, and trace evidence without inventing new vocabulary.

## Trace vocabulary

The proof depends on these events:

```txt
crosslane:create
crosslane:lane-create
crosslane:enqueue
crosslane:routed-enqueue
crosslane:reject
crosslane:lane-unhealthy
crosslane:lane-healthy
crosslane:defer-dependency
crosslane:lane-at-capacity
crosslane:deficit-add
crosslane:dispatch
crosslane:complete
crosslane:dispatch-empty
```

## Why this is useful

The primitive gives BrowserRT a place to attach later scheduler ideas:

- lane-specific provider health;
- admission and adaptive concurrency decisions;
- priority and fairness policy;
- fake-provider simulations;
- replayable trace evidence;
- eventual worker/storage/GPU/render provider integration.

## Audit/factor added

`facility:scheduler-contract-audit` checks that the scheduler surface is visible in source, docs, manifest, proof artifacts, and non-claim surfaces. This is an office-maintenance task: future sessions should be able to resume respectfully and know exactly what was earned.

## No production scheduler claim

The following remain non-claims:

- No production scheduler claim.
- No real preemption proof.
- No work-stealing implementation claim.
- No browser Worker scheduler proof.
- No OPFS/WebGPU/render/media/cross-tab provider integration proof.
- No latency, throughput, or fairness-SLO claim.

## Rev0025 model-walk amendment

Rev0025 adds `scheduler:cross-lane-model-walk-proof`, a deterministic seeded model-walk over the fake-provider `CrossLaneScheduler`. This is a semantic refactor guard: generated scheduler operations are compared against an independent oracle after every step. It strengthens confidence in queue accounting, lane health, fallback routing, dependency deferral, and rejection no-mutation behavior.

This amendment is not a production scheduler claim. It is not exhaustive formal verification, true concurrent interleaving, browser Worker scheduling, work stealing, priority inheritance, deadline scheduling, DRF, or a performance/fairness claim.
