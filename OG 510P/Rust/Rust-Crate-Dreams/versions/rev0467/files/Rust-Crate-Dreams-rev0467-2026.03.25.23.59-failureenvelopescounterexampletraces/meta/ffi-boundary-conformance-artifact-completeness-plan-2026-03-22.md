# ffi-boundary-conformance artifact completeness plan — 2026-03-22

This note sharpens **P-0121 FFI Boundary & Bindings Conformance Kit** into the same artifact-complete shape now used by the archive’s strongest support-contract lanes.

## Main judgment

A worthwhile next implementation step is **not** another bridge adapter first.
It is making three more review objects first-class:

1. `interface-authority.import.json`
2. `callback-lifecycle.receipt.json`
3. `ffi-support-bundle.manifest.json`

These are the missing objects that keep “Rust declaration”, “generated header”, “callback exists”, and “boundary is checked” from collapsing into one fake answer.

## Why these three objects matter now

### 1. `interface-authority.import.json`

The ecosystem now has several plausible authority sources:

- Rust `unsafe extern` declarations,
- `cxx::bridge` modules,
- UniFFI UDL / proc-macro metadata,
- Diplomat bridge modules,
- WIT package/world/interface definitions,
- generated C/C++ headers,
- generated foreign bindings.

Those are **not** equivalent truths.
A generated header may be derivative of Rust code; a WIT package may be the primary interface contract; a `cxx` bridge may rely on static assertions for some claims and unsafe `ExternType` assertions for others.

A reviewer therefore needs one explicit authority receipt that says:

- what family the surface belongs to,
- what artifact is primary authority,
- what artifacts are generated/derived/imported,
- whether the authority is local, imported, or mixed,
- and what manual-review gaps remain.

### 2. `callback-lifecycle.receipt.json`

The existing callback-execution report says where callbacks run.
That is not enough.

A reviewer also needs to know:

- how callbacks are registered,
- whether handles are cloned and freed,
- whether unregister-before-drop is required,
- whether cancellation/drop callbacks exist,
- whether late callback arrival after teardown is possible,
- and whether those guarantees were observed or merely documented.

This is where UniFFI callback/object-reference mechanics, async cancellation hooks, and explicit free/final-call rules become reviewable instead of folklore.

### 3. `ffi-support-bundle.manifest.json`

The lane now has enough receipts that another engineer needs one portable pack manifest, not a scavenger hunt.

That bundle should point to:

- interface-authority imports,
- ownership-transfer receipts,
- unwind-posture receipts,
- callback-execution reports,
- callback-lifecycle receipts,
- binding-coverage reports,
- layout-authority receipts,
- error-channel receipts,
- diff reports,
- and any explicitly imported adjacent-lane artifacts.

## Recommended MVP order

1. authority import capture
2. callback-lifecycle capture
3. bundle manifest export
4. joined diagnostics that cite imported authority and lifecycle caveats
5. release-to-release diffing for authority/lifecycle changes

## Suggested diagnostics to add or strengthen

- `generated_artifact_not_primary_authority`
- `mixed_authority_family_requires_manual_review`
- `callback_unregister_policy_undeclared`
- `callback_drop_or_cancel_route_undeclared`
- `late_callback_after_teardown_possible`
- `binding_surface_claims_check_without_authority_source`
- `bundle_missing_primary_authority_receipt`

## Best proving grounds

1. a Rust crate with `unsafe extern "C"` declarations plus `cbindgen` header generation,
2. a `cxx` crate mixing shared and opaque types with one reused unsafe `ExternType` mapping,
3. a UniFFI surface exposing callback interfaces or async callbacks,
4. a WIT/component crate where WIT is authoritative and generated Rust is derivative,
5. a mixed-surface crate where one foreign binding is tested and another is packaging-only.

## Non-goals

- not a universal interop runtime,
- not a package/distribution suite,
- not a whole-program ABI verifier,
- not a one-number FFI safety score,
- not a replacement for generators or bridge families.
