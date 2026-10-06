# Scheduler model and simulation frontier

Revision: rev0028

The rev0024 cross-lane scheduler proof proved one concrete contract scenario. Rev0025 adds a different kind of guard: a deterministic model walk that compares the live `CrossLaneScheduler` to a small independent reference model after generated operations.

## Why this frontier matters

A scheduler is dangerous to refactor because many bugs are accounting bugs: a rejected task mutates state, a dependency waits forever, a lane-health change blocks unrelated lanes, an in-flight task leaks, or fallback routing silently violates queue order. One hand-authored proof can miss those bugs. A reference model gives future sessions a cheap semantic oracle. The live scheduler snapshot is also checked through `validateCrossLaneSchedulerSnapshot` after generated steps so accounting drift is caught even before model divergence.

Rev0025 also exports `validateCrossLaneSchedulerSnapshot`, a cheap invariant helper that checks queued counts, queued costs, in-flight counts, lane capacity, duplicate task placement, and sorted completed ids before deeper model comparisons run. deterministic replay is required: the same seed must produce the same scheduler/model signature.

## Related-work pressure

Kubernetes' Scheduling Framework separates scheduling and binding cycles and exposes extension points. BrowserRT should eventually separate admission, placement, binding, execution, completion, and reconciliation rather than hiding everything inside one queue.

Tokio keeps runtime pressure on local queues, global queues, I/O/timer drivers, and work stealing. BrowserRT does not claim work stealing, but it should preserve room for local-agent queues and explicit stealing evidence later.

FoundationDB-style deterministic simulation is the north-star testing idea: run a complicated system in a controlled fake universe, make the randomness seeded, and preserve counterexamples. BrowserRT is not doing full deterministic simulation yet, but every provider family should move toward a small model, seeded command generator, invariant checker, deterministic replay artifact, and replayable counterexample shape.

TLA+ and other model-checking approaches remind us that concurrency bugs should be found in small models before code hardens around bad assumptions. Rev0025 is not formal verification; it is a cheap executable model-walk rung.

## Current model scope

`scheduler:cross-lane-model-walk-proof` models:

- enqueue acceptance and rejection;
- no-mutation rejection;
- lane health transitions;
- fallback routing at enqueue time;
- priority ordering inside lanes;
- lane-rank ordering across lanes;
- dependency deferral;
- in-flight capacity;
- dispatch identity;
- completion accounting;
- final drain accounting;
- trace event presence.

## Future simulation ladder

1. Keep the release-tier model walk cheap and current.
2. Add cross-lane interleaving simulation for submit/dispatch/complete races.
3. Compose the scheduler model with fake persisted-spill and admission providers.
4. Add provider failure/recovery histories.
5. Add deadline/yield modeling with explicit missed-deadline non-claims.
6. Add browser Worker scheduler smoke proof by explicit browser tier only.
7. Add same-origin mesh placement simulation before real cross-tab work.

## Non-claims

- No exhaustive model checking or formal verification claim.
- No production scheduler claim.
- No true concurrent interleaving, preemption, work stealing, priority inheritance, or deadline scheduling proof.
- No browser Worker scheduler proof.
- No OPFS, WebGPU, render, media, or mesh provider integration proof.
- No throughput, latency, fairness-SLO, or real performance claim.
