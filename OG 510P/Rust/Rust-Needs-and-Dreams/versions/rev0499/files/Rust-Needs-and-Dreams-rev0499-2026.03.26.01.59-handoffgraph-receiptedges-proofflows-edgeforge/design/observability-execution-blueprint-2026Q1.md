# Design: Observability execution blueprint 2026Q1

## Question
Once the archive accepts that Rust observability is strategically important, what should the worthy contribution actually become before it dissolves into “just use tracing”, “just wire up OpenTelemetry”, “just export OTLP”, “just use Tokio Console”, or “just buy a dashboard”?

## Short answer
A worthy contribution here is a **reference layer + report/pack command + adapter/import corpus** for **diagnostic-identity truth**, **signal/profile truth**, **activation/route truth**, **runtime-diagnostic capability truth**, **support/docs truth**, and **bounded consumer handoff**.

Not another exporter helper.
Not a backend bootstrap crate.
Not a dashboard empire.
Not a fake universal observability score.

In repo language, the missing thing is closer to **`cargo obspack` + `obs-product-pack/v0`** than to another instrumentation facade.

## Why this seam is execution-worthy now
The ecosystem's current shape makes the missing layer unusually visible:
- The 2025 State of Rust survey still says resource usage remains a top non-trivial productivity problem, debugging remains a live pain point, and online documentation is still the preferred canonical reference even as LLM/editor mediation rises. That combination raises the value of machine-readable runtime/diagnostic truth over prose-only setup lore.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `tracing-subscriber` still centers the `Layer` trait as a composable abstraction. That means real Rust tracing posture is already layered rather than singular.
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/layer/index.html
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/layer/trait.Layer.html
- `metrics` still presents itself as a facade whose consumer chooses the concrete recorder, so metrics posture is intentionally plural instead of one universal runtime.
  https://docs.rs/metrics
- OpenTelemetry Rust now documents traces, metrics, and logs together, but the current status table still marks all three major signal families as **Beta** for Rust.
  https://opentelemetry.io/docs/languages/rust/
- The opentelemetry-rust repo currently recommends `tracing` if you are starting fresh and points production users toward OTLP examples. That is useful guidance, but it still leaves room between “recommended ingredients” and “reviewable supported product surface.”
  https://github.com/open-telemetry/opentelemetry-rust
- OpenTelemetry's stability proposal says complexity and lack of stability are impediments to production deployments. That is exactly the kind of ecosystem signal that argues for a thinner reviewable boundary above exporters and config.
  https://opentelemetry.io/blog/2025/stability-proposal-announcement/
- OpenTelemetry Weaver argues for “observability by design” and treats telemetry conventions as something to define, validate, and evolve deliberately. That is a design lesson Rust can import without making OTel itself the whole answer.
  https://opentelemetry.io/blog/2025/otel-weaver/
- Tokio Console remains a distinct runtime-diagnostic capability with its own `tracing-subscriber` layer, gRPC export path, and experimental Tokio instrumentation requirements. That proves runtime diagnostics are real, but not interchangeable with general logs/traces/metrics.
  https://github.com/tokio-rs/console/blob/main/console-subscriber/README.md
- Cargo's 1.94 cycle still emphasizes that Cargo cannot be everything to everyone and explicitly highlights plugins, while also continuing structured logging/report work. That makes a thin plugin-shaped handoff layer more realistic than waiting for one built-in universal observability command.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The `opentelemetry-jaeger` crate is now explicitly unmaintained. That is a sharp reminder that exporter choice and support route are not timeless truths and should stay visibly reviewable.
  https://rustsec.org/advisories/RUSTSEC-2025-0123.html

That combination means the missing contribution is no longer “someone should make Rust observability nicer.”
It is a **portable product-truth and handoff layer**.

## What to refuse first
The wrong shapes are now clear enough that the archive should reject them explicitly.

### Wrong shape 1 — one backend or exporter as the answer
OTLP is increasingly the default production route, but it is not the same thing as observability truth.
If the proposal silently equates “supports OTLP” with “observability solved”, it is too thin.

### Wrong shape 2 — one dashboard or vendor portal as the answer
A UI can consume observability packs.
It should not be the canonical owner of what the subject emits, activates, and supports.

### Wrong shape 3 — one local tracing setup as the answer
A pretty `fmt` subscriber, a good `EnvFilter`, or a debug console setup can be a valuable lane.
It is not the whole production/runtime story.

### Wrong shape 4 — one runtime probe as the answer
Tokio Console proves that runtime diagnostics matter.
It should not silently redefine tracing, metrics, or support posture.

### Wrong shape 5 — one maturity score as the answer
Rust observability spans signal families, runtime diagnostics, activation routes, exporter routes, support claims, and downstream consumers.
A single score destroys too much meaning.

## Execution thesis
The worthy contribution should be built as six visibly separate truth layers.

### 1) Diagnostic-identity truth
The pack must say what names or classes are stable enough to matter.
Examples:
- span/event/error family names
- stable diagnostic ids or classes where they exist
- correlation keys and route/task/resource attachment points
- human-facing versus machine-facing rendering boundaries

### 2) Signal/profile truth
The pack must say what telemetry exists and which schema slice is actually promised.
Examples:
- traces / logs / metrics / runtime diagnostics
- semantic-convention or house-profile subsets
- required field names and attributes
- allowed aliases, deprecations, and migrations
- explicit validation vectors

### 3) Activation/route truth
The pack must say how the promised telemetry is actually activated.
Examples:
- exporter kind and protocol
- local/CI/prod profile selection
- endpoints, auth posture, and redaction-aware capture
- sampling, filtering, and retention posture
- `log` bridge posture
- environment/code/runtime gates such as `tokio_unstable`

