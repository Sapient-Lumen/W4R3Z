# SemVer API Diff Evidence Kit fixtures

This fixture family exists to make **P-0244 SemVer API Diff Evidence Kit** less abstract.

The point is not to replace `cargo-semver-checks`.
The point is to standardize one small **SemVer evidence bundle** another maintainer or tool can review.

## Core bundle files

- `public-api.snapshot.old.json`
- `public-api.snapshot.new.json`
- `api-match.report.json`
- `witness-plan.json`
- `witness-result.json`
- `semver-judgment.report.json`
- `semver.receipt.json`
- optional `semver-waivers.toml`
- `notes.md`

## Scenario families

### `impl_trait_parameter_witness`
Shows a case where a direct syntactic diff is not enough and the bundle must preserve a witness plan and witness result.

### `implied_bound_precision`
Shows a case where implied bounds make naïve syntax-only reasoning unsafe.
The bundle should preserve `manual_review_required` or a precision caveat instead of pretending certainty.

## Design guardrails

- Keep public-API snapshots separate from witness plans.
- Preserve source identity for compared crates explicitly.
- Distinguish rule-derived judgments from witness-derived judgments.
- Prefer short decisive verdicts plus `manual_review_required` over fake certainty.
