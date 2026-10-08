---
id: P-0362
title: ONNX + ONNX Runtime + Backend Test Conformance & Replay Kit — model/opset locks, backend diffs, and replayable inference evidence bundles
status: idea
domains: [ai, machine-learning, model-interchange, inference, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://onnx.ai/onnx/repo-docs/IR.html
  - https://onnx.ai/onnx/repo-docs/OnnxBackendTest.html
  - https://onnx.ai/onnx/repo-docs/ImplementingAnOnnxBackend.html
  - https://onnxruntime.ai/docs/reference/compatibility.html
  - https://crates.io/crates/onnx-ir
  - https://docs.rs/ort
  - https://crates.io/crates/tract-onnx
---

# Problem

Rust now has meaningful ONNX substrate for parsing, loading, and executing models, but the painful failures rarely happen at the level of “can I deserialize the file?” They usually happen at the seam between:

- ONNX IR version, operator-set version, and model metadata assumptions,
- runtime/backend capability differences,
- shape/type inference versus actual execution behavior,
- external-data and packaging details,
- and bug reports that arrive as “this model runs here but fails there” with no portable reproduction artifact.

The missing Rust contribution is not another inference runtime. It is a **conformance-and-replay workbench** that makes ONNX portability failures reproducible, comparable, and shareable.

# What it provides

- `model-lock` — lockfiles pinning IR version, opsets, external-data expectations, precision assumptions, dynamic-shape policy, and backend-specific quirks.
- `onnx-irx` — a neutral IR for normalized model metadata, backend capabilities, inference results, and validator/test findings.
- `backend-probe` — adapters that run one model or fixture set against multiple Rust-accessible backends and normalize the findings.
- `onnx-diff` — semantic diffs such as “same graph, incompatible opset assumptions”, “shape inference drift”, or “numerically acceptable but structurally different output”.
- `cargo onnx-evidence` — emits `*.onnxbundle.zip` containing model metadata, lockfile, backend reports, normalized diffs, and redaction-aware notes.

# What the crate should provide other people

1. **A boring default artifact for ONNX portability bugs**.
2. **Backend-aware locks** that pin exactly what a model expects and what a runtime actually supports.
3. **Normalized comparison across runtimes** so failures are attributable to opset drift, unsupported operators, layout assumptions, or numeric tolerance boundaries.
4. **Replayable CI and bug reports** without custom notebooks and ad hoc scripts.
5. **A bridge from Rust ONNX parser/runtime crates to evidence-grade interop workflows**.

# Persona / who it’s for

- Rust ML-platform teams shipping ONNX models to edge, desktop, or server runtimes
- Authors of Rust ONNX tooling and runtime adapters
- Teams migrating models between Python-centric build pipelines and Rust deployment targets
- Benchmark and compatibility harness authors

# Users & user stories

- **Inference engineer**: “Tell me whether this failure is an unsupported op, an opset mismatch, or a shape/type assumption drift.”
- **Runtime maintainer**: “Run the same fixture corpus against our backend and two others, then diff only the semantic failures.”
- **Deployment team**: “Lock what subset of ONNX this product actually depends on and catch drift in CI.”
- **Model publisher**: “Ship a portable evidence bundle when customers say the model fails on their hardware/runtime stack.”

# Prior art (and why it’s insufficient)

- ONNX publishes a real IR specification and a standard backend-test suite.
- ONNX Runtime publishes compatibility guidance and opset-support framing.
- Rust has real substrate in `onnx-ir`, `ort`, and `tract-onnx`.
- But Rust still lacks a boring-default crate for **model/opset lockfiles + cross-backend replay + semantic diffs + portable evidence bundles**.

# Design goals

1. **Backend-neutral core** — do not hardwire the crate to one runtime.
2. **Version-aware** — IR, opset, and backend capability assumptions must be explicit.
3. **Deterministic artifacts** — evidence bundles and diffs must be stable enough for CI and issue trackers.
4. **Tolerance-aware** — numeric comparisons must remain explainable rather than collapsing into pass/fail noise.
5. **Packaging-aware** — handle external data, model metadata, and bundle-level reproducibility.

# MVP surface

- Minimal types: `ModelLock`, `BackendProfile`, `OnnxBundle`, `InferenceFinding`, `BackendDiffFinding`
- Minimal functions:
  - `inspect_model()`
  - `run_backend_case()`
  - `compare_outputs()`
  - `diff_backend_reports()`
  - `write_bundle()`
- Feature flags:
  - `ort`
  - `tract`
  - `backend-test`
  - `external-data`
  - `redaction`

# Compatibility story

- MVP should target inference-first ONNX workflows, not every training-oriented feature.
- The crate should complement runtime/parser crates rather than replace them.
- Backend adapters can live in optional packs while the lockfile and report schemas stay neutral.
- Numeric-diff policy must be explicit and portable across CPU/accelerator differences.

# Conformance & fixtures

- Tiny models with pinned opsets and expected outputs.
- Cases for unsupported operators, missing initializers, dynamic axes, external data, and dtype drift.
- Goldens for “same IR, different backend support surface”, “same output shape, divergent values”, and “load succeeds but execution fails”.
- Optional adapters for selected ONNX backend-test cases.

# Path to boring stability

- Stabilize the lockfile and evidence-bundle schemas before chasing many backends.
- Start with a small set of Rust-accessible backends.
- Treat numeric-diff reporting as a first-class UX problem.
- Grow outward from tiny public fixtures rather than giant model zoos.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that inspect an ONNX model, pin its IR/opset expectations, run it against one or two Rust-accessible backends, and emit a compact `*.onnxbundle.zip` with normalized compatibility findings and semantic diffs.

# De-risk plan

1. Start with model inspection + lockfile generation before multi-backend diffing.
2. Support one well-understood adapter path first (`ort`), then add others.
3. Keep tolerance and expected-output policy explicit from day one.
4. Use official backend-test style fixtures before chasing large real-world models.

# Non-goals

- Not a new ML runtime.
- Not a full training framework.
- Not a general model-conversion service.
- Not a benchmark suite for every accelerator.

# Architecture & API sketch

```rust
pub struct ModelLock {
    pub ir_version: i64,
    pub opsets: Vec<OpsetPin>,
    pub dynamic_shape_policy: DynamicShapePolicy,
}

pub fn inspect_model(bytes: &[u8]) -> Result<ModelLock>;
pub fn run_backend_case(lock: &ModelLock, model: &[u8], backend: &BackendProfile) -> Result<BackendReport>;
```

Bundle draft: `profile.toml`, `model.onnx`, `metadata.json`, `backend-a/report.json`, `backend-b/report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat models and external data as untrusted input.
- Support bundle redaction for proprietary tensor names and metadata.
- Record exact runtime/backend/library versions in every evidence bundle.
- Keep bundle outputs deterministic enough for trustworthy review and regression tracking.

# Maintenance & governance plan

- Keep the core centered on lockfiles, normalized findings, diffs, and bundle format.
- Version backend adapters separately when necessary.
- Build a public fixture corpus around small but semantically revealing models.
- Avoid coupling the workbench to any one runtime vendor.

# Milestones

## 0.1
- model inspection
- opset/IR lockfile
- single-backend report writer

## 0.2
- multi-backend comparison
- numeric diff policy
- external-data support

## 1.0
- stable `*.onnxbundle.zip`
- backend-test adapter pack
- documented compatibility policy for supported backends

# Open questions

- What minimum subset of backend-test cases is enough for a compelling MVP?
- How should tolerated numeric drift be represented so maintainers trust the diffs?
- Which model metadata belongs in the stable lockfile versus optional annotations?

# Sources

- ONNX IR specification: https://onnx.ai/onnx/repo-docs/IR.html
- ONNX Backend Test: https://onnx.ai/onnx/repo-docs/OnnxBackendTest.html
- Implementing an ONNX backend: https://onnx.ai/onnx/repo-docs/ImplementingAnOnnxBackend.html
- ONNX Runtime compatibility: https://onnxruntime.ai/docs/reference/compatibility.html
- `onnx-ir`: https://crates.io/crates/onnx-ir
- `ort`: https://docs.rs/ort
- `tract-onnx`: https://crates.io/crates/tract-onnx
