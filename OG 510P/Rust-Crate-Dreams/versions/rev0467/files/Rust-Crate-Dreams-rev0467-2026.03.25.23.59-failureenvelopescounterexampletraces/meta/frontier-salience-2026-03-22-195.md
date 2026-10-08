# Frontier salience refresh — 2026-03-22 (195)

## Why P-0433 deserved one more pass

The archive already had decision authority, construct support, independence evidence, caveat basis, and lineage for **P-0433 MC/DC Coverage Workbench Kit**.
The remaining weak point was not runner coverage.
It was **comparison honesty**.

Current official and primary sources make that gap concrete:

1. Rust’s 2026 flagship themes explicitly keep MC/DC on the safety-critical milestone list.
2. The rustc coverage book still requires unstable doctest persistence to include doctest binaries and still documents a known doctest source-line issue.
3. `cargo-llvm-cov` still labels branch/doctest support unstable and documents scope-shaping behavior such as `--target` omitting proc-macro/build-script coverage from display.
4. Nightly rustc source now names `Block`, `Branch`, and `MCDC` coverage modes explicitly.
5. LLVM’s current source-based coverage docs state that raw profiles have no backward or forward compatibility guarantees, coverage mappings are not forward-compatible, and MC/DC instrumentation has hard exclusion limits.
6. Current Rust MC/DC research still shows that Rust constructs such as `?`, pattern matching, and constant-like values need language-aware interpretation.

That makes the sharper missing value here less “more coverage” and more a **support-contract layer for scope, comparison, and qualification truth**.

## Main ranked takeaway

**P-0433 MC/DC Coverage Workbench Kit** remains a worthy lead-lane because it can now offer something other crates still do not:

- a `campaign-scope.receipt` for what was actually exercised,
- a `comparison-basis.receipt` for whether two bundles may be trended together,
- and a `qualification-basis.receipt` for what kind of assurance story the campaign can honestly support.

## Why this beat adjacent ideas this pass

It beat a broader assurance-case pass because the coverage lane still had one unresolved honesty problem before higher-level bundling made sense.

It beat another runner/workflow pass because runners already exist; what is missing is a stable, diffable review contract above them.

It beat a generic test-campaign lane because MC/DC now has unusually concrete official substrate and unusually sharp comparability pitfalls.

## Boundaries to keep sharp

P-0433 should now own:

1. decision authority,
2. construct support,
3. campaign scope,
4. independence-pair evidence,
5. caveat basis,
6. comparison basis,
7. qualification basis,
8. evidence lineage,
9. and drift for MC/DC-facing support bundles.

It should not silently become:

- a generic coverage runner,
- a generic line/region/branch trend tool,
- a full assurance-case framework,
- or a generic test execution warehouse.
