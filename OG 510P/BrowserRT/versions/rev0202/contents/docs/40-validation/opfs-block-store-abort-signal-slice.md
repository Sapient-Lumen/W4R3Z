# OPFS block-store explicit AbortSignal slice

rev0095 closes a runtime gap in `OpfsAsyncBlockStore`: the guarded and lane-adapter surfaces already threaded `signal`/`abortSignal` options, but the raw OPFS provider did not honor them.  The provider now checks an explicit caller abort signal at provider checkpoints and fails closed with `BRT_OPFS_OPERATION_ABORTED` before continuing storage work.

The release proof `opfs:block-store-abort-signal-proof` uses the shared fake-OPFS harness to verify three risky cases:

1. a pre-aborted `put()` rejects before the provider opens OPFS or creates a block file;
2. invalid signal values reject as `BRT_OPFS_ABORT_SIGNAL_INVALID` instead of being ignored;
3. aborted in-flight `put()` calls abort the writable stream when still open and use the existing rollback path to remove any created final block file.

This is explicit caller-cancellation handling only.  It does **not** convert storage-lane operation timeouts into provider cancellation, does not claim exactly-once writes, and does not prove fsync durability, crash/power-loss safety, quota/eviction behavior, Web Locks fairness, sync-access-handle behavior, or cross-browser conformance.

Audit marker: not storage-lane timeout cancellation.
