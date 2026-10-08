---
id: P-0380
title: SafeTensors + GGUF Model Artifact Interop Workbench Kit — shard/profile locks, conversion-loss diffs, and portable model-file evidence bundles
status: idea
domains: [machine-learning, model-formats, interoperability, validation, tooling, inference, packaging]
last_reviewed: 2026-03-06
evidence:
  - https://huggingface.co/docs/safetensors/index
  - https://github.com/huggingface/safetensors
  - https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
  - https://docs.rs/candle-core/latest/candle_core/safetensors/index.html
  - https://docs.rs/gguf
  - https://github.com/huggingface/candle
---

# Problem

Rust already has meaningful substrate for model-file work: `safetensors` is well established, Candle loads and saves safetensors, and multiple crates parse GGUF. But the painful failures increasingly sit at the seam between:

- **sharded SafeTensors layouts and the logical tensor inventory**,
- **GGUF metadata / quantization declarations and what executors actually expect**,
- **weight files and the surrounding artifact contract** (tokenizer/config/chat-template/context assumptions),
- **format conversion and what was silently lost or rewritten**,
- and **“this model loads in executor A but not B” reports that ship no portable evidence**.

The missing Rust contribution is not another inference engine. It is a **model-artifact workbench** that treats SafeTensors, GGUF, and adjacent model metadata as one reviewable interoperability problem.

# What it provides

- `model-profile.lock` — pins format family, shard manifests, tensor inventory expectations, quantization/metadata policy, and optional executor-profile overlays.
- `model-irx` — a neutral IR for tensors, shard layout, GGUF metadata, tokenizer/config references, and conversion-loss findings.
- `inventory-diff` — semantic diffs such as “same tensors, different shard layout”, “same model family, quantization metadata changed”, or “conversion dropped auxiliary metadata”.
- `conversion-report` — tracks SafeTensors ↔ GGUF or adjacent transformations as explicit findings instead of hand-wavy success/failure.
- `cargo model-evidence` — emits `*.modelbundle.zip` with lockfile, inventory summaries, metadata diffs, and notes.

# What the crate should provide other people

1. **A boring default artifact for model-file interoperability bugs**.
2. **Explicit shard/profile locks** instead of vague “supports safetensors / GGUF”.
3. **Conversion-loss accounting** for format and metadata transitions.
4. **Portable bundle evidence** for Rust inference stacks and model-tooling pipelines.
5. **A shared review surface** for format, metadata, and executor assumptions above existing loaders.

# Persona / who it’s for

- Rust maintainers building model loading, conversion, or deployment tools
- Teams shipping local/edge inference artifacts
- Researchers trying to reproduce model-loading mismatches without giant ad hoc attachments
- Infra engineers validating model artifact policies in CI

# Users & user stories

- **Maintainer**: “Show me whether a failing artifact changed tensor inventory, metadata, quantization, or only shard layout.”
- **Deployment engineer**: “Pin the exact artifact contract we support and fail CI when it drifts.”
- **Converter author**: “Emit an explainable loss report when translating between formats.”
- **Support engineer**: “Share a compact evidence bundle without shipping full multi-gigabyte weights.”

# Prior art (and why it’s insufficient)

- SafeTensors is positioned as a safe, fast tensor storage format and has first-class Rust support.
- Candle can load and save SafeTensors.
- GGUF is documented as a file format for fast-loading GGML-based inference artifacts.
- Rust crates already parse GGUF metadata and structures.

What Rust still lacks is a **boring default artifact-layer workbench** for shard manifests, metadata/profile locks, conversion-loss reporting, and portable evidence bundles above existing loaders.

# Design goals

1. **Artifact-first** — model-file debugging should not require running inference.
2. **Shard-aware** — layout and inventory must be explicit and comparable.
3. **Loss-honest** — conversions must report what changed or vanished.
4. **Executor-aware but neutral** — allow profile overlays without locking into one runtime.
5. **Large-file disciplined** — support summaries and proofs without requiring full artifact copies.

# MVP surface

