# Forkwatch and witness receipts

`forkwatch.py` is the rev0009 answer to the mutability problem: a reader must not treat a signed mutable record as automatically latest enough. The DHT can validate signatures and still be a hostile place for fresh state.

## Failure modes modeled

| Failure | Example | Current response |
|---|---|---|
| Stale replica | Node returns sequence 2 after the client has seen sequence 3 | `STALE_VALID`, optional rollback witness receipt |
| Same-sequence fork | Publisher signs two different values at sequence 7 | `SAME_SEQ_FORK`, receipt includes both record hashes |
| Invalid signature | Store returns a mutated value or fake signature | `INVALID_SIGNATURE`, do not advance local memory |
| Expired record | Replica returns a record past TTL | `EXPIRED_RECORD`, do not advance local memory |
| Target mismatch | Record is presented under the wrong target | `TARGET_MISMATCH`, do not advance local memory |

## Local memory, not consensus

The `MutableHeadMemory` object keeps:

```text
highest_seq_by_target
best_hash_by_target
versions_by_target_seq
fork evidence
observations
witness receipts
```

This is private memory. It is not a global ledger. A garden node can share receipts, but the receiver should treat them as evidence from that witness, not as final truth.

## Receipt shape

A `WitnessReceipt` signs:

```text
witness public key
witness node id
claim kind
target
subject mutable public key
salt
highest sequence observed
observed sequence
record hashes
issued/expires
note
```

Receipt kinds:

```text
highest_seen
rollback_seen
same_seq_fork_seen
invalid_record_seen
stale_replica_seen
```

The most important receipt is same-sequence fork evidence. A rollback can be caused by lag. A fork means a signer or signing environment produced conflicting history at the same sequence. That should become sticky local evidence.

## Deep guess

Garden nodes should be good witnesses because they observe many paths and many replicas. But they should not become “truth servers.” The guardrail remains:

```text
witnessing is evidence preservation, not authority
```

## What tests now cover

- A valid lower-sequence record after a higher sequence becomes `STALE_VALID` and produces a rollback receipt.
- Two signed records at the same sequence with different values produce `SAME_SEQ_FORK` and a receipt containing both hashes.
- Tampered signatures do not advance local highest-seen memory.
- The fake chaos harness emits receipts for stale and forked lookup replies.

## Open pressure

The next hard step is adversarial path isolation: receipts should record not only a source node but a lookup path family. A fork seen through three disjoint paths is a different kind of evidence than a fork seen through one captured garden.
