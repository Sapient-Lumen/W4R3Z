# Design: Model Surface Kit (`cargo modelcheck`, `model-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust program’s supported model/inference surface: model identity, task/modality claims, tokenizer behavior, artifact sets, runtime/backend capabilities, checked examples, and evidence that the declared model surface still matches the shipped Rust application or crate.

This should **not** replace Candle, Burn, `ort`, `tract`, `tokenizers`, `hf-hub`, safetensors, GGUF, or model hubs.
It should make them compose better and make support claims reviewable.

## References (signals)
- Candle already spans CPU, CUDA, NCCL, and WASM/browser use, and ships model-oriented examples and bundled model implementations.
  https://huggingface.github.io/candle/
- Candle’s safetensors module already loads safetensor files into CPU/GPU memory and supports mmap/buffered/sliced loading modes.
  https://docs.rs/candle-core/latest/candle_core/safetensors/
- Burn is positioning itself as a serious multiplatform training/inference framework, and its ONNX import system generates Rust code from ONNX plus BurnPack weights.
  https://burn.dev/
  https://burn.dev/blog/release-0.19.0/
  https://docs.rs/burn-import/latest/burn_import/onnx/struct.ModelGen.html
- `tract` already reads ONNX or NNEF, optimizes them, and runs inference.
  https://github.com/sonos/tract
- `ort` already exposes ONNX Runtime from Rust.
  https://docs.rs/ort/latest/ort/
- `tokenizers` already models tokenization as a real Rust pipeline with normalizer, pre-tokenizer, model, and post-processor stages.
  https://docs.rs/tokenizers/latest/tokenizers/
  https://docs.rs/tokenizers/latest/tokenizers/tokenizer/
- `hf-hub` already aims to stay compatible with the Python Hub cache model.
  https://docs.rs/hf-hub/latest/hf_hub/
- safetensors is a safe zero-copy tensor format with metadata that can be parsed efficiently, even remotely.
  https://huggingface.co/docs/safetensors/index
  https://huggingface.co/docs/safetensors/metadata_parsing
- Hugging Face model cards already support structured metadata such as library, task (`pipeline_tag`), dataset, license, and evaluation results.
  https://huggingface.co/docs/hub/model-cards
- GGUF now has first-class metadata/tensor inspection on the Hub.
  https://huggingface.co/docs/hub/gguf
- Hugging Face’s model-format overview is a useful reality check that modern model packaging is already multi-format in practice.
  https://huggingface.co/blog/ngxson/common-ai-model-formats

## Core components

### 1) `model-surface/v0`
A model-support declaration.

Should include:
- model id and human name
- owning crate/app/service/package identity
- supported tasks or pipeline tags
- modalities (text, image, audio, video, multimodal)
- input/output surface references
- attached tokenizer profile ids
- attached artifact-set ids
- supported runtime-capability-profile ids
- support levels (stable, beta, experimental, legacy)
- deprecation/replacement notes
- raw source attachments (model card, runtime config, hub metadata, local manifests)

Should **not** flatten every runtime or file format into one fake canonical model blob.
It is the review surface, not the runtime.

### 2) `tokenizer-profile/v0`
A portable tokenizer contract.

Should include:
- tokenizer asset identifiers and filenames
- normalizer, pre-tokenizer, model, decoder, and post-processor identity where known
- vocabulary/merges or equivalent raw attachments
- special tokens and reserved ids
- padding/truncation policy
- prompt-template/chat-template references when applicable
- compatibility notes for the attached model surface
- raw attachment pointers (tokenizer JSON, sentencepiece model, merges/vocab files, added tokens)

This artifact exists because tokenizer mismatch is often a real production break, not a documentation footnote.

### 3) `model-artifact-set/v0`
A declaration of the physical artifacts attached to a model surface.

Should include:
- weight artifacts (`.safetensors`, `.onnx`, `.gguf`, `.bpk`, other runtime-specific files)
- config files
- tokenizer files
- adapter/LoRA/delta files
- quantized variants
- sharding/index files
- remote and local source locations
- hashes/signatures/provenance pointers where available
- raw format kind per artifact
- equivalence/relationship notes across variants

Must preserve raw format truth.
A `.gguf` variant and an `.onnx` variant are not magically the same object just because they claim the same task.

### 4) `input-output-profile/v0`
A task/interface-oriented attachment for model I/O.

Should include:
- input modality and representation notes
- expected shapes/sequence policies where meaningful
- output kinds (tokens, logits, embeddings, labels, boxes, masks, transcriptions, etc.)
- preprocessing/postprocessing expectations
- determinism/tolerance notes
- optional schema attachments when the I/O is structured enough to justify Schema Contract integration

This keeps task/interface truth distinct from runtime and file formats.

### 5) `runtime-capability-profile/v0`
A declaration of runtime/backend posture.

Should include:
- runtime lane (Candle-native, Burn-native, ONNX Runtime via `ort`, tract, GGUF runtime, future runtime)
- backend/device lane (CPU, CUDA, Metal, WebGPU, WASM, distributed)
- precision support (fp32, fp16, bf16, int8, int4, etc.)
- quantization assumptions and unsupported combinations
- operator/feature coverage notes
- memory/streaming/mmap support notes
- target/runtime baseline notes
- linked Support Envelope and Footprint attachments when available

This is where v0 can be honest about incomplete runtime parity.

### 6) `model-example-catalog/v0`
A collection of examples and fixtures.

