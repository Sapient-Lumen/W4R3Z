# Scenario: required-feature bin and default lib are distinct matrix cells

A crate ships a default library target plus a CLI binary guarded by `required-features = ["cli"]`.

The maintainer ran upgrade checks only for the default library lane.
The pack should not flatten that into “the upgrade was checked” for the whole package.
Instead it should publish an explicit sparse matrix showing:

- the default lib cell as observed,
- the `cli` binary cell as `unknown` or `manual_review_required`,
- and the exact capture-context receipt that backs the observed cell.

This keeps target/feature selection exact and prevents default-lane evidence from silently claiming coverage for a gated target.
