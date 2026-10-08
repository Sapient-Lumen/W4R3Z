# Crate observability-surface product plan — 2026-03-20

This note exists to keep **P-0518 Crate Observability Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing signal / stability / activation / route / sensitivity / drift contract**.
This refresh answers a narrower question:

> If somebody actually started building **P-0518** this week, what should version `0.1` look like now that route truth still does not tell another team whether signals are lossy, sampled, aggregated, or flush-dependent?

## Main judgment

A buildable `0.1` should still be a **small cargo subcommand plus library**.
But the center of gravity should now be slightly sharper:

- official signal families,
- signal stability,
- activation recipes,
- bridge routes,
- schema/convention posture,
- sensitivity boundaries,
- and **delivery/completeness posture**.

The key change is that `0.1` should explicitly support **delivery truth** without confusing delivery truth with route truth.

That means the crate should help maintainers publish one reviewable answer to:

- which spans, events, metrics, or logs are actually part of the crate’s intended support surface,
- which of those are stable enough for queries or alerts,
- which feature flags, filters, layers, runtimes, env vars, or cfgs are required to see them,
- which route actually carries them to fmt output, console, traces, metrics, or logs,
- **whether those routes are blocking, buffered, lossy, sampled, periodic, or shutdown/flush dependent**, 
- which semantic-convention/schema claims apply,
- which fields are safe, payload-derived, hashed, dropped, or manual-review territory,
- and what changed between releases.

It should **not** try to become a new subscriber, exporter, collector, dashboard, queue, or sampling processor.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, operators, and release reviewers, the crate should provide:

1. **One compact observability contract** instead of folklore split across README snippets, `tracing` calls, env-filter directives, exporter setup docs, and issue threads.
2. **A signal inventory** so spans, events, metrics, logs, and backend-only helper signals stop being blurred together.
3. **A stability policy** so teams can tell `stable_query_surface` apart from `supported_but_evolving`, `debug_only`, `internal_only`, or `manual_review_required`.
4. **An activation receipt** so “this crate is instrumented” becomes “needs this feature/filter/layer/runtime/cfg” rather than hand-wavy optimism.
5. **A bridge-route receipt** so another team can tell whether a signal family reaches fmt/log output, tokio-console, OpenTelemetry traces, OpenTelemetry metrics, OpenTelemetry logs, or none of those without extra glue.
6. **A delivery-posture receipt** so another team can tell whether the route is blocking, buffered with backpressure, lossy, batch-flushed, periodic, or sampled.
7. **A completeness-class report** so another team can tell `attempted_all_events` apart from `best_effort_buffered`, `representative_sample`, `aggregated_window`, `exit_sensitive`, or `manual_review_required`.
8. **A schema/convention profile** so integrators know whether the crate follows OpenTelemetry semantic conventions, uses custom names, or mixes both.
9. **A sensitivity boundary report** so operators know which fields are safe, hashed, payload-derived, or must remain manual-review territory.
10. **A short human summary** that can be pasted into production-readiness docs, support templates, or release notes.
11. **A release diff** that makes hidden signal drift loud.

For maintainers, the crate should provide:

1. a small pack file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake certainty,
3. a way to import existing `tracing`, `tracing-appender`, OpenTelemetry, and tokio-console substrate instead of replacing it,
4. one place to say whether a field is part of a stable query surface or only operationally illustrative,
5. one place to say whether a route is real, indirect, partial, or absent,
6. one place to say whether a delivery path is complete, sampled, lossy, or flush-dependent,
7. and a CI gate for “this release silently changed what operators rely on”.

## Recommended `0.1` command surface

### `cargo observability-pack init`
Create a starter `observability-pack.toml` by importing obvious candidates from:

