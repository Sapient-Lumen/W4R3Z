# Frame-stream transport frontier

Revision: rev0028

BrowserRT now has enough mailbox evidence to name a frontier: frame-stream transport.

## Current evidence ladder

```txt
ipc:sab-ring-proof                 -> Node fixed Int32 SPSC ring
browser:sab-ring-worker-proof      -> browser Worker fixed Int32 SPSC ring
ipc:sab-frame-ring-proof           -> Node variable-frame SPSC ring
ipc:sab-frame-model-proof          -> deterministic model oracle for variable-frame ring
browser:sab-frame-ring-worker-proof -> browser Worker variable-frame SPSC ring
```

This is not a finished transport layer. It is a proof ladder.

## Provider contract pressure

Every future frame provider should answer:

- What is one frame?
- Who owns the frame bytes before and after send?
- What happens when capacity is exhausted?
- Does rejection mutate state?
- How does close drain pending data?
- Where may blocking waits happen?
- Which trace events prove send, receive, wait, wake, wrap, close, and error?
- What is the fake provider or model oracle?

## Browser-specific rule

Blocking `Atomics.wait` must stay off the browser main thread. BrowserRT can use it in dedicated Workers, but the page/control plane should only observe non-blocking control results, snapshots, or async promises.

## Flow-control dream

Borrow the stream/backpressure idea, but keep BrowserRT's lower-level realities visible:

```txt
Readable/Writable interface for apps
bounded SAB/transfer/OPFS providers underneath
trace events and snapshots for the scheduler
```

The runtime should be able to say: storage is slow, the frame stream is filling, upstream parser must slow, and render lane keeps priority.

## Current non-claims

- No MPSC or MPMC frame mailbox proof.
- No variable-frame browser throughput or latency claim.
- No zero-copy schema overlay proof.
- No OPFS spill mailbox.
- No WebTransport provider.
- No cross-tab mesh transport.
- No cross-browser conformance.
