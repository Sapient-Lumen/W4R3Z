# Web Lock read-timeout nonpoison contract audit — rev0067

Task: `facility:web-lock-read-timeout-nonpoison-contract-audit`

## Purpose

This browser-light audit keeps the rev0067 read-side boundary wired into the cube without moving managed Chromium work into the release sweep. It checks that the runtime code distinguishes read-only Web Lock acquisition timeouts from mutating-provider timeouts, that the fast release probe exists, that the managed-browser proof exists, and that manifest, impact-map, surface-inventory, and first-read docs all point at the read-timeout nonpoison slice.

## Required contract markers

- `src/storage-lane-scheduler.mjs` contains the read-only Web Lock timeout policy.
- `tools/storage_lane_web_lock_read_timeout_nonpoison_probe.mjs` proves browser-light release behavior.
- `tools/browser_opfs_web_lock_read_timeout_nonpoison_probe.mjs` proves the real Chromium/Service Worker/OPFS/Web Locks path.
- `test/manifest.json` exposes the release guard and the explicit browser proof.
- `test/impact-map.json` maps runtime and proof edits to the new tasks.
- `test/surface-inventory.json` records the read-timeout nonpoison surfaces.

## Non-claims

The audit does not prove browser behavior. It only guards cube wiring and release-tier coverage. No cross-browser, fairness, starvation-freedom, mobile/background, OPFS durability, fsync, crash, quota, eviction, persistent-retention, SLO, or production-readiness claim is made.
