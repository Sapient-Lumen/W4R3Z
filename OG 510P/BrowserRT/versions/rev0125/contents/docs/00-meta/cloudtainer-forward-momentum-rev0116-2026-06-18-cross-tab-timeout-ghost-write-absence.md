# rev0116 forward momentum — cross-tab timeout ghost-write absence

The highest-risk product seam addressed in rev0116 is Web Locks timeout hygiene under same-origin contention. rev0115 proved that a second queued waiter could remain pending and later acquire after the holder released. rev0116 adds the missing no-mutation half: the first pending request that times out before lock acquisition now reports the content-addressed digest it would have written, and after the holder releases the installed browser OPFS package path verifies that digest remains absent through the storage-lane adapter.

This is deliberately not a new proof registry lane. The existing installed cross-tab browser package wedge now owns the behavior, the public API audit requires the example and receipt proof bit, and the package-installed probe fails if the digest absence check disappears.

Substantive files:

- `examples/browser-cross-tab-opfs-product-wedge-consumer.mjs`
- `tools/package_installed_browser_cross_tab_opfs_consumer_probe.mjs`
- `tools/public_api_contract_audit.mjs`

Non-claims remain unchanged: managed Chromium only; no cross-browser behavior, Web Locks fairness, quota/eviction survival, OPFS fsync or power-loss durability, arbitrary crash recovery, malicious same-origin safety, or production readiness claim.
