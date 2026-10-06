# BrowserRT steal-bank

This is the compact list of ideas to absorb. It is not a commitment to implement
all of them immediately. It is the ambition inventory for design pressure.

## S1: RPC facade, binary core

Borrow the ease of worker RPC, but keep hot-path payloads on a binary envelope
and explicit data-plane refs. The user-facing API may feel like calls; the kernel
must see envelopes, buffer ownership, task IDs, trace IDs, and resource hints.

## S2: Tasks, actors, objects

The core runtime model should have three primitives:

- `task`: stateless or bounded unit of work;
- `actor`: stateful worker/process with owned state and ordered methods;
- `object`: data-plane reference to transfer, shared memory, OPFS, stream, or
  GPU-resident data.

This steals from distributed runtimes without pretending a browser tab is a
cluster.

## S3: Capability lattice, not feature flags

Every runtime decision flows through capabilities. SAB, OPFS, GPU, worker
rendering, media, service-worker bridge, and cross-tab mesh are tiers and
requirements. They are not separate runtimes.

## S4: Explicit ownership and leases

Every data object has ownership state. A buffer can be owned, transferred,
shared, borrowed, GPU-resident, persistent, or released. Leaks and illegal access
are trace events, not vague bugs.

## S5: Backpressure is law

Every channel and pipeline edge declares capacity and overflow behavior. Native
streams can participate, but BrowserRT must also enforce backpressure for custom
queues, worker mailboxes, storage writes, GPU readbacks, and cross-tab messages.

## S6: Resource lanes

The scheduler sees lanes, not just workers:

- main;
- interactive;
- CPU;
- storage;
- GPU;
- render;
- media;
- network;
- cross-tab;
- maintenance.

A task declares desired lanes and fallback lanes. The scheduler admits it only if
budgets allow.

## S7: Calibration over guessing

Boot should measure message latency, transfer throughput, worker spawn cost,
OPFS throughput where available, GPU dispatch/readback where available, and
main-thread responsiveness. Defaults come from calibration, not static guesses.

## S8: Cooperative first, kill-box second

BrowserRT cannot truly preempt arbitrary JS. Cooperative yield checkpoints are
the default. Non-cooperative kernels run inside killable workers and are marked
as such.

## S9: Same-origin mesh

Multiple tabs should behave like a small same-origin runtime mesh:

- visible tab gets interactive priority;
- one tab or shared worker may coordinate storage maintenance;
- Web Locks protect exclusive jobs;
- BroadcastChannel propagates state changes;
- SharedWorker acts as a coordinator where supported.

This should be designed early even if implemented late.

## S10: Storage as a block kernel

BrowserRT storage starts as a log-structured block store with manifests,
journals, checksums, quota monitoring, temporary blocks, compaction, and crash
recovery. Databases, tables, media caches, and indexes live above it.

## S11: Service worker as boot perimeter

A service worker is not the compute kernel. It is the install/update/cache/offline
perimeter. BrowserRT should eventually ship a service-worker bridge that can
cache runtime assets, coordinate version upgrades, and report stale clients.

## S12: GPU as progressive lane

GPU compute and render paths are optional acceleration with pipeline caches,
buffer pools, fallback kernels, dispatch/readback telemetry, and device-loss
handling. No algorithm may be GPU-only unless the app explicitly requires it.

## S13: Observability as a product

Every serious primitive emits trace events. A devtools dashboard should show task
graphs, queues, workers, memory, storage, GPU dispatches, fallback decisions,
long tasks, and replay artifacts.

## S14: Runtime replay

A run should be recordable and partially replayable. Record task graph, message
envelopes, seeds, buffer hashes, block refs, capability profile, fallbacks,
worker crashes, and cancellation points. Exact determinism is not promised, but
replay should make failures small and discussable.

## S15: Plugin/process model

A future BrowserRT process declares permissions and resource limits. JS kernels,
Wasm kernels, and app plugins all go through the same capability, memory,
scheduler, and trace contracts.

## S16: Tradeoff docs are part of the API

Every advanced path needs a frank tradeoff page: SAB isolation costs, OPFS quota
risk, GPU support variance, service-worker update races, worker bridge latency,
visibility throttling, mobile constraints, and cloudtainer-only benchmark limits.
