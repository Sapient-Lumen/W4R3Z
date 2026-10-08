# Proof obligation — rev0042

The rev0042 proof lane must show:

- multi-service router actions reject active siblings, public bridge leftovers, drift, replay, forks, and low diversity;
- profile cooldown holds until the freeze window expires and diverse recovery evidence is present;
- operator key rotation requires successor cosign and recovery preserves hard-negative evidence with witness diversity;
- announcement repair rejects stale public announcements, rollback, fork, hard negatives, replay, drift, and low diversity;
- `controlplanefold` passes and preserves rev0041 `controlfold` predecessor history.

Evidence:

- `tests/test_rev0042_multiservice_cooldown_keyoperator.py`
- `scripts/ci/run_python_cloudtainer_lane.sh`
- `artifacts/process/rev0042_local_verification.json`
