# Gap: model products, artifacts, tokenizers, runtimes, and support contracts

## Why this gap matters
Rust’s model ecosystem has passed the point where the main question is “can Rust run ML models?”
The real question is now **what exactly a Rust model product is promising**.

Today, serious Rust model work is spread across multiple legitimate families:
- native Rust model/runtime lanes like Candle;
- multi-backend training/inference frameworks like Burn;
- ONNX Runtime attachment via `ort`;
- self-contained inference via `tract`;
- tokenizer pipelines via `tokenizers`;
- hub/cache acquisition via `hf_hub`;
- artifact formats like safetensors, ONNX, GGUF, and Burn’s own evolving storage/import lanes.

That is a healthy ecosystem pattern, but it leaves an underbuilt seam:
**artifact/tokenizer/runtime/backend/cache/support truth still tends to live in builder code, env vars, README prose, and per-runtime examples**.

## What is currently missing
The ecosystem still lacks one boring portable layer that can say, in reviewable form:
- which model is actually being shipped;
- which tokenizer and prompt-template assumptions belong to it;
- which artifact variants are first-class;
- which runtime families and backends are supported;
- which cache/auth/revision assumptions materially change behavior;
- which examples and docs are actually checked;
- and what support teams can safely promise.

## Why existing pieces are not enough by themselves
- Candle is already a real native Rust lane, but a Candle implementation does not by itself answer what support claims survive format changes, hub-resolution changes, or backend divergence.
- Burn is already serious about storage/import/backend portability, but that does not automatically become a stable review surface for consumers of a shipped model product.
- `ort` and `tract` are both real deployment lanes, but choosing one does not explain tokenizer truth, artifact lineage, quantization equivalence, or cache/auth posture.
- Hub metadata is increasingly structured, but it is still not the same thing as runtime/backends/support evidence inside a Rust product.

## Worthy contribution shape
A worthy contribution here is **not** another model runner, another file converter, another hub-downloader CLI, or another “serve any model” control plane.
It is a **Model Productization Stack**:
- **Model Surface** for identity / tokenizer / artifacts / examples / checks;
- **Offload Surface** for device / backend / precision / quantization posture;
- **Runtime Settings** for source / revision / cache / auth / backend activation;
- **Support Envelope + DocProof** for public support truth and checked docs.

## Strong first execution lanes
1. local CPU + safetensors + tokenizer truth;
2. hub-backed acquisition/cache/revision truth;
3. runtime-diversity comparison (`ort` / `tract` / Burn import / Candle-native);
4. quantized / GGUF variant truth;
5. downstream consumer imports into service / agent / scientific / client / release/support lanes.

## What to avoid
- flattening safetensors, GGUF, ONNX, and generated-Rust variants into one fake canonical model file;
- pretending tokenizer behavior is an implementation detail instead of part of the public contract;
- claiming backend support based only on compile success or one benchmark chart;
- hiding hub/cache/auth/revision posture in environment variables and tutorial text;
- treating model-card metadata as if it already proves real Rust runtime support.

## Suggested archive consequence
Promote an explicit **Model Productization Stack** so future revisions can stop re-solving model shipment and inference support as framework-local glue.
