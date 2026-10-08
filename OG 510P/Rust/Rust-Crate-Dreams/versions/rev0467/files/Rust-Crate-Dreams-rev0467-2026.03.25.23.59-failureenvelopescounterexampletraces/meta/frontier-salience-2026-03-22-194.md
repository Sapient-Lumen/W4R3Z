# Frontier salience note — 2026-03-22 (194)

The archive should spend one more pass on **P-0121 FFI Boundary & Bindings Conformance Kit** before widening into another generator-adjacent or language-shipkit lane.

## Why this lane still deserves another pass

The sharp missing layer is no longer “how do we generate bindings?”
The current substrate already answers that in many families.
The sharper missing question is:

> when a generated header, binding package, export macro, or custom section exists, what should another maintainer receive so projection basis, parity, and release-to-release drift do not get flattened into one fake “the foreign API is covered” story?

Recent source review keeps reinforcing that problem:

- Rust explicitly treats cross-language interop as an application area;
- `unsafe extern` and `C-unwind` make boundary responsibility more explicit, not less;
- UniFFI distinguishes interface definition methods and only generates foreign source bindings rather than building them;
- Diplomat backend attributes make backend-specific renames and namespaces a first-class possibility;
- `cbindgen` exposes configuration for layout, renaming, docs inclusion, parsing, and output style;
- and `wit-bindgen` options can materially change export-macro visibility and custom-section/link-helper behavior.

## Main archive judgment

Raise **P-0121** inside the lead cluster again, specifically for:

1. projection-basis receipts,
2. derivative-parity reports,
3. release-to-release projection drift,
4. and bundle manifests that keep authority, projection, ownership, callback, coverage, and error facts separate.

## Guardrail

Do not add another bridge wrapper, package shipkit, or language SDK helper unless it clearly escapes **P-0121**, the shipkit lanes, and the existing generator substrate.
