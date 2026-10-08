---
id: P-0517
title: Crate Performance Envelope Pack Kit — checked workload profiles, budget receipts, and perf diffs for library authors
status: idea
domains: [crates, cargo, benchmarking, performance, profiling, supportiveness, adoption]
last_reviewed: 2026-03-19
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://doc.rust-lang.org/cargo/commands/cargo-bench.html
  - https://doc.rust-lang.org/cargo/reference/profiles.html
  - https://blog.rust-lang.org/inside-rust/2024/12/13/this-development-cycle-in-cargo-1.84/
  - https://docs.rs/criterion/latest/criterion/
  - https://docs.rs/iai-callgrind/latest/iai_callgrind/
  - https://docs.rs/crate/divan/latest
  - https://docs.rs/crate/codspeed-criterion-compat/latest
  - https://docs.rs/crate/codspeed-divan-compat/latest
  - https://nexte.st/docs/integrations/criterion/
  - https://nexte.st/docs/features/benchmarks/
  - https://codspeed.io/docs/benchmarks/rust
  - https://docs.rs/divan/latest/divan/struct.AllocProfiler.html
---

# Problem

The archive now has much better answers for:

- **which crate to choose**,
- **what a crate claims to support**,
- **which interop profile it fits**,
- **how to configure it for a named scenario**,
- **what guidance it gives before failure**,
- **what it hands off after runtime failure**,
- **how to upgrade between releases**,
- and **how to leave it**.

But it still has a conspicuous receiver-facing gap around one of Rust’s biggest selling points:

- what a chosen crate hands other people when they ask **“which performance lane should I trust, on what workload, with what caveats, and how do I check it again later?”**

That gap matters because the current substrate is simultaneously real and fragmented:

1. `cargo bench` gives Rust a benchmark target model, but the default libtest benchmark harness is still nightly-only and many crates use a custom harness on stable instead.
2. Cargo profiles already expose meaningful performance tradeoffs (`opt-level`, LTO, debug info, custom profiles), and the docs explicitly say people should experiment because surprising results are common.
3. Criterion provides statistically grounded wall-time benchmarking.
4. Iai-Callgrind provides instruction/cache-oriented measurement that stays useful in virtualized CI.
5. Divan gives another modern stable benchmarking surface with grouped benchmark ergonomics.
6. CodSpeed compatibility layers show that teams are already trying to connect local benchmark suites to CI-hosted regression checking without rewriting everything.
7. The Rust vision work says crates need more **supportive interfaces**, not just elegant abstractions.
8. The 2025 survey says docs and code are still the main learning surfaces, and debugging/resource-usage pain remains visible.

The missing crate is therefore **not** another benchmark runner, **not** another profiler, and **not** another hosted regression service.
It is a **Crate Performance Envelope Pack Kit**.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **Which named workloads or performance scenarios matter for this crate?**
2. **Which metric should a downstream user trust for each one — wall time, instructions, allocations, peak RSS, binary size, startup time, or something else?**
3. **What kind of run produced the evidence — measurement, smoke-only sanity, replay/import, or manual review?**
4. **Which configuration, input corpus, workload lineage, and environment assumptions make the numbers honest?**
5. **Which numbers are representative budgets, and which are only comparative hints?**
6. **Which scenarios are hardware-sensitive, allocator-sensitive, runtime-sensitive, or too noisy for automatic pass/fail claims?**
7. **How did the crate’s performance envelope change across releases?**

That is more valuable than leaving users to reconstruct expectations from README screenshots, one-off Criterion reports, CI badges, and stale benchmark scripts.

# What it provides

