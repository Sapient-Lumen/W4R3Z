# Service Worker restart/update contract audit — rev0065

`facility:service-worker-restart-update-contract-audit` is a browser-light release audit. It does not launch Chromium. Its job is to keep the explicit browser proof discoverable and wired without turning the broad release sweep into a browser-heavy run.

The audit checks that the worker source exposes the short `put-once` command and identity needed by the restart/update proof; the browser proof uses a retained profile, reused origin server, v1/v2 Service Worker routes, `updateViaCache: 'none'`, guarded OPFS writes, page verification, storage-lane write, cleanup, unregister, and process reaping; the manifest, impact map, surface inventory, first-read docs, package scripts, Makefile targets, and current-office metadata all name the current proof and audit.

Non-claims:

- The audit does not prove browser runtime behavior.
- The audit does not prove cross-browser, mobile/background, fetch/push/offline, OPFS durability, quota, eviction, persistent-retention, or production behavior.
- The managed Chromium browser proof must still be run explicitly by id for runtime evidence.

Crash boundary note: this audit keeps restart/update documentation visible, but it does not prove browser crash, kernel crash, process kill, fsync, quota, eviction, persistent-retention, or cross-browser behavior.
