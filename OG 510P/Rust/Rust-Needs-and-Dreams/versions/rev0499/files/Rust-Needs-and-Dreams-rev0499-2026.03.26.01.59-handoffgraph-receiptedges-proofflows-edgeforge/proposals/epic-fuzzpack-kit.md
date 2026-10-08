# Epic Proposal: FuzzPack Kit (`cargo fuzzpack` + `fuzz-pack/v0`)

## One-sentence pitch
Give Rust one portable way to package **fuzz targets, corpora/crashers, persisted property-test regressions, execution-envelope facts, and replay/diff evidence** without forcing `cargo-fuzz`, `honggfuzz`, `test-fuzz`, `proptest`, and `LibAFL` into one fake engine.

## Why this is worthy
Rust’s fuzzing story is now rich enough that the missing contribution is **not** another engine wrapper.
It is the reusable evidence boundary above the engines.

The ecosystem signals line up:
- The Rust Fuzz Book still calls `cargo-fuzz` the recommended tool for fuzz testing Rust code, while being explicit that it is a tool to invoke a fuzzer and currently supports `libFuzzer`.
  https://rust-fuzz.github.io/book/cargo-fuzz.html
- `cargo-fuzz` already has real workflow surface area: workspace posture, `fmt`, `tmin`, `cmin`, and `coverage`. Those are exactly the kinds of intermediate truths that should be made reviewable rather than left as per-engine lore.
  https://docs.rs/crate/cargo-fuzz/latest/source/README.md
- The guide also documents feature-forwarding complexity and `--cfg fuzzing`, which means fuzz execution assumptions already leak into build/runtime behavior.
  https://rust-fuzz.github.io/book/cargo-fuzz/guide.html
- `honggfuzz` documents conditional-compilation and persistent-fuzzing support, proving engine plurality is real.
  https://docs.rs/crate/honggfuzz/latest
- `proptest` has explicit persisted-failure machinery and `std` versus `no_std` behavior, so Rust already has a durable regression lane that is not merely a byte corpus.
  https://docs.rs/proptest/latest/proptest/test_runner/struct.Config.html
  https://docs.rs/proptest/latest/proptest/test_runner/enum.FileFailurePersistence.html
- `test-fuzz` turns ordinary test executions into corpus-generation material and then reuses Rust’s test machinery for fuzzing. That is a major clue that Rust needs an interchange layer across testing and fuzzing, not one more isolated command.
  https://docs.rs/crate/test-fuzz/latest
- `LibAFL` demonstrates a much broader backend/runtime horizon: scalability over cores/machines, adaptable structured inputs, and recent binary-only/QEMU/sanitizer advances.
  https://github.com/AFLplusplus/LibAFL
  https://github.com/AFLplusplus/LibAFL/releases

Together these say the worthy move is a boring replay/review contract, not another “best fuzzer” argument.

## Deliverables
- `cargo fuzzpack` reference companion
- Schemas:
  - `fuzz-target-profile/v0`
  - `fuzz-pack/v0`
  - `fuzz-report/v0`
  - `fuzz-regression-import/v0`
  - `fuzz-pack-diff/v0`
- Adapters/importers for:
  - `cargo-fuzz` / libFuzzer
  - `honggfuzz`
  - `test-fuzz`
  - persisted `proptest` regressions
  - optional `LibAFL`-backed lanes as richer engine imports
- Docs:
  - corpus/crash/replay guide
  - property-regression import guide
  - CI budget + campaign-diff guide
  - coverage/replay attachment guide

## Strategic value
This deserves promotion because it gives Rust a portable answer to questions that recur across security review, CI, maintenance, and archaeology:
- what exact target was fuzzed;
- with what engine family;
- under what toolchain/sanitizer/cfg/runtime envelope;
- what corpus or regression inputs mattered;
- what was minimized or shrunk;
- what campaign evidence exists beyond one crashing file;
- and what changed between two fuzzing review points.

That lets FuzzPack compose upward with the broader Testing Contract Stack instead of staying a loose side lane.

## Reference CLI shape
- `cargo fuzzpack profile`
- `cargo fuzzpack run`
- `cargo fuzzpack pack`
- `cargo fuzzpack replay`
- `cargo fuzzpack diff`
- `cargo fuzzpack import-proptest`
- `cargo fuzzpack import-test-fuzz`
- `cargo fuzzpack verify-pack`

This should stay a **thin importer/packer/orchestrator**.
It should not replace the underlying engines.

## Milestones
1. **v0 replay lane**
   - `fuzz-target-profile/v0` + `fuzz-pack/v0`
   - `cargo-fuzz` importer/exporter
2. **v0.2 campaign lane**
   - `fuzz-report/v0`
   - corpus-growth and new-crasher diffs
3. **v0.3 regression-import lane**
   - `proptest` persisted-failure import
   - `test-fuzz` corpus/regression import
4. **v0.4 richer-engine lane**
   - `honggfuzz` and optional `LibAFL` imports
   - better execution-envelope and replay-attachment capture
5. **v1 testing-stack handoff**
   - bounded imports into run/config/coverage/replay/policy consumers

## Non-goals
- replacing `cargo-fuzz`, `honggfuzz`, `cargo-afl`, `test-fuzz`, `proptest`, or `LibAFL`;
- flattening property-testing regressions, byte corpora, and stateful/structured inputs into one fake universal input model;
- requiring raw sensitive crash inputs to be published by default;
- becoming a hosted fuzzing service or security scorecard.

## Success bar
This becomes worthy when a maintainer can attach one pack or report and another reviewer can honestly answer:
- what was fuzzed,
- what special build/runtime assumptions applied,
- how to replay the result,
- what regression or corpus history mattered,
- and what changed since the last reviewed fuzzing point,

without reverse-engineering CI directories, shell flags, or engine-specific file conventions.
