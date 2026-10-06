# SAB frame ring and binary mailbox frontier

Revision: rev0028.

## Current proof

`ipc:sab-frame-ring-proof` proves a single-producer / single-consumer SharedArrayBuffer ring for variable-size `Uint8Array` frames in Node worker_threads.

The proof uses:

- a fixed byte-capacity SharedArrayBuffer;
- an Int32 header;
- little-endian frame length and sequence fields;
- padded payload bytes;
- a wrap sentinel for reserved end-of-buffer gaps;
- `Atomics.wait` in the worker consumer;
- `Atomics.notify` on producer writes and close;
- explicit false return on oversize/full pushes;
- trace events for create, open, push, full, wrap, pop, consume-wrap, and close.

## Invariants

- Capacity is counted in bytes, not messages.
- Frames are copied into and out of the ring.
- A frame is accepted only if the payload plus header and any required wrap gap fit in remaining capacity.
- Oversize frames fail without mutating ring state.
- Full frames fail and increment full-hit evidence.
- Sequence numbers are payload metadata, not ring offsets.
- The consumer owns frame copying after pop.
- The ring closes by waking blocked consumers.

## Why not MPSC now?

MPSC/MPMC requires stronger claims: producer reservation, publication ordering, consumer gating, fairness, ABA avoidance, and deeper model tests. Rev0015 deliberately proves the byte-frame record format before adding producer contention.

## Why not browser Worker now?

The browser Worker fixed-ring proof already exists. The frame ring is cheap enough to harden in Node first. A browser Worker frame-ring proof can reuse the existing browser SAB fixture once the frame provider's invariants stop moving.

## Why not zero-copy schema now?

Cap'n Proto-like or FlatBuffers-like ambitions are seductive, but a schema view is a layer above transport. The current proof copies frames. A future schema provider can borrow frame payload memory under explicit lease rules only after memory ownership is stricter.

## Non-claims

- No MPSC/MPMC proof.
- No browser Worker frame-ring proof.
- No `Atomics.waitAsync` proof.
- No schema-zero-copy proof.
- No WebAssembly shared-memory proof.
- No OPFS spill mailbox proof.
- No throughput or latency claim.

## Rev0017 browser proof note

Revision: rev0028

The frontier now has a browser Worker variable-frame proof: `browser:sab-frame-ring-worker-proof`. The proof does not promote the frame ring to MPSC/MPMC or schema-zero-copy status. It only proves that the SPSC copied-frame provider can cross the browser page / module Worker boundary under cross-origin isolation while preserving frame ordering, lengths, checksums, wrap, close, and trace evidence.
