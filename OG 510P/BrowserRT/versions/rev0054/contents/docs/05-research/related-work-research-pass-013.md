# Related-work research pass 013: streams, flow control, and browser frame mailboxes

Revision: rev0028

This pass asks what BrowserRT becomes if its in-memory mailboxes are not just queues, but the first rung of a general transport substrate. The new concrete slice is still tiny: a browser Worker consumes variable-size frames from a SharedArrayBuffer SPSC ring. The ambition behind it is larger: BrowserRT should eventually express streams, datagrams, object refs, worker mailboxes, OPFS spill, and network transport with one shared flow-control vocabulary.

## Sources inspected

No external source code is imported into the cube. These are research inspirations recorded as source families only.

- WHATWG Streams: `pipeTo()` is a backpressure-preserving shape; BrowserRT should steal the idea that flow control is part of the pipe contract, not a side flag.
- MDN Streams API: readable, writable, and transform streams are the web-native vocabulary app authors already know.
- WebTransport API: reliable bidirectional streams and unreliable datagrams are a useful mental model for multiple provider shapes under one transport umbrella.
- QUIC RFC 9000: flow-controlled streams and multiplexing suggest future per-mailbox and per-runtime credits.
- Netty EventLoop and ChannelPipeline: separate event loops, channels, handlers, and pipeline stages are a useful model for BrowserRT lanes and providers.
- Reactor Netty: backpressure-ready network engines reinforce that runtime I/O should match consumer demand.
- Aeron flow control: the producer should learn that the receiver is slow without unbounded buffering.
- Cap'n Proto framing/schema pressure: BrowserRT should keep frame transport separate from schema/RPC views so future zero-copy schema overlays do not rewrite the ring.

## Stolen ideas

### 1. Treat mailboxes as transports

A mailbox is not merely `send(message)`. It is a transport with:

```txt
capacity
credits
frame boundaries
close semantics
error propagation
trace events
provider-specific ownership rules
```

The new `browser:sab-frame-ring-worker-proof` makes this explicit for a browser Worker variable-frame ring.

### 2. Separate stream semantics from provider mechanics

The app-facing contract should eventually look like a stream of frames or objects. The provider might be:

```txt
structured clone
transferable ArrayBuffer
SharedArrayBuffer fixed-cell ring
SharedArrayBuffer frame ring
OPFS spill mailbox
WebTransport stream
mesh mailbox
```

The stream contract should remain stable while providers change.

### 3. Per-stream and per-runtime flow control

QUIC's distinction between per-stream and connection-level flow control maps nicely onto BrowserRT:

```txt
mailbox capacity = per-stream limit
runtime memory budget = connection-level limit
```

This could prevent one busy provider from starving storage, render, or interactive lanes.

### 4. Frame proof before schema proof

Cap'n Proto and related binary-schema systems make zero-copy schema views tempting. BrowserRT should resist that until frame boundaries, backpressure, wrap, close, and browser Worker sharing are proven. The cube now has Node variable-frame, model-walk, and browser Worker variable-frame proofs as prerequisites for any schema-overlay dream.

## Ambition unlocked

BrowserRT could eventually expose a `FrameStreamProvider` family:

```ts
type FrameStreamProvider = {
  open(): FrameStream
  trySend(frame): boolean
  receive(): Frame | null
  close(): void
  snapshot(): FlowSnapshot
}
```

That provider could back worker mailboxes, actor messages, object-ref pipes, OPFS spill queues, media chunk transport, and WebTransport-like network edges.

## Tempering rule

The new proof is still one browser, one Worker, one SPSC copied-frame ring, and one cloudtainer. It is not a throughput claim, a latency claim, a cross-browser result, a schema-zero-copy proof, MPSC/MPMC, OPFS spill, or mesh transport. The dream grows only because the proof surface stays narrow.
