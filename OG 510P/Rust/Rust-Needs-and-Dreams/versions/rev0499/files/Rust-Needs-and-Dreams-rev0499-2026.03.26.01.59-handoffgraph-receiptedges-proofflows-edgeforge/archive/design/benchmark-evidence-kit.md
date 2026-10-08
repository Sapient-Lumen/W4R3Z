> Revision note (rev0452): read this note now beneath `design/benchmark-evidence-execution-blueprint-2026Q1.md` and keep the kit benchmark-native: the missing layer is portable comparability and handoff truth, not one runner, dashboard, or score.

# Design: Benchmark Evidence Kit (`cargo benchpack`, `benchmark-pack/v0`)

## Goal
Define a portable contract for benchmark-native evidence across Rust harnesses, runners, profiler lanes, and hosted services.

This kit should make it easy to answer:
- what benchmark subject ran,
- what measurement lane and counter semantics applied,
- what baseline or prior run was imported,
- what runner/import path produced the result,
- and what raw benchmark artifacts exist for deeper inspection.

This is **not** another benchmark engine, hosted dashboard, or universal performance-gating layer.
It is the benchmark-native substrate that should sit between:
- [`design/harness-protocol-kit.md`](./harness-protocol-kit.md),
- [`design/test-run-evidence-kit.md`](./test-run-evidence-kit.md),
- and [`design/perf-labs.md`](./perf-labs.md).

Read this together with [`design/benchmark-evidence-lane-map.md`](./benchmark-evidence-lane-map.md), which now defines the lane boundaries the rest of this kit should preserve.

## Why now
- Cargo’s docs still define a plural benchmark surface: libtest or custom harness, with `#[bench]` still unstable.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- nextest’s `cargo nextest bench` is now a real experimental import lane for Criterion.rs, the nightly libtest benchmark runner, and custom test-harness protocol users.
  https://nexte.st/docs/features/benchmarks/
- Criterion still has a native saved-baseline story, while `cargo-criterion` still exports machine-readable JSON but does not support baselines.
  https://bheisler.github.io/criterion.rs/book/user_guide/command_line_options.html
  https://bheisler.github.io/criterion.rs/book/cargo_criterion/cargo_criterion.html
- Divan makes counter semantics explicit instead of burying throughput assumptions in prose.
  https://docs.rs/divan/latest/divan/counter/index.html
- Iai-Callgrind shows that Rust benchmark lanes already span callgrind/cache/heap attachments and CI-oriented deterministic lanes, not just wall-time statistics.
  https://docs.rs/iai-callgrind/latest/iai_callgrind/
- CodSpeed publishes compatibility layers and measurement modes for Rust benchmark crates, proving hosted/imported benchmark plurality is operational rather than hypothetical.
  https://codspeed.io/docs/benchmarks/rust
  https://codspeed.io/docs/reference/codspeed-rust/cargo-codspeed
- rustc-perf’s multiple-collector direction reinforces the need for explicit benchmark lane and collector truth.
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html

## Core thesis
Rust needs a benchmark-native evidence layer that keeps these distinct:
1. benchmark subject identity,
2. measurement-lane and counter semantics,
3. native versus imported baseline posture,
4. runner/import posture,
5. native result data and raw attachments,
6. and downstream compare/gate conclusions.

That layer should be useful even when broader performance policy is still handled elsewhere.

## Artifacts
### `benchmark-subject/v0`
Declares what the benchmarked thing is.

Should support:
- package / workspace member / benchmark target / binary id
- harness family (`libtest-bench`, `criterion`, `cargo-criterion`, `divan`, `iai-callgrind`, `custom`, `hosted-import`)
- suite / group / case / benchmark id
- parameter values or scenario labels
- subject kind (`micro`, `macro`, `binary-scenario`, `compile`, `profiled`, `hosted-case`)

### `benchmark-lane-profile/v0`
Declares the benchmark lane semantics.

Should support:
- lane family (`cargo-bench`, `statistical-baseline`, `counter-throughput`, `runner-import`, `deterministic-profiler`, `hosted-adapter`)
- metric family (`wall-time`, `throughput`, `instructions`, `cache`, `heap`, `simulation`, `memory`, `custom`)
- counter semantics and units when relevant
- engine/tool identity and version
- native baseline capability (`native`, `imported`, `unsupported`, `absent`)
- comparability caveats and unsupported dimensions

Design rule:
- lane identity stays explicit. Criterion native baselines, `cargo-criterion` JSON export, Divan counters, Iai-Callgrind profiler outputs, and CodSpeed hosted modes must not collapse into one generic “benchmark result”.

