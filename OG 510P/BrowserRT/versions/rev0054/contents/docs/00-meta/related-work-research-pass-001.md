
# Related work research pass 001

This pass imports ideas, not dependencies. The source registry lives at
`artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json`. Raw external URLs are not
embedded because the cube remains cloudtainer-only and the validator forbids URL
drift.

## Research posture

BrowserRT should not copy one project. It should absorb patterns from several
families and then simplify them into one coherent browser runtime contract.

The working question for this pass was:

> What would BrowserRT become if it tried to be the one browser runtime substrate
> underneath serious local apps, while staying dependency-free inside ChatGPT
> cloudtainers?

## Families reviewed

### Worker RPC and worker pools

Examples: Comlink, Workerize, Greenlet-style function workers, threads.js,
workerpool, Piscina, Partytown.

What they get right:

- They make worker use approachable.
- They preserve main-thread responsiveness as a first-class goal.
- They prove that simple call shapes matter.
- Mature pools expose wait/run statistics, custom queues, cancellation, and
  resource limits.
- Partytown shows that proxying can be valuable when it protects the main
  thread, but also that proxy tradeoffs must be documented.

What BrowserRT should steal:

- A pleasant cold-path RPC layer.
- Worker prewarming and lifecycle hooks.
- Queue statistics and custom scheduling hooks.
- Cancellation and memory-limit discipline.
- A strong tradeoff page for proxied operations.

What BrowserRT should reject:

- Hiding serialization and copy costs.
- Treating workers as only remote functions.
- Allowing RPC objects to become the hot data path.

BrowserRT decision: expose an ergonomic RPC facade, but make the contract say it
is cold-path convenience. Hot paths use buffer refs, shared slabs, streams, OPFS
blocks, and GPU refs.

### Browser OS and Wasm runtimes

Examples: WebContainers, Browsix, Emscripten pthreads/Wasm workers, Pyodide.

What they get right:

- They prove the browser tab can host serious runtime abstractions.
- Browsix is especially useful as precedent: processes, pipes, signals, sockets,
  and a shared filesystem mapped onto web APIs.
- WebContainers shows the product power of making a browser runtime feel like a
  local development environment.
- Emscripten shows a practical bridge between POSIX-like expectations and the web
  via workers, SharedArrayBuffer, atomics, and virtual filesystems.
- Pyodide shows that language/runtime personalities can live above the browser
  substrate.

What BrowserRT should steal:

- Process-like lifecycle and supervision vocabulary.
- Pipes as bounded channels, not unbounded message streams.
- A shared object/block store as the center of data movement.
- Wasm kernel adapters as future plugin personality, not core dependency.
- Capability discovery before runtime promises.

What BrowserRT should reject:

- Becoming a full Unix clone.
- Becoming a full Node clone.
- Treating language/runtime personalities as the kernel.

BrowserRT decision: BrowserRT is a microkernel-ish substrate. Node, Python, SQL,
media, canvas, ML, and filesystem personalities are optional userland layers.

### Browser filesystems and storage

Examples: OPFS, BrowserFS, ZenFS, LightningFS, Emscripten file systems,
wa-sqlite OPFS discussions.

What they get right:

- Backend abstraction is useful.
- Node fs emulation is useful for portability.
- Narrow, fast storage layers can beat kitchen-sink filesystems.
- OPFS has enough low-level behavior to back serious local storage.
- Atomicity, manifests, journals, and concurrency must be designed rather than
  assumed.

What BrowserRT should steal:

- Storage backend interface with browser and Node test backends.
- Log-structured block store before high-level database semantics.
- Manifest swap and recovery receipts.
- A single-writer storage lane by default, with Web Locks/cross-tab election for
  future multi-tab storage leadership.
- Optional IndexedDB metadata/journal patterns if OPFS atomicity is not enough.

What BrowserRT should reject:

- Pretending OPFS is a normal user-visible filesystem.
- Pretending persistent browser storage can never be evicted or deleted.
- Allowing storage writes without crash-recovery semantics.

BrowserRT decision: build `RtBlockStore` first, not `fs` first and not database
first.

### Platform coordination and observability

Examples: Web Workers, transferables, SharedArrayBuffer, Web Locks,
BroadcastChannel, SharedWorker, scheduler.postTask/yield, Long Tasks API,
measureUserAgentSpecificMemory.

What they get right:

- The platform already contains coordination primitives that most apps ignore.
- Cross-tab coordination is possible enough to design for early.
- Long-task and memory surfaces can support runtime self-observation.
- Browser task priorities and yields exist, but are not universal enough to be
  assumed.

What BrowserRT should steal:

- Same-origin tab mesh using BroadcastChannel plus Web Locks.
- SharedWorker as a coordinator when available.
- Capability-tiered scheduler integration with postTask/yield.
- Long-task and memory telemetry as runtime health inputs.
- Feature-detected fallbacks for every one of these APIs.

