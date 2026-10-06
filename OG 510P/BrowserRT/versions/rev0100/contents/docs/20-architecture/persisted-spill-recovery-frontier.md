# Persisted spill recovery frontier

Revision: rev0031

`PersistedSpillMailbox` is the first recovery-shaped spill primitive. It is intentionally fake-provider-first.

## What it is

A mailbox that records payloads in a block-store provider and records queue metadata in an append-only journal.

The current proof covers:

- enqueue to provider-backed spill storage;
- delivery into a pending entries state;
- ack tombstones;
- checkpoint manifest checksums;
- replay of post-checkpoint records;
- torn-tail ignore in non-strict mode;
- corrupt manifest rejection;
- at-least-once redelivery of unacked pending entries;
- ack deletion of recovered blocks;
- trace evidence.

## Recovery ladder

This is a recovery ladder, not a durability claim:

```txt
fake metadata journal
  -> fake model-walk recovery
  -> filesystem provider
  -> OPFS async provider
  -> OPFS sync worker provider
  -> multi-tab storage leader
  -> retained-ref retention/compaction (rev0026 fake-provider proof)
  -> provider-integrated storage-lane scheduling
```

## At-least-once means at-least-once

Pending entries after recovery may be delivered again. That is correct for this proof. Exactly-once requires more machinery than this cube has earned.

## Design pressure for future providers

Future providers must define:

- whether ack deletes payload blocks immediately;
- whether retention keeps acked payloads;
- how much journal tail can be replayed under memory pressure;
- whether pending entries are redelivered, claimed, or timed out;
- how provider quota affects recovery;
- how corrupted or missing payload blocks are reported;
- which trace events prove each decision.

## Non-claims

- No OPFS durability claim.
- No browser Worker persisted spill proof.
- No fsync/flush guarantee.
- No quota or eviction behavior.
- No exactly-once delivery claim.
- No multi-producer or multi-consumer proof.
- No throughput or latency evidence.


## Rev0026 retention/compaction update

Rev0026 adds a separate frontier doc for retained-ref compaction. Recovery and compaction now interact through `compact-delete` journal records; this keeps retained-ref accounting coherent when recovering from a checkpoint before compaction plus a post-checkpoint journal tail.
