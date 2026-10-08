# Design: Model Productization Stack (Model Surface + Offload Surface + Runtime Settings + Support Envelope)

## Goal
Turn Rust model-facing products into a **portable productization stack** instead of leaving each project to express its model story as a tangle of model files, tokenizers, backend toggles, hub cache assumptions, quantization variants, lazy-loading tricks, and README folklore.

The stack should **not** replace Candle, Burn, `ort`, `tract`, `tokenizers`, `hf_hub`, safetensors, GGUF, or model hubs.
It should make them compose better and make supported model behavior reviewable.

## Why this note is needed now
Rust’s current model signals say the missing problem is no longer “can Rust run serious models at all?”
They say the missing problem is **what a Rust model product can honestly claim to ship and support**:
- Candle is a native Rust model/runtime lane and its Transformers integration explicitly combines `hf-hub` cache use, lazy safetensor loading, model configs, and Rust model structs.
- Candle’s safetensors support already includes memory-mapped and buffered loading modes, which means artifact-loading posture is part of the real product surface.
- Burn now presents itself as a multi-backend deep-learning framework for training and inference, and Burn 0.19 explicitly added `burn-store` with safetensors interoperability plus ONNX import that generates editable Rust code.
- `ort` is a Rust interface to ONNX Runtime with explicit hardware-accelerated deployment posture, while `tract` is deliberately tiny, self-contained, and portable for ONNX/TensorFlow inference. That is a classic sign that runtime families are real choices, not an implementation detail.
- `tokenizers` is explicit that tokenization is a staged pipeline (normalizer, pre-tokenizer, model, post-processor), and it can load pretrained tokenizers directly from the Hub. That means tokenizer behavior is not “just one file next to the weights.”
- `hf_hub` is explicit that it is trying to stay compatible with the Python Hugging Face cache model while still warning that its own surface is evolving. That makes acquisition/cache/update behavior part of the support boundary.
- safetensors and GGUF both prove that modern model products are multi-format in practice: safetensors emphasizes safe zero-copy tensor storage, while GGUF combines tensor payloads with standardized metadata and quantization variants visible on the Hub.
- Hugging Face model cards now carry structured metadata for task, library, base-model lineage, license, and evaluation results. That means supported model claims increasingly have machine-readable inputs, but Rust still lacks a portable layer that keeps those claims tied to runtime reality.

Together, those signals argue that the missing contribution is **not** another inference runtime, another weight format, another hub clone, or another thin model-downloader crate.
It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Model Surface: artifact, tokenizer, task, and package truth
Model Surface owns the **declared model-facing product boundary**:
- model identity and lineage,
- task/modality claims,
- tokenizer profiles,
- artifact sets and variant relationships,
- runtime capability attachments,
- example and check attachments,
- and imported model-card metadata.

This layer answers questions like:
- “What model family is actually being shipped?”
- “Which tokenizer and prompt/template assumptions are part of the supported interface?”
- “Are ONNX, safetensors, GGUF, Burn-native, or generated-Rust variants all first-class, or only some of them?”

Design rule: **model truth must not remain an incidental side effect of file naming conventions, hub repos, or example code**.

### 2) Offload Surface: backend, device, memory, and precision truth
Real model products are inseparable from backend posture.
Offload Surface owns:
- CPU / CUDA / Metal / WebGPU / WebAssembly / accelerator lanes,
- quantization and precision profiles,
- mmap / buffer / copy posture,
- transfer and fallback behavior,
- and checked backend-specific evidence.

This layer answers questions like:
- “Does this model product support CPU only, accelerator optional, or accelerator required?”
- “Which quantized variants are accepted on which backends?”
- “What really happens when a backend, operator, or kernel is missing?”

Design rule: **backend truth must not hide inside feature flags, benchmark screenshots, or one lucky local run**.

### 3) Runtime Settings: acquisition, cache, auth, activation, and selection truth
Model products change materially through settings:
- model source and revision selection,
- local path vs remote hub acquisition,
- cache directories and reuse posture,
- auth/token requirements,
- device/backend/precision selection,
- model/template/config overrides,
- and local/dev/prod differences.

This layer answers questions like:
- “Which model revision or file variant was actually selected?”
- “Did this use a local cache, a hub token, a bundled asset, or a runtime download?”
- “Which env/config changes alter model behavior materially?”

Design rule: **activation posture is product truth, not mere launcher trivia**.

### 4) Support Envelope + DocProof: public promise and checked-doc truth
Support Envelope and DocProof together own:
- supported targets and runtime floors,
- supported model/runtime/backend combinations,
- supported artifact-source and cache posture,
- docs/examples/tutorial truth,
- and release/support-facing claims.

