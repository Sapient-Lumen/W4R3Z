# BrowserRT agent brief — rev0125

Current revision: rev0125 / 0.0.125. Current office remains rev0125 for OPFS Raw Composite AbortSignal. Current office remains OPFS Raw Composite AbortSignal: `opfs:block-store-raw-composite-abort-signal-proof`, `browser:opfs-block-store-raw-composite-abort-signal-proof`, and `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`.

## Active work seam

rev0125 keeps the product focus on OPFS content-addressed commit correctness. The new risk-reduction wedge is guarded staged recovery:

- raw cross-provider recovery can still delete another provider's live staged temp if callers bypass coordination;
- `WebLockGuardedBlockStore.recoverStagedWrites()` now exists and runs through the same exclusive Web Lock as guarded `put()`, `delete()`, and `cleanupForTest()`;
- the proof demonstrates the unguarded failure mode, then proves guarded recovery queues behind a live staged publish and runs only after the staged temp is cleaned and the canonical block is readable;
- this protects only providers sharing the same guard lock name/prefix; raw providers and mismatched guards are intentionally non-claims.

Do not expand doctrine or registries unless the executable proof needs them. Prefer code, probe, and audit changes that close runtime failure modes.

## Validation anchors

Run the current wedge with:

```bash
npm run test:current
npm run audit:current
npm run test:opfs-block-store-guarded-staged-recovery
```

Browser-heavy rows remain retained package evidence unless a fresh managed-browser run is explicitly executed in this container.

## Non-claims

This release remains browser-light: no fresh cross-browser matrix, no quota or eviction survival proof, and no real crash/power-loss durability claim.

## rev0125 audit anchor — current office and non-claims
Current packaged head: `rev0125`. Canonical current task: browser:opfs-block-store-raw-composite-abort-signal-proof. Canonical audit: facility:opfs-block-store-raw-composite-abort-signal-contract-audit. Codename: OPFS Raw Composite AbortSignal. Runtime surface: OPFSAsyncBlockStore, abortSignal / AbortSignal, composite signal handling, raw OPFS block-store path, browser-light release proof. Rev0125 adds fake Web Locks guarded staged recovery serialization for staged temp cleanup.
Non-claims: not cross-browser proof, no quota guarantee, no eviction survival guarantee, no crash/power-loss durability proof, browser-heavy rows are retained evidence rather than fresh browser execution.
Storage note: guarded staged recovery is storage coordination hygiene; it does not claim production readiness.
