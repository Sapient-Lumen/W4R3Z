# Epic proposal: Observability Kit (`cargo obs` + `obs-pack/v0`)

## One-liner
Ship a standard, portable observability contract for Rust: `cargo obs`, versioned telemetry artifacts, validation vectors, and adapters around existing tracing / metrics / OpenTelemetry / async-diagnostics tools — with an explicit lane map so local formatted diagnostics, `log` bridges, metrics facades, OTLP export, runtime diagnostics, and imported machine reports do not collapse into one fake support claim.

## Why this is worthy
Rust is already good at instrumentation primitives, but still too fiddly at **operational coherence**.

The opportunity is not “invent another logging crate”. The opportunity is to make telemetry reviewable like API surface, coverage policy, or release evidence. That is strategic because it helps:
- production adoption,
- debugging,
- incident response,
- perf triage,
- release verification,
- and cross-team standardization.

## Users
- backend/service teams adopting Rust in production
- platform teams standardizing telemetry across many Rust services
- async-heavy teams that need both runtime diagnostics and vendor-neutral export
- library authors who want stable instrumentation promises
- incident/perf/reliability teams that need portable evidence packs

## MVP (6–10 weeks)
- `obs-intent/v0`, `obs-profile/v0`, `obs-report/v0`, `obs-pack/v0`
- lane profiles from [`design/observability-lane-map.md`](../design/observability-lane-map.md) so the MVP can say which observability lane it is actually proving
- `cargo obs init`, `doctor`, `validate`, `pack`
- reference adapter for `tracing` + `tracing-subscriber`
- OTLP-first OpenTelemetry path for logs/traces/metrics
- trace/log correlation checks
- optional Tokio Console capability detection and reporting
- minimal golden telemetry vectors for CI

## Good v1 extensions
- adapters for `metrics` facade and common exporters
- semantic-convention diffing and migration hints
- redaction-policy checks
- release attachment support via `release-pack/v0`
- incident-mode collection profile feeding Incident Kit / Replay Kit

## Non-goals (initially)
- build a collector
- build a hosted backend or UI
- replace OpenTelemetry specs
- force one metrics ecosystem on every Rust project
- promise universal semantic-convention support in v0

## Risks and mitigations
- **OTel churn / beta status**
  - keep the Rust facade small and artifact-focused; validate exported behavior instead of overcommitting to every upstream surface.
- **Too much scope**
  - start with profiles + reports + vectors, not universal integration.
- **Secret leakage in captured config**
  - make redaction a first-class report rule.
- **Confusion with debugger/perf tooling**
  - keep overlap boundaries explicit and attach packs rather than merging domains.

## Why now
The pieces are aligning:
- Rust still has a live debugging pain signal.
- Cargo is getting more machine-readable.
- OpenTelemetry is explicitly moving toward schema/versioning/validation discipline.
- Tokio Console proves that Rust-specific runtime diagnostics are valuable.

That combination makes this feel timely rather than premature.