- Minimal types: `ModelProfileLock`, `TensorInventory`, `ModelFinding`, `ModelBundle`
- Minimal functions:
  - `inspect_safetensors()`
  - `inspect_gguf()`
  - `diff_model_profiles()`
  - `write_bundle()`
- Feature flags:
  - `safetensors`
  - `gguf`
  - `shards`
  - `metadata`
  - `sampling`

# Compatibility story

- Builds on existing Rust loaders and parsers instead of replacing them.
- Can operate on summaries, header data, and selected tensor inventories when full artifacts are too large.
- Treats tokenizer/config or executor assumptions as explicit overlays around a stable core bundle schema.
- Keeps conversion adapters modular.

# Conformance & fixtures

- Tiny fixtures for sharded SafeTensors inventories, missing metadata keys, incompatible GGUF headers, quantization-profile drift, and conversion-loss cases.
- Goldens for “same logical tensors, different artifact layout” and “loads in one profile, fails another due to metadata assumptions”.
- Sample bundles that preserve inventory and metadata while omitting bulk tensor payloads.
- Public fixture packs for known artifact-shape edge cases.

# Path to boring stability

- Stabilize lockfile, inventory schema, and diff categories before broadening format support.
- Start with headers, metadata, shard manifests, and tensor inventory, not whole-model execution.
- Keep the first release focused on artifact correctness and explainability, not conversion throughput or runtime benchmarking.
- Prefer deterministic summaries that are CI-friendly.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that inspect SafeTensors and GGUF artifacts, pin a profile lock, summarize inventories and metadata, and emit a `*.modelbundle.zip` with explainable diffs and conversion findings.

# De-risk plan

1. Start with inventory/metadata summaries before deep tensor-content comparison.
2. Keep executor overlays optional and explicit.
3. Use public tiny fixture artifacts for test coverage.
4. Avoid turning the project into another inference runtime or model hub.

# Non-goals

- Not a new inference engine.
- Not a full model-conversion platform.
- Not a model registry or hosting service.
- Not a benchmark suite.

# Architecture & API sketch

```rust
pub struct ModelProfileLock {
    pub artifact_family: String,
    pub shard_policy: String,
    pub metadata_policy: String,
}

pub fn inspect_safetensors(bytes: &[u8]) -> Result<ModelReport>;
pub fn inspect_gguf(bytes: &[u8]) -> Result<ModelReport>;
pub fn diff_model_profiles(a: &ModelReport, b: &ModelReport, lock: &ModelProfileLock) -> ModelDiff;
```

Bundle draft: `model-profile.lock`, `inventory.json`, `metadata-report.json`, `conversion-findings.json`, `sample/`, `notes.md`.

# Security / safety model

- Treat model files and metadata as untrusted input.
- Support header/inventory-only bundles when distributing weight payloads is impossible or undesirable.
- Record exact parser/adapter versions in every bundle.
- Keep outputs deterministic and inspectable for CI and support handoff.

# Maintenance & governance plan

- Keep the core centered on profile locks, inventory summaries, diffs, and bundle format.
- Version format-specific adapters independently.
- Publish a small public corpus of tiny fixture artifacts that exercise layout and metadata edge cases.
- Resist expansion into a giant generalized ML platform.

# Milestones

## 0.1
- SafeTensors inspection
- GGUF inspection
- profile lockfile

## 0.2
- cross-format diffs
- shard/inventory reporting
- metadata/conversion findings

## 1.0
- stable `*.modelbundle.zip`
- public fixture corpus
- documented compatibility policy across supported artifact profiles

# Open questions

- Which surrounding files belong in MVP overlays: tokenizer, config, chat template, rope/context metadata?
- How much tensor-content proof is needed beyond inventory/header comparison?
- What is the right default policy for reporting format-conversion loss without pretending equivalence?

# Sources

- SafeTensors docs: https://huggingface.co/docs/safetensors/index
- `huggingface/safetensors`: https://github.com/huggingface/safetensors
- GGUF spec doc: https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
- Candle SafeTensors module: https://docs.rs/candle-core/latest/candle_core/safetensors/index.html
- `gguf` crate: https://docs.rs/gguf
- Candle project: https://github.com/huggingface/candle
