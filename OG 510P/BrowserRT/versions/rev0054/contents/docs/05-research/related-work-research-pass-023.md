# Related-work research pass 023 — model-oracled provider integration

Revision: rev0028  
Codename: Storage Lane Model Oracle

This pass treats BrowserRT less like a pile of probes and more like a runtime whose provider integrations need **model-oracled evidence** before they become expensive browser/OPFS/WebGPU surfaces.

## What we are stealing

### Deterministic simulation discipline

FoundationDB's simulation story keeps pushing the same lesson: make the fake world deterministic, replayable, and harsh before trusting real I/O. BrowserRT should keep using cheap fake providers for storage, scheduling, admission, and mailbox contracts before spending browser/OPFS budget.

Steal:

- seeded model walks;
- fake providers before real providers;
- artifact histories;
- replayable summaries;
- evidence that is cheap enough to run every release.

Non-steal:

- no claim that BrowserRT has FoundationDB-scale simulation;
- no claim that a single-threaded model walk proves browser correctness.

### Embedded model checking and state exploration

Stateright is useful inspiration because it frames system behavior as states and transitions, especially for actor-like systems. BrowserRT has emerging actors, schedulers, storage providers, and mailboxes. The shape we want is not a full formal model today; it is a habit: every provider-family proof should ask what a tiny reference model can say.

Steal:

- explicit state-transition vocabulary;
- state snapshots;
- small model surfaces near provider code;
- transition traces future sessions can inspect.

### History checkers and claims discipline

Porcupine and Jepsen/Elle are useful because they separate **a claim** from **a history** and then ask whether the history is legal under that claim. BrowserRT should eventually have history-style claim checkers for delivery semantics, scheduler accounting, memory ownership, and provider recovery.

Steal:

- executable sequential specifications;
- histories as first-class artifacts;
- visualizable counterexample thinking;
- claim-specific checkers instead of vague “passed tests.”

Non-steal:

- no linearizability proof in rev0028;
- no transactional isolation proof;
- no distributed-system checker embedded in the cube yet.

## BrowserRT interpretation

The new target shape is:

```txt
provider implementation
  + snapshot validator
  + generated command walk
  + tiny reference model
  + trace event requirements
  + non-claim charter
  + manifest task
  + audit task
```

The rev0028 concrete version is the storage-lane composition:

```txt
CrossLaneScheduler
  -> StorageLaneExecutor
      -> PersistedSpillMailbox
          -> fake MemoryBlockStore
```

The model does not simulate every block digest or journal entry. It verifies the logical delivery contract across generated enqueue, dequeue, ack, checkpoint, compact, health, provider-failure, capacity, and dependency-deferral operations.

## Why this belongs before OPFS

OPFS integration will be expensive and occasionally fragile in the cloudtainer. A fake-provider model walk gives us a cheap semantic office:

- what is supposed to happen when provider health fails;
- what a scheduler rejection may mutate;
- what compaction may not mutate;
- what final accounting must look like;
- which traces make the run explainable.

Only after that contract stabilizes should OPFS storage-lane work begin.
