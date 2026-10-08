# Array API — lane boundaries (2026-03-21)

This note keeps **P-0003 Array API** from collapsing into every adjacent numerics ambition.

## What this lane is

**P-0003** is a receiver-facing support contract for five truths:

1. **semantic profile**;
2. **layout/view truth**;
3. **device/dtype truth**;
4. **namespace coverage truth**;
5. **interop-route truth**.

It is about making array support claims reviewable across today’s Rust numerics ecosystem.

## What this lane is not

### Not another dense array or tensor implementation

This lane should not compete with `ndarray`, `mdarray`, `candle`, `burn`, `dfdx`, or future tensor crates.
It should import facts from them.

### Not another linear algebra library

`nalgebra`, `faer`, BLAS/LAPACK bindings, sparse solvers, and domain-specific numerical kernels are substrate.
`P-0003` stays focused on the support contract above them.

### Not the columnar / Arrow lane

Arrow arrays are known-length homogeneous columnar values with nullability and low-level buffer structure.
That is adjacent substrate, but not the same thing as dense n-D array semantics.
Treat Arrow as an explicit interop route or adjacent profile, not silent core evidence.

### Not the sparse-array standard lane

Sparse formats and graph/mesh/tensor-network structures should be kept separate until dense-core receipts are stable.

### Not the execution-semantics lane

Task scheduling, eager vs lazy execution, accelerator runtime behavior, fusion, kernel caching, and autotuning are implementation territory.
Keep those separate from `P-0003` unless a receipt explicitly imports them as non-core notes.

### Not the autodiff-standard lane

Autodiff is important, but it should enter as an extension or separate namespace-coverage claim rather than silently redefining the core array API.

## Five truths this lane must keep separate

1. **semantic profile** — dense n-D core, dense linear algebra, tensor backend, columnar bridge only, or manual-review required;
2. **layout/view** — row/column/custom stride, borrowed vs owned, view mutation, contiguous guarantees, reshape stability;
3. **device/dtype** — host-only, runtime device list, default device, dtype defaults, unsupported combinations, transfer posture;
4. **namespace coverage** — creation, indexing, broadcasting, reductions, linear algebra, autodiff extensions, columnar bridge support;
5. **interop route** — borrowed/zero-copy/copy-required/lossy/manual-review crossing between crates or formats.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- “supports arrays” and “supports dense n-D core semantics”,
- a matrix API and a general tensor API,
- row-major default plus custom strides and guaranteed column-major layout,
- host-only arrays and runtime-inspected multi-device tensors,
- backend-generic tensor support and dense-core generic array support,
- or Arrow columnar arrays and dense numeric tensors.

## Preferred artifact vocabulary

- `semantic-profile.receipt`
- `layout-view.receipt`
- `device-dtype.receipt`
- `namespace-coverage.receipt`
- `interop-route.receipt`
- `array-bundle.manifest`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
