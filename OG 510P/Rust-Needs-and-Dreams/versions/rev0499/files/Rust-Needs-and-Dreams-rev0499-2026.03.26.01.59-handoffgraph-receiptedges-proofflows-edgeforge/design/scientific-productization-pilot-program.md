# Design: Scientific Productization Pilot Program (CPU Array/Storage Truth → Interchange Proofs → Backend Activation → Model Attachments → Consumer Imports)

## Goal
Turn the **Scientific Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve Rust’s scientific and ML product story? This pilot program now acts as the execution path for [`proposals/epic-scientific-productization-stack.md`](../proposals/epic-scientific-productization-stack.md).

The pilot program should not chase a universal scientific platform. It should sequence the contribution so each lane proves something concrete before the next lane widens scope.

## Why a pilot program is necessary
Scientific/numerical work is one of the easiest places for good ideas to dissolve into giant abstractions, benchmark theater, or “just use Python” defensiveness.

Rust already has serious ingredients, but they come from different source-of-truth families and different failure modes:
- array/matrix/tensor APIs,
- persisted dataset/storage formats,
- accelerator/backend selection and fallback behavior,
- model/runtime/tokenizer artifacts,
- runtime settings and caches,
- docs/support claims.

A credible plan therefore needs to decide:
- when CPU-only array/storage evidence is already enough,
- when adapter and interchange truth must be attached,
- when backend/device activation becomes part of the contract,
- when model/runtime artifacts become a public support surface,
- and which downstream consumers justify graduation.

## Principles
1. **Start where the evidence gap is painful and common**
   - CPU array + persisted-storage truth is a more portable first win than a grand unified GPU or training platform.
2. **Respect multiple source-of-truth families**
   - `ndarray`/`faer`/Candle/Burn tensor truth, Zarr or table/dataset truth, DLPack interchange truth, and model/runtime truth all matter, but they are not the same thing. Inside Tensor Surface, the lane map now also distinguishes dense-array, matrix/linalg, runtime-tensor/device, persisted-array, interchange, and adapter/import lanes before Scientific Productization composes them.
3. **Keep copy-vs-borrowed behavior explicit**
   - adapter convenience is not a substitute for ownership/layout/device truth.
4. **Do not make GPU the entry price**
   - backend/offload evidence matters, but CPU-first lanes should still graduate cleanly.
5. **Settings are part of the product story**
   - backend/device/precision/model-path/cache activation changes what was actually tested or shipped.
6. **Consumers import; they do not redefine**
   - release, support, atlas, service, and agent tooling should import the scientific stack rather than reinterpret it from scratch.

## Common artifacts this program should drive
- `science-lane-brief/v0` — declare which scientific lane is being exercised, scope, crates/runtimes involved, and explicit non-goals.
- `scientific-import-profile/v0` — rules for importing tensor/dataset/offload/model/settings/support artifacts into one pilot without pretending they are one native truth.
- `array-storage-handoff/v0` — bounded description of how persisted arrays/datasets map into in-memory surfaces, including copy/lossiness notes.
- `backend-activation-brief/v0` — which backend/device/runtime/precision/cache settings were actually activated in a pilot.
- `science-consumer-handoff/v0` — how docs/release/support/atlas/embedded-service consumers may use a pilot result and what they must not conclude.
- `science-readiness-scorecard/v0` — not a fake maturity number; a lane-by-lane checklist showing which truths exist and which remain absent.
- `science-product-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

Reference command family: `cargo science-product` with `scientific-product-pack/v0` as the explicit proposal-layer bundle.

## Ranked pilot lanes

### 1) CPU array + storage lane
**Why first:** it proves the narrowest useful scientific claim without hiding behind GPU/runtime glamour.

**Concrete scope**
- array/matrix/tensor surface declaration for a CPU-centric lane,
- persisted-array or dataset attachment (for example Zarr-backed or table-backed input),
- layout/view/ownership posture,
- runtime-settings notes for file paths, caches, and feature flags,
- docs/support examples that state CPU-only posture honestly.

**Graduation bar**
- the pack can explain what array/storage truth was declared, what was actually checked, whether imports were copyful or borrowed, and what CPU/runtime assumptions held.

**What success looks like**
- a `faer`/`ndarray`/storage-adjacent proof that is useful even without any model runtime or GPU lane attached.

### 2) Interchange / adapter lane
**Why second:** the scientific ecosystem gets confusing exactly where data crosses family boundaries.

**Concrete scope**
- DLPack or equivalent adapter identity,
- copy-vs-borrowed behavior,
- shape/dtype/layout/device transfer notes,
- explicit partial or lossy conversions,
- comparison notes across at least two numerical families.

**Graduation bar**
- the pack can show when an adapter preserved semantics, when it copied, and what remained unsupported or watch-only.

### 3) Backend / offload activation lane
**Why third:** this is where scientific product claims often become hand-wavy unless runtime activation is explicit.

**Concrete scope**
- backend/device/runtime profile,
- kernel/dispatch/fallback posture,
- precision/autodiff/backend settings,
- CPU fallback or refusal reasons,
- checked offload evidence and caveats.

**Graduation bar**
- a reviewer can tell which backend/device path actually ran, which fallback path exists, and what support claims remain partial.

### 4) Model attachment / deployment lane
**Why fourth:** once the numerical substrate is honest, attach models without letting them erase lower-layer truth.

**Concrete scope**
- model/task/artifact/tokenizer declaration,
- attached tensor/runtime/backend requirements,
- inference/runtime comparison notes (for example portable runtime versus hardware-accelerated runtime),
- source-build vs packaged-artifact posture,
- support/docs notes for loading, caching, and runtime activation.

**Graduation bar**
- the pack can explain which model surface was shipped, which runtime(s) were checked, and what underlying tensor/backend assumptions matter.

### 5) Support / release / atlas consumer lane
**Why fifth:** this is where the stack proves it can matter beyond local experiments and lab notes.

**Concrete scope**
- release attachments,
- support-envelope claims tied to real scientific artifacts,
- docs/transcript imports,
- atlas or comparison views,
- optional service/agent/data consumer handoffs for embedded scientific components.

**Graduation bar**
- the stack can answer boring real-world questions like CPU-only versus GPU support, model/runtime prerequisites, storage assumptions, and adapter caveats without bespoke maintainer memory.

## What to defer
- a mega-framework that tries to own arrays, tensors, storage, models, and accelerators in one API;
- a fake universal array trait or one-true backend story;
- policy-first hard gates before the evidence lanes exist;
- “Rust notebook platform” dreams that obscure support and runtime truth;
- broad GPU/training claims without explicit backend activation artifacts.

## Immediate archive consequences
- Treat **Tensor Surface**, **Dataset Surface**, **Offload Surface**, **Model Surface**, **Runtime Settings**, and **Support Envelope** as one coupled frontier seam in later ranking discussions.
- Keep **Vector Surface** as an imported optimization substrate rather than promoting it to the default owner of scientific-product truth.
- Add a specific amnesia resistor so later revisions cannot collapse dataset/storage truth, array/tensor truth, backend/device truth, model/runtime truth, activation truth, and support claims into one note.

## Read this together with
- `design/scientific-productization-stack.md`
- `design/tensor-surface-kit.md`
- `design/dataset-surface-kit.md`
- `design/offload-surface-kit.md`
- `design/model-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
