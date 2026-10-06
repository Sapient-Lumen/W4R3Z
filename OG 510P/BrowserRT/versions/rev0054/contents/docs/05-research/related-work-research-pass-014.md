# Related-work research pass 014 — spill queues, watermarks, retention, and pressure propagation

Revision: rev0028

## Question

BrowserRT now has fixed-cell SAB rings, variable-frame SAB rings, browser Worker frame-ring proof, fake block stores, and journal/manifest recovery. The next transport question is: **what should a bounded mailbox do when memory pressure says “no more”?**

The tempting answer is “spill to storage.” This pass treats spill as a design frontier, not a magic answer.

## Sources inspected

- Akka Streams: bounded buffer space is a defining property of its stream model.
- Apache Flink: back pressure propagates upstream when downstream operators cannot consume fast enough.
- Logstash persistent queues: events can be stored on disk with checkpointing and replay semantics.
- Netty `WriteBufferWaterMark`: high and low water marks flip writability instead of letting outbound buffers grow without limit.
- Kafka topic cleanup policy: old log segments can be deleted or compacted depending on retention policy.
- Grafana Loki WAL: replay can apply backpressure/memory ceilings when a WAL is too large for memory recovery.
- FoundationDB transaction-log spilling design material: persistent-state spill changes need versioning and upgrade/rollback care.

## Stolen ideas

### 1. Spill is a pressure valve, not extra RAM

A spill mailbox must not turn “bounded memory” into “unbounded storage.” It needs explicit high/low watermarks, quota handling, rejection semantics, retention policy, and trace events.

### 2. Backpressure must propagate

If a spill provider is slow, full, unavailable, or recovering, the producer must learn that fact. The runtime should be able to choose wait, reject, drop, degrade, or cancel; silent queue growth is not allowed.

### 3. Acknowledgement is part of the storage contract

Persistent queues and WAL-shaped systems make clear that enqueue, delivery, acknowledgement, replay, and retention are separate states. BrowserRT should not pretend that “read from spill” means “safe to delete” until a consumer ack happens.

### 4. Watermarks are better than booleans

A mailbox should eventually expose snapshots such as:

```txt
memory bytes used
spill bytes used
queued frames
pending frames
high watermark crossed
low watermark crossed
provider health
oldest pending age
```

This lets a scheduler reason about pressure rather than simply observing a failed enqueue.

### 5. Retention is a first-class policy

Kafka-style delete/compact vocabulary is useful even for a tiny BrowserRT mailbox. BrowserRT will eventually need decisions for acked frames, expired frames, duplicate/coalescible frames, and crash-recovered frames.

## Ambition

The “one runtime” version has a transport ladder:

```txt
clone mailbox
transfer mailbox
SAB fixed-cell mailbox
SAB framed mailbox
SAB framed mailbox with OPFS spill
persistent/replayable mailbox
mesh mailbox across tabs
network transport mailbox
```

Spill mailboxes become the bridge between IPC, storage, scheduling, and replay. They are also a natural place for quota-aware admission control.

## Tempering boundary

rev0025 deliberately implements only a fake-provider spill mailbox proof. It does not claim OPFS durability, browser crash recovery, multi-tab coordination, or throughput. The point is to freeze semantics cheaply before paying browser/CDP/OPFS test cost.
