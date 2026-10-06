# rev0107 OPFS block-store raw composite AbortSignal slice

## What changed

`OpfsAsyncBlockStore` now composes direct raw-provider `signal` and `abortSignal` options instead of choosing `signal` and silently ignoring a sibling `abortSignal`.

This closes the gap left after the scheduled-lane and Web Lock guarded paths learned to compose abort sources: direct OPFS callers can now supply both cancellation handles without one source masking the other.

## Runtime boundary

The raw provider now validates both fields before OPFS work begins. Invalid `signal` or `abortSignal` shapes fail closed with `BRT_OPFS_ABORT_SIGNAL_INVALID`. When both supplied signals are valid, BrowserRT creates one effective provider signal. A pre-aborted secondary `abortSignal` rejects before digest/open/mutation even when `signal` is still live. A live secondary `abortSignal` can also abort during provider checkpoints and trigger existing failed-put rollback.

New observability:

- `compositeAbortSignals`
- `abortSignalOptionPairs`
- `storage:opfs-block-composite-abort-signal`

## Release proof

`tools/opfs_block_store_raw_composite_abort_signal_probe.mjs` uses fake OPFS to prove:

- pre-aborted `abortSignal` plus live `signal` rejects before provider open;
- invalid `abortSignal` plus valid `signal` is not masked;
- mid-write secondary `abortSignal` aborts the writable stream and rolls back the final block path;
- read-side secondary `abortSignal` also wins over a live `signal`;
- composite decisions are exposed through stats and trace output.

## Non-claims

This is not a browser-wide cancellation guarantee. Abort remains cooperative at BrowserRT checkpoints. The slice does not prove cross-browser behavior, OPFS fsync durability, crash or power-loss recovery, quota or eviction survival, Web Locks fairness, or production readiness.
