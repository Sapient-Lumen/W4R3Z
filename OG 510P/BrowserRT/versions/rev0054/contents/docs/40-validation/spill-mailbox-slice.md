# Validation slice — fake-provider spill mailbox

Revision: rev0028
Manifest id: `ipc:spill-mailbox-fake-proof`

## Purpose

Prove the first cheap semantics for a spill-aware mailbox before spending browser/CDP/OPFS budget.

## Command

```bash
node tools/spill_mailbox_probe.mjs --json artifacts/validation/REV0044-SPILL-MAILBOX-PROBE.json
```

## What it proves

- a fake memory block-store provider can act as the cold spill tier;
- frames enqueue to memory until the memory budget is exhausted;
- later frames spill to the provider;
- dequeue preserves FIFO order across memory and spill tiers;
- payload lengths and checksums are preserved;
- ack deletes spilled blocks;
- oversize frames are rejected;
- provider quota failures are surfaced as spill rejection;
- pending frames can be reclaimed and redelivered;
- trace events cover enqueue, spill write, dequeue, ack, reject, reclaim, and block-store operations.

## What it does not prove

- OPFS provider behavior;
- browser Worker behavior;
- durable crash recovery;
- multi-producer or multi-consumer safety;
- throughput or latency;
- cross-browser behavior.

## Why this is release-tier

This slice is Node-only, deterministic, and cheap. It belongs in release tier because it protects semantics without launching Chromium.
