# Validation slice: `browser:sab-frame-ring-worker-proof`

Revision: rev0028

This slice proves the first browser Worker variable-frame SharedArrayBuffer mailbox path.

## Command

```bash
node tools/browser_sab_frame_ring_worker_probe.mjs --json artifacts/validation/REV0044-BROWSER-SAB-FRAME-RING-WORKER-PROBE.json
```

## What it proves

The probe uses the shared managed browser/CDP fixture. It starts a local HTTP server with cross-origin-isolation headers, temporarily relaxes Chromium's managed URL policy if needed, launches Chromium, attaches CDP, imports BrowserRT, and runs a page-local proof.

The proof checks:

- the page is `crossOriginIsolated`;
- `SharedArrayBuffer` and `Atomics` are available;
- a module Worker can import the frame-ring provider;
- posting a `SharedArrayBuffer` to the Worker does not detach it from the sender;
- variable frame lengths are generated and consumed;
- oversize frames reject cleanly;
- bounded full rejection is observed before the consumer starts;
- producer backpressure/retry behavior is observed;
- the Worker consumes with `Atomics.wait`;
- the producer wakes via `Atomics.notify`;
- wrap sentinels and reserved gap bytes are observed;
- all 72 frames arrive in sequence;
- lengths, checksums, total bytes, and combined checksum match;
- close drains cleanly;
- trace events exist for create/open/full/wrap/spawn/ready/call/close/result/terminate;
- Chromium policy is restored and the process group is torn down.

## Why it is separate from release tier

Browser launch slices are expensive and can fail for cloudtainer reasons unrelated to frame-ring semantics. This slice is browser/full tier. Packaging runs the direct probe to create a named artifact, but broad release remains narrower.

## Non-claims

- No MPSC or MPMC frame mailbox proof.
- No `Atomics.wait` on the browser main thread.
- No `Atomics.waitAsync` proof.
- No zero-copy schema-view proof.
- No WebAssembly shared-memory proof.
- No OPFS spill mailbox proof.
- No WebTransport or mesh provider proof.
- No throughput or latency claim.
- No cross-browser conformance claim.
