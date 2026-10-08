# Public API Readiness Bundle Kit fixtures

This fixture pack exists to keep **P-0483 Public API Readiness Bundle Kit** concrete.
It models release-review support for library teams that already have analyzers but still lack one joined public-contract bundle.

## Core review objects

- `public-surface.snapshot.schema.json` — normalized inventory of public items, reexports, deprecations, and evidence origin.
- `semver-verdict.report.schema.json` — imported semver results, witness posture, and uncertainty classes.
- `public-dependency-boundary.report.schema.json` — public/private/ambiguous dependency boundary facts.
- `docs-readiness.report.schema.json` — docs/example readiness narrowed to the public surface.
- `waiver-ledger.receipt.schema.json` — explicit waiver entries with owner, expiry, and blocking/advisory posture.
- `release-readiness.verdict.schema.json` — compact joined release verdict.
- `public-api-readiness.schema.json` — top-level bundle container.

## Fixture families

- `patch_release_accidental_public_dependency_leak/` — patch release that quietly widens the public boundary via a reexported type.
- `minor_release_public_docs_regression/` — semver-compatible expansion whose public docs/examples are no longer good enough.
- `intended_major_break_with_stale_waiver/` — a break that may be acceptable in principle but still fails review because waiver hygiene drifted.

## Working rule

These fixtures should keep the lane conservative.
If a scenario only looks useful by pretending semver, dependency-boundary, docs, and waiver facts can be merged into one popularity or quality score, the lane is drifting away from the release-review artifact the archive is trying to design.
