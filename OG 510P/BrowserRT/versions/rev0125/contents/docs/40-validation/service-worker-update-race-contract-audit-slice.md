# Service Worker update-race contract audit — rev0067

Task: `facility:service-worker-update-race-contract-audit`

This browser-light audit keeps the rev0067 Service Worker update-race proof wired without launching Chromium. It checks that the browser proof, probe worker, CDP fixture support, first-read docs, manifest, impact map, surface inventory, package scripts, Makefile targets, and current-office metadata still point at the update-race slice.

The audit is intentionally not runtime evidence. It prevents drift around the proof that uses module Service Worker v1/v2 scripts, `updateViaCache: 'none'`, a v1-held BrowserRT guarded OPFS mutation Web Lock, page-side `BRT_WEB_LOCK_TIMEOUT`, storage-lane backpressure, blocked settled recovery while contended, CDP closure of the old Service Worker target, explicit recovery, absence of the timed-out OPFS block, and a verified v2 guarded OPFS write after settlement.

Non-claims: no browser runtime proof by itself; no cross-browser Service Worker/Web Locks/OPFS behavior claim; no full Service Worker update algorithm correctness claim; no mobile/background suspension, fetch/push/offline behavior, browser-shutdown durability, OPFS durability/fsync, power-loss safety, crash recovery, quota survival, eviction survival, persistent-retention, automatic recovery, throughput, latency, SLO, or production-readiness claim.

Run:

```sh
node tools/run_tests.mjs --tier release --id facility:service-worker-update-race-contract-audit --jobs 1 --json artifacts/validation/REV0067-SERVICE-WORKER-UPDATE-RACE-AUDIT-RUN.json
```
