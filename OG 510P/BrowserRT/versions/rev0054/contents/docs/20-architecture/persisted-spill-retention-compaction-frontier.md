# Persisted spill retention/compaction frontier

Revision: rev0031

`PersistedSpillMailbox` now has a fake-provider retention/compaction stair.

## The problem

A persisted spill mailbox can accumulate blocks even after messages are delivered and acked. Immediate deletion is not always the right policy: future providers may need replay windows, audit retention, dedupe windows, or delayed cleanup under quota pressure. But delayed deletion must not become hidden leakage.

## Current model

Rev0026 tracks retained payload refs separately from ready and pending live refs.

```txt
ready queue refs      -> live
pending delivery refs -> live
acked-only refs       -> compactable if no live entry shares the digest
```

Compaction is conservative:

1. compute live block digests from ready and pending entries;
2. enumerate retained refs not in the live set;
3. dry-run can report candidates without mutation;
4. real compaction deletes candidates from the provider;
5. real compaction writes `compact-delete` journal records;
6. recovery replays `compact-delete` records so retained-ref accounting stays coherent.

## Why content-addressing is tricky

Two messages may share one payload block. If one message is acked and another remains ready or pending, the shared block must not be deleted. Rev0026's proof includes this case.

## Future questions

- Should retention be count-based, byte-based, age-based, sequence-based, or provider-health-based?
- Should the maintenance lane choose compaction when quota is high, or should admission reject first?
- Should compact-delete records be batched?
- Should provider manifests be trusted, or should retained refs be the only source of compaction candidates?
- How should missing compacted blocks be reported during recovery?
- What is the smallest OPFS proof that does not imply durability it has not earned?

## Non-claims

- No OPFS persisted-spill proof.
- No browser Worker persisted-spill proof.
- No production retention/compaction/garbage-collection algorithm claim.
- No fsync, flush, quota, eviction, or durability claim.
- No exactly-once delivery claim.
- No multi-producer or multi-consumer proof.
- No throughput or latency claim.
