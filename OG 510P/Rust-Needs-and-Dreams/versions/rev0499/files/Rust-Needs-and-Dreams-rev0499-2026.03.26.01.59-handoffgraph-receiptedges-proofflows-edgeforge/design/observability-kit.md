# Design: Observability Kit (`cargo obs`, `obs-pack/v0`)

## Goal
Define a portable observability contract for Rust services and libraries so tracing, logs, metrics, OpenTelemetry export, and async-runtime diagnostics compose into one reviewable, testable boundary.

This should **not** replace `tracing`, `tracing-subscriber`, OpenTelemetry Rust, Tokio Console, or the `metrics` ecosystem. It should make them easier to combine consistently.

Read this together with [`design/observability-lane-map.md`](./observability-lane-map.md): the archive should now keep **structured tracing composition, local formatted diagnostics, `log` bridges, metrics facades, OpenTelemetry export/profile posture, runtime diagnostics, and imported machine reports** distinct instead of narrating one fake “telemetry enabled” surface.

## References (signals)
- `tracing` is Rust’s structured, event-based diagnostics framework.
  https://docs.rs/tracing
- `tracing-subscriber` centers on the composable `Layer` abstraction.
  https://docs.rs/tracing-subscriber
- OpenTelemetry Rust documents traces, metrics, and logs together; all are currently marked beta in the language docs.
  https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry says ecosystem complexity is creating production-adoption barriers, including configuration breakage and rollout complexity.
  https://opentelemetry.io/blog/2025/stability-proposal-announcement/
- OpenTelemetry’s “observability by design” push argues for versioned semantic conventions, validation, and CI-facing workflows.
  https://opentelemetry.io/blog/2025/otel-weaver/
- The OpenTelemetry Rust repo recommends OTLP exporters for production scenarios.
  https://github.com/open-telemetry/opentelemetry-rust
- OpenTelemetry SDK configuration defines OTLP as the default exporter for traces, metrics, and logs when auto-configured.
  https://opentelemetry.io/docs/languages/sdk-configuration/general/
- Tokio Console already provides an async diagnostic wire protocol and `tracing-subscriber` layer.
  https://github.com/tokio-rs/console
- Cargo is actively building structured reporting surfaces.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- `opentelemetry-jaeger` is now flagged unmaintained by RustSec, which strengthens the case for OTLP-first defaults.
  https://rustsec.org/packages/opentelemetry-jaeger.html

## Core components

### 1) `obs-intent/v0`
A design-time declaration of what a project intends to emit:
- enabled signals: traces / logs / metrics / console-runtime diagnostics
- target environments: dev / ci / prod
- correlation policy: trace IDs in logs, baggage policy, resource attributes
- chosen semantic-convention profile(s)
- exporter classes: OTLP / console / Prometheus / custom adapter
- privacy / redaction rules
- sampling and retention intent

This is the contract humans review before rollout.

### 2) `obs-profile/v0`
A machine-readable description of the chosen telemetry schema slice:
- semantic convention version or profile name
- required resource attributes
- required span/log/metric names
- allowed field aliases / migrations
- optional runtime-diagnostic capabilities (Tokio Console, runtime metrics)
- stability level per signal

Design rule: keep the profile narrower than the full OTel universe. Projects need a declared subset they can validate.

### 3) `obs-report/v0`
The effective runtime/export configuration actually produced:
- resolved exporters and endpoints
- signal enablement
- protocol (`grpc`, `http/protobuf`, `http/json`) where relevant
- enabled subscriber / recorder layers
- warnings (for example: unmaintained exporter, missing resource attrs, missing trace/log correlation)
- capture of env-driven config decisions when safe to record

This is the explainable “what happened” artifact.

### 4) `obs-vectors/v0`
Portable validation vectors from a canonical run:
- sample traces
- sample logs
- sample metrics
- optional runtime-diagnostic capture metadata
- correlation checks
- schema/field presence checks

Design rule: use small golden vectors for CI, not full telemetry dumps.

### 5) `obs-pack/v0`
Bundle format:
- `obs-intent/v0`
- `obs-profile/v0`
- `obs-report/v0`
- `obs-vectors/v0`
- optional attached raw config snippets or collector config excerpts
- verification summary

This is the portable thing releases, CI jobs, and incident packs can attach.

### 6) `cargo obs`
Reference UX:
- `cargo obs init`
- `cargo obs doctor`
- `cargo obs profile`
- `cargo obs vectors`
- `cargo obs validate`
- `cargo obs pack`

`cargo obs` should start as an adapter, validator, and packer. It should not become a backend or collector.

## Default policy
- **OTLP-first** for production-facing export paths.
- **Console + human-readable layers** for local development.
- **Schema/profile validation in CI** before treating telemetry as dependable.
- **Runtime-specific diagnostics remain opt-in capabilities**, not assumptions.

## What the kit should provide to others
- **Service teams:** one boring bootstrap path for coherent logs/traces/metrics.
- **Library authors:** a way to declare telemetry promises without forcing one backend.
- **Async teams:** a clean bridge between general telemetry and Tokio Console-style diagnostics.
- **Security/compliance teams:** one place to review redaction, endpoint, and signal policy.
- **Tool authors:** stable attachment points for replay, incident, perf, and release workflows.

## Overlap boundaries
- **Not Debugger Experience Kit:** debugger metadata and repro packs stay there.
- **Not Replay Kit:** failure reproduction and bug cassettes stay there.
- **Not Perf Labs:** performance evidence stays distinct, though perf runs can attach `obs-pack/v0`.
- **Not Cargo Report Kit:** Cargo machine reports remain their own family, but should be ingestible by `cargo obs` for correlation.

## Hard problems (explicitly scoped)
1. **Metrics ecosystem split**
   - support adapters rather than forcing all users onto one metrics API.
2. **Semantic convention sprawl**
   - v0 should support profile subsets instead of claiming universal coverage.
3. **Runtime-specific diagnostics**
   - Tokio Console and runtime metrics are valuable but should stay capability-gated.
4. **Config capture can leak secrets**
   - reports need redaction-aware serialization.
5. **Do not become an observability vendor SDK**
   - the goal is portable contracts and validation, not backend lock-in.

## Evaluation plan
Pilot on:
1. a web service using `tracing` + `tracing-subscriber` + OpenTelemetry OTLP,
2. a Tokio service with Console enabled in dev only,
3. a library using `metrics` facade + optional tracing integration,
4. a CI pipeline validating telemetry vectors before release.

Success bar:
- one repo can describe its telemetry without bespoke wiki glue,
- reviewers can tell what telemetry changed between releases,
- CI can validate semantic promises,
- and teams can compose Rust-native async diagnostics with vendor-neutral telemetry instead of maintaining two disconnected worlds.
