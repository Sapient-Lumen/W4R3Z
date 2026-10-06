# Related work map: what BrowserRT should steal

This revision imports ideas from adjacent systems without importing their scope.
It records source names, patterns, and hazards. Direct external source links are
intentionally not stored in the cube because the cube remains cloudtainer-only and
URL-free under validation; use the source registry by name when re-researching.

## Summary thesis

The serious adjacent work clusters into single-slice systems:

- worker RPC convenience;
- worker pools;
- off-main-thread script relocation;
- task-graph schedulers;
- actor/object runtimes;
- browser micro-OS/dev environments;
- service-worker/offline tooling;
- OPFS/WebGPU/WebCodecs/OffscreenCanvas substrate APIs;
- high-performance browser products that quietly built internal runtimes.

BrowserRT should not clone any one of them. Its opening is to become the
coherent boundary layer between all of them: a browser userspace kernel with a
control plane, data plane, resource scheduler, storage lane, GPU lane,
observability, and cross-tab mesh.

## Worker RPC lineage

Representative sources: Comlink, threads.js.

What they get right:

- They make worker calls easy enough that application developers will actually
  use them.
- They hide message-port plumbing and expose async interfaces.
- They prove that pleasant ergonomics matter, not just raw throughput.

What BrowserRT should steal:

- A thin optional RPC facade for cold paths and developer ergonomics.
- Transfer handlers / adapters for values that need custom movement semantics.
- A clear rule that every remote call is async, even when it looks local.

What BrowserRT should refuse:

- Making RPC the default hot path.
- Hiding large structured-clone costs behind a friendly function call.
- Letting worker APIs imply that memory ownership is casual.

BrowserRT stance: RPC is a shell. The kernel hot path is binary envelopes,
buffer refs, streams, shared slabs, and storage refs.

## Worker pool lineage

Representative sources: Piscina, Tinypool, workerpool, Node worker threads.

What they get right:

- Worker lifecycle and pooling need explicit policy.
- Queue size, utilization, task isolation, and worker restart behavior are real
  API concerns.
- CPU-bound work and I/O-bound work need different treatment.

What BrowserRT should steal:

- Pool-level observability.
- Resource hints and admission control.
- Worker crash isolation.
- Node backend for cloudtainer tests.
- Small install footprint discipline from tiny-pool variants.

What BrowserRT should refuse:

- Treating the runtime as only a CPU worker pool.
- Assuming worker count equals available useful parallelism.
- Treating storage, GPU, render, media, and cross-tab coordination as somebody
  else's problem.

BrowserRT stance: workers are one lane family inside a resource kernel.

## Off-main-thread relocation lineage

Representative source: Partytown.

What it gets right:

- Main-thread budget is a product feature.
- Moving work to workers may require proxying APIs that were not designed for
  workers.
- Tradeoffs must be documented because not every script or API is safe to move.

What BrowserRT should steal:

- A disciplined main-thread proxy/bridge model for the few operations that must
  touch DOM or browser UI state.
- A strong tradeoff page for latency, unsupported APIs, and synchronous-looking
  calls that are actually remote.
- The posture that the main thread is sacred and must be explicitly budgeted.

What BrowserRT should refuse:

- Pretending sync remote calls are free.
- Trying to virtualize the entire DOM as a first implementation goal.

BrowserRT stance: the main thread is a scarce interrupt lane, not the default
place to compute.

## Browser micro-OS lineage

Representative source: WebContainers.

What it gets right:

- The browser can host a surprisingly complete local operating environment.
- A filesystem/process mental model can be compelling in web apps.
- Boot experience, sandbox boundaries, and developer tools matter as much as raw
  primitives.

What BrowserRT should steal:

- The audacity of a browser-native OS-like abstraction.
- A clear boot profile and capability report.
- The idea that local browser software can feel like a platform, not a page.

What BrowserRT should refuse:

- Cloning Node-in-the-browser as the core mission.
- Depending on external services, hosted packages, or opaque runtimes.

BrowserRT stance: not a Node clone; a browser userspace kernel for application
workloads.

## Wasm thread lineage

Representative sources: Emscripten pthreads, Emscripten Wasm Workers, Wasm
Component Model docs.

What they get right:

- Shared memory plus workers unlocks real multithreaded Wasm.
- Cross-origin isolation is not incidental; it is a deployment constraint.
- Component boundaries and typed interfaces matter once plugins arrive.

What BrowserRT should steal:

