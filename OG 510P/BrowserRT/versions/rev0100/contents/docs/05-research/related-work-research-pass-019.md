# Related work research pass 019 — scheduler kernels and cross-lane contracts

Revision: rev0028

This pass asks what BrowserRT can steal from serious scheduling systems before it spends browser or provider budget. The point is not to copy an algorithm. The point is to shape a small contract that future provider schedulers can respect.

## Sources studied

- Kubernetes Scheduling Framework scheduling/binding cycles and plugin vocabulary.
- Dask scheduler policies and fixed task-state vocabulary.
- Tokio runtime scheduler and task model.
- Go scalable scheduler design and Go scheduler work-stealing discussions.
- Apple Dispatch / Grand Central Dispatch queues.
- libuv event-loop and threadpool design notes.
- SEDA staged event-driven architecture: stages, queues, admission control, and dynamic controllers.
- Prioritized Task Scheduling API.
- Kubernetes pod priority/preemption and API Priority and Fairness vocabulary carried forward from earlier passes.
- Ray placement-group/resource-bundle scheduling pressure carried forward from earlier actor/object-ref passes.
- OpenTelemetry traces/spans vocabulary carried forward for proof evidence.

## Ideas stolen

### 1. Runtime schedulers split drivers, work, timers, and resources

Tokio is useful because it frames a runtime as more than a task queue: it has I/O driver resources, timers, and a scheduler. BrowserRT should similarly avoid a single queue. It needs lanes for CPU, storage, GPU, render, media, mesh, maintenance, and interactive work.

### 2. Work stealing is not the first contract

Go/Tokio-style work stealing is tempting, but rev0025 deliberately does not implement it. BrowserRT first needs the lower contract: what is a lane, what does dispatch mean, what happens when a lane is full or unhealthy, how dependencies are represented, and how proof artifacts tell future sessions what happened.

### 3. Dispatch queues are a vocabulary, not a browser solution

Grand Central Dispatch reinforces that users should submit work to queues rather than manually manage raw threads. BrowserRT should eventually give app authors small names such as `storage`, `gpu`, `interactive`, and `maintenance`, not ask them to micromanage every Worker.

### 4. libuv warns that I/O and CPU must not be collapsed

libuv separates the event loop from its threadpool and uses the threadpool for file-system work. BrowserRT should not pretend all lanes are equal: storage workers, GPU dispatch, CPU workers, and render work have different blocking and recovery behavior.

### 5. Browser scheduler APIs are provider hints, not the kernel

The Prioritized Task Scheduling API gives browser-level priority/yield tools, but it is not universally baseline and cannot be BrowserRT's whole scheduler. BrowserRT should map onto it where present, trace when it does, and keep its own lane contracts independent of that provider.

### 6. Scheduler frameworks need extension points, but BrowserRT first needs contracts

Kubernetes scheduling is useful because it separates scheduling/binding cycles and extension points. BrowserRT should eventually allow lane providers to contribute admit/filter/score/bind-like decisions, but rev0025 only earns the smaller fake-provider contract.

### 7. Stateful schedulers need explicit state names

Dask is useful because it names task states and transitions. BrowserRT should eventually do the same for queued, deferred, in-flight, completed, rejected, cancelled, and failed tasks so future refactors do not erase semantics.

### 8. Stages and queues are the right mental model for browser lanes

SEDA is useful because it decomposes services into stages connected by queues and treats admission control as part of load conditioning. BrowserRT lanes should evolve as stages with queues, controllers, provider health, and telemetry.

### 9. Scheduling needs traces as proof, not vibes

OpenTelemetry vocabulary keeps pushing this cube toward spans/events. Every future lane decision should have a trace: admitted, deferred, dispatched, routed, completed, rejected, cancelled, or failed.

## What rev0025 turns into code

The concrete slice is intentionally fake-provider and release-tier friendly:

- `CrossLaneScheduler`.
- lane definitions with rank, capacity, quantum, health, and queue-cost limits;
- task priority, lane, flow id, cost, dependencies, and fallback lanes;
- dispatch events and completion events;
- lane health and fallback routing;
- no-mutation rejection checks;
- an audit that verifies source/docs/manifest/proof/non-claim coherence.

## What remains forbidden

- No production scheduler claim.
- No work-stealing implementation claim.
- No browser Worker scheduler proof.
- No preemption proof.
- No latency, throughput, or fairness-SLO claim.
- No OPFS/WebGPU/render/media/cross-tab provider integration proof.
