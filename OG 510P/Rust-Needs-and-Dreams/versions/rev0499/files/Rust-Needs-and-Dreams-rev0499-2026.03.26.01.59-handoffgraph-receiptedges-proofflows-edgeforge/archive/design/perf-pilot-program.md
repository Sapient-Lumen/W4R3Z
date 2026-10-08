# Design: Perf Pilot Program (`cargo perf pilot`, `perf-pilot-pack/v0`)

## Goal
Make [`design/perf-labs.md`](./perf-labs.md) executable as a **ranked rollout plan** instead of leaving it as a good but still slightly abstract kit.

A worthy contribution here is not merely another benchmark harness, another hosted dashboard, or another pretty regression graph. It is a performance-evidence substrate that can:
- describe what was measured,
- preserve how it was measured,
- say whether two runs are actually comparable,
- make baseline freshness and waiver posture explicit,
- and let CI / release / review workflows consume the same attachable artifacts.

## Why this needs its own design layer
Perf Labs was already directionally right, but current Rust signals make the missing execution posture much clearer:
1. **Performance pain remains broad.** The 2025 State of Rust survey says resource usage (slow compile times and storage usage) is still one of the biggest productivity problems.
   https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
2. **Performance is part of a flagship Rust theme.** The 2025H2 project goals put “Flexible, fast(er) compilation” in the flagship set and explicitly frame it as improving both specialized build scenarios and everyday development workflows.
   https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/
3. **Cargo is becoming more machine-facing about build performance.** The build-analysis goal and the 1.93/1.94 development-cycle updates say Cargo is recording build metadata across invocations and adding `cargo report timings`, `cargo report rebuild`, and `cargo report sessions` to explain why builds were slow or rebuilt.
   https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
   https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
   https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
4. **rustc-perf is explicitly pushing toward multi-collector, multi-configuration reality.** The current goal is about distributed benchmarking across multiple platforms and configurations, and it explicitly says current perf-regression policy does not yet account for conflicting results.
   https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html
5. **Rust’s official benchmarking entrypoints remain fragmented.** `cargo bench` still centers libtest-style benchmarking where `#[bench]` is unstable/nightly-only, custom harnesses are normal, and the stable story is still ecosystem-composed.
   https://doc.rust-lang.org/cargo/commands/cargo-bench.html

That combination means the next credible move is not “invent a better benchmark runner”. It is to define a **ranked pilot program** for workload identity, metric-lane identity, collector-profile truth, baseline hygiene, and reviewable compare/gate outcomes.

## Working thesis
A serious contribution should make all of these answerable in one place:
- Which workload family is this? (`compile`, `micro`, `service`, `instruction-count`, `allocation`, etc.)
- Which measurement lane produced the result?
- Which collector profile or runner class produced it?
- Which baseline is in force, and is it fresh enough to trust?
- If a gate fired, why?
- If the result is inconclusive, is that because of noise, stale baselines, runner drift, or metric mismatch?

## Design principles
1. **Collector identity is first-class.** Do not treat machine differences as footnotes.
2. **Metric families stay explicit.** Wall-time, instructions, cache simulation, compile timings, heap profiles, and end-to-end service scenarios are neighbors, not synonyms.
3. **Baseline policy is part of the evidence.** A result without baseline freshness and selector truth is not ready for governance.
4. **Reason-coded gates beat charts.** Pretty visualization is fine, but CI / release / policy consumers need stable verdicts and reason codes.
5. **Adapters before replacement.** The point is to unify evidence from existing engines and reports before replacing them.
6. **Hosted / federated labs are a later pilot, not the starting assumption.** The format should work in one repo before it tries to run the world.

## Recommended pilot order

### Pilot 1 — Compile-workflow evidence lane
Use Cargo build-analysis and `cargo report` style inputs to standardize compile-time performance evidence for real developer workflows.

