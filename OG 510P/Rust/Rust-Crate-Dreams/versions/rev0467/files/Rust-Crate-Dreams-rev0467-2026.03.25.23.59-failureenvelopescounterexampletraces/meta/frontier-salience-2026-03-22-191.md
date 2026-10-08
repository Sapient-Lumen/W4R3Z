# Frontier salience note — 2026-03-22 (191)

## Main judgment

The archive should spend another pass on **P-0121 FFI Boundary & Bindings Conformance Kit** before widening into another interop-adjacent sector.

## Why

Current Rust and adjacent interop sources make the missing layer sharper than “better bindings tooling”:

- Rust now explicitly treats **Cross-language interop** as a roadmap application area.
- Rust 2024 `unsafe extern` requirements make boundary signatures an explicit safety author responsibility.
- `"C-unwind"` keeps unwind-permitted and non-unwind ABI lanes distinct.
- UniFFI, CXX, Diplomat, WIT/component-model, and `cbindgen` each make different authority / lifetime / representation claims that are useful but non-uniform.

The missing crate is therefore not another generator, not another language-specific runtime helper, and not another package shipkit.
It is a receiver-facing contract for:

1. **interface authority**,
2. **ownership and unwind posture**,
3. **callback execution and lifecycle**,
4. **binding coverage and representation authority**,
5. **error-channel posture**,
6. and **portable review bundles**.

## Ranking consequence

Raise **P-0121** back into the lead cluster for the next few passes.
The lane is most worthy when it keeps interface-authority imports, callback lifecycle receipts, and bundle manifests distinct from the existing ownership / unwind / layout / error objects.

## What not to do

Do not spend the next pass on:

- another header generator wrapper,
- another language-specific SDK shipper,
- another bridge benchmark,
- or another generalized “FFI safety score”.

Those are adjacent at best.
The sharper missing value is the boring contract another team can review and diff.
