# Capability tiers

BrowserRT is one runtime with multiple capability tiers.

| Tier | Name | Meaning |
|---:|---|---|
| 0 | basic | main thread plus structured clone fallback |
| 1 | workered | dedicated workers and transferables |
| 2 | isolated | SharedArrayBuffer and Atomics in cross-origin-isolated contexts |
| 3 | persistent | OPFS block store and storage worker paths |
| 4 | accelerated | WebGPU compute/render paths |
| 5 | mesh | cross-tab coordination through SharedWorker, BroadcastChannel, or Web Locks |

## Detection rule

Capabilities are detected at boot, but they are also checked at use sites. A
capability can disappear or fail, especially GPU devices and storage quota.

## Requirement rule

Applications may declare required tiers:

```js
await rt.require({ memory: 'transfer', storage: 'optional', gpu: 'optional' });
```

If a required tier is missing, BrowserRT fails with an explicit capability error.
If an optional tier is missing, BrowserRT chooses a traced fallback.

## No split-brain runtime

Do not fork BrowserRT into separate SAB, OPFS, or WebGPU variants. The point of
BrowserRT is coherent degradation.


## Adapter rule

Each tier is implemented through adapters. Adapters probe, optionally calibrate,
run lane-specific tasks, emit traces, and close. No adapter may silently downgrade
without emitting `capability:downgrade`.

## Ambitious future lanes

The tier table is intentionally broad enough for future render, media, audio,
ML, plugin, and same-origin mesh lanes. These future lanes are optional adapters,
not core scope commitments for the baby implementation.

