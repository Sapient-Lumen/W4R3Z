# Cloudtainer forward momentum — rev0118 runtime lifecycle

Current office remains rev0118 / OPFS Raw Composite AbortSignal.

This pass deliberately chose runtime substance over another registry slice. The high-risk false-green seam was lifecycle ownership: a bounded queue could still create unbounded pending promises, a timed-out worker call could keep mutating in the worker, worker startup could wait forever, and `runtime.close()` did not own resources created through `boot()`.

## Concrete changes

- `BoundedChannel` now has `maxWaitingSenders` and `maxWaitingReceivers`; overflow=`wait` cannot grow an unlimited waiter list.
- Channel `send()` and `receive()` now accept `signal`/`abortSignal` and `timeoutMs`; aborts/timeouts remove waiters and emit trace evidence.
- `BoundedChannel.close()` rejects pending waiters and clears queued work with an explicit closed disposition.
- `WorkerAgent` now enforces `readyTimeoutMs`; a never-ready worker is terminated and emits `agent:ready-timeout`.
- Worker call timeout/caller abort now sends `agent:cancel`; the worker shells route that to a per-call `AbortController` and emit `agent:cancelled`.
- Late worker results or errors after cancellation are classified as late settlements rather than disappearing silently.
- `boot()` now owns closeable resources returned by runtime factories and exposes `ownedResources()` plus deterministic `closeAsync()`.

## Audit/refactor result

The refactor compresses several informal lifecycle behaviors into one local ownership model without expanding the current-office registry. `tools/runtime_lifecycle_contract_audit.mjs` checks the source, worker shells, smoke evidence, and type surface for the new contract.

## Remaining risk

Cancellation is cooperative. A worker operation that ignores its signal can still continue until it returns or the agent is terminated. Compatibility `close()` still returns the legacy trace array and dispatches close asynchronously; `closeAsync()` is the deterministic contract. This pass does not claim cross-browser conformance, quota reservation, eviction survival, fsync durability, arbitrary crash recovery, browser-light equivalence, or production readiness.
