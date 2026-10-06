# Runtime dreambank 023 — the model-oracled provider kernel

Revision: rev0028  
Codename: Storage Lane Model Oracle

The dream: every BrowserRT provider family grows a cheap oracle before it grows an expensive implementation.

## Ambitious version

A future BrowserRT provider would ship with:

```txt
real provider
fake provider
snapshot validator
history recorder
reference model
model-walk generator
claim checker
counterexample minimizer
trace viewer
```

For example:

```txt
OPFS block store
  fake memory store
  journal/recovery model
  quota model
  crash/reload history checker
  compaction invariant checker
```

Or:

```txt
GPU lane
  fake GPU queue
  CPU reference kernel
  readback model
  device-loss model
  fallback routing checker
```

Or:

```txt
cross-tab mesh
  fake tab cluster
  Web Locks model
  BroadcastChannel delivery model
  leader-election checker
```

## Why this matters

BrowserRT is risky because it combines many browser substrates that are individually tricky. The cube cannot afford to discover all semantic bugs in expensive browser tests. The cheap oracle should find the embarrassing contract mistakes first.

## Rev0028 earned rung

Rev0028 adds a storage-lane model-walk proof. It checks the composition of:

```txt
CrossLaneScheduler + StorageLaneExecutor + PersistedSpillMailbox + MemoryBlockStore
```

against a small logical FIFO/pending/ack model under deterministic generated operations.

## Non-claims

- No formal verification.
- No exhaustive state-space search.
- No true concurrent interleaving proof.
- No OPFS model proof.
- No durability claim.
- No exactly-once delivery claim.
- No production scheduler claim.
