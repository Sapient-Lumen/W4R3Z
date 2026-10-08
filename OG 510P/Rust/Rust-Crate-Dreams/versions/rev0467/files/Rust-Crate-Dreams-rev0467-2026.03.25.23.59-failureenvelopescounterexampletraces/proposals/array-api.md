---
id: P-0003
title: Array API — semantic profiles, layout receipts, device/dtype inspection, and interop routes for Rust numerics
status: idea
domains: [science, numerics, gpu, tensors, linear-algebra, interop]
last_reviewed: 2026-03-21
evidence:
  - https://data-apis.org/array-api/latest/purpose_and_scope.html
  - https://data-apis.org/array-api/latest/API_specification/inspection.html
  - https://docs.rs/ndarray/latest/ndarray/struct.ArrayBase.html
  - https://docs.rs/nalgebra/latest/nalgebra/
  - https://docs.rs/faer/latest/faer/
  - https://docs.rs/linalg-traits/latest/linalg_traits/
  - https://docs.rs/mdarray/latest/mdarray/
  - https://docs.rs/candle-core/latest/candle_core/enum.Device.html
  - https://docs.rs/burn-tensor/latest/burn_tensor/
  - https://docs.rs/arrow-array/latest/arrow_array/
  - https://scientificcomputing.rs/2025/discussions.html
---

# Problem

Rust now has enough serious array and tensor substrate that the main missing value is no longer “some array crate exists”.
The gap is that downstream users still cannot get one compact, reviewable answer for:

- **what semantic profile a crate actually supports**,
- **what layout/view assumptions are safe to rely on**,
- **what device and dtype inspection truths exist at runtime**,
- **what operation namespaces are actually promised**, and
- **how interop between crates is zero-copy, copy-required, lossy, or manual-review-only**.

Today’s ecosystem is rich but structurally split:

- `ndarray` is a general n-dimensional array library with row-major default order, views, slicing, and custom stride support;
- `nalgebra` is optimized around low-dimensional linear algebra and geometry, with one parametrizable matrix type spanning compile-time and runtime sizes;
- `faer` is optimized for medium/large dense linear algebra and documents a column-major matrix layout;
- `mdarray` offers another dense multidimensional vocabulary with static/dynamic dimensions and view types;
- `candle`, `burn`, and `dfdx` expose tensor/device/back-end stories with materially different device, autodiff, and execution assumptions;
- `arrow-array` is a columnar array substrate with null buffers and type-erased array values, which is adjacent but not the same support surface as dense numeric tensors.

That means a crate saying “accepts arrays”, “supports tensors”, or even “backend agnostic” still leaves too much ambiguity for scientific, ML, HPC, visualization, and data-engineering users.

The missing crate is therefore **not** a universal new tensor engine and **not** another one-off adapter.
It is the boring receiver-facing layer that lets Rust libraries publish an honest **array support contract**.

# Why this moved now

## 1. The wider ecosystem has already shown that fragmentation itself deserves a standard surface

The Python Array API standard says fragmentation across multidimensional array and tensor libraries makes it difficult to write code that works with multiple libraries, and responds with a standard centered on common functionality, semantics, data interchange, device support, conformance, and inspection utilities.
Rust now has enough analogous fragmentation that the same lesson applies.

## 2. Rust array crates are strong, but they optimize for different truths

The current docs make the differences concrete:

- `ndarray` emphasizes generic n-dimensional arrays, views, slicing, and shapes that include strides;
- `nalgebra` emphasizes low-dimensional linear algebra, graphics, and physics;
- `faer` emphasizes performance for medium/large dense matrices and a column-major memory model;
- `mdarray` emphasizes dense multidimensional ownership and view types with static/dynamic dimensions;
- `burn`, `candle`, and `dfdx` emphasize tensors, devices, backends, and in some cases autodiff.

So the next missing layer is not another container — it is the contract that says which profile is actually being claimed.

## 3. Existing generic-trait prior art proves the hard part is semantic mismatch, not just trait syntax

`linalg-traits` is useful and important, but its own docs explicitly say that `ndarray` overloads `*` for elementwise multiplication while `nalgebra` overloads `*` for matrix multiplication.
That is exactly the kind of mismatch a worthy crate should surface as **namespace coverage** and **semantic profile** truth rather than pretending all “matrix support” is interchangeable.

## 4. Device and dtype inspection now matter in ordinary practice

The Array API standard’s inspection utilities require implementations to expose capabilities, devices, default device, and default dtypes.
That maps directly onto current Rust tensor practice: `candle` has `Cpu`, `Cuda`, and `Metal` devices plus dtype-dependent defaults, while `burn`’s tensors are generic over backend and tensor kind.
A serious Rust array contract should therefore publish **device/dtype truth** rather than burying it in backend docs.

