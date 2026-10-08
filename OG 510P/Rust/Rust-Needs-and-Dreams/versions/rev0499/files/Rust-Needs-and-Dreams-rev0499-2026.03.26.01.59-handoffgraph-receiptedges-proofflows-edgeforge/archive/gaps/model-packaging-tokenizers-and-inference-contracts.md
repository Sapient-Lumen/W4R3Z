# Gap: model packaging, tokenizers, and inference contracts

## What is missing
Rust has credible machine-learning runtimes, artifact formats, and hub clients, but it still lacks a **shared model-surface contract**.

Today there is no standard Rust way to describe, exchange, diff, and review:
- which model artifact set a program officially supports,
- which tokenizer pipeline and special-token behavior belong to those weights,
- which task or inference surface is being claimed (generation, embeddings, classification, vision, speech, multimodal, etc.),
- which input/output shapes, dtypes, modalities, or preprocessing/postprocessing rules are part of the support promise,
- which runtime lanes are supported for a given model surface (Candle-native, Burn-native, ONNX via `ort`, ONNX/NNEF via `tract`, GGUF-oriented runtimes, etc.),
- which artifact formats are attached or expected (`.safetensors`, `.onnx`, `.gguf`, BurnPack, tokenizer JSON, model-card metadata, adapters/LoRAs, quantized variants),
- which hardware, precision, quantization, and memory assumptions were actually checked,
- and what evidence exists that the declared model surface still matches the shipped Rust application or crate.

That missing layer matters because Rust already has real point solutions. Candle supports CPU, CUDA, and WASM/browser use and can load safetensors into CPU/GPU memory; Burn supports training and inference across backends and can import ONNX into generated Rust plus BurnPack weights; `tract` reads ONNX or NNEF and runs inference; `ort` exposes ONNX Runtime from Rust; `tokenizers` provides a real tokenization pipeline in Rust; `hf-hub` mirrors the Hub cache model; Hugging Face model cards and model metadata already encode things like task, datasets, license, and library; safetensors and GGUF both have inspectable metadata surfaces. What Rust still lacks is a portable review layer above those pieces.

Sources:
- https://huggingface.github.io/candle/
- https://docs.rs/candle-core/latest/candle_core/safetensors/
- https://burn.dev/
- https://burn.dev/blog/release-0.19.0/
- https://docs.rs/burn-import/latest/burn_import/onnx/struct.ModelGen.html
- https://github.com/sonos/tract
- https://docs.rs/ort/latest/ort/
- https://docs.rs/tokenizers/latest/tokenizers/
- https://docs.rs/tokenizers/latest/tokenizers/tokenizer/
- https://docs.rs/hf-hub/latest/hf_hub/
- https://huggingface.co/docs/safetensors/index
- https://huggingface.co/docs/safetensors/metadata_parsing
- https://huggingface.co/docs/hub/model-cards
- https://huggingface.co/docs/hub/gguf
- https://huggingface.co/blog/ngxson/common-ai-model-formats

## The current seam is awkward
The ecosystem clearly has ingredients:
- Candle is a serious Rust-native ML lane with CPU, CUDA, distributed, and WASM support,
- Burn is a serious Rust-native tensor/training/inference lane with multiple backends and an ONNX import path that emits Rust code plus BurnPack weights,
- `tract` is a tiny self-contained inference toolkit that reads ONNX or NNEF,
- `ort` is a Rust binding for ONNX Runtime,
- safetensors gives a safe zero-copy tensor format and lightweight metadata inspection,
- GGUF has become a visible model-distribution lane with inspectable metadata on the Hub,
- `tokenizers` models tokenization as a composed Rust pipeline,
- `hf-hub` keeps Rust clients compatible with the Hub cache model,
- and model cards already carry structured metadata such as task (`pipeline_tag`), datasets, library name, license, and evaluation results.

But real Rust deployments still hand-assemble their support story out of:
- one runtime-specific loader,
- one weight format,
- one tokenizer file or ad hoc tokenizer choice,
- README prose about task and expected prompts,
- hub metadata that may or may not match the runtime packaging,
- benchmark notes for one machine,
- and scattered examples that do not say what combinations were actually checked.

The result is not that Rust lacks model runtimes.
The result is that there is no portable way to say:
- “these weights, tokenizer files, adapters, and task tags belong together,”
- “these runtimes/backends and precisions are officially supported,”
- “these input/output assumptions are part of the support promise,”
- “these quantized or alternative-format variants are equivalent enough for this surface,”
- or “these combinations were actually checked on these targets.”

