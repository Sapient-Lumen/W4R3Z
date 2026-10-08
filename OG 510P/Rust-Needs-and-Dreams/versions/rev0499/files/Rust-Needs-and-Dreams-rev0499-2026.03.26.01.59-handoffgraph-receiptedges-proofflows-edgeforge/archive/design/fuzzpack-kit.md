# Design: FuzzPack Kit (`cargo fuzzpack`, `fuzz-pack/v0`)

## Goal
Define a portable contract for **fuzz and generative-test evidence** so Rust teams can share **what target was exercised, with which engine or generator, against which corpus/seeds, under which execution envelope, and how a failure was reproduced or minimized**.

This should **not** replace `cargo fuzz`, `honggfuzz`, `cargo-afl`, `test-fuzz`, `proptest`, or `LibAFL`.
It should make them compose better and leave behind reviewable artifacts.

## References (signals)
- The Rust Fuzz Book still says `cargo-fuzz` is the **recommended tool** for fuzz testing Rust code; `cargo-fuzz` itself says it is a Cargo subcommand for `libFuzzer`, supports workspace fuzz directories, and already exposes `fmt`, `tmin`, `cmin`, and `coverage` commands.
  https://rust-fuzz.github.io/book/cargo-fuzz.html
  https://rust-fuzz.github.io/book/cargo-fuzz/guide.html
  https://docs.rs/crate/cargo-fuzz/latest/source/README.md
- `cargo-fuzz` also documents that every instrumented crate in the fuzz tree is compiled with `--cfg fuzzing`, which makes fuzz-specific behavioral adaptation a real contract surface rather than folklore.
  https://rust-fuzz.github.io/book/cargo-fuzz/guide.html
- `honggfuzz` remains a live alternative lane and documents both conditional-compilation support (`--cfg fuzzing`) and persistent-fuzzing material.
  https://docs.rs/crate/honggfuzz/latest
- `proptest` is not just “random tests”; it has explicit failure-persistence machinery, persisted seeds, and `std` versus `no_std` differences that materially change what regressions survive.
  https://docs.rs/proptest/latest/proptest/test_runner/struct.Config.html
  https://docs.rs/proptest/latest/proptest/test_runner/enum.FileFailurePersistence.html
- `test-fuzz` shows a different but very important lane: it records function arguments during `cargo test` to generate a corpus, then reuses Rust’s test machinery to drive fuzzing. That means ordinary tests and fuzz corpora are already converging in practice.
  https://docs.rs/crate/test-fuzz/latest
- `LibAFL` is now strong evidence that Rust fuzzing is not one-engine-sized: it positions itself as a reusable fuzzer library, highlights scalability across cores and machines, explicit adaptability to structured inputs, and its recent release moved to Rust 2024 while adding binary-only ASan-in-Rust and improved snapshot/QEMU support.
  https://github.com/AFLplusplus/LibAFL
  https://github.com/AFLplusplus/LibAFL/releases

## Working thesis
Rust no longer lacks fuzz engines.
It lacks a **shared evidence contract above them**.

Today, the ecosystem can already produce:
- libFuzzer-style corpora and minimized crashers,
- honggfuzz runs and conditional-compilation adaptations,
- persisted proptest regressions and shrink outcomes,
- `test-fuzz` corpora derived from ordinary tests,
- LibAFL-native execution state and richer backend/runtime assumptions.

What it still cannot do cleanly is answer one boring but vital question:

**What exactly should another maintainer, CI lane, security reviewer, or future assistant receive if they want to replay, inspect, diff, or budget fuzz evidence honestly?**

## Core components

### 1) `fuzz-target-profile/v0`
Declares the target under fuzz or property-driven exploration.

Required ideas:
- subject identity (`workspace`, `package`, `target`, `commit?`, `lockfile_hash?`, `toolchain?`)
- target family (`bytes`, `structured-arbitrary`, `serialized-call`, `state-machine`, `property-regression-import`)
- engine family (`libfuzzer`, `honggfuzz`, `afl`, `libafl`, `proptest-only`, `mixed`)
- target creation lane (`cargo-fuzz`, `honggfuzz`, `test-fuzz`, handwritten, imported)
- required cfg/features/targets/profile/sanitizer posture
- whether `#[cfg(fuzzing)]` or equivalent target-specific adaptations were in play
- whether the target expects corpus files, stdin, serialized arguments, or another input bridge

### 2) `fuzz-pack/v0`
Portable replay package for one concrete regression or reviewed corpus slice.

