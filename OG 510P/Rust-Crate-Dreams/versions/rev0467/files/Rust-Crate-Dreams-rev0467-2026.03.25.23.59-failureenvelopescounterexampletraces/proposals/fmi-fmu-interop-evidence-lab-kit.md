---
id: P-0225
title: FMI / FMU Interop & Evidence Lab Kit — build, probe, and compare FMUs across tools with reproducible bundles
status: idea
domains: [simulation, control, modeling, fmi, fmu, interop, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://fmi-standard.org/docs/3.0.1/
  - https://github.com/modelica/fmi-standard
  - https://modelica.github.io/fmi-guides/main/fmi-guide/
  - https://crates.io/crates/fmi
  - https://docs.rs/fmi-xtask
needs:
  - A Rust-first way to *reliably* build, inspect, and regression-test FMUs, then compare behavior across simulation tools.
  - A shareable evidence bundle for “tool A integrates this FMU but tool B fails” with normalized traces and metadata.
risks:
  - Tool diversity: different simulators interpret edge cases differently; must focus on measurement + comparison rather than declaring a single truth.
  - Determinism: floating point + solver differences require careful "tolerance profiles" and trace canonicalization.
---

## Problem
FMI/FMUs are a practical interchange format for simulation and digital twins, but engineering teams struggle with:
- building compliant FMUs,
- understanding why a given FMU fails in a specific tool,
- and catching regressions when changing models/toolchains.

Rust has an `fmi` crate (FMU runtime interface) and build tooling like `fmi-xtask`, but the ecosystem lacks a **standard interop harness**: probe → run scenarios → capture traces → compare.

## What this crate provides
A workspace that turns FMU interop into CI-friendly artifacts:

1. **FMU inspector:** parse `modelDescription.xml`, validate structure, extract supported capabilities and variability.
2. **Scenario runner:** run standardized experiments (step responses, parameter sweeps, event handling) using a chosen master/solver.
3. **Tool adapters:** execute the same scenarios across multiple simulators (where available) via adapter interface.
4. **Trace canonicalization:** normalize time series, events, tolerances, and metadata.
5. **Evidence bundles:** `*.fmubundle.zip` with inputs + outputs + logs + capability snapshots.
6. **Diff/explain:** produce an “explain report” for divergences (events at different times, discontinuities, solver step changes).

### Bundle format: `*.fmubundle.zip`
- `manifest.json` (FMI version, platform, runner/tool adapter, solver settings)
- `fmu.sha256` + `modelDescription.xml`
- `capabilities.json` (normalized)
- `scenario.json` (stimulus definition)
- `trace.arrow` or `trace.parquet` (time series)
- `events.jsonl` (discrete events)
- `logs.txt` (tool logs) + `redaction.json`
- `verdict.json` (pass/fail + tolerances)

## Users
- Industrial simulation teams exchanging FMUs across vendors.
- Rust shops embedding simulation models into services.
- Open-source model/tool authors seeking reproducible bug reports.

## Prior art (insufficient)
- FMI standard + implementers’ guides exist, but don’t provide an ecosystem harness.
- `fmi` focuses on consuming FMUs, not tool-to-tool interop testing.
- `fmi-xtask` helps build FMUs from Rust, but interop validation remains manual.

## Design goals
- **Adapter-first:** separate core trace IR from each simulator/tool.
- **Tolerance profiles:** define numeric tolerances per signal and per scenario.
- **Deterministic packaging:** stable bundle structure, stable metadata hashing.
- **Redaction by default:** avoid leaking proprietary model names/paths.

Non-goals:
- Replacing vendor certification suites.
- Providing a full simulation solver stack in the core.

## Architecture sketch
Workspace:
- `fmu-lab-core` — FMU inspector, capability IR, bundle writer/reader.
- `fmu-lab-scenarios` — scenario DSL + standard suites.
- `fmu-lab-trace` — canonicalization, tolerance profiles, diff/explain.
- `fmu-lab-adapter-rust` — baseline runner using Rust `fmi` crate + simple master.
- `fmu-lab-cli` — `inspect`, `run`, `bundle`, `diff`, `report`.

## MVP (4–8 weeks)
1. `inspect` FMU and validate `modelDescription.xml` into a normalized capabilities report.
2. Baseline runner: co-simulation step + basic scenario DSL.
3. Bundle emission + diff between two runs.

## De-risk plan
- Start with FMI 3.0.x subset for co-simulation with fixed step sizes.
- Use a small curated set of open FMUs (license-clean) for regression.
- Add optional golden traces and tolerance tuning per scenario.

## Maintenance
- Keep adapters optional and community-owned.
- Version bundle schema and preserve backward reading.
- Provide a public corpus runner for FMU compatibility smoke tests.

## Sources
- FMI 3.0.1 specification and project repository.
- FMI 3.0 implementers’ guide.
- Rust crates: `fmi`, `fmi-xtask`.
