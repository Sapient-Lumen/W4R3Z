# Design: Tensor Surface Kit (`cargo tensorcheck`, `tensor-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust project’s supported **array / matrix / tensor surface**: shape and dtype truth, layout and view posture, ownership and mutability assumptions, device/autodiff/runtime posture, interchange/storage adapters, and checked evidence for what actually works.

This should **not** replace `ndarray`, `nalgebra`, `faer`, Candle, Burn, DLPack, Zarr, Arrow, or model/runtime frameworks.
It should make them compose better and make support claims reviewable.

Read [`design/tensor-surface-lane-map.md`](./tensor-surface-lane-map.md) first: Tensor Surface must keep **dense-array + matrix/linalg + runtime-tensor/device + persisted-array + interchange/attachment + adapter/consumer-import** lanes separate instead of narrating one fake canonical tensor object.

## References (signals)
- `ndarray` centers a general `ArrayBase` model for n-dimensional arrays, with explicit view and raw-storage vocabulary.
  https://docs.rs/ndarray/latest/ndarray/struct.ArrayBase.html
  https://docs.rs/ndarray/latest/ndarray/type.ArrayView.html
  https://docs.rs/ndarray/latest/ndarray/trait.RawData.html
- `nalgebra` explicitly distinguishes statically and dynamically sized matrices and uses column-major storage in its matrix family.
  https://www.nalgebra.rs/docs/user_guide/vectors_and_matrices/
  https://docs.rs/nalgebra/latest/nalgebra/base/type.Matrix3.html
- `faer` is a high-performance linear algebra library with explicit `Mat` / `MatRef` / `MatMut` vocabulary types.
  https://docs.rs/faer/latest/faer/
  https://docs.rs/faer/latest/faer/mat/index.html
- Candle exposes `Tensor`, `Shape`, `Layout`, and `Device` as first-class core concepts.
  https://docs.rs/candle-core/latest/candle_core/struct.Tensor.html
  https://docs.rs/candle-core/latest/candle_core/shape/index.html
  https://docs.rs/candle-core/latest/candle_core/layout/index.html
- Burn exposes tensor/backend/device/autodiff vocabulary and Burn Store adds cross-framework tensor/model storage lanes.
  https://docs.rs/burn/latest/burn/tensor/index.html
  https://docs.rs/burn/latest/x86_64-pc-windows-msvc/burn/tensor/backend/index.html
  https://docs.rs/burn-store
- `argmin-math` already supports `Vec`, `ndarray`, `nalgebra`, and `faer`, which is strong evidence that multi-family numerical interop is a real need rather than a hypothetical one.
  https://docs.rs/argmin-math/
- DLPack exists specifically to enable stable tensor exchange across frameworks and hardware backends, and Rust already has `dlpark` as a safe wrapper / trait layer.
  https://dmlc.github.io/dlpack/latest/
  https://dmlc.github.io/dlpack/latest/c_api.html
  https://docs.rs/dlpark/latest/dlpark/versioned/index.html
  https://docs.rs/dlpark/latest/dlpark/traits/index.html
- `zarrs` demonstrates that Rust already has a serious multidimensional-array storage lane with explicit metadata and validation rules.
  https://docs.rs/zarrs/latest/zarrs/
  https://docs.rs/zarrs/latest/zarrs/array/struct.Array.html
- Apache Arrow remains an important adjacent structured-data lane, but its own format docs make clear that it is a columnar structured-data model rather than a universal tensor authority.
  https://arrow.apache.org/docs/format/Columnar.html
  https://docs.rs/arrow-array/latest/arrow_array/struct.RecordBatch.html

## Lane interpretation (read before defining artifacts)
Tensor Surface should now be read through the explicit lane map in [`design/tensor-surface-lane-map.md`](./tensor-surface-lane-map.md). In practice that means:
- `ndarray`-style dense arrays are not the same lane as `nalgebra`/`faer` matrix families.
- Matrix families are not the same lane as Candle/Burn runtime-managed tensors.
- Persisted multidimensional-array metadata (`zarrs`) is not the same lane as in-memory tensor/runtime truth.
- DLPack and adjacent attachments are interchange lanes, not the one native authority for every family.
- Adapter crates and downstream importers must report exact vs copy-required vs lossy outcomes rather than erasing the source/destination lanes.

