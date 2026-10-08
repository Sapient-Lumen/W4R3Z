---
id: P-0518
title: Crate Observability Surface Pack Kit — signal catalogs, route/delivery truth, cost classes, redaction boundaries, and observability diffs for library authors
status: idea
domains: [crates, observability, tracing, opentelemetry, telemetry, dx, supportiveness, docs]
last_reviewed: 2026-03-20
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://tokio.rs/tokio/topics/tracing
  - https://docs.rs/tracing/latest/tracing/
  - https://docs.rs/tracing-subscriber/latest/tracing_subscriber/
  - https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html
  - https://docs.rs/tracing-appender/latest/tracing_appender/non_blocking/
  - https://docs.rs/opentelemetry_sdk/latest/opentelemetry_sdk/trace/struct.SdkTracerProvider.html
  - https://docs.rs/opentelemetry_sdk/latest/opentelemetry_sdk/logs/struct.SdkLoggerProvider.html
  - https://opentelemetry.io/docs/concepts/sampling/
  - https://docs.rs/opentelemetry/latest/opentelemetry/
  - https://docs.rs/opentelemetry-appender-tracing/latest/opentelemetry_appender_tracing/
  - https://docs.rs/console-subscriber/latest/console_subscriber/
  - https://docs.rs/tracing-opentelemetry/latest/tracing_opentelemetry/
  - https://opentelemetry.io/docs/languages/rust/
  - https://opentelemetry.io/docs/languages/rust/libraries/
  - https://opentelemetry.io/docs/concepts/semantic-conventions/
  - https://opentelemetry.io/docs/specs/otel/schemas/
  - https://opentelemetry.io/docs/specs/otel/common/instrumentation-scope/
  - https://opentelemetry.io/docs/concepts/signals/logs/
  - https://opentelemetry.io/docs/security/handling-sensitive-data/
---

# Problem

Rust now has a lot of observability substrate, but very little **crate-authored observability support**.

A downstream adopter can often discover that a crate uses `tracing`, or that an instrumentation crate exists, or that there are OpenTelemetry adapters in the ecosystem.
What they still usually cannot answer quickly is:

- **Which spans, events, metrics, or logs does this crate intentionally emit?**
- **Which fields are stable enough to alert/query on, and which are debug-only?**
- **What feature flags or runtime integrations are required to get meaningful signals?**
- **Which route actually carries those signals — fmt/log output, console, OpenTelemetry traces, OpenTelemetry metrics, or some separate log bridge?**
- **What kind of delivery/completeness claim is honest once buffering, loss, sampling, aggregation windows, and exit/flush behavior are accounted for?**
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

## 6. Route truth still is not delivery truth

Current Rust telemetry substrate makes an ordinary overclaim easy:

a crate can honestly say that a signal family reaches `fmt`, OpenTelemetry traces, OpenTelemetry metrics, or OpenTelemetry logs,
while still leaving another team unable to tell whether that route is blocking, lossy, sampled, periodically aggregated, or dependent on clean shutdown / `force_flush`.

That matters because:

- `tracing_appender::non_blocking` defaults to **lossy** buffering and exposes dropped-line counters rather than guaranteeing complete delivery;
- `WorkerGuard` exists specifically because buffered logs/events may not be written on abrupt termination;
- OpenTelemetry tracing/logging providers expose explicit `force_flush` and shutdown surfaces for remaining buffered data;
- metrics are aggregated in memory and periodically exported rather than emitted downstream as one raw event per measurement;
- and sampling explicitly means some traces/spans are not processed or exported at all.

So the missing value is not only “which route exists?” but also “what another team may honestly rely on from that route?”.

# Main judgment

See also `meta/crate-observability-surface-product-plan-2026-03-19.md` for the current implementation-ready `0.1` sketch.

A worthy crate here should provide a receiver-facing answer to:

1. **Which signals does this crate intentionally emit?**
2. **Which of those signals are stable enough to query or alert on?**
3. **What feature flags, filters, layers, runtimes, or exporter bridges are required to actually see them?**
4. **Which bridge route actually carries those signals — fmt/log output, console, traces, metrics, logs, or only manual-review territory?**
5. **What delivery/completeness posture is actually honest for those routes — blocking, lossy, sampled, periodic, flush-dependent, or manual-review territory?**
6. **Which semantic-convention or schema posture is the crate claiming for those signals?**
7. **Which fields are safe, sensitive, payload-derived, or otherwise manual-review territory?**
8. **What is the likely cost/cardinality posture of turning the signals on?**
9. **How did that observability surface change across releases?**

That is more valuable than leaving users to reconstruct signal meaning from code, subscribers, exporter docs, and production archaeology.

# What it provides