### 4) Runtime-diagnostic capability truth
The pack must keep runtime diagnostics first-class instead of flattening them into generic telemetry.
Examples:
- console subscriber enabled or absent
- protocol/client posture
- runtime family and minimum capabilities
- dev-only versus supportable versus production-inadvisable status

### 5) Support/docs truth
The pack must say what downstream consumers are entitled to rely on.
Examples:
- stable / beta / experimental / local-only lanes
- checked docs and setup transcripts
- unsupported platform or runtime combinations
- known caveats such as deprecated exporter families or partial signal support

### 6) Consumer-handoff truth
The pack must say what later systems may honestly import.
Examples:
- release attachments
- incident/debug imports
- CI/review policy inputs
- support/runbook imports
- assistant-facing summaries that stay bounded by the pack

## What the artifact should look like in theory
A serious v0 should standardize a small family, not a monolith:
- `obs-subject/v0`
- `obs-profile/v0`
- `obs-activation-report/v0`
- `obs-runtime-diagnostic-profile/v0`
- `obs-support-report/v0`
- `obs-product-pack/v0`

And one top-level command surface:
- `cargo obspack report` — collect and normalize one or more observability-native reports into reviewable artifacts
- `cargo obspack pack` — bundle reports, attachments, and bounded metadata into `obs-product-pack/v0`

The contract must preserve raw attachments by reference where needed:
- subscriber/profile declarations
- OpenTelemetry profile or semantic-convention validation outputs
- runtime-diagnostic captures or console endpoints
- redacted activation/environment receipts
- Cargo report imports
- checked docs/setup transcripts

## What the artifact should look like in practice
The archive should now prefer these proving lanes, in order.

### Lane 1 — structured tracing + local diagnostics lane
Start with `tracing` + `tracing-subscriber` layering and require explicit distinction between human-formatted output and machine-facing identity/profile declarations.

Why first:
- proves the design is not secretly a vendor-specific export layer;
- meets ordinary Rust services and CLIs where they already are;
- forces identity truth to stabilize before wider backend ambition.

### Lane 2 — OTLP production-profile lane
Add an OTLP-backed profile that records exact activation/export posture, required attributes, and route caveats.

Why second:
- matches the current practical recommendation path for production scenarios;
- proves profile truth and activation truth can survive real deployment configuration;
- forces the design to model exporter drift and deprecation honestly.

### Lane 3 — metrics and legacy-log import lane
Show how metrics-recorder selection and `log`-bridge posture are imported as explicit truths rather than assumed side effects.

Why third:
- prevents the blueprint from becoming trace-only;
- makes adapter lossiness and partial correlation visible;
- tests the difference between emitted signal truth and consumer-side unification.

### Lane 4 — runtime-diagnostic lane
Attach Tokio Console-style runtime diagnostics as a declared capability with separate activation and support status.

Why fourth:
- proves runtime diagnostics are first-class but not universal;
- prevents local async-debug tooling from impersonating production telemetry;
- forces support-envelope honesty around experimental runtime instrumentation.

### Lane 5 — release / incident / support consumer lane
Show a release or incident consumer importing observability facts without redefining them.

Why fifth:
- validates that the pack helps real downstream review;
- keeps observability truth below policy and above raw backend folklore;
- proves this is ecosystem infrastructure rather than a nicer telemetry README.

## Strategic boundaries with adjacent seams
This blueprint is intentionally close to other strong archive seams, but it is not them.

### Not Debuggability Acceptance
Debuggability covers developer loop and investigation ergonomics more broadly.
Observability covers declared telemetry/product truth that debug, support, and incident consumers may import.

### Not Runtime Settings
Runtime Settings owns broader configuration/default/source precedence.
Observability imports activation posture from it and narrows that to telemetry-specific claims.

### Not Support Envelope
Support Envelope owns platform/runtime/docs support lanes broadly.
Observability narrows that to supported telemetry and runtime-diagnostic posture.

### Not Cargo report work
Cargo report and structured logging/report work are important imports.
They do not by themselves define signal/profile/support truth for application observability.

### Not one OpenTelemetry SDK choice
OpenTelemetry is a major proving ground and source of design lessons.
But the worthy contribution here should still work for tracing-native, metrics-native, runtime-diagnostic, and mixed-lane Rust projects.

## Why this counts as a worthy contribution
This would count as worthy because it would give Rust something it still does not have:
**a reviewable way to move from “we emit telemetry” to “here is an honest pack with identity, signal/profile, activation, runtime capability, support, and handoff truth intact.”**

That is strategically large enough to matter because:
- it reduces observability folklore;
- it improves release/support/incident/debug conversations without demanding one backend winner;
- it composes with present tooling instead of replacing it;
- and it creates a clean substrate for assistants and downstream tooling without letting them invent claims the subject never made.

## Ranking impact
This does **not** reorder the top of the archive.
It sharpens one remaining high-value seam.

Interpretation:
- **Build-State Evidence** stays the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** stays the clearest under-ranked day-to-day missing middle;
- **Observability Contract** now becomes the clearest execution answer for **runtime telemetry / activation / support / consumer-handoff** work;
- **Runtime Settings**, **Support Envelope**, **Incident**, **Replay**, and domain productization stacks remain major adjacent consumers/importers;
- and future observability proposals should now prove identity, profile, activation, runtime-diagnostic, support, and handoff truth before widening into control planes, vendors, or scoreboards.
