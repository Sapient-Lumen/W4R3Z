# Safety Contract Consumer Kit fixtures

This fixture set exists to keep “contracts are available” from collapsing into one fake “all consumers used them the same way” story.

The first compact artifacts are now:

- `contract-authority.receipt.json`
- `consumer-coverage.matrix.json`
- `semantic-lane.report.json`
- `contracts-bundle.manifest.json`

The proving-ground scenarios are intentionally small:

1. std-style contract authority plus one Kani profile still does not settle other consumer lanes,
2. `verify-rust-std` accepted-tool plurality does not mean uniform clause coverage,
3. runtime checks, bounded model checking, refinement typing, and separation-logic proofs are distinct semantic lanes,
4. portable bundles must keep authority, coverage, and semantics separate.

Use these fixtures when one contracts snapshot or one green verifier run would otherwise overclaim cross-tool support.
Do not infer uniform semantics from shared clause text alone.
