
# Ambition frontier: one runtime to rule local browser software

This is a dream surface, not an implementation claim. Its job is to preserve the
shape of the ridiculous version while the implementation stays tiny.

## North-star sentence

BrowserRT becomes the origin-local userspace kernel for serious browser apps:
processes, agents, tasks, object refs, memory, storage, GPU, render, media,
audio, network, mesh, telemetry, replay, and devtools under one capability-aware
runtime.

## The one-to-rule architecture

```text
Application personalities
  data apps | IDEs | editors | media | ML | games | scientific tools
        ↓
BrowserRT userland adapters
  rpc | pipelines | actors | plugins | fs facade | provider adapters
        ↓
BrowserRT kernel contract
  tasks | agents | object refs | supervisors | lanes | backpressure | trace
        ↓
BrowserRT data plane
  transfer buffers | shared slabs | OPFS blocks | streams | GPU buffers | frames
        ↓
Browser platform
  workers | OPFS | SAB/Atomics | WebGPU | WebCodecs | OffscreenCanvas |
  AudioWorklet | Web Locks | BroadcastChannel | Service Worker
```

## Wild but coherent capabilities

### 1. Origin-local process table

Every worker, plugin, storage leader, GPU manager, and cross-tab coordinator is
an agent with lifecycle, owner, permissions, resource budget, trace ID, and
supervisor.

Tiny proof: a worker agent can crash, restart, and emit a lifecycle trace.

### 2. Browser object store

All large data becomes an object ref. The object may be in memory, shared memory,
OPFS, GPU memory, stream, or media frame form. Applications can ask for a view,
but the runtime owns movement and fallback evidence.

Tiny proof: a task returns a transferable-buffer object ref and a second task
consumes it without structured-cloning the payload.

### 3. Capability lattice boot

At boot, BrowserRT measures and records capability tiers: basic, workered,
isolated, persistent, accelerated, mesh. It also calibrates message cost, worker
spawn cost, storage throughput, and optional GPU dispatch/readback cost.

Tiny proof: boot report records feature presence plus one transfer benchmark.

### 4. Runtime mesh

Same-origin tabs become a small cluster. Visible tabs get interaction priority;
hidden tabs can contribute maintenance or compute only under explicit policy;
Web Locks prevent duplicate compaction/storage leadership.

Tiny proof: two tabs elect a storage leader and emit a mesh trace.

### 5. Kernel devtools

BrowserRT ships a devtools page that shows lanes, queues, workers, object refs,
storage usage, fallback events, long tasks, and memory probes.

Tiny proof: Jank Guillotine demo records task and queue events.

### 6. Replay and failure packets

A runtime failure can be exported as a compact trace packet: capability profile,
task graph, envelope log, buffer hashes, storage receipts, and crash records.
This is ideal for cloudtainer iteration because the next revision can carry the
failure packet.

Tiny proof: a cancelled task produces a replayable trace skeleton.

### 7. Plugin/process model

A plugin declares permissions and limits before it can run. BrowserRT grants only
specific lanes and object refs. This is not a browser security boundary; it is an
internal capability discipline.

Tiny proof: a plugin worker can only call registered kernels and cannot access an
ungranted object ref.

### 8. Provider marketplace without dependency lock-in

Providers implement one interface for CPU JS, Wasm, WebGPU, media, render, audio,
or future accelerators. BrowserRT chooses by capability, cost, and policy.

Tiny proof: one kernel runs through CPU provider; an optional WebGPU provider is
selected only if boot capability and calibration allow it.

## Tempering principles

- The absurd version must compile down to tiny executable proofs.
- Every dream feature must be an optional lane/provider/personality, not core
  bloat.
- The core kernel must remain understandable in one sitting.
- The cube must never accumulate surfaces faster than validation can protect.
- Performance claims require trace evidence and must name the environment.

## First tiny proof sequence

1. Boot report.
2. Trace log.
3. Bounded channel.
4. One worker agent.
5. Transferable object ref.
6. Supervisor restart of worker agent.
7. Jank Guillotine trace.
8. Browser smoke harness.
9. OPFS block-store stub.
10. Mesh leader-election stub.

When those are stable, the dream can grow without becoming slop.
