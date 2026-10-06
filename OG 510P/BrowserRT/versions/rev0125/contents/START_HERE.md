# START HERE — BrowserRT rev0125

Start with the product seam, not the registry: rev0125 keeps OPFS Raw Composite AbortSignal as the current office and fixes the staged-recovery gap across provider instances when callers use the Web Lock guard.

Current packaged head: `rev0125` / `0.0.125`.

Current package target: `BrowserRT-rev0125-2026.06.18.17.02-opfs-block-store-raw-composite-abort-signal-current-proof-guarded-staged-recovery-web-lock-serialization-green-lock.zip`.

Current release task: `opfs:block-store-raw-composite-abort-signal-proof`.
Current browser task: `browser:opfs-block-store-raw-composite-abort-signal-proof`.
Current audit: `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`.

Run:

```bash
npm run test:current
npm run audit:current
npm run test:opfs-block-store-guarded-staged-recovery
```

The highest-value next step is either a fresh managed-browser OPFS/Web Locks version of this guarded staged-recovery wedge or canonical-block scrub/repair; avoid adding another proof registry until one of those product risks is closed.

## Non-claims

This release is browser-light. It does not claim fresh cross-browser execution, quota or eviction survival, or real crash/power-loss durability for staged recovery.

## rev0125 audit anchor — current office and non-claims
Current packaged head: `rev0125`. Canonical current task: browser:opfs-block-store-raw-composite-abort-signal-proof. Canonical audit: facility:opfs-block-store-raw-composite-abort-signal-contract-audit. Codename: OPFS Raw Composite AbortSignal. Runtime surface: OPFSAsyncBlockStore, abortSignal / AbortSignal, composite signal handling, raw OPFS block-store path, browser-light release proof. Rev0125 adds fake Web Locks guarded staged recovery serialization for staged temp cleanup.
Non-claims: not cross-browser proof, no quota guarantee, no eviction survival guarantee, no crash/power-loss durability proof, browser-heavy rows are retained evidence rather than fresh browser execution.
Storage note: guarded staged recovery is storage coordination hygiene; it does not claim production readiness.
