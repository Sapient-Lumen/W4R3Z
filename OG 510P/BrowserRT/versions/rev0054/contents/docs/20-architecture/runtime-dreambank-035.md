# Runtime dreambank 035 — one runtime, many providers

Current revision: rev0054

The one-to-rule-them-all dream is not a giant monolith. It is a small kernel plus a provider ladder.

```txt
BrowserRT kernel
  -> agents/processes
  -> object refs
  -> bounded mailboxes
  -> storage providers
  -> scheduler lanes
  -> overload governors
  -> accelerator providers
  -> network providers
  -> plugin capabilities
  -> traces/replay/model histories
```

## Dream: BrowserRT as a local compute OS for the browser

A heavy local browser app should be able to ask BrowserRT:

```txt
Run this task by this deadline.
Use this bytes object without cloning it.
Persist this block if memory pressure rises.
Route this work through CPU unless GPU calibration says otherwise.
Reject background work under congestion but let critical work through.
Record the whole thing as a history a future session can replay.
Coordinate one storage-maintenance owner across tabs.
```

That is the dream. The cube's job is to earn it one rung at a time.

## Provider ladder

- **clone provider:** lowest-common denominator, structured clone, simple but slow.
- **transfer provider:** ArrayBuffer ownership movement.
- **SAB provider:** shared-memory rings/frames when cross-origin isolation exists.
- **OPFS provider:** origin-private blocks, manifests, journals, retained refs.
- **mesh provider:** BroadcastChannel, Web Locks, SharedWorker, ServiceWorker.
- **accelerator provider:** WebGPU/WebNN/WASM/SIMD with CPU fallback.
- **network provider:** WebRTC/WebTransport/server relay provider families.
- **plugin provider:** JS/Wasm components with explicit capabilities.

## Ambition traps

- Do not make WebGPU the personality of the project.
- Do not make OPFS page-reload readback sound like durability.
- Do not let fake-provider model proofs become browser-provider claims.
- Do not claim WebRTC/WebTransport behavior without real network evidence.
- Do not claim mobile/background behavior from desktop headless Chromium.
- Do not claim secure sandboxing from a TypeScript policy object.

## The strong thesis

BrowserRT's most valuable future is not one flashy demo. It is a **reusable runtime contract** underneath many demos and applications. The contracts to protect are:

- capabilities, not feature branches;
- data plane separate from control plane;
- object refs instead of giant object graphs;
- bounded queues, no unbounded hidden buffers;
- trace every fallback and rejection;
- browser-heavy proofs explicit by id/tier;
- dreams separated from earned claims.
