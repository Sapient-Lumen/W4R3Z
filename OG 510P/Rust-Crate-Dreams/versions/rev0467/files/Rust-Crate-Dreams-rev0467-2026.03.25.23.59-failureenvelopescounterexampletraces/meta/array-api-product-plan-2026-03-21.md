# Array API — product plan (2026-03-21)

This note sharpens **P-0003 Array API** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0003** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should **not** try to become a new universal tensor engine, a giant trait hierarchy, or a replacement for `ndarray`, `nalgebra`, `faer`, `mdarray`, `candle`, `burn`, `dfdx`, or Arrow.
It should provide one boring, reviewable **array support contract** above today’s crate families.

`0.1` should make five things first-class:

1. **semantic profile** — whether a crate is claiming `dense_nd_core`, `dense_linalg`, `tensor_backend`, `columnar_bridge_only`, or `manual_review_required`;
2. **layout/view truth** — what shape/stride order, borrowed-view, mutation-view, and contiguous assumptions are actually promised;
3. **device/dtype truth** — what devices and dtype defaults exist at runtime and whether transfer is explicit or hidden;
4. **namespace coverage truth** — which operation sets are intentionally supported and at what strength;
5. **interop-route truth** — whether conversions are borrowed, zero-copy, copy-required, lossy, or manual-review-only.

## What `0.1` should provide other people

- one compact `semantic-profile.receipt.json`
- one compact `layout-view.receipt.json`
- one compact `device-dtype.receipt.json`
- one compact `namespace-coverage.receipt.json`
- one compact `interop-route.receipt.json`
- one compact `array-bundle.manifest.json`
- one compact `array.summary.md`
- one compact `array.diff.json`
- a small dense-core conformance harness

## Commands worth shipping first

- `cargo array-contract capture`
- `cargo array-contract check`
- `cargo array-contract diff`
- `cargo array-contract summary`
- `cargo array-contract bundle`

## What to import, not reinvent

- profile and inspection ideas from the Python Array API standard, especially conformance and runtime capability/device/dtype discovery
- layout/stride/view facts from `ndarray` and `mdarray`
- dense-linear-algebra facts from `nalgebra` and `faer`
- device/backend facts from `candle`, `burn`, and similar tensor crates
- conversion facts from adapters and bridge crates when available
- Arrow/columnar facts only as adjacent interop routes, not as proof of dense-core equivalence

## Suggested `0.1` doctor warnings

- `profile_claim_exceeds_actual_namespace_support`
- `matrix_support_claim_hides_elementwise_vs_matmul_difference`
- `layout_claim_missing_stride_or_order_receipt`
- `device_claim_missing_runtime_default_dtype_basis`
- `zero_copy_claim_missing_layout_and_ownership_basis`
- `arrow_bridge_claimed_as_dense_nd_core`
- `autodiff_or_backend_extensions_claimed_as_core_namespace`

## First proving-ground scenarios

1. **`linalg-traits` is useful, but its own docs show `ndarray` and `nalgebra` disagree on `*`, so a namespace-coverage receipt is mandatory**
2. **`ndarray` supports row-major default plus custom strides, while `faer` documents column-major layout, so layout receipts must stay explicit**
3. **`candle` exposes concrete devices and dtype defaults, so device/dtype receipts should be first-class rather than buried in backend docs**
4. **Arrow arrays are valuable columnar substrate, but they need an interop-route receipt instead of silently counting as dense n-D core support**
5. **`mdarray` dense arrays and `burn` backend-generic tensors should not share one semantic profile unless the claim is deliberately narrowed**

## What to leave for later

- sparse-array standardization
- a full autodiff extension standard
- GPU kernel portability or scheduling contracts
- a universal “all numerics in Rust” trait hierarchy
- a new execution engine or backend runtime

## Main success condition

A team evaluating a numerical Rust dependency should be able to answer, from one small bundle:

- what semantic family is actually promised,
- what layout/view assumptions are safe,
- what devices and default dtypes exist,
- what namespaces are intentionally supported,
- and how values cross to neighboring ecosystems.

That is enough for `0.1` to be genuinely useful.
