# Design note: Scientific Productization Stack (Tensor Surface + Dataset Surface + Offload Surface + Model Surface + Runtime Settings + Support Envelope)

## Goal
Define the **division of labor and consumer flow** between Rust array/tensor surfaces, dataset/storage surfaces, accelerator/offload surfaces, model/runtime surfaces, runtime activation, and support/docs claims so the ecosystem can make **scientific and ML products** reviewable without anointing one giant numerical runtime, one Python-compatibility layer, or one framework as the answer.

This is **not** a new top-level kit.
It is a stack note explaining how existing archive pieces should compose, and it now pairs with an explicit proposal-layer candidate in [`proposals/epic-scientific-productization-stack.md`](../proposals/epic-scientific-productization-stack.md): a thin `cargo science-product` / `scientific-product-pack/v0` layer above those existing surfaces.
- [`design/tensor-surface-kit.md`](./tensor-surface-kit.md)
- [`design/tensor-surface-lane-map.md`](./tensor-surface-lane-map.md)
- [`design/dataset-surface-kit.md`](./dataset-surface-kit.md)
- [`design/offload-surface-kit.md`](./offload-surface-kit.md)
- [`design/model-surface-kit.md`](./model-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/vector-surface-kit.md`](./vector-surface-kit.md)

## Why this note is needed now
Rust’s current signals are no longer saying only “scientific or ML work is possible in Rust.” They are saying the ecosystem now has enough serious ingredients that the next missing contribution is the **productization layer above them**:
- Rust’s current offload goal is explicit that the intended direction is to combine batching, autodiff, and offloading, with the longer-term hope of state-of-the-art libraries like `faer` and more libraries in other languages using Rust as their backend.
  https://rust-lang.github.io/rust-project-goals/2025h1/GPU-Offload.html
- The December 2025 project-goals update says work was spent enabling offload in CI to enable `std::offload` on nightly. That is a useful signal that backend/device truth is moving toward the language/toolchain surface rather than remaining a detached experiment.
  https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- `Burn` now presents itself as a comprehensive dynamic deep-learning framework built in Rust with flexibility, compute efficiency, and portability as primary goals.
  https://docs.rs/burn/latest/burn/
- Candle presents itself as a minimalist ML framework for Rust with a focus on performance, including GPU support, and ease of use. That means Rust users already have a serious model/tensor lane, but not yet a shared review boundary above it.
  https://github.com/huggingface/candle
- `faer` is explicit about pure-Rust linear algebra with a focus on portability, correctness, and performance. That is a materially different, lower-level numerical lane than deep-learning runtimes, and it should stay legible as such.
  https://docs.rs/faer/latest/faer/
- `zarrs` shows that Rust already has a serious multidimensional-array storage lane with Zarr V3 support and conformance claims. That means storage-backed array truth is part of the scientific story, not an afterthought.
  https://docs.rs/zarrs/latest/zarrs/
- Outside Rust, the lesson is increasingly clear: the Data APIs Consortium’s 2024 Array API revision says interoperability and consistent developer experience are the point, while DLPack exists because array/tensor systems need a stable in-memory exchange structure across frameworks and hardware. Rust should learn from that: the next worthy move is coordination and evidence above point tools, not another monolith.
  https://data-apis.org/blog/array_api_v2024_release/
  https://docs.rs/dlpackrs/latest/dlpackrs/
- Rust model deployment is already heterogeneous too: `ort` focuses on hardware-accelerated ONNX inference and training, while `tract` is deliberately tiny, portable, and self-contained for TensorFlow/ONNX inference. That is exactly the pattern where productization matters more than picking a winner.
  https://docs.rs/ort/latest/ort/
  https://docs.rs/tract-core/latest/tract_core/

Together these signals justify treating scientific/numerical productization as a **frontier-worthy ecosystem seam** rather than leaving Rust scientific work as a pile of tensor APIs, storage formats, device backends, model runtimes, and README folklore.

## Stack layers

### 1) Tensor Surface: array / matrix / tensor truth
Tensor Surface owns the **public numerical shape** of a crate or application:
- shape/dtype/layout/view posture
- ownership and mutability assumptions
- device/autodiff/interchange profiles
- adapter truth between matrix/array/tensor families
- checked numerical surface evidence

Tensor Surface answers questions like:
- “Is this really a CPU array lane, a matrix lane, or a runtime tensor lane?”
- “What layouts, views, devices, and autodiff assumptions are public?”
- “Are adapters zero-copy, copyful, partial, or watch-only?”

Design rule: **do not flatten `ndarray`, `faer`, `nalgebra`, Candle, Burn, and storage-backed tensors into one fake canonical array object**. Read the explicit lane split in [`design/tensor-surface-lane-map.md`](./tensor-surface-lane-map.md): dense-array, matrix/linalg, runtime-tensor/device, persisted-array, interchange, and adapter/import lanes must stay legible inside the wider scientific stack.

### 2) Dataset Surface: storage / table / chunk truth
Dataset Surface owns the **persisted or transport-backed data boundary**:
- dataset/table identities
- layout and chunking profiles
- engine/storage capability assumptions
- checked samples and compatibility reports
- raw-format attachments and lossiness notes

Dataset Surface answers questions like:
- “What persisted or remote data shape is expected?”
- “Which storage/layout assumptions are real?”
- “How much of the scientific workflow depends on array storage versus in-memory tensors?”

Design rule: **keep stored-array truth separate from in-memory tensor truth** even when they are frequently attached.

### 3) Offload Surface: backend / kernel / dispatch truth
Offload Surface owns the **accelerator and heterogeneous-compute boundary**:
- kernel maps and backend profiles
- buffer/transfer posture
- dispatch/fallback lanes
- launch/synchronization truth
- checked offload evidence

Offload Surface answers questions like:
- “What backend/device/runtime assumptions are public?”
- “What falls back safely to CPU and what simply is not supported?”
- “Where do kernel dispatch and device memory become part of the product surface?”

Design rule: **device/backend truth must not hide inside benchmark screenshots, feature flags, or one framework’s backend enum**.

### 4) Model Surface: model/task/runtime truth
Model Surface owns the **packaged model boundary**:
- model identity and modality/task claims
- tokenizer and artifact sets
- runtime/backend capabilities
- checked examples and model evidence
- imported runtime attachments

Model Surface answers questions like:
- “What model family is being shipped?”
- “What runtime is required or merely supported?”
- “What exactly was checked on-device, in CI, or in deployment-like environments?”

Design rule: **a model is not the same thing as a tensor runtime, dataset format, or accelerator lane**.

### 5) Runtime Settings: activation truth
Runtime Settings owns the **operational control plane** for scientific products:
- backend/device/model-path/precision/cache settings
- precedence and default rules
- secret/token/provider posture when model download or remote resources exist
- migration and rename truth
- checked activation examples

Runtime Settings answers questions like:
- “Which backend, precision, cache, or artifact source was actually activated?”
- “Which environment assumptions were merely available versus selected?”
- “What was different between local CPU runs, GPU CI, and shipped deployments?”

Design rule: **scientific product behavior should not depend on hidden environment variables and launcher scripts alone**.

### 6) Support Envelope + DocProof: supported reality
Support Envelope and DocProof own the **supportability boundary**:
- target/runtime floors
- source-build versus shipped-artifact posture
- docs/examples/notebook-like transcript truth
- feature/cfg availability posture
- release/support-facing evidence

This layer answers questions like:
- “What platforms, devices, and runtime combinations are actually supported?”
- “Do the docs and examples reflect CPU-only, GPU, and model-download reality honestly?”
- “What can release/support/atlas consumers conclude without source-diving?”

Design rule: **scientific products must not pretend one successful local run proves device/runtime/model support**.

### 7) Lower-layer imports: Vector Surface stays a substrate
Vector Surface remains important, but it should usually stay a **lower-layer optimization substrate** for this stack:
- fixed-width SIMD and scalable-vector posture,
- target-feature hazards,
- dispatch/fallback semantics,
- alignment/layout assumptions.

Scientific Productization should import vector truth where it matters without letting vector lanes silently become the default owner of tensor, dataset, model, or support truth.

### 8) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **Release / distribution** consumers can attach scientific product facts to artifacts.
- **Support / docs** consumers can explain CPU-only versus backend/device/model-dependent behavior honestly.
- **Atlas / commons** consumers can compare Rust scientific stacks without pretending one runtime is the ecosystem.
- **Agent / retrieval / service** consumers can import model/runtime/data facts when scientific components are embedded inside larger products.

Design rule: **consumers import selected evidence; they do not redefine the scientific truth models**.

## What an epic contribution should look like in practice
A worthy contribution here is not “build the Rust version of NumPy + JAX + PyTorch + Dask in one repo.”
It is a portable, reviewable stack with clear boundaries:

1. **CPU array/storage first**
   - prove tensor + dataset + runtime-settings truth on one CPU-centric scientific lane;
2. **interchange second**
   - add DLPack/adapter/import evidence so copy-vs-borrowed semantics become explicit;
3. **offload third**
   - attach backend/device/runtime profiles and fallback truth without erasing the CPU lane;
4. **model/product fourth**
   - attach model/runtime/tokenizer/artifact truth to the underlying numerical/data surfaces;
5. **support/docs/release consumers fifth**
   - show that real docs/support/release/atlas consumers can import the stack honestly.

An eventual aggregate artifact may exist, but it should be a **thin pack of referenced artifacts**, not a new mega-format that absorbs arrays, storage, devices, models, and settings into one fake canonical object. The explicit candidate is now [`proposals/epic-scientific-productization-stack.md`](../proposals/epic-scientific-productization-stack.md): `cargo science-product` / `scientific-product-pack/v0`.

## Ranked first execution lanes
1. **CPU array + storage lane**
   - best first exporter because it is the narrowest proof that Rust can connect numerical surfaces and persisted-array surfaces without immediately hiding behind GPU/runtime complexity.
2. **Array/tensor interchange lane**
   - proves copy-vs-borrowed, shape/layout/device, and adapter-lossiness truth across families.
3. **Backend/offload activation lane**
   - makes device/runtime/backend claims real instead of aspirational.
4. **Model deployment lane**
   - proves the stack can attach model/runtime/tokenizer/artifact truth without pretending the model surface owns tensors or datasets.
5. **Support/release/atlas consumer lane**
   - shows the stack matters beyond one lab benchmark or example notebook.

## Non-goals
- one universal Rust array trait as the enforced answer;
- one giant numerical runtime that hides matrix/tensor/storage/device/model differences;
- a Python-compatibility marketing page masquerading as ecosystem architecture;
- flattening array, dataset, offload, model, settings, and support truths into one “scientific readiness” score;
- pretending backend/device/model support can be inferred from feature flags or benchmark tables alone.

## Archive implications
- The archive should now treat **Tensor Surface + Dataset Surface + Offload Surface + Model Surface + Runtime Settings + Support Envelope** as a coupled **Scientific Productization Stack** in frontier discussions.
- Future revisions should prefer **explicit array/storage/backend/model/support truth, adapter lossiness notes, activation evidence, and ranked pilots** over another numerical mega-crate, fake universal array abstraction, or GPU-only brag page.
- When Agent, Data, Service, Atlas, Release, or Support work cites scientific readiness, they should import **tensor truth**, **dataset/storage truth**, **offload/backend truth**, **model/runtime truth**, **activation truth**, and **support truth** separately.

## References (signals)
- Rust offload goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/GPU-Offload.html
- December 2025 project-goals update (`std::offload` CI/nightly progress):
  https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- Burn:
  https://docs.rs/crate/burn/latest
- Candle:
  https://github.com/huggingface/candle
- faer:
  https://docs.rs/faer/latest/faer/
- zarrs:
  https://docs.rs/zarrs/latest/zarrs/
- Array API standard:
  https://data-apis.org/blog/array_api_v2024_release/
- DLPack:
  https://docs.rs/dlpackrs/latest/dlpackrs/
- ort:
  https://docs.rs/ort/latest/ort/
- tract:
  https://docs.rs/tract-core/latest/tract_core/
