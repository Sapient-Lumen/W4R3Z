# Browser OPFS sync Worker slice

Revision: rev0028

## Manifest id

`browser:opfs-sync-worker-proof`

## Purpose

Prove one narrow claim: inside the managed cloudtainer Chromium/CDP fixture, a
dedicated browser module Worker can use OPFS `createSyncAccessHandle` to perform
a synchronous write/read/flush/close path off the main thread.

## What it proves

- The shared browser fixture can serve a page and Worker module with COOP/COEP.
- BrowserRT can boot inside the page.
- A transferable payload object ref detaches the sender-side `ArrayBuffer`.
- A dedicated module Worker can access OPFS.
- The Worker can call `createSyncAccessHandle` on an OPFS file handle.
- The handle exposes read, write, truncate, flush, getSize, and close methods.
- The Worker can write bytes, flush, read them back, and report equal bytes.
- The page can record an OPFS sync object ref and trace events.
- The harness restores temporary Chromium policy changes and tears down.

## What it does not prove

- No cross-browser conformance.
- No production durability.
- No journaled block-store correctness.
- No crash recovery.
- No quota-pressure behavior.
- No multi-tab coordination.
- No performance benchmark.
- No claim that sync handle is always available on every browser/device.

## Command

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-sync-worker-proof --jobs 1
```

## Artifact

`artifacts/validation/REV0044-BROWSER-OPFS-SYNC-WORKER-PROBE.json`

The artifact should contain:

- `status: passed`;
- `observations.page.crossOriginIsolated: true`;
- sender-side detachment evidence;
- sync access handle method evidence;
- equal bytes written/read;
- OPFS object ref backend `opfs-sync-access-handle`;
- policy restoration evidence;
- per-phase timing.

## Test economics

This is a medium browser-process test. It should stay separate from async OPFS,
SAB, WebGPU, and block-store recovery tests. If it flakes, quarantine is allowed
only as an explicit risk ledger entry with a reproduction command and exit
criterion.

Required phrase for audit: sender-side `ArrayBuffer` detachment.