- maintainer-declared signals,
- `tracing` metadata visible in tests/examples,
- known instrumentation adapters such as `tracing-opentelemetry`,
- known runtime-specific support such as `console-subscriber`,
- selected semantic-convention hints,
- and a few delivery-shape hints such as `tracing_appender::non_blocking`, `MetricsLayer`, and provider flush/shutdown usage.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo observability-pack capture`
Emit one normalized receipt bundle from a declared observability workflow.
This should capture:

- signal inventory,
- stability classes,
- activation requirements,
- bridge routes,
- delivery posture,
- completeness classes,
- schema/convention posture,
- sensitivity boundaries,
- and imported evidence.

`capture` should work on imported artifacts too.
It must not require a live collector, dashboard, or vendor account.

### `cargo observability-pack check`
Run the local validation pass:

- do declared signals still exist,
- do stability and cost classes parse,
- do activation recipes point at real features/layers/env vars/runtime assumptions,
- do declared bridge routes agree with the configured layers/adapters,
- do declared delivery postures agree with the chosen buffering/sampling/export model,
- do completeness classes overclaim route truth,
- do schema/convention claims agree with declared signal names and schema URLs where present,
- are sensitivity boundaries internally coherent,
- and which parts remain manual-review-only?

### `cargo observability-pack doctor`
Render human-facing warnings for suspicious situations such as:

- `advertised_signal_hidden_by_default_filter`
- `console_recipe_requires_tokio_unstable`
- `otel_log_route_claimed_but_tracing_opentelemetry_only_exports_traces_and_metrics`
- `non_blocking_lossy_route_claimed_complete`
- `periodic_metric_route_claimed_per_event_delivery`
- `batch_export_route_without_flush_posture`
- `stable_query_surface_without_activation_recipe`
- `schema_url_changed_without_surface_notice`
- `sensitive_field_exposed_as_safe`
- `env_filter_regex_on_untrusted_input`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo observability-pack summary`
Render a short receiver-facing note for docs, runbooks, or release review.
A good summary answers:

- which signals are official,
- which are stable enough for queries and alerts,
- what must be enabled to see them,
- which route actually carries them,
- **what delivery/completeness posture is honest for each family**,
- and where schema/sensitivity caveats remain.

### `cargo observability-pack diff <old> <new>`
Compare two receipts or packs and classify:

- `signal_added`
- `signal_removed`
- `stability_changed`
- `activation_requirement_changed`
- `bridge_route_changed`
- `delivery_posture_changed`
- `completeness_class_changed`
- `schema_profile_changed`
- `field_name_changed`
- `sensitivity_changed`
- `cost_changed`
- `manual_review_required`

### `cargo observability-pack pack`
Emit one compact `.observabilitysurface.zip` bundle for CI artifacts, release review, downstream support, or platform handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `observability_surface_model`
  - shared Rust types for packs, receipts, reports, policies, and diffs
- `observability_surface_discovery`
  - import logic for declared signals, `tracing` metadata, and selected adapter hints
- `observability_surface_check`
  - policy validation, doctor warnings, activation/route/delivery/schema consistency, and drift checks
- `observability_surface_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-observability-pack`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `observability_surface_tracing`
- `observability_surface_tracing_subscriber`
- `observability_surface_tracing_appender`
- `observability_surface_tracing_otel`
- `observability_surface_console`
- `observability_surface_semconv`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `observability-pack.toml`
- `signal-catalog.receipt.json`
- `observability-surface.report.json`
- `signal-cost.report.json`
- `redaction-boundary.report.json`
- `instrumentation-recipe.manifest.json`
- `signal-stability.policy.json`
- `activation-recipe.receipt.json`
- `bridge-route.receipt.json`
- `schema-convention.profile.json`
- `observability-check.report.json`
- `observability-diff.report.json`
- `observability-notes.summary.md`

This refresh adds two more important review objects:

- `delivery-posture.receipt.json` — records whether a signal family is blocking, buffered with backpressure, buffered-lossy, batch-exported, periodically exported, sampled, or still manual-review territory.
- `completeness-class.report.json` — records whether another team should interpret the route as `attempted_all_events`, `best_effort_buffered`, `representative_sample`, `aggregated_window`, `exit_sensitive`, or `manual_review_required`.

These files matter because crate observability gets vague again if the archive records signals and routes but not **what kind of delivery/completeness claim another team is actually supposed to trust**.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared pack facts**
   - `observability-pack.toml`
   - maintainer-declared signals, stability classes, and recipes
2. **Observed signal inventory**
   - tests/examples
   - selected `tracing` metadata
   - instrumentation-adapter hints
3. **Activation requirements**
   - feature flags
   - `EnvFilter` / `RUST_LOG`
   - layers and per-layer filters
   - runtime/cfg requirements
4. **Bridge routes**
   - fmt/log output
   - console subscriber path
   - OpenTelemetry trace/metric/log bridges
   - absent or manual-review-only routes
5. **Delivery/completeness posture**
   - synchronous versus buffered routes
   - lossy versus backpressure behavior
   - batch/flush dependence
   - periodic aggregation windows
   - sampling posture
6. **Schema/convention posture**
   - semantic-convention domains
   - schema URLs
   - custom naming overlays
7. **Sensitivity and cost boundaries**
   - safe vs sensitive vs hash/truncate
   - cardinality and cost notes
8. **Manual review zones**
   - anything uncertain or backend-specific

The importer should prefer visible uncertainty over synthesis.
