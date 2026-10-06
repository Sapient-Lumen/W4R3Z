# Kernel Kit support bundle contract audit — rev0107

Status: rev0107 linked refinement. Runtime revision remains rev0107.

This support bundle contract audit stays browser-light. It verifies the support bundle, exact commands, evidence ledger, replay plan, and non-claims without launching Chromium.

The rev0107 risk change is the quota pressure checkpoint: the bundle must include `storage-pressure-checkpoint`, `proof.storagePressureCheckpointPresent`, the exact command `browser:opfs-lane-quota-backpressure-proof`, and the evidence ledger row `browser-storage-pressure-artifact`.

The rev0139 risk change is storage recovery guidance: the browser-light bundle must carry a privacy-bounded `storage-recovery-guidance` section with canonical rows for admission rejection, Web Lock timeout, and provider quota so operators can tell pre-mutation rejection from mutation-attempted quota failure without raw error message, stack, path, digest, or lock-name leakage.

Required non-claims remain visible: No production support-bundle claim. No automated failure triage claim. The quota pressure/backpressure path is not eviction survival, quota reservation, fsync, crash recovery, or cross-browser storage conformance. This remains browser-light audit evidence.
