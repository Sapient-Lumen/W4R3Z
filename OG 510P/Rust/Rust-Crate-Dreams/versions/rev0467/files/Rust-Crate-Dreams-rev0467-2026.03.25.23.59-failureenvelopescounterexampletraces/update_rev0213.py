from pathlib import Path
root = Path('/mnt/data/rust_crate_dreams_work')
proposal = '''---
id: P-0518
title: Crate Observability Surface Pack Kit — signal catalogs, cost classes, redaction boundaries, and observability diffs for library authors
status: idea
domains: [crates, observability, tracing, opentelemetry, telemetry, dx, supportiveness, docs]
last_reviewed: 2026-03-17
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://tokio.rs/tokio/topics/tracing
  - https://docs.rs/tracing/latest/tracing/
  - https://docs.rs/tracing-subscriber/latest/tracing_subscriber/
  - https://opentelemetry.io/docs/languages/rust/
  - https://opentelemetry.io/docs/languages/rust/libraries/
  - https://opentelemetry.io/docs/concepts/semantic-conventions/
  - https://opentelemetry.io/docs/concepts/signals/logs/
---

# Problem

Rust now has a lot of observability substrate, but very little **crate-authored observability support**.

A downstream adopter can often discover that a crate uses `tracing`, or that an instrumentation crate exists, or that there are OpenTelemetry adapters in the ecosystem.
What they still usually cannot answer quickly is:

- **Which spans, events, metrics, or logs does this crate intentionally emit?**
- **Which fields are stable enough to alert/query on, and which are debug-only?**
- **What feature flags or runtime integrations are required to get meaningful signals?**
- **What is the likely cost of turning those signals on?**
- **Which attributes may contain identifiers, payload-derived values, or other sensitive material?**
- **How did the crate’s observability surface change across releases?**

That leaves teams reverse-engineering support surfaces from README snippets, sample dashboards, semiconventional field names, and trial-and-error subscriber configuration.

The missing crate is **not** another tracing subscriber, **not** another OpenTelemetry exporter, and **not** another schema linter.

The missing crate is the boring receiver-facing layer that lets a crate hand other people a **checked observability surface contract**.

# Why this moved now

Several current Rust and observability signals line up unusually well.

## 1. Rust’s own vision work now explicitly asks for more supportive crate interfaces

The December 2025 vision-doc work argues that Rust should expand extensibility to include **supportive interfaces from crates**, explicitly naming better diagnostics and guidance as part of the gap.
That same logic applies to observability support: a crate may already emit signals, but users still lack a stable support surface that tells them what those signals mean and how much trust to place in them.

## 2. The 2025 survey still says docs and code are the main learning surfaces

The 2025 State of Rust survey says online documentation remains the preferred canonical reference, followed by studying the code itself.
That means observability expectations left in issue comments, blog posts, or tribal ops lore are still effectively under-specified.

## 3. Rust already has meaningful tracing and telemetry substrate

Tokio’s tracing docs say `tracing` is a framework for collecting structured, event-based diagnostics and call out multiple downstream uses: OpenTelemetry export, Tokio Console, stdout/file logging, and profiling.
The `tracing` and `tracing-subscriber` docs show a rich existing ecosystem of layers, filters, formatters, and integration crates.
So the missing value is not “Rust cannot emit telemetry”.

## 4. OpenTelemetry keeps raising the expectation for stable signal meaning

OpenTelemetry semantic conventions are explicitly about common names for operations and data across codebases, libraries, and platforms.
Its logs docs say structured logs are preferred in production because stable schema makes them easier to validate, parse, correlate, and analyze at scale.
That makes **signal stability, naming, and redaction boundaries** part of the crate’s product surface, not just backend configuration.

## 5. Rust telemetry support is still fragmented at the library boundary

The OpenTelemetry Rust docs say traces, metrics, and logs are all still beta in Rust today.
The OpenTelemetry Rust “Using instrumentation libraries” page also says many libraries and frameworks are supported through instrumentation crates, but that as of August 2025 the docs team did not know of any Rust library with OpenTelemetry natively integrated by default.
That makes the boundary between crate authors, instrumentation crates, and downstream operators especially important.

# What it provides

- `observability-pack.toml` — versioned declaration of named signals, feature/runtime requirements, stability class, sampling assumptions, and redaction/cost notes.
- `signal-catalog.receipt.json` — observed inventory of spans, events, metrics, logs, targets, layers, and exporter-relevant integrations captured from code, tests, or instrumentation adapters.
- `observability-surface.report.json` — machine-readable summary of the crate’s intended observability surface grouped into stable, evolving, debug-only, and internal-only signals.
- `signal-cost.report.json` — records cost classes such as `always_on_low_cost`, `conditional_low_cost`, `debug_only`, `runtime_sensitive`, `allocator_sensitive`, `high_cardinality_risk`, and `manual_review_required`.
- `redaction-boundary.report.json` — records fields or attribute families that are explicitly safe, explicitly sensitive, hashed, sampled, truncated, or left to manual-review policies.
- `instrumentation-recipe.manifest.json` — commands, feature flags, subscriber/layer setup, runtime assumptions, and minimal examples for actually seeing the advertised surface.
- `observability-check.report.json` — verifies whether the advertised signals were observed under the stated recipe and whether declared stability/redaction classes are internally coherent.
- `observability-diff.report.json` — compares two versions and classifies `signal_added`, `signal_removed`, `field_renamed`, `stability_changed`, `cost_changed`, `redaction_changed`, `recipe_changed`, and `manual_review_boundary_changed`.
- `observability-notes.summary.md` — short human-facing summary rendered from the structured artifacts.
- `cargo observability-pack capture` — capture one crate’s observed surface.
- `cargo observability-pack check` — verify the declared surface.
- `cargo observability-pack diff <old> <new>` — compare two crate observability surfaces.
- `cargo observability-pack summary` — render a reviewable Markdown summary.

# What the crate should provide other people

1. **A stable signal catalog** instead of forcing users to grep for `span!`, `event!`, log keys, and exporter setup.
2. **Signal stability classes** so people know what is query-safe versus debug-only or internal.
3. **Checked setup recipes** so adopters can see how to actually activate meaningful signals.
4. **Redaction and sensitivity boundaries** so operators know which fields should be filtered, hashed, dropped, or treated as manual-review territory.
5. **Cost and cardinality honesty** so turning on telemetry does not feel like blind faith.
6. **Release-to-release diffs** so observability regressions become reviewable like API changes.
7. **Reusable import artifacts** for docs portals, pathfinder crates, runtime handoff packs, platform engineering dashboards, and org-specific telemetry governance.

# Persona / who it’s for

- library maintainers whose crates emit spans, events, metrics, or logs
- application teams deciding whether a dependency is operable enough to use in production
- platform/observability engineers trying to standardize ingestion and alerting
- docs/tool authors who want stable observability metadata instead of scraped prose
- release reviewers who need to detect telemetry drift without diffing raw code by hand

# Users & user stories

- **Service engineer**: “Show me which spans and fields this crate emits in the HTTP happy path, and which ones are stable enough to build dashboards on.”
- **Platform engineer**: “Tell me whether enabling this crate’s telemetry is low-cost, high-cardinality-risk, or backend-sensitive before I bless it for production.”
- **Security reviewer**: “Give me one artifact showing which fields may contain IDs, payload fragments, or secrets so I can decide what must be redacted.”
- **Library author**: “Publish one checked signal catalog so users stop asking which events are intended versus incidental.”
- **Release reviewer**: “Diff two versions and tell me whether signal names, field stability, or redaction boundaries changed.”

# Prior art (and why it’s insufficient)

- `tracing` provides spans, events, fields, feature flags, and ecosystem integrations.
- `tracing-subscriber` provides composable layers and filters.
- Tokio Console, JSON/logfmt formatters, vendor exporters, and many framework-specific crates expose signals in different ways.
- OpenTelemetry provides APIs/SDKs, semantic conventions, exporters, and instrumentation libraries.
- Telemetry-schema and semantic-convention linters help standardize emitted keys.
- Redaction policy crates or layers can scrub sensitive fields.

What remains missing is the joined, maintainer-authored artifact that says:

- these are the **named signals** this crate intentionally emits,
- these are the **stability classes** of those signals,
- these are the **recipes** required to see them,
- these are the **cost/cardinality** caveats,
- these are the **redaction boundaries**,
- and this is how the crate’s **observability surface changed** across releases.

That is a different lane from:

- **P-0509** task-first crate choice,
- **P-0510** capability contracts,
- **P-0511** shared interop profiles,
- **P-0512** compile-time guidance,
- **P-0513** runtime handoff bundles,
- **P-0517** performance envelopes,
- generic tracing/OTel setup kits,
- telemetry schema linting,
- or org-specific collector/backend governance.

# Design goals

1. **Receiver-facing first** — optimize for downstream users deciding whether they can operate this crate well.
2. **Signal-catalog over plumbing** — describe intended emitted signals rather than replacing telemetry stacks.
3. **Stability honesty** — let maintainers say which names and fields are stable, evolving, or internal.
4. **Redaction explicitness** — make sensitivity boundaries reviewable rather than leaving them to folklore.
5. **Cost honesty** — include overhead and cardinality caveats as part of the surface.
6. **Join, don’t replace** — import from `tracing`, `tracing-subscriber`, OpenTelemetry adapters, and tests rather than competing with them.
7. **Diffability** — make release-to-release observability drift explicit.

# MVP surface

- Minimal `observability-pack.toml` schema with named signals, classes, and recipe references.
- Import lane for `tracing` metadata discovered in tests/examples and selected instrumentation adapters.
- Signal stability vocabulary: `stable_query_surface`, `supported_but_evolving`, `debug_only`, `internal_only`, `manual_review_required`.
- Cost vocabulary: `always_on_low_cost`, `conditional_low_cost`, `debug_only`, `runtime_sensitive`, `allocator_sensitive`, `high_cardinality_risk`, `manual_review_required`.
- `observability-check.report.json` that records whether advertised signals were seen and whether declared recipes were reproducible.
- `observability-diff.report.json` for release-to-release surface drift.
- `cargo observability-pack summary` to render a short reviewable Markdown summary.

# Artifact vocabulary

## `observability-pack.toml`

```toml
schema_version = "0.1"
crate = "example-crate"

[[signal]]
name = "http.request"
kind = "span"
stability = "stable_query_surface"
recipe_ref = "recipes/http_server.toml"
cost_class = "conditional_low_cost"
redaction_class = "safe_by_default"

[[signal]]
name = "db.query.error"
kind = "event"
stability = "supported_but_evolving"
recipe_ref = "recipes/db_client.toml"
cost_class = "runtime_sensitive"
redaction_class = "manual_review_required"
```

## `signal-cost.report.json`

```json
{
  "schema_version": "0.1",
  "crate": "example-crate",
  "signals": [
    {
      "name": "http.request",
      "kind": "span",
      "cost_class": "conditional_low_cost",
      "cardinality_risk": "low",
      "notes": "emitted when tracing feature is enabled"
    },
    {
      "name": "db.query.error",
      "kind": "event",
      "cost_class": "runtime_sensitive",
      "cardinality_risk": "high",
      "notes": "statement text must be redacted or normalized before export"
    }
  ]
}
```

# Distinctive implementation shape

## Crates

- `obspack-core` — schemas, diff logic, summary rendering, stability/cost/redaction vocabularies.
- `obspack-capture` — imports from tests/examples, `tracing` metadata surfaces, and selected instrumentation adapters.
- `obspack-tracing` — tracing-specific capture helpers and signal normalization.
- `obspack-otel` — OpenTelemetry semantic-convention import and compatibility helpers.
- `cargo-observability-pack` — CLI.

## Stability vocabulary

- `stable_query_surface`
- `supported_but_evolving`
- `debug_only`
- `internal_only`
- `manual_review_required`

## Redaction vocabulary

- `safe_by_default`
- `contains_identifiers`
- `payload_derived`
- `hash_or_truncate`
- `drop_before_export`
- `manual_review_required`

## Cost vocabulary

- `always_on_low_cost`
- `conditional_low_cost`
- `debug_only`
- `runtime_sensitive`
- `allocator_sensitive`
- `high_cardinality_risk`
- `manual_review_required`

# Example scenario families

1. **HTTP server crate** — request/response spans, status/error events, latency histograms, stable route labels, and explicit user-ID redaction boundaries.
2. **Database client crate** — connection lifecycle spans, query events, pool metrics, SQL-text sensitivity rules, and cost/cardinality notes.
3. **CLI/batch crate** — startup/shutdown events, structured progress logs, and “debug-only” verbose instrumentation.
4. **Async library crate** — task lifecycle spans, queue-depth metrics, backpressure events, and runtime-specific caveats.

# Why this could be epic

Because it would give Rust a missing middle layer between:

- “this crate uses tracing / OpenTelemetry somewhere”,
- and “operators can actually trust and adopt the emitted signals.”

That matters for a huge spread of crate categories:

- HTTP frameworks and middleware,
- database clients,
- async runtimes and service abstractions,
- storage/network libraries,
- CLI tools,
- background workers,
- and high-level frameworks whose production readiness depends on predictable observability.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that let one crate declare five to twenty intended signals, attach setup/redaction/cost metadata to them, verify that those signals actually appear under named recipes, and emit one diffable `observability-pack` bundle.

# De-risk plan

1. Start with `tracing`-centric crates and test/example-driven capture rather than trying to infer every signal statically.
2. Keep the stability/cost/redaction vocabularies small and conservative.
3. Treat automatic field capture as best-effort; allow manual annotations.
4. Make unknown or manual-review classes first-class output instead of forcing fake certainty.

# Non-goals

- Not a replacement for `tracing`, `tracing-subscriber`, OpenTelemetry SDKs, or collectors.
- Not a full org telemetry governance platform.
- Not a vendor-specific backend integration suite.
- Not a profiler or benchmarking framework.
- Not a guarantee that emitted telemetry will never change.

# Architecture & API sketch

```rust
pub enum SignalStability {
    StableQuerySurface,
    SupportedButEvolving,
    DebugOnly,
    InternalOnly,
    ManualReviewRequired,
}

pub fn capture_signal_catalog(root: &Path) -> Result<SignalCatalogReceipt>;
pub fn verify_observability_pack(root: &Path, pack: &ObservabilityPack) -> Result<ObservabilityCheckReport>;
pub fn diff_observability_packs(old: &ObservabilityPack, new: &ObservabilityPack) -> ObservabilityDiffReport;
pub fn write_summary(report: &ObservabilitySurfaceReport, out: &Path) -> Result<()>;
```

Bundle draft: `observability-pack.toml`, `signal-catalog.receipt.json`, `observability-surface.report.json`, `signal-cost.report.json`, `redaction-boundary.report.json`, `instrumentation-recipe.manifest.json`, `observability-check.report.json`, `observability-diff.report.json`, `notes.md`.

# Maintenance & governance plan

- Track `tracing` and OpenTelemetry Rust ecosystem evolution closely.
- Keep vocabularies stable even when imported telemetry stacks change underneath them.
- Maintain fixture crates spanning HTTP, DB, CLI, and async-library patterns.
- Publish clear rules for when a signal may be classed as stable versus evolving or internal.

# Milestones

## 0.1
- core schemas
- `tracing` capture helpers
- summary renderer
- one HTTP and one DB fixture

## 0.2
- diffing across releases
- redaction-boundary report
- signal-cost report
- basic OpenTelemetry-semconv import helpers

## 1.0
- stable artifact vocabulary
- richer recipe checking
- import adapters for instrumentation crates
- public fixture corpus and docs examples

# Open questions

- How much signal discovery should be automatic versus annotation-based?
- What is the smallest stable vocabulary for “query-safe” versus “debug-only” telemetry?
- How should the crate treat framework-specific instrumentation crates that live outside the library being documented?
- Which cost classes are honest enough to be portable without pretending hardware and backend overhead are uniform?

# Sources

- Rust vision-doc post: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tokio tracing topic: https://tokio.rs/tokio/topics/tracing
- `tracing` docs: https://docs.rs/tracing/latest/tracing/
- `tracing-subscriber` docs: https://docs.rs/tracing-subscriber/latest/tracing_subscriber/
- OpenTelemetry Rust docs: https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry Rust instrumentation-libraries docs: https://opentelemetry.io/docs/languages/rust/libraries/
- OpenTelemetry semantic conventions docs: https://opentelemetry.io/docs/concepts/semantic-conventions/
- OpenTelemetry logs docs: https://opentelemetry.io/docs/concepts/signals/logs/
'''
lane = '''# Crate observability-surface lanes — 2026-03-17

This note keeps **P-0518 Crate Observability Surface Pack Kit** from collapsing into generic “better telemetry”, “better tracing setup”, or “better observability tooling”.

## The lane

**P-0518** is the crate-authored, receiver-facing artifact layer for:

- named emitted signals,
- setup recipes,
- stability classes,
- cost and cardinality caveats,
- redaction and sensitivity boundaries,
- and release-to-release observability-surface diffs.

It answers:

- “What telemetry does this crate intentionally emit?”
- “Which names and fields are stable enough to build alerts or dashboards on?”
- “What feature flags or adapters do I need to see those signals?”
- “What might this signal surface cost or leak?”
- “How did the crate’s observability surface change across releases?”

## What it is not

### 1. Not task-first crate choice

**P-0509** helps users decide which crate to start with.
**P-0518** helps users operate a crate they already chose or are reviewing.

### 2. Not producer-side capability contracts

**P-0510** is about what a crate claims to support in general.
**P-0518** is about the emitted telemetry surface and its operational meaning.

### 3. Not shared interop profiles

**P-0511** defines reusable compatibility boundaries across crates.
**P-0518** may import those profiles, but it is not itself an interop contract.

### 4. Not compile-time guidance or runtime handoff

**P-0512** and **P-0513** are supportiveness lanes around failure and recovery.
**P-0518** is about what operators can observe before, during, and around runtime, not the bundle handed off after a failure is already being triaged.

### 5. Not upgrade, off-ramp, config-scenario, or performance packs

**P-0514**, **P-0515**, **P-0516**, and **P-0517** are about migration, leaving a crate, setup recipes, and performance posture.
**P-0518** may reference those lanes, but it is specifically about emitted signals and their meaning.

### 6. Not tracing/telemetry plumbing

`tracing`, `tracing-subscriber`, OpenTelemetry SDKs, exporters, and setup kits are the plumbing and wiring.
**P-0518** sits above them as the contract layer that says what signals matter and how trustworthy they are.

### 7. Not telemetry schema linting or semantic-convention governance

Schema-lint and semantic-convention tools help standardize names and keys.
**P-0518** is broader and more product-facing: it says which signals a crate intends to expose, not just whether the names were well chosen.

### 8. Not generic redaction policy tooling

Redaction policy crates can scrub sensitive data.
**P-0518** instead records which signal families are safe, sensitive, hashed, truncated, or manual-review territory for one crate’s intended surface.

### 9. Not full observability platforms

Collectors, vendor backends, dashboards, and org-wide governance systems are broader operational stacks.
**P-0518** is a portable crate-support artifact, not a platform replacement.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **task-first crate choice**,
2. **general support/interop claims**,
3. **shared interop profiles**,
4. **compile-time guidance**,
5. **runtime handoff**,
6. **upgrade/off-ramp support**,
7. **configuration/setup scenarios**,
8. **performance envelopes**,
9. **observability-surface contracts**,
10. **telemetry plumbing / schema governance / redaction tooling**,
11. or **full observability platforms**.

Do **not** let the archive quietly rephrase observability-surface contracts as “better tracing setup”, “better OpenTelemetry support”, or “better dashboards”.
'''
frontier = '''# Frontier salience scan — 2026-03-17 (crate observability surfaces promoted as the operability-support lane)

This pass added a new top-level proposal: **P-0518 Crate Observability Surface Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a tenth distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), **P-0513** (runtime handoff/support bundles), **P-0514** (release-to-release upgrade packs), **P-0515** (deprecation/successor off-ramp packs), **P-0516** (configuration/setup scenarios), and **P-0517** (performance envelopes).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another tracing subscriber,
- another OpenTelemetry exporter,
- another schema linter,
- another redaction layer,
- another dashboard,
- or another “one-line telemetry init” facade.

It is the boring crate that can hand other people:

- one **observability pack**,
- one **signal-catalog receipt**,
- one **observability-surface report**,
- one **signal-cost report**,
- one **redaction-boundary report**,
- one **instrumentation-recipe manifest**,
- one **observability-check report**,
- and one **observability diff**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0516 Crate Configuration Scenario Pack Kit**
7. **P-0517 Crate Performance Envelope Pack Kit**
8. **P-0518 Crate Observability Surface Pack Kit**
9. **P-0512 Crate Guidance Pack Kit**
10. **P-0513 Crate Runtime Handoff Pack Kit**
11. **P-0515 Crate Off-Ramp Pack Kit**
12. **P-0510 Crate Capability Contract & Interop Profile Kit**
13. **P-0511 Crate Interop Profile Pack Kit**
14. **P-0429 rustc_public Analysis Workbench Kit**
15. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0518 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, and emitted telemetry is a real missing support surface for production adopters.
- The 2025 survey says **docs and code** are still the main learning surfaces, so observability support left in ops lore or issue comments remains under-specified.
- Tokio’s tracing docs and the `tracing` / `tracing-subscriber` docs show Rust already has rich structured diagnostics substrate, which means the missing value is not “Rust cannot emit telemetry”.
- OpenTelemetry semantic conventions exist precisely to make names and meanings consistent across codebases and platforms, which makes signal stability a real review surface.
- OpenTelemetry’s logs guidance says structured logs are preferred in production because stable schemas are easier to validate, correlate, and analyze.
- OpenTelemetry Rust still documents traces, metrics, and logs as beta, and its Rust instrumentation-libraries page still highlights a library-boundary fragmentation story rather than a single stable native-integration default.

That means the lane is both:

- **timely** — because the telemetry substrate is mature enough that the next missing value is signal-contract honesty,
- and **distinct** — because the missing value is a crate-authored observability surface above tracing/OTel plumbing and below org-wide telemetry governance.

## What changed in the archive

Added:
- `proposals/crate-observability-surface-pack-kit.md`
- `meta/crate-observability-surface-lanes-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-33.md`
- `fixtures/crate-observability-surface-pack-kit/`
- `entries/2026-03-17-204.md`

Updated:
- `README.md`
- `INDEX.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- task-first crate choice,
- support / interop claims,
- shared ecosystem profiles,
- compile-time guidance,
- runtime handoff,
- upgrade packs,
- off-ramp packs,
- configuration scenarios,
- performance envelopes,
- tracing/OTel plumbing,
- telemetry schema governance,
- and full observability platforms

into one fake “Rust telemetry solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://tokio.rs/tokio/topics/tracing
- https://docs.rs/tracing/latest/tracing/
- https://docs.rs/tracing-subscriber/latest/tracing_subscriber/
- https://opentelemetry.io/docs/languages/rust/
- https://opentelemetry.io/docs/languages/rust/libraries/
- https://opentelemetry.io/docs/concepts/semantic-conventions/
- https://opentelemetry.io/docs/concepts/signals/logs/
'''
entry = '''# Entry 204 — crate observability surfaces promoted as the operability-support lane

This pass added a new top-level proposal: **P-0518 Crate Observability Surface Pack Kit**.
It also added the lane-boundary and fixture scaffolding needed to stop future passes from collapsing telemetry wiring, semantic-convention linting, redaction tooling, dashboarding, and receiver-facing crate observability support into one fake “better telemetry” story.

## Why this moved now

Several current Rust and observability signals line up unusually well.

### 1. The ecosystem-supportiveness frontier still lacked a good observability-support lane

The archive already had stronger answers for:

- **task-first crate choice** via **P-0509**,
- **producer-side support / interop claims** via **P-0510**,
- **shared interop profile contracts** via **P-0511**,
- **compile-time / early-failure guidance** via **P-0512**,
- **runtime failure handoff** via **P-0513**,
- **release-to-release migration** via **P-0514**,
- **successor / off-ramp support** via **P-0515**,
- **setup/configuration scenarios** via **P-0516**,
- and **performance envelopes** via **P-0517**.

But it still lacked a good answer to:

- “Once a team chose and configured a crate, what exactly does the crate hand them so they can understand, enable, trust, and review its emitted telemetry surface?”

That left the archive with better answers for **choice**, **setup**, **migration**, **failure**, and **performance** than for **production observability posture**, which is strange for a language used heavily in services and infrastructure.

### 2. Official substrate makes this a contract problem, not a missing-telemetry-knobs problem

Tokio’s tracing docs already frame `tracing` as structured, event-based diagnostics with spans and events and point to real downstream uses like OpenTelemetry export, Tokio Console, logging, and profiling.
The `tracing` and `tracing-subscriber` docs already expose rich ecosystem integrations, composable layers, filters, and multiple output modes.
OpenTelemetry Rust already has traces, metrics, and logs surfaces, plus semantic conventions and instrumentation libraries.

That means the sharper question is no longer “how do we do telemetry in Rust at all?” but “what portable artifact should sit above today’s telemetry substrate so a crate can tell downstream users what it actually emits and what those signals mean?”

### 3. Current telemetry tooling is real but still fragmented at the library boundary

The OpenTelemetry Rust docs explicitly point people toward instrumentation libraries for dependencies.
The same page says that as of August 2025 the docs team did not know of any Rust library with native OpenTelemetry integration by default.
Meanwhile OpenTelemetry semantic conventions and structured-log guidance keep pushing the ecosystem toward stable signal meaning.

What is still missing is the boring pack that can say:

- these are the named signals we intend to emit,
- these are the feature/runtime conditions required to see them,
- these names and fields are stable enough for queries and alerts,
- these ones are debug-only or evolving,
- these fields are sensitive or high-cardinality,
- and this is how the signal surface changed across releases.

### 4. Rust’s current official messaging makes “supportive observability surfaces” more plausible than before

The vision-doc work explicitly recommends more **supportive interfaces from crates**.
The 2025 survey says docs and source remain the main learning surfaces.
That combination makes it more credible to treat signal catalogs, redaction notes, and observability drift as part of a crate’s product surface rather than as backend-specific folklore.

## Repository changes

### New proposal
- Added **P-0518 Crate Observability Surface Pack Kit**.

### New boundary note
- Added `meta/crate-observability-surface-lanes-2026-03-17.md` so future passes keep these lanes distinct:
  - task-first crate choice,
  - support / interop claims,
  - shared interop profiles,
  - compile/runtime supportiveness,
  - configuration scenarios,
  - performance envelopes,
  - observability-surface contracts,
  - tracing/OTel plumbing,
  - schema/redaction tooling,
  - and full observability platforms.

### New fixtures
- Added `fixtures/crate-observability-surface-pack-kit/` with a first artifact vocabulary:
  - `observability-pack.schema.json`
  - `signal-catalog.receipt.schema.json`
  - `observability-surface.report.schema.json`
  - `signal-cost.report.schema.json`
  - `redaction-boundary.report.schema.json`
  - `instrumentation-recipe.manifest.schema.json`
  - `observability-check.report.schema.json`
  - `observability-diff.report.schema.json`
- Added starter scenario notes for:
  - `http_server`
  - `db_client`
  - `cli_batch`

### Repo-memory updates
Updated:
- `README.md`
- `INDEX.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`
- `meta/frontier-salience-2026-03-17-33.md`

## Main judgment after the pass

The worthy crate here is not another subscriber or exporter.
It is the boring contract layer that can hand other people:

- one **observability pack**,
- one **signal-catalog receipt**,
- one **surface report**,
- one **cost report**,
- one **redaction-boundary report**,
- one **instrumentation recipe manifest**,
- one **observability check report**,
- and one **observability diff**.
'''
research = '''## 2026-03-17 refresh — crate observability-surface pass (204)

### Sources consulted
- Rust vision-doc post: “What do people love about Rust?”
- 2025 State of Rust survey results
- Tokio tracing topic docs
- `tracing` docs
- `tracing-subscriber` docs
- OpenTelemetry Rust docs
- OpenTelemetry Rust instrumentation-libraries docs
- OpenTelemetry semantic-conventions docs
- OpenTelemetry logs docs

### Kept together
- the distinction between **observability-surface contracts** and generic telemetry plumbing
- the fact that Rust already has real tracing/OTel substrate, which changes the missing-crate question
- the fact that docs/source remain the main learning path, making emitted-signal expectations part of the product rather than an afterthought
- the need to keep schema linting, redaction tooling, and full observability platforms separate from a crate-authored signal contract

### Result
- Added a new top-level proposal: **P-0518 Crate Observability Surface Pack Kit**.
- Added a crate-observability-surface lane-boundary note.
- Added fixture/schema stubs for **P-0518** so the proposal now has concrete pack/receipt/report/recipe/cost/redaction/diff surfaces.
- Updated the crate-frontier map and repo-memory files so future passes do not rediscover this seam under “better tracing setup”, “better OpenTelemetry support”, or “better dashboards”.

### Freshness anchors
- Re-check the vision-doc and survey language before repeating the same supportiveness priorities later on.
- Re-check Tokio/tracing/tracing-subscriber docs before claiming the same substrate later on.
- Re-check OpenTelemetry Rust status and instrumentation-library guidance before assuming the same fragmentation story later on.
- Re-check semantic-convention and logs guidance before assuming the same schema-stability posture later on.

### Common false gap patterns from this pass
1. “Rust needs better telemetry plumbing” when the sharper gap is a **crate-authored observability surface with stability, cost, and redaction boundaries**.
2. “`tracing` / OpenTelemetry already solve this” when they mostly solve emission and transport substrate rather than the joined receiver-facing contract.
3. “Schema linting already solves this” when naming conventions are not the same thing as a crate-authored signal catalog.
4. “Dashboards prove operability” when dashboards are downstream views, not a portable support artifact.

'''
roadmap = '''## 2026-03-17 refresh — crate observability-surface lane joins the ecosystem-supportiveness frontier

This pass added **P-0518 Crate Observability Surface Pack Kit** and should further change how the repo thinks about “ecosystem supportiveness”.

### Main judgment
- The archive now has **ten** distinct ecosystem-supportiveness lanes:
  - **P-0509** task-first crate choice,
  - **P-0516** present-tense configuration/setup scenario support,
  - **P-0517** performance-envelope support,
  - **P-0518** observability-surface support,
  - **P-0514** release-to-release upgrade support,
  - **P-0512** compile-time / early-failure guidance,
  - **P-0513** runtime failure handoff,
  - **P-0515** successor / deprecation / off-ramp support,
  - **P-0510** producer-side capability contracts,
  - **P-0511** shared ecosystem interop profiles.
- The missing value for **P-0518** is not generic tracing/OTel setup and not semantic-convention linting by itself. It is the boring workflow that turns a crate’s intended emitted telemetry into **observability packs, signal-catalog receipts, cost/redaction reports, checked recipes, and surface diffs**.

### Working rule
- Keep **P-0518** separate from telemetry plumbing: wiring a subscriber or exporter is not the same lane as publishing a stable signal catalog.
- Keep **P-0518** separate from schema linting: naming rules are not the same thing as a receiver-facing surface contract.
- Keep **P-0518** separate from redaction tooling: generic scrubbing is not the same thing as declaring one crate’s sensitivity boundaries.
- Keep **P-0518** separate from **P-0513**: runtime-failure handoff is not the same lane as present-tense observability support.
- Keep **P-0518** separate from **P-0517**: performance posture is not the same thing as emitted signal posture.

'''
llm = '''## Added 2026-03-17 (204): crate observability-surface layering discipline

When a proposal touches **crate observability support**, future revisions must state explicitly whether the missing value is primarily about:

1. **telemetry plumbing** (subscribers, exporters, env/config wiring),
2. **schema governance** (semantic conventions, field naming, linting),
3. **redaction / privacy policy tooling**,
4. **receiver-facing observability-surface contracts** (named signals, stability, cost, sensitivity, recipes, diffs),
5. or a **full observability platform** (collector/backend/dashboard governance).

Do not let the archive silently collapse “this crate emits telemetry”, “this crate’s signals are stable enough to rely on”, and “this org can govern telemetry at scale” into one vague observability story. The strongest missing crates here are often **contract layers above plumbing and below platforms**.

'''
known = '''## Added 2026-03-17 (204)

### Crate observability-surface substrate
- Tokio’s tracing topic docs say `tracing` is a framework for collecting structured, event-based diagnostic information and highlight downstream uses like OpenTelemetry export, Tokio Console, logging, and profiling. https://tokio.rs/tokio/topics/tracing
- `tracing` docs list a wide ecosystem of integrations, including `tracing-subscriber`, OpenTelemetry export, framework middleware, and multiple formatter/output layers. https://docs.rs/tracing/latest/tracing/
- `tracing-subscriber` docs show composable `Layer` and `Filter` abstractions, JSON/fmt/env-filter support, and `no_std`-aware layering surface. https://docs.rs/tracing-subscriber/latest/tracing_subscriber/
- OpenTelemetry Rust docs say traces, metrics, and logs are all currently beta in Rust. https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry semantic-conventions docs define common names for operations and data across libraries and platforms. https://opentelemetry.io/docs/concepts/semantic-conventions/
- OpenTelemetry logs docs say structured logs are preferred in production because stable schemas are easier to validate, parse, correlate, and analyze at scale. https://opentelemetry.io/docs/concepts/signals/logs/
- OpenTelemetry Rust instrumentation-libraries docs say many libraries/frameworks are supported through instrumentation crates, and as of that page’s August 2025 update the docs did not know of any Rust library with OpenTelemetry natively integrated by default. https://opentelemetry.io/docs/languages/rust/libraries/

**Conclusion:** the gap is **not** “Rust cannot do telemetry” and not “Rust lacks schema guidance.” The sharper gap is a **crate-authored observability-surface contract** above today’s tracing/OTel substrate, schema guidance, and instrumentation crates.

'''
(root/'proposals'/'crate-observability-surface-pack-kit.md').write_text(proposal)
(root/'meta'/'crate-observability-surface-lanes-2026-03-17.md').write_text(lane)
(root/'meta'/'frontier-salience-2026-03-17-33.md').write_text(frontier)
(root/'entries'/'2026-03-17-204.md').write_text(entry)
fx=root/'fixtures'/'crate-observability-surface-pack-kit'
fx.mkdir(parents=True, exist_ok=True)
schemas={
'observability-pack.schema.json':'{\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\n  "title": "ObservabilityPack",\n  "type": "object",\n  "required": ["schema_version", "crate", "signals"],\n  "properties": {\n    "schema_version": {"type": "string"},\n    "crate": {"type": "string"},\n    "signals": {\n      "type": "array",\n      "items": {\n        "type": "object",\n        "required": ["name", "kind", "stability", "recipe_ref"],\n        "properties": {\n          "name": {"type": "string"},\n          "kind": {"enum": ["span", "event", "metric", "log"]},\n          "stability": {"enum": ["stable_query_surface", "supported_but_evolving", "debug_only", "internal_only", "manual_review_required"]},\n          "recipe_ref": {"type": "string"},\n          "cost_class": {"type": "string"},\n          "redaction_class": {"type": "string"}\n        }\n      }\n    }\n  }\n}\n',
'signal-catalog.receipt.schema.json':'{\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\n  "title": "SignalCatalogReceipt",\n  "type": "object",\n  "required": ["schema_version", "crate", "signals_observed"],\n  "properties": {\n    "schema_version": {"type": "string"},\n    "crate": {"type": "string"},\n    "signals_observed": {\n      "type": "array",\n      "items": {\n        "type": "object",\n        "required": ["name", "kind"],\n        "properties": {\n          "name": {"type": "string"},\n          "kind": {"enum": ["span", "event", "metric", "log"]},\n          "feature_conditions": {"type": "array", "items": {"type": "string"}},\n          "targets": {"type": "array", "items": {"type": "string"}}\n        }\n      }\n    }\n  }\n}\n',
'observability-surface.report.schema.json':'{\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\n  "title": "ObservabilitySurfaceReport",\n  "type": "object",\n  "required": ["schema_version", "crate", "summary"],\n  "properties": {\n    "schema_version": {"type": "string"},\n    "crate": {"type": "string"},\n    "summary": {\n      "type": "object",\n      "properties": {\n        "stable_query_surface": {"type": "integer"},\n        "supported_but_evolving": {"type": "integer"},\n        "debug_only": {"type": "integer"},\n        "internal_only": {"type": "integer"},\n        "manual_review_required": {"type": "integer"}\n      }\n    }\n  }\n}\n',
'signal-cost.report.schema.json':'{\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\n  "title": "SignalCostReport",\n  "type": "object",\n  "required": ["schema_version", "crate", "signals"],\n  "properties": {\n    "schema_version": {"type": "string"},\n    "crate": {"type": "string"},\n    "signals": {\n      "type": "array",\n      "items": {\n        "type": "object",\n        "required": ["name", "cost_class"],\n        "properties": {\n          "name": {"type": "string"},\n          "cost_class": {"enum": ["always_on_low_cost", "conditional_low_cost", "debug_only", "runtime_sensitive", "allocator_sensitive", "high_cardinality_risk", "manual_review_required"]},\n          "cardinality_risk": {"enum": ["low", "medium", "high", "manual_review_required"]},\n          "notes": {"type": "string"}\n        }\n      }\n    }\n  }\n}\n',
'redaction-boundary.report.schema.json':'{\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\n  "title": "RedactionBoundaryReport",\n  "type": "object",\n  "required": ["schema_version", "crate", "rules"],\n  "properties": {\n    "schema_version": {"type": "string"},\n    "crate": {"type": "string"},\n    "rules": {\n      "type": "array",\n      "items": {\n        "type": "object",\n        "required": ["signal_name", "field_glob", "redaction_class"],\n        "properties": {\n          "signal_name": {"type": "string"},\n          "field_glob": {"type": "string"},\n          "redaction_class": {"enum": ["safe_by_default", "contains_identifiers", "payload_derived", "hash_or_truncate", "drop_before_export", "manual_review_required"]},\n          "notes": {"type": "string"}\n        }\n      }\n    }\n  }\n}\n',
'instrumentation-recipe.manifest.schema.json':'{\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\n  "title": "InstrumentationRecipeManifest",\n  "type": "object",\n  "required": ["schema_version", "recipes"],\n  "properties": {\n    "schema_version": {"type": "string"},\n    "recipes": {\n      "type": "array",\n      "items": {\n        "type": "object",\n        "required": ["name", "command"],\n        "properties": {\n          "name": {"type": "string"},\n          "command": {"type": "string"},\n          "feature_flags": {"type": "array", "items": {"type": "string"}},\n          "runtime_notes": {"type": "array", "items": {"type": "string"}}\n        }\n      }\n    }\n  }\n}\n',
'observability-check.report.schema.json':'{\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\n  "title": "ObservabilityCheckReport",\n  "type": "object",\n  "required": ["schema_version", "crate", "status"],\n  "properties": {\n    "schema_version": {"type": "string"},\n    "crate": {"type": "string"},\n    "status": {"enum": ["pass", "warn", "manual_review_required", "fail"]},\n    "findings": {"type": "array", "items": {"type": "string"}}\n  }\n}\n',
'observability-diff.report.schema.json':'{\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\n  "title": "ObservabilityDiffReport",\n  "type": "object",\n  "required": ["schema_version", "changes"],\n  "properties": {\n    "schema_version": {"type": "string"},\n    "changes": {\n      "type": "array",\n      "items": {\n        "type": "object",\n        "required": ["kind", "subject"],\n        "properties": {\n          "kind": {"enum": ["signal_added", "signal_removed", "field_renamed", "stability_changed", "cost_changed", "redaction_changed", "recipe_changed", "manual_review_boundary_changed"]},\n          "subject": {"type": "string"},\n          "notes": {"type": "string"}\n        }\n      }\n    }\n  }\n}\n'
}
for name,text in schemas.items(): (fx/name).write_text(text)
for name,text in {
'http_server/README.md':'# HTTP server scenario\n\nFocus: request spans, status/error events, route labels, stable query fields, and explicit user/session redaction boundaries.\n',
'db_client/README.md':'# DB client scenario\n\nFocus: connection lifecycle spans, query-error events, pool metrics, high-cardinality SQL/text hazards, and cost classes for verbose instrumentation.\n',
'cli_batch/README.md':'# CLI / batch scenario\n\nFocus: startup/shutdown logs, structured progress logs, and the difference between always-on user-facing logs and debug-only diagnostics.\n',
}.items():
    p=fx/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text)
