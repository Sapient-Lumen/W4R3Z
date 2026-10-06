# Persisted spill recovery slice

Revision: rev0036

Manifest task:

```txt
ipc:persisted-spill-recovery-proof
```

Command:

```bash
node tools/persisted_spill_recovery_probe.mjs --json artifacts/validation/REV0044-PERSISTED-SPILL-RECOVERY-PROBE.json
```

## What it proves

The slice creates a fake provider-backed `PersistedSpillMailbox`, enqueues twelve frames, checkpoints with ready and pending entries, applies a post-checkpoint journal tail, appends a torn tail record, recovers, drains the recovered queue, and verifies:

- checkpoint captured queue and pending entries;
- post-checkpoint journal records replay;
- torn tail is ignored;
- corrupt manifest is rejected;
- pending entries are requeued for at-least-once redelivery;
- acked messages are not redelivered;
- FIFO order after recovery is the expected order;
- payload checksums match;
- ack deleted recovered blocks;
- trace events are present.

## Why it belongs in release

This is a cheap Node-only proof in the release tier. It is intentionally browser-light and does not launch Chromium. It lets future OPFS work inherit recovery semantics rather than discovering them inside expensive browser fixtures.

## Non-claims

- No OPFS provider proof.
- No browser Worker persisted spill proof.
- No fsync, flush, quota, eviction, or crash durability claim.
- No exactly-once delivery claim.
- No multi-producer or multi-consumer proof.
- No throughput or latency claim.

## Release-tier economics

This slice is release tier because it is browser-light, Node-only, fake-provider-only, and observed to run in well under one second in the cloudtainer. It is intentionally cheap enough to run before any OPFS or browser persisted-spill work.


## Rev0026 carry-forward

The recovery proof remains release-tier and is now paired with `ipc:persisted-spill-compaction-proof`. Recovery is still fake-provider-only and still at-least-once for pending entries.
