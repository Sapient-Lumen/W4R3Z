# Cargo lock contention upstream fit — 2026-03-08

## Main judgment

**P-0490 Cargo Lock Contention Witness Kit** is now a clearer fit to current upstream Rust/Cargo reality than it was when first promoted.

The reason is not that upstream solved contention.
The reason is that upstream now makes the **substrate** unusually explicit:

- rust-analyzer says it can compete with manual Cargo commands over the build lock,
- rust-analyzer documents `cargo.targetDir` as a way to avoid that blocking at the cost of duplicated artifacts,
- Cargo’s build-dir-layout work explicitly says the layout rework is meant to make fine-grained caching and locking easier,
- Cargo’s unstable `build-dir-new-layout` docs repeat that locking/caching motivation,
- and Cargo’s cache-lock internals make package/index cache locking a real coordination mechanism rather than folklore.

That means the missing crate no longer needs to act like it is proving locks exist.
It should instead standardize the **receiver-facing witness bundle** above that substrate.

## What the crate should not try to own

### Not P-0494
**P-0494** is about what a tool-oriented workflow actually built and when it should fall back to a fuller build.
A lock-contention witness should only mention tool-only workflows when they matter as a mitigation choice.

### Not P-0489
**P-0489** is about consumers that still depend on Cargo’s internal build-dir layout.
A lock-contention witness may mention the relevant root, but it should not become a general migration planner for layout changes.

### Not P-0469
**P-0469** is about why work rebuilt.
A lock-contention witness is about why work could not make progress yet.
These often co-occur in complaints, but the receiver-facing artifact should keep them separate.

### Not a scheduler
The proposal should still avoid process killing, queue management, or heavy orchestration.
The value is a compact diagnosis and mitigation bundle, not a daemon that controls everyone’s workflows.

## Strongest current artifact contract

The cleanest 0.1 shape now looks like:

1. one `cache-root.manifest.json`,
2. one `lock-wait.receipt.json`,
3. one `collision-diagnosis.report.json`,
4. one `mitigation.plan.json`,
5. optionally one `process-role.snapshot.json`,
6. and one small `notes.md`.

That is enough to answer:

- which root was involved,
- what kind of wait was observed,
- how strong the evidence was,
- and which trade-off the maintainer should choose next.

## Why this is better than another generic performance crate

The current official substrate already covers too much ground for another vague “Cargo performance helper” to stay crisp.
A worthy crate here should be narrow enough that a maintainer can attach one bundle to an issue and another maintainer can read it without reproducing the live blocking event.

## Best next repo moves

Future passes on this frontier should prefer:

1. scenario bundles for shared-target-dir conflicts, package-cache waits, and mitigated separate-target-dir setups,
2. schema stabilization for wait provenance, confidence, and mitigation trade-offs,
3. conservative diff vocabulary for “got worse / got better / now mitigated”,
4. and explicit redaction rules for paths and process names.

They should not add another generic IDE/Cargo pain proposal unless it is clearly distinct from:

- tool-build parity,
- live lock contention,
- build-dir consumer transition,
- or rebuild causality.

## Sources

- rust-analyzer FAQ: https://rust-analyzer.github.io/book/faq.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Cargo unstable features (`build-dir-new-layout`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- Cargo build-cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo cache-lock internals: https://doc.rust-lang.org/beta/nightly-rustc/cargo/util/cache_lock/index.html
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
