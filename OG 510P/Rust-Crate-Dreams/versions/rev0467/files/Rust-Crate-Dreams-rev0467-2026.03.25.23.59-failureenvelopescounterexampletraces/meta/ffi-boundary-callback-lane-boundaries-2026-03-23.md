# ffi-boundary callback lane boundaries — 2026-03-23

This note keeps **P-0121 FFI Boundary & Bindings Conformance Kit** from collapsing callback support into adjacent lanes.

## Within P-0121, keep these truths separate

1. **callback authority** — what artifact defines the callback surface and which direction it crosses.
2. **callback execution** — inline / foreign-thread / continuation / runtime-origin behavior.
3. **callback lifecycle** — registration, clone/free, unregister-before-drop, cancellation hooks, late-call hazards.
4. **callback completion** — exactly-once vs channel-mediated vs unspecified completion and unexpected-error posture.

## Distinct from async-runtime assurance

`P-0532` is about runtime families, deployment topology, capability availability, and shutdown posture.
`P-0121` is about what an FFI callback surface honestly claims above whatever runtime exists.

## Distinct from package/mobile shipkits

Package and shipkit lanes may prove that bindings were built and distributed.
`P-0121` should stay focused on boundary semantics, not distribution assembly.

## Distinct from generator comparison

The point is not “which generator is best”.
The point is whether a maintainer can publish a callback support receipt that survives mixed families:
- UniFFI foreign traits,
- Diplomat callback parameters,
- CXX callback/adapter recipes,
- WIT import/export-driven callback-like surfaces.

## Non-goals

Do not turn this lane into:
- a universal executor adapter,
- a callback runtime,
- a test harness for every foreign language backend,
- or a broad “async interop” product.
