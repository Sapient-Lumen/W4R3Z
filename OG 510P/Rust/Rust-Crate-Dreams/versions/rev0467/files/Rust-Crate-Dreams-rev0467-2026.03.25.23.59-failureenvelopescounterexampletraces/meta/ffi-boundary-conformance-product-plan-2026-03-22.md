# ffi-boundary-conformance-kit product plan — 2026-03-22

This note sharpens **P-0121 FFI Boundary & Bindings Conformance Kit** into a stronger implementation-ready `0.1` direction.

## Main judgment

A worthwhile `0.1` should still **not** try to become:

- another bindings generator,
- another package shipkit,
- or a universal language-interop abstraction.

It should become a **boundary contract layer** that helps a crate publish one reviewable answer to six boring but high-value questions:

1. How is ownership transferred at the boundary?
2. What is the panic / unwind policy for each exported surface?
3. Where and how do callbacks execute, and what teardown rule makes them sound?
4. Which bindings are actually checked versus merely generated or documented?
5. What representation really crosses the boundary, and who is its source of truth?
6. How do errors, exceptions, and unexpected failures cross the boundary?

## Why this lane got stronger

Fresh official and ecosystem substrate makes the gap more actionable than it used to be:

- the Rust project now explicitly frames **Cross-language interop** as a strategic application area;
- the January 2026 safety-critical write-up says C/C++ interop is part of the safety story and calls out bindings/debugging friction directly;
- the 2024 Edition requires `unsafe extern` blocks, making boundary obligations more explicit;
- the Reference and RFC 2945 keep unwinding and non-unwinding ABI categories sharply distinct;
- `cxx` sharply distinguishes shared by-value types from opaque indirection-only types and documents explicit `Result`/exception handling;
- UniFFI documents object-reference ownership, callback handle behavior, async cancellation hooks, and error shaping;
- Diplomat documents limited type surfaces and explicit opacity / mutability choices;
- WIT and the Canonical ABI make interface authority and low-level calling contracts explicit for component boundaries;
- `cbindgen` remains useful generation substrate, but generated declarations are not a complete receiver-facing contract.

That means the missing value is now even more clearly the contract layer **above** the substrate.

## What the crate should provide other people

For SDK teams, systems integrators, release reviewers, and downstream adopters, the crate should provide:

1. **One interface-authority import** so the primary contract is explicit.
2. **One projection-basis receipt** so generated headers/bindings/custom sections are tied back to authority and configuration.
3. **One derivative-parity report** so backend attrs, renames, omitted items, and generated-only gaps stop masquerading as full equivalence.
4. **One ownership-transfer receipt** instead of free-function folklore.
5. **One unwind-posture receipt** instead of scattered ABI and panic caveats.
3. **One callback-execution report** instead of guessing thread/runtime assumptions from codegen.
4. **One binding-coverage report** instead of equating generation with verification.
5. **One layout-authority receipt** instead of flattening shared structs, opaque handles, serialized buffers, and canonical ABI resources into “has bindings”.
9. **One error-channel receipt** instead of flattening `Result`, exceptions, status returns, callback failures, and panic translation into “returns errors”.
10. **One projection-drift report** so receiver-visible foreign-surface change is reviewable across releases.
11. **One compact contract-check report** that keeps imported facts, observed checks, and manual-review zones visibly separate.

## Nine first-class review objects

### 1. `interface-authority.import`
Answers:
- what artifact is primary authority,
- what family the boundary belongs to,
- what derived artifacts exist,
- and where mixed/manual authority remains.

### 2. `projection-basis.receipt`
Answers:
- what emitted foreign artifact is being described,
- which generator/backend/configuration produced it,
- whether it is full, subset, renamed, backend-shaped, or packaging-only,
- and whether generation stops before build/package proof.

### 3. `derivative-parity.report`
Answers:
- whether a generated header/binding/custom section still faithfully reflects the primary authority,
- what receiver-visible differences were introduced by generator options, backend attributes, or omission,
- what proof backs the parity statement,
- and whether manual review is still required.

### 4. `ownership-transfer.receipt`
Answers:
- what boundary surface is being described,
- whether the value is borrowed, copied, opaque-handle-based, explicit-free, reference-counted, or runtime-managed,
- which allocation domain owns the backing storage,
- what release mechanism exists,
- and how long the foreign side may keep it.

### 5. `unwind-posture.receipt`
Answers:
- which ABI family is in play,
- whether Rust panics are caught and translated, abort, or are intentionally allowed to unwind,
- whether foreign exceptions/unwinds may enter Rust,
- and what containment strategy exists.

### 6. `callback-execution.report`
Answers:
- whether callbacks are synchronous, event-driven, or continuation/future-based,
- where execution originates,
- what thread or runtime affinity is assumed,
- whether teardown depends on unregister-before-drop,
- and whether completion is inline, after return, or via a poll/cancel/free lifecycle.

