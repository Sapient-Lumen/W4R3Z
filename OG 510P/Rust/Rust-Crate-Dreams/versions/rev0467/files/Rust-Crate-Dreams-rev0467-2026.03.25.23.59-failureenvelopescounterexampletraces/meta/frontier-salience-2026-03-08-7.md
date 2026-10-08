# Frontier salience scan — 2026-03-08 (seventh pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it sharpens the archive's top Cargo frontier around a newer fact: **Cargo build-analysis is now real enough that the missing crate value begins above it**.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
   - Stronger than before because the crate can now layer on top of `-Zbuild-analysis` and `cargo report` instead of inventing a recorder from scratch.
2. **P-0468 Cargo Resolver Explanation Kit**
   - Still one of the highest-leverage ideas, especially if it shares stable bundle vocabulary with P-0469 rather than acting like an isolated graph product.
3. **P-0046 buildscript-ux-kit**
   - Still extremely strong because build-script failures remain common, noisy, and poorly packaged for support workflows.
4. **P-0486 Debuggability Support Contract Kit**
   - Still the strongest non-Cargo stack center, but this pass gives the edge back to Cargo because upstream build-analysis has recently moved the feasibility frontier.
5. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Still very real, but best understood as a parity/fallback layer that can reuse the same session/receipt vocabulary P-0469 is now sharpening.
6. **P-0059 buildscript-testkit**
7. **P-0058 native-deps-kit**
8. **P-0493 Source Path Hygiene & Debug Source Kit**
9. **P-0491 Debugger Visualizer Compatibility Kit**

## Why P-0469 rose again

The key change is not that rebuild pain suddenly got worse.
The key change is that upstream Cargo now has a more explicit evolving surface for persisted build sessions, rebuild reasons, and timing replay.

That makes P-0469 more attractive because it can now promise another person something very concrete:

- import an actual Cargo session,
- freeze it into a smaller stable bundle,
- classify rebuild causes conservatively,
- and hand that bundle to CI, a reviewer, or a support engineer.

That is a stronger near-term crate contract than a broad “build performance insights” pitch.

## What should happen next

The best next Cargo-facing passes should prefer:

1. build-analysis import schemas and tiny scenario bundles for **P-0469**,
2. shared session / baseline / receipt vocabulary across **P-0469 / P-0468 / P-0494**,
3. proposal-file upgrades clarifying what another person receives,
4. and evidence refreshes as `cargo report` grows or changes.

They should **not** add another generic Cargo performance proposal unless the seam is clearly distinct from:

- rebuild explanation,
- resolver explanation,
- tool-invocation parity,
- or historical build-analysis warehousing.

## Sources

- Cargo unstable features (`build-analysis`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo tracking issue (`-Zbuild-analysis`): https://github.com/rust-lang/cargo/issues/15844
- Cargo issue (`cargo report` session selection): https://github.com/rust-lang/cargo/issues/16472
- Cargo issue (man pages for new `cargo report *` commands): https://github.com/rust-lang/cargo/issues/16488
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
