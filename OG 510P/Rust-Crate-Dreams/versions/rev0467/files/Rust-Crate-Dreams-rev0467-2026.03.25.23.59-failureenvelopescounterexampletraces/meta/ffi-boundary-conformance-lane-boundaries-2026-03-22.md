# ffi-boundary-conformance-kit lane boundaries (2026-03-22)

This note exists so the archive does not flatten several adjacent interop, plugin, and shipkit lanes into one fake “Rust bindings crate” story.

## Core judgment

**P-0121 ffi-boundary-conformance-kit** should be the lane for:

- interface-authority truth,
- projection-basis truth,
- derivative-parity truth,
- ownership-transfer truth,
- unwind-posture truth,
- callback-execution truth,
- binding-coverage truth,
- layout-authority truth,
- error-channel truth,
- and projection-drift truth.

It is the lane for the question:

> “What boundary contract is this Rust crate actually publishing to another team across its foreign-language or foreign-runtime surfaces?”

## Keep separate from these adjacent lanes

### 1. Toolchain / ABI-coherence lanes
These are about whole-program compiler flags, target features, sysroots, and build coordination.

`ffi-boundary-conformance-kit` is **not** a whole-program ABI-policy lane.
It starts at the boundary surface another team consumes.

### 2. Generators and bridges themselves
- `cbindgen`
- UniFFI
- Diplomat
- `cxx`
- `wit-bindgen`

These tools already provide generation and runtime substrate.
`ffi-boundary-conformance-kit` should **not** collapse into another generator or wrapper that hides the bridge family.

The missing value is the **reviewable contract above those tools**.

### 3. Shipkits and packaging lanes
XCFramework, SwiftPM, Node-API prebuild, NuGet, JNI/JAR, RubyGems, and similar lanes are about delivery workflows.

`ffi-boundary-conformance-kit` is **not**:
- a packaging recipe collection,
- a release artifact shipper,
- or a language-specific distribution suite.

It may feed those lanes, but it owns **boundary truth**, not delivery truth.

### 4. Plugin / component lanes
Stable plugin host and Wasm plugin/component lanes add:
- lifecycle posture,
- capability grants,
- execution budgets,
- sandbox/composition concerns.

Those are not plain FFI boundary questions.
P-0121 can lend vocabulary, but it should not absorb those lanes.

### 5. Language-runtime attachment lanes
Python/Node/JVM/other runtime-specific integration often adds interpreter attachment, event-loop, thread-state, or host-runtime constraints.

Those constraints may deserve their own support lanes or shipkits.
P-0121 should not become a universal runtime-policy framework.

## Review objects that should stay first-class

### `interface-authority.import`
Keeps Rust declarations, WIT worlds, bridge modules, UDL/proc-macro declarations, generated headers, and generated bindings from collapsing into one fake “the interface is defined here” claim.

### `projection-basis.receipt`
Keeps generated headers, generated source bindings, custom-section metadata, packaging stubs, and backend-shaped projections from collapsing into one fake “the foreign API is obvious” claim.

### `derivative-parity.report`
Keeps faithful projections, renamed projections, subset projections, backend-shaped projections, and generated-but-unbuilt surfaces from collapsing into one fake “the generated artifact matches authority” claim.

### `ownership-transfer.receipt`
Keeps borrowed values, copied values, opaque handles, explicit-free routes, and refcounted handles from collapsing into one fake “safe FFI” claim.

### `unwind-posture.receipt`
Keeps panic translation, process-abort policy, unwind-ABI routes, and foreign-exception posture from collapsing into one fake “panic-safe” claim.

### `callback-execution.report`
Keeps synchronous callbacks, foreign-thread events, continuation callbacks, and async future machinery from collapsing into one fake “supports callbacks” claim.

### `binding-coverage.report`
Keeps directly checked surfaces, generated-only surfaces, packaging-only surfaces, and docs-only surfaces from collapsing into one fake “supports Swift/Kotlin/Python/C++” claim.

### `layout-authority.receipt`
Keeps shared structs, opaque handles, serialized buffers, and canonical ABI/resource lanes from collapsing into one fake “the type crosses the boundary” claim.

### `error-channel.receipt`
Keeps flat enums, status codes, structured results, exceptions, callback errors, and panic translation from collapsing into one fake “returns errors” claim.

## Doctor warnings worth keeping separate

The implementation should distinguish warnings such as:

- `projection_basis_implicit`
- `projection_subset_without_receiver_notice`
- `backend_projection_nonuniform`
- `generated_source_not_built_or_packaged`
- `layout_source_of_truth_implicit`
- `representation_mode_mixed`
- `by_value_claim_without_layout_authority`
- `panic_policy_implicit`
- `foreign_unwind_policy_implicit`
- `callback_after_drop_hazard`
- `binding_surface_generated_but_unchecked`
- `error_payload_flattened`
- `unexpected_callback_failure_panics`
- `manual_review_required`

## Non-goals for this boundary note

This note is **not** asking P-0121 to become:

- the one blessed Rust FFI generator,
- a whole packaging stack,
- a whole-program ABI-policy tool,
- a plugin runtime,
- or a universal language-runtime policy framework.
