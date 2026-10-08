---
id: P-0166
title: Sensitive Data Redaction & Policy Kit — correct-by-default PII handling for logs/traces/metrics in Rust
status: idea
domains: [security, privacy, observability, policy, dx]
last_reviewed: 2026-03-05
evidence:
  - https://opentelemetry.io/docs/security/handling-sensitive-data/
  - https://opentelemetry.io/docs/languages/dotnet/logs/redaction/
---

# Problem
Observability pipelines frequently leak secrets and PII (tokens, emails, IDs). OpenTelemetry is explicit that implementers must decide what’s sensitive and enforce handling, but **the Rust ecosystem lacks an ergonomic, end-to-end “redaction policy + tests + evidence” kit**. citeturn0search7

# What this crate should provide (to other people)
A policy-first toolkit that makes “safe telemetry” the default:

- `redaction-kit`:
  - declarative policies (allow/deny, regex, structured-field classification)
  - schema-aware redaction (attribute keys, headers, JSON fields)
  - deterministic transforms with **explain traces** (“why was this redacted?”)
- `cargo redaction doctor`:
  - scan telemetry for high-risk fields
  - produce a stable `redaction-report.json` for CI gating
- Evidence bundles: `redaction-bundle.zip`
  - before/after samples (sanitized)
  - policy hashes + versioned rules
  - explain logs + diff summaries
- Integrations:
  - `tracing` layer to scrub fields/events
  - OTel exporter hooks to enforce attribute rules
  - optional collector config generator (but library-first)

# Prior art (and why it’s insufficient)
- OTel guidance exists (and SDKs have examples), but Rust needs a **shared policy contract** and repeatable tests. citeturn0search3turn0search7

# Design goals
- **Policy as code**: policies live in-repo, reviewed, tested, versioned.
- **Deterministic**: same input + policy → same output (diffable in CI).
- **Explainability**: every redaction decision can be traced.
- **Ergonomic**: drop-in defaults for common sensitive classes (auth headers, tokens, emails).

# Policy format sketch
- `redaction.toml`:
  - `classes`: `pii.email`, `secret.token`, `id.user`
  - `rules`: matchers (key paths, regex, type hints) + actions (hash, drop, mask, allow)
  - `exceptions`: audited allowlist (with expiry dates)

# Conformance & testing
- A corpus of “known bad” samples (tokens, cookies, IDs) and expected sanitized outputs.
- Property tests: no policy should *increase* sensitive entropy leakage.
- Optional “canary” mode that counts redaction hits and alerts on regressions.

# Milestones
- 0.1: `tracing` layer + policy parser + deterministic redaction + report.json
- 0.2: OTel exporter integration + evidence bundle tool
- 0.3: CI mode + corpus pack + explain traces
