# Kernel Kit support bundle roadmap — rev0107

Status: rev0107 linked refinement. Runtime revision remains rev0107.

The support bundle roadmap now treats quota pressure as a concrete follow-up path rather than an implied TODO. Keep the browser-light support bundle small, but require it to name `browser:opfs-lane-quota-backpressure-proof` and `browser-storage-pressure-artifact` so future sessions can spend browser/CDP budget intentionally.

Forward risk order now prioritizes storage recovery guidance before broader doctrine: keep the operator path actionable for admission rejection, lock contention, and provider quota, while preserving the deferral of automatic retry, quota/eviction survival, and cross-browser lifecycle claims.

Next risk order: run quota pressure/backpressure proof when browser budget is available; keep quota/eviction survival deferred until directly tested; then widen cross-browser/mobile lifecycle and side-channel/privacy posture.

Non-claims: No production support-bundle claim. No automated failure triage claim. This browser-light roadmap is not a quota/eviction survival claim, quota reservation, fsync, crash recovery, or cross-browser storage conformance claim.
