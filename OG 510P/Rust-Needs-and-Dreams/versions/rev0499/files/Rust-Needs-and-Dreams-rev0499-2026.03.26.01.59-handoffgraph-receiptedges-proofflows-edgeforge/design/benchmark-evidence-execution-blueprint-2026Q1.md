# Design: Benchmark Evidence execution blueprint 2026Q1

## Question
Once the archive accepts that Rust benchmarking is strategically important, what should the worthy contribution actually become before it dissolves into “just use Criterion”, “just use rustc-perf”, “just use a hosted service”, or “just post a screenshot in CI”?

## Short answer
A worthy contribution here is a **reference layer + report/pack command + adapter/import corpus** for **benchmark subject truth**, **measurement-lane truth**, **collector/configuration truth**, **baseline truth**, **verdict/comparability truth**, and **bounded consumer handoff**.

Not another benchmark harness.
Not a fake universal score.
Not a perf dashboard empire.
Not a hosted service pretending all measurements have the same semantics.

In repo language, the missing thing is closer to **`cargo benchpack` + `benchmark-pack/v0`** than to a new runner.

## Why this seam is execution-worthy now
The ecosystem's current shape makes the missing layer unusually visible:
- Cargo still exposes a plural benchmark foundation: `cargo bench` can run libtest or a custom harness, and `#[bench]` remains unstable/nightly-only. That means stable benchmarking still depends on ecosystem harnesses rather than one canonical built-in lane.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
  https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- Criterion still has a real native baseline model (`--save-baseline`, `--baseline`, `--load-baseline`), while `cargo-criterion` still says its machine-readable JSON lane does **not** support baselines. So even one popular benchmark family already splits into native-baseline truth versus machine-export truth.
  https://bheisler.github.io/criterion.rs/book/user_guide/command_line_options.html
  https://bheisler.github.io/criterion.rs/book/cargo_criterion/cargo_criterion.html
  https://bheisler.github.io/criterion.rs/book/cargo_criterion/external_tools.html
- Divan makes throughput/counter semantics explicit and first-class, including bytes/items/cycles-style counting and allocation profiling. That means not every serious benchmark lane is just “time in ns”.
  https://docs.rs/divan/latest/divan/
  https://docs.rs/divan/latest/divan/counter/index.html
- Iai-Callgrind explicitly positions itself as a CI-suitable deterministic benchmarking harness centered on Callgrind, while also supporting Cachegrind and DHAT-style lanes. That is a materially different evidence family from statistical wall-time sampling.
  https://docs.rs/iai-callgrind/latest/iai_callgrind/
- nextest now has an experimental `cargo nextest bench` flow with dedicated benchmark timeouts and support for Criterion, nightly libtest benches, and custom test-harness protocol users. That means the runner/import seam is now live enough to matter architecturally.
  https://nexte.st/docs/features/benchmarks/
  https://nexte.st/changelog/
- CodSpeed’s Rust docs explicitly support multiple framework families and distinct measurement modes, which proves that hosted adapter/import lanes are now part of ordinary Rust benchmarking rather than a niche edge case.
  https://codspeed.io/docs/guides/how-to-benchmark-rust-code
- rustc-perf is itself moving toward multiple collectors and comparisons **within** a configuration, not across flattened configurations. That is exactly the kind of comparability discipline the broader ecosystem lacks.
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html
  https://github.com/rust-lang/rustc-perf/blob/master/README.md
- The compiler-performance survey and Cargo build-analysis work show that build/performance diagnosis is an increasingly first-class Rust concern. That raises the value of benchmark-side evidence that can survive handoff into broader performance review without becoming folklore.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

That combination means the missing contribution is no longer “someone should make benchmarking nicer”.
It is a **portable comparability and handoff layer**.

## What to refuse first
The wrong shapes are now clear enough that the archive should reject them explicitly:

### Wrong shape 1 — one benchmark engine as the answer
Criterion, Divan, Iai-Callgrind, and rustc-perf all matter, but they are not substitutes for one another.
If the proposed contribution picks one and narrates the rest away, it is too small.

### Wrong shape 2 — one hosted product as the answer
A service can be a proving lane or import adapter.
It should not become the canonical owner of benchmark truth.

### Wrong shape 3 — one universal performance score
Rust performance evidence spans wall-time, throughput, instructions, cache behavior, heap behavior, simulation, and build-time families.
A single score destroys too much meaning.

### Wrong shape 4 — a dashboard without an evidence contract
A UI can be useful, but if it cannot tell reviewers what exact subject ran, what lane it used, what baseline posture applied, and why two results are or are not comparable, it is downstream gloss.

### Wrong shape 5 — “Perf Labs will solve it later”
Perf Labs, release review, or support tooling can consume benchmark evidence.
They should not have to reconstruct benchmark-native semantics from screenshots and tool-specific blobs.

## Execution thesis
The worthy contribution should be built as six visibly separate truth layers.

### 1) Benchmark subject truth
The pack must say what exact thing was measured.
Examples:
- workspace / package / benchmark target identity
- group / case / parameter / scenario identity
- subject class such as `micro`, `binary-scenario`, `compile`, `profiled`, `hosted-case`
- optional feature / cfg / target / toolchain bounds

### 2) Measurement-lane truth
The pack must say what kind of measurement this is.
Examples:
- statistical wall-time lane
- explicit throughput/counter lane
- deterministic profiler lane
- hosted simulation / walltime / memory lane
- build or compile benchmark lane when imported from a broader perf substrate

