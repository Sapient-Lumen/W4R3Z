---
id: P-0022
title: privacy-metrics-kit
status: idea
domains: [observability, privacy, tooling, compliance]
last_reviewed: 2026-03-01
evidence:
  - https://internals.rust-lang.org/t/no-telemetry-in-the-rust-compiler-metrics-without-betraying-user-privacy/19275
  - https://docs.rs/opendp/latest/opendp/
  - https://crates.io/keywords/differential-privacy
---

# Problem
Rust projects (especially developer tools and CLIs) often *want* basic usage/health metrics, but “telemetry” is culturally fraught and frequently rejected unless it is transparent and privacy-preserving.

Today, teams either:
- avoid metrics entirely (losing feedback loops), or
- bolt on ad-hoc instrumentation that’s hard to audit and easy to get wrong.

# Users & user stories
- **Tool maintainers**: “I want to know which subcommands are slow or crashy without collecting anything sensitive.”
- **Enterprises**: “I need opt-in, auditable, policy-controlled metrics that can run offline.”
- **Security/privacy reviewers**: “I need a manifest of exactly what is collected, how it is protected, and where it goes.”

# Prior art (and why it’s insufficient)
- `tracing`/OpenTelemetry/Prometheus stacks: great plumbing, but not a privacy/consent framework.
- Differential privacy libraries (e.g., OpenDP): powerful, but not integrated into a practical “shipping metrics” workflow for Rust tools.

# Design goals
1. **Default-off / explicit opt-in** with a clear consent surface.
2. **Auditable by construction**: metrics must be declared in a manifest, with types and privacy class.
3. **Safe primitives** for common needs (counters, histograms, crash pings) with *automatic redaction* rules.
4. **Optional privacy-preserving modes**:
   - local-only (write to disk),
   - aggregated export (no raw events),
   - local DP mechanisms (bounded contribution, privacy budget).
5. **Small dependency footprint** for “tooling/CLI” use.

# Non-goals
- A hosted analytics SaaS.
- Full-blown observability stack replacement.
- Collecting user identifiers, file paths, or raw command lines by default.

# Architecture & API sketch
## Concepts
- **Manifest** (versioned): defines metric names, types, units, and privacy class.
- **Collector**: local in-process sink that enforces policy + shaping.
- **Exporter**: optional outputs (file, stderr, OTLP metrics, Prometheus exposition).

## Example API
```rust
use privacy_metrics_kit::{manifest, counter, Kit};

static MANIFEST: manifest::Manifest = manifest::include!("metrics.toml");

fn main() {
    let kit = Kit::from_env(MANIFEST).expect("policy");
    let build_ms = counter!("build_ms_total"); // checked against manifest at compile-time via macro expansion
    build_ms.add(123);
    kit.flush();
}
```

## Manifest requirements
- metric name, type, unit
- privacy class: {public, coarse, sensitive}
- bounds (min/max) for DP-safe aggregation
- export permissions (local only / allowed exporters)

# Security / safety model
- **No raw event export** in MVP; only aggregated values.
- **Policy gate**: a single config file (or env var) controls enablement and export targets.
- **Redaction helpers**: utilities for hashing/bucketing (e.g., duration buckets) rather than logging values.
- **DP support** (phase 2): bounded contribution + per-metric epsilon budgets; refuse to export if bounds missing.

# Maintenance & governance plan
- Keep “core” crate dependency-light.
- Treat manifest schema changes as semver-major.
- Provide a “privacy review checklist” in-repo; require it for new metric additions.

# Milestones
- **0.1**: manifest format + macros + local file exporter + policy gate.
- **0.2**: OTLP metrics exporter + Prometheus exposition.
- **0.3**: DP-safe aggregations for counters/histograms (optional feature flag).
- **0.4**: crash/exception reporting as *counts* (no stack traces unless user explicitly enables).
- **1.0**: stable manifest + compatibility policy + docs for “tool maintainers” and “enterprise rollout”.

# Open questions
- How strict should compile-time validation be (e.g., reject unknown metrics at build time vs runtime)?
- How to handle “version skew” between binaries and policy manifests?

# Sources
- Rust community discussion: telemetry without betraying privacy — https://internals.rust-lang.org/t/no-telemetry-in-the-rust-compiler-metrics-without-betraying-user-privacy/19275
- OpenDP library (DP building blocks) — https://docs.rs/opendp/latest/opendp/
- Differential privacy ecosystem keyword — https://crates.io/keywords/differential-privacy
