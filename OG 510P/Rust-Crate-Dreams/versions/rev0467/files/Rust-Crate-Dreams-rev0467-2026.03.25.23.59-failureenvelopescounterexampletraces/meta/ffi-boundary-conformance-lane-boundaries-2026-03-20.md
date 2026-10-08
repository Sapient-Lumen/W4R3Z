# ffi-boundary-conformance-kit lane boundaries (2026-03-20)

This note exists so the archive does not flatten several adjacent FFI and shipping lanes into one fake “Rust bindings crate” story.

## Core judgment

**P-0121 ffi-boundary-conformance-kit** should be the lane for:

- **ownership-transfer truth**,
- **unwind-posture truth**,
- **callback-execution truth**,
- and **binding-coverage truth**.

It is the lane for the question:

> “What boundary contract is this Rust crate actually publishing to another team across its foreign-language or foreign-runtime surfaces?”

## Keep separate from these adjacent lanes

### 1. P-0454 ABI Coherence Profile Kit

ABI Coherence Profile Kit is about:
- whole-program compiler-flag coherence,
- target modifiers,
- sysroot rebuilding,
- and exemption ledgers.

`ffi-boundary-conformance-kit` is **not**:
- a whole-program compiler-flag policy layer,
- a build-std or sanitizer coordination lane,
- or a substitute for rustc ABI-mismatch checks.

This lane starts **at the boundary surface another team consumes**.
It does not own toolchain-wide coherence.

### 2. Specific generators and bridges (`cbindgen`, UniFFI, Diplomat, `cxx`, WIT/component tools)

Existing tools already provide:
- header generation,
- language-specific binding generation,
- C++ bridge generation,
- and component-model bindings.

`ffi-boundary-conformance-kit` should **not** collapse into:
- another bindings generator,
- another header renderer,
- or a wrapper that hides the underlying bridge family.

The missing value is the **reviewable contract above those tools**.

### 3. Package / publish / artifact shipping lanes

Package-review and publish-receipt lanes are about:
- what bytes were packaged,
- what became authoritative in the index,
- and which public surfaces have converged.

`ffi-boundary-conformance-kit` is **not**:
- a release receipt for crates.io,
- a package-surface reviewer,
- or a mobile packaging workflow.

It may feed those lanes, but it owns **boundary truth**, not distribution truth.

### 4. SDK semver / migration lanes

Migration and upgrade lanes are about:
- release-to-release hazard summaries,
- codemods,
- and review pack governance.

`ffi-boundary-conformance-kit` is **not**:
- a semver oracle,
- an SDK migration planner,
- or a changelog replacement.

Its job is to publish the current boundary contract in a way that later lanes can diff.

## Review objects that should stay first-class

### `ownership-transfer.receipt`

Keeps borrowed values, copied values, opaque handles, explicit-free routes, and refcounted handles from collapsing into one fake “safe FFI” claim.

### `unwind-posture.receipt`

Keeps panic translation, process-abort policy, unwind-ABI routes, and foreign-exception posture from collapsing into one fake “panic-safe” claim.

### `callback-execution.report`

Keeps synchronous callbacks, foreign-thread events, continuation callbacks, and async future machinery from collapsing into one fake “supports callbacks” claim.

### `binding-coverage.report`

Keeps directly checked surfaces, generated-only surfaces, packaging-only surfaces, and docs-only surfaces from collapsing into one fake “supports Swift/Kotlin/Python/C++” claim.

## Doctor warnings worth keeping separate

The first implementation should distinguish warnings such as:

- `borrow_exceeds_call_boundary`
- `allocator_ownership_implicit`
- `panic_policy_implicit`
- `foreign_unwind_policy_implicit`
- `callback_after_drop_hazard`
- `callback_thread_origin_unknown`
- `binding_surface_generated_but_unchecked`
- `manual_review_required`

## Non-goals for this boundary note

This note is **not** asking P-0121 to become:

- the one blessed Rust FFI generator,
- a whole packaging stack,
- a whole-program ABI-policy tool,
- or a formal proof system for foreign runtimes.