## 5. Columnar, dense, linear-algebra, and tensor surfaces should stop being flattened into one fake “array support” claim

`arrow-array` is explicit that Arrow arrays are known-length homogeneous sequences backed by low-level buffers and null metadata.
That is valuable substrate, but it is not the same thing as dense n-D views or tensor devices.
The archive should therefore keep Arrow-style columnar interop explicit as an **interop route** or adjacent profile, not treat it as silent proof of a common dense array API.

# What it provides

- `semantic-profile.receipt.json` — whether a crate is claiming `dense_nd_core`, `dense_linalg`, `tensor_backend`, `columnar_bridge_only`, or `manual_review_required`.
- `layout-view.receipt.json` — row/column/custom-stride posture, contiguous guarantees, borrowed-view support, mutation-view support, indexing/slicing caveats, and reshape/layout stability notes.
- `device-dtype.receipt.json` — runtime devices, default device, dtype availability/defaults, transfer posture, host-only vs accelerator posture, and unsupported-combination notes.
- `namespace-coverage.receipt.json` — which operation namespaces are intentionally supported (`core_create`, `index_slice`, `broadcast_elementwise`, `linear_algebra`, `reductions`, `autodiff_extensions`, `columnar_interop`) and whether support is exact, partial, extension-only, imported, or manual-review-only.
- `interop-route.receipt.json` — crate-to-crate or crate-to-format route with zero-copy vs copy-required vs lossy projection posture, layout changes, nullability/shape loss, and device-transfer notes.
- `array-bundle.manifest.json` — bundle manifest joining the above receipts for one crate version.
- `array.summary.md` — human-readable summary rendered from the receipts.
- `array.diff.json` — release-to-release diff on profile, layout, device, namespace, and interop changes.
- `cargo array-contract capture` — capture a crate’s advertised/imported surface.
- `cargo array-contract check` — verify declared receipts against tests/examples/adapters.
- `cargo array-contract diff <old> <new>` — compare two versions.
- `cargo array-contract summary` — render a compact support summary.

# What the crate should provide other people

1. **A clear semantic profile** so users know whether they are getting dense n-D arrays, linear algebra, tensor backend semantics, or only a bridge.
2. **Layout and view honesty** so zero-copy assumptions, contiguous assumptions, and mutation/view support are reviewable.
3. **Device and dtype inspection** so CPU/GPU/Metal/backend posture and default dtype rules stop being folklore.
4. **Namespace coverage truth** so “supports matrix ops” or “NumPy-like” becomes a reviewable promise instead of vague marketing.
5. **Interop-route honesty** so downstream crates know whether conversions are borrowed, copied, lossy, or shape/layout restricted.
6. **Conformance leverage** so backend authors can run a shared suite for the dense-core portions they actually claim.
7. **Release-to-release drift visibility** so semantic regressions are reviewable like API regressions.

# Persona / who it’s for

- scientific-computing crate authors who want to accept “array-like” inputs without overclaiming support
- ML / inference library authors who need backend/device receipts
- HPC / simulation teams switching between dense-nD and dense-linear-algebra implementations
- data and visualization teams bridging dense arrays to Arrow/columnar pipelines
- reviewers who need one compact answer before adopting a numerical dependency

# Users & user stories

- **Scientific library author**: “Tell me whether I can accept both `ndarray` and `mdarray` under one dense-core profile without lying about layouts or broadcasting.”
- **ODE / optimization maintainer**: “Show me whether this crate only needs the linear-algebra namespace so I do not accidentally promise tensor-device semantics.”
- **ML engineer**: “Give me one receipt that says which devices and default dtypes exist, and whether moving to GPU is explicit or automatic.”
- **Interop engineer**: “I need to know whether converting from dense tensors to Arrow is zero-copy, copy-required, or lossy.”
- **Release reviewer**: “Diff two versions and tell me whether broadcasting, layout guarantees, or device defaults changed.”

# Prior art (and why it’s insufficient)

- `ndarray`, `mdarray`, `nalgebra`, `faer`, `candle`, `burn`, and `dfdx` are all meaningful substrate, but each is an implementation family rather than a shared support contract.
- The Python Array API standard proves common semantics, conformance, inspection, and versioning matter — but it is for Python libraries, and Rust still needs its own crate-facing contract vocabulary.
- `linalg-traits` is good prior art for generic linear-algebra consumers, but it is intentionally narrower than dense n-D arrays, tensors, devices, dtype defaults, and interop-route truth.
- Arrow traits and builders are good prior art for columnar arrays, but they do not by themselves define dense n-D layout or broadcasting semantics.
- Individual backend-agnostic frameworks (`burn`, etc.) help within their own ecosystems, but do not give the rest of Rust one shared receipt vocabulary.

