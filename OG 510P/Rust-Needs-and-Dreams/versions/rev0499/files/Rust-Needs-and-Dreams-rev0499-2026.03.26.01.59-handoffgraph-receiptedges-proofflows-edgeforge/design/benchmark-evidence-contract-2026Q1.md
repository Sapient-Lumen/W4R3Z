## Execution addendum (rev0452)
For questions about what the archive's **performance-claim / measurement-lane / baseline / comparability seam** should actually ship, read `design/benchmark-evidence-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- keep **Benchmark Evidence Contract** as the boundary contract;
- keep **Perf Labs** as the broader performance-review consumer layer;
- do **not** promote a new frontier here;
- and treat the new blueprint as the **execution layer** that carries subject, lane, collector/configuration, baseline, verdict/comparability, and handoff truth without collapsing into one benchmark engine or one score.

# Design: Benchmark Evidence Contract 2026Q1

## Goal
Promote the archive's benchmark/performance substrate from “a useful kit with a good lane map” to a first-class **Benchmark Evidence Contract**: a reviewable boundary for **what exact benchmark subject was measured, which measurement lane and collector semantics applied, what baseline posture is honest, how runner/import or hosted-adapter lossiness should be described, and what later CI / release / perf-lab / assistant consumers may legitimately conclude**.

This contract should sit:
- **above** raw benchmark directories, screenshots, one-off dashboard links, and freeform PR comments;
- **below** broader performance policy, release gates, and product-level performance narratives;
- and **beside** Harness Protocol, Test Run Evidence, Cargo Report, Build-State Evidence, and Perf Labs rather than replacing any of them.

The point is not to invent one more benchmark engine.
The point is to stop losing truth whenever a Rust performance claim becomes “we ran something in CI and it looked faster”.

## Why this seam matters now
The case for a first-class benchmark-evidence contract is stronger in 2026 than it was even a year ago:
- Cargo's benchmark surface is still explicitly plural: `cargo bench` can run libtest or a custom harness, and `#[bench]` remains unstable/nightly-only.
- Rust 1.94 widened workspace benchmark selection with `cargo bench --all`.
- nextest now has an experimental `cargo nextest bench` lane and benchmark-specific timeout controls.
- Criterion still has a real native baseline story, while `cargo-criterion` still exposes machine-readable JSON without baseline support.
- Divan makes counter semantics explicit instead of burying throughput assumptions in prose.
- Iai-Callgrind keeps deterministic profiler-backed metric families and raw attachments first-class.
- CodSpeed's Rust adapters keep hosted benchmark plurality and measurement-mode differences explicit.
- rustc-perf's multiple-collector direction reinforces that comparison should happen within a declared configuration rather than across flattened performance folklore.
- Cargo's build-analysis/report work keeps making machine-readable evidence more normal elsewhere in the toolchain, which raises the bar for benchmark-side handoffs too.

That combination means the missing contribution is no longer “a nicer benchmark dashboard”.
It is a **portable benchmark-evidence contract** that keeps subject, lane, baseline, collector/configuration, verdict, and consumer handoff visibly distinct.

## References (signals)
- `cargo bench` docs and benchmark-target docs.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
  https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- Rust release notes: `cargo bench --all`.
  https://doc.rust-lang.org/beta/releases.html
- nextest benchmark docs and benchmark-specific configuration.
  https://nexte.st/docs/features/benchmarks/
  https://nexte.st/docs/configuration/reference/
- Criterion baseline docs and `cargo-criterion` machine-readable JSON docs.
  https://bheisler.github.io/criterion.rs/book/user_guide/command_line_options.html
  https://bheisler.github.io/criterion.rs/book/cargo_criterion/cargo_criterion.html
- Divan counter docs.
  https://docs.rs/divan/latest/divan/counter/index.html
- Iai-Callgrind docs.
  https://docs.rs/iai-callgrind/latest/iai_callgrind/
- CodSpeed Rust docs and cargo-codspeed docs.
  https://codspeed.io/docs/benchmarks/rust
  https://codspeed.io/docs/reference/codspeed-rust/cargo-codspeed
- rustc-perf improvements goal.
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html
- Cargo 1.94 development cycle report.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Working thesis
A worthy contribution here should make it easy to answer all of these without opening three benchmark engines, two CI logs, and a hosted service UI side by side:
1. What exact **benchmark subject** was measured?
2. Which **measurement lane** was authoritative: statistical wall-time, throughput counters, deterministic profiler counts, hosted simulation/memory, or something else?
3. Which **collector/configuration** facts matter for comparability?
4. What **baseline** was used, and was it native, imported, hosted, absent, stale, or unsupported?
5. What is the honest **verdict posture**: improved, regressed, unchanged, inconclusive, not-comparable, or baseline-stale?
6. What later consumers — Perf Labs, release review, CI gates, support, assistants — may honestly import from the result?

If the design cannot answer those questions, then Rust still lacks the performance-claim boundary it needs.

## Contract shape
Read the existing benchmark substrate as a contract with six visibly separate layers:

