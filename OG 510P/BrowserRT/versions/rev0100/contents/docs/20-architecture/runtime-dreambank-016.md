# Runtime dreambank 016 — adaptive concurrency kernel

Revision: rev0028

## Dream

BrowserRT should treat **adaptive concurrency as a scheduler sense organ**: a bounded feedback loop that notices when a provider is filling queues faster than it can drain them.

Adaptive concurrency as a scheduler sense organ means BrowserRT can feel overload before queues explode.

BrowserRT should eventually know how much work a lane, provider, or mailbox can safely accept right now.

The far version:

```ts
const limit = rt.admission.adaptive({
  provider: 'opfs-sync-storage-lane',
  protect: ['critical', 'user-blocking'],
  shed: ['maintenance', 'background'],
  target: { queueDelayMs: 8 },
  fallback: 'watermark-static'
})

const lease = limit.tryAcquire({ priority: 'background', weight: 1 })
```

The runtime should then use observed completion latency, queue delay, provider health, timeout/drop signals, and main-thread jank to adjust the number of in-flight tasks.

## New runtime noun

```txt
AdaptiveConcurrencyController
```

It is a feedback controller layered above fixed watermarks. It gates work by current `limit`, records releases as samples, observes a window, and changes the limit.

## Provider ladder

```txt
static-limit
watermark-limit
fake-latency-adaptive-limit
provider-latency-adaptive-limit
lane-wide-adaptive-limit
fair-adaptive-limit
mesh-wide-adaptive-limit
```

rev0025 only implements the fake-latency adaptive rung.

## Control-loop shape

```txt
tryAcquire → admit/reject
release    → record latency/outcome
window     → estimate healthy vs queued
decision   → increase/decrease/probe/hold
trace      → explain every transition
```

## Why it belongs in BrowserRT

Adaptive concurrency crosses BrowserRT's core surfaces:

- worker pool saturation;
- storage-provider latency;
- spill mailbox pressure;
- main-thread jank;
- GPU readback delay;
- media/render deadlines;
- cross-tab mesh pressure;
- plugin budgets.

A serious runtime should expose a common policy vocabulary instead of forcing every library to reinvent a fragile limiter.

## Ambition

The far version can feed multiple signals into admission:

```txt
OPFS write latency
SAB mailbox queue delay
worker task completion latency
long-task observer evidence
GPU readback latency
quota warnings
hidden-tab throttling
cross-tab leader health
```

Then it can degrade deliberately:

```txt
lower background concurrency
spill less and reject earlier
prefer cached summaries
reduce render detail
pause compaction
protect current user interactions
```

## Non-goal for this revision

The rev0025 slice is not a production controller. It is a deterministic proof that BrowserRT can represent adaptive acquire/release/window/probe semantics and trace them.

## Current event anchor

`scheduler:adaptive-concurrency-proof` requires both `adaptive:limit-increase` and `adaptive:limit-decrease` so the controller cannot pass by merely admitting and rejecting static limits.