- `observability-pack.toml` — versioned declaration of named signals, feature/runtime requirements, stability class, sampling assumptions, and redaction/cost notes.
- `signal-catalog.receipt.json` — observed inventory of spans, events, metrics, logs, targets, layers, and exporter-relevant integrations captured from code, tests, or instrumentation adapters.
- `observability-surface.report.json` — machine-readable summary of the crate’s intended observability surface grouped into stable, evolving, debug-only, and internal-only signals.
- `signal-cost.report.json` — records cost classes such as `always_on_low_cost`, `conditional_low_cost`, `debug_only`, `runtime_sensitive`, `allocator_sensitive`, `high_cardinality_risk`, and `manual_review_required`.
- `redaction-boundary.report.json` — records fields or attribute families that are explicitly safe, explicitly sensitive, hashed, sampled, truncated, or left to manual-review policies.
- `instrumentation-recipe.manifest.json` — commands, feature flags, subscriber/layer setup, runtime assumptions, and minimal examples for actually seeing the advertised surface.
- `signal-stability.policy.json` — explicit meaning and minimum evidence for `stable_query_surface`, `supported_but_evolving`, `debug_only`, `internal_only`, and `manual_review_required`.
- `activation-recipe.receipt.json` — declared or observed feature flags, env vars, filters, layers, runtime assumptions, cfgs, and exporter bridges actually required to surface the signals.
- `bridge-route.receipt.json` — records which routes actually carry which signal families to fmt/log output, console, traces, metrics, or logs.
- `delivery-posture.receipt.json` — records whether a signal family is blocking, backpressure-buffered, lossy-buffered, batch-exported, periodically exported, sampled, or still manual-review territory.
- `completeness-class.report.json` — records whether another team should interpret a signal family as `attempted_all_events`, `best_effort_buffered`, `representative_sample`, `aggregated_window`, `exit_sensitive`, or `manual_review_required`.
- `schema-convention.profile.json` — semantic-convention domain, schema URL, custom-extension posture, and query-compatibility expectation for a signal family.
- `observability-check.report.json` — verifies whether the advertised signals were observed under the stated recipe and whether declared stability/redaction classes are internally coherent.
- `observability-diff.report.json` — compares two versions and classifies `signal_added`, `signal_removed`, `field_renamed`, `stability_changed`, `cost_changed`, `redaction_changed`, `recipe_changed`, and `manual_review_boundary_changed`.
- `observability-notes.summary.md` — short human-facing summary rendered from the structured artifacts.
- `cargo observability-pack capture` — capture one crate’s observed surface.
- `cargo observability-pack check` — verify the declared surface.
- `cargo observability-pack diff <old> <new>` — compare two crate observability surfaces.
- `cargo observability-pack summary` — render a reviewable Markdown summary.
- `cargo observability-pack doctor` — render suspicious route/delivery/completeness situations for human review.

# What the crate should provide other people

1. **A stable signal catalog** instead of forcing users to grep for `span!`, `event!`, log keys, and exporter setup.
2. **Signal stability classes** so people know what is query-safe versus debug-only or internal.
3. **Checked setup recipes** so adopters can see how to actually activate meaningful signals.
4. **Activation honesty** so teams can tell “visible by default” apart from “requires a feature flag, `RUST_LOG` directive, named layer, runtime feature, or exporter bridge”.
5. **Bridge-route honesty** so teams can tell fmt/log output, console routes, OpenTelemetry trace routes, OpenTelemetry metric routes, and absent log routes apart instead of assuming one bridge covers everything.
6. **Schema/convention posture** so integrators know which signals follow OpenTelemetry semantic conventions, which are crate-specific, and when schema drift matters.
7. **Redaction and sensitivity boundaries** so operators know which fields should be filtered, hashed, dropped, or treated as manual-review territory.
8. **Cost and cardinality honesty** so turning on telemetry does not feel like blind faith.
9. **Release-to-release diffs** so observability regressions become reviewable like API changes.
10. **Reusable import artifacts** for docs portals, pathfinder crates, runtime handoff packs, platform engineering dashboards, and org-specific telemetry governance.

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
- `EnvFilter` and per-layer filtering already provide real activation substrate for spans and events.
- Tokio Console and `console-subscriber` already expose runtime/task/resource signals under specific runtime and subscriber conditions.
- `tracing-opentelemetry` already bridges tracing spans into OpenTelemetry traces and metrics, but explicitly does not export logs.
- OpenTelemetry provides APIs/SDKs, semantic conventions, schemas, exporters, and instrumentation libraries.
- Telemetry-schema and semantic-convention linters help standardize emitted keys.
- Redaction policy crates or layers can scrub sensitive fields.

What remains missing is the joined, maintainer-authored artifact that says:

