# Unsafe Field Invariant Ledger Kit fixtures

This fixture set makes **P-0460 Unsafe Field Invariant Ledger Kit** concrete.

## First-class artifacts

- `field-authority.receipt.json` — records where an invariant claim came from and who owns it.
- `mutation-lane.report.json` — records which safe/unsafe/generated paths can mutate an invariant-bearing field.
- `trusted-constructor.receipt.json` — records which constructors or reconstitution paths are trusted to establish the invariant.
- `invariant-witness.report.json` — records what tests/Miri/contracts/manual review actually covered and what remained out of scope.
- `field-contract-drift.diff.json` — records what changed across revisions.
- `unsafe-field-bundle.manifest.json` — portable manifest joining the review artifacts.

## Core review question

Can another engineer tell:

1. which fields matter to soundness,
2. who is allowed to mutate them,
3. which constructors are trusted,
4. what evidence actually touched those claims,
5. and how that story changed release-to-release?

If not, the crate still lives in unsafe folklore more than in reviewable contract territory.
