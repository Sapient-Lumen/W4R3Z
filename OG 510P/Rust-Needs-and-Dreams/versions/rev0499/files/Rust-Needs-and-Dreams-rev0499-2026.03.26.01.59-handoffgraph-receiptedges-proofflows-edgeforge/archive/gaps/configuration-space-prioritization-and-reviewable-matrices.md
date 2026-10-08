# Gap: configuration-space prioritization and reviewable matrices

## What is missing
Rust projects increasingly live in a large configuration space rather than one canonical build.
That space spans:
- Cargo features and optional dependencies,
- `cfg(...)` conditionals and custom cfg values,
- target triples and target-specific docs/build behavior,
- profiles/toolchains,
- and command lanes such as `check`, `test`, docs, coverage, fuzzing, or verification.

The ecosystem has useful point tools for pieces of this problem, but no shared way to answer one basic question:
**which configurations did we choose to run, why these ones, and what evidence came back from them?**

Sources:
- https://docs.rs/crate/cargo-hack/latest
- https://github.com/taiki-e/cargo-hack
- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://blog.rust-lang.org/2024/05/06/check-cfg/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rust-forge/release/platform-support.html

## The current seam is awkward
Today, serious Rust teams often stitch together ad hoc matrices from:
- `cargo-hack` feature powersets / grouped features / skips,
- hand-maintained GitHub Actions matrices,
- target lists chosen partly for docs.rs defaults or platform tiers,
- `check-cfg` validation,
- and separate machine-readable outputs from test or coverage tools.

That works, but only locally and only if maintainers remember the reasoning.
`cargo-hack` is excellent at enumeration and CI-oriented workarounds, but it is not a durable explanation layer.
Cargo’s own docs are also explicit that `cargo metadata` cannot fully represent feature relationships across dependency kinds, commands, and selected targets under the newer resolver behavior.
That means there is no single blessed “just inspect metadata and you know the real matrix” answer today.

Sources:
- https://github.com/taiki-e/cargo-hack
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html

## Why this matters
This gap is larger than CI convenience.
It affects:
1. **testing quality** — bugs hide in feature/cfg/target interactions that default-only CI misses;
2. **coverage honesty** — a coverage number without the tested configuration set is easy to overread;
3. **verification/fuzzing economics** — bounded, reviewable configuration selection is how expensive assurance work becomes tractable;
4. **cross-platform claims** — docs.rs target choices, platform tiers, and target-specific cfg behavior make target selection a real product claim;
5. **change review** — when the chosen matrix changes, that should be a diffable engineering decision rather than a silent YAML edit.

Recent signals make this especially timely.
RustyEx shows compiler-guided ranking and bounded configuration generation are now concrete enough to discuss seriously.
Cargo is also moving toward richer report surfaces (`cargo report timings`, `cargo report rebuild`, `cargo report sessions`), while nextest and cargo-llvm-cov already emit machine-readable outputs that could attach to per-configuration runs.

Sources:
- https://arxiv.org/abs/2601.16008
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- https://nexte.st/docs/machine-readable/list/
- https://docs.rs/crate/cargo-llvm-cov/latest
- https://docs.rs/crate/nextest-metadata/latest

## What “good” looks like
A worthy contribution here is not “test every combination forever” and not “replace Cargo’s resolver”.
It is a shared selection-and-evidence layer:
- one `config-set/v0` that records the bounded configuration matrix to run;
- one `config-analysis-report/v0` that explains why those configs were chosen and which space remains uncovered;
- one `config-run-report/v0` that maps configuration ids to build/test/coverage/fuzz/verify outcomes and attachments;
- and one `config-pack/v0` bundle for CI, release review, audits, or design discussions.

That would let Feature Kit, Coverage Evidence Kit, FuzzPack Kit, Formal Verification Kit, Public API Kit, Cross Toolchain Kit, and Downstream Testing Kit all consume the same explicit matrix subject instead of each inventing a new one.