- these are the **named signals** this crate intentionally emits,
- these are the **stability classes** of those signals,
- these are the **recipes** required to see them,
- these are the **filters, layers, features, runtimes, or bridges** needed to activate them,
- these are the **semantic-convention / schema claims** attached to them,
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
4. **Activation honesty** — make filters, layers, runtime requirements, and exporter bridges explicit.
5. **Bridge-route honesty** — keep "signal exists" separate from "signal reaches the route people think it does".
6. **Schema honesty** — record when signal meaning depends on a semantic-convention or schema version.
7. **Redaction explicitness** — make sensitivity boundaries reviewable rather than leaving them to folklore.
8. **Cost honesty** — include overhead and cardinality caveats as part of the surface.
9. **Join, don’t replace** — import from `tracing`, `tracing-subscriber`, OpenTelemetry adapters, and tests rather than competing with them.
10. **Diffability** — make release-to-release observability drift explicit.

# MVP surface

- Minimal `observability-pack.toml` schema with named signals, classes, and recipe references.
- Import lane for `tracing` metadata discovered in tests/examples and selected instrumentation adapters.
- Signal stability vocabulary: `stable_query_surface`, `supported_but_evolving`, `debug_only`, `internal_only`, `manual_review_required`.
- Cost vocabulary: `always_on_low_cost`, `conditional_low_cost`, `debug_only`, `runtime_sensitive`, `allocator_sensitive`, `high_cardinality_risk`, `manual_review_required`.
- `observability-check.report.json` that records whether advertised signals were seen and whether declared recipes were reproducible.
- `signal-stability.policy.json` for explicit meaning and minimum evidence behind each stability class.
- `activation-recipe.receipt.json` for the real features/filters/layers/runtime assumptions needed to surface the signals.
- `bridge-route.receipt.json` for route truth across fmt/log output, console, traces, metrics, and logs.
- `schema-convention.profile.json` for semantic-convention and schema-URL posture.
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
- `obspack-activation` — feature/filter/layer/runtime recipe capture and witness logic.
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
5. **Filter-gated support path** — advertised signals that require explicit `EnvFilter` / `RUST_LOG` posture or per-layer filtering to appear.
6. **Tokio-console support path** — runtime/task/resource signals that require Tokio `tracing` support, a console subscriber path, or runtime-specific cfg assumptions.
7. **Semantic-convention drift path** — semconv/schema changes that rename or reclassify the stable query surface.
8. **Lossy log route path** — nonblocking/loggy routes that are real but not complete.
9. **Batch flush path** — trace/log export surfaces that require `force_flush` or graceful shutdown to make exit-time claims honest.
10. **Periodic metric route path** — aggregate/windowed metric surfaces that should not masquerade as per-event delivery.

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

Bundle draft: `observability-pack.toml`, `signal-catalog.receipt.json`, `observability-surface.report.json`, `signal-cost.report.json`, `redaction-boundary.report.json`, `instrumentation-recipe.manifest.json`, `bridge-route.receipt.json`, `delivery-posture.receipt.json`, `completeness-class.report.json`, `observability-check.report.json`, `observability-diff.report.json`, `notes.md`.

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
- How strict should the crate be when a signal is declared `stable_query_surface` but is hidden behind non-default filters?
- What is the smallest honest vocabulary for lossy, sampled, periodic, and flush-dependent signal families without pretending backend durability is uniform?
- How much semantic-convention/schema information should be imported automatically versus maintainer-declared?

# Sources

- Rust vision-doc post: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tokio tracing topic: https://tokio.rs/tokio/topics/tracing
- `tracing` docs: https://docs.rs/tracing/latest/tracing/
- `tracing-subscriber` docs: https://docs.rs/tracing-subscriber/latest/tracing_subscriber/
- `EnvFilter` docs: https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html
- `console-subscriber` docs: https://docs.rs/console-subscriber/latest/console_subscriber/
- `tracing-opentelemetry` docs: https://docs.rs/tracing-opentelemetry/latest/tracing_opentelemetry/
- OpenTelemetry Rust docs: https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry Rust instrumentation-libraries docs: https://opentelemetry.io/docs/languages/rust/libraries/
- OpenTelemetry semantic conventions docs: https://opentelemetry.io/docs/concepts/semantic-conventions/
- OpenTelemetry schemas docs: https://opentelemetry.io/docs/specs/otel/schemas/
- OpenTelemetry logs docs: https://opentelemetry.io/docs/concepts/signals/logs/
- OpenTelemetry sensitive-data docs: https://opentelemetry.io/docs/security/handling-sensitive-data/

- `tracing-appender` docs: https://docs.rs/tracing-appender/latest/tracing_appender/non_blocking/
- `SdkTracerProvider` docs: https://docs.rs/opentelemetry_sdk/latest/opentelemetry_sdk/trace/struct.SdkTracerProvider.html
- `SdkLoggerProvider` docs: https://docs.rs/opentelemetry_sdk/latest/opentelemetry_sdk/logs/struct.SdkLoggerProvider.html
- OpenTelemetry sampling docs: https://opentelemetry.io/docs/concepts/sampling/
- `opentelemetry` metrics docs: https://docs.rs/opentelemetry/latest/opentelemetry/
- `opentelemetry-appender-tracing` docs: https://docs.rs/opentelemetry-appender-tracing/latest/opentelemetry_appender_tracing/
