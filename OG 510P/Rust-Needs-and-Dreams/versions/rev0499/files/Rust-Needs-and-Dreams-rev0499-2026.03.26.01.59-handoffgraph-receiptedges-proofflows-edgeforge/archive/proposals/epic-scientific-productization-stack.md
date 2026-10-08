# Epic proposal: Scientific Productization Stack (`cargo science-product`, `scientific-product-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **scientific and ML products** that links **array/tensor truth**, **dataset/storage truth**, **backend/device truth**, **model/runtime attachments**, **runtime activation**, and **support/docs truth** into one portable review boundary without pretending one numerical runtime, one backend, or one model stack has already won.

## Why this is now worth doing
Rust’s scientific ecosystem is now strong enough that the missing contribution looks like a **product boundary above the ingredients** rather than another ingredient:
- Rust’s current offload work is explicitly aimed at combining batching, autodiff, and offloading, with the stated hope of state-of-the-art libraries like `faer` and more libraries in other languages using Rust as their backend.
  https://rust-lang.github.io/rust-project-goals/2025h1/GPU-Offload.html
- The December 2025 project-goals update says work was spent enabling offload in CI to enable `std::offload` on nightly. That means backend/device truth is moving closer to the language/toolchain surface, not staying a niche experiment.
  https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- The current scientific ingredients are clearly real but clearly non-equivalent. `faer` focuses on high-performance linear algebra for medium/large matrices; `zarrs` focuses on multidimensional-array storage and metadata; Apache Arrow is a native Rust cross-language in-memory data platform; Polars builds a Rust dataframe lane on Arrow’s memory model; and `object_store` explicitly provides a uniform object-storage API that lets the same binary run across multiple clouds and local environments.
  https://docs.rs/faer/latest/faer/
  https://docs.rs/zarrs/latest/zarrs/
  https://docs.rs/arrow/latest/arrow/
  https://docs.pola.rs/api/rust/dev/polars/
  https://docs.rs/object_store/latest/object_store/
- The model/runtime lanes are also substantial and plural. Burn presents itself as a comprehensive dynamic deep-learning framework built in Rust with flexibility, compute efficiency, and portability goals; Candle presents itself as a minimalist ML framework with performance and GPU support; `ort` is a Rust binding for ONNX Runtime; and `tract` is explicitly tiny, self-contained, and portable for TensorFlow/ONNX inference.
  https://docs.rs/burn/latest/burn/
  https://github.com/huggingface/candle
  https://docs.rs/ort/latest/ort/
  https://docs.rs/tract-core/latest/tract_core/
- Interchange prior art is also now strong enough to stop pretending every ecosystem needs a single winning runtime. DLPack is an in-memory interchange format recognized by major deep-learning and array-processing frameworks, and the 2024 Array API revision explicitly frames interoperability and consistent semantics as the point.
  https://docs.rs/dlpackrs/latest/dlpackrs/
  https://data-apis.org/blog/array_api_v2024_release/
- `hf_hub` further shows that model acquisition/cache identity is already a practical Rust runtime concern, because it aims to stay cache-compatible with the Python `huggingface_hub` package rather than inventing a disconnected artifact world.
  https://docs.rs/hf-hub/latest/hf_hub/

What is still missing is the **stack-level boundary that says one scientific product subject was reviewed with these numerical surfaces, these storage assumptions, these backend/device paths, these model/runtime attachments, these activated settings, these support caveats, and these bounded consumer handoffs**.

## Working name
- CLI: `cargo science-product`
- primary artifact: `scientific-product-pack/v0`

## Scope
### This epic should own
- scientific-product subject identity
- imported tensor / dataset / offload / model / runtime-settings / support attachments
- diffable review points across layout, storage, backend/device, model/runtime, activation, and support claims
- bounded release / support / atlas / service / agent / assistant handoffs
- verification of pack integrity and import references

### This epic should not own
- a universal Rust NumPy/JAX/PyTorch replacement
- a hosted model-serving or notebook control plane
- one giant array trait that silently absorbs matrices, tensors, dataframes, and storage
- a benchmark dashboard masquerading as support truth
- picking one backend/runtime as the ecosystem winner
- a one-number “scientific ready” badge

## Candidate artifact family
### `scientific-product-brief/v0`
Why the product exists, intended consumer set, scientific lanes in scope, supported environments, freshness budget, and review status.

### `scientific-product-subject/v0`
The exact crate/binary/release/deployment subject, imported tensor/dataset/offload/model surfaces, comparison base, and environment/support scope.

### `scientific-product-pack/v0`
The portable review bundle linking:
- imported `tensor-surface` / `dataset-surface` / `offload-surface` / `model-surface` attachments
- imported runtime-settings / cache / auth / precision / backend activation attachments
- imported array-storage handoff and interchange notes
- imported support/docs/platform and optional release handoffs
- local notes, waivers, caveats, and integrity metadata

### `scientific-product-diff/v0`
What changed between two review points, with separate sections for:
- array/tensor shape/layout/device/autodiff posture
- dataset/storage/layout/catalog assumptions
- backend/device/runtime/fallback posture
- model/task/tokenizer/artifact/runtime attachments
- activation settings and cache/auth differences
- support/docs/platform claims
- migration requirements and operator/user actions

### `scientific-product-handoff/v0`
Bounded consumer summaries for:
- release review
- support/docs review
- atlas/adoption review
- service/data/agent import consumers
- assistant/editor rendering

## Recommended rollout
1. CPU array + storage lane
2. interchange / adapter lane
3. backend / offload activation lane
4. model attachment lane
5. support / release / atlas / embedded-consumer lane

This should be driven by [`design/scientific-productization-pilot-program.md`](../design/scientific-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a nicer tensor runtime,
- a nicer Zarr or Arrow adapter,
- a nicer GPU wrapper,
- a nicer model downloader,
- or a nicer benchmarking or notebook helper.

An epic contribution here instead gives Rust one **portable scientific-product contract** above those lanes.
That is strategically different because it can:
- make release/support/atlas/service/agent reviews share the same subject and evidence boundary;
- let arrays, datasets, backends, and model runtimes stay specialized without pretending any one defines the whole product;
- keep array/tensor truth, dataset/storage truth, backend/device truth, model/runtime truth, activation truth, and support/docs truth distinct but linked;
- and give downstream tooling a bounded artifact to import instead of re-scraping examples, cargo features, GPU notes, hub-cache setup, and issue threads.

## Design principles
- **Array truth is not dataset truth.**
- **Backend/device truth is not model truth.**
- **Interchange prior art does not mean ecosystem convergence.**
- **Activation settings materially change what was actually tested or shipped.**
- **Support/docs caveats are part of the product boundary.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact scientific product subject,”
- “these are the numerical and storage surfaces we actually support,”
- “these are the backend/device/runtime paths that were actually checked,”
- “these are the model/runtime attachments and acquisition/cache assumptions,”
- “these are the settings that materially changed behavior,”
- “these are the docs/support/platform caveats,”
- “this is what changed from the prior review,”
- and “this is what release/support/atlas/service/agent consumers may safely conclude,”

without inventing a bespoke “ML/science readiness” schema for every repository.

## Read this with
- `design/scientific-productization-stack.md`
- `design/scientific-productization-pilot-program.md`
- `design/tensor-surface-kit.md`
- `design/dataset-surface-kit.md`
- `design/offload-surface-kit.md`
- `design/model-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