The kit should therefore publish lane-aware declarations first and only then attach shape/layout/ownership/device/storage facts underneath them.

## Core components

### 1) `tensor-surface/v0`
A design-time declaration of the supported numerical surface for a crate/binary/workspace.

Required ideas:
- stable surface identity
- boundary kind:
  - dense n-dimensional array lane
  - matrix / linear-algebra lane
  - runtime tensor / device lane
  - persisted multidimensional-array lane
  - interchange / attachment lane
  - adapter / consumer-import lane
- intended consumers:
  - scientific / numerical
  - ML training / inference
  - image / raster / signal processing
  - geospatial / simulation / optimization
  - internal only
- support class:
  - official
  - checked subset
  - experimental
  - deprecated
  - internal
- attached shape/dtype, layout/view, device/autodiff, and interchange profiles

This is the thing humans review before trusting automation.

### 2) `shape-dtype-profile/v0`
A machine-readable description of numerical shape and element semantics.

Required ideas:
- rank / dimensionality posture:
  - fixed rank
  - dynamic rank
  - mixed rank families
- static vs dynamic dimension notes where relevant
- named-dimension or axis-label posture when relevant
- element families:
  - integer
  - float
  - bool
  - complex
  - quantized
  - domain-specific/custom
- dtype constraints and unsupported combinations
- broadcasting / reduction / indexing notes where they materially affect support

Design rule: shape and element truth are not the same thing as device or storage truth.

### 3) `layout-view-profile/v0`
A description of memory-layout and view semantics.

Required ideas:
- contiguous / strided / column-major / row-major / mixed posture
- borrowed view support
- mutable view support
- slicing / reshaping / transpose / broadcast-view posture
- aliasing caveats when public
- copy-on-adapt vs view-preserving behavior where relevant
- layout-sensitive API claims

Design rule: preserve explicit layout/view truth instead of burying it in example code.

### 4) `ownership-mutability-profile/v0`
A declaration of what can be owned, borrowed, mutated, or shared.

Required ideas:
- owned / borrowed / ref-counted / runtime-managed lanes
- mutability posture
- in-place update support or absence
- lifetime/borrowing constraints when part of the public surface
- interior mutability or graph-managed state when relevant
- copy/clone/materialization costs when adapters require them

Design rule: do not flatten array views, matrix references, and graph-managed tensors into one fake “tensor object.”

### 5) `device-autodiff-profile/v0`
A declaration of backend/runtime posture.

Required ideas:
- CPU / accelerator / mixed-device lanes
- backend/runtime families (pure CPU arrays, matrix engines, Candle, Burn, custom runtimes)
- autodiff posture:
  - none
  - optional
  - required
  - backend-specific
- precision / quantization notes that materially affect support
- unsupported backend/device combinations
- target/runtime baseline notes when public support depends on them

Design rule: device truth belongs here, not inside shape/layout artifacts.

### 6) `tensor-interchange-profile/v0`
A declaration of persistence and exchange lanes.

Required ideas:
- interchange/storage families:
  - DLPack
  - Arrow attachment lane
  - Zarr
  - SafeTensors / Burn Store / model-oriented tensor stores
  - crate-native binary / serde lane
- zero-copy / borrowed / copy-required / lossy / unsupported posture
- shape/dtype/layout fidelity notes
- metadata carried vs dropped
- device-transfer assumptions
- version / spec / format attachments

Design rule: preserve raw DLPack/Zarr/Arrow/store truth as attachments instead of flattening them into one fake universal tensor file.

### 7) `tensor-adapter-profile/v0`
A first-class description of how one numerical surface adapts to another.

Required ideas:
- source and destination surface ids
- exact / copy-required / lossy / partial / unsupported result class
- shape/dtype/layout/device changes
- required materialization or host/device transfer
- unsupported edge cases
- migration notes

Design rule: adapter truth is first-class. “Works with X” is not enough.

### 8) `tensor-check-plan/v0`
A concrete declaration of what is checked.

Required ideas:
- selected surfaces and adapter pairs
- selected shape/dtype/layout/device cases
- selected interchange/storage lanes
- checks performed:
  - shape/dtype extraction
  - layout/view validation
  - adapter-fidelity checks
  - device/autodiff checks
  - load/store/exchange checks
  - copy-vs-view expectations
  - negative / unsupported-case checks
