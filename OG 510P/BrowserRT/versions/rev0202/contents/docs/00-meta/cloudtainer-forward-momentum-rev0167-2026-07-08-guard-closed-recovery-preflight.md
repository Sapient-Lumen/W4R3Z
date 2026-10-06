# rev0167 linked forward momentum — guard-closed recovery preflight

Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal. Rev0167 is linked lifecycle hardening, not a runtime promotion.

The concrete risk was a closed `WebLockGuardedBlockStore`: `#throwIfClosed()` previously threw before the normal guarded recovery path, so consumers could see a raw lifecycle error while the generic `BRT_OPFS_*` classifier might imply provider mutation. The fix attaches browser-storage recovery guidance before throw and records `BRT_OPFS_WEB_LOCK_GUARD_CLOSED` as `guard-lifecycle-closed`, `preMutationRejected: true`, `mutationAttempted: false`, and `mutationCommitted: false`.

The targeted fake Web Locks proof now closes the guard, attempts `put()`, and asserts no `locks.request` call and no provider mutation. The contract audit guards the closed-reject trace, shared recovery guidance trace, type union, and probe assertions.

Research boundary: Web Locks release when callback work settles and aborts only reject pending requests; OPFS remains quota-bound and cleared with site data. Closed-guard recovery is therefore a local BrowserRT lifecycle preflight, not browser durability, persistence, fairness, or cross-browser proof.
