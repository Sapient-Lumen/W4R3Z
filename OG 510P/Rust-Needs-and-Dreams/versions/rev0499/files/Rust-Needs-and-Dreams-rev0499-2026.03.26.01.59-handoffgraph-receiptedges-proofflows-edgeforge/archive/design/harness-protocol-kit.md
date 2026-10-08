# Design: Harness Protocol Kit (`cargo harness`, `harness-pack/v0`)

## Goal
Define a reviewable contract for what Rust test and benchmark harnesses can declare to runners and tools **before execution**.

This kit is about the boundary between:
- libtest and future libtest-like harnesses,
- Cargo’s `test` / `bench` UX,
- nextest-style runners,
- nightly custom test frameworks,
- stable ecosystem harnesses such as Criterion/Divan-style lanes,
- doctest consumers,
- and IDE / CI tooling.

It is **not** a new universal runner and **not** a replacement for libtest, nextest, Criterion, Divan, rstest, trybuild, or rustdoc.

## Why now
- The Testing Team RFC says the Rust project needs a more holistic testing story spanning Cargo, libtest, rustdoc, CI, IDEs, and custom frameworks.
  https://rust-lang.github.io/rfcs/3455-t-test.html
- The libtest JSON RFC is already pushing responsibilities from the harness toward the runner and explicitly calls for a future Cargo RFC so custom harnesses can opt into the new protocol.
  https://rust-lang.github.io/rfcs/3558-libtest-json.html
- That RFC also names capabilities that matter to real tools: benches, doctests, test locations, markers, dynamic skipping, parameterization, multiple failures, metrics, and parallel harness execution.
  https://rust-lang.github.io/rfcs/3558-libtest-json.html
- Cargo’s docs say `cargo bench` can drive either libtest or a custom harness, while `#[bench]` remains unstable. That means the stable benchmark story is already ecosystem-composed and would benefit from a portable contract.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- Cargo’s `test` docs say doctest execution details are not guaranteed and may change in the future, which is exactly why doctest posture should be declared through capabilities rather than assumed.
  https://doc.rust-lang.org/cargo/commands/cargo-test.html
- Cargo 1.94 still lists the libtest JSON experiment as unfinished work needing owners.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Core thesis
Rust needs a shared contract for:
1. **subject discovery**,
2. **capability declaration**,
3. **runner-adapter compatibility**,
4. **suite/case/fixture/bench/doctest identity**,
5. and **metric/metadata extensibility**.

That contract should be portable even when the actual execution engine differs.

## What this kit owns
### 1) `harness-capability-report/v0`
Declares what a harness supports and what a consumer may rely on.

Examples:
- subject kinds supported (`test`, `bench`, `doctest`, `suite`, `setup-script`, `fixture`, `generated-case`)
- selection modes (`substring-filter`, `exact-filter`, `marker-filter`, `skip-filter`)
- discovery features (`list`, suite hierarchy, parameterized expansion, location data)
- execution posture (`parallel-in-process`, `process-per-case`, `process-per-binary`, `retry-aware`, `shuffle-capable`)
- result richness (`multiple-failures`, `captured-output`, `timing`, `rng-seed`, bench metrics)
- special lanes (`doctest-aware`, `custom-framework`, `bench-only`, `libtest-compatible`)
- stability class (`stable`, `nightly`, `experimental`, `adapter-import`)

### 2) `harness-discovery-report/v0`
Portable inventory of what the harness exposes.

Examples:
- subject ids and kinds
- suite membership
- parameterized-case expansion or templates
- ignored/disabled posture and reasons
- markers/tags/categories
- source locations when available
- bench subjects and declared metric families
- doctest subjects and hosting/rendering assumptions when relevant

### 3) `harness-adapter-report/v0`
Declares how a runner or tool is interfacing with the harness.

Examples:
- adapter kind (`cargo-test`, `cargo-bench`, `nextest-import`, `ide-import`, `custom`)
- protocol mode (`native`, `json`, `junit-bridge`, `scraped`, `manual`)
- lossiness notes
- unsupported capability list
- translation rules for ids, suites, markers, metrics, or retries

### 4) `harness-pack/v0`
A lightweight attachment bundle containing:
- one capability report,
- one or more discovery reports,
- optional adapter reports,
- raw attachments only when needed.

## What this kit does **not** own
- Final execution result truth → that belongs to [`design/test-run-evidence-kit.md`](./test-run-evidence-kit.md)
- CI matrix identity → [`design/config-set-kit.md`](./config-set-kit.md)
- Coverage semantics → [`design/coverage-evidence-kit.md`](./coverage-evidence-kit.md)
- Benchmark-native result, lane/counter, and baseline-import truth → [`design/benchmark-evidence-kit.md`](./benchmark-evidence-kit.md)
- Benchmark comparison policy → [`design/perf-labs.md`](./perf-labs.md)
- Docs-host or long-form teaching validation → [`design/docproof-kit.md`](./docproof-kit.md)

This kit is upstream of those consumers.

## Reference UX: `cargo harness`
- `cargo harness capabilities`
- `cargo harness discover`
- `cargo harness adapter-report --runner nextest`
- `cargo harness pack`
- `cargo harness verify-pack <path>`

## Example consumers
### Cargo
Use capability and discovery reports to decide when it can provide:
- summary UX,
- `--list`/selection help,
- bench/test shared interaction modes,
- and clearer behavior for custom harnesses.

### nextest
Import stable discovery/capability truth instead of inferring every behavior from libtest conventions alone.

### IDEs/editors
Use location-aware discovery reports for test/bench navigation and run affordances.

### Perf / benchmark tooling
Import benchmark subject identity and declared metric families without pretending benchmark comparison policy belongs in the harness layer.

### Doc tooling
Import doctest subject identity and posture while remaining explicit about what rustdoc-specific behavior may still be unstable or lossy.

## First pilot targets
1. libtest capability + discovery export
2. nextest adapter report
3. custom-framework opt-in shape
4. benchmark subject / metric-family declaration
5. doctest posture import

## Strategic bar
The bar is not “can we invent another runner?”
The bar is “can Rust publish a stable-enough harness contract that runners, IDEs, CI, docs, and benchmark tools can all consume honestly?”
