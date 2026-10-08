# Migration map — rev0124 to rev0125

## Added

- `evaluator/p1-chrony-policy.json`
- `tools/chrony_policy.py`
- `tests/profile-decision-acceptance.yaml`
- `tools/profile_decision_acceptance.py`
- `examples/evaluator/chrony-p1-after-display-limit-unsatisfied.json`
- `evaluator/CHRONY-P1-POLICY-DECISION-REV0125.md`
- `AUDIT-2026.06.17-rev0125.md`
- `archive/REV0125-AUDIT-POLICY-DECISION-ACCEPTANCE-REFACTOR.md`

## Changed

- `tools/chrony_adapter.py` and `tools/chrony_observation_eval.py` now load the P1 chrony lane table from `evaluator/p1-chrony-policy.json`.
- `tools/validate_archive.py` now runs the chrony policy self-test and executable profile-decision acceptance runner.
- Chrony-generated examples were regenerated with rev0125 policy references.
- `tests/semantic-test-vectors.yaml` now includes `TV-125-001` for the diagnostic-only post-display-horizon example.

## Not changed

- No TimeState core field was added.
- No claim of live capture, NTS verification, named UTC traceability, leap-smear discovery, PTP support, or non-chrony interoperability was added.
