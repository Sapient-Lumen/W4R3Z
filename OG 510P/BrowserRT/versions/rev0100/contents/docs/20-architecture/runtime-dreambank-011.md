# Runtime dreambank 011 — framed binary mailboxes

Revision: rev0028.

## Dream

BrowserRT eventually has a mailbox provider family that can move tiny commands, large binary records, streams, frame batches, trace packets, plugin messages, and OPFS spill handles without collapsing everything into JSON objects.

The provider ladder now looks like this:

```txt
clone-mailbox
transfer-mailbox
sab-spsc-int32-node
sab-spsc-int32-browser-worker
sab-spsc-frame-node
sab-spsc-frame-browser-worker
sab-spsc-frame-batch
sab-mpsc-command
opfs-spill-mailbox
mesh-mailbox
schema-view-mailbox
```

Rev0015 implements only `sab-spsc-frame-node`.

## Primitive vocabulary

A frame is not a schema object. A frame is a transport record:

```txt
length:int32
sequence:int32
payload:bytes
padding:0..3 bytes
```

A wrap sentinel is also a transport record:

```txt
length = -1
reserved gap to end of ring
```

That means BrowserRT can reason about byte capacity, reserved bytes, backpressure, close, and sequence order before choosing any schema system.

## Why this matters

Fixed `Int32` rings are useful for counters, commands, and smoke tests. Real BrowserRT data-plane messages need bytes: encoded envelopes, small binary manifests, hashes, trace batches, compressed blocks, GPU dispatch descriptors, or control packets. Variable frames are the bridge between toy rings and serious mailbox providers.

## Future provider dreams

- A browser Worker version of the frame ring.
- Batched frame reads to reduce per-frame overhead.
- A frame decoder with mutation corpus tests.
- OPFS spill frames when byte capacity stays full.
- A schema-view provider that can expose frame bytes as typed structures without copying.
- A WebAssembly shared-memory provider using offsets and lengths.
- A mesh provider that turns frames into cross-tab messages through a coordinator.

## Tempering rule

Every future mailbox provider must state:

- producer count;
- consumer count;
- ordering guarantee;
- ownership model;
- frame/object lifetime;
- overflow behavior;
- trace events;
- proof artifact;
- non-claims.

Rev0015 stays intentionally small: SPSC, copied frames, Node worker_threads, no performance claim.
