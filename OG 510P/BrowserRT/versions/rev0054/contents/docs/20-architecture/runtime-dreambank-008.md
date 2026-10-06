# Runtime dreambank 008 — recovery as a browser kernel service

Revision: rev0028

## Absurd ambition

BrowserRT eventually becomes the place where browser apps ask:

```txt
what state did this provider accept?
what journal records are safe to replay?
what checkpoint is authoritative?
what tail is torn or corrupt?
what maintenance lane should compact this later?
what trace proves the recovery decision?
```

That is a storage kernel, not a key-value helper.

## Tiny current proof

`storage:journal-recovery-proof` proves only a fake in-memory provider. It creates journal records, checkpoints a manifest, recovers from an old and latest checkpoint, ignores a torn/corrupt tail, rejects a corrupt manifest checksum, and emits recovery trace events.

## Dream primitives

- `journal record`: accepted operation plus checksum and sequence.
- `manifest checkpoint`: compact provider state at a sequence.
- `replay cursor`: last checkpoint sequence plus applied journal seqs.
- `recovery reconciler`: provider-specific routine that decides what to apply, ignore, or reject.
- `maintenance lane`: future checkpoint/compaction work scheduled away from interactions.
- `recovery trace`: event or span evidence for every decision.

## Non-claims

- No durable browser storage yet.
- No OPFS crash consistency.
- No fsync/flush semantics.
- No quota or eviction proof.
- No compaction proof.
- No multi-tab recovery leader.