- SAB-is-a-tier, not baseline.
- Worker pool prewarming for threaded Wasm kernels.
- Wasm module adapters with explicit memory import/export rules.
- Future component-style plugin contracts.

What BrowserRT should refuse:

- Making Wasm mandatory.
- Letting Wasm modules bypass runtime telemetry, memory policy, or cancellation
  rules.

BrowserRT stance: Wasm kernels are processes/plugins governed by the same
scheduler and memory contracts as JS kernels.

## Distributed/task runtime lineage

Representative sources: Dask, Ray, Tokio, libuv.

What they get right:

- Task graphs and dependencies are the right model for complex pipelines.
- Stateful actors are distinct from stateless tasks.
- Work stealing helps with imbalanced workloads, but locality and synchronization
  costs matter.
- Event loops and blocking pools must be separated.
- Dashboards and scheduler introspection are not luxuries.

What BrowserRT should steal:

- Dask-style task graphs for pipelines.
- Ray-style actors and object refs for stateful browser processes.
- Tokio-style local queues with stealing, but adapted to workers and browser
  priorities.
- libuv-style separation between event loop and background blocking work.
- Scheduler dashboards as part of the runtime, not an afterthought.

What BrowserRT should refuse:

- Pretending browser workers are equivalent to OS threads.
- Pretending cooperative JS tasks can be preempted safely.
- Scheduling only by worker availability instead of memory, storage, GPU,
  visibility, deadline, and UI budget.

BrowserRT stance: tasks, actors, and objects are three first-class runtime
entities.

## Service-worker/offline lineage

Representative sources: Service Worker API, Workbox.

What they get right:

- Deployment lifecycle and update semantics are hard.
- Offline/cached execution needs policy, versioning, and a recovery story.
- Service workers are a network/cache boundary, not a general compute worker.

What BrowserRT should steal:

- Versioned runtime install/update/rollback posture.
- A service-worker bridge for asset/runtime caching and offline boot.
- Explicit lifecycle states and upgrade receipts.

What BrowserRT should refuse:

- Treating service workers as the compute scheduler.
- Hiding upgrade races and stale-client problems.

BrowserRT stance: service workers are the boot/cache/network perimeter; dedicated
workers and shared workers run the compute kernel.

## Browser substrate API lineage

Representative sources: OPFS, WebGPU, WebCodecs, OffscreenCanvas, Streams,
Compression Streams, Long Tasks, Web Locks, BroadcastChannel, MessageChannel,
SharedWorker, Scheduler APIs.

What the substrate gets right:

- The browser already exposes enough primitives to build serious local systems.
- OPFS gives a performance-oriented origin-private storage surface.
- WebGPU provides GPU compute/render dispatch where supported.
- WebCodecs, OffscreenCanvas, and workers allow media/render work off the main
  thread.
- Streams already contain a native concept of backpressure.
- Web Locks and BroadcastChannel make same-origin cross-tab coordination viable.
- Long Tasks and performance observers give the runtime a UI-jank signal.

What BrowserRT should steal:

- One capability lattice that includes all of these APIs.
- Native stream backpressure semantics for pipeline channels.
- Mesh coordination using Web Locks plus BroadcastChannel plus SharedWorker when
  available.
- Long-task telemetry as a first-class health signal.
- Compression streams as an optional block-store transform, not a vendored
  dependency.

What BrowserRT should refuse:

- Assuming any single substrate API is present everywhere.
- Hiding quota, eviction, device loss, isolation, and browser support constraints.

BrowserRT stance: every substrate feature is a capability; every capability has
fallbacks and trace evidence.

## High-performance browser product lineage

Representative sources: Figma engineering posts, Photoshop-on-web discussions,
OffscreenCanvas case studies.

What they get right:

- Serious web apps often become a browser inside the browser.
- GPU rendering, Wasm, service-worker caching, full-browser integration tests,
  and tool-specific internal runtimes are practical, not fantasy.
- End-to-end browser tests catch bugs unit tests miss.

What BrowserRT should steal:

- Test in the real browser path whenever possible.
- Treat performance infrastructure as product infrastructure.
- Build demos that force full-stack runtime behavior, not isolated APIs.

What BrowserRT should refuse:

- Claiming real-device performance from cloudtainer-only tests.
- Baking a single app's assumptions into the general runtime.

BrowserRT stance: the cube can prove integration correctness; real-device
performance remains an explicit future validation lane.
