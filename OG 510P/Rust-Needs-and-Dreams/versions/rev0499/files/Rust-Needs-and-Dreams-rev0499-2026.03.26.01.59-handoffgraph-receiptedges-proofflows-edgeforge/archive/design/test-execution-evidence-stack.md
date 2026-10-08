# Design: Test Execution Evidence Stack

## Goal
Turn Rust’s growing set of machine-readable testing lanes into one composable execution stack instead of a pile of adjacent point tools.

The stack is:
- [`design/harness-protocol-kit.md`](./harness-protocol-kit.md) for harness capability, discovery, suite/case shape, and runner-adapter truth
- [`design/test-run-evidence-kit.md`](./test-run-evidence-kit.md) for run profiles, result truth, recording imports, and attachments
- [`design/config-set-kit.md`](./config-set-kit.md) for bounded matrix selection and config ids
- [`design/benchmark-evidence-kit.md`](./benchmark-evidence-kit.md) for benchmark-native result, lane, and baseline-import truth
- [`design/coverage-evidence-kit.md`](./coverage-evidence-kit.md) for coverage semantics and gating
- [`design/fuzzpack-kit.md`](./fuzzpack-kit.md) for corpus/crash evidence
- [`design/replay-kit.md`](./replay-kit.md) for replayable async/concurrency failures
- [`design/downstream-testing-kit.md`](./downstream-testing-kit.md) for reverse-dependency selection and reporting
- [`design/device-lab-kit.md`](./device-lab-kit.md) for hardware-backed execution lanes

This is **not** a claim that all of these should become one tool.
It is a claim that they now need one shared execution/evidence posture.

## Why this needs synthesis now
The archive already had strong testing ideas, but current Rust signals make the missing shared layer much clearer:
1. **Better test tooling is now explicit project-roadmap terrain.** Rust’s 2026 flagships put “better test tooling” under **Building blocks**, which means the project now openly treats test infrastructure as foundational work rather than runner polish.  
   https://rust-lang.github.io/rust-project-goals/2026/flagships.html
2. **Upstream still wants programmatic default-harness output and more Cargo-owned reporting.** The 2025H2 libtest-JSON goal says libtest is the default harness for Cargo projects, says people rely on programmatic output, and points toward reporting shifting from harnesses to Cargo, more powerful custom runners, and lower-friction custom harnesses. Cargo 1.94 still lists finishing that experiment as a live area needing owners.  
   https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html  
   https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
3. **Rust’s native testing surface is still plural and partly unstable.** `cargo test` still mixes libtest, `rustdoc` doctests, and `harness = false` custom flows, while warning that doctest execution details are not guaranteed and may change. The rustc tests book still says `--format json` is unstable, and benches plus custom test frameworks remain nightly/experimental.  
   https://doc.rust-lang.org/cargo/commands/cargo-test.html  
   https://doc.rust-lang.org/rustc/tests/index.html
4. **The strongest external runner already behaves like infrastructure, not just a prettier CLI.** nextest now documents machine-readable test and binary lists, JUnit output, experimental libtest-like JSON, and persistent run recordings that store full event streams, captured outputs, and workspace metadata. That raises the value of explicit import boundaries rather than trying to flatten nextest-native artifacts into a fake universal test report.  
   https://nexte.st/docs/machine-readable/  
   https://nexte.st/docs/design/architecture/recording-runs/
5. **Runner-native output still does not solve the shared boundary by itself.** Cargo’s external-tools docs say `--message-format=json` only controls Cargo and rustc output, not arbitrary tool output. nextest now forwards Cargo message formats, but its own machine-readable docs still say first-class newline-delimited JSON test-run output and detected configuration are future work.  
   https://doc.rust-lang.org/cargo/reference/external-tools.html  
   https://nexte.st/docs/running/  
   https://nexte.st/docs/machine-readable/

## Working thesis
A serious contribution here should make it easy to answer:
- what harness subjects existed,
- which capabilities and adapter assumptions applied,
- which runner semantics applied,
- which config ids were exercised,
- what actually happened,
- which raw runner-native recordings were imported,
- which specialized evidence attached,
- which outcomes were flaky or infra-shaped,
- and which downstream consumers are entitled to conclude what.

## Stack roles
### 1) Harness Protocol Kit
Owns:
- harness capability declarations
- subject discovery
- suite/case hierarchy
- benchmark/doctest posture
- runner-adapter compatibility reports

This is the harness contract substrate.

### 2) Test Run Evidence Kit
Owns:
- subject ids for concrete runs
- run profiles
- test result reports
- runner-recording imports
- flake observations
- attachment indexes

This is the execution substrate.

### 3) Config Set Kit
Owns:
- bounded matrix choice
- config ids
- selection rationale
- skipped-space truth

This is the matrix substrate.

### 4) Benchmark Evidence Kit
Owns:
- benchmark-native subjects
- measurement-lane and counter semantics
- runner/import posture for benchmarks
- baseline-import truth
- native result and attachment lineage

This is the benchmark-specific substrate that should bridge testing execution and broader performance review.

### 5) Coverage Evidence Kit
Owns:
- criterion semantics
- merged coverage reports
- coverage gates

This is a major consumer of the execution substrate, not a replacement for it.

### 6) FuzzPack / Replay / Device Lab
Own:
- specialized evidence families for crash reproduction, schedule replay, and hardware-backed runs

These are attachment-rich testing lanes that should keep their semantics but reuse run/config truth where possible.

### 7) Downstream Testing Kit
Owns:
- selection of dependent packages and cross-project plans

This is the ecosystem-scale consumer of the stack.

## Strategic rule
The archive should now prefer **harness truth first, execution truth second, imported runner-native recordings third, specialized evidence fourth**.
That means:
- do not invent a generic dashboard before stable harness and run packs exist;
- do not let run reports silently take over capability/discovery questions that belong to harness contracts;
- do not let nextest recordings, JUnit exports, or libtest-like JSON become the de facto canonical format for every consumer;
- do not let coverage or mutation tools silently redefine test identity;
- and do not flatten Miri, hardware labs, replay, or fuzzing into one fake “test run” story.

## Next credible move
The next real step is the ranked rollout in [`design/test-execution-pilot-program.md`](./test-execution-pilot-program.md) plus the stack-level proposal [`proposals/epic-test-execution-evidence-stack.md`](../proposals/epic-test-execution-evidence-stack.md):
- harness capability/discovery truth first,
- default-harness/nextest run truth second,
- config-bound CI lane third,
- coverage + Miri attachment lane fourth,
- replay/fuzz/mutation consumers after that,
- downstream/device-lab consumers after that.
