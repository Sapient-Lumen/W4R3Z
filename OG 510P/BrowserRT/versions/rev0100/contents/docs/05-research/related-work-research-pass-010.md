# Related-work research pass 010 — browser shared-memory mailboxes

Revision: rev0028

## Research seam

This pass keeps pushing BrowserRT toward a browser userspace kernel, but narrows
one frontier: the shared-memory mailbox should work in the actual browser Worker
fixture, not only in Node `worker_threads`.

The useful related-work pressure comes from five families.

1. SharedArrayBuffer and Atomics define the browser primitive boundary. Shared
   memory is capability-gated by cross-origin isolation, `SharedArrayBuffer` is
   shared rather than transferred, and blocking waits belong off the browser main
   thread.
2. LMAX Disruptor-style rings suggest that the ring itself is only one part of
   the design; sequence counters, gating, and consumer progress are the real
   contract surfaces.
3. Aeron-style messaging suggests that BrowserRT should distinguish app
   messages, transport buffers, flow control, backpressure, and publication /
   subscription state rather than mixing them into one opaque queue.
4. Reactive Streams reinforces that backpressure should be contractual and
   observable, not a hidden side effect.
5. Cloudflare Durable Objects and similar coordination systems keep suggesting
   one future shape: a named coordination object owns ordering and state, while
   callers interact through references and messages.

## Steals for BrowserRT

- Treat every mailbox provider as a resource with explicit capacity, ownership,
  blocking policy, trace events, and fallback path.
- Keep the data plane byte-oriented. A shared-memory ring transports fixed cells
  or frames; it does not transport arbitrary JS object graphs.
- Keep the control plane small. Worker spawn, ready, call, result, close, and
  failure are still envelopes and traces.
- Record sequence/wraparound evidence. A single message is not a ring proof.
- Preserve the "no main-thread blocking waits" rule. `Atomics.wait` is acceptable
  inside the dedicated Worker proof; it is not a BrowserRT UI-thread primitive.
- Keep same-origin coordination dreams separate from shared-memory proof. A
  browser Worker SAB ring is not a BroadcastChannel, SharedWorker, or Web Locks
  mesh.

## Ambitious dream

BrowserRT eventually has a mailbox provider registry:

```txt
clone-mailbox                 baseline object messages
transfer-mailbox              one-owner ArrayBuffer payloads
sab-spsc-int32                baby fixed cell ring
sab-spsc-frame                framed binary records
sab-mpsc-command              multiple producers, one owner/consumer
sab-trace-broadcast           trace fanout without object churn
stream-mailbox                Web Streams backpressure adapter
opfs-spill-mailbox            bounded queue that spills data-plane refs
wasm-shared-memory-mailbox    Wasm linear-memory adapter
mesh-mailbox                  same-origin multi-tab coordination adapter
```

Every provider should advertise the same contract vocabulary: capacity,
blocking semantics, fairness assumptions, object-ref shape, cancellation policy,
trace kinds, and non-claims.

## What rev0025 proves

Rev0014 adds `browser:sab-ring-worker-proof`. It is intentionally narrow:

- local managed Chromium/CDP fixture;
- cross-origin isolated page;
- module Worker spawn;
- SharedArrayBuffer posted to the Worker without detaching;
- fixed Int32 SPSC ring;
- main-thread producer uses nonblocking `tryPush` plus async retry;
- Worker consumer uses `Atomics.wait` through `waitPop`;
- wraparound, close, in-order receipt, sum, and trace evidence.

## What it still does not prove

- no MPSC or MPMC mailbox;
- no variable-length frame ring;
- no `Atomics.waitAsync` path;
- no SharedWorker, ServiceWorker, BroadcastChannel, Web Locks, or mesh proof;
- no WebAssembly shared-memory adapter;
- no latency or throughput benchmark;
- no cross-browser conformance.
