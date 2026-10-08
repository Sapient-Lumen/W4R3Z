# ffi-boundary-conformance-kit product plan — 2026-03-20

This note sharpens **P-0121 FFI Boundary & Bindings Conformance Kit** into an implementation-ready `0.1` direction.

## Main judgment

A worthwhile `0.1` should **not** try to become:

- another bindings generator,
- another per-language packaging tool,
- or a generic FFI “safety” framework that rewrites every existing bridge.

It should instead become a **boundary contract layer** that helps a crate publish one reviewable answer to four boring but high-value questions:

1. **How is ownership transferred at the boundary?**
2. **What is the panic / unwind policy for each exported surface?**
3. **Where and how do callbacks execute, and what teardown rule makes them sound?**
4. **Which bindings are actually checked versus merely generated or documented?**

The missing value is the contract layer above today’s generators, bridges, and runtime adapters.

## Why this lane got stronger

Current Rust and ecosystem substrate makes the gap more actionable than it used to be:

- the 2024 Edition now requires `unsafe extern` blocks, making boundary obligations more explicit;
- the Reference and RFC 2945 keep unwinding and non-unwinding ABI categories sharply distinct;
- `catch_unwind` remains available for catching unwinding Rust panics at a boundary, but only for unwinding panics;
- the Nomicon still calls out callback-after-destruction hazards and the need to unregister before drop for async callbacks;
- UniFFI now exposes runtime support for buffers, handles, futures, and callback continuations;
- UniFFI’s own callback-interface docs say callback interfaces are soft-deprecated and conceptually thread-safe outside Rust’s type system;
- Diplomat, `cxx`, `cbindgen`, and `wit-bindgen` each provide strong slices, but none publish one shared receiver-facing contract for ownership, unwind, callback, and coverage truth.

That means the ecosystem no longer mainly lacks raw primitives.
It lacks a **shared product-shape** for publishing FFI boundary support truth.

## What the crate should provide other people

For SDK teams, systems integrators, release reviewers, and downstream adopters, the crate should provide:

1. **One ownership-transfer receipt** instead of free-function folklore.
2. **One unwind-posture receipt** instead of scattered ABI and panic caveats.
3. **One callback-execution report** instead of guessing thread/runtime assumptions from codegen.
4. **One binding-coverage report** instead of equating generation with verification.
5. **One compact contract-check report** that keeps imported facts, observed checks, and manual-review zones visibly separate.

## Four first-class review objects

### 1. `ownership-transfer.receipt`

This artifact should answer:

- what boundary surface is being described,
- whether the value is borrowed, copied, opaque-handle-based, explicit-free, reference-counted, or runtime-managed,
- which allocation domain owns the backing storage,
- what release mechanism exists,
- and how long the foreign side may keep it.

### 2. `unwind-posture.receipt`

This artifact should answer:

- which ABI family is in play,
- whether Rust panics are caught and translated, abort, or are intentionally allowed to unwind,
- whether foreign exceptions/unwinds may enter Rust,
- and what containment strategy exists.

### 3. `callback-execution.report`

This artifact should answer:

- whether callbacks are synchronous, event-driven, or continuation/future-based,
- where execution originates,
- what thread or runtime affinity is assumed,
- whether teardown depends on unregister-before-drop,
- and whether completion is inline, after return, or via a poll/cancel/free lifecycle.

### 4. `binding-coverage.report`

This artifact should answer:

- which surfaces exist,
- which family each one belongs to,
- how it is generated,
- and whether it was `directly_checked`, `generated_only`, `packaging_only`, `docs_only`, or still `manual_review_required`.

## Recommended `0.1` command surface

### `cargo ffi-contract capture`
Capture the declared/imported contract and emit:
- `ownership-transfer.receipt.json`
- `unwind-posture.receipt.json`
- `callback-execution.report.json`
- `binding-coverage.report.json`

### `cargo ffi-contract check`
Run conservative checks and emit:
- `ffi-contract-check.report.json`

### `cargo ffi-contract diff`
Compare two bundles and emit:
- `ffi-contract-diff.report.json`

### `cargo ffi-contract bundle`
Produce one compact `.fficontractbundle.zip`.

## Recommended crate/workspace split

- `ffi_contract_model`
- `ffi_contract_import_uniffi`
- `ffi_contract_import_diplomat`
- `ffi_contract_import_cbindgen`
- `ffi_contract_import_cxx`
- `ffi_contract_import_wit`
- `ffi_contract_check`
- `ffi_contract_pack`
- `cargo-ffi-contract`

## Discovery order

1. **Boundary family import**
   - `extern` C ABI surfaces
   - `cxx::bridge`
   - UniFFI metadata and scaffolding
   - Diplomat bridge definitions
   - WIT/component-model bindings
2. **Ownership capture**
   - buffers
   - handles / opaque types
   - callback object references
   - explicit free or drop routes
3. **Unwind capture**
   - ABI family
   - `catch_unwind` wrappers
   - abort-profile assumptions
   - explicit unwind ABI routes
4. **Callback capture**
   - registration model
   - thread/runtime origin
   - teardown rule
   - async continuation lifecycle
5. **Coverage capture**
   - language/runtime targets
   - generation mode
   - check mode
6. **Bundle and diff**
   - export one compact review bundle

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- `unsafe extern` and ABI declarations
- explicit `catch_unwind` wrappers
- UniFFI RustBuffer/Handle/future surfaces
- Diplomat opaque-type bridges
- `cxx` bridge declarations
- `cbindgen` header facts
- WIT/component model bindings

### Do not flatten into one fake verdict
- “uses UniFFI”
- “has a C ABI”
- “supports callbacks”
- “supports async”
- “generated bindings exist”

Those are ingredients, not the contract.

## Preferred proving grounds

- a C ABI crate with explicit free functions and a borrowed buffer lane,
- a UniFFI library exporting futures and foreign callbacks,
- a Diplomat or `cxx` crate using opaque handles or bridge-only types,
- a mixed-surface crate where one language binding is directly tested and another is only packaged.

## Non-goals

- not a generator replacement,
- not a per-language packaging suite,
- not a whole-program ABI coherence checker,
- not a blanket proof that foreign runtimes obey Rust-side thread assumptions.
