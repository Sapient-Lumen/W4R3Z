# Frontier salience scan — 2026-03-08 (eighth pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it makes a narrower claim: the archive's Cargo explainability frontier is now strong enough that **P-0035 deserves a sharper place in the stack**, but still *below* the more immediate support-oriented P-0469.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
   - Still the best next incubation target because the user story is immediate and the artifact is the easiest to explain and review.
2. **P-0468 Cargo Resolver Explanation Kit**
   - Still one of the highest-leverage explainability crates because graph-cause questions remain common and poorly packaged.
3. **P-0046 buildscript-ux-kit**
   - Still extremely strong because build-script failures are common, noisy, and not yet packaged into a good support contract.
4. **P-0486 Debuggability Support Contract Kit**
   - Still the strongest non-Cargo support stack center.
5. **P-0035 cargo-build-insights**
   - Rose because Cargo now has enough build-analysis substrate that the missing long-horizon value is clearer: imported session warehousing, regression adjudication, and durable trend artifacts.
6. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Still important, but best kept as the tool-parity layer rather than the historical analytics layer.
7. **P-0059 buildscript-testkit**
8. **P-0058 native-deps-kit**
9. **P-0493 Source Path Hygiene & Debug Source Kit**
10. **P-0491 Debugger Visualizer Compatibility Kit**

## Why P-0035 rose without becoming #1

Two things changed at once:

- Cargo build-analysis and `cargo report` are now real enough to import.
- Cargo's unstable docs note that machine-readable `--timings=json` is gone on 1.94-nightly.

That makes a warehouse/import/diff crate **more distinct** than before.
But it does not make it more urgent than the per-run support artifact in P-0469.

The result is a cleaner stack:

- P-0469 for one incident,
- P-0035 for many sessions,
- P-0468 for graph causes,
- P-0494 for tool/workflow parity.

## What should happen next

The best next Cargo-facing passes should prefer:

1. fixture/schema stubs for **P-0035**,
2. proposal refreshes clarifying what the crate hands other people,
3. more explicit layer boundaries between P-0035 and P-0469,
4. and freshness checks as Cargo's report/session shape evolves.

They should **not** add another generic Cargo build-performance idea unless it is clearly distinct from:

- support bundles,
- historical session warehousing,
- resolver explanation,
- or tool/workflow parity.

## Sources

- Cargo unstable features (`build-analysis`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo tracking issue (`-Zbuild-analysis`): https://github.com/rust-lang/cargo/issues/15844
- Cargo issue (`cargo report` session selection): https://github.com/rust-lang/cargo/issues/16472
- Cargo external-tools JSON: https://doc.rust-lang.org/cargo/reference/external-tools.html
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
