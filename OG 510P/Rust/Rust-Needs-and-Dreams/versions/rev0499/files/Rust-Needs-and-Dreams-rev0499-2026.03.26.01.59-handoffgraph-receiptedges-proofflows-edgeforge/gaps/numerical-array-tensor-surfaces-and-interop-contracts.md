# Gap: Numerical array/tensor surfaces and interop contracts

## What is missing
## Newly explicit problem: Rust numerical work still lacks a lane map
The archive already knew the ecosystem had good pieces, but it was still under-modeling one key thing: **not all numerical surfaces are the same lane**. Dense arrays, matrix vocabularies, runtime tensors, persisted multidimensional arrays, interchange structures, and adapter/import consumers all carry different support truths.

That is why this gap now pairs with [`design/tensor-surface-lane-map.md`](../design/tensor-surface-lane-map.md): the missing contribution is not just more schemas, but a discipline that keeps those lanes separate while still letting them compose.

Rust now has serious building blocks for numerical arrays, matrices, tensors, and multidimensional storage, but it still lacks a **boring, end-to-end contract workflow** for those surfaces.

Today teams can separately:
- model n-dimensional arrays and views with `ndarray`,
- work with statically and dynamically sized matrices in `nalgebra`,
- use `faer` for high-performance matrix work with `Mat` / `MatRef` / `MatMut`,
- run tensor workloads on device-aware backends with Candle and Burn,
- exchange tensors through DLPack-compatible lanes,
- and persist multidimensional arrays through formats like Zarr or model-oriented tensor stores.

What is still missing is the shared layer that answers:
- what array/matrix/tensor surface a project is officially claiming to support,
- which shape, dtype, layout, view, and ownership facts matter for that claim,
- which device/backend/autodiff assumptions are part of the supported surface,
- which interchange/storage lanes are zero-copy, copy-required, lossy, or unsupported,
- and what evidence actually justifies those claims over time.

## Why it matters
This is not just an ML-framework problem.

Array and tensor surfaces are increasingly **interfaces**:
- scientific and numerical libraries exchange matrix/array values across crate boundaries;
- ML systems move tensors among training, inference, serialization, and accelerator backends;
- geospatial, imaging, and simulation code increasingly treat multidimensional arrays as durable boundary objects;
- and storage/interchange formats like DLPack and Zarr mean the interesting question is often not “can Rust represent this?” but “what exactly is being promised, copied, borrowed, or adapted?”

Rust’s numerical ecosystem is no longer one lane.
It is now a set of partially overlapping array, matrix, tensor, storage, and device ecosystems.
That raises the value of a shared review/evidence layer above them.

## Existing building blocks worth composing
- `ndarray` centers a general n-dimensional `ArrayBase` model, explicitly distinguishes owned arrays and views, and exposes low-level storage/layout vocabulary through traits such as `RawData`.
  https://docs.rs/ndarray/latest/ndarray/struct.ArrayBase.html
  https://docs.rs/ndarray/latest/ndarray/type.ArrayView.html
  https://docs.rs/ndarray/latest/ndarray/trait.RawData.html
- `nalgebra` explicitly distinguishes statically and dynamically sized matrices and uses column-major storage for its matrix family.
  https://www.nalgebra.rs/docs/user_guide/vectors_and_matrices/
  https://docs.rs/nalgebra/latest/nalgebra/base/type.Matrix3.html
- `faer` already presents a serious high-performance matrix lane with owned and borrowed matrix vocabulary types (`Mat`, `MatRef`, `MatMut`).
  https://docs.rs/faer/latest/faer/
  https://docs.rs/faer/latest/faer/mat/index.html
- Candle’s core tensor lane already exposes `Tensor`, `Shape`, `Layout`, and `Device` as first-class concepts.
  https://docs.rs/candle-core/latest/candle_core/struct.Tensor.html
  https://docs.rs/candle-core/latest/candle_core/shape/index.html
  https://docs.rs/candle-core/latest/candle_core/layout/index.html
- Burn already treats backend, device, tensor metadata, autodiff, and model/tensor storage as real surface areas; Burn Store explicitly calls out cross-framework interoperability plus SafeTensors/PyTorch lanes.
  https://docs.rs/burn/latest/burn/tensor/index.html
  https://docs.rs/burn/latest/x86_64-pc-windows-msvc/burn/tensor/backend/index.html
  https://docs.rs/burn-store
- `argmin-math` is especially good prior art because it already supports abstractions over `Vec`, `ndarray`, `nalgebra`, and `faer` instead of assuming one numerical type family wins.
  https://docs.rs/argmin-math/
- DLPack explicitly exists as a stable in-memory tensor exchange structure across hardware backends, and Rust already has `dlpark` as a safe versioned wrapper / trait layer.
  https://dmlc.github.io/dlpack/latest/
  https://dmlc.github.io/dlpack/latest/c_api.html
  https://docs.rs/dlpark/latest/dlpark/versioned/index.html
  https://docs.rs/dlpark/latest/dlpark/traits/index.html
- `zarrs` already exposes a serious Rust lane for multidimensional array storage and metadata, including Zarr V3 support and metadata validation.
  https://docs.rs/zarrs/latest/zarrs/
  https://docs.rs/zarrs/latest/zarrs/array/struct.Array.html
- Apache Arrow remains extremely relevant as an adjacent structured-data lane, but its own docs emphasize a language-agnostic columnar format for table-like data; that is useful boundary evidence for why dataset/table truth should stay adjacent to, not inside, tensor-surface truth.
  https://arrow.apache.org/docs/format/Columnar.html
  https://docs.rs/arrow-array/latest/arrow_array/struct.RecordBatch.html

## Why existing tools are not yet the whole answer
The ecosystem has **real execution and representation tools**, but not the **shared contract / adapter / evidence layer**:
- `ndarray` gives a flexible dense n-D array model.
- `nalgebra` gives statically and dynamically sized linear algebra surfaces.
- `faer` gives a high-performance matrix vocabulary.
- Candle and Burn give device-aware tensor runtimes.
- DLPack gives a cross-framework exchange structure.
- Zarr and tensor-storage crates give persistence lanes.

But teams still have to invent their own answers for:
- stable tensor/array identities beyond ad hoc type names,
- normalized shape/dtype/layout/view declarations,
- explicit device/autodiff/support claims,
- honest adapter-lossiness reports,
- and diffable review artifacts for array/tensor surface drift.

This is the same archive pattern seen elsewhere: strong point tools, weak shared artifacts.

## Target outcome
A project should be able to say:
- “this is the array/matrix/tensor surface we officially support,”
- “these shape/dtype/layout/view/device facts define that support,”
- “these interchange/storage lanes are zero-copy, copy-required, lossy, or unsupported,”
- “these checks justify the claim,”
- and “this is the portable bundle CI, release review, downstream crates, and later archaeology can consume.”

That is bigger than a math-trait crate and smaller than a new numerical platform.
