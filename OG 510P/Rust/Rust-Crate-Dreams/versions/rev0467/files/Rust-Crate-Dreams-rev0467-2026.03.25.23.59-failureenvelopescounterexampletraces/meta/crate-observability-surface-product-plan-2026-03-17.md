# Crate observability-surface product plan — 2026-03-17

This note exists to keep **P-0518 Crate Observability Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing signal / activation / sensitivity / drift contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0518** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which spans, events, metrics, or logs the crate intentionally emits,
- which of those signals are stable enough to query or alert on,
- which feature flags, filters, layers, runtimes, or exporters are required to actually see them,
- which naming/schema conventions they follow,
- which fields may contain identifiers, payload-derived material, or otherwise sensitive values,
- and what changed between releases.

It should **not** try to become a new subscriber, exporter, collector, dashboard, schema-registry service, or full observability platform.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, operators, and release reviewers, the crate should provide:

1. **One compact observability contract** instead of folklore split across README snippets, `tracing` calls, backend setup docs, and issue threads.
2. **A signal inventory** so spans, events, metrics, logs, and backend-only helper signals stop being blurred together.
3. **A stability policy** so teams can tell `stable_query_surface` apart from `supported_but_evolving`, `debug_only`, `internal_only`, or `manual_review_required`.
4. **An activation receipt** so “this crate is instrumented” can be read as “needs the `tracing` feature, a specific layer/filter, and maybe a runtime/config flag” rather than as hand-wavy optimism.
5. **A schema/convention profile** so integrators know whether the crate follows OpenTelemetry semantic conventions, uses custom field names, or mixes both.
6. **A sensitivity boundary** so operators know which fields are safe, hash-or-truncate, payload-derived, or must remain manual-review territory.
7. **A short human summary** that can be pasted into production-readiness docs, support templates, or release notes.
8. **A release diff** that makes hidden signal drift loud.

For maintainers, the crate should provide:

1. a small pack file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake certainty,
3. a way to import existing `tracing`, `tracing-subscriber`, OpenTelemetry, and tokio-console substrate instead of replacing it,
4. one place to say whether a field is part of a stable query surface or only operationally illustrative,
5. and a CI gate for “this release silently changed what operators rely on”.

## Recommended `0.1` command surface

### `cargo observability-pack init`
Create a starter `observability-pack.toml` by importing obvious candidates from:

- maintainer-declared signals,
- `tracing` metadata visible in tests/examples,
- known instrumentation adapters such as `tracing-opentelemetry`,
- and selected runtime-specific support such as tokio-console integration.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo observability-pack capture`
Emit one normalized receipt bundle from a declared observability workflow.
This should capture:

- signal inventory,
- stability classes,
- activation requirements,
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
- do schema/convention claims agree with declared signal names and schema URLs where present,
- are sensitivity boundaries internally coherent,
- and which parts remain manual-review-only?

### `cargo observability-pack doctor`
Render human-facing warnings for suspicious situations such as:

- `advertised_signal_hidden_by_default_filter`
- `console_recipe_requires_runtime_feature`
- `semconv_schema_changed_without_surface_notice`
- `stable_query_surface_without_activation_recipe`
- `sensitive_field_exposed_as_safe`
- `trace_export_recipe_claimed_for_logs`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo observability-pack summary`
Render a short receiver-facing note for docs, runbooks, or release review.
A good summary answers:

- which signals are official,
- which are stable enough for queries and alerts,
- what must be enabled to see them,
- and where schema/sensitivity caveats remain.

### `cargo observability-pack diff <old> <new>`
Compare two receipts or packs and classify:

- `signal_added`
- `signal_removed`
- `stability_changed`
- `activation_requirement_changed`
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
  - policy validation, doctor warnings, activation/schema consistency, and drift checks
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
- `observability-check.report.json`
- `observability-diff.report.json`
- `observability-notes.summary.md`

This pass adds three more important artifacts:

- `signal-stability.policy.json` — what `stable_query_surface`, `supported_but_evolving`, `debug_only`, `internal_only`, and `manual_review_required` mean and what minimum evidence each class expects.
- `activation-recipe.receipt.json` — the declared or observed features, env vars, filters, layers, runtimes, cfgs, or exporter adapters actually required to see a signal family.
- `schema-convention.profile.json` — which semantic-convention domain or schema URL the crate claims, whether names are conventional vs custom, and where schema drift is expected to matter.

Those files matter because crate observability gets vague again if the archive only records signals and redaction but not:

- whether a “stable” signal is actually stable enough to build queries on,
- whether a declared signal is visible by default or only under special filter/runtime/export conditions,
- and whether semantic meaning is tied to a particular schema URL or only to crate-local naming.

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
4. **Schema/convention posture**
   - semantic-convention domains
   - schema URLs
   - custom naming overlays
