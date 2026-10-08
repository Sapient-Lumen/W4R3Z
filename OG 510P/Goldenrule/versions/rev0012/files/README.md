# Concord

Concord is a research lab for deterministic reciprocity experiments.

Core split:
- Rust (`crates/gr_engine`) for simulation and formalizable artifacts.
- Python (`grlab`) for orchestration, reporting, and workflow tooling.

Project scope is defined in [docs/PROJECT_CHARTER.md](/workspace/docs/PROJECT_CHARTER.md).

Execution plan is tracked in [docs/SCIENCE_PLAN.md](/workspace/docs/SCIENCE_PLAN.md).

## Operating Contract

- Behavioral rules for humans/agents: [AGENTS.md](/workspace/AGENTS.md)
- Governance and ops docs: [docs/README.md](/workspace/docs/README.md)
- Implementation provenance: [docs/PROVENANCE.md](/workspace/docs/PROVENANCE.md)

## Command Index

Primary repo controls run through `make`:

```bash
make doctor
make test-quick
make test-full
make gate
make gate-strict
make clean-test-artifacts
make test-flake N=5
make test-soak N=2
make test-soak-async N=2
make check-soak-status
make test-formal-smoke
make test-formal-tools
make test-examples-json
make test-examples-unique-ids
make test-required-examples
make test-schema-json
make test-policy-json
make test-hooks-contract
make test-artifact-gitkeeps
make test-timing-artifacts
make test-generated-docs
make test-research-docs
make test-claim-classes
make update-claim-matrix
make test-claim-matrix
make test-claim-register
make update-claim-register-summary
make test-claim-register-summary
make test-risk-register
make update-risk-register-summary
make test-risk-register-summary
make test-doc-links
make test-readme-commands
make test-docs-index
make test-release-doc
make test-tranches
make update-tranche-status
make test-tranche-status
make test-ci-smoke
make test-policy-expirations
make test-spec-evidence
make test-make-help
make test-scripts-exec
make test-scripts-compile
make update-experiment-catalog
make test-experiment-catalog
make update-command-inventory
make test-command-inventory
make update-validator-inventory
make test-validator-inventory
make update-policy-inventory
make test-policy-inventory
make update-schema-inventory
make test-schema-inventory
make update-artifact-buckets
make test-artifact-buckets
make report-artifact-summary
make test-reports-json
make report-repro-bundle
make test-release-manifest-schema
make test-release-manifest-entries RELEASE_VERSION=dev
make test-release-checksums RELEASE_VERSION=dev
```

`make gate-strict` requires strict security tools (currently `cargo-audit` and `cargo-deny`).

Core legacy checks:

```bash
tools/check.sh
```

Domain CLI examples:

```bash
python3 -m grlab run examples/experiments/ipd_smoke.json
python3 -m grlab report runs/<run_id>
python3 -m grlab verify runs/<run_id>
python3 -m grlab gauntlet --candidate examples/strategies/tft.json --world examples/worlds/ipd_long.json
python3 -m grlab holdout --candidate examples/strategies/tft.json
python3 -m grlab search --world examples/worlds/ipd_long.json --opponent examples/strategies/extortion_chi3.json --trials 100 --out /tmp/search.json
```

## Baseline Layout

- `specs/`: normative spec and assumption ledger.
- `docs/`: governance and operational policy.
- `docs/FORMAL_METHODS.md`: formal invariants and solver posture.
- `docs/CLAIM_TAXONOMY.md`: claim classes and evidence obligations.
- `docs/CLAIM_MATRIX.md`: generated claim-class matrix.
- `docs/CLAIM_REGISTER.md`: generated claim register summary.
- `docs/RISK_REGISTER.md`: generated risk register summary.
- `docs/EXPERIMENT_CATALOG.md`: generated index of example scientific assets.
- `docs/QUALITY_ASSURANCE.md`: executable QA posture and gates.
- `docs/REPRODUCIBILITY.md`: deterministic replay and repro bundle rules.
- `docs/CI_POLICY.md`: CI smoke and deterministic enforcement.
- `docs/DEPENDENCY_POLICY.md`: dependency and allowlist posture.
- `schemas/`: validation schemas.
- `goldens/`: versioned reference artifacts.
- `artifacts/`: ephemeral run output (ignored from VCS).
- `scripts/`: automation and gate adapters.
- `tests/control/`: governance control tests.
