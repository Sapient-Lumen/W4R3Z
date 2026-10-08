# Crate performance-envelope product plan — 2026-03-19

This note exists to keep **P-0517 Crate Performance Envelope Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing workload / metric / confidence contract**.
This refresh answers a narrower question:

> If somebody actually started building **P-0517** this week, what should version `0.1` look like now that Cargo/bench/profile substrate, Criterion, Iai-Callgrind, Divan, CodSpeed compatibility layers, and cargo-nextest’s benchmark/test-mode split are all more explicit?

## Main judgment

A buildable `0.1` should still be a **small cargo subcommand plus library**.
But the center of gravity should now be slightly sharper:

- named scenarios,
- metric authority,
- **execution intent**,
- **workload lineage**,
- profile / harness / environment fidelity,
- noise / trust classes,
- and release diffs.

The key change is that `0.1` should explicitly distinguish **measurement** from **benchmark-sanity verification**.
It should also distinguish **authoritative workloads** from convenient synthetic inputs.

That means the crate should help maintainers publish one reviewable answer to:

- which workloads matter,
- which metric rules each one,
- whether a run was measuring or only checking that a benchmark still compiles and doesn’t panic,
- what input lineage made the scenario representative,
- which profile / harness / environment actually produced the evidence,
- and what changed between releases.

It should **not** try to become a new benchmark runner, profiler, dashboard, or hosted perf platform.
Those are imports and proving grounds, not the product.

## What the crate should provide other people

For downstream users, adopters, and release reviewers, the crate should provide:

1. **One compact performance contract** instead of folklore scattered across README charts, benchmark scripts, CI dashboards, and issue comments.
2. **A scenario map** so users can see whether the crate optimizes for startup, throughput, latency, instruction budget, memory budget, or binary size.
3. **A metric-authority policy** so users know which number to trust for each scenario and which numbers are only supporting evidence.
4. **An execution-intent report** so users can tell whether a recorded run was real measurement, smoke-only sanity, replay/imported evidence, or manual-review territory.
5. **A workload-lineage receipt** so users know whether a scenario rests on an inline synthetic case, a checked fixture corpus, a seeded generator, or a captured trace.
6. **An environment-fidelity receipt** so profile drift, harness drift, corpus drift, allocator/runtime drift, and CI-versus-local drift stop being hidden.
7. **A noise-class report** so maintainers can say `ci_reliable`, `comparative_only`, `hardware_sensitive`, or `manual_review_required` instead of faking certainty.
8. **A short human summary** that can be pasted into docs, release notes, or architecture review packets.
9. **A release diff** that makes changed workloads, changed metrics, or changed trust classes loud.

For maintainers, the crate should provide:

1. a small policy file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake benchmark precision,
3. adapters for common Cargo / Criterion / Iai / Divan / CodSpeed substrate instead of bespoke reinvention,
4. one place to record benchmark honesty that is narrower than profiling and wider than one benchmark output file,
5. and a CI gate for “this release changed what performance story we are telling”.

## Recommended `0.1` command surface

### `cargo perf-envelope init`
Create a starter `perf-pack.toml` by importing obvious candidates from:

- `[[bench]]` targets and harness settings,
- declared benchmark tools and adapters,
- benchmark group names or benchmark IDs when those are available,
- selected profile settings,
- and maintainer-declared scenario names.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo perf-envelope capture`
Emit one normalized receipt bundle from a declared performance scenario.
This should capture:

- named scenarios,
- metric authority,
- execution intent,
- workload lineage,
- environment fidelity,
- noise classes,
- observed budgets or baselines,
- and imported evidence sources.

`capture` should work on imported artifacts too.
It must not require one blessed benchmark framework.

### `cargo perf-envelope check`
Run the local validation pass:

- do declared scenarios and metrics parse,
- does each scenario declare one authoritative metric,
- is execution intent explicit,
- do profile / harness / adapter assumptions line up with observed evidence,
- is workload lineage declared for authoritative scenarios,
- are CI/local trust classes explicit,
- are unsupported compatibility-layer features surfaced,
- and which parts remain manual-review-only?

### `cargo perf-envelope doctor`
Render human-facing warnings for suspicious situations such as:

- `criterion_test_mode_presented_as_authoritative_measurement`
- `release_claim_measured_with_bench_profile_only`
- `authoritative_metric_missing`
- `authoritative_workload_missing_lineage`
- `instruction_budget_claim_without_callgrind_or_equivalent`
- `wall_time_claim_marked_ci_reliable_without_pinned_environment`
- `compat_layer_unsupported_feature_present`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo perf-envelope summary`
Render a short receiver-facing note for docs or release review.
A good summary answers:

- which workloads matter,
- which metric is authoritative for each,
- what kind of run backed the claim,
- how representative the workload lineage is,
- how to rerun the scenario,
- how trustworthy the result is in CI or locally,
- and where the caveats are.