### 7. `binding-coverage.report`
Answers:
- which surfaces exist,
- which family each one belongs to,
- how it is generated,
- and whether it was `directly_checked`, `generated_only`, `packaging_only`, `docs_only`, or still `manual_review_required`.

### 8. `layout-authority.receipt`
Answers:
- whether the surface crosses as a shared by-value type, opaque handle, serialized buffer, or canonical ABI value/resource,
- who is the source of truth for that representation,
- whether the representation is verified by static assertions, interface checking, generated code only, or manual review,
- and whether by-value crossing is actually allowed.

### 9. `error-channel.receipt`
Answers:
- whether failure crosses as a `Result`, exception, callback result, status+out-param, canonical result, or nothing explicit,
- whether payload fidelity is code-only, flat enum, structured fields, message-only, or opaque foreign error,
- how panics are handled,
- and what happens to unexpected callback / foreign-side failures.

## Recommended `0.1` command surface

### `cargo ffi-contract capture`
Capture the declared/imported contract and emit:
- `interface-authority.import.json`
- `projection-basis.receipt.json`
- `derivative-parity.report.json`
- `ownership-transfer.receipt.json`
- `unwind-posture.receipt.json`
- `callback-execution.report.json`
- `binding-coverage.report.json`
- `layout-authority.receipt.json`
- `error-channel.receipt.json`

### `cargo ffi-contract check`
Run conservative checks and emit:
- `ffi-contract-check.report.json`

### `cargo ffi-contract diff`
Compare two bundles and emit:
- `projection-drift.report.json`
- `ffi-contract-diff.report.json`

### `cargo ffi-contract bundle`
Produce one compact `.fficontractbundle.zip`.

## Recommended crate/workspace split

- `ffi_contract_model`
- `ffi_contract_import_cabi`
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
2. **Representation capture**
   - shared by-value types
   - opaque handles and indirection-only types
   - serialized buffer lowerings
   - canonical ABI values/resources
3. **Ownership capture**
   - buffers
   - handles / opaque types
   - callback object references
   - explicit free or drop routes
4. **Unwind + error capture**
   - ABI family
   - `catch_unwind` wrappers
   - abort-profile assumptions
   - exception mapping
   - callback unexpected-failure behavior
5. **Callback capture**
   - registration model
   - thread/runtime origin
   - teardown rule
   - async continuation lifecycle
6. **Coverage capture**
   - language/runtime targets
   - generation mode
   - check mode
7. **Bundle and diff**
   - export one compact review bundle

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- `unsafe extern` and ABI declarations
- explicit `catch_unwind` wrappers
- `cxx` shared-vs-opaque type declarations and `Result`/exception routes
- UniFFI RustBuffer/handle/object-ref/future surfaces
- Diplomat opaque-type and supported-type declarations
- WIT interface/resource/result declarations
- `cbindgen` header-generation facts

### Do not flatten into one fake verdict
- “uses UniFFI”
- “has a C ABI”
- “supports C++”
- “supports callbacks”
- “supports async”
- “generated bindings exist”
- “returns errors”

Those are ingredients, not the contract.

## Best first proving grounds

- a C ABI crate with explicit free functions and a borrowed buffer lane,
- a `cxx` crate mixing shared and opaque types,
- a UniFFI library exporting futures and foreign callbacks,
- a WIT/component crate exposing resources/results,
- a mixed-surface crate where one language binding is directly tested and another is only packaged.

## Non-goals

- not a generator replacement,
- not a package shipkit suite,
- not a whole-program ABI coherence checker,
- not a blanket proof that foreign runtimes obey Rust-side thread assumptions,
- not a universal language-runtime policy layer.

## Freshness anchors

- program-management update — https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- safety-critical Rust — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust 2024 `unsafe extern` — https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
- external blocks — https://doc.rust-lang.org/reference/items/external-blocks.html
- RFC 2945 `C-unwind` — https://rust-lang.github.io/rfcs/2945-c-unwind-abi.html
- `cxx` docs — https://cxx.rs/shared.html ; https://cxx.rs/concepts.html ; https://cxx.rs/binding/result.html
- UniFFI docs — https://mozilla.github.io/uniffi-rs/latest/internals/object_references.html ; https://mozilla.github.io/uniffi-rs/latest/internals/async-ffi.html ; https://mozilla.github.io/uniffi-rs/latest/udl/errors.html ; https://mozilla.github.io/uniffi-rs/latest/foreign_traits.html
- Diplomat book — https://rust-diplomat.github.io/book/types.html ; https://rust-diplomat.github.io/book/opaque.html
- component model docs — https://component-model.bytecodealliance.org/design/why-component-model.html ; https://component-model.bytecodealliance.org/design/wit.html ; https://component-model.bytecodealliance.org/using-wit-resources.html
- `cbindgen` docs — https://docs.rs/cbindgen/latest/cbindgen/
