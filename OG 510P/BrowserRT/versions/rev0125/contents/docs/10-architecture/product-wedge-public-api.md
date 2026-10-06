# Product wedge public API

BrowserRT's supported consumer seam is `src/public-api.mjs` inside the cube and the package root when installed. It intentionally exposes a small product wedge instead of the full internal barrel in `src/browserrt.mjs`.

The wedge must prove a real path: boot a runtime, push bounded work through a channel, run a supervised Worker call with a transferable object reference, reject excess admission without mutation, write/read through a storage lane, close the trace, and validate a receipt.

Current proof commands:

```sh
node tools/product_wedge_public_api_probe.mjs --json artifacts/validation/REV0108-PRODUCT-WEDGE-PUBLIC-API-PROBE.json
node tools/package_installed_consumer_smoke_probe.mjs --json artifacts/validation/REV0108-PACKAGE-INSTALLED-CONSUMER-SMOKE-PROBE.json
node tools/package_installed_browser_consumer_smoke_probe.mjs --json artifacts/validation/REV0108-PACKAGE-INSTALLED-BROWSER-CONSUMER-SMOKE-PROBE.json
node tools/package_installed_browser_opfs_consumer_probe.mjs --json artifacts/validation/REV0108-PACKAGE-INSTALLED-BROWSER-OPFS-CONSUMER-PROBE.json
node tools/package_installed_browser_cross_tab_opfs_consumer_probe.mjs --json artifacts/validation/REV0108-PACKAGE-INSTALLED-BROWSER-CROSS-TAB-OPFS-CONSUMER-PROBE.json
node tools/package_installed_browser_reopen_opfs_consumer_probe.mjs --json artifacts/validation/REV0108-PACKAGE-INSTALLED-BROWSER-OPFS-REOPEN-CONSUMER-PROBE.json
node tools/package_installed_browser_tab_close_opfs_consumer_probe.mjs --json artifacts/validation/REV0108-PACKAGE-INSTALLED-BROWSER-TAB-CLOSE-OPFS-CONSUMER-PROBE.json
node tools/public_api_contract_audit.mjs --json artifacts/audit/REV0108-PUBLIC-API-CONTRACT-AUDIT.json
```

Package-installed smoke is part of the product wedge because the package root has previously looked valid while either the tarball or declarations were incomplete. The Node guard packs a local tarball, installs it into a temporary consumer, imports `browserrt`, runs the product wedge outside the source tree, compiles a strict TypeScript consumer, and compares the installed `BrowserRTRuntime` method set with the actual `boot()` method set. The browser guard repeats the installed-package path in managed Chromium: it serves the installed package files under COOP/COEP, uses an import map to resolve `browserrt` to the installed public API, loads the module Worker from the installed package, transfers an `ArrayBuffer`, and validates the same receipt.

The browser OPFS guard closes the earlier fast-path non-claim. It packs and installs the tarball, imports the installed public API in managed Chromium, then writes, verifies, reads, estimates, settles, and cleans up a real OPFS async block through `WebLockGuardedBlockStore` and the storage-lane scheduler. This proves the supported package boundary can reach the guarded browser storage coordination path, not merely the memory-backed lane used by the fast wedge.

The cross-tab OPFS guard closes the next same-origin coordination gap. It opens two managed Chromium page targets against the installed package, imports `browserrt` through the same import map in both tabs, gives both tabs one OPFS prefix and Web Lock name, holds an exclusive lock in tab A, verifies tab B times out before acquisition while queued, releases the lock, then writes from both tabs through storage-lane operations and cross-reads each tab's block by content ref. The proof intentionally demonstrates pending-lock cancellation and recovery after release; it does not claim fairness once a lock is acquired.


The tab-close OPFS guard closes the next Web Locks lifecycle gap. It opens a holder tab and survivor tab against the installed package, writes a real OPFS block while the holder remains inside an exclusive Web Lock callback, proves the survivor times out before acquisition, closes the holder page target through CDP, then proves the survivor can settle, write, read the holder block by ref, and clean up. 

All package guards verify the npm tarball includes the needed runtime files and excludes development-only `artifacts/`, `tools/`, `test/`, and `node_modules/` surfaces.

Non-claims: this is not a package-publication, bundler, semver, browser matrix, cross-browser, quota-pressure, organic eviction, fsync, abrupt crash-recovery, renderer-crash semantics, multi-tab fairness under organic load, or production-readiness claim.
