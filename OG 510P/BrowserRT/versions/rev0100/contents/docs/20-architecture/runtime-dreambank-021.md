# Runtime dreambank 021 — retention as a runtime plane

Revision: rev0028

BrowserRT should not treat retention as storage trivia. Retention is part of the runtime contract because it sits between admission control, mailboxes, block stores, recovery, quota, and future browser storage providers.

## Dream primitive

```ts
const mailbox = rt.persistedSpillMailbox({ deleteBlockOnAck: false })

const dryRun = await mailbox.compact({ dryRun: true, reason: 'quota-preflight' })

const result = await mailbox.compact({ reason: 'maintenance-lane' })
```

But the true future primitive is larger:

```txt
RetentionPolicy
  maxReadyFrames
  maxReadyBytes
  minSequenceToKeep
  protectPending
  protectLiveRefs
  deleteAckedPayloads
  compactJournalRecords
  emitTraceEvidence
```

## Why this matters

A browser runtime must handle constrained storage. OPFS and browser quota pressure will eventually force decisions: wait, reject, drop, compact, spill, or degrade. Those decisions should not be ad hoc.

## Provider ladder

```txt
fake retained-ref compaction
  -> fake retention policy model walk
  -> Node filesystem provider
  -> OPFS async provider
  -> OPFS sync worker provider
  -> cross-tab storage leader with Web Locks
  -> quota-pressure/eviction-aware maintenance lane
```

## Important invariant

Do not delete live content-addressed payload blocks. A block is live if any ready or pending entry still references its digest. This is true even if an acked entry shares the same digest.

## Rev0026 earned stair

Rev0026 adds `PersistedSpillMailbox.compact()` with:

- dry-run candidate enumeration;
- live digest protection;
- retained-ref tracking in checkpoints;
- compact-delete journal records;
- replay of compact-delete during recovery;
- trace evidence;
- fake-provider proof artifact.

## Non-claims

- No OPFS persisted-spill proof.
- No browser Worker persisted-spill proof.
- No fsync, flush, quota, eviction, or durability claim.
- No production retention, compaction, or garbage-collection algorithm claim.
- No exactly-once delivery claim.
- No throughput or latency claim.
