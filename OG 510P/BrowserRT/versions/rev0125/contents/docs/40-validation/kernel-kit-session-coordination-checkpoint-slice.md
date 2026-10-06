# Kernel Kit session coordination checkpoint slice

Runtime revision: rev0107.

This slice adds an executable session coordination checkpoint for the BrowserRT Kernel Kit. It is deliberately focused on same-origin session risks that are easy to miss when the demo only proves a single happy-path page:

- exclusive Web Locks contention must be observed or explicitly deferred;
- queued lock acquisition must wait until release before it is treated as useful evidence;
- local handoff state must be single-use cleared;
- a stale handoff read must return null or remain visibly deferred;
- fairness, crash recovery, abandoned lock recovery, cross-browser/mobile lifecycle, and production multi-tab coordination stay non-claims.

Release-tier command:

```bash
node tools/run_tests.mjs --tier release --id demo:kernel-kit-session-coordination-checkpoint-proof --jobs 1
```

Browser-heavy command:

```bash
node tools/run_tests.mjs --tier browser --id browser:kernel-kit-session-coordination-checkpoint-proof --jobs 1
```

The release-tier proof creates a synthetic observed checkpoint and verifies the default support bundle keeps browser-heavy lock and stale-handoff rows deferred. The browser-heavy proof opens two same-origin managed Chromium pages, proves `navigator.locks.request(..., { ifAvailable: true })` is denied while another page holds an exclusive lock, proves a queued request acquires only after release, verifies `navigator.locks.query()` drains after the proof, observes a cross-tab `storage` event, clears the handoff once, and verifies a stale read returns null.

This is not production coordination. It does not claim Web Locks fairness, starvation-freedom, browser crash recovery, process-kill recovery, fsync durability, quota or eviction survival, cross-browser behavior, mobile behavior, service-worker lifecycle behavior, or stale-state immunity beyond the single observed handoff clear path.
