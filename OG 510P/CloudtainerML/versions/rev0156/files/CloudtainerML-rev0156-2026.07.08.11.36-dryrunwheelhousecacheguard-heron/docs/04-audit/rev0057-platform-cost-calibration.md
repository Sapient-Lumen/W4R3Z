# rev0057 — platform cost calibration and router veto

`rev0056` left a dangerous opening: the adaptive router looked useful only after assigning QK score work a high proxy cost relative to value reads. `rev0057` replaces that open assumption with a measured native CPU primitive calibration.

## Added artifacts

- `artifacts/probe-results/REV0057_PLATFORM_PRIMITIVE_COST_NATIVE.json`
- `artifacts/probe-results/REV0057_PLATFORM_COST_CALIBRATED_ROUTER.json`
- `artifacts/run-manifests/REV0057_PLATFORM_COST_CALIBRATED_ROUTER_RUN_MANIFEST.json`
- `artifacts/audit/REV0057_PLATFORM_COST_CALIBRATION_AUDIT.json`

## Finding

The measured router-dimension CPU ratio for one QK dot versus one sequential value accumulation is about `1.06`, while the `rev0056` all-row break-even was `12.0`. Using sparse/gather value accumulation makes the QK/value ratio even less favorable to the router.

The adaptive router remains interesting only for low-support rows. It does not beat the dense-score histogram on all rows or high-support rows under the measured CPU primitive ratio.

## Claim boundary

This does not close the GPU/fused-kernel blocker. It closes only the measured CPU primitive ratio blocker for the tiny learned-trace router frontier.
