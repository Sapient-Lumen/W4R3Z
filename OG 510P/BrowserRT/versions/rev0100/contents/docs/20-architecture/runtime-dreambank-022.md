# Runtime dreambank 022 — provider-integrated storage lanes

Revision: rev0028

BrowserRT's scheduler work and persisted-spill work now touch. The dreambank update is simple but important:

```txt
A lane is not useful until it can drive a provider.
A provider is not safe until its work is scheduled, bounded, traced, and claim-gated.
```

## New runtime noun

```txt
StorageLaneExecutor
```

This is not a production storage scheduler. It is a small composition surface that lets a `CrossLaneScheduler` dispatch operations against a `PersistedSpillMailbox`:

```txt
enqueue payload
  -> scheduler task on storage lane
  -> mailbox.enqueue
  -> journal/persisted-spill trace
  -> scheduler complete

dequeue payload
  -> scheduler task on storage lane
  -> mailbox.dequeue
  -> pending delivery
  -> scheduler complete

ack payload
  -> scheduler task on storage lane
  -> mailbox.ack
  -> no exactly-once claim
  -> scheduler complete

compact/checkpoint
  -> scheduled maintenance/storage work
  -> trace evidence
  -> no durability claim
```

## Why this matters

Before rev0028, scheduler proofs and persisted-spill proofs were adjacent but not integrated. Rev0027 takes the first earned step toward a runtime where lanes actually govern providers.

Future BrowserRT should make these decisions visible:

- Is a storage operation user-blocking or maintenance?
- Is the storage lane healthy?
- Is a provider error severe enough to mark the lane unhealthy?
- Did a dependency gate hold compaction until a prior delivery or ack completed?
- Did capacity prevent dispatch while work was in flight?
- Did compaction protect live refs?
- Did a proof overclaim OPFS, durability, performance, or exactly-once semantics?

## Ambitious extension ladder

```txt
fake storage-lane executor
  -> fake provider model walks
  -> storage-lane admission policy
  -> provider health/retry policy
  -> OPFS provider skeleton
  -> browser Worker storage lane
  -> cross-tab storage leader
  -> replayable storage-lane histories
  -> eventually, pluggable provider placement
```

## Boundary

Rev0027 proves composition, not production. It does not add OPFS, browser storage, work stealing, real contention, throughput, latency, or durability claims.
