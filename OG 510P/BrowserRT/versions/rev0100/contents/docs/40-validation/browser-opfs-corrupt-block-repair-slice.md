# Browser OPFS corrupt block repair slice — rev0062

Current revision: rev0062.

## Purpose

`browser:opfs-corrupt-block-repair-proof` closes a correctness hole left by the restart, quota-pressure, and storage-lane backpressure proofs: a content-addressed block store must not treat a final hash-path filename as proof that the bytes behind the file are valid.

Before this slice, duplicate detection in `OpfsAsyncBlockStore.put()` was filename-first. If a crash, failed write, manual corruption, or browser implementation edge left a corrupt file at the expected hash path, a later `put()` of the correct payload could have deduped against the corrupt file and returned success while `get()` failed checksum validation later.

Rev0061 changes that behavior. The async OPFS provider now verifies existing final-hash files before dedupe, treats `has()` as “valid block exists” rather than “some file exists,” fails `get()` closed on checksum mismatch, deletes corrupt final-hash files during a subsequent `put()` of the correct payload, rewrites the block, and records the repair in trace/stats.

## Evidence required

- deliberately inject a corrupt `.blk` file at the exact final content-addressed OPFS path for a known payload
- prove `has(ref)` returns `false` for the corrupt file
- prove `verify(ref)` reports `present: true`, `ok: false`, and the corrupt actual digest
- prove `get(ref)` fails closed with `BRT_OPFS_BLOCK_CHECKSUM_MISMATCH`
- prove `put(payload)` does not accept filename-only dedupe and instead reports `repairedCorrupt: true`
- prove the repaired block reads/checksums/verifies successfully
- prove a second `put(payload)` dedupes only after valid-content verification
- prove delete/cleanup removes the repaired namespace

## Runtime changes

`src/opfs-block-store.mjs` now includes:

- verified duplicate detection before content-addressed dedupe
- verified `has()` semantics by default
- post-write verification by default
- corrupt final-hash repair on `put()` by default
- explicit `storage:opfs-block-corrupt`, `storage:opfs-block-repair`, `storage:opfs-block-write-close`, and `storage:opfs-block-integrity-ok` traces
- stats for `integrityChecks`, `corruptBlocksDetected`, `corruptDeletes`, `corruptRepairs`, `postWriteVerifications`, and exclusive-writer fallbacks

## Non-claims

- This is Chromium-in-cloudtainer evidence only, not cross-browser OPFS conformance.
- Deliberate corrupt-file injection is not organic crash, power-loss, quota-eviction, storage-pressure, or filesystem-fault evidence.
- Verification and repair do not prove fsync durability, persistent-storage retention, Storage Buckets behavior, multi-tab coordination, throughput, latency, capacity, or production durability.
- `createWritable({ mode: "exclusive" })` narrows same-file writer contention where supported, but this slice does not prove full multi-tab or multi-worker coordination; Web Locks/storage-lane coordination remains a separate surface.
- Browser-heavy proof remains explicit browser/full tier only; broad release remains browser-light.

## Commands

```bash
node tools/run_tests.mjs --tier release --id opfs:block-store-corrupt-block-repair-proof --jobs 1 --json artifacts/validation/REV0062-OPFS-CORRUPT-BLOCK-REPAIR-RUN.json
node tools/run_tests.mjs --tier browser --id browser:opfs-corrupt-block-repair-proof --jobs 1 --json artifacts/validation/REV0062-BROWSER-OPFS-CORRUPT-BLOCK-REPAIR-RUN.json
node tools/run_tests.mjs --tier browser --id browser:opfs-corrupt-block-repair-proof,browser:opfs-lane-quota-backpressure-proof,browser:opfs-quota-pressure-proof --jobs 1
```
