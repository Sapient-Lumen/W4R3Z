# Claim Matrix

Generated from `specs/claim_classes.yaml`.

- total_claim_classes: 7

| id | title | evidence_class | strict_gate_required | required_checks |
|---|---|---|---|---|
| `CC-001` | Empirical performance claim | `empirical` | no | make test-quick<br>make test-full<br>make test-spec-evidence |
| `CC-002` | Robustness claim | `empirical` | no | make test-quick<br>make gate<br>make test-experiment-catalog |
| `CC-003` | Formal invariance claim | `formal` | yes | make test-formal-smoke<br>make test-formal-tools<br>make gate |
| `CC-004` | Cross-solver agreement claim | `formal` | yes | make test-formal-tools<br>make gate<br>make gate-strict |
| `CC-005` | Probabilistic bound claim | `hybrid` | yes | make gate<br>make gate-strict |
| `CC-006` | Operational reproducibility claim | `operational` | no | make report-repro-bundle<br>make test-release-checksums RELEASE_VERSION=dev<br>make test-release-hygiene RELEASE_VERSION=dev |
| `CC-007` | Policy exception claim | `assumption` | no | make test-spec-ledger<br>make test-policy-expirations<br>make test-spec-evidence |
