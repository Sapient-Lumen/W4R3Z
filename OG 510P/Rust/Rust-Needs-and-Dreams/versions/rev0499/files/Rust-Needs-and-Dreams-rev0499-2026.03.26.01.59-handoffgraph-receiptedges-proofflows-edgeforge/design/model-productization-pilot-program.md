# Pilot program: Model Productization Stack

## Goal
Exercise the smallest set of model-facing lanes that prove the archive’s proposed **Model Productization Stack** is real and useful: model/artifact/tokenizer truth, backend/offload truth, runtime/cache/auth activation, and support/docs truth.

This pilot program should produce reusable artifacts and comparison notes.
It should not try to standardize all of model serving or inference.

## Pilot artifact families
- `model-surface/v0`
- `tokenizer-profile/v0`
- `model-artifact-set/v0`
- `runtime-capability-profile/v0`
- `model-check-plan/v0`
- `model-check-report/v0`
- `model-pack/v0`
- imported support/docs attachments from Support Envelope / DocProof

## Ranked pilot lanes

### Pilot 1: local CPU + safetensors + tokenizer truth
**Why first:**
It proves the narrowest serious lane with the least backend variance.
It is enough to show that model identity, tokenizer identity, artifact identity, and checked examples belong together.

**Candidate substrates:**
- Candle + safetensors + tokenizers
- Burn store on CPU
- tract or `ort` where tokenization and model artifacts are split explicitly

**What to export:**
- model identity and task/modality declaration;
- tokenizer profile including special-token and prompt-template notes where relevant;
- artifact set with file hashes / roles / variant notes;
- CPU runtime-capability profile;
- checked load + tokenize + one inference/report fixture.

**Success condition:**
A reviewer can tell exactly which model files, tokenizer assets, runtime lane, and checked examples are part of the supported contract.

### Pilot 2: hub-backed acquisition / cache / revision lane
**Why second:**
Rust model users increasingly fetch and cache artifacts dynamically.
That means revision pinning, cache reuse, and auth posture materially affect support truth.

**Candidate substrates:**
- `hf_hub`
- Candle integration using Hub cache
- tokenizers `from_pretrained`

**What to export:**
- remote-vs-local acquisition posture;
- pinned revision or moving-reference notes;
- cache-location and reuse posture;
- auth/token requirements if any;
- failure modes for missing or stale cache;
- checked report showing what was actually resolved.

**Success condition:**
A reviewer can distinguish “supports this model” from “might download something compatible at runtime if the cache and auth situation happen to cooperate.”

### Pilot 3: runtime-diversity lane
**Why third:**
The ecosystem already has multiple legitimate runtime families.
A serious stack has to show how one model-facing contract attaches to different runtime lanes without pretending they are interchangeable.

**Candidate substrates:**
- Burn imported ONNX → generated Rust lane
- `ort` ONNX Runtime lane
- `tract` self-contained inference lane

**What to export:**
- per-runtime capability profiles;
- operator / precision / target notes;
- unsupported-combination notes;
- comparison of what remains common versus runtime-specific.

**Success condition:**
A reviewer can see which truths belong to the model contract and which belong to one runtime family.

### Pilot 4: quantized / GGUF / backend-divergence lane
**Why fourth:**
Real model products increasingly ship format variants and quantized variants that are not behaviorally identical.
GGUF and quantized safetensors are enough to show the danger of flattening variants into one fake model package.

**Candidate substrates:**
- GGUF metadata on the Hub
- quantized safetensors variants
- CPU vs accelerator variants in Candle / Burn / `ort`

**What to export:**
- variant family and lineage;
- quantization type / precision / backend restrictions;
- memory-map vs buffer-load posture;
- support-level labels per variant.

**Success condition:**
A reviewer can tell which variants are stable, experimental, partial, or unsupported on a given target/backend.

### Pilot 5: downstream-consumer lane
**Why fifth:**
The stack matters only if other archive surfaces can import it.

**Candidate consumers:**
- Agent Productization Stack
- Scientific Productization Stack
- Service Productization Stack
- Client / Web / Polyglot lanes
- Release / Support / Atlas consumers

**What to export:**
- one support/docs consumer import;
- one service/agent/scientific import;
- one release/support import showing bundled-vs-downloaded artifact posture.

**Success condition:**
A consumer can reuse model-productization facts without re-describing tokenizer, artifact, backend, or cache truth.

## Comparison questions the pilots should answer
- Which facts are stable model-product facts versus runtime-specific facts?
- Which tokenizer assumptions are public contract versus best-effort defaults?
- Which artifact variants are equivalent, related, or incompatible?
- Which failures are acquisition/cache/auth failures versus runtime/operator/backend failures?
- Which docs/examples are checked support evidence versus illustrative teaching material?

## Early artifacts worth standardizing
- `model-surface/v0`
- `tokenizer-profile/v0`
- `model-artifact-set/v0`
- `runtime-capability-profile/v0`
- `model-check-report/v0`
- `model-pack/v0`

These are enough to prove the seam without freezing a giant schema too early.

## What this pilot program should resist
- becoming a new inference runtime;
- becoming a Hub clone or model registry;
- assuming one tokenizer file shape or one weight format is universal;
- treating backend/default/device selection as invisible plumbing;
- calling tutorial snippets “support evidence” without checked reports.

## Recommended first implementation order
1. Candle + safetensors + tokenizers CPU lane
2. `hf_hub` / cache / revision lane
3. `ort` / `tract` / Burn-import comparison lane
4. quantized / GGUF variant lane
5. downstream consumer import lane

## Expected archive follow-ons
- Promote Model Productization Stack in frontier and priority docs.
- Add model-specific amnesia resistance language.
- Make future scientific, agent, client, service, and release revisions import model-productization facts instead of re-deriving them.