- intentionally omitted lanes and why

### 9) `tensor-check-report/v0`
Evidence from extraction and compatibility checks.

Possible contents:
- extracted shape/dtype/layout/device summary
- adapter pass/fail/unsupported findings
- copy-required or layout-loss findings
- interchange/storage fidelity findings
- unsupported-backend or unsupported-dtype results
- linked raw attachments: metadata dumps, DLPack descriptors, Zarr metadata, benchmark smoke notes, or runtime logs

### 10) `tensor-diff-report/v0` (optional)
For compatibility-sensitive change review:
- rank or shape posture changed
- dtype support widened/narrowed
- layout/view guarantees changed
- device/autodiff support changed
- adapter result class changed
- interchange/storage fidelity changed
- support class changed

Should distinguish:
- additive changes
- compatibility-sensitive changes
- copy-cost changes
- runtime/device regressions
- metadata-only updates

### 11) `tensor-pack/v0`
Bundle format containing:
- `tensor-surface/v0`
- `shape-dtype-profile/v0`
- `layout-view-profile/v0`
- `ownership-mutability-profile/v0`
- optional `device-autodiff-profile/v0`
- one or more `tensor-interchange-profile/v0`
- optional `tensor-adapter-profile/v0`
- one or more `tensor-check-report/v0`
- optional `tensor-diff-report/v0`
- optional raw attachments: DLPack descriptors, Zarr metadata, store metadata, benchmark notes, example fixtures, and runtime-specific logs

This is the unit that should travel through CI, release review, model/data/offload integration work, and later archaeology.

### 12) `cargo tensorcheck`
Reference UX:
- `cargo tensorcheck init`
- `cargo tensorcheck inspect`
- `cargo tensorcheck adapters`
- `cargo tensorcheck check`
- `cargo tensorcheck diff`
- `cargo tensorcheck pack`

`cargo tensorcheck` should begin as an adapter / explainer / packer.
It should not pretend to be the one true array library, tensor runtime, or numerical platform.

## Default policy
- **Separate shape/dtype truth, layout/view truth, ownership/mutability truth, device/autodiff truth, and interchange truth.**
- **Preserve raw library and format truth** from `ndarray`, `nalgebra`, `faer`, Candle, Burn, DLPack, Zarr, Arrow attachments, and model-store lanes instead of flattening them into one fake universal tensor object.
- **Treat adapter lossiness as a first-class outcome** so copy-required, layout-sensitive, and unsupported conversions are honest.
- **Keep checked evidence distinct from illustrative examples** so docs stay honest.
- **Prefer bounded evidence** (small fixtures, metadata snapshots, explicit adapter checks) over giant numeric dumps.
- **Keep Arrow and dataset/table truth adjacent, not absorbed.**

## What the kit should provide to others
- **Model Surface Kit:** attach tensor-runtime and tensor-storage truth without making model packs own every shape/layout/device detail.
- **Offload Surface Kit:** import device/backend and transfer assumptions from explicit tensor-adapter and device profiles instead of guessing them from runtime names.
- **Dataset Surface Kit:** attach Arrow/Zarr/multidimensional-storage truth where datasets feed tensor consumers without turning tabular schemas into fake tensor authorities.
- **Geospatial Surface Kit:** describe raster/array-like spatial payloads and array adapters without flattening CRS/geometry truth into tensor metadata.
- **Support Envelope / Perf / Footprint work:** record supported backends, precision posture, and adapter costs in a reusable way.

## Overlap boundaries
- **Not another array/tensor runtime:** `ndarray`, `nalgebra`, `faer`, Candle, Burn, and future runtimes remain the execution layer.
- **Not another universal math trait:** abstraction crates like `argmin-math` remain valuable, but this kit is about reviewable support truth above them.
- **Not the dataset/table contract:** Arrow tables, Parquet, catalogs, Delta, and Iceberg remain dataset-surface territory.
- **Not the model/task contract:** tokenizer/task/artifact/runtime claims remain model-surface territory.
- **Not the accelerator/kernel contract:** kernel maps, launch semantics, and transfer synchronization remain offload-surface territory.
