# Browser Kernel Kit session coordination checkpoint slice

Runtime revision: rev0107.

The browser-heavy session coordination proof is the risky part of the slice. It spends managed Chromium/CDP budget intentionally instead of hiding multi-tab assumptions inside a browser-light support bundle.

Command:

```bash
node tools/run_tests.mjs --tier browser --id browser:kernel-kit-session-coordination-checkpoint-proof --jobs 1
```

The probe serves a tiny same-origin page, creates a second page target through CDP, and checks:

1. both pages are same-origin and expose `navigator.locks` and `localStorage`;
2. the primary page holds an exclusive Web Lock;
3. the peer page receives `acquired: false` for an `ifAvailable` exclusive request while the primary lock is held;
4. a queued peer request does not acquire until the primary page releases;
5. `navigator.locks.query()` has no held or pending rows for the proof lock after completion;
6. a peer-written local handoff key triggers same-origin storage events;
7. the handoff is consumed once and removed;
8. the stale read after removal is null.

The artifact is compact and suitable for package sealing, but it is not an eviction, durability, fairness, crash-recovery, or cross-browser proof. Abandoned lock release remains explicitly deferred.

This remains a not production coordination posture: it preserves browser-heavy evidence boundaries and explicit non-claims instead of upgrading the proof into production multi-tab coordination.

The explicit non-claim boundary is part of the proof: Web Locks fairness is not claimed, crash recovery is not claimed, and stale handoff behavior is limited to this single observed clear/read-null path.
