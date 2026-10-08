---
id: P-0209
title: OpenTelemetry SemConv Lint + Codegen Kit — validate, upgrade, and generate semantic-convention usage
status: idea
domains: [observability, telemetry, opentelemetry, tooling, linting]
last_reviewed: 2026-03-05
evidence:
  - https://opentelemetry.io/docs/specs/otel/semantic-conventions/
  - https://opentelemetry.io/docs/specs/semconv/
  - https://github.com/open-telemetry/semantic-conventions
  - https://crates.io/crates/opentelemetry-semantic-conventions
---
# P-0209: OpenTelemetry SemConv Lint + Codegen Kit

**One-liner:** A Rust-first toolkit that **validates, upgrades, and generates** OpenTelemetry Semantic Conventions usage—turning semconv drift into actionable diffs and stable CI checks.

## Why this is missing (the gap)
OpenTelemetry’s semantic conventions are a moving target, and projects regularly:
- ship inconsistent attribute names across crates/services
- accumulate “local dialects” that break dashboard portability
- struggle to migrate when conventions evolve

Rust has an `opentelemetry-semantic-conventions` crate with constants, but teams still need:
- **linting**: detect non-standard attributes and invalid cardinality patterns
- **codegen**: generate strongly-typed wrappers from a pinned semconv version
- **migration tooling**: map old→new attribute names with a report
- **policy**: organization-level allow/deny lists for attributes

OpenTelemetry explicitly defines semantic conventions as shared naming patterns across traces/metrics/logs/profiles/resources, and has ongoing stabilization work that highlights the challenges of change management.

## Target users
- platform teams standardizing telemetry across repos
- library authors exposing instrumentation hooks
- CI systems ensuring “no semconv drift”

## Crate shape (workspace)
- `otel_semconv_schema` — parse pinned semconv artifacts; expose IR
- `otel_semconv_codegen` — generate Rust types + helpers (feature-gated by semconv version)
- `otel_semconv_lint` — lints for attributes/spans/metrics/logs (with suppressions)
- `otel_semconv_migrate` — mapping engine + report generator
- `cargo-otel-lint` — cargo subcommand for workspace-wide checks
- `fixtures/semconv/` — pinned semconv snapshots + golden outputs

## MVP (4–8 weeks)
1. Pin to a known semconv snapshot and emit Rust constants + strongly typed builders
2. Lint: detect unknown attributes + wrong namespace + “high-cardinality risk” heuristics
3. Migration report: suggest replacements for a small curated mapping set
4. CI integration: fail on drift; optionally auto-fix in a “rewrite” mode

## De-risk plan
- Start by ingesting the semantic conventions as a static artifact checked into the repo
- Integrate with `tracing` + `opentelemetry` usage patterns only after lints are reliable
- Keep the linter explainable (each rule has a reason + link)

## Scorecard (0–5)
- Impact: 4
- Neglectedness: 3
- Feasibility: 4
- Adoptability: 5
- Sustainability: 4
- Differentiation: 4

## References
- OpenTelemetry Semantic Conventions concept docs (opentelemetry.io/docs/concepts/semantic-conventions/)
- OpenTelemetry blog: stability proposal announcement (opentelemetry.io/blog/2025/stability-proposal-announcement/)
- Rust OpenTelemetry docs landing page (opentelemetry.io/docs/languages/rust/)
- `opentelemetry-semantic-conventions` crate (crates.io/crates/opentelemetry-semantic-conventions; docs.rs/opentelemetry-semantic-conventions)
