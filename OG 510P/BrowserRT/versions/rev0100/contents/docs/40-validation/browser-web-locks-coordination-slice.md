# Browser Web Locks coordination slice

Historical revision: rev0065

## Slice

`browser:web-locks-coordination-proof`

This explicit browser-tier slice probes a mesh/storage prerequisite that was previously only a non-claim: same-origin coordination through Web Locks. It checks three small browser behaviors in managed Chromium: exclusive same-name lock requests do not overlap, shared same-name lock requests can co-hold, and a dedicated Worker waits for the main page to release an exclusive same-origin lock before acquiring it.

The proof is intentionally narrow. It does not wire Web Locks into OPFS or storage lanes yet; it gives the cube executable evidence for one browser primitive needed before multi-tab or storage-leader coordination can become credible.

## Evidence

- Tool: `tools/browser_web_locks_coordination_probe.mjs`
- Manifest task: `browser:web-locks-coordination-proof`
- Expected artifact: `artifacts/validation/REV0060-BROWSER-WEB-LOCKS-COORDINATION-PROBE.json`

## Required observations

- `navigator.locks.request` and `navigator.locks.query` are available in the managed Chromium page.
- Two exclusive lock requests with the same name produce `maxExclusiveActive: 1` and no overlap.
- Two shared lock requests with the same name produce `maxSharedActive >= 2`.
- A dedicated Worker exposes `navigator.locks` and receives the lock only after the main page releases its exclusive lock.

## Non-claims

No storage durability, OPFS quota, eviction, crash-recovery, fairness, background lifecycle, or cross-browser conformance claim.

- No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.
- No cross-browser conformance claim.
- No lock fairness, starvation, background lifecycle, crash, or page-freeze claim.
- No production storage-leader or mesh coordination claim.
- No throughput, latency, SLO, or real performance claim.

## Core non-claims

No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.
