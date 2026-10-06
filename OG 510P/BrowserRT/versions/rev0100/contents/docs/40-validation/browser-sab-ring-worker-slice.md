# Browser SAB ring Worker slice

Revision: rev0028

## Manifest task

`browser:sab-ring-worker-proof`

## Purpose

Prove the same baby SPSC SharedArrayBuffer ring from the Node slice inside the
managed browser/CDP fixture, while keeping blocking waits off the browser main
thread.

This slice is intentionally **browser tier** rather than broad release tier by
default. The direct probe is still run during packaging, but it can be invoked
by id so expensive browser launches do not silently accumulate in every release
harness pass.

## What the slice does

1. Starts the shared one-shot browser fixture.
2. Serves a local page with COOP/COEP headers.
3. Temporarily relaxes Chromium managed URL policy when required and restores it.
4. Imports BrowserRT from the local server.
5. Boots BrowserRT with `browserSabRingWorkerProbe` and `sharedMemoryRingProbe`.
6. Allocates a fixed Int32 SharedArrayBuffer ring with BRT1 magic.
7. Prefills the ring and proves bounded full rejection.
8. Spawns `src/browser-sab-ring-worker.mjs` as a module Worker.
9. Posts the SharedArrayBuffer to the Worker and verifies it is not detached.
10. Produces the remaining values with async retry/backpressure on the page.
11. Consumes values in the Worker with `Atomics.wait` through `waitPop`.
12. Closes the ring and verifies wraparound, in-order receipt, sum, close, and
    trace evidence.

## Required artifact

`artifacts/validation/REV0044-BROWSER-SAB-RING-WORKER-PROBE.json`

The artifact must show:

- `crossOriginIsolated: true`;
- SharedArrayBuffer and Atomics constructors observed in page and Worker;
- module Worker ready event;
- shared object ref with `kind: "shared"`;
- SAB byte length unchanged after `postMessage`;
- full ring rejection before consumer starts;
- wraparound observed;
- 64 values pushed and popped;
- in-order receipt and matching sum;
- worker-only `Atomics.wait` path;
- policy restoration.

## Non-claims

- no MPSC or MPMC proof;
- no variable-length frame ring;
- no main-thread blocking wait;
- no `Atomics.waitAsync` proof;
- no SharedWorker, ServiceWorker, BroadcastChannel, Web Locks, or mesh proof;
- no WebAssembly shared-memory adapter;
- no latency or throughput claim;
- no cross-browser conformance.
