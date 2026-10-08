# Cargo SBOM precursor product plan — 2026-03-23

This note sharpens **P-0125 Cargo SBOM Precursor Workbench Kit** into a more implementation-ready next pass.

## Main judgment

A worthwhile `0.2` should not jump straight to bigger format coverage or policy engines.
It should make three boring answers reviewable:

1. **how did we capture this precursor evidence?**
2. **which artifacts were actually eligible and observed?**
3. **where does the strongest honest claim stop?**

## What the crate should provide other people

For release engineers, security reviewers, downstream integrators, and SBOM-tool authors, the crate should now provide:

1. **one capture-route receipt** instead of guessing whether files came from a direct build or a copied/exported tree,
2. **one artifact-coverage report** instead of treating every missing sidecar as equal,
3. **one coverage-ceiling report** instead of overclaiming same-invocation completeness,
4. **one portable workbench bundle** that joins route, coverage, normalization, transform, and diff artifacts,
5. **one conservative vocabulary** that other tools can build on.

## Four first-class artifacts for the next implementation slice

### 1. `capture-route.receipt.json`
Minimum fields:
- `capture_mode`
- `same_invocation_claim`
- `discovery_sources`
- `freshness_visibility`
- `notes`

### 2. `artifact-coverage.report.json`
Minimum fields per artifact:
- `artifact_label`
- `target_kind`
- `crate_types`
- `precursor_eligibility`
- `observation_status`
- `association_basis`
- `fresh`
- `notes`

### 3. `coverage-ceiling.report.json`
Minimum fields:
- `limit_kind`
- `severity`
- `summary`
- `affected_artifacts`
- `manual_review_required`

### 4. `sbom-workbench-bundle.manifest.json`
Minimum fields:
- `declared_artifacts`
- `coverage_artifacts`
- `transform_artifacts`
- `share_posture`
- `manual_review_gaps`

## Recommended command posture

### `cargo sbom-workbench capture`
Should emit:
- existing capture lock / ingest report / normalized graph,
- `capture-route.receipt.json`,
- `artifact-coverage.report.json`,
- optional `coverage-ceiling.report.json`,
- and a bundle manifest.

### `cargo sbom-workbench verify`
Should check:
- direct-capture routes outrank scans,
- imported-tree claims are fenced correctly,
- eligible-but-missing outputs are distinguished from out-of-scope outputs,
- and manual-review gaps remain visible.

### `cargo sbom-workbench diff`
Should compare:
- route changes,
- eligibility/coverage changes,
- and ceiling changes,
- separately from normalized graph churn.

## Preferred proving grounds

1. A binary crate captured directly from one nightly invocation.
2. An `rlib`-only lane that should stay out of precursor scope.
3. An imported `--artifact-dir` export that cannot prove same-invocation generation.
4. A mixed build where `compiler-artifact` reports `fresh = true` for reused outputs.

## Non-goals

- not CycloneDX/SPDX feature expansion by itself,
- not publish attestation,
- not distro packaging policy,
- not general sidecar shipping policy.

## Sources

- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
