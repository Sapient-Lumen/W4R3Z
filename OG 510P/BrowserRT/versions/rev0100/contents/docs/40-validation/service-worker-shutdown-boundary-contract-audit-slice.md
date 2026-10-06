# Service Worker shutdown-boundary contract audit — rev0066

Current audit: `facility:service-worker-shutdown-boundary-contract-audit`

The audit is intentionally browser-light. It verifies that the managed Chromium shutdown-boundary proof is wired through runtime helpers, CDP fixture cleanup, manifest, impact map, surface inventory, first-read docs, operator shortcuts, and current-office metadata without moving browser-heavy execution into the release tier.

The audit protects the following current surfaces:

- `tools/browser_opfs_web_lock_service_worker_shutdown_boundary_probe.mjs`
- `tools/browserrt_opfs_web_lock_service_worker_holder.mjs`
- `tools/browser_cdp_fixture.mjs`
- `docs/40-validation/browser-opfs-web-lock-service-worker-shutdown-boundary-slice.md`
- `test/manifest.json`
- `test/impact-map.json`
- `test/surface-inventory.json`

Non-claims: this audit does not launch Chromium, prove Service Worker runtime behavior, prove Web Locks fairness, prove OPFS durability, prove quota/eviction/persistent-retention behavior, or certify production readiness.

Additional non-claims carried for slice-doc audits: no cross-browser conformance, no crash recovery guarantee, no quota survival, and no eviction survival claim.
