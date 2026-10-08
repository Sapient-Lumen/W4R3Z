---
id: P-0211
title: OpenMetrics / Prometheus Exposition Conformance Kit — parsers, canonicalization, fuzz corpora, and repro bundles
status: idea
domains: [observability, metrics, formats, conformance, fuzzing]
last_reviewed: 2026-03-05
evidence:
  - https://prometheus.io/docs/specs/om/open_metrics_spec/
  - https://github.com/prometheus/OpenMetrics
  - https://crates.io/crates/openmetrics-parser
needs:
  - A stable, spec-aligned foundation for OpenMetrics / Prometheus text exposition *that is test-harness-grade*, not just “a parser”.
  - Canonicalization + round-trip checks so teams can compare outputs across exporters and collectors.
  - Shared fuzz+golden corpora and `*.metricsbundle.zip` failure artifacts for CI and interop.
risks:
  - Spec evolution (OpenMetrics 2.0 work) and Prometheus compatibility footguns; must pin versions and ship compatibility modes.
  - High stakes for correctness (monitoring + billing); require conservative defaults and strong test suites.
---

## Problem

Metrics pipelines are “stringly typed” at their boundaries. Teams repeatedly re-implement parsing, escaping/unescaping, validation, and “diffable output”.

OpenMetrics is specified by Prometheus and has a published spec.
Source: https://prometheus.io/docs/specs/om/open_metrics_spec/

Rust has parsers (e.g., `openmetrics-parser`), but the ecosystem lacks a **conformance+interop workbench** that provides corpora, canonicalization, fuzzing, and portable repro artifacts.
Source: https://crates.io/crates/openmetrics-parser

## What this crate should provide

### 1) `openmetrics-conformance` core library
- Parse to a stable IR:
  - MetricFamily, Sample, LabelSet, Exemplars, Units, Help/Type metadata
- Validate against selected spec mode:
  - `prometheus-text` (legacy)
  - `openmetrics-1.0` (strict)
  - “collector tolerant” (for ingestion compatibility)

### 2) Canonicalization (“diffable output”)
- Stable sort orders for families/samples/labels
- Normalized floats (`NaN`, `+Inf`, `-Inf`) and timestamp handling
- Deterministic escaping rules
- Canonical text writer + canonical JSON writer

### 3) Golden corpora + compatibility fixtures
- `fixtures/openmetrics/`:
  - must-pass spec examples
  - real-world scrape samples (redacted)
  - negative tests (invalid labels, dup samples, bad TYPE/UNIT)
- Version-pinned snapshot packs: `openmetrics-fixtures-v1/…`

### 4) Fuzzing + minimization
- Built-in fuzz harnesses (feature-gated) for:
  - parser (panic safety)
  - canonical writer (round-trip)
  - validator (invariants)
- Minimizer that emits a smallest failing input.

### 5) Repro bundles: `*.metricsbundle.zip`
- `input.txt` (minimized)
- `mode.json` (spec mode + settings)
- `parse.json` (IR dump)
- `errors.json` (structured diagnostics)
- `env.json` (crate version, git SHA)

### 6) Tooling UX
- `cargo openmetrics check <file|url>`
- `cargo openmetrics canon <file|url>`
- `cargo openmetrics fuzz` (optional)

## Prior art (and why it’s insufficient)

- OpenMetrics spec + repo define the target behavior and will evolve (2.0 work noted in repo).
  Source: https://github.com/prometheus/OpenMetrics
- Existing Rust parsers are valuable, but do not consistently provide canonicalization/diffing, shared corpora, fuzz harnesses, and portable failure bundles.
  Source: https://crates.io/crates/openmetrics-parser

## MVP plan (3–6 weeks)

1. Define stable IR + strict parser wrapper (can reuse existing parser crate initially).
2. Canonical text writer (stable ordering + escaping) + JSON writer.
3. Start fixtures:
   - spec-derived + a small curated real-world set.
4. `cargo openmetrics check` that produces `*.metricsbundle.zip` on failure.

## v1 plan (8–12 weeks)

- Compatibility profiles (Prometheus vs OpenMetrics strict).
- Differential testing:
  - compare against another implementation (language-agnostic via bundles) when available.
- Fuzz harness + minimization pipeline.

## Why this is “missing-middle” and high leverage

If Rust becomes *the easiest place to validate and canonically diff metrics*, it reduces operational risk for exporters, sidecars, and collectors — and creates a shared language for interop bugs.