### `cargo perf-envelope diff <old> <new>`
Compare two receipts or packs and classify:

- `scenario_added`
- `scenario_removed`
- `metric_authority_changed`
- `execution_intent_changed`
- `workload_lineage_changed`
- `budget_changed`
- `corpus_changed`
- `profile_or_harness_changed`
- `noise_class_changed`
- `manual_review_required`

### `cargo perf-envelope pack`
Emit one compact `.perfenvelope.zip` bundle for CI artifacts, release review, downstream support, or docs tooling.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.

- `perf-envelope-core` — schema types, validation, diff logic, summary rendering, and shared vocabulary.
- `perf-envelope-capture` — imports from Cargo target/profile metadata and generic evidence receipts.
- `perf-envelope-criterion` — Criterion adapter.
- `perf-envelope-iai` — Iai-Callgrind adapter.
- `perf-envelope-divan` — Divan adapter.
- `perf-envelope-codspeed` — CodSpeed compatibility-layer importers and support-gap classification.
- `perf-envelope-nextest` — import of nextest benchmark/test-mode evidence without confusing test-mode runs with performance measurement.
- `cargo-perf-envelope` — CLI.

## Five review objects that should be explicit in `0.1`

### `metric-authority.policy`
This is where maintainers say which metric actually rules each scenario.

### `execution-intent.report`
This is where the crate records what kind of run produced the evidence.
Examples:

- `authoritative_measurement`
- `supporting_measurement`
- `smoke_only`
- `compile_and_run_sanity`
- `replay_only`
- `manual_review_required`

This file matters because benchmark-related CI often proves **that the suite still runs**, not that the measured number should be trusted as a release budget.

### `workload-lineage.receipt`
This is where the crate records where the workload came from.
Examples:

- inline synthetic micro input,
- checked fixture file,
- seeded generated dataset,
- captured production trace,
- imported replay corpus.

This file matters because an authoritative metric without authoritative workload lineage is often just precise trivia.

### `environment-fidelity.receipt`
This is where the crate records whether the observed run really matched the advertised environment.
Examples:

- benchmark harness disabled or not,
- `bench` profile versus `release` / custom profile,
- allocator/runtime/backend choice,
- corpus identifier and warm/cold assumptions,
- CI runner versus local machine,
- compatibility-layer limitations or unsupported benchmark features.

### `noise-class.report`
This is where the crate records what sort of trust is justified.
Examples:

- `ci_reliable`
- `locally_reliable`
- `comparative_only`
- `hardware_sensitive`
- `allocator_sensitive`
- `runtime_sensitive`
- `manual_review_required`

## Best proving grounds for `0.1`

Prioritize crates where performance posture is real, but a full profiler platform would be overkill:

- CLI crates with cold-start and binary-size tradeoffs,
- parser/serializer crates with tiny-input latency versus throughput tradeoffs,
- async crates with runtime-sensitive or allocator-sensitive behavior,
- embedded-ish crates that need CI-stable instruction budgets,
- framework crates whose default profile or adapter choice changes the story users should trust.

## Scenarios to support early

1. **Bench-profile versus release/custom-profile fidelity** — because `cargo bench` defaults are useful but not identical to every production claim.
2. **Criterion test mode versus real measurement** — because nextest-style sanity runs are useful, but they are not budgets.
3. **Instruction-count CI authority** — because Iai-Callgrind can provide a stronger CI story than wall time for some workloads.
4. **Compatibility-layer runs with partial semantic coverage** — because a suite running under a compatibility layer does not mean every benchmark feature survived unchanged.
5. **Allocation-budget scenarios** — because Divan-style allocation profiling can be exactly the right metric while also perturbing time measurements.
6. **Captured-trace workload lineage** — because downstream users trust performance claims more when the workload origin is explicit.

## Adoption plan

The winning adoption motion is:

1. start with maintainers already publishing benches,
2. import their current runners rather than replacing them,
3. make summaries simple enough for README / release note use,
4. and make diffs useful enough for CI/release review.

The first release should target teams already using some mix of Criterion, Iai-Callgrind, Divan, CodSpeed, or nextest benchmark/test-mode workflows.
Those teams already have measurement substrate; they lack a compact contract.

## Explicit non-goals for `0.1`

- not a universal profiler UI
- not a replacement for Criterion / Iai-Callgrind / Divan / CodSpeed
- not a hosted perf-regression service
- not an attempt to standardize one metric for all crates
- not a benchmark corpus generator platform
- not a guarantee that synthetic or imported workloads are representative without maintainer review

## Working judgment

The 2026 version of **P-0517** should be treated as a **performance-support contract crate**, not as another benchmarking framework.
Its most valuable gift to other people is not more numbers.
It is a compact explanation of **which numbers matter, what kind of run produced them, what workloads they stand for, and how much trust they deserve**.
