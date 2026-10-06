# Kernel Kit lifecycle checkpoint contract audit slice

Status: rev0107 linked refinement. Runtime revision remains rev0107.

The lifecycle checkpoint audit is intentionally small and practical. It verifies that the new checkpoint is not just a document:

- the checkpoint probe validates;
- the lifecycle rows exist in source;
- runtime imports, exports, and methods are wired;
- the support bundle carries the checkpoint;
- the browser runner creates work/reload lifecycle checkpoints;
- TypeScript declarations expose the surface;
- manifest, impact map, surface inventory, and package-retention paths name the proof and audit artifacts;
- docs state the quota/eviction, cross-browser/mobile, and side-channel deferrals as not production readiness.

This is an audit/refactor of evidence shape. It reduces waste by giving future sessions one product-path lifecycle checkpoint instead of asking them to re-read scattered OPFS, Web Locks, storage posture, reload, and support-bundle slices.

## Deliberate limits

The audit does not launch Chromium. Browser-heavy confirmation still belongs to `browser:kernel-kit-demo-proof` and the current OPFS/browser proof lane. The audit checks the wiring and runs a browser-heavy synthetic shape so that observed rows cannot only ever be deferred.

## Practical next use

When a future session asks what is riskiest, read the checkpoint first. The highest-value next browser work should come from its deferred high-risk rows: quota/eviction behavior, cross-browser/mobile lifecycle behavior, and OPFS timing/privacy side-channel posture.

## rev0107 quota pressure checkpoint

The lifecycle checkpoint now separates quota pressure/backpressure from quota/eviction survival. The browser-light support bundle carries `quota-pressure-backpressure-evidence` as an explicit deferred row and names the browser-heavy command `browser:opfs-lane-quota-backpressure-proof`; running that command can observe quota pressure without erasing the broader quota/eviction survival deferral. This keeps quota pressure visible while preserving the not production readiness posture.