This layer answers questions like:
- “Which model/backend/target combinations are actually supported versus merely possible?”
- “Do docs and examples reflect real cache/auth/backend behavior?”
- “What can support and release teams safely promise?”

Design rule: **one example that loads a model is not a support contract**.

### 5) Downstream consumers
The stack becomes ecosystem-shaping when real consumers can import it honestly:
- **service / agent / scientific / client** consumers can attach model facts without reinventing them;
- **release / distribution** consumers can distinguish bundled artifacts from on-demand downloads and cached acquisitions;
- **support / incident** consumers can answer whether a failure belongs to tokenizer mismatch, artifact mismatch, backend mismatch, activation mismatch, or support boundary;
- **atlas / learning / documentation** consumers can compare serious Rust model lanes without pretending one runtime or one file format has already won.

Design rule: **consumers import selected model-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust model runner.”
It is a portable boring stack with clear boundaries:

1. **artifact and tokenizer truth first**
   - prove stable product identity, tokenizer profile identity, model-card/task/lineage attachments, and variant-aware artifact declarations on one real model product;
2. **backend and quantization truth second**
   - prove CPU/accelerator/precision/quantization posture can be captured honestly instead of implied by runtime defaults;
3. **acquisition and activation truth third**
   - prove local path / bundled asset / hub cache / authenticated fetch / revision pinning can be expressed as reviewable state;
4. **checked behavior and support/docs fourth**
   - prove examples, eval snippets, and checked docs can be attached without pretending illustrative material is the same as stable support evidence;
5. **consumer imports fifth**
   - prove service, agent, client, scientific, release, and support consumers can reuse the same facts instead of re-deriving them.

An eventual aggregate artifact may exist, but it should be a **thin pack of linked artifacts**, not a mega-schema that erases model truth, backend truth, settings truth, and support truth.

## Ranked first execution lanes
1. **local CPU + safetensors/tokenizer lane**
   - best first exporter because it proves model identity, tokenizer identity, artifact identity, and runtime settings without immediately depending on every backend family.
2. **hub-backed acquisition/cache lane**
   - proves revision, cache, auth, and lazy-loading posture are real product truths.
3. **ONNX / generated-import / runtime-diversity lane**
   - proves multiple runtime families can expose one model-facing contract without being flattened.
4. **quantized / GGUF / backend-divergence lane**
   - proves format-specific metadata and backend-specific support must stay explicit.
5. **consumer lane**
   - proves services, agents, clients, releases, and support/docs systems can import the stack honestly.

## Non-goals
- one universal Rust inference runtime;
- one weight format to replace all others;
- one hub clone or package manager for every model artifact;
- flattening tokenizer truth, model-card truth, backend truth, cache/auth truth, and support truth into one fake “model support” blob;
- pretending scientific, agentic, client, and service uses all want the same model contract shape.

## Archive implications
- The archive should now treat **Model Surface + Offload Surface + Runtime Settings + Support Envelope** as a coupled **Model Productization Stack** in frontier discussions.
- Future revisions should prefer **artifact/tokenizer truth, backend/quantization truth, acquisition/cache/auth activation, and support/docs truth** over another runtime bake-off, weight-format shootout, hub-wrapper crate, or model-serving control plane.
- When Scientific, Agent, Client, Service, Web, Release, or Support work touches model shipment or inference support, it should import model-productization artifacts rather than re-explain model/package/backend/cache posture from scratch.

## Read this together with
- `design/model-surface-kit.md`
- `design/offload-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
- `design/scientific-productization-stack.md`
- `design/agent-productization-stack.md`

## References (signals)
- Burn crate docs:
  https://burn.dev/docs/burn/
- Burn 0.19 storage/import notes:
  https://burn.dev/blog/release-0.19.0/
- Candle core docs:
  https://docs.rs/candle-core/latest/candle_core/
- Candle Transformers integration:
  https://huggingface.co/docs/transformers/en/community_integrations/candle
- `ort`:
  https://docs.rs/crate/ort/latest
- `tract`:
  https://docs.rs/crate/tract/latest
- `tokenizers`:
  https://docs.rs/tokenizers/latest/tokenizers/
- `hf_hub`:
  https://docs.rs/hf-hub/latest/hf_hub/
- safetensors:
  https://huggingface.co/docs/safetensors/index
- GGUF on the Hub:
  https://huggingface.co/docs/hub/gguf
- model cards / structured metadata:
  https://huggingface.co/docs/hub/model-cards