### 1) Benchmark subject truth
The contract must preserve what exact measured thing exists:
- package / workspace member / benchmark target / binary id
- suite / group / case id
- parameterization or scenario identity
- subject class such as `micro`, `binary-scenario`, `compile`, `profiled`, or `hosted-case`

### 2) Measurement-lane truth
The contract must keep engine and metric semantics explicit:
- `cargo-bench` foundation versus Criterion-native statistical lanes
- counter-bearing throughput lanes
- deterministic profiler lanes
- hosted adapter modes
- declared metrics, units, and caveats

### 3) Collector / configuration truth
The contract must show what makes comparison honest or dishonest:
- runner / engine / adapter identity and version
- target triple, profile, codegen backend, and relevant feature/config posture
- host/CI/container class where relevant
- declared comparability scope and exclusions

### 4) Baseline truth
The contract must keep baseline posture visible:
- native saved baseline ids
- imported prior-run baselines
- hosted baselines
- absent / unsupported / stale / incompatible baselines
- branch, release, or revision anchors

### 5) Verdict truth
The contract must distinguish raw measurements from interpreted comparison:
- summary values and units
- optional differential statistics when the engine supports them
- explicit verdicts such as `improved`, `regressed`, `unchanged`, `inconclusive`, `not-comparable`, `baseline-stale`
- reason codes instead of one fake benchmark score

### 6) Consumer-handoff truth
The contract must tell later consumers what they may honestly import:
- CI and PR review can import subject + lane + baseline + verdict
- Perf Labs can import benchmark packs without re-owning benchmark-native semantics
- release/support docs can import bounded result slices
- assistants can summarize the pack, but must not claim more authority than the pack actually carries

## What the MVP should look like in theory
A realistic v0 is not “solve performance measurement for all of Rust”.
It is:
- one schema family for subject, lane, collector/configuration, baseline, verdict, and bundle packaging;
- one Criterion-native proof;
- one counter-bearing proof;
- one deterministic-profiler proof;
- one runner-import proof;
- and one hosted-adapter proof.

Required artifacts:
- `benchmark-subject/v0`
- `benchmark-lane-profile/v0`
- `benchmark-collector-profile/v0`
- `benchmark-baseline-import/v0`
- `benchmark-verdict-report/v0`
- `benchmark-pack/v0`

Required rules:
- keep **subject** distinct from **lane**;
- keep **lane** distinct from **collector/configuration**;
- keep **baseline** distinct from **verdict**;
- keep **runner/import or hosted-adapter posture** distinct from **benchmark-native truth**;
- keep **benchmark-native truth** distinct from **Perf Labs policy**.

## What the MVP should look like in practice
### Pilot 1 — stable local lane pair
Show Criterion native plus Divan counter-bearing packs with explicit subject/lane/baseline identity.

### Pilot 2 — runner-import lane
Show `cargo nextest bench` import posture without pretending it is transparent to the underlying harness.

### Pilot 3 — deterministic-profiler lane
Show Iai-Callgrind or adjacent Valgrind-backed imports with raw attachments and explicit metric-family identity.

### Pilot 4 — hosted adapter lane
Show CodSpeed imports that preserve original harness identity and hosted measurement-mode truth.

### Pilot 5 — Perf Labs handoff lane
Show one bounded import from benchmark-native packs into broader comparison/gating work without re-describing benchmark semantics.

## Why this should be promoted instead of “just more Perf Labs”
The archive already has strong work on Perf Labs, Build-State Evidence, Cargo Report, and Harness Protocol.
Those are still right, but the next sharpening move here is **not** a broader policy engine or another dashboard.

Why this promotion wins now:
- official and primary tool signals are strongest on **plural benchmark lanes plus partial machine-readable imports**, not on one new benchmark winner;
- the archive already has enough benchmark-native substrate to justify a composition layer;
- promoting the contract reduces the risk that one screenshot, one Criterion baseline, one nextest import, one callgrind trace, or one hosted report silently defines the whole performance story.

So this revision promotes the **benchmark-native performance-claim boundary**, not the whole performance platform.

## Ranking impact
This does **not** reorder the archive's top band.
It adds one more explicit frontier beneath the current map:
- Build-State Evidence stays #1 overall.
- Adoption Navigation remains the strongest anti-tacit-knowledge frontier.
- Debuggability stays high.
- Maintenance Reality remains the clearest stewardship/continuity seam.
- Defect Escalation remains the clearest upstream-routing / repro-to-regression-handoff seam.
- Benchmark Evidence Contract becomes the clearest next **performance-claim / compare-shaping** move.

That means it should sit below the broad build/debug/resource band, but above another round of benchmark folklore, dashboard screenshots, or engine-specific badges.

## What not to build
Do **not** build:
- a universal benchmark portal;
- a new benchmark engine pretending to subsume Criterion, Divan, Iai-Callgrind, nextest, and hosted adapters;
- a one-number “performance score” layer;
- or a CI bot that makes verdicts without preserving benchmark-native semantics.

The winning contribution is thinner and more durable:
**publish explicit benchmark subject truth, explicit lane and baseline truth, explicit collector/configuration truth, explicit verdict truth, and hand that off honestly to multiple consumers without flattening unlike measurement models into one score.**