- `perf-pack.toml` — versioned declaration of named performance scenarios, workload families, metrics, profile assumptions, input corpus references, environment constraints, and manual-review boundaries.
- `perf-surface.receipt.json` — observed benchmark/profiling facts imported from Cargo benchmark targets, harness settings, profiles, benchmark adapters, and selected environment controls.
- `perf-scenario.report.json` — machine-readable summary of named scenarios such as `small_input_latency`, `streaming_throughput`, `cold_start_cli`, `heap_budget`, `instruction_count_ci`, or other crate-specific lanes.
- `perf-recipe.manifest.json` — commands, profiles, input fixtures, environment preconditions, affinity/allocator notes, and expected outputs for each named scenario.
- `perf-check.report.json` — verifies whether the advertised scenarios actually ran under the stated harness/profile/tooling matrix.
- `perf-budget.report.json` — stores representative budgets, confidence classes, threshold semantics, and `manual_review_required` cases.
- `metric-authority.policy.json` — explicit meaning for which metric is authoritative per scenario and what supporting evidence is merely advisory.
- `execution-intent.report.json` — explicit statement of whether a run was authoritative measurement, supporting measurement, smoke-only sanity, replay/imported evidence, or manual-review territory.
- `workload-lineage.receipt.json` — explicit record of where a scenario’s workload came from and whether it is replayable or representative.
- `environment-fidelity.receipt.json` — explicit record of profile/harness/corpus/runtime/allocator/CI conditions and known distortions.
- `noise-class.report.json` — explicit classification such as `ci_reliable`, `comparative_only`, `hardware_sensitive`, or `manual_review_required`.
- `perf-diff.report.json` — compares two perf packs and classifies `scenario_added`, `scenario_removed`, `budget_changed`, `metric_authority_changed`, `execution_intent_changed`, `environment_changed`, `workload_lineage_changed`, `noise_class_changed`, and `manual_review_boundary_changed`.
- `perf-notes.summary.md` — compact human-facing explanation derived from the structured artifacts.
- `cargo perf-pack capture` — capture one crate’s performance-envelope bundle from benchmark targets, adapters, and selected runs.
- `cargo perf-pack doctor` — render human-facing warnings about profile drift, unsupported adapter semantics, and fake-precision confidence claims.
- `cargo perf-pack check` — verify the selected scenarios.
- `cargo perf-pack diff <old> <new>` — compare performance-envelope surfaces across releases.
- `cargo perf-pack summary` — render a reviewable summary from the structured artifacts.

# What the crate should provide other people

1. **A crate-authored performance contract** above raw benchmark outputs and below impossible “performance guaranteed everywhere” claims.
2. **Named workload profiles** so users can tell whether the crate optimizes for startup, tail latency, throughput, memory, instruction count, or binary size.
3. **Execution-intent honesty** so “the benchmark still runs” is not confused with “the release budget was measured.”
4. **Workload-lineage honesty** about whether a scenario rests on a synthetic toy case, checked fixture corpus, or captured trace.
5. **Benchmark honesty** about cache warmth, allocator/runtime/backend choices, and CI versus local measurement meaning.
6. **Checked performance receipts** so maintainers can prove which measurement lanes were actually exercised.
7. **Diffable performance envelopes** so release reviewers can see when a crate changed what it optimizes for, not just whether one benchmark number moved.
8. **Reusable import artifacts** for docs portals, template generators, pathfinder crates, perf dashboards, and org review tooling.
9. **Wide-scope usefulness** across embedded, CLI, server, parser, crypto, data, async, and graphics crates without pretending one metric rules them all.

# Persona / who it’s for

- library maintainers whose crates have meaningful performance tradeoffs
- framework teams supporting multiple runtimes, allocators, backends, or profiles
- downstream adopters choosing between crates or between modes of one crate
- release reviewers who want to diff performance posture without trusting screenshots
- docs/tool authors who want stable artifacts instead of scraping prose or CI logs

# Users & user stories

- **CLI maintainer**: “Show me the honest cold-start and binary-size lane, not just throughput numbers from a warmed benchmark loop.”
- **Backend engineer**: “Tell me whether this crate’s default profile is tuned for throughput or tail latency, and what command reproduces that claim.”
- **Embedded maintainer**: “Give me one heap/instruction-budget scenario I can actually check in CI without pretending wall-clock timing is stable.”
- **Library author**: “Publish one performance envelope so users can see which workloads I optimize for and where I stop promising.”
- **Release reviewer**: “Diff two releases and tell me whether the workload, metric, or environment contract changed before I argue about one number.”

# Prior art (and why it’s insufficient)

- `cargo bench` provides benchmark targets and profile defaults.
- Criterion provides statistical wall-time measurement.
- Iai-Callgrind provides precise instruction/cache-oriented benchmarking and diffable results.
- Divan provides a modern stable benchmarking surface.
- CodSpeed compatibility layers connect existing benchmark suites to hosted CI measurement.
- Profiling and observability crates provide capture substrate and report formats.