### `benchmark-run-import/v0`
Records execution imported from another runner or orchestrator.

Should support:
- source runner identity (`cargo`, `nextest`, `hosted-service`, `custom`)
- timeout / setup / wrapper / sharding posture
- imported execution ids or pointers to generic run evidence
- lossiness notes when the imported path cannot preserve all harness-native details

### `benchmark-baseline-import/v0`
Records which baseline the result is compared against.

Should support:
- native harness baseline ids when available
- prior local run imports
- hosted baseline refs
- branch / release / commit anchors
- baseline freshness / staleness / incompatibility reasons
- explicit `unsupported` or `none`

### `benchmark-result-report/v0`
Portable benchmark-native result artifact.

Should support:
- subject ids and lane-profile id
- baseline/import refs
- summary numbers and units
- change statistics or differential summary when native tools expose them
- raw sample/profile/callgrind attachment refs
- reason-coded comparability posture (`comparable`, `advisory`, `not-comparable`)
- optional runner-import refs

### `benchmark-pack/v0`
Bundle for review, CI, and later archaeology.

Should support:
- manifest and schema versions
- one or more `benchmark-subject/v0` records
- one or more `benchmark-lane-profile/v0` records
- optional `benchmark-run-import/v0`
- optional `benchmark-baseline-import/v0`
- one or more `benchmark-result-report/v0`
- checksums / provenance / external attachment refs

## Design principles
- **Lane identity first.** Direct Cargo launch, statistical baseline lanes, counter lanes, deterministic profiler lanes, runner imports, and hosted adapters are related but not interchangeable.
- **Baseline honesty.** Native saved baselines, imported branch baselines, and absent/unsupported baselines must remain distinct.
- **Adapters before reinvention.** The first win is common evidence, not a monolithic new benchmark runner.
- **Metric-family clarity.** Wall-time, throughput, instructions, cache, heap, simulation, and hosted-memory output are not one score.
- **Portable packs, external blobs.** Large traces or profile artifacts should be referenced and hashed without bloating the archive.

## Next credible move
The archive should now treat the ranked rollout in [`design/benchmark-evidence-pilot-program.md`](./benchmark-evidence-pilot-program.md) as the next real step:
- stable local lane pair first,
- runner-import lane second,
- deterministic profiler lane third,
- hosted adapter lane fourth,
- Perf Labs handoff fifth.

The point is to prove lane, baseline, and runner honesty before trying to standardize every performance workflow at once.

## What the kit should provide to others
- **Library authors:** attachable evidence for performance claims and regressions.
- **Application teams:** one place to define benchmark subjects and preserve how they were measured.
- **CI and hosted benchmark services:** a common import/report format instead of bespoke JSON and screenshots.
- **Tool authors:** a shared schema for publishing results from existing harnesses and adapters.
- **Reviewers:** explicit answers to “what ran?”, “how was it measured?”, “what was it compared against?”, and “what is actually comparable?”

## Integration points
- **Harness Protocol Kit** for capability/discovery truth before benchmark execution.
- **Test Run Evidence Kit** for generic runner/harness execution truth when a benchmark run is imported.
- **Perf Labs** for broader compare/gate policy above benchmark-native semantics.
- **Coverage Evidence Kit / Sanitizer Battery Kit / Device Lab Kit** when benchmark subjects depend on explicit specialized execution lanes.
- **Config Set Kit** when a bounded matrix id must be attached to a benchmark claim.

## Hard problems (explicitly scoped)
1. **Baseline lifecycle**
   - native, imported, hosted, and unsupported baselines should remain distinct.
2. **Runner lossiness**
   - nextest or hosted orchestration may not preserve all harness-native details.
3. **Engine comparability**
   - Criterion, Divan, Iai-Callgrind, and hosted adapters are not mutually substitutable.
4. **Storage and privacy**
   - traces and profiler outputs can be large or sensitive; packs should support redaction and external references.
5. **Metric gaming**
   - downstream gates should be explainable and overrideable, not silently optimized around one simplistic threshold.

## Overlap boundaries
- **Not Harness Protocol Kit:** harness discovery and capability negotiation stay there.
- **Not Test Run Evidence Kit:** generic execution/run truth stays there.
- **Not Perf Labs:** broader compare/gate workloads and policy stay there.
- **Not one benchmark engine:** this kit imports current engines rather than replacing them.
- **Not one global score:** the design must resist collapsing unlike lanes into a single benchmark number.