Should include:
- canonical prompts/examples and expected outputs or output tolerances
- tokenizer-boundary examples
- negative/error cases
- quantized-variant comparison fixtures
- illustrative-only vs checked markers
- fixture datasets/media references

Examples are valuable, but v0 must distinguish checked evidence from teaching material.

### 7) `model-check-plan/v0`
A declaration of what will be exercised.

Should include:
- selected runtimes/backends/targets
- selected artifact variants
- selected tokenizer profiles
- selected example fixtures
- selected precision/quantization combinations
- selected functional checks (load, tokenize, shape validation, numerical tolerance, metadata consistency)
- selected perf/resource checks if attached
- skips and unsupported-space notes

### 8) `model-check-report/v0`
A run artifact.

Should record:
- environment/tool/runtime versions
- selected model/tokenizer/artifact/runtime ids
- load success/failure
- tokenizer consistency findings
- shape/dtype/runtime mismatch findings
- missing operator/runtime capability failures
- numerical-tolerance or golden-output results
- linked footprint/perf/resource notes if measured
- linked raw logs/attachments

Should distinguish:
- unsupported combination
- declared combination failed
- illustrative-only material not checked
- metadata drift
- runtime-specific degradation accepted by policy

### 9) `model-diff-report/v0`
Optional diff artifact.

Should explain:
- task/modality changes
- tokenizer changes
- weight/artifact changes
- quantization/profile additions/removals
- runtime support changes
- I/O-surface changes
- evaluation/result metadata changes
- support-level changes

Should distinguish additive, breaking, runtime-specific, and metadata-only drift.

### 10) `model-pack/v0`
Bundle format containing:
- `model-surface/v0`
- one or more `tokenizer-profile/v0`
- one or more `model-artifact-set/v0`
- optional `input-output-profile/v0`
- one or more `runtime-capability-profile/v0`
- optional `model-example-catalog/v0`
- one or more `model-check-report/v0`
- optional `model-diff-report/v0`
- optional raw attachments: ONNX, safetensors metadata, GGUF metadata, model cards, tokenizer files, eval reports, footprints, and signatures

This is the unit that should travel through CI, release review, model packaging, service deployment, and later archaeology.

### 11) `cargo modelcheck`
Reference UX:
- `cargo modelcheck init`
- `cargo modelcheck inspect`
- `cargo modelcheck tokenizers`
- `cargo modelcheck runtimes`
- `cargo modelcheck check`
- `cargo modelcheck diff`
- `cargo modelcheck pack`

`cargo modelcheck` should begin as an explainer / adapter / packer.
It should not pretend to be the one true inference runtime.

## Default policy
- **Separate model identity, tokenizer identity, runtime identity, and artifact identity.**
- **Preserve raw format truth as attachments** instead of flattening ONNX, safetensors, GGUF, BurnPack, and future formats into one fake universal file model.
- **Treat tokenizer behavior as part of the support surface**, not incidental setup.
- **Keep checked and illustrative examples separate** so docs stay honest.
- **Prefer adapters over runtime replacement** in v0.
- **Keep task/modality claims explicit** and trace them to raw model-card or local metadata where possible.

## What the kit should provide to others
- **Application authors:** one reviewable statement of which model artifacts, tokenizers, runtimes, and tasks they actually support.
- **Service teams:** attachable evidence for model behavior that can compose with service/event/settings kits.
- **Platform teams:** artifacts that survive runtime churn and make target/resource assumptions explicit.
- **Policy and trust tooling:** structured hooks for licenses, provenance, model cards, and artifact signatures without pretending those alone prove runtime correctness.
- **Tool authors:** stable inputs that can attach Footprint, Support Envelope, Perf, Schema, and Release Pipeline evidence without owning them.

## Overlap boundaries
- **Not Schema Contract Kit:** structured model I/O may attach schema artifacts, but Model Surface Kit is about model/tokenizer/artifact/runtime support claims above any one schema language.
- **Not Footprint Kit:** that kit measures resource budgets; Model Surface Kit declares model/runtime variants and can attach footprint evidence.
- **Not Support Envelope Kit:** that kit owns target/runtime baseline claims; Model Surface Kit links to them when a given model variant depends on them.
- **Not Runtime Settings Kit:** prompts, model choices, and deployment knobs can attach settings artifacts, but settings are not the model surface itself.
- **Not Service Surface or Event Surface Kits:** those own application interfaces; Model Surface Kit owns the ML boundary behind them.
- **Not Plugin Surface or Wasm Component Kits:** model runtimes may load through plugins/components, but that remains a separate extension/runtime concern.
- **Not Release Pipeline Kit:** release tooling should attach `model-pack/v0`; it should not absorb model-support truth.

## Hard problems (explicitly scoped)
1. **Equivalent task labels are not universal**
   - v0 should preserve raw task tags and local aliases instead of pretending one universal taxonomy is already solved.
2. **Tokenizer mismatch is common and operationally severe**
   - tokenizer assets and behavior must be first-class, not inferred from file names.
3. **Formats are plural and will stay plural**
   - safetensors, ONNX, GGUF, BurnPack, and future formats all matter; v0 must adapt rather than pick one winner.
4. **Runtime parity is incomplete**
   - supported operators, quantization modes, and device lanes differ across runtimes; capability profiles must be explicit.
5. **Numerical identity is contextual**
   - v0 should support tolerances, drift notes, and policy, not fake “same model” guarantees where quantization/runtime differences matter.
