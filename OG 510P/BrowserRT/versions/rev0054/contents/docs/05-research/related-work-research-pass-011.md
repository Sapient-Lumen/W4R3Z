# Related work research pass 011 — binary framed mailboxes

Revision: rev0028.

## Question

BrowserRT already has fixed-`Int32` SharedArrayBuffer rings in Node and browser Worker contexts. The next research question is whether the mailbox vocabulary should grow toward variable-size binary frames before touching MPSC/MPMC, browser frame rings, OPFS spill mailboxes, or schema-aware zero-copy transport.

## Sources consulted

This pass researched Cap'n Proto encoding/serialization, Reactive Streams, Aeron flow control, LMAX Disruptor sequencing, Hypothesis stateful testing, PropEr, ClusterFuzz/AFL-style fuzzing, and PlusCal/TLA+ model-checking pressure. The source registry records domains and takeaways without embedding external URLs in the cube.

## Ideas stolen

### Frame before schema

Cap'n Proto is a useful warning, not an implementation dependency. It pushes the imagination toward buffer-backed access and low-copy schema views, but BrowserRT should not jump straight to schema/RPC transport. The first primitive should be a tiny binary frame: length, sequence, payload bytes, and explicit wrap handling.

### Offer failure is backpressure

Aeron-style `offer` failure and Reactive Streams backpressure both reinforce the same rule: a producer must observe capacity pressure at the protocol boundary. For BrowserRT that means `tryPushFrame()` returning false is not a nuisance; it is the visible backpressure event.

### Sequences survive ambition

The Disruptor vocabulary of rings, sequences, and gating remains valuable. Rev0015 does not implement multi-consumer gating, but the sequence number in each frame is the first baby step toward a transport that can eventually support replay, loss detection, and ordered trace reconstruction.

### Stateful tests should arrive early

Hypothesis and PropEr strengthen a testing direction: once mailboxes have push, pop, close, wrap, overflow, and corruption states, hand-picked examples are insufficient. The next facility growth should include tiny state-machine tests and deterministic model walks for mailbox providers.

### Fuzzing belongs outside release at first

Coverage-guided fuzzing and AFL-style corpus mutation are tempting for binary frame readers. BrowserRT should not add expensive fuzzing to release gates, but it should design the frame parser so a future local corpus test can mutate lengths, sentinels, sequence numbers, and truncated records.

### Tiny models before MPSC

PlusCal/TLA+ pressure says: do not build MPSC/MPMC from vibes. A small mailbox model can define producer/consumer offsets, reserved wrap gaps, close state, and backpressure before the implementation expands.

## Cube effect

Rev0015 adds `ipc:sab-frame-ring-proof`, a Node worker_threads SPSC SharedArrayBuffer variable-frame ring proof. It proves variable payload lengths, oversize rejection, bounded-full rejection, producer retry/backpressure, wrap sentinel handling, ordered delivery, checksum and length agreement, close, and trace events.

## Non-steals

No external code is imported. No Cap'n Proto, FlatBuffers, Aeron, Reactive Streams, Hypothesis, AFL, or TLA+ dependency enters the cube. These are design pressure sources only.
