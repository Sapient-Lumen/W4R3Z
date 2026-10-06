# rev0106 Web Lock guarded AbortSignal contract audit slice

`tools/web_lock_guarded_abort_signal_contract_audit.mjs` is the static contract audit for the rev0106 runtime slice. It checks that the runtime hooks, type markers, release proof, browser proof, documentation, manifest rows, impact map row, surface inventory rows, current-office scripts, Makefile routing, `check_cube`, and deep/current-office audits all point at the same current slice.

The audit intentionally protects `WebLockGuardedBlockStore` against two regressions:

- direct guarded calls must not drop `abortSignal` while acquiring the Web Lock or calling the provider;
- `WebLockCoordinator` must not relabel provider-side errors as `BRT_WEB_LOCK_ABORTED` after acquisition.

The audit is not behavioral evidence by itself. The release proof and managed Chromium proof provide the behavior checks. Non-claims remain explicit: no cross-browser proof, no quota or eviction guarantee, no crash or fsync durability guarantee, no Web Locks fairness claim, and no production readiness claim.
