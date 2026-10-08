# ffi-boundary callback product plan — 2026-03-23

This note sharpens **P-0121 FFI Boundary & Bindings Conformance Kit** into a more implementation-ready callback-support slice.

## Main judgment

A worthwhile next increment should **not** become:

- another bridge generator,
- another runtime/executor crate,
- or a package/distribution helper.

It should become a **callback support-contract layer** that answers four boring but high-value questions:

1. Which artifact defines the callback surface and its directionality?
2. Is that callback native to the bridge family or only an adapter recipe layered on top?
3. What completion obligation exists — inline return, exactly-once done callback, channel send, or manual review?
4. What happens when cancellation, teardown, or unexpected callback failure occurs?

## What the crate should provide other people

### 1. `callback-authority.receipt.json`
This receipt should answer:
- what callback surface is being described,
- what artifact is authoritative (`trait`, bridge module, WIT world, generated adapter, etc.),
- whether the direction is `rust_calls_foreign`, `foreign_calls_rust`, `adapter_mediated`, or `bidirectional`,
- whether the support is native, limited, or adapter-only,
- and where manual review still starts.

### 2. `callback-completion.report.json`
This report should answer:
- what completion signal exists,
- whether completion is `exactly_once`, `at_most_once`, `inline`, `channel_mediated`, or `unspecified`,
- whether cancellation hooks exist and what they mean,
- whether completion may still arrive after teardown/drop,
- and how unexpected callback failures are surfaced.

### 3. portable bundle joins
A bundle should be able to point at:
- callback authority,
- callback execution,
- callback lifecycle,
- callback completion,
- and adjacent error-channel artifacts
without turning them into one fake verdict.

## Recommended `0.1` command surface

### `cargo ffi-contract capture --callbacks`
Emit:
- `callback-authority.receipt.json`
- `callback-execution.report.json`
- `callback-lifecycle.receipt.json`
- `callback-completion.report.json`

### `cargo ffi-contract check --callbacks`
Emit diagnostics such as:
- `callback_direction_implicit`
- `callback_native_vs_adapter_implicit`
- `callback_completion_unspecified`
- `callback_cancellation_unspecified`
- `callback_late_completion_manual_review`
- `unexpected_callback_error_posture_implicit`

### `cargo ffi-contract bundle --callbacks`
Emit one bundle manifest that keeps those callback facts separate.

## Best first proving grounds

1. a **UniFFI** foreign-future callback surface with exactly-once completion and optional dropped-future cancellation;
2. a **UniFFI** foreign trait whose unexpected callback errors must map into a declared error instead of panicking;
3. a **Diplomat** callback-parameter surface that is limited and not a symmetric foreign-trait story;
4. a **CXX** async workaround using oneshot callbacks and opaque context that must be reported as adapter-mediated rather than native async support.
