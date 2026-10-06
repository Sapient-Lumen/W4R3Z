# Test slice — storage-lane model walk

Task id: `scheduler:storage-lane-model-walk-proof`  
Revision introduced: rev0028

## Purpose

This slice exercises generated deterministic operation sequences against the storage-lane provider composition:

```txt
CrossLaneScheduler
  -> StorageLaneExecutor
      -> PersistedSpillMailbox
          -> MemoryBlockStore fake provider
```

It compares each step to a tiny logical model of ready deliveries, pending deliveries, acks, and payload checksums.

## Why this slice exists

The scripted provider proof is good but narrow. The model walk makes future refactors safer by running many small generated sequences cheaply in the release tier. It is designed to catch contract drift before OPFS/browser tests become necessary.

## Evidence required

The artifact must prove:

- deterministic replay matches;
- every generated step agrees with the logical model;
- every snapshot validates through `validateStorageLaneExecutorSnapshot`;
- health rejection does not mutate state;
- provider failure does not mutate logical delivery state;
- capacity blocking is observed;
- dependency deferral is observed;
- compaction does not mutate logical delivery state;
- final scheduler/mailbox accounting is empty;
- required trace events are present.

## Non-claims

- No OPFS storage-lane model proof.
- No browser Worker storage-lane proof.
- No durability, fsync, flush, quota, or eviction claim.
- No formal verification or exhaustive model checking.
- No true concurrent interleaving proof.
- No production scheduler claim.
- No throughput or latency claim.
- No exactly-once delivery claim.


Artifact: `artifacts/validation/REV0044-STORAGE-LANE-MODEL-WALK-PROBE.json`.

This is a release-tier, browser-light fake-provider model-walk proof.
