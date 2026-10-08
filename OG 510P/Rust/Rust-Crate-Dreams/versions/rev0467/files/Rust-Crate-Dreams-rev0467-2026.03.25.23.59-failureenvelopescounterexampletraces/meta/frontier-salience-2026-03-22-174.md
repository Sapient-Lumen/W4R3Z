# Frontier salience refresh — 2026-03-22 (174)

## Why P-0433 rose again

The archive already had an MC/DC proposal, but current official Rust sources make the sharper missing value clearer.

What changed is not only that MC/DC appears in safety-critical conversations.
It is that the Rust 2026 flagship themes now explicitly list **implement MC/DC coverage support** as a milestone, while the current coverage substrate still exposes real seams:

1. rustc source-based coverage is real and documented via `-C instrument-coverage`;
2. detailed mode selection still routes through unstable `-Z coverage-options`;
3. `cargo-llvm-cov` already exposes unstable `--branch` and `--mcdc` switches;
4. Rust’s own branch-coverage limitations issue still lists unsupported or caveat-heavy construct classes such as match arms, or-patterns, `?`, `.await`, and macro-generated branches.

That makes the missing crate here less “another coverage wrapper” and more a **support-contract layer for MC/DC evidence**.

## Main ranked takeaway

**P-0433 MC/DC Coverage Workbench Kit** now deserves a full artifact-rich lane because it can offer something other crates do not:

- a decision-authority receipt for what decision inventory was actually in scope,
- a construct-support matrix for which branch forms were supported or not,
- an independence-pair report for each condition,
- a caveat-basis receipt for unstable/toolchain/known-limitation posture,
- and an evidence-lineage receipt for how verdicts map back to concrete runs.

## Why this beat adjacent ideas this pass

It beat another future-incompat or public-dependency pass because those lanes are already much farther along in the archive’s artifact style.

It beat a generic coverage dashboard pass because the real gap is not visualization; it is **support honesty**.

It beat a broader assurance-case pass because MC/DC now has unusually concrete official substrate and unusually sharp review objects.

## Boundaries to keep sharp

P-0433 should own:

1. decision authority,
2. construct support,
3. independence-pair evidence,
4. caveat basis,
5. evidence lineage,
6. and drift for MC/DC-facing support bundles.

It should not silently become:

- a generic coverage runner,
- a line/branch/region dashboard,
- a full assurance-case framework,
- or a generic test execution warehouse.
