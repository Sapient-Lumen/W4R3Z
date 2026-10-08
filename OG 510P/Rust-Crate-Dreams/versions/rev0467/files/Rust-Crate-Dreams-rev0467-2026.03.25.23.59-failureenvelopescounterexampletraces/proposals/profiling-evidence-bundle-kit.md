---
id: P-0117
title: Profiling Evidence Bundle Kit (CPU + heap + async)
status: idea
domains: [performance, devtools, observability, profiling]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/flamegraph-rs/flamegraph
  - https://crates.io/crates/pprof
  - https://docs.rs/jemalloc_pprof/latest/jemalloc_pprof/
  - https://crates.io/crates/tracing-flame
---

# Problem

Rust has excellent profiling building blocks (perf + flamegraphs, pprof output, allocator heap profiling, tracing-to-flame), but the workflow is fragmented:

- multiple tools with incompatible outputs,
- “works on my machine” environment drift (symbols, flags, kernel settings),
- hard-to-share profiles (no standard bundle that maintainers can reproduce),
- minimal CI ergonomics (how do you gate “regressed by 20%” responsibly?).

The missing crate is **not another profiler**; it is a **portable evidence bundle** + cargo UX that standardizes collection and comparison.

# What it should provide other people

## 1) A standard `*.profbundle.zip` artifact

A deterministic bundle format that can be attached to issues/PRs:

- `manifest.json` (tool versions, OS/kernel, CPU model, build profile, commit SHA)
- `binary/` (optional, or a build recipe + hash)
- `symbols/` (optional cache pointers; never require full debug artifacts)
- `cpu.pprof` (pprof protobuf)
- `heap.pprof` (optional; jemalloc or other backends)
- `tracing.folded` (optional; folded stacks from tracing-flame)
- `notes.md` (what to do next; repro steps)
- `redaction.json` (paths/usernames sanitized)

## 2) `cargo profile` workflows

- `cargo profile cpu` — capture CPU profile → `cpu.pprof`
- `cargo profile heap` — capture heap profile → `heap.pprof`
- `cargo profile flamegraph` — produce SVG (optional, non-authoritative)
- `cargo profile bundle` — assemble the profbundle (the unit of collaboration)
- `cargo profile diff <A> <B>` — produce a stable `profile-diff.json`:
  - top regressions by symbol,
  - “frame moved” heuristics,
  - confidence scoring (sampling noise awareness).

## 3) Backend adapters (feature-gated)

- perf / `cargo-flamegraph`
- pprof-based CPU sampling
- allocator backends (jemalloc_pprof initially, others later)
- tracing-derived folded stacks (tracing-flame)

## 4) CI gating “profiles” (safe defaults)

- `pr-smoke`: short sample, low overhead, warn-only
- `nightly`: longer sample, regression thresholds, trend storage
- `release`: gated by confidence + repeated samples (avoid noisy failures)

# MVP (4–6 weeks)

- Define `profbundle` schema (JSON) + pack/unpack.
- Support:
  - CPU profiling via `pprof` crate,
  - flamegraph generation via `cargo-flamegraph` (as an optional helper),
  - tracing folded stacks via `tracing-flame`.
- Generate a minimal `profile-diff.json` for A/B comparisons of pprof symbol tables.

# v1 (8–16 weeks)

- Heap profiles via `jemalloc_pprof` (feature-gated).
- Deterministic symbol resolution strategy:
  - local DWARF,
  - debuginfod (optional),
  - “symbol map” caching.
- Stabilize diff semantics:
  - normalize inlining frames,
  - group by crate/module,
  - handle LTO variability.

# Conformance & testing

- Fixture corpus of small programs with known hotspots; golden diffs.
- “Noise harness”: run N profiles and ensure diff stability bounds.

# Notes

This kit is deliberately *artifact-first*: maintainers can request “attach a profbundle”, reproduce locally, and compare across versions without re-teaching profiling tooling every time.

