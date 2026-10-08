# Crate observability-surface product plan — 2026-03-19

This note exists to keep **P-0518 Crate Observability Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing signal / stability / activation / sensitivity / drift contract**.
This refresh answers a narrower question:

> If somebody actually started building **P-0518** this week, what should version `0.1` look like now that the ecosystem also makes **bridge-route boundaries** unusually explicit?

## Main judgment

A buildable `0.1` should still be a **small cargo subcommand plus library**.
But the center of gravity should now be slightly sharper:

- official signal families,
- signal stability,
- activation recipes,
- **bridge routes**,
- schema/convention posture,
- sensitivity boundaries,
- and release diffs.

The key change is that `0.1` should explicitly support **route truth** without confusing route truth with signal existence.

That means the crate should help maintainers publish one reviewable answer to:

- which spans, events, metrics, or logs are actually part of the crate’s intended support surface,
- which of those are stable enough for queries or alerts,
- which feature flags, filters, layers, runtimes, env vars, or cfgs are required to see them,
- which route actually carries them to fmt output, console, traces, metrics, or logs,
- which semantic-convention/schema claims apply,
- which fields are safe, payload-derived, hashed, dropped, or manual-review territory,
- and what changed between releases.

It should **not** try to become a new subscriber, exporter, collector, dashboard, schema-registry service, or full observability platform.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, operators, and release reviewers, the crate should provide:

1. **One compact observability contract** instead of folklore split across README snippets, `tracing` calls, env-filter directives, exporter setup docs, and issue threads.
2. **A signal inventory** so spans, events, metrics, logs, and backend-only helper signals stop being blurred together.
3. **A stability policy** so teams can tell `stable_query_surface` apart from `supported_but_evolving`, `debug_only`, `internal_only`, or `manual_review_required`.
4. **An activation receipt** so “this crate is instrumented” becomes “needs this feature/filter/layer/runtime/cfg” rather than hand-wavy optimism.
5. **A bridge-route receipt** so another team can tell whether a signal family reaches fmt/log output, tokio-console, OpenTelemetry traces, OpenTelemetry metrics, OpenTelemetry logs, or none of those without extra glue.
6. **A schema/convention profile** so integrators know whether the crate follows OpenTelemetry semantic conventions, uses custom names, or mixes both.
7. **A sensitivity boundary report** so operators know which fields are safe, hashed, payload-derived, or must remain manual-review territory.
8. **A short human summary** that can be pasted into production-readiness docs, support templates, or release notes.
9. **A release diff** that makes hidden signal drift loud.

For maintainers, the crate should provide:

1. a small pack file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake certainty,
3. a way to import existing `tracing`, `tracing-subscriber`, OpenTelemetry, and tokio-console substrate instead of replacing it,
4. one place to say whether a field is part of a stable query surface or only operationally illustrative,
5. one place to say whether a route is real, indirect, partial, or absent,
6. and a CI gate for “this release silently changed what operators rely on”.

## Recommended `0.1` command surface

### `cargo observability-pack init`
Create a starter `observability-pack.toml` by importing obvious candidates from:

- maintainer-declared signals,
- `tracing` metadata visible in tests/examples,
- known instrumentation adapters such as `tracing-opentelemetry`,
- known runtime-specific support such as `console-subscriber`,
- and selected semantic-convention hints.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo observability-pack capture`
Emit one normalized receipt bundle from a declared observability workflow.
This should capture:

- signal inventory,
- stability classes,
- activation requirements,
- bridge routes,
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
- do schema/convention claims agree with declared signal names and schema URLs where present,
- are sensitivity boundaries internally coherent,
- and which parts remain manual-review-only?

### `cargo observability-pack doctor`
Render human-facing warnings for suspicious situations such as:

- `advertised_signal_hidden_by_default_filter`
- `console_recipe_requires_tokio_unstable`
- `otel_log_route_claimed_but_tracing_opentelemetry_only_exports_traces_and_metrics`
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
- and where schema/sensitivity caveats remain.

### `cargo observability-pack diff <old> <new>`
Compare two receipts or packs and classify:

- `signal_added`
- `signal_removed`
- `stability_changed`
- `activation_requirement_changed`
- `bridge_route_changed`
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
  - policy validation, doctor warnings, activation/route/schema consistency, and drift checks
- `observability_surface_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-observability-pack`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `observability_surface_tracing`
- `observability_surface_tracing_subscriber`
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
- `schema-convention.profile.json`
- `observability-check.report.json`
- `observability-diff.report.json`
- `observability-notes.summary.md`

This refresh adds one more important review object:

- `bridge-route.receipt.json` — records whether a signal family reaches fmt/log output, tokio-console, OpenTelemetry traces, OpenTelemetry metrics, OpenTelemetry logs, or only manual-review territory.

That file matters because crate observability gets vague again if the archive records signals and activation but not **which route another team is actually supposed to rely on**.

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
5. **Schema/convention posture**
   - semantic-convention domains
   - schema URLs
   - custom naming overlays
6. **Sensitivity and cost boundaries**
   - safe vs sensitive vs hash/truncate
   - cardinality and cost notes
7. **Manual review zones**
   - anything uncertain or backend-specific

The importer should prefer visible uncertainty over synthesis.

## Best proving grounds for `0.1`

Prioritize crates where observability posture is real, but a full platform would be overkill:

- async/server crates with `tracing` instrumentation and operator-facing docs,
- crates that advertise tokio-console support,
- crates that bridge `tracing` into OpenTelemetry,
- crates that claim semconv-aligned field names,
- crates whose signals may contain identifiers, payload fragments, or other sensitive material.

## Scenarios to support early

1. **Advertised signal hidden by default filter posture** — because a signal existing in code is not the same thing as being visible under the default recipe.
2. **Tokio console recipe requires runtime-specific activation** — because console visibility depends on real Tokio features/cfg, not merely on importing the crate.
3. **OpenTelemetry bridge route does not carry logs** — because `tracing-opentelemetry` does not export logs, and route truth needs to stay explicit.
4. **Semantic-convention/schema drift changes query posture** — because schema URLs and field names evolve.
5. **Potentially untrusted filter input requires regex-off or manual review** — because filter behavior itself can widen the support/safety boundary.
6. **Payload-derived identifiers require hash/drop posture** — because observability support without sensitivity posture is not trustworthy support.

## Adoption plan

The winning adoption motion is:

1. start with maintainers already using `tracing`,
2. import their current recipes rather than replacing them,
3. make summaries simple enough for README / runbook / release note use,
4. make diffs useful enough for CI/release review,
5. and make route/sensitivity surprises loud before operators discover them the hard way.

The first release should target teams already using some mix of `tracing`, `tracing-subscriber`, `console-subscriber`, and OpenTelemetry adapters.
Those teams already have signal substrate; they lack a compact contract.

## Explicit non-goals for `0.1`

- not a universal subscriber or exporter framework
- not a replacement for `tracing`, `tracing-subscriber`, or OpenTelemetry SDKs
- not a hosted observability backend or governance platform
- not an attempt to prove that every signal is safe for every deployment context
- not a promise that route coverage is backend-independent
- not a guarantee that semconv or schema migration can always be handled automatically

## Working judgment

The 2026 version of **P-0518** should be treated as an **observability-support contract crate**, not as another telemetry stack.
Its most valuable gift to other people is not more emitted signals.
It is a compact explanation of **which signals matter, how to turn them on, which route actually carries them, what schema posture they claim, and how much sensitivity review they still require**.
