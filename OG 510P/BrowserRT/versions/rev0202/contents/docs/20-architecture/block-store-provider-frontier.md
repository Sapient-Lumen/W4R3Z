# Block store provider frontier

Revision: rev0028

## Boundary

BrowserRT's block store is a substrate, not a database. It owns bytes and verifiable references. Higher-level libraries own tables, indexes, documents, media timelines, and user semantics.

## Provider ladder

```txt
memory-fake
  -> node-fs-fake-or-real
  -> opfs-async
  -> opfs-sync-worker
  -> opfs-sync-handle-pool
  -> mesh-coordinated-opfs
```

Every rung needs a separate test slice.

## Provider contract

A provider must expose explicit behavior:

- read-after-write within one provider instance;
- whether writes are atomic;
- whether list is authoritative;
- whether blocks are immutable;
- whether deletion is supported;
- whether it can corrupt or partially write in tests;
- whether it reports quota/usage;
- whether it can recover after restart.

Rev0011 only proves the fake provider's in-process read-after-write and verification behavior.

## Why content addressing first

Content addressing lets BrowserRT dedupe, verify, replay, and compare without inventing higher-level semantics too early. It also lets the test facility reuse artifacts by digest later.

## Why fake provider first

Browser OPFS tests are expensive in the cloudtainer. A fake provider is cheap and deterministic. It lets the cube test storage invariants, corruption detection, model walks, and failure handling before paying for browser fixture launches.

## Future slices

1. `storage:fake-block-store-proof` — current rev0025 slice.
2. `storage:node-fs-block-store-proof` — same contract with temporary filesystem backend.
3. `browser:opfs-block-store-async-proof` — OPFS async provider using the same contract.
4. `browser:opfs-block-store-sync-worker-proof` — worker-owned sync handle provider.
5. `storage:journal-manifest-fake-proof` — journal and manifest in fake provider.
6. `browser:opfs-journal-recovery-proof` — browser restart/reopen recovery.
7. `browser:opfs-quota-pressure-proof` — quota and failure envelope.
8. `mesh:storage-leader-lock-proof` — Web Locks coordination.

## Non-claims

- No current durability proof.
- No crash recovery proof.
- No compaction proof.
- No OPFS block-store proof.
- No quota pressure proof.
- No multi-tab proof.
