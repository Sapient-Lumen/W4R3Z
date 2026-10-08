# Gap: fuzzing + generative-testing evidence and replay contracts

## What is missing
Rust already has **multiple credible fuzzing and generative-testing lanes**, but it still lacks one shared way to answer:

**What exact target was exercised, under what engine/configuration, with what corpus or persisted regression inputs, and how should another machine or reviewer replay and compare the result?**

This is not a small ergonomic detail anymore.
It is the difference between “we fuzz this crate” as folklore and “here is the exact reviewed evidence bundle” as an ecosystem contract.

## The ecosystem is now strong enough that the missing seam is above the engines
Current signals are unusually clear:
- The Rust Fuzz Book still says `cargo-fuzz` is the recommended tool for fuzz testing Rust code. It also documents that `cargo-fuzz` currently supports `libFuzzer`, that feature forwarding is a real concern, and that fuzzed crates are compiled with `--cfg fuzzing`.
  https://rust-fuzz.github.io/book/cargo-fuzz.html
  https://rust-fuzz.github.io/book/cargo-fuzz/guide.html
- `cargo-fuzz` itself already supports workspace integration plus `fmt`, `tmin`, `cmin`, and `coverage`. That means Rust already has target creation, minimization, and coverage sidecars — just not one reusable review bundle above them.
  https://docs.rs/crate/cargo-fuzz/latest/source/README.md
- `honggfuzz` remains a real alternative lane and exposes its own conditional-compilation and persistent-fuzzing story.
  https://docs.rs/crate/honggfuzz/latest
- `proptest` has explicit failure-persistence behavior, persisted seeds, and `std` versus `no_std` differences. That means Rust already has a durable regression-input lane that is not reducible to libFuzzer-style byte corpora.
  https://docs.rs/proptest/latest/proptest/test_runner/struct.Config.html
  https://docs.rs/proptest/latest/proptest/test_runner/enum.FileFailurePersistence.html
- `test-fuzz` can generate a fuzz corpus from ordinary `cargo test` execution and then fuzz the same target, which is powerful evidence that Rust’s “test” and “fuzz” worlds are already overlapping in practice.
  https://docs.rs/crate/test-fuzz/latest
- `LibAFL` is strong proof that Rust fuzzing is no longer one-engine-sized: it emphasizes scalability across cores and machines, adaptability to structured inputs, and recent work like Rust-implemented binary-only ASan and improved snapshots/QEMU support.
  https://github.com/AFLplusplus/LibAFL
  https://github.com/AFLplusplus/LibAFL/releases

## Why the current seam is awkward
Today, reproducer truth is fragmented across:
- engine-specific corpus directories,
- minimized crash files,
- ad hoc CI artifacts,
- property-test regression files,
- `#[cfg(fuzzing)]` assumptions hidden in source,
- target/toolchain/sanitizer settings hidden in shell history,
- and optional coverage or replay evidence that may or may not have been saved.

That fragmentation makes several common tasks much harder than they should be:
1. **cross-machine reproduction** — another maintainer often lacks the exact engine/toolchain/sanitizer/cfg envelope;
2. **campaign review** — a nightly fuzzing run and one minimized crasher are different artifacts, but teams often mix them together;
3. **engine plurality** — libFuzzer, honggfuzz, AFL-derived lanes, LibAFL, and property-testing regressions are real but non-equivalent;
4. **CI policy** — budgets, corpus growth, and “known regression replay” tend to live in bespoke scripts;
5. **assistant/archaeology use** — future tools can only see whatever happened to survive in issue text or release notes.

## What “good” looks like
A worthy contribution here is not another engine and not a universal dashboard.
It is a shared evidence layer:
- one `fuzz-target-profile/v0` describing the target, engine family, and execution assumptions;
- one `fuzz-pack/v0` for a replayable regression or reviewed corpus slice;
- one `fuzz-report/v0` for campaign summaries;
- one `fuzz-regression-import/v0` for persisted `proptest` or `test-fuzz` regressions;
- and one `fuzz-pack-diff/v0` for comparing campaigns or reproducers over time.

That would let Rust keep engine diversity **and** still gain a boring replay/review contract.

## Why this counts as a worthy contribution
The bar here is high enough to matter:
- security and safety work can import exact reproducers instead of screenshots and shell snippets;
- CI can compare corpus/crash/regression drift explicitly;
- property testing and coverage-guided fuzzing can be linked without being falsely equated;
- embedded/binary-only/structured-input fuzzing lanes can record what made them special;
- and future release/support/incident workflows can import concrete evidence instead of relying on maintainers’ memory.

The result would be a thin `cargo fuzzpack` / `fuzz-pack/v0` layer above existing engines and test integrations, not a replacement for them.
