# SAB ring and shared-memory frontier

Revision: rev0028

## Current rung

SPSC means single producer / single consumer. The current proofs are deliberately SPSC only.

`ipc:sab-ring-proof` proves a tiny fixed-slot `SharedArrayBuffer` ring in Node `worker_threads`.

`browser:sab-ring-worker-proof` proves the same baby provider shape inside the managed browser/CDP fixture with a dedicated module Worker.

Together they prove:

- BRT1 magic header;
- Int32 fixed-size payloads;
- single producer;
- single consumer;
- bounded full rejection;
- producer retry/backpressure evidence;
- consumer-side blocking `Atomics.wait` through `waitPop` off the browser main thread;
- producer `Atomics.notify` on push;
- SharedArrayBuffer stays shared rather than transferred/detached in the browser proof;
- wraparound evidence;
- close semantics;
- trace events.

## Why this belongs now

BrowserRT's control/data-plane split eventually needs a faster IPC path than structured clone. But SAB is too easy to misuse. The cube needs cheap testable toys before the real mailbox family grows.

## Provider ladder

1. `clone-channel`: baseline correctness, not hot path.
2. `transfer-channel`: one-owner buffers for bulk one-shot data.
3. `sab-spsc-fixed-node`: rev0025 Node proof, fixed Int32 payload.
4. `sab-spsc-fixed-browser-worker`: rev0025 browser Worker SAB ring proof, fixed Int32 payload.
5. `sab-spsc-frame`: variable-size binary envelopes.
6. `sab-mpsc-command`: many producers into a lane owner.
7. `sab-trace-broadcast`: multiple devtools/replay consumers with cursors.
8. `wasm-shared-memory`: raw offset/length ABI for Wasm kernels.
9. `mesh-mailbox`: same-origin multi-tab coordination adapter.

## Invariants to keep

- Ring capacity is fixed after allocation.
- Ring close wakes waiters.
- Full rings do not silently overwrite unread data.
- Bulk bytes do not ride in the control ring.
- Browser main thread never uses blocking `Atomics.wait`.
- Browser SAB proofs require `crossOriginIsolated: true`.
- Every fallback is traced.
- Every provider has a manifest test.

## Non-claims

- No MPSC proof.
- No MPMC proof.
- No variable-frame envelope ring.
- No waitAsync proof.
- No Wasm shared-memory proof.
- No SharedWorker, ServiceWorker, BroadcastChannel, Web Locks, or mesh proof.
- No throughput or latency claim.

## Rev0015 frame-ring extension

The fixed `SharedInt32Ring` remains the smallest mailbox proof. Rev0015 adds `SharedFrameRing`, a separate SPSC byte-frame provider. Keeping them separate is intentional: fixed cells prove cheap command/counter movement, while variable frames prove binary data-plane movement with byte-capacity backpressure and wrap sentinels.

The new provider still inherits the same non-claims: no MPSC, no MPMC, no public latency claim, and no browser Worker frame proof yet.
