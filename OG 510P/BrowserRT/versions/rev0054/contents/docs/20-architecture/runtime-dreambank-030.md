# Runtime dreambank 030 — admission as a first-class runtime gate

Current revision: rev0054

The ambitious idea: BrowserRT should eventually govern every expensive lane through an explicit admission plane before work can consume storage, GPU, worker, render, media, or mesh resources.

## Dream

A future heavy browser app might ask BrowserRT:

```txt
Can this operation enter the storage lane?
Can it bypass congestion because it is user-blocking?
Should it wait, spill, reject, degrade, or retry?
Which provider owns the lease?
Which trace proves the decision?
```

The runtime should answer with a typed admission row, not hidden queue behavior.

## Why this matters

Without admission gates, every other resilience primitive can become too late:

- retry budgets limit retries, but primary work can still flood the lane;
- circuit breakers protect providers, but local memory can already be congested;
- spill queues preserve work, but can become unbounded pressure valves;
- browser tests can pass while future apps accidentally make overload invisible.

Rev0035 does the first fake-provider rung: admission wraps provider-resilience histories and every rejection must show no provider mutation.

## Future ambition

- admission history model walks;
- cross-lane admission budgets shared across storage/render/GPU/media;
- fairness-aware admission by flow;
- admission leases tied to object refs and memory slabs;
- browser Worker and OPFS admission providers only after fake-provider histories mature.