Should support:
- linked `fuzz-target-profile/v0`
- crashing input bytes or structured/serialized representation
- minimized input if available
- shrink trace or regression-seed import when the source was property testing rather than a coverage-guided engine
- selected corpus subset with stable hashes
- execution envelope:
  - engine/backend version
  - Rust toolchain / target triple
  - sanitizer / instrumentation posture
  - notable environment/cfg/runtime assumptions
- raw artifact pointers (coverage dir, engine-native crash file, runner logs, replay attachment)
- optional redaction and sensitivity notes

### 3) `fuzz-report/v0`
Run-level summary for CI, nightly soaks, or campaign review.

Should record:
- run identity and generator identity
- target(s) exercised
- budget (`time`, `execs`, campaign class)
- status per target (`no-crash`, `crash`, `timeout`, `infra-failed`, `not-provisioned`, `partial`)
- corpus delta summary
- new crashers / regressions discovered
- optional coverage or progress attachments
- imported raw runner artifacts with stability/lossiness notes

### 4) `fuzz-regression-import/v0`
Bridge for non-engine-native regressions.

This exists because `proptest` and `test-fuzz` are important, but they are **not** coverage-guided engines in the same shape.
The import artifact should preserve:
- source lane (`proptest`, `quickcheck-family`, `test-fuzz`, bespoke harness)
- persisted seed / failure-persistence location semantics
- shrink outcome or minimization notes
- serialization assumptions
- exact lossiness when importing into a broader fuzz view

### 5) `fuzz-pack-diff/v0`
Reason-coded comparison between two campaigns or reproducer bundles.

Should highlight:
- target-profile drift
- engine/runtime/toolchain/sanitizer drift
- corpus growth or pruning
- new crashers versus already-known regressions
- replay success/failure changes

### 6) `cargo fuzzpack`
Reference UX:
- `cargo fuzzpack profile`
- `cargo fuzzpack run`
- `cargo fuzzpack pack`
- `cargo fuzzpack replay`
- `cargo fuzzpack diff`
- `cargo fuzzpack import-proptest`
- `cargo fuzzpack import-test-fuzz`

`cargo fuzzpack` should begin as an **orchestrator / importer / packer**.
It should not try to become one universal fuzzer.

## What the kit should provide to others
- **Test Execution Evidence Stack:** attach fuzz and generative-testing evidence to shared run/config subjects without letting fuzz reports redefine harness or run identity.
- **Replay Kit:** import concurrency/schedule replay evidence when a reproducer is not purely input-driven.
- **Coverage Evidence Kit:** attach coverage outputs honestly as imported evidence rather than pretending coverage is the same thing as fuzz truth.
- **Safety Evidence / Trust / Policy consumers:** inspect portable regressions and campaign posture without scraping CI or engine-specific directories.
- **Device Lab / embedded lanes:** preserve target/runtime assumptions instead of flattening embedded or binary-only fuzzing into the same envelope as desktop libFuzzer runs.

## Overlap boundaries
- **Not Test Run Evidence Kit:** that kit owns generic run/result truth. FuzzPack owns corpus/crash/seed/shrink/replay-specific evidence.
- **Not Coverage Evidence Kit:** coverage is an attachment, not the canonical fuzz subject.
- **Not Replay Kit:** replay owns schedule/world reproduction; FuzzPack imports it when needed.
- **Not one engine wrapper:** engine-specific UIs remain valid and should keep their detailed knobs.

## Hard problems (explicitly scoped)
1. **Coverage-guided and property-based lanes are related but not identical**
   - `proptest` regressions, `test-fuzz` corpora, and libFuzzer crashers must not be flattened into one fake input format.
2. **Execution envelopes matter**
   - sanitizer, cfg, target, toolchain, and backend differences can be the difference between “reproduces” and “does not reproduce.”
3. **Sensitive inputs are common**
   - v0 must support omission, hashing, or redacted surrogates without pretending nothing was lost.
4. **Campaign summaries and replay bundles are different artifacts**
   - `fuzz-report/v0` and `fuzz-pack/v0` should stay linked but distinct.
5. **Raw engine artifacts should stay attached, not erased**
   - keep corpora, crash files, logs, and reports as imports where useful rather than normalizing away the details.

## Minimal adoption path
1. Publish schemas for `fuzz-target-profile/v0`, `fuzz-pack/v0`, and `fuzz-report/v0`.
2. Ship `cargo fuzzpack pack` and `cargo fuzzpack replay` first for `cargo-fuzz` targets.
3. Add `honggfuzz` import/export.
4. Add `proptest` and `test-fuzz` regression-import lanes.
5. Add optional coverage/progress/replay attachments and CI diffs.
