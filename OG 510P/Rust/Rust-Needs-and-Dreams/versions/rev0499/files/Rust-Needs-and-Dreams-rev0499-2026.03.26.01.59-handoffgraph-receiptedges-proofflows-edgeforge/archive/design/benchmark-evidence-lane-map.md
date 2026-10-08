# Design: Benchmark Evidence lane map (cargo-bench foundations, statistical baselines, counter lanes, runner imports, deterministic profiler lanes, and hosted adapters)

## Goal
Sharpen **Benchmark Evidence Kit** so the archive stops treating “benchmark support” as one bucket.
Rust benchmarking already spans materially different lanes, and they differ in **how the subject is named**, **which engine or harness is authoritative**, **what kind of measurement is being reported**, **how baselines behave**, **which runner/import path was involved**, and **what later performance consumers may honestly conclude**.

The archive should therefore keep benchmark review grounded in a lane map instead of one flattened “perf number”.

## Signals from the current ecosystem
- Cargo’s own benchmark docs still keep the foundation plural: `cargo bench` can use the default libtest benchmark runner, `#[bench]` is still unstable/nightly-only, and targets can disable the libtest harness and provide their own `main`.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- nextest’s current benchmark docs still describe `cargo nextest bench` as an experimental benchmark-running lane that supports Criterion.rs, the nightly libtest benchmark runner, and custom harnesses following the custom test-harness protocol.
  https://nexte.st/docs/features/benchmarks/
- Criterion’s user guide still documents named baselines through `--save-baseline` and `--baseline`, while the `cargo-criterion` docs still say the Cargo extension exposes machine-readable JSON but does **not** currently support baselines.
  https://bheisler.github.io/criterion.rs/book/user_guide/command_line_options.html
  https://bheisler.github.io/criterion.rs/book/cargo_criterion/cargo_criterion.html
- Divan keeps throughput/counter semantics explicit through `BytesCount`, `CharsCount`, `CyclesCount`, and `ItemsCount` rather than burying them in prose.
  https://docs.rs/divan/latest/divan/counter/index.html
- Iai-Callgrind explicitly positions itself as a benchmark framework/harness using Valgrind Callgrind for extremely accurate and consistent measurements suitable for CI, while also allowing Cachegrind and DHAT-style lanes.
  https://docs.rs/iai-callgrind/latest/iai_callgrind/
- CodSpeed’s Rust docs keep hosted adapter plurality explicit: supported compatibility layers include Divan, Criterion.rs, and bencher/libtest, while `cargo-codspeed` exposes distinct `simulation`, `walltime`, and `memory` measurement modes.
  https://codspeed.io/docs/benchmarks/rust
  https://codspeed.io/docs/reference/codspeed-rust/cargo-codspeed
- rustc-perf’s project goals still emphasize multiple collectors with comparison **within** a given configuration rather than across configurations. That is an important design lesson for general benchmark evidence too.
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html

## The lanes

### 1) Cargo-bench foundation lane (nightly libtest or custom harness)
This is the lowest common benchmark-launch lane Rust itself exposes.

What defines it:
- `cargo bench` as the launcher
- nightly libtest benchmark support or a custom harness behind `harness = false`
- target/workspace selection from Cargo
- benchmark binary identity and filter arguments
- minimal baseline semantics unless the harness adds them

Why it deserves its own lane:
- Cargo already says the built-in `#[bench]` surface is unstable
- custom harnesses are part of the real benchmark story, not a weird edge case
- this lane is often the path local or CI tooling sees first, even when richer semantics live deeper in the harness

Design rule:
- keep Cargo launch truth separate from the richer measurement semantics of Criterion, Divan, Iai-Callgrind, or hosted adapters

### 2) Statistical baseline lane (Criterion native)
This is the lane for statistics-driven microbenchmarking with named baselines.

What defines it:
- Criterion-native benchmark ids, groups, and statistics
- saved or compared named baselines
- local benchmark result directories
- statistical confidence/change estimates
- wall-time-focused interpretation unless counters/profile imports say otherwise

Why it deserves its own lane:
- Criterion’s native baseline story is real and useful
- a Criterion baseline is not the same thing as a generic prior run in some other system
- this lane answers “what changed relative to a saved reference set?” in a way other lanes often do not

Design rule:
- keep Criterion-native baselines separate from generic branch comparisons or hosted service baselines

### 3) Counter / throughput lane (Divan and similar)
This is the lane where benchmarks are explicitly about processed work units, not just elapsed time.

What defines it:
- counters such as bytes, chars, cycles, or items
- throughput-oriented review
- type-generic or parameterized benchmark families
- benchmark outputs whose meaning depends on declared counter semantics

