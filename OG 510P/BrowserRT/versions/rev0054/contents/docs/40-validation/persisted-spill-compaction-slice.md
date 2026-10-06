# Persisted spill compaction slice

Revision: rev0036

Manifest task:

```txt
ipc:persisted-spill-compaction-proof
```

Command:

```bash
node tools/persisted_spill_compaction_probe.mjs --json artifacts/validation/REV0044-PERSISTED-SPILL-COMPACTION-PROBE.json
```

## What it proves

The slice creates a fake-provider `PersistedSpillMailbox` with delayed delete-on-ack. It enqueues five frames, including two frames with identical payload bytes to force content-addressed dedupe. It then delivers and acks two entries, leaves one pending, checkpoints, runs dry-run compaction, runs real compaction, recovers from the pre-compaction checkpoint plus post-checkpoint journal, drains recovered entries, and performs final compaction.

The proof checks:

- retained refs are captured in the checkpoint;
- dry-run compaction reports the one unique acked-only block;
- dry-run does not mutate provider state;
- real compaction deletes only the unreferenced unique acked block;
- a live duplicate payload prevents deletion of the shared digest;
- pending and ready entries survive compaction;
- compact-delete is journaled;
- recovery replays compact-delete;
- pending delivery is requeued after recovery;
- post-recovery drain preserves sequence and checksum expectations;
- final compaction deletes remaining unreferenced blocks;
- trace events are present.

## Why it belongs in release

This is release-tier because it is Node-only, fake-provider-only, deterministic, and fast. It adds semantic protection before any OPFS/provider spending.

## Non-claims

- No OPFS persisted-spill proof.
- No browser Worker persisted-spill proof.
- No fsync, flush, quota, eviction, or durability claim.
- No exactly-once delivery claim.
- No production retention, compaction, or garbage-collection algorithm claim.
- No throughput or latency claim.
