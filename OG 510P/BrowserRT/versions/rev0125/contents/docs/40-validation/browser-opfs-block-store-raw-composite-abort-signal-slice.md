# rev0107 browser OPFS raw composite AbortSignal slice

## Managed Chromium proof

`tools/browser_opfs_block_store_raw_composite_abort_signal_probe.mjs` runs the raw `OpfsAsyncBlockStore` composition path in a managed Chromium page with real OPFS.

The proof covers:

- direct raw OPFS `put()` rejects when `abortSignal` is already aborted even if `signal` is live;
- a malformed `abortSignal` sibling is not hidden by a valid `signal`;
- direct raw OPFS `get()` honors the secondary `abortSignal`;
- a patched browser `createWritable()` path aborts after writable acquisition but before `write()`, proving the composed signal reaches provider checkpoints before bytes are written;
- the guarded OPFS/Web Locks smoke path still writes, verifies, reads, cleans up, and drains locks.

## Why this matters

The previous wrappers were safer than the raw provider. That is risky because callers and future adapters can still reach the provider directly. Rev0107 makes the raw provider own the same two-field abort vocabulary as the scheduled and guarded paths.

## Non-claims

Managed Chromium is not a cross-browser conformance result. The proof does not claim OPFS fsync durability, crash safety, eviction survival, quota reservation, Web Locks fairness, or production storage readiness.
