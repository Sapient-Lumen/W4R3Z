# Runtime dreambank 019 — one scheduler to coordinate lanes, not one queue to own them all

Revision: rev0028

The mile-high dream is that BrowserRT becomes a local browser compute kernel. This pass turns that dream toward scheduling. The one-to-rule-them-all scheduler is not a giant universal algorithm. It is a disciplined contract that lets each provider lane be honest about capacity, health, cost, dependencies, and fallback.

## Ambitious shape

Imagine a future BrowserRT job graph:

```txt
interactive input
  -> parse command on interactive lane
  -> read blocks on storage lane
  -> compute summary on cpu or gpu lane
  -> update canvas on render lane
  -> compact old state on maintenance lane
```

The kernel should know that storage is a lane with exclusive handles, GPU is a provider with device-loss risk, CPU is parallel but not infinite, render has frame-budget pressure, and maintenance should not starve user-visible work.

## Provider ladder

The scheduler should eventually choose among:

```txt
main-thread cooperative provider
browser Worker pool provider
Node worker_threads provider
storage-worker provider
OPFS sync-handle provider
WebGPU provider
OffscreenCanvas render provider
media/WebCodecs provider
same-origin mesh provider
fake deterministic provider
```

The key is not that all providers are implemented now. The key is that every provider can speak the same small language:

```txt
admit -> enqueue -> defer/dispatch -> complete/fail/cancel -> trace
```

## Why cross-lane comes after fairness/admission/adaptive control

Earlier slices gave us local pieces:

- bounded queues and ring buffers;
- spill and persisted-spill semantics;
- admission watermarks;
- adaptive concurrency;
- per-priority/per-flow fairness.

Rev0024 connects those ideas at the lane level. It asks how work moves across `interactive`, `cpu`, `storage`, `gpu`, and `maintenance` without promising production scheduling.

## The future crazy version

A real future BrowserRT scheduler may include:

- work stealing among CPU workers;
- lane-specific admission controllers;
- storage handle leases;
- GPU device-loss fallback;
- render frame-budget deadlines;
- cross-tab leader-election for maintenance;
- trace-driven replay;
- deterministic fake-provider simulation;
- model walks for dependency graphs;
- priority inheritance;
- resource reservations;
- preemption by worker termination where safe.

## The baby version earned here

Rev0024 earns only this:

```txt
CrossLaneScheduler can deterministically route, defer, dispatch, complete, and reject fake tasks across fake lanes, with trace evidence.
```

That is enough to let future sessions climb stairs without pretending the staircase is already a building.
