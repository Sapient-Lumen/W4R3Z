# Frontier salience refresh — 2026-03-22 (200)

## Why P-0433 deserved another pass

The archive already had decision authority, construct support, independence evidence, caveat basis, campaign scope, comparison basis, qualification basis, and lineage for **P-0433 MC/DC Coverage Workbench Kit**.
The remaining weak point was no longer basic comparability.
It was **durability and review debt honesty**.

Current official and primary sources make that gap concrete:

1. Rust’s 2026 flagship themes explicitly keep MC/DC on the safety-critical milestone list.
2. The rustc coverage book still requires unstable doctest persistence for doctest binaries and still points at a known doctest line-number issue.
3. The rustc codegen-options book still warns that coverage profile data formats may change and may not work with non-shipped tools.
4. `cargo-llvm-cov` still labels `--mcdc` and doctest support unstable.
5. LLVM’s current coverage/profile docs say raw profiles have no backward or forward compatibility guarantees, while indexed formats are not forward-compatible.
6. Rust’s current branch-coverage limitations issue still leaves `match` arms, or-patterns, `?`, `.await`, and macro-introduced branches unsupported or caveat-heavy.

That makes the sharper missing value here less “more MC/DC evidence” and more a **support-contract layer for profile compatibility, explicit policy, and manual-review debt**.

## Main ranked takeaway

**P-0433 MC/DC Coverage Workbench Kit** remains a worthy lead-lane because it can now offer something adjacent crates still do not:

- a `profile-compatibility.receipt` for whether the retained/merged inputs are safe for the intended claim,
- a `campaign-policy.receipt` for what support bar and exclusions were explicitly chosen,
- and a `manual-review-debt.report` for what still blocks a stronger assurance story.

## Why this beat adjacent ideas this pass

It beat a broader assurance-case pass because the MC/DC lane still had unresolved debt/accounting problems before higher-level claim assembly made sense.

It beat another runner/workflow pass because runners already exist; what is missing is a stable, diffable review contract above them.

It beat a generic trend/history lane because profile durability and unsupported-construct debt still change the meaning of an apparently simple time series.

## Boundaries to keep sharp

P-0433 should now own:

1. decision authority,
2. construct support,
3. campaign scope,
4. independence-pair evidence,
5. caveat basis,
6. comparison basis,
7. qualification basis,
8. profile compatibility,
9. campaign policy,
10. manual-review debt,
11. evidence lineage,
12. and drift for MC/DC-facing support bundles.

It should not silently become:

- a generic coverage runner,
- a generic line/region/branch trend tool,
- a full assurance-case framework,
- or a generic evidence warehouse.
