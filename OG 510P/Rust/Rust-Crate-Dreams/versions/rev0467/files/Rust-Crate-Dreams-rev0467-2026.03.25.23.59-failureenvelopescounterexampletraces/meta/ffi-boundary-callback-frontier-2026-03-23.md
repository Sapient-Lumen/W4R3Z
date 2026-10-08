# ffi-boundary callback frontier — 2026-03-23

This note sharpens **P-0121 FFI Boundary & Bindings Conformance Kit** around one missing seam:

> callback support is not one thing.

The archive now needs two more first-class review objects above the existing callback-execution / callback-lifecycle lane:

1. `callback-authority.receipt.json`
2. `callback-completion.report.json`

## Why these objects matter now

Current interop substrate is very uneven in ways that are visible to downstream users:

- **UniFFI** supports foreign traits / callbacks, but the docs make ownership, exactly-once completion, optional cancellation hooks, and unexpected-error mapping explicit.
- **Diplomat** is intentionally **unidirectional** and says callback support in parameters is **limited**.
- **CXX** supports callback patterns today, but direct async FFI is still **not implemented** and the documented workaround is an adapter recipe over channels plus opaque context.
- **WIT / wit-bindgen** make import/export directionality explicit, which means callback-like surfaces derive authority from world structure, not only generated Rust signatures.

A reviewer therefore needs more than “supports callbacks”.
They need to know:

- **who authored the callback contract**,
- **which direction the callback actually crosses**,
- **whether the callback is native to that family or only an adapter recipe**,
- **what completion obligation exists**,
- **whether cancellation is wired**,
- and **what happens on unexpected callback failure**.

## New archive stance

Treat **P-0121** as owning these callback-layer truths:

- callback authority,
- callback execution,
- callback lifecycle,
- callback completion,
- and callback-adjacent error posture.

Do **not** let future passes flatten those into:
- generic async-runtime support,
- generic mobile SDK support,
- generic generator comparison,
- or generic “callbacks are available”.
