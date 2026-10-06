# Priority fairness frontier

Revision: rev0028

BrowserRT's overload-governance ladder now has these rungs:

```txt
bounded channel
  -> spill mailbox
  -> watermark admission
  -> adaptive concurrency
  -> priority/fairness scheduling
```

The new question is not merely whether work can enter the runtime. It is whether the runtime can preserve critical work and prevent same-priority starvation under pressure.

## Current primitive

`PriorityFairScheduler` is a deterministic baby provider. It is intentionally small:

```ts
const scheduler = createPriorityFairScheduler({
  maxQueuedCost: 400,
  maxFlowQueuedCost: 96,
  maxTaskCost: 64
})

scheduler.enqueue({ flowId: 'plugin-a', priority: 'background', cost: 7 })
scheduler.enqueue({ flowId: 'plugin-b', priority: 'background', cost: 3 })
const next = scheduler.dispatchNext()
```

## Current invariants

- Higher priority dispatches before lower priority when higher priority has dispatchable work.
- Same-priority flows rotate through a deficit-style scheduler.
- Variable task cost affects flow credit.
- A noisy flow cannot exceed its queue-cost limit.
- Oversize tasks are rejected.
- Rejected work must not mutate queue cost or queue count.
- Every important decision emits a trace event.

## What future sessions should respect

Do not turn this into a production scheduler by assertion. Earn the next rung:

1. define the invariant;
2. add a tiny model/proof;
3. add a manifest task;
4. emit trace evidence;
5. update non-claims.

## Non-claims

- No preemption.
- No deadline handling.
- No cross-lane resource scheduling.
- No browser Worker scheduler proof.
- No multi-threaded scheduler contention proof.
- No performance claim.