### 3) Collector / configuration truth
The pack must say what makes comparisons honest or dishonest.
Examples:
- harness / runner / adapter identity and version
- profile / target / codegen / runtime flags
- host / CI / container / collector class
- explicit comparability scope (`same-lane`, `same-collector-family`, `advisory-only`, `not-comparable`)

### 4) Baseline truth
The pack must keep baselines first-class instead of implied.
Examples:
- native named baseline
- imported branch or revision baseline
- hosted service baseline
- absent / unsupported / stale / incompatible baseline
- baseline freshness and anchor refs

### 5) Verdict and comparability truth
The pack must keep measurement separate from interpretation.
Examples:
- summary values and metric units
- optional confidence intervals or differential stats
- explicit verdicts such as `improved`, `regressed`, `unchanged`, `inconclusive`, `baseline-stale`, `not-comparable`
- explicit reason codes instead of a vague “performance changed” banner

### 6) Consumer-handoff truth
The pack must say what later consumers may honestly import.
Examples:
- CI / PR review can import verdict slices and raw links
- release review can import bounded evidence summaries
- Perf Labs can aggregate packs without re-owning lane semantics
- assistants can summarize packs, but not invent comparability beyond what the pack declares

## What the artifact should look like in theory
A serious v0 should standardize a small family, not a monolith:
- `benchmark-subject/v0`
- `benchmark-lane-profile/v0`
- `benchmark-collector-profile/v0`
- `benchmark-baseline-import/v0`
- `benchmark-result-report/v0`
- `benchmark-pack/v0`

And one top-level command surface:
- `cargo benchpack report` — collect and normalize one or more benchmark-native results into reviewable reports
- `cargo benchpack pack` — bundle reports, attachments, and bounded metadata into `benchmark-pack/v0`

The contract must preserve raw attachments by reference where needed:
- Criterion report directories
- cargo-criterion JSON streams
- Divan counter metadata
- callgrind / cachegrind / DHAT outputs
- hosted-run receipts or external report URLs

## What the artifact should look like in practice
The archive should now prefer these proving lanes, in order:

### Lane 1 — stable local pair
Criterion native + Divan.

Why first:
- proves the design is not secretly one harness format;
- forces baseline truth and counter truth to coexist;
- hits ordinary Rust library workflows quickly.

### Lane 2 — runner import
`cargo nextest bench`.

Why second:
- proves that runner/setup/wrapper/timeouts can be imported honestly;
- keeps benchmark-native truth distinct from generic run orchestration.

### Lane 3 — deterministic profiler lane
Iai-Callgrind (and adjacent Valgrind-backed families).

Why third:
- proves the design can hold raw profiler artifacts and non-wall-time metric families;
- gives CI-facing deterministic evidence a first-class home.

### Lane 4 — hosted adapter lane
CodSpeed or an equivalent hosted compatibility path.

Why fourth:
- proves the design survives service mediation and measurement-mode differences;
- prevents hosted workflow from silently redefining the whole schema.

### Lane 5 — bounded Perf Labs handoff
Use benchmark packs as imported evidence inside broader performance review.

Why fifth:
- validates that benchmark-native packs can feed larger compare/gate workflows without semantic collapse;
- keeps benchmark evidence below policy rather than replacing it.

## Strategic boundaries with adjacent seams
This blueprint is intentionally close to other strong archive seams, but it is not them.

### Not Build-State Evidence
Build-State explains why work was rebuilt and where time/resources went across builds.
Benchmark Evidence explains what performance-claim subject was measured and how comparable the results are.

### Not Harness Protocol
Harness Protocol is about discovery and execution capability.
Benchmark Evidence is about measured-subject and baseline/verdict handoff.

### Not Test Run Evidence
Test Run Evidence records generic execution truth.
Benchmark Evidence records benchmark-native lane semantics that generic run records are not rich enough to carry.

### Not Perf Labs
Perf Labs is the broader performance-review / compare / policy layer.
Benchmark Evidence is the narrow, portable benchmark-native import layer below it.

### Not rustc-perf itself
rustc-perf is a major proving ground and inspiration.
But the worthy contribution here should work for ecosystem crates, library teams, CI adapters, and hosted runners too.

## Why this counts as a worthy contribution
This would count as worthy because it would give Rust something it still does not have:
**a reviewable way to move from “we ran benchmarks” to “here is an honest evidence pack with subject, lane, collector, baseline, comparability, and handoff truth intact.”**

That is strategically large enough to matter because:
- it reduces performance folklore;
- it improves CI/review/release conversations without demanding one benchmark winner;
- it composes with current tooling instead of replacing it;
- and it helps Rust scale from local microbench work to distributed, multi-collector, and hosted performance workflows.

## Ranking impact
This does **not** reorder the top of the archive.
It sharpens one remaining high-value seam.

Interpretation:
- **Build-State Evidence** stays the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** stays the clearest under-ranked day-to-day missing middle;
- **Benchmark Evidence** now becomes the clearest execution answer for **performance-claim / compare-shaping** work;
- **Perf Labs** remains the broader performance consumer layer above it;
- and future benchmark, hosted-perf, CI-regression, and performance-review notes should import this layer instead of rediscovering comparability truth privately.

## Read with
- `design/benchmark-evidence-contract-2026Q1.md`
- `design/benchmark-evidence-kit.md`
- `design/benchmark-evidence-lane-map.md`
- `design/benchmark-evidence-pilot-program.md`
- `proposals/epic-benchmark-evidence-kit.md`
- `design/harness-protocol-kit.md`
- `design/perf-labs.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
