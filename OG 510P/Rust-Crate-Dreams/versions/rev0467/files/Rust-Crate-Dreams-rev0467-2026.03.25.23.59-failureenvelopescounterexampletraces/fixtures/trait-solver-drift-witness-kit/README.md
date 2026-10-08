# Trait Solver Drift Witness Kit fixtures

This fixture set makes **P-0442 Trait Solver Drift Witness Kit** concrete.

## First-class artifacts

- `comparison-lane.receipt.json` — records which solver lane actually ran.
- `corpus-authority.receipt.json` — records where the case came from and which expectations are authoritative.
- `obligation-class.report.json` — records what class of solver question changed.
- `diagnostic-normalization.receipt.json` — records what normalization happened before a diagnostic-only verdict.
- `minimization-lineage.receipt.json` — records how a reduced repro maps back to the source case.
- `solver-drift.diff.json` — records the conservative change class.
- `solver-support-bundle.manifest.json` — portable manifest joining the review artifacts.

## Core review question

Can another engineer tell:

1. which solver lane actually ran,
2. what kind of obligation changed,
3. whether the drift is semantic or diagnostic,
4. how the diagnostics were normalized,
5. and whether a minimized witness still represents the source corpus faithfully?

If not, the crate still lives in solver folklore more than in reviewable contract territory.