Model cards help with discovery, safetensors/GGUF help with metadata inspection, and runtime crates help with execution, but none of those alone is the whole Rust-side support boundary for shipping models inside applications, crates, CLIs, services, or edge binaries. That is the archive pattern worth elevating: strong parts, weak shared boundary.

Sources:
- https://huggingface.github.io/candle/
- https://docs.rs/candle-core/latest/candle_core/safetensors/
- https://burn.dev/
- https://burn.dev/blog/release-0.19.0/
- https://docs.rs/burn-import/latest/burn_import/onnx/struct.ModelGen.html
- https://github.com/sonos/tract
- https://docs.rs/ort/latest/ort/
- https://docs.rs/tokenizers/latest/tokenizers/tokenizer/
- https://docs.rs/hf-hub/latest/hf_hub/
- https://huggingface.co/docs/hub/model-cards
- https://huggingface.co/docs/hub/gguf
- https://huggingface.co/blog/ngxson/common-ai-model-formats

## Why this matters
This gap is bigger than “better ML docs.”
It affects:
1. **application packaging** — apps need one reviewable statement of which weights/tokenizer/runtime combinations they support rather than a pile of ad hoc loaders and notes;
2. **deployment reliability** — tokenizer mismatch, task-tag drift, quantization mismatch, and backend-specific ops gaps are real compatibility failures, not cosmetic metadata issues;
3. **cross-runtime portability** — teams should be able to preserve one declared model surface while experimenting with Candle-native, Burn-native, ONNX Runtime, tract, or future runtimes;
4. **resource and platform review** — model support claims depend on precision, memory footprint, GPU/CPU expectations, and target/runtime assumptions that should attach cleanly to Footprint Kit and Support Envelope Kit rather than being buried in blog posts;
5. **supply-chain and licensing review** — model cards already expose license, dataset, and evaluation metadata, but Rust tools do not yet attach that cleanly to shipped model-support claims;
6. **service and CLI composition** — Service Surface Kit, Event Surface Kit, Runtime Settings Kit, Command Surface Kit, and Identity Surface Kit all benefit from a model boundary without owning it.

The Hugging Face Hub already treats model metadata, task tags, evaluation results, and file-format inspection as first-class concerns, which is a strong signal that “what this model artifact set claims to be” is not incidental. Rust is missing the adapter layer that makes those claims portable, reviewable, and checkable inside Rust-native products.

Sources:
- https://huggingface.co/docs/hub/model-cards
- https://huggingface.co/docs/hub/gguf
- https://huggingface.co/docs/safetensors/metadata_parsing
- https://docs.rs/tokenizers/latest/tokenizers/tokenizer/
- https://docs.rs/hf-hub/latest/hf_hub/

## What “good” looks like
A worthy contribution here is **not** another tensor engine, another ONNX runtime wrapper, another hub mirror, another tokenizer implementation, or another model-serving framework.

It is a shared model-surface boundary:
- one `model-surface/v0` describing model identity, intended tasks, modalities, supported runtimes, supported artifact variants, support levels, and links to attached raw artifacts,
- one `tokenizer-profile/v0` describing tokenizer assets, normalization/pre-tokenization/postprocessing behavior, special tokens, truncation/padding assumptions, and compatibility with the declared model surface,
- one `model-artifact-set/v0` describing weights, adapters, quantized variants, config files, model-card metadata, tokenizer files, and provenance pointers without flattening their raw source truth,
- one `runtime-capability-profile/v0` describing backend/runtime kind, precision support, quantization support, device assumptions, memory notes, and unsupported operators/features,
- one `model-example-catalog/v0` containing canonical prompts/examples, expected outputs or tolerances, negative cases, tokenizer-boundary cases, and illustrative-vs-checked labels,
- one `model-check-plan/v0` describing which runtimes, formats, targets, precisions, and fixtures were exercised,
- one `model-check-report/v0` recording compatibility findings, tokenizer drift, shape/dtype mismatches, missing-op/runtime failures, and raw attachment pointers,
- one optional `model-diff-report/v0` for declared-surface changes across versions or artifact variants,
- and one `model-pack/v0` bundle for CI, release review, registry publication, service packaging, and later archaeology.

That would let Rust teams treat model support as a reviewable product surface instead of a pile of files and examples.
