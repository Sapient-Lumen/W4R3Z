---
id: P-0421
title: pprof + OpenTelemetry Profiling + Parca Interop Workbench Kit — profile locks, symbolization receipts, and cross-signal performance evidence
status: idea
domains: [profiling, observability, performance, debugging, telemetry, interop, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://github.com/google/pprof
  - https://github.com/google/pprof/blob/main/proto/profile.proto
  - https://opentelemetry.io/blog/2024/profiling/
  - https://opentelemetry.io/docs/specs/semconv/registry/attributes/pprof/
  - https://github.com/parca-dev/parca
  - https://docs.rs/pprof
  - https://docs.rs/pprof_util
---

# Problem

Profiling is finally becoming a first-class interoperability surface instead of a per-language side alley. `pprof` remains the de facto profile artifact family, Parca explicitly treats `pprof` as an open standard, and OpenTelemetry is actively building a profiling signal that can correlate with other telemetry.

Rust already has meaningful pieces — `pprof`, utilities for profile manipulation, and ecosystem paths into continuous profiling — but failures still happen at the seam between:

- **a raw `pprof` artifact and the exact symbolization/build-ID assumptions required to interpret it**,
- **always-on profiling backends and the portable profile bundle someone else can inspect offline**,
- **`pprof` data and the OpenTelemetry profiling model / attributes used to connect it to traces and resources**,
- **continuous profiling UI views and the underlying evidence needed for regression review or incident handoff**,
- and **performance investigations that still degrade into screenshots of flamegraphs with missing provenance.**

The missing Rust contribution is not another profiler. It is an **interop workbench** for pinning profile format, symbolization state, build IDs, resource labels, cross-signal links, and replayable evidence in one boring bundle.

# What it provides

- `profile.lock` — pins profile family, symbolization state, build IDs, resource labels, and OTel correlation assumptions.
- `symbolization-receipt` — records what debug info, mappings, and fold/unfold steps were used.
- `profile-diff` — semantic diff between two profiles beyond “file changed”.
- `otel-bridge` — adapter that emits OTel-friendly correlation receipts from pinned profile artifacts.
- `cargo profile-evidence` — emits `*.profilebundle.zip` with raw profiles, receipts, diffs, and notes.

# What the crate should provide other people

1. **A boring handoff bundle for performance investigations**.
2. **Reproducible symbolization** instead of one-off local flamegraph state.
3. **A stable bridge between `pprof` artifacts and OTel-style resource/profile metadata**.
4. **Diffable evidence for regressions** rather than screenshot-based review.
5. **A Rust-native profile-core library** that other profilers, agents, and CI tools can reuse.

# Persona / who it’s for

- performance and observability engineers
- runtime / infra teams running continuous profiling
- incident responders and regression triage teams
- tool builders integrating Rust with `pprof`/Parca/OTel ecosystems

# Users & user stories

- **Perf engineer**: “Package the exact profile plus symbolization inputs behind this flamegraph.”
- **CI owner**: “Diff these two profiles and tell me whether the change is real or just symbolization drift.”
- **Observability engineer**: “Attach resource/tracing context to a profile bundle without inventing a new profile format.”
- **Incident responder**: “Share one portable archive instead of screenshots and ad hoc profile exports.”

# Prior art (and why it’s insufficient)

- `pprof` defines a common profile format and tooling family.
- Parca stores and visualizes `pprof`-formatted profiles.
- OpenTelemetry is building a profiling signal and `pprof`-related semantic conventions.
- Rust already has `pprof` and emerging utility crates.

What Rust still lacks is a **portable evidence layer** that pins raw profile artifacts, symbolization assumptions, build IDs, and cross-signal links together.

# Design goals

1. **Profile-family honest** — keep `pprof` artifacts primary instead of inventing another profile format.
2. **Symbolization-explicit** — missing or changed debug info must be visible.
3. **Cross-signal ready** — allow trace/resource correlation without making it mandatory.
4. **Diffable** — compare profiles semantically, not only bytewise.
5. **CI-friendly** — approval and regression review should work offline.

# MVP surface

- Minimal types: `ProfileLock`, `SymbolizationReceipt`, `ProfileDiff`, `OtelBridgeReceipt`, `ProfileBundle`
- Minimal functions:
  - `read_pprof()`
  - `capture_symbolization()`
  - `diff_profiles()`
  - `emit_otel_receipt()`
  - `write_bundle()`
- Feature flags:
  - `pprof`
  - `otel`
  - `parca`
  - `jemalloc`
  - `redaction`

# Compatibility story

- Centers the existing `pprof` ecosystem rather than replacing it.
- Supports offline bundles from already-collected profiles.
- Treats OTel correlation as an adapter above raw profile artifacts.
- Leaves storage/UI/query systems out of the core.

# Conformance & fixtures

- Goldens for symbolization drift, folded/unfolded stacks, build-ID mismatches, label drift, and merged-profile ambiguity.
- Tiny CPU and heap profile corpora.
- Fixtures that connect raw profiles to trace/resource metadata receipts.
- Redacted example bundles for public bug reports.

# Path to boring stability

- Stabilize `profile.lock`, symbolization receipts, and diff output before chasing every profiler source.
- Start with offline `pprof` artifact handling.
- Keep Parca/OTel adapters thin and optional.
- Resist drift into becoming a full profiler or profiling backend.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 5/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that ingest a `pprof` profile, pin symbolization/build-ID assumptions, emit semantic diffs and OTel correlation receipts, and package the result into `*.profilebundle.zip`.

# De-risk plan

1. Start with `pprof` input/output and offline diffing.
2. Add symbolization receipts before any deep backend integration.
3. Treat OTel metadata as additive overlays.
4. Pilot in CI/regression-review workflows first.

# Non-goals

- Not another sampling profiler.
- Not a profile store or UI.
- Not a replacement for Parca.
- Not a full OpenTelemetry collector component.

# Architecture & API sketch

```rust
pub struct ProfileLock {
    pub format: String,
    pub build_ids: Vec<String>,
    pub symbolization_state: String,
    pub resource_labels: Vec<(String, String)>,
}

pub fn read_pprof(path: &std::path::Path) -> Result<ProfileBundle>;
pub fn capture_symbolization(bundle: &ProfileBundle) -> Result<SymbolizationReceipt>;
pub fn diff_profiles(a: &ProfileBundle, b: &ProfileBundle) -> ProfileDiff;
pub fn emit_otel_receipt(bundle: &ProfileBundle) -> Result<OtelBridgeReceipt>;
```

Bundle draft: `profile.lock`, `raw.pb.gz`, `symbolization-receipt.json`, `profile-diff.json`, `otel-receipt.json`, `notes.md`.

# Security / safety model

- Support redaction of paths, hostnames, container IDs, and symbols where needed.
- Keep raw profiles and symbolized views distinct.
- Mark inferred labels/correlations separately from observed facts.
- Allow public bundles that preserve statistical shape while removing sensitive identifiers.

# Maintenance & governance plan

- Track `pprof` and OTel profiling expectations explicitly.
- Keep symbolization and format handling in the core; backends stay optional.
- Publish small regression corpora with controlled build IDs.
- Avoid scope creep into always-on profiling infrastructure.

# Milestones

## 0.1
- `profile.lock`
- raw `pprof` bundle reader/writer
- symbolization receipt schema

## 0.2
- profile diff engine
- OTel correlation receipt
- redacted public corpus

## 1.0
- stable `*.profilebundle.zip`
- compatibility policy for `pprof`/OTel bridge assumptions
- CI-friendly performance evidence gates

# Open questions

- What is the smallest portable receipt that still makes symbolization reproducible?
- Which OTel profiling fields belong in the stable core versus overlays?
- How should merged or downsampled profiles declare their derivation chain?

# Sources

- `pprof` repository: https://github.com/google/pprof
- `profile.proto`: https://github.com/google/pprof/blob/main/proto/profile.proto
- OpenTelemetry profiling announcement: https://opentelemetry.io/blog/2024/profiling/
- OTel `pprof` semantic attributes: https://opentelemetry.io/docs/specs/semconv/registry/attributes/pprof/
- Parca repository: https://github.com/parca-dev/parca
- `pprof` crate docs: https://docs.rs/pprof
- `pprof_util` crate docs: https://docs.rs/pprof_util
