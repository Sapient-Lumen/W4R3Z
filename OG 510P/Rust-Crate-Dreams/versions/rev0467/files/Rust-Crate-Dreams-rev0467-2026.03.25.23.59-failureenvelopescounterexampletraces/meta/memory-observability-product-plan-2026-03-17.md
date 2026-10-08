# Memory observability product plan — 2026-03-17

This note exists to keep **P-0084 Memory Observability Kit** disciplined.
The archive already decided that the missing value is a **shareable memory-evidence workflow**.
This pass answers a narrower question:

> If somebody actually started building **P-0084** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps teams publish one reviewable answer to:

- what capture scope was actually profiled,
- which backend observed the data and what that backend can or cannot see,
- how trustworthy symbolization and attribution are,
- what allocation / live-bytes / RSS / dump evidence was captured,
- which regressions are important enough to gate,
- and what changed between two captures.

It should **not** try to become a universal allocator, a whole hosted observability platform, a kernel-wide tracing framework, or a perfect profiler replacement for every operating system.
Those are imports and proving grounds, not the product.

## What the crate should provide other people

For downstream users, performance engineers, and release reviewers, the crate should provide:

1. **One compact memory evidence bundle** instead of folklore scattered across ad hoc profiler runs, shell recipes, heap dumps, and screenshots.
2. **A capture-scope policy** so people know whether they are looking at startup, one operation, a soak period, a background phase, or the whole process lifetime.
3. **A symbolization-fidelity report** so backtrace quality, stripped builds, missing frame pointers, path redaction, and partial attribution are made explicit.
4. **A backend-capability report** so allocator-interception, jemalloc stats, heap dumps, or imported profiles are not treated as equivalent when they are not.
5. **A regression-gate policy** so teams can say which metrics matter enough to fail CI or block release review.
6. **A short human summary** that can be attached to incidents, performance reviews, or upgrade notes.
7. **A release diff** that makes changed capture scope, changed backend, changed attribution quality, or changed memory budgets loud.

For maintainers, the crate should provide:

1. a small policy file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake profiler certainty,
3. adapters for common Rust memory-observation substrate instead of bespoke reinvention,
4. one place to record “what kind of memory evidence do we trust here?” that is narrower than full observability and more honest than one flamegraph image,
5. and a CI gate for “this release changed our memory story”.

## Recommended `0.1` command surface

### `cargo memobs init`
Create a starter `memobs-pack.toml` by importing obvious candidates from:

- maintainer-declared phases or workloads,
- supported profiling backends,
- chosen output paths and redaction defaults,
- known allocator configuration,
- and optional budget/regression expectations.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo memobs capture`
Emit one normalized receipt bundle from a declared memory scenario.
This should capture:

- capture scope,
- backend identity and capability class,
- symbolization fidelity,
- observed allocation/live-bytes/RSS or dump evidence,
- regression-gate metrics,
- and imported evidence sources.

`capture` should work on imported artifacts too.
It must not require one blessed backend.

### `cargo memobs check`
Run the local validation pass:

- do declared scopes and backends parse,
- does each scenario state what evidence class is authoritative,
- are symbolization limitations explicit,
- are redaction choices reviewable,
- are gate thresholds tied to named metrics,
- and which parts remain manual-review-only?

### `cargo memobs doctor`
Render human-facing warnings for suspicious situations such as:

- `heap_dump_without_scope_boundary`
- `allocator_trace_without_live_bytes_story`
- `rss_regression_without_allocator_or_phase_context`
- `symbolization_missing_or_partial`
- `backend_cannot_support_claimed_metric`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo memobs summary`
Render a short receiver-facing note for incidents, docs, or review packets.
A good summary answers:

- what was captured,
- for how long or over which phase,
- with which backend,
- how trustworthy the attribution is,
- which metrics moved,
- and where the caveats are.

### `cargo memobs diff <old> <new>`
Compare two receipts or packs and classify:

- `capture_scope_changed`
- `backend_changed`
- `symbolization_fidelity_changed`
- `metric_budget_changed`
- `phase_boundary_changed`
- `regression_gate_changed`
- `manual_review_required`

### `cargo memobs pack`
Emit one compact `.memobs.zip` bundle for CI artifacts, incident handoff, release review, or support escalation.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.

- `memobs-core` — schema types, validation, diff logic, summary rendering, and shared vocabulary.
- `memobs-capture` — capture session model, receipt writing, artifact packing, redaction support.
- `memobs-leaktracer` — import/adapter for leaktracer-style allocator evidence.
- `memobs-dhat` — import/adapter for dhat-style scoped heap profiles.
- `memobs-jemalloc` — import/adapter for jemalloc stats and optional profile dumps.
- `cargo-memobs` — CLI.

Optional or later adapters should stay optional until the core vocabulary is trusted.

## Three artifact types that should be explicit in `0.1`

### `capture-scope.policy`
This is where maintainers say what the run *covers*.
Examples:

- `startup_cli`
- `single_operation`
- `steady_state_window`
- `background_phase`
- `whole_process_lifetime`
- `manual_review_required`

Without this file, memory captures drift into “interesting profile, unclear boundary”.

### `symbolization-fidelity.report`
This is where the crate records how trustworthy the call stacks and symbols really are.
Examples:

- `full_symbols`
- `trimmed_symbols`
- `partial_symbols`
- `allocator_stats_only`
- `stripped_binary`
- `manual_review_required`

This file matters because a pretty call tree and a stats-only sample are not equivalent evidence.

### `regression-gate.policy`
This is where maintainers say which metrics actually justify a failure or escalation.
Examples:

- `peak_rss_bytes`
- `live_bytes_after_phase`
- `alloc_count`
- `bytes_allocated_total`
- `heap_dump_growth_factor`
- `manual_review_required`

The purpose is to prevent teams from confusing “we captured something memory-related” with “we know what should gate a release”.

## Best proving grounds for `0.1`

Prioritize crates and applications where memory drift is real, but a full observability platform would be overkill:

- CLI or service crates with startup or steady-state RSS regressions,
- libraries whose allocation counts are easy to collect but whose live-memory story is easy to miss,
- jemalloc-based services that can produce allocator stats but not always callsite attribution,
- async systems where background work starts after the “interesting phase” unless scope boundaries are explicit,
- and teams that need a redaction-safe handoff artifact rather than another screenshot-heavy profiling ritual.

## Scenarios to support early

1. **Alloc count flat but peak RSS regresses** — because allocation counts alone can miss retained memory or fragmentation-like symptoms.
2. **Scoped profiler ends before background phase** — because phase boundaries are often the real bug in memory evidence.
3. **Allocator stats present but callsite attribution missing** — because backend capability should be explicit, not assumed.
4. **Redacted path or symbol output still diffable** — because support handoff often needs privacy without destroying comparability.

## Deliberately later

Leave these for follow-on work unless they become necessary for one proving-ground crate:

- always-on production collection,
- hosted dashboards,
- kernel-wide tracing orchestration,
- platform-specific privilege management,
- a universal visualization UI,
- and automatic leak diagnosis.

## What would make `0.1` successful

`0.1` is successful if a team can produce one small bundle that lets another person answer:

- *what exactly was profiled?*
- *which backend produced this evidence?*
- *how trustworthy is the attribution?*
- *which memory metric should we care about?*
- *and did that story change in the new release?*

That is enough to prove the missing layer is real.
