# Provider contract frontier

Revision: rev0028

BrowserRT should not bake one browser API into each runtime feature. It should expose provider contracts.

## Provider contract shape

Each provider should eventually declare:

```txt
id
family
capabilities required
capabilities provided
startup cost estimate
steady-state cost estimate
failure modes
teardown contract
trace events
manifest test ids
fallback providers
non-claims
```

## Why this belongs early

Without providers, the runtime becomes a set of special cases:

```txt
if Worker then this
if OPFS then that
if WebGPU then another thing
```

With providers, BrowserRT can become a reconciled runtime:

```txt
I need a compute lane for user-visible work.
Available providers: main, browser-worker, fake-simulator.
Chosen provider: browser-worker.
Reason: Worker exists, transferables exist, selected task is not tiny.
Trace: provider:selected.
```

## Provider families that matter

Current:

- `node-worker-thread-agent`;
- `browser-module-worker-agent`;
- `browser-cdp-fixture`;
- `memory-transfer-arraybuffer`;
- `trace-json-artifact`.

Future:

- `opfs-async-block-store`;
- `opfs-sync-worker-store`;
- `sab-ring-mailbox`;
- `webgpu-compute-dispatch`;
- `broadcastchannel-bus`;
- `weblocks-reconciler`;
- `fake-deterministic-scheduler`;
- `fake-storage-provider`.

## Rev0008 provider proof

`browser:worker-agent-proof` is the first browser provider proof beyond boot. It proves that `browser-module-worker-agent` can run the shared agent runtime and process a transferred buffer.

It remains deliberately separate from OPFS, SAB, WebGPU, SharedWorker, ServiceWorker, and mesh.
