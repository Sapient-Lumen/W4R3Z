# Runtime dreambank 017 — priority fairness as an overload-governance primitive

Revision: rev0028

BrowserRT can become a browser userspace kernel only if it can govern overloaded local work. The previous rungs gave it bounded queues, spill, watermarks, and adaptive concurrency. This rung adds a missing noun: **fairness across flows**.

## Dream

A future BrowserRT task could carry:

```txt
priority: critical | user-blocking | user-visible | background | maintenance
flowId: user/session/plugin/provider/component identity
cost: estimated bytes/cpu/ms/work units
lane: cpu/storage/gpu/render/media/mesh
```

The scheduler would then answer:

```txt
Which priority class is protected?
Which flow is noisy?
Which lower-priority work may borrow spare capacity?
Which task must be rejected before it mutates state?
Which trace proves that decision?
```

## Borrowed vocabulary

- **Priority level:** protects critical work from best-effort floods.
- **Flow:** groups related work so a noisy producer can be isolated.
- **Deficit:** credit used to schedule variable-cost work fairly.
- **Noisy neighbor:** one flow that should not starve peers.
- **Borrowing:** lower-priority work may use idle capacity but should not steal from protected work.
- **Load shedding:** rejecting work deliberately to keep the runtime alive.

## Baby primitive in this revision

`PriorityFairScheduler` implements a small deterministic priority + flow scheduler:

- fixed priority order;
- per-priority quantum;
- per-flow queue;
- deficit accounting;
- variable task cost;
- global queue cost limit;
- per-flow queue cost limit;
- oversize task rejection;
- no-mutation rejection evidence;
- trace events for creation, enqueue, reject, deficit add, dispatch, and empty flows.

## Why not more yet

This is not the BrowserRT scheduler. It is a proof surface for one scheduling law:

```txt
Priority protects critical work; deficit-style flow rotation prevents same-priority noisy-neighbor starvation.
```

The actual runtime scheduler still needs deadlines, cancellation, cross-lane resource estimates, worker affinity, storage/GPU/readback pressure, and mesh behavior.

## Future frontier

- Priority borrowing across lanes.
- Cross-lane fairness between CPU/storage/GPU/render work.
- Deadline-aware dispatch.
- Provider-health-aware fairness.
- Multi-agent scheduler state.
- Deterministic replay of scheduling decisions.
- Browser Worker scheduler proof.
- Scheduler trace viewer.

## Non-claims

- No production scheduler claim.
- No exact Kubernetes, DRR, Linux CFS, WFQ, or SRE implementation.
- No preemptive scheduling.
- No browser Worker proof.
- No throughput/latency performance evidence.
