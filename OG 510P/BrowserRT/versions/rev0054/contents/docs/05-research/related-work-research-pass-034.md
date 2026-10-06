# Related-work research pass 034 — OPFS storage-lane bridge

Current revision: rev0054

This pass keeps the OPFS work narrow and bridge-shaped. The useful related-work pressure is not "OPFS is a database"; it is that OPFS can be a browser-local storage provider, but BrowserRT still needs a scheduler/admission/recovery story around it.

Stolen ideas:

- **OPFS as provider, not promise.** MDN frames the origin private file system as origin-private storage, optimized for performance and subject to browser storage quotas. BrowserRT therefore treats OPFS as a provider lane with explicit quota/eviction non-claims.
- **Storage is bounded background work.** libuv and Tokio both reinforce that filesystem-looking operations consume limited runtime resources. BrowserRT should schedule OPFS work through a lane rather than sprinkling ad hoc awaits across app code.
- **SQLite/Wasm OPFS pressure.** SQLite's OPFS persistence docs and forum discussions keep multi-tab and concurrency boundaries visible. BrowserRT should not claim multi-tab safety until a Web Locks / leader / worker-gate proof exists.
- **No silent provider promotion.** The async block-store provider proof was earned in rev0039; rev0039 only earns a storage-lane adapter proof. Durability, crash recovery, fsync-like semantics, quota pressure, and sync handles remain unearned.

The concrete stair for this pass is `browser:opfs-storage-lane-adapter-proof`: route async OPFS block put/get/has/verify/delete through `StorageLaneExecutor` and `CrossLaneScheduler` in a managed Chromium/CDP fixture, while preserving broad release as browser-light.
