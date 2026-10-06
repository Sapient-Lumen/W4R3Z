# Storage-lane provider integration frontier

Revision: rev0028

This frontier describes the first provider-integrated storage-lane scheduling rung.

## Current earned shape

Rev0027 wires three existing surfaces together:

```txt
CrossLaneScheduler
  dispatches storage/maintenance tasks
StorageLaneExecutor
  executes the dispatched storage operation
PersistedSpillMailbox
  owns enqueue/dequeue/ack/checkpoint/compact semantics over a fake block provider
```

The proof is intentionally fake-provider and release-tier. It earns only the right to say BrowserRT can express storage work as scheduled lane work.

## Why this is the right next stair

Earlier scheduler proofs were purely fake tasks. Earlier persisted-spill proofs were direct mailbox calls. That was useful for isolating semantics, but future BrowserRT needs a boundary where the scheduler can actually drive provider operations.

The first boundary must stay tiny:

- scheduler health rejection before mailbox mutation;
- storage lane capacity blocking while a task is in flight;
- scheduled enqueue/dequeue/ack/checkpoint/snapshot operations;
- maintenance-lane compaction;
- dependency deferral for gated maintenance;
- live-ref-safe compaction;
- trace evidence across scheduler, storage lane, mailbox, and block store;
- no OPFS or durability claims.

## Provider integration law

```txt
Provider work must be scheduled, bounded, traced, and claim-gated.
```

If a future provider cannot explain lane, priority, capacity, health, dependency, and trace behavior, it should not enter BrowserRT as a runtime claim.

## What remains unearned

- No OPFS storage-lane provider proof.
- No browser Worker storage-lane provider proof.
- No fsync, flush, quota, eviction, or durability claim.
- No production storage scheduler claim.
- No work stealing or provider migration claim.
- No deadline, preemption, or priority-inheritance claim.
- No throughput or latency claim.
- No cross-browser conformance claim.
- No WebGPU proof.