What remains missing is the joined artifact that says:

- which **named performance scenarios** the maintainer intends,
- which **metric** is authoritative for each,
- which profile/input/environment assumptions make the numbers honest,
- which scenarios are only comparative or manual-review-only,
- and how the crate’s **performance envelope** changed across releases.

That is a different lane from:

- **P-0509** task-first crate choice,
- **P-0516** setup/configuration scenarios,
- **P-0512** compile-time guidance,
- **P-0513** runtime handoff,
- **P-0514** upgrade packs,
- profiling evidence bundles,
- generic benchmark frameworks,
- hosted CI perf services,
- or domain-specific performance workbenches.

# Design goals

1. **Receiver-facing first** — optimize for downstream decisions, not maintainer vanity charts.
2. **Scenario over benchmark soup** — name real workloads instead of dumping every bench target.
3. **Metric honesty** — let maintainers say “instruction count is authoritative here, wall time is not.”
4. **Join, don’t replace** — import Criterion, Iai-Callgrind, Divan, CodSpeed, and custom adapters where useful.
5. **Explicit noise classes** — support `ci_reliable`, `locally_informative`, `hardware_sensitive`, and `manual_review_required`.
6. **Diffability** — support release-to-release review of performance posture.
7. **Wide-scope usefulness** — remain relevant across tiny libraries and large frameworks.

# MVP surface

- Minimal `perf-pack.toml` schema with named scenarios, metrics, recipe references, and confidence classes.
- Import lane for Cargo benchmark targets, profile selection, and harness mode.
- Adapter imports for Criterion JSON-like outputs and Iai-Callgrind summary/diff outputs first; Divan/CodSpeed adapters next.
- `metric-authority.policy.json` to make one authoritative metric explicit per scenario.
- `environment-fidelity.receipt.json` to make profile/harness/corpus/runtime drift explicit.
- `noise-class.report.json` to keep CI-trust versus local-only guidance reviewable.
- `perf-check.report.json` that records whether advertised scenarios actually ran.
- `perf-budget.report.json` with representative value + tolerance + confidence/noise class.
- `perf-diff.report.json` to compare two envelope versions.
- `cargo perf-pack summary` to render a short, reviewable Markdown summary.

# Artifact vocabulary

## `perf-pack.toml`

```toml
schema_version = "0.1"
crate = "example-crate"

[[scenario]]
name = "cold_start_cli"
metric = "wall_time_ms"
confidence = "manual_review_required"
recipe = "recipes/cold_start_cli.toml"

[[scenario]]
name = "instruction_count_ci"
metric = "instructions"
confidence = "ci_reliable"
recipe = "recipes/instruction_count_ci.toml"
```

## `perf-budget.report.json`

```json
{
  "schema_version": "0.1",
  "crate": "example-crate",
  "scenarios": [
    {
      "name": "instruction_count_ci",
      "metric": "instructions",
      "baseline": 182340,
      "tolerance_percent": 3.0,
      "confidence": "ci_reliable",
      "manual_review_boundary": null
    },
    {
      "name": "cold_start_cli",
      "metric": "wall_time_ms",
      "baseline": 18.2,
      "tolerance_percent": 10.0,
      "confidence": "manual_review_required",
      "manual_review_boundary": "startup is machine-sensitive; compare only on pinned runners"
    }
  ]
}
```

# Distinctive implementation shape

## Crates

- `perfpack-core` — schemas, pack/diff logic, confidence vocabulary, summary rendering.
- `perfpack-capture` — importers for Cargo benchmark targets and selected tool outputs.
- `perfpack-criterion` — Criterion adapter.
- `perfpack-iai` — Iai-Callgrind adapter.
- `perfpack-divan` — Divan adapter.
- `cargo-perf-pack` — CLI.

## Confidence vocabulary

The crate should make confidence explicit instead of forcing fake precision:

- `ci_reliable`
- `locally_reliable`
- `comparative_only`
- `hardware_sensitive`
- `allocator_sensitive`
- `runtime_sensitive`
- `manual_review_required`

## Metric vocabulary

Allow multiple first-class metric lanes rather than one benchmark monoculture:

- wall time
- instruction count
- cache misses / cache-sensitive derived stats
- allocations / peak RSS
- startup time
- binary size

