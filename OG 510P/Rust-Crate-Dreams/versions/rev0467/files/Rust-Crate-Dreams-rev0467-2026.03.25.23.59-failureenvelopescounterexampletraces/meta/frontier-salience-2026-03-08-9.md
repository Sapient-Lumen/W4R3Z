# Frontier salience scan — 2026-03-08 (ninth pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it upgrades the archive’s reading of **P-0494 Cargo Compile-Time-Deps Workflow Kit**.
The proposal is now more concrete because the current official substrate is no longer just one unstable Cargo flag; it is a **whole documented workflow boundary** spanning Cargo policy, rust-analyzer command/config knobs, and Cargo’s build-dir-layout direction.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
   - Still the best next incubation target because the user story is immediate and the receiver-facing artifact is very easy to explain.
2. **P-0468 Cargo Resolver Explanation Kit**
   - Still one of the highest-leverage Cargo-facing ideas because feature/version/duplicate-build causes remain under-packaged.
3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Rose because current docs now make the tool/build boundary unusually explicit, and the crate can now promise a very concrete receiver-facing bundle.
4. **P-0046 buildscript-ux-kit**
   - Still exceptionally strong because build-script failure explanation remains noisy and underserved.
5. **P-0486 Debuggability Support Contract Kit**
   - Still the strongest non-Cargo support stack center.
6. **P-0035 cargo-build-insights**
   - Still important, but more warehouse-like and therefore slightly less immediate than a single support or parity artifact.
7. **P-0490 Cargo Lock Contention Witness Kit**
   - Strong and practical, but best kept distinct from parity/fallback and rebuild explanation.
8. **P-0059 buildscript-testkit**
9. **P-0058 native-deps-kit**
10. **P-0489 Cargo Build-Dir Consumer Transition Kit**

## Why P-0494 rose

Three current facts matter here:

- Cargo explicitly documents `--compile-time-deps` as a permanently unstable tool-oriented surface.
- rust-analyzer documents the command/config surface it uses for build scripts, checks, targets, sysroot source, and target dirs.
- Cargo’s build-dir-layout goal explicitly names rust-analyzer/Cargo contention and shared-cache pain as motivation.

That means **P-0494** is no longer just “some editor workflow idea.”
It is a more precise crate contract:

- one tool-build receipt,
- one compile-surface manifest,
- one parity report,
- and one fallback plan another person can actually review.

## What should happen next

The best next passes on this frontier should prefer:

1. more fixture/schema stubs for **P-0494**,
2. shared vocabulary across **P-0494 / P-0490 / P-0489**,
3. proposal refreshes that sharpen what the crate hands to another person,
4. and freshness checks as Cargo and rust-analyzer evolve.

They should **not** add another generic Cargo IDE/tooling proposal unless it is clearly distinct from:

- rebuild explanation,
- resolver explanation,
- tool-workflow parity,
- lock contention,
- or build-dir consumer transition.

## Sources

- Cargo unstable features (`compile-time-deps`): https://doc.rust-lang.org/cargo/reference/unstable.html#compile-time-deps
- RFC 3477 (`cargo check` policy): https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo metadata docs: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