What BrowserRT should reject:

- Assuming any single browser primitive is universal.
- Building mesh late as an incompatible afterthought.
- Treating observability as a demo overlay instead of kernel evidence.

BrowserRT decision: the runtime contract must assume multiple agents from day
one even if implementation starts with one page and dedicated workers.

### Accelerators, media, and rendering

Examples: WebGPU, ONNX Runtime Web, WebLLM, TensorFlow.js WebGPU backend, wgpu,
WebCodecs, OffscreenCanvas, AudioWorklet.

What they get right:

- Accelerator providers are chosen conditionally, not assumed.
- WebGPU can unlock serious local compute, but upload/readback costs matter.
- Browser-local AI shows the ambition ceiling for local compute.
- Media and rendering APIs have worker-capable surfaces that should be treated as
  lanes.
- AudioWorklet is a special low-latency universe and should not be scheduled like
  generic CPU work.

What BrowserRT should steal:

- Execution-provider model: choose CPU, Wasm, WebGPU, or other providers by task.
- Shader/pipeline/device caches with explicit fallback traces.
- Progress hooks for large model/kernel/resource loading.
- Readback-cost accounting.
- Distinct `gpu`, `render`, `media`, and `audio` lanes.

What BrowserRT should reject:

- GPU-only algorithms.
- Hiding accelerator fallbacks.
- Scheduling audio callbacks through a generic task queue.

BrowserRT decision: BrowserRT exposes accelerators as lanes and providers; it
never becomes a WebGPU-only runtime.

### Offline and service-worker stacks

Examples: Service Workers and Workbox.

What they get right:

- Offline/update behavior has lifecycle complexity that must be handled by
  policy, not vibes.
- Caching strategies are explicit names and contracts.
- Service workers are powerful, but their installation/update lifecycle can
  surprise applications.

What BrowserRT should steal:

- Named strategies and lifecycle receipts.
- Clear separation between application asset caching and runtime data storage.
- Service-worker bridge as an optional future boundary for network/offline
  features.

What BrowserRT should reject:

- Hiding service-worker updates behind magical defaults.
- Letting asset cache policy contaminate OPFS block-store policy.

BrowserRT decision: keep service workers out of the first kernel, but design the
mesh/protocol so a service-worker bridge can exist later.

### Actor and distributed runtime inspirations

Examples: Erlang/OTP, Akka, Tokio, Ray.

What they get right:

- Small primitives can scale if they are the right primitives.
- Supervision trees are a better failure model than scattered try/catch.
- Tasks, actors, and objects are a powerful triad.
- Work-stealing and resource-aware scheduling matter.
- A runtime becomes an ecosystem when tracing, timers, synchronization, and
  scheduling are part of the substrate.

What BrowserRT should steal:

- Supervision trees for workers/processes.
- Actor-like stateful agents for storage, GPU, mesh, and plugins.
- Task/object references instead of implicit giant return values.
- Resource requirements per task: CPU, memory, storage, GPU, deadline.
- Trace-first failure reports.

What BrowserRT should reject:

- Pretending browser tabs are datacenter nodes.
- Hiding browser throttling, quota, or isolation limits.
- Overbuilding distribution before single-origin correctness exists.

BrowserRT decision: define `task`, `agent`, `object-ref`, and `supervisor` early.
Implementation can remain tiny.

## Consolidated steals

1. Cold-path RPC, hot-path byte refs.
2. Worker pools with statistics, cancellation, custom queues, and limits.
3. Process/agent lifecycle and supervision.
4. Pipes as bounded channels.
5. Shared object/block store as data-plane center.
6. Backend/provider model for CPU, Wasm, GPU, storage, render, media, audio.
7. Storage journaling and manifest receipts.
8. Cross-tab mesh as future local cluster.
9. Observability as kernel evidence.
10. Runtime replay as debugging and cloudtainer collaboration tool.

## Anti-steals

These are the tempting ideas to avoid:

- Do not expose only a remote-function API.
- Do not emulate Unix or Node as the core product.
- Do not start with SQL, AI, canvas, or media personalities.
- Do not treat browser storage as permanent.
- Do not assume SharedArrayBuffer, WebGPU, scheduler APIs, or SharedWorker.
- Do not create five separate runtimes for five capability tiers.
- Do not let service-worker lifecycle leak into core storage semantics.
- Do not call a software-GPU cloudtainer smoke test a real-device benchmark.

## Immediate contract changes requested by this pass

- Add an explicit `task / agent / object-ref / supervisor` vocabulary.
- Add cold-path versus hot-path API doctrine.
- Add source-family registry to avoid rediscovering adjacent projects.
- Add one-to-rule ambition as a roadmap annex, while marking it non-claim.
- Expand open questions around service workers, actor supervision, and browser
  mesh failure modes.
