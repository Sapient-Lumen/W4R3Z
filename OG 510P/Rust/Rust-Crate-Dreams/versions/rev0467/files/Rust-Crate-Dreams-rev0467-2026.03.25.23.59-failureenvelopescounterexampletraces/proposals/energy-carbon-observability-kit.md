---
id: P-0123
title: Energy & Carbon Observability Kit (bench + CI diffs)
status: idea
domains: [performance, devtools, sustainability, benchmarking, linux]
last_reviewed: 2026-03-05
evidence:
  - https://docs.kernel.org/power/powercap/powercap.html
  - https://www.kernel.org/doc/Documentation/power/powercap/powercap.txt
  - https://bheisler.github.io/criterion.rs/book/
  - https://docs.rs/criterion/latest/criterion/
  - https://ilmanzo.github.io/post/measure_your_power_consumption/
---

# Problem

Rust teams increasingly care about energy and laptop battery impact, but the workflow is fragmented:

- some measure CPU time, others measure wall time,
- energy counters are OS/CPU-specific (RAPL, powercap, perf),
- results are noisy and hard to compare across runs,
- there is no “standard artifact” that makes energy regressions actionable in CI.

The ecosystem has excellent benchmarking (Criterion), but lacks a crate that elevates
**energy** (and eventually carbon) to a first-class regression metric with reproducible evidence.

# What it should provide other people

## 1) A standard artifact: `*.energybundle.zip`

A portable bundle that captures:

- `meta.json` (hardware model, governor, turbo state if known, kernel version),
- `bench.json` (criterion-like statistical summaries),
- `energy.json` (joules per domain where available: pkg/cores/dram),
- `timeline.csv` (optional sampling over time),
- `notes.md` (run conditions),
- `report.json` (diff-friendly summary: joules/op, joules/sec, confidence).

Crucially: an **explicit measurement method** field:
- `powercap:intel-rapl`,
- `perf:power/energy-pkg/`,
- `external:...` (future adapters).

## 2) `cargo energy` workflows

- `cargo energy bench` — run benchmark suites and produce bundles.
- `cargo energy diff <baseline> <candidate>` — compare bundles with thresholds.
- `cargo energy doctor` — warn on obvious confounders (scaling governor, background load).

## 3) Adapters that degrade gracefully

- Linux-first MVP:
  - prefer `powercap` sysfs when available (best precision, simple),
  - fallback to `perf stat` energy events when powercap isn’t available.
- “No energy available” mode:
  - still produce valid bundles with CPU+wall time and mark energy as unavailable.

# Design sketch

## Components

- `energy-sensors` (readers for powercap + perf parsing)
- `energybundle` (artifact format + validation)
- `cargo-energy` (integration)

## Statistical approach

- Piggyback on Criterion’s measurement loops where possible.
- Provide a “measurement plugin” trait:
  - start sample,
  - stop sample,
  - emit joules and metadata.

# MVP (credible in 2–6 weeks)

- Bundle schema + validator.
- Linux powercap reader for intel-rapl zones.
- Criterion integration:
  - wrapper harness that measures energy per benchmark group.
- `cargo energy bench` + `diff`.

# v1 scope (what makes it epic)

- CI-friendly noise model:
  - warmup policies,
  - outlier detection,
  - confidence intervals on joules/op.
- Support AMD where feasible (best-effort; document limitations).
- Optional “carbon intensity” attachment:
  - ingest external carbon-intensity values as metadata (no baked-in network calls).
- Export formats:
  - GitHub PR comment markdown,
  - JSON for dashboards.

# Testing

- Fake sensor backend for deterministic unit tests.
- Golden bundle fixtures in repo.
- Validate reading/parsing against documented kernel interfaces.

# Risks and non-goals

- Not a “power limit controller” crate (though powercap supports caps); focus on measurement.
- Cross-platform parity will take time; keep core format stable and adapters optional.

# Adoption path

1) Start with Linux developer laptops + CI runners.
2) Add well-documented “how to reduce noise” guidance.
3) Encourage library maintainers to publish energy-regression badges for critical crates.
