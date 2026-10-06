# Validation slice — ipc:sab-frame-ring-proof

Revision: rev0028.

## Purpose

Add a cheap, release-tier, Node worker_threads proof that BrowserRT can move variable-size binary frames through a bounded SharedArrayBuffer mailbox.

## Command

```bash
node tools/sab_frame_ring_probe.mjs --json artifacts/validation/REV0044-SAB-FRAME-RING-PROBE.json
```

Or through the manifest runner:

```bash
node tools/run_tests.mjs --tier release --id ipc:sab-frame-ring-proof --jobs 1
```

## Evidence required

The artifact must show:

- `SharedArrayBuffer` and `Atomics` available;
- variable payload lengths observed;
- oversize frame rejection;
- bounded full rejection before consumer start;
- producer backpressure/retry after consumer starts;
- wraparound observed through wrap sentinels;
- reserved gap bytes observed;
- all frames received;
- sequence numbers in order;
- length and checksum agreement;
- total byte and combined checksum agreement;
- ring closed;
- zero pending bytes;
- worker pop count matches push count;
- required trace event kinds present.

## Why this belongs in release

Unlike browser/CDP slices, this proof does not launch Chromium. It exercises a core IPC invariant cheaply inside Node and creates a reusable provider surface for future browser, OPFS spill, and model-test work.

## Non-claims

This slice is not a browser Worker frame proof, not MPSC/MPMC, not zero-copy schema transport, not `waitAsync`, not WebAssembly shared memory, and not a performance benchmark.

## Rev0017 relationship to browser frame proof

Revision: rev0028

The Node-side `ipc:sab-frame-ring-proof` remains the cheap release-tier provider proof. The browser-side `browser:sab-frame-ring-worker-proof` is a separate browser/full-tier slice because Chromium/CDP launch and teardown cost must stay visible.