A scenario must declare exactly which metric is authoritative.

# Example scenario families

1. **Cold-start CLI** — startup time, binary size, stripped/unstripped notes.
2. **Streaming throughput** — MB/s or records/s with fixed corpus and backpressure assumptions.
3. **Small-input latency** — p50/p95 wall time or instruction count on tiny inputs.
4. **Heap budget** — allocations and peak RSS under a bounded workload.
5. **CI-stable instruction budget** — instruction-count lane for noisy or virtualized environments.

# Why this could be epic

Because it would give Rust a missing middle layer between “we ran some benches” and “users can actually trust what this crate says about performance.”

That matters for a huge spread of crate categories:

- parsers,
- serializers,
- async/network libraries,
- crypto and compression crates,
- CLI tooling,
- embedded components,
- data processing libraries,
- and high-level frameworks whose defaults silently choose one performance posture over another.

If **P-0509** helps users choose *which crate*, **P-0516** helps them choose *how to configure it*, and **P-0517** would help them understand *what performance tradeoff they are actually buying*.

For an implementation-ready `0.1` shape, see `meta/crate-performance-envelope-product-plan-2026-03-19.md`.

## 0.1

A credible `0.1` should stay small: one cargo subcommand plus library, importers for Cargo benchmark targets plus Criterion and Iai-Callgrind first, Divan and CodSpeed adapters next, and three new explicit artifact types that keep hidden benchmark ambiguity reviewable:

- **metric-authority policy** — which metric actually rules each named scenario;
- **environment-fidelity receipt** — whether the observed run matched the advertised profile/harness/corpus/runtime story;
- **noise-class report** — whether the scenario is CI-reliable, locally informative, comparative-only, or manual-review-only.

Early `doctor` warnings should focus on three especially common lies-by-omission:

- release claims measured only with default `bench` profile assumptions,
- CI imports that preserve benchmark execution but not benchmark semantics,
- and scenarios whose authoritative metric is still implicit.

# Adoption plan

## Phase 0
- Start with maintainers who already have Criterion or Iai-Callgrind benches and want a reviewable contract above them.
- Support one simple Markdown summary for README/docs linking.

## Phase 1
- Land importers for Criterion + Iai-Callgrind first.
- Add two or three scenario examples from different crate classes (CLI, parser, embedded-ish).

## Phase 2
- Add Divan and CodSpeed adapters.
- Add optional import/export for pathfinder or docs-portal crates.

## Phase 3
- Encourage release-review workflows: compare the old and new perf pack in CI, but keep automatic verdicts conservative.

# Scope boundaries

## In scope
- named scenario contracts
- measurement confidence vocabulary
- bundle import from existing benchmark/profiling tools
- checked recipes and performance-surface diffs
- reviewable artifacts for docs/CI/release notes

## Out of scope
- inventing a new universal benchmark runner
- replacing profilers
- promising machine-independent benchmark truth
- building a hosted performance SaaS
- domain-specific workload labs for every niche sector

# Risks / objections

## “Performance is too machine-specific for a contract”
That is exactly why the crate needs explicit confidence classes and manual-review boundaries.
The problem is not uncertainty; the problem is hidden uncertainty.

## “Criterion / Iai / Divan already solve this”
They solve measurement surfaces, not the joined receiver-facing contract over workloads, metrics, caveats, and diffs.

## “This will tempt maintainers into cargo-cult numbers”
Only if the crate hides noise. The design should force maintainers to classify scenarios conservatively and to record environment assumptions.

# Open questions

- Which adapter output shapes are stable enough for long-lived imports?
- Should `perf-budget.report.json` allow statistical intervals directly or only summary/tolerance pairs in MVP?
- How much binary-size and memory-budget support belongs in the MVP versus a later cross-tool import lane?
- Should scenario recipes include CPU-affinity/container pinning advice in structured form or only free-text notes at first?

# Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://blog.rust-lang.org/inside-rust/2024/12/13/this-development-cycle-in-cargo-1.84/
- https://docs.rs/criterion/latest/criterion/
- https://docs.rs/iai-callgrind/latest/iai_callgrind/
- https://docs.rs/crate/divan/latest
- https://docs.rs/crate/codspeed-criterion-compat/latest
- https://docs.rs/crate/codspeed-divan-compat/latest
