# Test slice — ipc:sab-ring-proof

Revision: rev0028

## Purpose

This slice gives BrowserRT its first concrete shared-memory IPC proof without paying another browser/CDP launch cost. Rev0014 keeps this Node proof as the cheap baseline and adds a separate browser Worker SAB proof rather than merging the two.

It tests:

- `SharedArrayBuffer` allocation;
- `Atomics` availability;
- fixed Int32 ring header with BRT1 magic;
- bounded full rejection;
- producer retry/backpressure evidence;
- worker-thread consumer using `waitPop` and `Atomics.wait`;
- producer wake through `Atomics.notify`;
- wraparound;
- close waking the consumer;
- all values received in order;
- trace event evidence.

## Command

```bash
node tools/run_tests.mjs --tier release --id ipc:sab-ring-proof --jobs 1
```

Direct probe:

```bash
node tools/sab_ring_probe.mjs --json artifacts/validation/REV0044-SAB-RING-PROBE.json
```

## Current evidence

The generated artifact is:

```txt
artifacts/validation/REV0044-SAB-RING-PROBE.json
```

The key observations are:

- `fullBeforeConsumer: true`
- `producerBackpressureObserved: true`
- `wraparoundObserved: true`
- `allReceived: true`
- `valuesInOrder: true`
- `sumMatches: true`
- `ringClosed: true`
- `noPendingItems: true`
- `workerPopCountMatches: true`
- `traceHasRequiredEvents: true`

## Non-claims

- This is the Node worker_threads proof; browser Worker SAB evidence lives in `browser:sab-ring-worker-proof`.
- This is SPSC only.
- This is fixed Int32 payload only.
- This is not an MPSC/MPMC mailbox.
- This is not a latency or throughput benchmark.
- This does not prove `Atomics.waitAsync`.
- This does not prove WebAssembly shared-memory integration.

## Next slice

The browser-scoped and capability-gated sibling slice is now:

```txt
browser:sab-ring-worker-proof
```

It proves the same SPSC ring inside the existing managed CDP fixture with `crossOriginIsolated: true`, while still avoiding blocking waits on the browser main thread.
