# Epic proposal: Model Surface Kit

## Thesis
Rust’s ML ecosystem is now strong enough that the missing contribution is no longer “yet another model runtime.”
The higher-leverage missing piece is a **portable model-surface contract** that lets teams declare, diff, validate, and ship what their model integrations actually promise: task/modality claims, tokenizer behavior, artifact variants, runtime capabilities, checked fixtures, and linked metadata/evidence.

In other words: Rust needs a boring, attachable `model-pack/v0` more than it needs one more runtime wrapper.

## Why now
The ecosystem signals line up:
- Candle already spans CPU, CUDA, distributed, and WASM/browser lanes,
- Burn is explicitly pushing multiplatform training/inference and ONNX-to-Rust import,
- `tract` is a serious self-contained inference toolkit for ONNX/NNEF,
- `ort` gives Rust access to ONNX Runtime,
- `tokenizers` is a real Rust tokenizer pipeline rather than a tiny helper crate,
- `hf-hub` gives Rust clients a cache-compatible Hub lane,
- safetensors and GGUF both expose inspectable model metadata surfaces,
- and model cards already carry structured metadata for task, datasets, library, license, and evaluation results.

That means the missing substrate is not raw capability.
It is the **reviewable model boundary above today’s pieces**.

Sources:
- https://huggingface.github.io/candle/
- https://burn.dev/
- https://burn.dev/blog/release-0.19.0/
- https://docs.rs/burn-import/latest/burn_import/onnx/struct.ModelGen.html
- https://github.com/sonos/tract
- https://docs.rs/ort/latest/ort/
- https://docs.rs/tokenizers/latest/tokenizers/tokenizer/
- https://docs.rs/hf-hub/latest/hf_hub/
- https://huggingface.co/docs/safetensors/index
- https://huggingface.co/docs/hub/model-cards
- https://huggingface.co/docs/hub/gguf

## What should be built
A first credible version should ship:
1. `model-surface/v0`, `tokenizer-profile/v0`, `model-artifact-set/v0`, optional `input-output-profile/v0`, `runtime-capability-profile/v0`, optional `model-example-catalog/v0`, `model-check-plan/v0`, `model-check-report/v0`, optional `model-diff-report/v0`, and `model-pack/v0`
2. adapters for common Rust runtime lanes (Candle, Burn/BurnPack, ONNX Runtime via `ort`, tract, and attachment support for GGUF metadata and Hub/model-card metadata)
3. docs/reference generation for declared tasks, tokenizers, artifact variants, runtime support, and checked combinations
4. validation/reporting support for tokenizer drift, artifact mismatch, runtime-capability mismatch, quantization/profile gaps, and metadata inconsistency
5. release/CI examples showing model packs attached to CLIs, services, edge deployments, and library crates

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one Candle-based application that declares safetensors + tokenizer assets + CPU/CUDA/WASM runtime profiles
- one Burn-based application importing ONNX into Rust code plus BurnPack weights
- one ONNX-centric application that checks the same model surface across `ort` and `tract`
- one GGUF-oriented application that attaches raw GGUF metadata and tokenizer/runtime expectations rather than flattening them away
- one service or CLI deployment that uses the pack to keep model-card metadata, runtime settings, and checked examples attached to the shipped binary

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve task/modality claims, tokenizer truth, artifact identity, and runtime posture
2. **v0.2 adapters**
   - support Candle, Burn/BurnPack, ONNX Runtime, tract, safetensors metadata, GGUF metadata, and model-card attachments
   - support raw artifacts without flattening them into one fake runtime format
3. **v0.3 cross-kit integration**
   - integrate with Footprint, Support Envelope, Perf, Runtime Settings, Schema, Service Surface, Event Surface, Trust Signals, and Release Pipeline workflows
   - support diff/baseline workflows across model variants and runtime lanes
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one runtime choice

## Success metrics
- Teams can review model-support changes as explicit artifacts instead of reading README prose, loader code, and benchmark notes.
- Tokenizer, weight, and runtime assumptions remain documented from one declared source.
- Checked model combinations are easier to trust because illustrative examples stay separate from tested evidence.
- Runtime migrations become easier because model-surface claims survive beyond one inference stack.
- Rust model deployments become easier to hand off to platform, docs, security, and release workflows without bespoke glue.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Runtime Settings Kit covers knobs and precedence,
- Service Surface and Event Surface Kits cover application interfaces,
- Schema Contract Kit covers structured payload descriptions,
- Footprint Kit and Support Envelope Kit cover deployment/resource assumptions,
- and Release Pipeline / Trust Signals cover packaging and distribution evidence.

But none of those is the portable contract for the **composed model/tokenizer/artifact/runtime boundary itself**.
Model Surface Kit is the missing substrate that keeps task claims, tokenizer truth, artifact variants, runtime posture, and checked model behavior attached to one reviewable interface without absorbing every inference runtime into one mega-format.
