# Crate performance-envelope product plan — 2026-03-17

This note exists to keep **P-0517 Crate Performance Envelope Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing workload / metric / confidence contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0517** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which named workloads actually matter for this crate,
- which metric is authoritative for each workload,
- which profile, harness, corpus, and environment assumptions make the measurement honest,
- which scenarios are CI-stable, locally-informative, comparative-only, or manual-review-only,
- what representative budgets or guardrails exist,
- and what changed between releases.

It should **not** try to become a new benchmark runner, a new profiler, a new hosted regression service, or a universal replacement for Criterion, Iai-Callgrind, Divan, or CodSpeed.
Those are imports and proving grounds, not the product.

## What the crate should provide other people

For downstream users, adopters, and release reviewers, the crate should provide:

1. **One compact performance contract** instead of folklore scattered across README charts, benchmark scripts, CI dashboards, and issue comments.
2. **A scenario map** so users can see whether the crate optimizes for startup, throughput, latency, instruction budget, memory budget, or binary size.
3. **A metric-authority policy** so users know which number to trust for each scenario and which numbers are only supporting evidence.
4. **An environment-fidelity receipt** so profile drift, harness drift, corpus drift, allocator/runtime drift, and CI-versus-local drift stop being hidden.
5. **A noise-class report** so maintainers can say “CI-reliable”, “hardware-sensitive”, “comparative-only”, or “manual review required” instead of faking certainty.
6. **A short human summary** that can be pasted into docs, release notes, or architecture review packets.
7. **A release diff** that makes changed workloads, changed metrics, or changed trust classes loud.

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
- do profile / harness / adapter assumptions line up with observed evidence,
- are CI/local trust classes explicit,
- are unsupported compatibility-layer features surfaced,
- and which parts remain manual-review-only?

### `cargo perf-envelope doctor`
Render human-facing warnings for suspicious situations such as:

- `release_claim_measured_with_bench_profile_only`
- `authoritative_metric_missing`
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
- how to rerun the scenario,
- how trustworthy the result is in CI or locally,
- and where the caveats are.

### `cargo perf-envelope diff <old> <new>`
Compare two receipts or packs and classify:

- `scenario_added`
- `scenario_removed`
- `metric_authority_changed`
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
- `cargo-perf-envelope` — CLI.

## Three artifact types that should be explicit in `0.1`

### `metric-authority.policy`
This is where maintainers say which metric actually rules each scenario.
Examples:

- `cold_start_cli` → `wall_time_ms`
- `instruction_count_ci` → `instructions`
- `heap_budget` → `peak_rss_bytes`
- `binary_size_release` → `artifact_bytes`

Supporting metrics are allowed, but the authoritative metric must be singular and explicit.

### `environment-fidelity.receipt`
This is where the crate records whether the observed run really matched the advertised environment.
Examples:

- benchmark harness disabled or not,
- `bench` profile versus `release` profile,
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

The main purpose is to make uncertainty reviewable rather than hidden.

## Best proving grounds for `0.1`

Prioritize crates where performance posture is real, but a full profiler platform would be overkill:

- CLI crates with cold-start and binary-size tradeoffs,
- parser/serializer crates with tiny-input latency versus throughput tradeoffs,
- async crates with runtime-sensitive or allocator-sensitive behavior,
- embedded-ish crates that need CI-stable instruction budgets,
- and framework crates whose default profile or adapter choice changes the story users should trust.

## Scenarios to support early

1. **Bench-profile versus release-profile fidelity** — because `cargo bench` defaults are useful but not identical to every production claim.
2. **Instruction-count CI authority** — because some crates should trust Iai-Callgrind-style counts in CI more than wall time.
3. **Compatibility-layer support gaps** — because “the same benchmark suite still runs” is not the same as “the same benchmark semantics were preserved”.
4. **Cold-start and binary-size pairing** — because CLI adopters often care about both together.
5. **Heap-budget or allocation-sensitive scenarios** — but only when the environment assumptions are explicit.

## Deliberately later

Leave these for follow-on work unless they become necessary for one proving-ground crate:

- deep profiler ingestion,
- flamegraph or trace UI hosting,
- automatic workload synthesis,
- organization-wide baseline storage,
- cross-repo hosted regression dashboards,
- and domain-specific labs for GPU, browser, or distributed workloads.

## What would make `0.1` successful

`0.1` is successful if maintainers can publish a small, reviewable bundle that lets a downstream reader answer:

- *what should I measure?*
- *which number should I trust?*
- *under what assumptions?*
- *how trustworthy is this result?*
- *and did that story change in the new release?*

That is enough to prove the missing layer is real.
