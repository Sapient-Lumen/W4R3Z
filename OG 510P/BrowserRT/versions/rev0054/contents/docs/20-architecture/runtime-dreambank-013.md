# Runtime dreambank 013: BrowserRT as a frame-stream transport kernel

Revision: rev0028

The one-runtime dream now has a transport layer shape. BrowserRT should be able to coordinate data moving between agents without every subsystem inventing its own queue, stream, buffer pool, backpressure flag, close rule, and trace schema.

## The future noun: frame stream

A frame stream is a bounded sequence of byte frames plus control events:

```txt
open
trySend(frame)
receive(frame)
credit/update
close
abort
snapshot
trace
```

The first implementation family is tiny:

```txt
sab-spsc-frame-node
sab-spsc-frame-model
sab-spsc-frame-browser-worker
```

The new slice adds the third rung: `browser:sab-frame-ring-worker-proof`.

## Provider ladder

BrowserRT should preserve one app-level transport contract across providers:

```txt
clone-frame-stream            // easiest correctness baseline
transfer-frame-stream         // one-owner ArrayBuffer movement
sab-spsc-int32                // fixed cells, cheap proof
sab-spsc-frame-node           // variable-size frames in Node worker_threads
sab-spsc-frame-browser-worker // variable-size frames in browser Worker
opfs-spill-frame-stream       // bounded memory with disk spill
webtransport-frame-stream     // network-facing transport
mesh-frame-stream             // cross-tab/cross-agent route
schema-view-frame-stream      // future typed binary views
```

Each provider must declare ownership rules, blocking rules, close behavior, trace events, and non-claims.

## Flow-control shape

A provider should eventually surface at least these values:

```ts
type FlowSnapshot = {
  usedBytes: number
  freeBytes: number
  framesSent: number
  framesReceived: number
  credits?: number
  closed: boolean
  provider: string
}
```

The runtime scheduler can use these snapshots to choose between waiting, spilling, dropping, lowering quality, or canceling upstream work.

## Why this matters

Storage, media, rendering, local databases, vector search, code indexing, and plugin sandboxes all need to move bytes between agents. BrowserRT should not let each lane choose incompatible semantics. A single frame-stream vocabulary gives the runtime a shared way to reason about pressure and failure.

## New proof boundary

The current browser proof says:

```txt
browser page + module Worker + SharedArrayBuffer frame ring + Atomics.wait in Worker + Atomics.notify from producer + variable payloads + wrap sentinel + close
```

It does not say:

```txt
MPSC/MPMC
zero-copy schema view
waitAsync
OPFS spill
WebTransport
cross-browser conformance
performance
```

## Dream features that now have a path

- Object refs sent as framed control messages.
- Bulk bytes sent as framed data messages.
- OPFS spill when a memory mailbox is full.
- Stream adapters to WHATWG `ReadableStream` / `WritableStream`.
- Credit propagation from render/media/storage consumers back to CPU producers.
- Trace projections that show pressure flowing backward through a pipeline.
