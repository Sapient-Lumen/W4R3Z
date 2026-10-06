# BrowserRT

Current packaged head: `rev0125` / `0.0.125`. Current task: `browser:opfs-block-store-raw-composite-abort-signal-proof`. Current release proof: `opfs:block-store-raw-composite-abort-signal-proof`. Current audit: `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`. Current package slug: `opfs-block-store-raw-composite-abort-signal-current-proof`.

BrowserRT is a browser-local runtime experiment for keeping one workload coherent across queues, workers, storage, OPFS, Web Locks, and tabs. The current engineering priority is storage/lifecycle correctness with executable proof, not registry expansion.

rev0125 hardens OPFS staged recovery across provider instances:

- the proof first demonstrates the raw risk: a second unguarded provider can delete a live staged temp and make the writer fail before publish;
- `WebLockGuardedBlockStore.recoverStagedWrites()` now routes staged-temp cleanup through the same exclusive Web Lock as guarded writes;
- guarded recovery waits behind a live staged put, then observes no staged candidates after the writer publishes and cleans up;
- the canonical `.blk` remains readable through another guarded provider using the same lock name.

Start with `START_HERE.md`, then run `npm run test:current` and `npm run audit:current`.

## Non-claims

This release is browser-light. It does not claim fresh cross-browser execution, quota or eviction survival, or real crash/power-loss durability for staged recovery.

## rev0125 audit anchor — current office and non-claims
Current packaged head: `rev0125`. Canonical current task: browser:opfs-block-store-raw-composite-abort-signal-proof. Canonical audit: facility:opfs-block-store-raw-composite-abort-signal-contract-audit. Codename: OPFS Raw Composite AbortSignal. Runtime surface: OPFSAsyncBlockStore, abortSignal / AbortSignal, composite signal handling, raw OPFS block-store path, browser-light release proof. Rev0125 adds fake Web Locks guarded staged recovery serialization for staged temp cleanup.
Non-claims: not cross-browser proof, no quota guarantee, no eviction survival guarantee, no crash/power-loss durability proof, browser-heavy rows are retained evidence rather than fresh browser execution.
Storage note: guarded staged recovery is storage coordination hygiene; it does not claim production readiness.
