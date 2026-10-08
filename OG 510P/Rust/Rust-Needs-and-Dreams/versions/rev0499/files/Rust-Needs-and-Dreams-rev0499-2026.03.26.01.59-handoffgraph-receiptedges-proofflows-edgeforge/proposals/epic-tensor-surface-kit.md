# Epic proposal: Tensor Surface Kit

## Thesis
Rust’s numerical ecosystem is mature enough that the missing contribution is no longer “yet another ndarray competitor,” “yet another tensor runtime,” or “yet another fake universal math trait.”
The higher-leverage missing piece is a **portable tensor-surface contract** that lets teams declare, diff, validate, and ship what an array/matrix/tensor boundary actually promises: shape/dtype truth, layout/view posture, ownership semantics, device/autodiff assumptions, interchange/storage lanes, and checked adapter evidence.

In other words: Rust needs a boring, attachable `tensor-pack/v0` more than it needs one more runtime trying to become the whole story. Read [`design/tensor-surface-lane-map.md`](../design/tensor-surface-lane-map.md) as the explicit rule for what must stay separate.

## Why now
The ecosystem signals line up:
- `ndarray` is a serious general n-dimensional array lane with explicit views and raw-storage vocabulary.
- `nalgebra` remains a major statically/dynamically sized linear algebra lane with clear storage semantics.
- `faer` is a high-performance matrix vocabulary with owned and borrowed matrix types.
- Candle and Burn show that Rust tensor work is now a real runtime/device/backprop ecosystem rather than a novelty.
- `argmin-math` already has to bridge multiple numerical families instead of assuming one winner.
- DLPack exists precisely because tensor interchange matters across runtimes and hardware backends.
- Zarr and model/tensor stores show that persistence and interchange are part of the real surface, not an afterthought.

That means the missing substrate is not raw capability.
It is the **reviewable tensor boundary above today’s pieces**.

Sources:
- https://docs.rs/ndarray/latest/ndarray/struct.ArrayBase.html
- https://docs.rs/ndarray/latest/ndarray/type.ArrayView.html
- https://www.nalgebra.rs/docs/user_guide/vectors_and_matrices/
- https://docs.rs/faer/latest/faer/
- https://docs.rs/candle-core/latest/candle_core/struct.Tensor.html
- https://docs.rs/burn/latest/burn/tensor/index.html
- https://docs.rs/burn-store
- https://docs.rs/argmin-math/
- https://dmlc.github.io/dlpack/latest/
- https://docs.rs/dlpark/latest/dlpark/versioned/index.html
- https://docs.rs/zarrs/latest/zarrs/

## What should be built
A first credible version should ship:
0. a lane catalog that distinguishes **dense-array, matrix/linalg, runtime-tensor/device, persisted-array, interchange/attachment, and adapter/consumer-import** lanes before any finer-grained profiles are attached
1. `tensor-surface/v0`, `shape-dtype-profile/v0`, `layout-view-profile/v0`, `ownership-mutability-profile/v0`, optional `device-autodiff-profile/v0`, `tensor-interchange-profile/v0`, optional `tensor-adapter-profile/v0`, `tensor-check-plan/v0`, `tensor-check-report/v0`, optional `tensor-diff-report/v0`, and `tensor-pack/v0`
2. adapters for common Rust numerical families (`ndarray`, `nalgebra`, `faer`, Candle, Burn) plus interchange/storage attachment lanes (DLPack, Zarr, model-store formats, Arrow attachments where relevant)
3. docs/reference generation for declared tensor surfaces, supported dtypes/layouts/devices, and checked adapter evidence
4. validation/reporting support for shape/layout drift, copy-required vs borrowed adaptation, device/backprop support narrowing, and storage/interchange fidelity
5. examples showing tensor packs attached to scientific libraries, optimization crates, ML runtimes, accelerator consumers, and data/storage workflows

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one `ndarray` / `nalgebra` / `faer` pilot that proves exact vs copy-required vs unsupported conversions belong in first-class adapter reports
- one Candle / Burn pilot that publishes device/autodiff/runtime posture without pretending runtime names tell the whole story
- one DLPack / Zarr / store-fidelity pilot that turns zero-copy and persistence claims into checked artifacts
- one downstream importer showing Model Surface or Offload Surface can consume tensor packs rather than rebuilding tensor truth from scratch

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve shape/dtype, layout/view, ownership, device/autodiff, and interchange truth as separate artifacts
2. **v0.2 adapters**
   - support `ndarray`, `nalgebra`, `faer`, Candle, Burn, DLPack, Zarr, and adjacent store/attachment lanes
   - support honest copy-required / lossy / unsupported outcomes rather than pretending every adapter is zero-copy
3. **v0.3 cross-kit integration**
   - integrate with Model Surface, Offload Surface, Dataset Surface, Geospatial Surface, Support Envelope, Perf, and Footprint workflows
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact runtime/library choice

## Success metrics
- Teams can review array/tensor boundary changes as explicit artifacts instead of type aliases, README prose, and scattered examples.
- Library-family differences become easier to reason about because layout/view/device assumptions are explicit.
- Zero-copy and adapter-fidelity claims become easier to trust because copy-required and lossy cases are first-class outcomes.
- ML/scientific/data/offload workflows become easier to connect because tensor truth survives beyond one runtime choice.
- Rust numerical ecosystems become easier to hand off across teams because the support surface is no longer implicit.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Dataset Surface Kit covers tabular dataset/table contracts,
- Model Surface Kit covers task/tokenizer/artifact/runtime packaging,
- Offload Surface Kit covers kernels, transfers, and backend execution posture,
- Geospatial Surface Kit covers geometry/CRS/runtime truth,
- and Support Envelope / Footprint / Perf kits cover environment and cost assumptions.

But none of those is the portable contract for the **array/matrix/tensor boundary itself**.
Tensor Surface Kit is the missing substrate that keeps shape, dtype, layout, ownership, device, interchange, and checked adapter evidence attached to one reviewable numerical interface without absorbing the rest of the stack into one mega-format.