for rel,section in [('meta/research-ledger.md',research),('meta/roadmap.md',roadmap),('meta/llm-hygiene.md',llm),('meta/known-existing.md',known)]:
    p=root/rel; p.write_text(section+p.read_text())
readme=(root/'README.md').read_text()
needle='For crate-authored performance-support / benchmark-honesty work specifically, also consult `meta/crate-performance-envelope-lanes-2026-03-17.md` so configuration scenarios, performance envelopes, generic benchmark frameworks, profiling bundles, and hosted CI perf services do not get collapsed into one fake perf-support lane.'
readme=readme.replace(needle, needle+' For crate-authored observability-surface support specifically, also consult `meta/crate-observability-surface-lanes-2026-03-17.md` so observability-surface contracts, telemetry plumbing, semantic-convention linting, redaction tooling, and full observability platforms do not get collapsed into one fake telemetry-support lane.')
readme=readme.replace('For a tighter ranked view of the current narrow frontier, see `meta/frontier-salience-2026-03-08-33.md`; for the broader cross-domain portfolio view, see `meta/frontier-salience-2026-03-17-32.md`,', 'For a tighter ranked view of the current narrow frontier, see `meta/frontier-salience-2026-03-08-33.md`; for the broader cross-domain portfolio view, see `meta/frontier-salience-2026-03-17-33.md`, `meta/frontier-salience-2026-03-17-32.md`,')
(root/'README.md').write_text(readme)
cfm=(root/'meta/crate-frontier-map-2026-03-16.md').read_text()
cfm=cfm.replace('- `proposals/crate-performance-envelope-pack-kit.md` (**P-0517**)', '- `proposals/crate-performance-envelope-pack-kit.md` (**P-0517**)\n- `proposals/crate-observability-surface-pack-kit.md` (**P-0518**)')
cfm=cfm.replace('- **P-0517** is the sharpest performance-support lane next to it: it answers what performance tradeoff a downstream user is actually buying, which metric is authoritative, and where benchmark honesty stops.', '- **P-0517** is the sharpest performance-support lane next to it: it answers what performance tradeoff a downstream user is actually buying, which metric is authoritative, and where benchmark honesty stops.\n- **P-0518** is the sharpest operability/observability-support lane next to it: it answers what telemetry a downstream user can actually expect, which names are stable enough to rely on, and where cost or sensitivity boundaries begin.')
(root/'meta/crate-frontier-map-2026-03-16.md').write_text(cfm)
index=(root/'INDEX.md').read_text()
index=index.replace('- **P-0517** — `proposals/crate-performance-envelope-pack-kit.md` — Crate Performance Envelope Pack Kit — checked workload profiles, budget receipts, and perf diffs for library authors', '- **P-0517** — `proposals/crate-performance-envelope-pack-kit.md` — Crate Performance Envelope Pack Kit — checked workload profiles, budget receipts, and perf diffs for library authors\n- **P-0518** — `proposals/crate-observability-surface-pack-kit.md` — Crate Observability Surface Pack Kit — signal catalogs, cost/redaction receipts, and observability diffs for library authors')
index=index.replace('- **Entry 203** — `entries/2026-03-17-203.md` — crate performance envelopes promoted as the performance-support lane', '- **Entry 203** — `entries/2026-03-17-203.md` — crate performance envelopes promoted as the performance-support lane\n- **Entry 204** — `entries/2026-03-17-204.md` — crate observability surfaces promoted as the operability-support lane')
(root/'INDEX.md').write_text(index)