Must prove:
- clean vs incremental vs relink-sensitive workflows can be named explicitly;
- `perf-workload/v0`, `perf-measurement-profile/v0`, `perf-collector-profile/v0`, and `perf-compare-report/v0` are enough to compare build-performance results honestly;
- Cargo-native timing and rebuild artifacts can be attached without scraping HTML or ad hoc logs;
- baseline drift and “not comparable” outcomes are understandable to everyday maintainers.

Why first:
- this is where official Cargo motion is strongest right now;
- the user pain is broad, not niche;
- it composes directly with Build Cache / Change Impact / Build Doctor instead of duplicating them.

### Pilot 2 — Library microbenchmark lane
Use a library workspace with stable custom harnesses and/or common benchmarking crates to prove that Perf Labs works outside compiler/build workflows.

Must prove:
- microbenchmark subjects can be named consistently across packages, groups, and fixtures;
- stable-channel benchmarking remains workable without pretending the ecosystem has one canonical engine;
- compare reports preserve units, significance posture, and known-noise caveats;
- release or PR review can attach one pack instead of bespoke benchmark markdown.

Why second:
- it gives the kit an approachable adoption path for ordinary libraries;
- it keeps the archive honest that runtime evidence matters too, not only compile performance.

### Pilot 3 — Deterministic CI lane (instruction / callgrind / cache-sim style)
Use a CI-friendly measurement lane where collector noise is reduced and comparisons are intentionally stricter.

Must prove:
- instruction-count or simulator-style results can live in the same artifact family without being confused with wall-time data;
- compare/gate policy can treat these lanes as stronger evidence for some changes;
- attachments such as callgrind/cachegrind outputs remain external but still integrity-linked from the pack.

Why third:
- it tests the archive’s claim that metric families should compose without being flattened;
- it produces one of the clearest CI gating stories for performance-sensitive crates.

### Pilot 4 — Service / scenario macrobenchmark lane
Use a real application or service with request traces, datasets, or scripted scenarios.

Must prove:
- service-like workloads can be described as first-class subjects instead of one-off benchmark scripts;
- fixture/dataset identity, environment assumptions, and warmup policy can be preserved;
- the pack can carry summary verdicts while pointing to large external traces or flamegraphs;
- reviewers can see whether a scenario is comparable or only advisory.

Why fourth:
- it proves the substrate is not only for microbenchmarks or compiler teams;
- it makes the kit relevant to production Rust applications where “the benchmark” is actually a scenario family.

### Pilot 5 — Federated collector lane
Use multiple collectors / platforms / architectures and prove the schema remains honest under distribution.

Must prove:
- collector fleets can be described without smuggling in fake cross-machine comparability;
- comparisons default to within compatible collector classes;
- conflicting results and unsupported comparisons are preserved instead of silently averaged away;
- a status-page / hosted-service consumer can ingest packs without redefining the core schema.

Why fifth:
- it lines up with the current rustc-perf direction;
- it is strategically important but operationally heavier than the first four pilots.

## Shared schema discipline
Every pilot must keep these distinct:
1. **subject** vs **measurement lane**
2. **collector profile** vs **baseline selector**
3. **observed result** vs **policy verdict**
4. **portable summary** vs **large external attachments**
5. **advisory comparison** vs **gate-worthy comparison**

## Immediate archive consequences
Read this file together with:
- [`design/perf-labs.md`](./perf-labs.md)
- [`proposals/epic-perf-labs.md`](../proposals/epic-perf-labs.md)
- [`design/cargo-report-kit.md`](./cargo-report-kit.md)
- [`design/build-cache-kit.md`](./build-cache-kit.md)
- [`design/change-impact-kit.md`](./change-impact-kit.md)
- [`design/build-doctor-kit.md`](./build-doctor-kit.md)

The archive should now prefer:
- **compile-workflow and baseline-hygiene pilots first**,
- **adapters / evidence convergence before new engines**,
- and **reason-coded compare/gate artifacts** over performance dashboards or leaderboard designs.

## What should wait
Do **not** start with:
- a global hosted performance service for all crates,
- one fake universal benchmark score,
- automatic cross-machine normalization that hides collector drift,
- or a new “standard benchmark harness” crusade.

Those may become consumers later. They are not the core missing substrate.
