# Design: Perf Labs (`cargo perf`, `perf-pack/v0`)

## Goal
Create a Cargo-native performance evidence layer that makes it easy to:
- define reviewable workloads,
- record **what measurement lane** was used,
- preserve **which collector/configuration class** produced the result,
- compare against explicit baselines,
- gate on explainable verdicts,
- and attach one portable pack to CI, pull requests, releases, or dashboards.

This should converge existing tools rather than replace them. The point is not to kill Criterion, Iai-Callgrind, rustc-perf-style workflows, profiler tools, or Cargo’s newer report surfaces. The point is to give them a **shared comparison and evidence boundary**.

Current posture in the archive: **companion kit / evidence substrate**. Perf Labs should sit above benchmark engines, profiler attachments, and Cargo report surfaces, but it should increasingly import benchmark-native evidence through **Benchmark Evidence Kit** instead of re-describing every benchmark harness and hosted adapter itself. It is now the middle layer of a broader **Resource Evidence Stack** with **Benchmark Evidence Kit + Footprint Kit**; that shared frontier should strengthen coordination, not blur the line between benchmark-native facts, broader performance comparison/gating, time, storage, artifact bytes, and memory evidence.

## References (signals)
- 2025 State of Rust survey results: resource usage remains a major productivity issue.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `rustc-perf` improvements: multiple collectors, multiple configurations, and comparisons within configuration rather than across them.  
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html
- rustc dev guide perf testing: perf runs compare compiler versions across concrete workflow configurations such as fresh and incremental builds.  
  https://rustc-dev-guide.rust-lang.org/tests/perf.html
- Production-ready Cranelift backend goal: compile-time improvements for local development make workflow-specific performance evidence more valuable.  
  https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html
- Cargo 1.94 dev cycle: `cargo report timings`, `cargo report rebuild`, and `cargo report sessions` make structured performance-related attachments more practical.  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo bench docs: stable benchmarking remains split between unstable `#[bench]` and custom harness workflows.  
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html  
  https://doc.rust-lang.org/rustc/tests/index.html
- Criterion external-tools docs: machine-readable output comes from `cargo-criterion --message-format=json`, while CSV output is being deprecated.  
  https://bheisler.github.io/criterion.rs/book/cargo_criterion/external_tools.html  
  https://bheisler.github.io/criterion.rs/book/user_guide/csv_output.html
- `iai-callgrind`: accurate/consistent CI-friendly measurement and support for other Valgrind tools such as Cachegrind and DHAT.  
  https://docs.rs/iai-callgrind

## Core UX: `cargo perf`
- `cargo perf plan`
  - validate workload manifests, measurement profiles, and baseline selectors
- `cargo perf record`
  - run a workload and emit raw evidence plus normalized metadata
- `cargo perf compare --against <ref|version|artifact|baseline-id>`
  - emit a normalized comparison report with verdicts and reason codes
- `cargo perf gate`
  - apply policy to one or more comparison reports
- `cargo perf pack`
  - produce `perf-pack/v0`
- `cargo perf verify-pack <path>`
  - verify schema versions, checksums, attachment references, and tool identities
- `cargo perf explain <reason-code>`
  - decode why a comparison ended in `regressed`, `inconclusive`, `not-comparable`, etc.
- optional import / adapter flows:
  - `cargo perf import criterion`
  - `cargo perf import iai`
  - `cargo perf import cargo-report`

## Artifacts
### `perf-subject/v0`
Defines what is being measured:
- package / workspace member / binary / example / benchmark group
- workload family (`micro`, `macro`, `service`, `compile`, `memory`, `custom`)
- subject kind (`runtime`, `compile`, `allocation`, `profile-attachment`, etc.)
- fixture/dataset identifiers
- owning repo / revision / package metadata

### `perf-workload/v0`
Versioned workload manifest:
- command / entrypoint / function / request scenario
- input fixtures / datasets / corpus refs
- warmup and repetition policy
- sample budget or run budget
- selected measurement lanes
- optional profile/toolchain matrix
- notes on known nondeterminism or external-service dependencies

