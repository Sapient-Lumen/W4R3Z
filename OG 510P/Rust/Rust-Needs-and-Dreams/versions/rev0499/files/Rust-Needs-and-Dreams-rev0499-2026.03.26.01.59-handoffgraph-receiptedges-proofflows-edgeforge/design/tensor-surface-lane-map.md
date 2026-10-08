# Design: Tensor Surface Lane Map

## Goal
Sharpen **Tensor Surface Kit** into an explicit lane map so future revisions stop flattening Rust numerical work into one fake “array support”, “tensor support”, or “scientific readiness” verdict.

The missing contribution is not one universal array trait or one winning runtime.
It is a reviewable boundary that keeps today’s materially different numerical families legible enough to compare, adapt, and hand off.

## Why this needs a lane map now
Rust already has multiple serious numerical families, but they do not mean the same thing:
- `ndarray` centers general n-dimensional arrays with owned/storage/view vocabulary.
- `nalgebra` and `faer` are strongly linear-algebra-shaped matrix families with their own size/storage/view assumptions.
- Candle and Burn are runtime/device-shaped tensor families with device and autodiff posture in the public story.
- `zarrs` makes persisted multidimensional-array metadata and validation a real lane.
- DLPack is explicitly an interchange lane, not a universal native tensor object.
- `argmin-math` already proves Rust users need bridges across `Vec`, `ndarray`, `nalgebra`, and `faer` rather than one winner.

That means the next ecosystem contribution should preserve **lane identity + adapter truth + evidence** above those pieces.

## The lanes

### 1) Dense n-dimensional array lane
Use for general-purpose in-memory array surfaces whose primary identity is **rank/shape + element type + view/slice behavior**.

Typical examples:
- `ndarray`
- dense CPU array APIs with borrowed views and strided semantics

Keep explicit:
- dynamic/fixed rank posture
- slicing/view semantics
- stride and contiguity posture
- copy-vs-view adaptation behavior

Do **not** quietly reinterpret this lane as matrix-only or runtime-tensor-only.

### 2) Linear algebra / matrix lane
Use for families whose primary identity is **matrix/vector semantics**, decomposition-oriented operations, or strongly shaped storage assumptions.

Typical examples:
- `nalgebra`
- `faer`

Keep explicit:
- static vs dynamic size posture
- matrix-major storage/layout assumptions
- owned vs `MatRef`/`MatMut`-style borrowing lanes
- exact-vs-lossy adaptation to general arrays

Do **not** flatten matrix families into generic tensor claims just because the values are multidimensional.

### 3) Runtime tensor / device lane
Use for families whose primary identity is **runtime-managed tensors**, often with device placement, backend selection, quantization, or autodiff posture in the public contract.

Typical examples:
- Candle
- Burn

Keep explicit:
- device/backend family
- autodiff posture
- runtime-managed ownership or graph state
- host/device transfer or materialization requirements

Do **not** let the runtime name stand in for shape/layout/support truth.

### 4) Persisted multidimensional-array lane
Use for families whose primary identity is **stored arrays plus metadata**, not just in-memory values.

Typical examples:
- `zarrs`
- other array-store metadata lanes when they are genuinely array-shaped rather than model-packaging-shaped

Keep explicit:
- metadata/version/conformance posture
- chunking/layout/storage assumptions
- load/store validation and round-trip findings
- array-store truth versus in-memory tensor truth

Do **not** flatten persisted-array metadata into runtime tensor support.

### 5) Interchange / attachment lane
Use for **cross-family exchange structures** or adjacent attachments that move tensor-like payloads without becoming the native authority for every family.

Typical examples:
- DLPack
- model-oriented tensor-storage attachments where Tensor Surface is only importing array payload truth rather than owning model/runtime truth
- Arrow attachments when tensor work is adjacent to tabular/columnar boundaries

Keep explicit:
- zero-copy vs copy-required vs lossy posture
- shape/dtype/layout fidelity
- device-transfer assumptions
- metadata preserved vs dropped

Do **not** narrate an interchange structure as the one true tensor API.

### 6) Adapter / consumer-import lane
Use for crates or workflows whose main value is **bridging or consuming** multiple numerical families without owning all of their semantics.

Typical examples:
- `argmin-math`
- downstream model/offload/data consumers importing tensor packs

Keep explicit:
- which source and destination lanes are involved
- what was exact, copy-required, lossy, partial, or unsupported
- what the consumer imported versus redefined

Do **not** let a successful adapter demo erase the underlying lane differences.

## Cross-cutting truths that must stay separate
Every lane can still carry multiple distinct truths:
- **shape/dtype truth**
- **layout/view truth**
- **ownership/mutability truth**
- **device/autodiff truth**
- **interchange/storage truth**
- **check/report evidence**
- **bounded consumer imports**

Those are not interchangeable. A tensor lane can share shape truth with an array lane while differing radically on layout, ownership, device, or storage posture.

## Preferred archive interpretation
When the archive discusses Tensor Surface going forward, prefer:
- **dense-array lane**
- **matrix/linalg lane**
- **runtime-tensor/device lane**
- **persisted-array lane**
- **interchange/attachment lane**
- **adapter/consumer-import lane**

over:
- one fake “numerical object”
- one fake “tensor support” verdict
- one universal Rust array trait proposal
- silently importing dataset/model/offload truth into Tensor Surface

## What a worthy contribution should look like in practice
A thin `cargo tensorcheck` / `tensor-pack/v0` layer should:
- publish which lane or lanes a crate is actually claiming,
- attach separate shape/layout/ownership/device/storage artifacts,
- report exact vs copy-required vs lossy adapters,
- record what was checked and what remained imported,
- and hand bounded tensor facts to Dataset / Model / Offload / Scientific Productization consumers.

The bar is not another tensor runtime.
The bar is making lane-aware tensor claims reviewable.

## Read this together with
- `design/tensor-surface-kit.md`
- `design/tensor-surface-pilot-program.md`
- `gaps/numerical-array-tensor-surfaces-and-interop-contracts.md`
- `proposals/epic-tensor-surface-kit.md`
- `design/scientific-productization-stack.md`
