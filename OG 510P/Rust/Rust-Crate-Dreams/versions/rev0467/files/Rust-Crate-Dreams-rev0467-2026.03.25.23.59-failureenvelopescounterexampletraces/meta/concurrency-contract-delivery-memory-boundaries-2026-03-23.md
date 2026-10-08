# Concurrency Contract Kit delivery-memory boundaries — 2026-03-23

This note exists to keep the new delivery-memory / backlog-pressure slice of **P-0538** from dissolving into adjacent lanes.

## Keep these claims separate

### 1. Delivery memory is not wait cancellation
A waiter can lose queue place on cancellation while the surface still has strong memory semantics for already-sent values.
Conversely, a surface can be cancel-safe for a particular receive call and still retain only the latest value or one coalesced wake.

### 2. Delivery memory is not fairness
FIFO waiter ordering does not imply queued message retention, and latest-value semantics do not imply unfair scheduling.

### 3. Backlog pressure is not recovery posture
Poisoning / non-poisoning / panic recovery tell you what happens after failure, not what happens when producers outrun consumers.

### 4. Delivery memory is not driver-liveness
A surface may clearly say what it remembers and still require a runtime, local set, or explicit executor drive loop to make progress.

### 5. Delivery memory is not executor abstraction
This lane does not replace channel crates or runtime adapters.
It exports receiver-facing support reports over them.

## Adjacency guardrails

- If the main question is which runtime or executor to use, stay in runtime / abstraction / locality lanes.
- If the main question is whether cancellation consumes a value, stay in wait-cancellation first.
- If the main question is starvation or ordering, stay in fairness first.
- If the main question is queue/message retention and lag/drop/block behavior, this slice owns it.

## Doctor-rule direction

Future doctor checks should reject at least these false equivalences:

- “wake memory” == “message queue”
- “latest value visible” == “all values retained”
- “lagged error exists” == “no loss occurred”
- “unbounded” == “safe under pressure”
- “single-consumer delivery” == “broadcast fanout”