### `perf-measurement-profile/v0`
Declares the measurement lane:
- metric family (`wall-time`, `instructions`, `cache`, `heap`, `compile-time`, `custom`)
- engine identity (`criterion`, `cargo-criterion`, `iai-callgrind`, `custom`, `cargo-report` import, etc.)
- engine version and configuration
- confidence / significance model if applicable
- units and aggregation method
- unsupported-lane notes

Design rule: metric families stay explicit. Wall-time, instruction counts, cache simulation, compile timings, and heap profiles are not interchangeable.

### `perf-collector-profile/v0`
Records the configuration class that produced the result:
- CPU / memory / virtualization / runner class
- OS / kernel / container image / host image digest when available
- target triple, profile, linker, codegen backend, relevant flags
- environment normalization rules (governor pinning, affinity, isolated runner, etc.)
- collector/host identity for hosted services or distributed benchmark farms

Design rule: comparisons should default to **within-collector-profile** unless a policy explicitly says otherwise.

### `perf-baseline-record/v0`
Defines comparison anchors:
- baseline revision / release / tag / artifact id
- selection policy (`main`, `latest-release`, `last-green`, pinned commit, rolling window)
- freshness / expiry metadata
- whether multiple baselines are expected or allowed

### `perf-compare-report/v0`
Portable comparison artifact:
- subject ids and workload ids
- candidate + baseline metadata
- measurement-profile id and collector-profile id
- summary metrics and optional raw-sample refs
- verdict:
  - `IMPROVED`
  - `REGRESSED`
  - `UNCHANGED`
  - `INCONCLUSIVE`
  - `NOT-COMPARABLE`
  - `BASELINE-STALE`
- reason codes such as:
  - `PERF:NOISE-ABOVE-BUDGET`
  - `PERF:COLLECTOR-PROFILE-DRIFT`
  - `PERF:BASELINE-MISSING`
  - `PERF:THRESHOLD-EXCEEDED`
  - `PERF:COMPILE-WORKFLOW-CHANGED`
  - `PERF:METRIC-FAMILY-MISMATCH`
- optional attachment refs:
  - flamegraphs
  - callgrind/cachegrind outputs
  - heap/allocation profiles
  - `cargo report timings` / `rebuild` excerpts with authoritative-basis, coverage-slice, and instability warnings when they are shared outside the original machine

### `perf-policy/v0`
Policy for CI and release workflows:
- per-workload thresholds
- required sample counts or confidence posture
- allowed comparator classes
- critical-path workloads
- waiver windows and approvers
- “warn / fail / inconclusive / require-human-review” handling
- stale-baseline policy

### `perf-pack/v0`
Bundle for CI, review, and later archaeology:
- `manifest.json`
- `perf-subject.json`
- `perf-workload.json`
- `perf-measurement-profile.json`
- `perf-collector-profile.json`
- `perf-baseline-record.json` (optional)
- `perf-compare-report.json`
- `perf-policy.json` (optional)
- checksums / provenance / schema versions
- attachment pointers or digests

## Design principles
- **Configuration-aware comparison first.** “Faster” only means something relative to a declared measurement lane and collector profile.
- **One boundary, many engines.** Keep Criterion, Valgrind-backed lanes, Cargo imports, profiler attachments, and custom harnesses composable.
- **Runtime and compile lanes may coexist, but must not blur together.** The substrate should support both without pretending they are the same metric family.
- **Inconclusive is a real result.** Noise, runner drift, and stale baselines are not bugs in the UX; they are realities the artifact format should preserve.
- **Adapters before reinvention.** The first win is common evidence, not a monolithic new benchmark runner.
- **Portable packs, external blobs.** Large traces or profiles should be referenced, hashed, and attachable without bloating git history.

