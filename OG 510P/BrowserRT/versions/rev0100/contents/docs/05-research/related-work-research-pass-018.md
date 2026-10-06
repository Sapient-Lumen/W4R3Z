# Related-work research pass 018 — persistent spill recovery and replayable queues

Revision: rev0028

This pass asks what BrowserRT should steal from systems that keep queued work meaningful across restarts without pretending that persistence is free or exactly-once.

## Sources consulted

No external code, data, or dependencies were imported. These are pattern sources only.

- Amazon SQS visibility timeout: delivered-but-not-deleted work becomes visible again after the timeout; useful pressure for pending redelivery without exactly-once claims.
- RabbitMQ consumer acknowledgements and durable queues: acknowledgement, requeue, and persistence semantics are explicit protocol surfaces, not comments.
- NATS JetStream streams: stream storage, retention limits, and consumers separate stored data from delivery state.
- Kafka retention and compaction: queues/logs need explicit retention policies; cleanup and compaction are not incidental implementation details.
- Redis Streams consumer groups: pending entries are a named state; delivered-but-not-acknowledged work can be inspected and later recovered or claimed.
- Logstash persistent queues: disk-backed queues use acknowledgements and replay unacknowledged events after abnormal termination; when the queue is full, backpressure is pushed to inputs.
- Browser Storage API and Storage Buckets: browser-local persistence is quota/eviction shaped; BrowserRT must not confuse fake-provider recovery with browser durability.
- Web Locks: same-origin storage-leader coordination is a future provider concern, not a rev0025 claim.
- Apache Pulsar negative acknowledgements and cursor state: replay/redelivery is part of the consumer protocol, not a surprising side effect.
- PostgreSQL/SQLite/RocksDB WAL vocabulary: write-ahead logs and checkpoints separate append, recover, replay, and compaction responsibilities.

## Stolen ideas

### Pending is not a bug

A delivered item that has not been acknowledged is a real state. BrowserRT should name that state, trace it, and test it. A future provider must decide whether pending work is requeued, claimed, timed out, or abandoned.

### Recovery is at-least-once unless earned otherwise

The baby recovery contract is at-least-once redelivery of unacknowledged deliveries. Exactly-once would require idempotence, dedupe keys, external side-effect discipline, or transaction coupling; none of that is earned here.

### Spill is a pressure valve plus recovery cost

A spill queue protects memory only if it has capacity, retention, acknowledgement, recovery, and cleanup policy. Otherwise it becomes hidden unbounded storage.

### Journal tails are normal failure surfaces

Recovery must know what to do with a torn or corrupt tail record. Rev0023 adopts the baby rule: replay valid records after the checkpoint and ignore the first invalid tail in non-strict mode.

### Cleanup must be explicit

Acked spilled payloads should not linger forever unless retention policy says so. The fake proof checks deletion after recovered drain, but this is not an OPFS durability claim.

## What enters rev0025

- `PersistedSpillMailbox` as a fake-provider persisted spill mailbox.
- `ipc:persisted-spill-recovery-proof` as a release-tier proof.
- `docs/20-architecture/persisted-spill-recovery-frontier.md`.
- `docs/40-validation/persisted-spill-recovery-slice.md`.
- A check-cube factor that stops browser artifact validation from secretly defeating the browser-light release posture.

## Non-claims

- No OPFS persisted spill provider.
- No browser restart or crash recovery proof.
- No fsync, flush, quota, or browser eviction claim.
- No exactly-once delivery claim.
- No multi-producer or multi-consumer proof.
- No throughput or latency claim.
