# Channel Surface Contract Kit — lane boundaries (2026-03-20)

**P-0529** is about the receiver-facing support contract for channels and message-passing surfaces.

It answers questions like:

- What kind of capacity surface does this channel expose?
- What happens when producers outrun consumers?
- What does a successful send actually mean?
- What history does a receiver get?
- What happens during close / drop / clean shutdown?

## It is not:

### Not `crate-resource-surface-pack-kit`
That lane is about queues/pools/caches/threads as resource surfaces and saturation evidence.
**P-0529** is narrower and more semantic: message visibility, overflow behavior, delivery meaning, and shutdown/drain truth for channels.

### Not `crate-lifecycle-surface-pack-kit`
That lane is about background work, stop verbs, shutdown phases, and aftermath truth.
**P-0529** is about the channel surface itself: what close, buffer drain, reserved capacity, and delivery semantics mean.

### Not `crate-observability-surface-pack-kit`
That lane is about signal route/delivery truth for telemetry.
**P-0529** is about application-facing message-passing primitives, even when they are not observability data.

### Not an actor framework
An actor framework can consume these receipts, but **P-0529** does not define supervision, mailbox scheduling, retries, or actor lifecycle policy.

### Not another channel crate
Tokio, futures, async-channel, crossbeam, flume, Embassy, and others already provide primitives.
**P-0529** publishes the support contract above them.

### Not a generic queue benchmark suite
Performance can be imported later, but the `0.1` problem is semantic honesty, not throughput ranking.
