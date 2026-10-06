# Fake block-store testing slice

Revision: rev0028

## Manifest id

`storage:fake-block-store-proof`

## Why this slice exists

BrowserRT storage work is about to get expensive. OPFS, sync handles, browser restarts, quota, Web Locks, and multi-tab behavior all cost more than a Node process. This slice creates a cheap storage proof that future provider implementations must match.

## What it proves

The slice runs `tools/fake_block_store_probe.mjs` and writes `artifacts/validation/REV0044-FAKE-BLOCK-STORE-PROBE.json`.

It proves:

- content-addressed block refs are created from SHA-256 digests;
- duplicate bytes map to the same ref;
- read-after-write works in the fake provider;
- a deterministic command walk matches a simple in-memory model;
- checksum verification catches intentionally corrupted bytes; this is the current corruption detection proof;
- injected provider write failure is observable;
- operation kinds and trace event kinds are recorded.

## What it intentionally does not prove

- OPFS persistence.
- OPFS sync-handle correctness.
- Browser storage durability.
- Quota pressure behavior.
- Journal/manifest recovery.
- Crash recovery.
- Multi-tab safety.
- Real performance.

## Why fake-provider evidence matters

The fake provider is the place to make storage invariants cheap. The browser provider should then prove that the same contract survives real browser APIs. This prevents future storage slices from becoming one giant OPFS integration blob.
