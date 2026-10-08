# Gap: Observability interoperability and telemetry contracts

## What is missing
Rust has strong observability building blocks, but production teams still assemble them by hand:
- `tracing` and `tracing-subscriber` give structured diagnostics and composable layers.
- OpenTelemetry Rust now documents traces, metrics, and logs together, but all three are still marked beta in the language docs.
- Tokio Console gives async-runtime diagnostics through a wire protocol and subscriber layer, but it is a specialized lane, not a general contract for service telemetry.
- The `metrics` ecosystem remains a separate facade/recorder world with its own layering model.

The missing contribution is a **portable telemetry contract** that says:
- which observability lane is actually in play (structured tracing composition, local formatted diagnostics, legacy-log import, metrics recorder stacks, OpenTelemetry export/profile posture, runtime diagnostics, or imported machine reports),
- which signals a service emits,
- how they correlate,
- which semantic conventions it follows,
- which exporter/config policy it expects,
- and how CI can validate that the claimed telemetry actually exists.

## Why it matters
This is no longer “just logging”.

The 2025 State of Rust survey still reports debugging as one of the main productivity problems, and the compiler team launched a dedicated 2026 debugging survey that explicitly calls out async debugging, cross-debugger support, visualizers, and expression evaluation as missing pieces. Meanwhile, Cargo is moving toward structured machine-readable reporting (`cargo report timings`, `rebuild`, `sessions`), which makes telemetry-shaped workflows more realistic inside Rust tooling.

At the same time, OpenTelemetry itself is warning that the ecosystem’s complexity creates barriers to production adoption: configuration churn, breakage across minor versions, performance regressions, and rollout complexity. OpenTelemetry’s own “observability by design” work argues that telemetry should be treated more like a versioned API with validation, policy, and schema discipline.

Rust needs a kit that makes observability **boring to adopt, boring to review, and boring to validate**.

## Existing building blocks worth composing
- `tracing` is the core structured diagnostics framework.
  https://docs.rs/tracing
- `tracing-subscriber` centers on composable `Layer`s.
  https://docs.rs/tracing-subscriber
- `tracing-log` bridges `log` records into `tracing` events.
  https://docs.rs/tracing-log
- OpenTelemetry Rust covers traces, metrics, and logs.
  https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry appender crates bridge Rust logging/tracing into OTel.
  https://github.com/open-telemetry/opentelemetry-rust/blob/main/opentelemetry-appender-tracing/README.md
- Tokio Console already proves the value of runtime-specific diagnostic streams for async Rust.
  https://github.com/tokio-rs/console
- `metrics` and `metrics-util` provide a parallel metrics facade + layering model.
  https://docs.rs/metrics
  https://docs.rs/metrics-util/latest/metrics_util/layers/

## Why existing tools are not yet the whole answer
Today’s pieces are strong but fragmented:
- `tracing` is great for structured events and spans.
- OpenTelemetry is the cross-vendor standard, but Rust-side rollout still has beta status and recent migration churn.
- Tokio Console is excellent for async debugging, but it is not a release/CI-grade telemetry contract.
- The `metrics` facade is useful, but it does not by itself solve cross-signal correlation or semantic convention drift.

This is the same pattern seen elsewhere in the archive: the ecosystem has point tools, but lacks the **shared artifact/report/policy layer**.

## Target outcome
A project should be able to say:
- “we emit traces, logs, and metrics under this profile,”
- “these fields and resource attributes are guaranteed,”
- “these async/runtime diagnostics are available in dev,”
- “this CI job validated the contract,”
- and “this release shipped with this telemetry profile and this effective config.”

That is bigger than a helper crate and smaller than a new backend.
