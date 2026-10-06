# Related work research pass 022 — storage lanes, blocking pools, object locality

Revision: rev0028

This pass studies runtimes that keep blocking storage, object movement, and scheduling policy from collapsing into one vague queue. The goal is to sharpen BrowserRT's next rung: provider-integrated storage-lane scheduling that remains fake-provider, deterministic, and claim-gated.

## Sources remembered

- libuv thread pool work scheduling: libuv internally uses a thread pool for file-system operations and exposes work-queue vocabulary. BrowserRT should treat storage work as a lane with capacity and health, not as random background callbacks.
- libuv file-system operations: async file operations still run through a threadpool, which reinforces that "async API" can hide bounded blocking resources.
- Tokio `spawn_blocking`: blocking work gets a separate pool, but long-lived blocking tasks reduce effective capacity. BrowserRT should track provider occupancy, capacity blocking, and admission instead of pretending storage work is free.
- Ray Core objects: tasks and actors produce object refs that can live outside the caller. BrowserRT's data plane should preserve object-ref thinking across blocks, mailboxes, OPFS, SAB, and future GPU buffers.
- Ray scheduling: locality and resource utilization both matter. BrowserRT's storage lane should remember where payload refs live and when provider health changes placement decisions.
- Dask scheduling policies and work stealing: scheduling can optimize placement, but work stealing can backfire. BrowserRT should make provider migration/fallback explicit and traced, not implicit magic.

## Stolen ideas

- Storage is a scarce runtime lane, not a generic async function.
- Provider health belongs in scheduling decisions.
- Blocking work needs its own capacity accounting.
- Object refs are the boundary between control-plane tasks and data-plane payloads.
- Scheduling should keep locality and provider readiness visible.
- Work stealing and fallback are future claims, not default behavior.
- A provider-integrated proof should compose existing primitives rather than inventing a new scheduler.

## Ambitious dream

BrowserRT eventually has a storage-placement plane:

```txt
storage operations declare provider, object refs, cost, priority, dependency, fallback, retention policy
scheduler dispatches through storage/maintenance lanes
provider health and quota feed back into admission
compaction and checkpointing are maintenance work, not hidden side effects
object refs preserve locality and ownership boundaries
trace shows why a task ran, waited, failed, or was rejected
```

The "one runtime" dream is not a bigger queue. It is a small set of provider contracts that let storage, IPC, GPU, render, media, and mesh lanes share one scheduling language without sharing false guarantees.

## Boundary

Rev0027 earns only a fake-provider composition proof: `CrossLaneScheduler` drives a `PersistedSpillMailbox` through `StorageLaneExecutor`. It does not earn OPFS, browser Worker storage, durability, quotas, eviction behavior, work stealing, throughput, or production scheduler claims.
