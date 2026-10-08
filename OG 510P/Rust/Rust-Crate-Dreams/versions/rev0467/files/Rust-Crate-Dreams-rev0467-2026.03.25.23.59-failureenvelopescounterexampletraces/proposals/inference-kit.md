---
id: P-0032
title: inference-kit — stable Rust inference API with adapters (tract/ort/…)
status: idea
domains: [ml, ai, inference, interoperability, wasm]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/sonos/tract
  - https://crates.io/crates/ort
  - https://ort.pyke.io/backends
  - https://www.reddit.com/r/rust/comments/186plbx/onnx_libraries_in_rust/
  - https://github.com/e-tornike/best-of-ml-rust
---

# Problem

Rust ML inference is real and growing, but app developers still face a familiar pain:
**every runtime has its own API, tensor types, and deployment constraints.**

Even when all you want is “run this ONNX model,” you must pick a backend early and rewrite integration later.

We need a small, stable crate that defines the **common contract** for inference, and ships adapters to major runtimes.

# Users & user stories

- **Product teams:** “I want inference in Rust without marrying a single backend.”
- **Edge/embedded:** “I need a pure-Rust fallback (or WASM-friendly path) where ONNX Runtime isn’t viable.”
- **Library authors:** “Expose ML features behind a stable trait surface so downstreams can choose backends.”
- **Benchmarkers:** “Run the same model across runtimes and platforms with consistent measurement.”

# Prior art (and why it’s insufficient)

- `tract` is a pure Rust inference toolkit that runs ONNX/NNEF, but it is its own ecosystem.
- `ort` provides a modern ONNX Runtime wrapper and supports alternative backends, but is still a backend-specific API.
- Various crate lists exist, but no standard interface has emerged.

# Design goals

1. **Tiny core interface** that is easy to implement and hard to misuse.
2. **Backend adapters** shipped as separate crates with feature flags.
3. **Tensor interoperability**: minimal set of dtypes/layouts with zero-copy where possible.
4. **Deployment-aware**: WASM/embedded constraints baked in (feature-gated backends).
5. **Ergonomic ONNX path**: load an ONNX model and run it with predictable I/O typing.
6. **Benchmark harness** and golden tests for correctness across backends.

# Non-goals

- Competing with full frameworks (training, autograd, model authoring).
- Providing every exotic tensor feature in v1.

# Architecture & API sketch

Crate split:

- `inference-api` (core traits): `Backend`, `Session`, `Tensor`, `Value`.
- `inference-onnx` (ONNX loader + shape/dtype validation helpers).
- adapters: `inference-tract`, `inference-ort`, etc.

Sketch:

```rust
use inference_api::{Backend, Tensor};
use inference_onnx::Model;

let model = Model::from_path("m.onnx")?;
let backend = inference_ort::OrtBackend::new()?;
let mut session = backend.compile(&model)?;

let input: Tensor<f32> = Tensor::from_array(&[1,3,224,224], data)?;
let outputs = session.run([("input", input)])?;
```

Key design points:
- explicit shape/dtype validation at boundaries
- stable naming/ordering conventions
- streaming outputs for large tensors where possible

# Security / safety model

- Ensure safe FFI boundaries in adapters (especially ONNX Runtime).
- Provide “no dynamic downloads” policy for models in default examples/docs.
- Encourage sandboxing untrusted model execution (integration story with `isolate-kit`).

# Maintenance & governance plan

- Keep `inference-api` dependency-light and semver-stable.
- Adapter crates can evolve faster with independent versions.
- Establish a conformance suite: same ONNX models must match expected outputs within tolerance.

# Milestones

0. **0.1**: `inference-api` + `inference-onnx` minimal, plus one adapter (`inference-tract` or `inference-ort`).
1. **0.2**: second adapter; golden model test suite; benchmark harness.
2. **0.3**: WASM-friendly adapter story (pure Rust).
3. **1.0**: stable tensor/value contract + conformance requirements.

# Open questions

- What is the minimal tensor contract that still supports most inference models?
- How should we handle dynamic shapes (batching) without bloating the API?

# Sources

- tract repo (pure Rust inference; supports ONNX).
- ort crate docs/backends (ONNX Runtime wrapper, alternative backends).
- Community request for abstraction across ONNX libraries.
- Curated Rust ML ecosystem list.
