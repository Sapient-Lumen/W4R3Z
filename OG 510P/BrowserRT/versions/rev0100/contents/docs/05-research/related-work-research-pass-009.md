# Related-work research pass 009 — shared-memory IPC, rings, and bounded mailboxes

Revision: rev0028

This pass aims at the memory/IPC lane. The question is not merely whether BrowserRT can allocate a `SharedArrayBuffer`; the question is what kind of mailbox discipline can survive future ambition without being redesigned.

## Sources researched

- MDN SharedArrayBuffer.
- MDN Atomics.wait.
- MDN Atomics.notify.
- LMAX Disruptor User Guide.
- Tokio bounded mpsc channel documentation.
- Crossbeam channel documentation.
- Emscripten pthreads support.
- Emscripten Wasm Workers API.
- WebAssembly threads proposal overview.
- V8 Atomics wait/notify/waitAsync feature note.

No source code was imported. This is a design-pressure pass only.

## What to steal

### 1. Sequenced rings, not vague queues

The LMAX Disruptor lesson is not "use this exact algorithm in JavaScript." The lesson is that a ring with explicit sequence counters, ownership, gating, and named consumers is easier to reason about than an opaque queue when low-latency exchange matters.

BrowserRT should eventually have several mailbox shapes:

- SPSC fixed-slot ring for one producer and one consumer.
- MPSC command ring for many producers into one lane owner.
- SPMC broadcast/cursor ring for trace consumers.
- Variable-frame ring for envelopes and compact telemetry.
- Bulk data refs outside the ring.

The rev0025 proof only claims the first rung: SPSC, fixed Int32 payloads, Node worker_threads.

### 2. Bounded channels are a correctness rule

Tokio and Crossbeam both reinforce the same pressure: bounded channels make capacity explicit. Unbounded mailboxes defer failure until memory or latency collapse. BrowserRT has already made boundedness a law in docs; rev0025 gives the shared-memory path a cheap proof.

The stolen rule: every BrowserRT queue must have one of these behaviors when full:

- wait;
- fail;
- drop by declared policy;
- spill to storage;
- lower fidelity;
- cancel upstream work.

The ring proof implements fail/try-push semantics and producer retry in the probe. It does not yet implement async reservation APIs, fairness, or producer parking.

### 3. Shared memory must remain capability-gated

SharedArrayBuffer is a higher-tier capability, not the baseline. In browsers, sharing requires cross-origin isolation. In Node/cloudtainer, the same primitive is useful for cheap algorithm proofs. BrowserRT should use Node proofs to design the data structure, then browser proofs to validate deployment constraints.

### 4. Atomics are a primitive, not an app API

`Atomics.wait` and `Atomics.notify` are low-level synchronization primitives. BrowserRT should not expose raw Atomics as its main app API. Instead, it should expose named mailbox providers and traceable behavior.

The future BrowserRT API should look like:

```ts
const inbox = rt.mailbox.create({
  shape: 'spsc-fixed-ring',
  capacity: 1024,
  payload: 'u32',
  overflow: 'wait',
  provider: 'sab-or-transfer'
})
```

Not like:

```ts
Atomics.wait(header, 3, x)
```

### 5. Wasm threads make this strategically important

Emscripten pthreads and the WebAssembly threads proposal both push toward shared memory plus atomics as the substrate for serious multithreaded Wasm. BrowserRT should design its object refs and mailboxes so a future Wasm kernel can plug into a ring without changing the control plane.

## What not to steal yet

- Do not import a dependency.
- Do not attempt an MPMC queue in the baby cube.
- Do not claim latency numbers.
- Do not block the browser main thread with `Atomics.wait`.
- Do not let SAB be required for BrowserRT baseline operation.
- Do not conflate ring payloads with large data; large data should remain object refs, blocks, streams, or shared slabs.

## New pressure added to the cube

BrowserRT now needs an explicit shared-memory ladder:

1. Node SPSC fixed Int32 ring proof. Current rev0025 slice.
2. Browser Worker SPSC fixed Int32 ring proof behind cross-origin isolation.
3. Variable-frame ring for small envelopes.
4. Transfer fallback with the same mailbox contract.
5. Shared slab object refs for bulk data.
6. MPSC command ring for lane owners.
7. Trace broadcast ring for devtools/replay.
8. Wasm memory adapter.

The important point is not the exact sequence. The important point is that shared-memory IPC must be designed as a family of provider contracts, not as a one-off clever queue.
