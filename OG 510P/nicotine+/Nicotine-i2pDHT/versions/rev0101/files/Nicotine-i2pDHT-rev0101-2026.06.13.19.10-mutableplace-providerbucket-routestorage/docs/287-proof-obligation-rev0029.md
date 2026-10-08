# Proof obligations — rev0029

Executable obligations:

- `checkpointlane.py` must accept linked advancing checkpoints while preserving live hard-negative facts.
- `checkpointlane.py` must reject rollback, fork, previous-link mismatch, bad signature, conflicting facts, and hard-negative drops.
- `egressmeter.py` must enforce byte, stream, raw-key, decoy, family, freshness, and replay budgets.
- `dispatchjoin.py` must reject upstream misbinding and quarantine scope/object leaks before handler dispatch.
- `foldseal.py` must keep rev0029 navigable and verify that rev0028 foldspine still passes.

Evidence:

```text
tests/test_rev0029_checkpoint_egress_dispatch_foldseal.py
scripts/ci/run_python_cloudtainer_lane.sh
artifacts/process/rev0029_local_verification.json
```
