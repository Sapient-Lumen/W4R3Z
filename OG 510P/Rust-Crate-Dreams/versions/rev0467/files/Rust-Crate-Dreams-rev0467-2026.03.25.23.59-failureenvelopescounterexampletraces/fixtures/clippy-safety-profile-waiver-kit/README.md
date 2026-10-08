# Clippy Safety Profile & Waiver Kit fixtures

This fixture set makes **P-0459 Clippy Safety Profile & Waiver Kit** concrete.

## First-class artifacts

- `policy-authority.receipt.json` — records where each effective lint level came from.
- `checked-scope.matrix.json` — records what packages / targets / features / test/private scopes were actually checked.
- `diagnostic-channel.receipt.json` — records whether findings came from stable rustc/Clippy or nightly Cargo linting.
- `waiver-decision.record.json` — records explicit exception decisions with owner and expiry.
- `lint-policy-drift.diff.json` — records what changed across revisions.
- `lint-support-bundle.manifest.json` — portable manifest joining the review artifacts.

## Core review question

Can another engineer tell:

1. which policy was intended,
2. where the effective levels came from,
3. what scope was actually checked,
4. which channels produced the findings,
5. and what changed release-to-release?

If not, the crate still lives in lint folklore more than in reviewable contract territory.
