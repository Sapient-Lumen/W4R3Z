# ffi-boundary-conformance projection/parity plan — 2026-03-22

This note sharpens **P-0121 FFI Boundary & Bindings Conformance Kit** one layer further.

## Main judgment

The next worthwhile implementation step is **not** another bridge/generator adapter first.
It is making three more review objects first-class:

1. `projection-basis.receipt.json`
2. `derivative-parity.report.json`
3. `projection-drift.report.json`

These are the missing objects that keep “we generated a header/binding” from masquerading as “the receiver-facing contract is obvious and still faithful.”

## Why these objects matter now

Current interop substrate is rich but configurable:

- UniFFI can mix UDL and proc-macro surfaces, generate source bindings without building them, and still has conditional-compilation caveats.
- Diplomat can apply backend-specific attributes such as renames, namespaces, and iterator lowering, which means one backend projection is not necessarily the same public surface as another.
- `cbindgen` exposes substantial configuration around names, layout, macro expansion, parsing, docs inclusion, and output language.
- `cxx` keeps a stronger coupling between the bridge and generated code, but still distinguishes source-of-truth directions, namespaces, names, error conversion, and async lanes.
- `wit-bindgen` has options that affect export-macro naming/visibility, generated type breadth, and custom-section helper behavior.

A reviewer therefore needs more than “authority exists” and “bindings were generated.”
They need to know **what derivative surface was emitted, how it was shaped, whether it still faithfully reflects authority, and what changed across releases.**

## Recommended new review objects

### 1. `projection-basis.receipt.json`

This receipt should answer:
- what emitted artifact is being reviewed,
- what primary authority it projects from,
- what tool/backend/configuration produced it,
- whether it is a full projection, subset projection, renamed projection, backend-shaped projection, or packaging-only artifact,
- and whether generation stops before build/package proof.

### 2. `derivative-parity.report.json`

This report should answer:
- whether the derivative artifact still faithfully reflects the authority source,
- what receiver-visible differences were introduced (renames, namespaces, hidden items, changed result/exception lowering, docs-only adornment, helper disablement, etc.),
- what proof class backs the claim,
- and whether the resulting surface is safe to summarize as “equivalent”, “subset”, “different but acceptable”, or “manual review required”.

### 3. `projection-drift.report.json`

This report should answer:
- what changed release-to-release in the projected foreign surface,
- whether the drift came from authority change, generator/backend/config change, or packaging/build change,
- whether the drift is additive, receiver-visible, breaking, or manual-review-only,
- and which downstream surfaces need explicit re-review.

## Suggested diagnostics

- `projection_basis_implicit`
- `projection_subset_without_receiver_notice`
- `backend_projection_nonuniform`
- `generated_source_not_built_or_packaged`
- `projection_drift_receiver_visible`
- `projection_drift_breaking`
- `projection_parity_manual_review_required`

## Best proving grounds

1. a `cbindgen` crate whose generated header includes configured renames/docs/layout knobs,
2. a Diplomat crate using backend attrs to rename or namespace one backend differently from another,
3. a UniFFI crate that mixes UDL and proc-macro surfaces and only generates foreign source code,
4. a WIT/component crate where export-macro/custom-section options materially shape the derivative surface,
5. a mixed-surface crate where one binding projection is directly built and another is generated-only.

## Non-goals

- not a universal generator test suite,
- not a language-package shipkit,
- not a generic semver checker for every foreign ecosystem,
- not a proof that every generated artifact compiles in every downstream toolchain,
- not a one-number “FFI parity score”.
