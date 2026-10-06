# One-runtime vision — rev0044

Current revision: rev0054

BrowserRT could become the browser's local runtime substrate: not an app, but the layer apps use to become serious local software.

## Workstreams to protect

1. **Testing office:** keep release cheap, browser slices explicit, artifacts useful, and affected selection trustworthy.
2. **Provider ladder:** fake -> Node -> browser smoke -> browser provider -> external evidence.
3. **Storage lane:** OPFS block store, adapter, journal/manifest, worker sync handle, quota/crash non-claims.
4. **Scheduler/overload lane:** admission, retry, retry budget, breaker/bulkhead, model oracles, provider histories.
5. **IPC lane:** transfer refs, SAB fixed rings, SAB frame rings, spill mailboxes, model walks.
6. **Mesh lane:** Web Locks, BroadcastChannel, SharedWorker, ServiceWorker, same-origin ownership.
7. **Accelerator lane:** CPU/WASM/WebGPU/WebNN provider broker, smoke first, performance external.
8. **Plugin lane:** capability handles and component/plugin worlds.
9. **Devtools lane:** trace viewer, model history viewer, replay, claim checker.

## Near-term recommendation after rev0044

Return to earned low-level stairs. Good next candidates:

- OPFS journal/manifest skeleton;
- OPFS Worker/sync-access-handle block-store provider;
- OPFS storage-lane model boundary;
- storage-lane adapter failure/recovery semantics;
- multi-tab Web Locks leader-election smoke.

Do not jump directly from rev0044 dream docs into production claims.