Why it deserves its own lane:
- counter-bearing results answer a different question than “this function took X ns”
- Divan makes those counters explicit today
- if this lane is flattened into ordinary wall-time, downstream performance consumers lose the meaning of the measurement

Design rule:
- keep counter semantics separate from summary timings and separate from hosted adapter modes

### 4) Runner-import lane (`cargo nextest bench` and equivalent)
This is the lane where benchmark execution is imported through a runner rather than the harness’s default execution path.

What defines it:
- runner-managed setup, wrappers, timeouts, and sharding
- imported execution semantics from nextest
- compatibility with Criterion, nightly libtest benchmarks, or custom-harness protocol users
- explicit lossiness if runner output omits harness-native detail

Why it deserves its own lane:
- nextest itself documents benchmark running as experimental
- runner import is strategically valuable, but it is not transparent
- benchmark review should preserve what changed because a runner got involved

Design rule:
- keep runner/import truth separate from benchmark-native subject/lane/baseline truth

### 5) Deterministic profiler lane (Iai-Callgrind / Cachegrind / DHAT family)
This is the lane for deterministic or near-deterministic measurements driven by profiler tooling rather than ordinary timer statistics.

What defines it:
- Callgrind, Cachegrind, DHAT, or adjacent Valgrind-backed tools
- instruction/cache/heap-style metric families
- raw profiler attachments and differential reports
- CI-oriented consistency claims

Why it deserves its own lane:
- it is not “more accurate Criterion”; it is a different engine family with different raw artifacts
- it is often the best lane for noisy CI environments
- downstream consumers need to know whether they are looking at timer samples or profiler-derived counts

Design rule:
- keep deterministic profiler lanes separate from statistical timer lanes and from hosted simulation modes

### 6) Hosted adapter lane (CodSpeed and adjacent services)
This is the lane where local benchmark code runs through a hosted measurement/archival workflow.

What defines it:
- compatibility layers for existing harnesses
- hosted build/run orchestration
- service-provided baseline and archival posture
- measurement modes such as simulation, walltime, and memory

Why it deserves its own lane:
- hosted adapters are strategically important, but they are not neutral transport
- CodSpeed explicitly changes the surrounding build/run workflow and measurement-mode vocabulary
- a hosted compatibility layer should not erase which local harness originally authored the benchmark

Design rule:
- keep hosted adapter truth separate from local harness-native truth and from later Perf Labs policy/gating conclusions

## Review rules that follow from the lane map
1. Keep **Cargo launch truth** separate from **benchmark-engine semantics**.
2. Keep **Criterion-native baselines** separate from **`cargo-criterion` JSON export posture**.
3. Keep **counter/throughput semantics** separate from **ordinary wall-time summaries**.
4. Keep **runner-import semantics** separate from **benchmark-native subject identity**.
5. Keep **deterministic profiler lanes** separate from **statistical timer lanes**.
6. Keep **hosted adapter baselines and modes** separate from **local harness baselines**.
7. Keep **portable review artifacts** separate from **tool-native raw attachments**.
8. Keep **benchmark-native truth** separate from **broader Perf Labs compare/gate policy**.

## What a worthy contribution should look like
The worthy contribution here is **not**:
- another benchmark harness,
- another fake universal benchmark score,
- another hosted dashboard wrapper,
- or another CI comment bot that rewrites every engine into one table.

It is a thin `cargo benchpack` / `benchmark-pack/v0` layer that can preserve:
- lane identity,
- subject identity,
- engine and measurement semantics,
- baseline provenance,
- runner/import posture,
- raw attachments,
- and bounded Perf Labs handoffs.

That means downstream reviewers can answer:
- *was this plain `cargo bench`, Criterion, Divan, nextest-imported, Iai-Callgrind, or hosted-adapter evidence?*
- *did the result depend on native saved baselines, imported baselines, or no baseline at all?*
- *was the primary metric statistical wall-time, throughput counters, instructions/cache/heap, or hosted simulation/memory output?*
- *what changed because a runner or hosted adapter got involved?*
- *what may a broader perf consumer conclude, and what must remain benchmark-native truth?*

## Immediate archive consequences
Read this together with:
- `design/benchmark-evidence-kit.md`
- `design/benchmark-evidence-pilot-program.md`
- `gaps/benchmark-evidence-subjects-lanes-baselines-and-imports.md`
- `proposals/epic-benchmark-evidence-kit.md`
- `design/harness-protocol-kit.md`
- `design/test-run-evidence-kit.md`
- `design/perf-labs.md`

The archive should now prefer **lane-aware benchmark packs before one fake benchmark verdict**, and it should keep benchmark-engine semantics, runner imports, and hosted adapters reviewable instead of narrating them as interchangeable “perf data”.