# Design goals

1. **Receiver-facing first** — optimize for another team deciding whether they can depend on this crate safely.
2. **Profiles before universality** — start by naming support classes honestly instead of pretending one trait surface can erase all differences.
3. **Conformance where possible, receipts where necessary** — dense-core pieces can be tested; ecosystem mismatches should become explicit receipts rather than hidden incompatibilities.
4. **Interop honesty** — every route should say whether it is zero-copy, borrowed, copy-required, or lossy.
5. **Device/dtype explicitness** — backend and accelerator posture should be published, not guessed from examples.
6. **Small stable vocabulary** — prefer a few durable receipt types over a giant trait universe.
7. **Layered adoption** — let crates adopt one profile/namespace/interop route at a time.

# MVP surface

- one `semantic-profile.receipt.json`
- one `layout-view.receipt.json`
- one `device-dtype.receipt.json`
- one `namespace-coverage.receipt.json`
- one `interop-route.receipt.json`
- one `array-bundle.manifest.json`
- dense-core conformance tests for construction, indexing, broadcasting, and reductions where the profile claims them
- import adapters for `ndarray`, `mdarray`, `nalgebra`, `faer`, and one tensor backend family to prove the vocabulary works
- `summary` and `diff` commands so humans can review results without reading raw JSON

# Distinctive implementation shape

## Crates

- `array-contract-core` — schemas, diff logic, summary rendering, profile/coverage vocabularies.
- `array-contract-conformance` — dense-core conformance harness.
- `array-contract-import` — imports from adapter metadata and curated crate-specific inspectors.
- `array-contract-adapters/*` — optional adapters for `ndarray`, `mdarray`, `nalgebra`, `faer`, `candle`, `burn`, and others.

## First-class truths

1. **semantic profile** — what family of array semantics is actually promised;
2. **layout/view** — what shape/stride/borrow/mutation assumptions are safe;
3. **device/dtype** — what execution targets and dtype defaults are real;
4. **namespace coverage** — what operation sets are supported and at what strength;
5. **interop route** — how values cross library boundaries and what is lost.

# Adoption path

## MVP → v0.1

- dense-core profile vocabulary stabilized
- `ndarray` + `mdarray` + `nalgebra` + `faer` import adapters
- conformance harness for dense-core construction/indexing/broadcast/reduction claims
- diffable JSON/Markdown outputs

## v0.2

- first tensor-backend adapters (`candle`, `burn`, `dfdx`)
- better device/dtype inspection importers
- more explicit autodiff extension vocabulary

## v0.3

- interop-route receipts for Arrow bridges and selected zero-copy routes
- optional sparse/columnar-adjacent profile notes without merging them into dense core

## v1.0

- stable receipt vocabulary
- multiple independent adopters publishing bundle artifacts
- downstream crates using receipts as dependency-adoption evidence

# Non-goals

- replacing `ndarray`, `nalgebra`, `faer`, `candle`, `burn`, `dfdx`, or Arrow
- creating a universal execution engine
- standardizing GPU kernels, schedulers, or autodiff internals
- pretending columnar arrays and dense tensors are the same support surface
- defining every numerical algorithm in one trait hierarchy

# Open questions

- What is the smallest dense-core namespace that can attract adoption without becoming useless?
- Should compile-time-shape-heavy tensor libraries get one shared extension vocabulary, or remain profile-specific at first?
- Which interop routes can be checked mechanically versus requiring manual-review receipts?
- How should sparse arrays enter the story later without destabilizing the dense-core contract?

# Sources

- https://data-apis.org/array-api/latest/purpose_and_scope.html
- https://data-apis.org/array-api/latest/API_specification/inspection.html
- https://docs.rs/ndarray/latest/ndarray/struct.ArrayBase.html
- https://docs.rs/nalgebra/latest/nalgebra/
- https://docs.rs/faer/latest/faer/
- https://docs.rs/linalg-traits/latest/linalg_traits/
- https://docs.rs/mdarray/latest/mdarray/
- https://docs.rs/candle-core/latest/candle_core/enum.Device.html
- https://docs.rs/burn-tensor/latest/burn_tensor/
- https://docs.rs/arrow-array/latest/arrow_array/
- https://scientificcomputing.rs/2025/discussions.html