## Next credible move
The archive should now treat a **ranked pilot program** as the next real step for Perf Labs:
- compile-workflow evidence first,
- library microbench lanes second,
- deterministic CI instruction/count lanes third,
- service/macrobenchmark lanes fourth,
- federated multi-collector labs fifth.

See [`design/perf-pilot-program.md`](./perf-pilot-program.md) and [`design/resource-evidence-pilot-program.md`](./resource-evidence-pilot-program.md). The point is to prove comparability and baseline hygiene before trying to standardize every benchmark workflow at once, while also making compile/storage/resource reviews composable with Footprint Kit.

## What the kit should provide to others
- **Library authors:** release-attachable evidence for performance claims and regressions.
- **Application teams:** one place to define critical workloads and gate them honestly.
- **CI and hosted benchmark services:** a common compare/report/gate format instead of bespoke JSON and screenshots.
- **Tool authors:** a shared schema for publishing results from existing engines.
- **Reviewers:** explicit answers to “what changed?”, “how was it measured?”, and “is this actually comparable?”

## Integration points
- **Cargo Report Kit** for importing Cargo-native timing/rebuild/session information, including observation epoch and currentness posture so compile-workflow timing artifacts do not silently pose as current benchmark truth.
- **Build Doctor Kit** for turning compile-time evidence into diagnoses and suggestions.
- **Build Cache Kit** for correlating cache/layout changes with measured compile regressions.
- **Footprint Kit** for connecting runtime regressions to binary/section/allocation growth without collapsing them into one metric.
- **Release Pipeline Kit** for carrying performance packs as release artifacts.
- **Public API Kit** when releases need both compatibility evidence and performance evidence.
- **Coverage Evidence Kit / Config Set Kit** when CI needs bounded matrix ids attached to perf claims.

## Hard problems (explicitly scoped)
1. **Noise and runner variance**
   - v0 should make inconclusive results normal, not embarrassing.
2. **Hosted-service comparability**
   - distributed benchmark services need explicit collector identities and comparison classes.
3. **Compile vs runtime measurements**
   - one ecosystem substrate, multiple metric families, no fake unified score.
4. **Baseline lifecycle**
   - baselines age, drift, disappear, or cease to represent the intended target.
5. **Storage and privacy**
   - traces can be huge or contain sensitive path/environment data; packs should support redaction and external attachment references.
6. **Metric gaming**
   - CI gates should be explainable and overrideable, not silently optimized around one simplistic threshold.

## Overlap boundaries
- **Not Benchmark Evidence Kit:** benchmark-native subject ids, lane/counter semantics, runner imports, baseline imports, and raw benchmark result lineage should stay in [`design/benchmark-evidence-kit.md`](./benchmark-evidence-kit.md); Perf Labs imports that substrate when benchmark packs participate in broader performance review.
- **Not Cargo Report Kit:** Cargo reports are inputs and attachments; Perf Labs owns normalized performance comparison and gating artifacts.
- **Not Build Doctor Kit:** Build Doctor diagnoses why builds are slow and suggests interventions; Perf Labs records and compares performance evidence.
- **Not Footprint Kit:** footprint and size budgets remain separate evidence families even when they correlate with performance.
- **Not rustc-perf itself:** rustc-perf is a concrete, high-value benchmark service and a source of design lessons; Perf Labs should generalize the evidence boundary rather than replace the compiler team’s infrastructure.
- **Not one leaderboard:** the design must resist collapsing workloads, metric families, and configurations into one fake global performance score.

## Evaluation plan
Pilot on four classes of projects:
1. a library using Criterion / cargo-criterion for microbenchmarks,
2. a service using end-to-end scenario workloads,
3. a performance-sensitive crate using Iai-Callgrind in CI,
4. a compile-sensitive workspace that attaches Cargo timing / rebuild artifacts to compare reports.

Success bar:
- teams can define important workloads once,
- comparison reports clearly explain whether results are comparable,
- CI can gate on stable reason codes without scraping logs,
- releases can attach one `perf-pack/v0`,
- and no project has to abandon its preferred benchmark engine to participate.
