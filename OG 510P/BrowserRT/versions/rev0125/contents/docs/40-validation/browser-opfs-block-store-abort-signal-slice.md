# Browser OPFS block-store explicit AbortSignal slice

The managed Chromium proof `browser:opfs-block-store-abort-signal-proof` runs the rev0095 abort-signal boundary in a real browser realm.  It creates a raw `OpfsAsyncBlockStore`, rejects a pre-aborted `put()` before the store reports opened provider state, rejects an invalid signal value, verifies that a later valid OPFS put/read path still works, and confirms a pre-aborted `get()` returns `BRT_OPFS_OPERATION_ABORTED`.

The proof also performs a guarded OPFS/Web Locks write with `signal: null` to keep the adapter-compatible path covered after the raw-provider change.  Managed Chromium Web Locks query state must drain to zero held and pending locks after the guarded write.

Non-claims remain explicit: Managed Chromium only; no cross-browser claim, no production readiness claim, no storage-lane timeout cancellation claim, no OPFS fsync durability, no quota/eviction proof, no crash recovery proof, and no sync-access-handle proof.  Deterministic mid-write abort rollback is covered by the fake-OPFS release proof rather than by browser timing.

Audit marker: not storage-lane timeout cancellation.