5. **Sensitivity and cost boundaries**
   - safe vs sensitive vs hash/truncate
   - cardinality and cost notes
6. **Manual review zones**
   - anything uncertain or backend-specific

The importer should prefer visible uncertainty over synthesis.

## Stability policy

The first implementation should treat **signal stability as a first-class review object** and keep it separate from activation posture or backend/exporter choice.

### What should count as stability classes in `0.1`

- `stable_query_surface`
- `supported_but_evolving`
- `debug_only`
- `internal_only`
- `manual_review_required`
- `unknown`

### What should *not* be encoded as stability classes in `0.1`

- “this happened to show up in logs once”
- “the backend can query it so it must be stable”
- “an instrumentation crate emitted it, therefore the library promises it”
- “the crate uses semantic conventions, so every field is stable forever”

The stability policy should be versioned and diffable.
If a maintainer cannot explain why a signal is safe to query over time, it should fall back to `supported_but_evolving` or `manual_review_required`.

## Activation policy

The first implementation should make **signal activation** reviewable rather than burying it in code snippets.

### Activation classes worth distinguishing in `0.1`

- `always_visible_with_declared_default_subscriber`
- `requires_feature_flag`
- `requires_env_filter_or_rust_log`
- `requires_named_layer`
- `requires_runtime_specific_instrumentation`
- `requires_exporter_bridge`
- `manual_review_required`

The receipt should capture concrete details like:

- crate feature names,
- environment variables,
- per-layer filters,
- runtime cfg requirements,
- adapter crate names,
- and whether the advertised recipe was actually observed.

That keeps “the signal exists somewhere in code” separate from “a downstream user can actually see it”.

## Schema / convention policy

`0.1` should treat **semantic meaning** as a review object rather than assuming every field is purely crate-local.

The first implementation should record:

- whether the crate follows OpenTelemetry semantic conventions for a signal family,
- which schema URL or convention version it claims when one is known,
- whether the span/event names are conventional, custom, or mixed,
- and whether a release diff changed field names in a way that likely affects query compatibility.

This matters because OpenTelemetry semantic conventions and schemas are versioned and evolving.
If a crate moves from one schema URL to another or renames fields without explaining why, the review artifact should make that drift loud.

## Sensitivity policy

The first implementation should keep **redaction / sensitivity** conservative and human-reviewable.

### Sensitivity classes worth supporting in `0.1`

- `safe_by_default`
- `contains_identifiers`
- `payload_derived`
- `hash_or_truncate`
- `drop_before_export`
- `manual_review_required`

That vocabulary is intentionally smaller than full privacy/compliance frameworks.
The goal is to publish receiver-facing boundaries, not to promise legal sufficiency.

## `0.1` fixture strategy

Start with three families that capture the highest-value confusion:

1. **Filter-gated signal visibility**
   - advertised events or spans that disappear under default `EnvFilter` / `RUST_LOG` posture
2. **Runtime-specific console instrumentation**
   - tokio-console-style recipes that require explicit runtime features or cfg posture
3. **Semantic-convention / schema drift**
   - schema URL changes or renamed fields that should affect query-surface review

Avoid trying to start with every telemetry backend at once.

## What to leave for later

Defer all of the following until the core pack vocabulary feels trustworthy:

- static inference of every possible signal,
- vendor/backend-specific dashboard bundles,
- collector pipeline generation,
- full privacy policy management,
- automated cardinality benchmarking,
- and logs/metrics/traces correlation visualizers.

Those are attractive follow-ons, but they are not the first missing crate.

## Minimum lovable MVP

A library and cargo subcommand that let one crate declare five to twenty intended signals, attach stability/activation/sensitivity/schema notes to them, verify that the named recipes actually surface them, and emit one diffable `observability-pack` bundle.

## Adoption plan

1. Start with `tracing`-centric crates and test/example-driven capture.
2. Make `summary` output readable enough for README/docs inclusion.
3. Treat OpenTelemetry semantic-convention and schema imports as optional but first-class when present.
4. Ship doctor warnings for the three most common lies:
   - “stable” without evidence,
   - “emits signals” without an activation recipe,
   - and “safe” without a sensitivity note.

## Why this is still distinct from adjacent lanes

- **P-0513 runtime handoff** is about incident/support bundles after runtime failure. **P-0518** is about the standing observability surface a crate publishes before and during operations.
- **P-0517 performance envelopes** are about workloads, budgets, and expected costs. **P-0518** is about signals, activation, and meaning.
- **schema/redaction tooling** helps generate or scrub telemetry. **P-0518** publishes the crate-authored contract above those tools.
- **tokio-console / `tracing-opentelemetry` / subscribers / exporters** are substrate. **P-0518** is the reviewable support layer above them.
