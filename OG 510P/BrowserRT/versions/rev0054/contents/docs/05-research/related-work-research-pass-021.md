# Related work research pass 021 — retention, trimming, compaction

Revision: rev0028

This pass studies retention and compaction systems as design pressure for BrowserRT persisted spill mailboxes. The goal is not to copy a production queue. The goal is to steal the right nouns early so the fake-provider proof does not paint future OPFS/storage providers into a corner.

## Sources remembered

- Redis stream trimming: `XTRIM` separates retention by maximum length and minimum stream ID. BrowserRT should remember that retention can be count-like or sequence/time-like.
- Kafka cleanup policy: delete and compact are different mechanisms, and some systems combine them. BrowserRT should not blur "delete old entries" with "retain latest value per key" or "delete unreferenced payload blocks".
- NATS JetStream stream limits: stream retention is bounded by age, count, bytes, and discard behavior. BrowserRT should model admission/retention/compaction as connected pressure policies.
- RocksDB compaction: leveled, universal/tiered, and FIFO vocabulary warns that compaction is a provider strategy, not a universal primitive.
- Redis Streams and consumer groups: pending delivery state is not the same thing as retained log/storage state.

## Stolen ideas

- Retention is a policy boundary, not just a cleanup loop.
- Compaction must protect live references.
- Dry-run compaction belongs in the developer tool surface.
- Content-addressed dedupe makes live-ref protection subtle: an acked message and a live message may share one block.
- Compaction decisions need trace evidence.
- Compaction/recovery interaction needs a journal record or checkpoint boundary.
- Fake-provider compaction should be cheap and deterministic before OPFS spending.

## Ambitious dream

BrowserRT eventually has a provider-independent retention plane:

```txt
mailbox retains ready entries
pending deliveries are tracked separately
acks create tombstones or immediate deletes
retention policies choose what can be forgotten
compaction deletes only unreferenced payload/storage blocks
recovery replays compact-delete decisions
provider health and quota feed back into admission
```

The ambitious endpoint is a runtime where memory mailboxes, OPFS spill queues, stream providers, and cross-tab storage leaders can all ask the same questions:

```txt
What is live?
What is pending?
What is acked?
What may be compacted?
What must be retained for replay?
What can be safely deleted under pressure?
```

## Boundary

Rev0026 earns only a fake-provider retained-ref compaction proof. It does not earn OPFS durability, eviction behavior, quota behavior, exactly-once delivery, or a production compaction algorithm.
